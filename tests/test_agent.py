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


from tests.fakes import FakeClient, response

class AgentTests(unittest.TestCase):
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
        with self.assertLogs("agent", level="ERROR"):
            events = list(run_agent(new_history(), "hello", FakeClient([])))
        self.assertIn("internal application error", events[-1]["content"])

    def test_current_date_is_refreshed_and_not_stored(self):
        from datetime import date
        client = unittest.mock.Mock()
        client.chat.return_value = response()
        history = new_history()
        with patch("agent.date") as clock:
            clock.today.return_value = date(2027, 1, 10)
            list(run_agent(history, "Tomorrow", client))
            first = client.chat.call_args.kwargs["messages"][0]["content"]
            clock.today.return_value = date(2027, 1, 11)
            list(run_agent(history, "Tomorrow again", client))
            second = client.chat.call_args.kwargs["messages"][0]["content"]
        self.assertIn("2027-01-10", first)
        self.assertIn("2027-01-11", second)
        self.assertNotIn("Current local date", history[0]["content"])

    def test_connection_and_response_errors_are_distinct(self):
        from ollama import ResponseError
        for error, expected in [(ConnectionError(), "connection failed"), (ResponseError("model missing", 404), "status 404")]:
            client = unittest.mock.Mock()
            client.chat.side_effect = error
            result = list(run_agent(new_history(), "Plan", client))[-1]
            self.assertIn(expected, result["content"])

    def test_malformed_model_call_is_reported(self):
        message = {"role": "assistant", "content": "", "tool_calls": [{"function": {"arguments": {}}}]}
        client = unittest.mock.Mock()
        client.chat.return_value = SimpleNamespace(message=SimpleNamespace(model_dump=lambda **kw: message))
        result = list(run_agent(new_history(), "Plan", client))[-1]
        self.assertIn("model-response error", result["content"])

    def test_agent_save_then_load_across_conversations(self):
        plan = json.loads((Path(__file__).parent / "fixtures/valid_itinerary.json").read_text())
        with tempfile.TemporaryDirectory() as folder, patch("tools.itinerary.DATA_DIR", Path(folder)):
            save_client = FakeClient([response([("save_itinerary", {"filename": "demo.json", "itinerary_json": json.dumps(plan)})]), response(content="Saved")])
            events = list(run_agent(new_history(), "Save the full plan", save_client))
            saved = next(e for e in events if e["type"] == "tool_result")
            self.assertTrue(saved["result"]["ok"])
            self.assertTrue(Path(folder, "demo.json").is_file())
            load_client = FakeClient([response([("load_itinerary", {"filename": "demo.json"})]), response(content="Loaded")])
            events = list(run_agent(new_history(), "Load demo.json", load_client))
            loaded = next(e for e in events if e["type"] == "tool_result")
            self.assertEqual(loaded["result"]["data"]["itinerary"], plan)
