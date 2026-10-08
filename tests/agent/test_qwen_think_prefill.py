"""Qwen template-prefilled thoughts must not become visible answer deltas."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from agent.qwen_think_prefill import QwenThinkPrefill
from agent.think_scrubber import StreamingThinkScrubber


def test_prefill_is_chunk_safe_without_changing_plain_or_native_answers():
    cases = [
        ("private thought</think>answer", "stop", "answer"),
        ("<think>private thought</think>answer", "stop", "answer"),
        ("plain answer", "stop", "plain answer"),
        ("unfinished thought", "length", ""),
        ("unfinished thought", None, ""),
    ]
    for text, finish, expected in cases:
        for width in range(1, len(text) + 1):
            parser = QwenThinkPrefill("Qwen/Qwen3.8-27B-FP8")
            scrubber = StreamingThinkScrubber()
            visible = []
            for offset in range(0, len(text), width):
                visible.append(scrubber.feed(parser.feed(text[offset:offset + width])))
                assert "private" not in "".join(visible)
            visible.append(scrubber.feed(parser.finish(finish)))
            visible.append(scrubber.flush())
            assert "".join(visible) == expected
    parser = QwenThinkPrefill("qwen3.8-27b")
    assert parser.feed("", native_reasoning=True) == ""
    assert parser.feed("literal </think> in an answer") == "literal </think> in an answer"
    assert QwenThinkPrefill("unrelated-model").feed("ordinary text") == "ordinary text"
    parser = QwenThinkPrefill("qwen3.8-27b", "none")
    assert parser.feed("partial answer") == "partial answer"
    assert parser.finish("length") == ""


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("effort", ["none", "low", "medium", "xhigh"])
def test_real_request_hides_prefilled_reasoning_without_changing_effort(tmp_path, streaming, effort):
    from agent.chat_completion_helpers import direct_api_call, interruptible_streaming_api_call
    from agent.agent_runtime_helpers import strip_think_blocks
    from agent.transports.chat_completions import ChatCompletionsTransport
    from providers import get_provider_profile
    from run_agent import AIAgent
    from sci_constants import parse_reasoning_effort

    requests = []
    answer = "OK" if effort == "none" else "private thought</think>OK"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append(body)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream" if body.get("stream") else "application/json")
            self.end_headers()
            base = {"id": "qwen-fixture", "created": 1, "model": "qwen3.8-27b"}
            if body.get("stream"):
                for index, character in enumerate(answer):
                    chunk = {**base, "object": "chat.completion.chunk", "choices": [{"index": 0,
                             "delta": {"content": character},
                             "finish_reason": "stop" if index == len(answer) - 1 else None}]}
                    self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
                    self.wfile.flush()
                self.wfile.write(b"data: [DONE]\n\n")
            else:
                self.wfile.write(json.dumps({**base, "object": "chat.completion", "choices": [{"index": 0,
                    "message": {"role": "assistant", "content": answer}, "finish_reason": "stop"}]}).encode())

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}/v1"
    visible = []
    agent = AIAgent(api_key="fixture-only", base_url=base_url, provider="custom", model="qwen3.8-27b",
                    platform="subagent", quiet_mode=True, skip_memory=True, skip_context_files=True,
                    enabled_toolsets=[], save_trajectories=False, stream_delta_callback=visible.append)
    kwargs = ChatCompletionsTransport().build_kwargs(
        agent.model, [{"role": "user", "content": "Reply OK"}],
        provider_profile=get_provider_profile("custom"), base_url=base_url,
        reasoning_config=parse_reasoning_effort(effort))
    try:
        call = interruptible_streaming_api_call if streaming else direct_api_call
        response = call(agent, kwargs)
        assert requests[-1]["reasoning_effort"] == effort
        assert strip_think_blocks(agent, response.choices[0].message.content).strip() == "OK"
        if streaming:
            assert "".join(visible).strip() == "OK"
        assert kwargs["messages"] == [{"role": "user", "content": "Reply OK"}]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
