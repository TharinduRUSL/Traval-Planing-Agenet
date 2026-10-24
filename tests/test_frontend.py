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

class FrontendTests(unittest.TestCase):
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

    def test_supported_destinations_and_new_conversation(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).parents[1] / "main.py")).run(timeout=20)
        text = " ".join(item.value for item in app.markdown)
        self.assertIn("Colombo · Kandy · Paris · London", text)
        self.assertNotIn("Tokyo", text)
        app.session_state["turns"] = [{"user": "old", "answer": "old answer", "trace": []}]
        app.run()
        next(b for b in app.button if "New conversation" in b.label).click().run()
        self.assertEqual(app.session_state["turns"], [])
        self.assertEqual(len(app.session_state["messages"]), 1)
