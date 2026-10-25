# Agent design

Default model: qwen2.5:3b, a compact approximately three-billion-parameter tool-calling model. It is chosen to reduce local hardware requirements. Compare real behavior on your machines rather than claiming universal accuracy.

## Explain the loop

1. Validate text and selected tool.
2. Build the active function whitelist and append the user's message.
3. For steps 1 through 10, add today's local date and current selection to a temporary system message.
4. Call the official Ollama Python Client with full history and active functions.
5. Append the assistant message, including tool calls.
6. If there are no calls, yield the final response and return.
7. For each call, yield tool_start, validate its name/arguments, execute only an enabled registered function, append the JSON tool result, and yield tool_result.
8. Repeat. After request 10, execute its requested calls but do not make request 11. Yield a clear limit notice.

No eval, shell execution or arbitrary generated Python is used. Multiple tool calls in a model response run sequentially. The selection filters both model schemas and execution, so an unwanted tool cannot bypass the dropdown restriction merely by being named.

## Errors and memory

Connection/timeouts, Ollama response errors, invalid configuration/model messages and unexpected internal errors have separate final messages. Unexpected errors are logged to the terminal for debugging. Do not publish terminal logs containing personal itineraries.

The frontend retains system/user/assistant/tool messages across reruns. New conversation clears memory, not saved files. The current date is rebuilt for every model request; it is not frozen at session creation.

## Remaining limits

A small model may ask unnecessary questions, miss a tool, generate bad arguments or reach 10 steps. No claim of live quality is based on mocked tests. Overwrite intent is instructed in the system prompt and implemented as an explicit boolean; it is not an independent natural-language authorization engine. Keep the application for trusted local use.
