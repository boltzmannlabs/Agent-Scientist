"""Direct endpoint benchmark contracts; no calls to the configured Qwen server."""

import asyncio
import csv
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import time

import httpx


spec = importlib.util.spec_from_file_location(
    "qwen_endpoint_load_test", Path(__file__).resolve().parents[2] / "scripts/qwen_endpoint_load_test.py"
)
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


def options(**overrides):
    defaults = dict(base_url="http://benchmark.invalid/v1", model="test-qwen", requests=100,
                    concurrency=100, temperature=0.3, max_tokens=512, timeout=10, stream=False)
    return SimpleNamespace(**(defaults | overrides))


def test_burst_releases_all_requests_and_preserves_each_answer(tmp_path):
    async def exercise():
        received = []
        all_received = asyncio.Event()

        async def handler(reader, writer):
            header_block = (await reader.readuntil(b"\r\n\r\n")).decode("ascii")
            lines = header_block.split("\r\n")
            headers = dict(line.lower().split(": ", 1) for line in lines[1:] if line)
            payload = json.loads(await reader.readexactly(int(headers["content-length"])))
            prompt = payload["messages"][-1]["content"]
            assert "authorization" not in headers
            assert lines[0] == "POST /v1/chat/completions HTTP/1.1"
            received.append(prompt)
            if len(received) == 100:
                all_received.set()
            await asyncio.wait_for(all_received.wait(), timeout=5)
            body = json.dumps({
                "id": "response-" + str(len(received)), "model": "test-qwen",
                "choices": [{"message": {"content": "Answer to: " + prompt}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
            }).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n"
                         + f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        server = await asyncio.start_server(handler, "127.0.0.1", 0, backlog=200)
        async with server:
            port = server.sockets[0].getsockname()[1]
            summary = await benchmark.run_burst(options(base_url=f"http://127.0.0.1:{port}/v1"), "", tmp_path)
        assert len(received) == len(set(received)) == 100
        assert summary["peak_client_inflight"] == summary["successful"] == 100
        with (tmp_path / "responses.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 100
        assert {int(row["request_id"]) for row in rows} == set(range(1, 101))
        assert all(row["response"] == "Answer to: " + row["prompt"] for row in rows)
        assert all(row["first_delta_ms"] == "" and float(row["total_ms"]) >= 0 for row in rows)

    asyncio.run(exercise())


def test_stream_timings_and_http_failure_do_not_retry_or_leak_credentials():
    class Chunks(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'data: {"choices":[{"delta":{"reasoning_content":"Considering "}}]}\n\n'
            yield b'data: {"choices":[{"delta":{"content":"Answer"},"finish_reason":"length"}]}\n\n'
            yield b'data: {"choices":[],"usage":{"completion_tokens":12}}\n\n'
            yield b'data: [DONE]\n\n'

    async def exercise():
        requests = []
        secret = "test-secret-not-to-log"

        def handler(request):
            requests.append(request)
            if len(requests) == 1:
                return httpx.Response(200, stream=Chunks(), headers={"content-type": "text/event-stream"})
            return httpx.Response(429, text="Rate limit for " + secret)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            good = await benchmark.call_endpoint(client, options(stream=True), 1, "easy", "Prompt one",
                                                  time.perf_counter(), secret)
            bad = await benchmark.call_endpoint(client, options(stream=True), 2, "easy", "Prompt two",
                                                 time.perf_counter(), secret)
        assert len(requests) == 2
        assert good["success"] and good["truncated"]
        assert good["response"] == "Answer" and good["reasoning"] == "Considering "
        assert good["first_delta_ms"] <= good["first_answer_ms"] <= good["total_ms"]
        assert good["completion_tokens"] == 12 and good["prompt_tokens"] == ""
        assert not bad["success"] and bad["http_status"] == 429
        assert "[REDACTED]" in bad["error"] and secret not in str(bad)

    asyncio.run(exercise())
