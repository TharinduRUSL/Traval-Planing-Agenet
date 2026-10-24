from types import SimpleNamespace

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


