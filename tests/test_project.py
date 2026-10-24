"""Offline tests: fake SDK responses and API fixtures, never fake live validation."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from tools import TOOLS, TOOL_MAP
from tools.budget import calculate_budget
from tools.itinerary import save_itinerary, load_itinerary
from tools.weather import get_weather
from tools.currency import get_currency_conversion
from tools.travel_time import get_travel_time
from agent import run_agent, new_history


def response(calls=None, content="Done"):
    data = {"role": "assistant", "content": content}
    if calls:
        data["tool_calls"] = [{"function": {"name": n, "arguments": a}} for n, a in calls]
    return SimpleNamespace(message=SimpleNamespace(model_dump=lambda **kwargs: data))


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0
    def chat(self, **kwargs):
        self.calls += 1
        return next(self.responses)


class ProjectTests(unittest.TestCase):
    def test_nine_tools_and_bad_arguments(self):
        self.assertEqual(len(TOOLS), 9)
        for tool in TOOLS:
            self.assertTrue(tool.__doc__)
            self.assertFalse(tool(unexpected_argument=True)["ok"])

    def test_budget_group_and_decimal(self):
        result = calculate_budget(2, 2, 10, 5, 8, 100)["data"]
        self.assertEqual(result["total"], 83.6)
        self.assertEqual(result["remaining"], 16.4)
        self.assertTrue(result["within_budget"])
        self.assertFalse(calculate_budget(True, 1, 1, 1, 1, 1)["ok"])
        self.assertFalse(calculate_budget(1, 1, float("nan"), 1, 1, 1)["ok"])

    def test_persistence_and_traversal(self):
        plan = {"destination": "Colombo", "days": [{"activities": ["Museum"]}], "budget": {"total": 50}}
        with tempfile.TemporaryDirectory() as folder, patch("tools.itinerary.DATA_DIR", Path(folder)):
            self.assertTrue(save_itinerary("trip.json", json.dumps(plan))["ok"])
            self.assertEqual(load_itinerary("trip.json")["data"]["itinerary"], plan)
            self.assertFalse(save_itinerary("trip.json", json.dumps(plan))["ok"])
            self.assertTrue(save_itinerary("trip.json", json.dumps(plan), True)["ok"])
            self.assertFalse(save_itinerary("../escape.json", json.dumps(plan))["ok"])
            self.assertFalse(save_itinerary("bad.json", "{}")["ok"])
            self.assertFalse(load_itinerary("absent.json")["ok"])
            Path(folder, "broken.json").write_text("not json")
            self.assertFalse(load_itinerary("broken.json")["ok"])

    def test_travel_estimate(self):
        self.assertEqual(get_travel_time("Colombo", "National Museum", "National Museum")["data"]["minutes"], 0)
        self.assertFalse(get_travel_time("Colombo", "Unknown", "National Museum")["ok"])

    def test_api_failures(self):
        import requests
        with patch("tools.weather.fetch", side_effect=requests.Timeout):
            self.assertFalse(get_weather("Colombo", "2027-01-01")["ok"])
        with patch("tools.weather.fetch", return_value={"results": [{"name": "Colombo", "timezone": "Asia/Colombo"}]}):
            self.assertIn("Forecast unavailable", get_weather("Colombo", "2099-01-01")["error"])
        with patch("tools.currency.fetch", side_effect=[{"USD": "Dollar", "EUR": "Euro"}, {"rates": {"EUR": .9}, "date": "2026-10-23"}]):
            self.assertEqual(get_currency_conversion(100, "USD", "EUR")["data"]["converted_amount"], 90)

    def test_multiple_calls_and_followup(self):
        client = FakeClient([response([("search_attractions", {"city": "Colombo", "interests": []}), ("get_local_tips", {"city": "Colombo"})]), response(), response(content="Follow-up")])
        history = new_history()
        events = list(run_agent(history, "Plan Colombo", client))
        self.assertEqual(len([e for e in events if e["type"] == "tool_result"]), 2)
        self.assertEqual(len([m for m in history if m["role"] == "tool"]), 2)
        list(run_agent(history, "Make day 2 cheaper", client))
        self.assertEqual(len([m for m in history if m["role"] == "user"]), 2)

    def test_limit_unknown_tool_and_bad_json(self):
        client = FakeClient([response([("unknown", {})])] * 10)
        history = new_history()
        events = list(run_agent(history, "Loop", client))
        self.assertEqual(client.calls, 10)
        self.assertIn("Stopped after 10", events[-1]["content"])
        self.assertEqual(len([m for m in history if m["role"] == "tool"]), 10)
        bad = FakeClient([response([("get_local_tips", "{")]), response()])
        events = list(run_agent(new_history(), "bad", bad))
        self.assertFalse(next(e for e in events if e["type"] == "tool_result")["result"]["ok"])

    def test_selected_tool_blocks_other_calls(self):
        client = FakeClient([response([("get_local_tips", {"city": "Colombo"}),
                                       ("search_attractions", {"city": "Colombo", "interests": []})]), response()])
        with patch("agent.TOOL_MAP", {**TOOL_MAP, "search_attractions": unittest.mock.Mock()}) as registry:
            events = list(run_agent(new_history(), "Colombo", client, selected_tool="get_local_tips"))
            registry["search_attractions"].assert_not_called()
        results = [e["result"] for e in events if e["type"] == "tool_result"]
        self.assertTrue(results[0]["ok"])
        self.assertFalse(results[1]["ok"])

    def test_selection_schema_and_reset(self):
        client = unittest.mock.Mock()
        client.chat.return_value = response()
        history = new_history()
        list(run_agent(history, "Tips", client, selected_tool="get_local_tips"))
        self.assertEqual([f.__name__ for f in client.chat.call_args.kwargs["tools"]], ["get_local_tips"])
        list(run_agent(history, "Full trip", client))
        self.assertEqual(len(client.chat.call_args.kwargs["tools"]), 9)
        self.assertNotIn("Current tool selection:", history[0]["content"])
        self.assertEqual(len([m for m in history if m["role"] == "user"]), 2)
        self.assertIn("Unknown tool selection", list(run_agent(history, "test", client, selected_tool="invalid"))[0]["content"])

    def test_model_failure(self):
        events = list(run_agent(new_history(), "hello", FakeClient([])))
        self.assertIn("Ollama could not complete", events[-1]["content"])

    def test_streamlit_render_and_chat(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).parents[1] / "main.py"))
        app.run(timeout=20)
        self.assertFalse(app.exception)
        def fake_run(messages, prompt, selected_tool=None):
            self.assertEqual(selected_tool, "get_local_tips")
            yield {"type": "tool_start", "step": 1, "name": "get_local_tips", "arguments": {"city": "Colombo"}}
            yield {"type": "tool_result", "step": 1, "name": "get_local_tips", "arguments": {"city": "Colombo"}, "result": {"ok": True, "data": {}}}
            yield {"type": "final", "content": "Test plan"}
        self.assertEqual(len(app.selectbox(key="tool_selection").options), 10)
        app.selectbox(key="tool_selection").select("Local tips").run()
        with patch("agent.run_agent", fake_run) as mocked:
            app.chat_input[0].set_value("Plan Colombo").run(timeout=20)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state["turns"]), 1)
        self.assertEqual(len(app.expander), 1)


if __name__ == "__main__":
    unittest.main()
