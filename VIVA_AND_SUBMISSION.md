# Viva and submission checklist

## Ten-minute walkthrough

- 0–1 min: problem, supported cities, local model, real APIs versus curated estimates.
- 1–3 min: show a multi-step request and visible tool names, arguments and results.
- 3–5 min: walk through agent.py: history, model request, tool calls, whitelist, result messages, final answer and 10-step cap.
- 5–6 min: change day 2; explain session-state memory and context limits.
- 6–7 min: save, restart conversation, load the JSON and show data/.
- 7–8 min: explain validation and one failed API/file input.
- 8–9 min: run offline tests; distinguish them from a real Ollama demo.
- 9–10 min: limitations, individual contributions and future improvements.

## Questions to prepare

1. Why is this an agent? The model chooses tools, receives results and repeats before answering.
2. Why exactly nine? The registry is the only source of exposed functions; helpers are internal.
3. Why append assistant tool calls? They establish which requests the following tool messages answer.
4. Why JSON? Structured results are easy to inspect, serialize, persist and return to the model.
5. Does a tool error crash the app? The tool wrapper returns an error envelope; the model can retry.
6. Is the weather for next year real? No: outside-window requests fail transparently.
7. What persists? JSON files; browser-session chat state is temporary.
8. How is a budget computed? Per-person daily costs times days and travelers, plus trip admissions per person times travelers, then contingency.
9. What prevents arbitrary execution? The whitelist; there is no eval or shell tool.
10. Is a small model always correct? No. Inspect traces and test real tasks; schema and tool validation do not guarantee perfect reasoning.

## Remaining submission work for your group

- Register 2–3 members and scenario with the lecturer.
- Create a shared Git repository and have every member contribute code and understand all modules.
- Run the real-machine acceptance tasks in VALIDATION.md and record actual results.
- Write a 1,500–2,500-word PDF report: problem; architecture; nine tool designs/parameters/sample outputs; loop and prompt; actual testing and fixes; limitations/future work; individual contribution table.
- Add an appendix describing AI assistance honestly; do not claim generated code was independently authored.
- Record a 3–5-minute video with two complete tasks, including a multi-step plan and visible trace.
- Submit the repository link with report/video as instructed. No API secrets or personal itinerary data in commits.

Suggested contribution table columns: member name, student ID, implemented modules, test work, documentation work, commit references. Fill with real work only.
