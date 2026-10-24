# Build validation — 24 October 2026

- Python 3.12 automated suite: **11 tests passed**.
- Streamlit AppTest: initial page and simulated chat/tool trace render without exceptions.
- Both entry points (`python main.py` and `python -m streamlit run main.py`) started Streamlit and printed local URLs in subprocess smoke checks on port 8597.
- Official Ollama SDK: all nine decorated functions successfully convert to schemas with named typed parameters.
- Offline tests use mocked model/API responses; no live Ollama model was available for inference validation here.
- External API integration has been checked against official documentation and fixtures, but live endpoint availability was not verified in this restricted environment.
- The host had a SOCKS-proxy environment without its optional dependency. Tests ran with host proxy variables removed; this is a test-environment issue, not an instruction to alter your Windows security settings.
- Dependency ranges are declared rather than a cross-platform lockfile. The versions used for automated checks are listed below.

## Installed versions during testing

- ollama: 0.6.3
- streamlit: 1.66.1
- requests: 2.34.2
- python-dotenv: 1.2.4
- tzdata: 2026.5

## Real-machine acceptance checklist

1. Install dependencies, start Ollama and pull qwen2.5:3b.
2. Launch with python main.py; open the printed localhost link.
3. Stop it, then launch with streamlit run main.py; confirm the same interface.
4. Run example 1 with tomorrow's date. Inspect the real weather output and all tool calls.
5. Verify budget arithmetic; confirm the saved JSON includes every planned day and matches the displayed plan.
6. Ask to make day 2 cheaper; confirm earlier destination, traveler count and dates are retained.
7. Start a new conversation, load the saved file, revise and save under another name.
8. Run the Paris example to exercise currency conversion.
9. Try a distant future weather date and an unsupported currency; verify clear errors rather than invented data.
10. Record actual outcomes for the report, including model mistakes and retries.

## Tool-selector update

Additional tests verify selected-tool schema filtering, blocking unselected tool execution, switching back to all nine tools without stale scope, invalid selection handling, and selecting Local tips through Streamlit AppTest before sending a message. Live model inference remains unverified.
