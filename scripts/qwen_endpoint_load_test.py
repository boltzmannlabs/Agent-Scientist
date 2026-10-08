#!/usr/bin/env python3
"""Direct, one-shot load test of an OpenAI-compatible Qwen endpoint (no Sci)."""

import argparse
import asyncio
import csv
import json
import os
from pathlib import Path
import statistics
import time
from datetime import datetime, timezone

import httpx


TOPICS = (
    "DNA", "RNA", "genes", "chromosomes", "proteins", "enzymes", "cell membranes",
    "mitochondria", "ribosomes", "stem cells", "antibodies", "antigens", "vaccines",
    "the immune system", "genetic variation", "inheritance", "mutations", "gene expression",
    "cell division", "photosynthesis", "cellular respiration", "microbiomes",
    "natural selection", "biodiversity", "scientific controls",
)
STYLES = (
    ("easy", "Explain {topic} to a beginner."),
    ("easy", "Give a simple everyday analogy for {topic}, explaining its limits."),
    ("medium", "Explain how {topic} relates to another biological concept, with one example."),
    ("medium", "Describe a common misconception about {topic} and explain the correction."),
)
FIELDS = (
    "request_id", "difficulty", "prompt", "started_utc", "ended_utc", "start_offset_ms",
    "headers_ms", "first_delta_ms", "first_answer_ms", "total_ms", "http_status", "success",
    "finish_reason", "truncated", "response_id", "server_request_id", "returned_model",
    "prompt_tokens", "completion_tokens", "total_tokens", "response", "reasoning", "error",
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def prompts(count):
    # Interleave related topics while keeping each prompt distinct and the workload similar.
    entries = [(level, template.format(topic=topic) + " Answer in at most 80 words.")
               for level, template in STYLES for topic in TOPICS]
    return entries[:count]


async def call_endpoint(client, args, request_id, difficulty, prompt, epoch, api_key):
    started = time.perf_counter()
    row = dict.fromkeys(FIELDS, "")
    row.update(request_id=request_id, difficulty=difficulty, prompt=prompt,
               started_utc=utc_now(), start_offset_ms=round((started - epoch) * 1000, 3),
               success=False, truncated=False)
    payload = {
        "model": args.model, "temperature": args.temperature, "max_tokens": args.max_tokens,
        "messages": [{"role": "system", "content": "Answer clearly and concisely. No tools are available."},
                     {"role": "user", "content": prompt}],
        "stream": args.stream,
    }
    if args.stream:
        payload["stream_options"] = {"include_usage": True}
    parts, reasoning_parts = [], []
    usage, stream_finished = {}, False
    try:
        async with asyncio.timeout(args.timeout):
            async with client.stream("POST", args.base_url.rstrip("/") + "/chat/completions",
                                     json=payload) as response:
                row.update(http_status=response.status_code,
                           headers_ms=round((time.perf_counter() - started) * 1000, 3),
                           server_request_id=response.headers.get("x-request-id", ""))
                if not response.is_success:
                    body = (await response.aread()).decode("utf-8", errors="replace")
                    raise ValueError(f"HTTP {response.status_code}: {body[:2000]}")
                if args.stream:
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            stream_finished = True
                            break
                        if not data:
                            continue
                        chunk = json.loads(data)
                        if chunk.get("error"):
                            raise ValueError(str(chunk["error"]))
                        row["response_id"] = chunk.get("id", row["response_id"])
                        row["returned_model"] = chunk.get("model", row["returned_model"])
                        usage = chunk.get("usage") or usage
                        for choice in chunk.get("choices", []):
                            if choice.get("index", 0) != 0:
                                continue
                            delta = choice.get("delta") or {}
                            answer = delta.get("content") or ""
                            reasoning = delta.get("reasoning_content") or delta.get("reasoning") or ""
                            elapsed = round((time.perf_counter() - started) * 1000, 3)
                            if (answer or reasoning) and row["first_delta_ms"] == "":
                                row["first_delta_ms"] = elapsed
                            if answer and row["first_answer_ms"] == "":
                                row["first_answer_ms"] = elapsed
                            parts.append(answer)
                            reasoning_parts.append(reasoning)
                            if choice.get("finish_reason"):
                                row["finish_reason"] = choice["finish_reason"]
                                stream_finished = True
                    if not stream_finished:
                        raise ValueError("Stream ended without a finish reason or [DONE]")
                else:
                    result = json.loads(await response.aread())
                    if result.get("error"):
                        raise ValueError(str(result["error"]))
                    choice = result["choices"][0]
                    message = choice["message"]
                    parts.append(message.get("content") or "")
                    reasoning_parts.append(message.get("reasoning_content") or message.get("reasoning") or "")
                    row.update(response_id=result.get("id", ""), returned_model=result.get("model", ""),
                               finish_reason=choice.get("finish_reason", ""))
                    usage = result.get("usage") or {}
        if not "".join(parts).strip():
            raise ValueError("No answer content returned (reasoning-only or empty response)")
        row["success"] = True
    except (httpx.HTTPError, TimeoutError, ValueError, KeyError, IndexError, TypeError) as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        row.update(ended_utc=utc_now(), total_ms=round((time.perf_counter() - started) * 1000, 3),
                   response="".join(parts), reasoning="".join(reasoning_parts),
                   truncated=row["finish_reason"] == "length")
        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            row[key] = usage.get(key, "")
        if api_key:
            for key, value in row.items():
                if isinstance(value, str):
                    row[key] = value.replace(api_key, "[REDACTED]")
    return row


def latency_stats(values):
    if not values:
        return None
    ordered = sorted(values)

    def percentile(p):
        position = (len(ordered) - 1) * p
        lower = int(position)
        upper = min(lower + 1, len(ordered) - 1)
        return round(ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower), 3)

    return dict(min=ordered[0], mean=round(statistics.mean(values), 3), p50=percentile(.5),
                p95=percentile(.95), p99=percentile(.99), max=ordered[-1])


async def run_burst(args, api_key, output):
    gate, semaphore = asyncio.Event(), asyncio.Semaphore(args.concurrency)
    active, peak = 0, 0
    epoch = 0.0
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    limits = httpx.Limits(max_connections=args.concurrency, max_keepalive_connections=args.concurrency)
    async with httpx.AsyncClient(headers=headers, limits=limits, timeout=args.timeout,
                                 follow_redirects=False, trust_env=False,
                                 transport=httpx.AsyncHTTPTransport(retries=0, limits=limits)) as client:
        async def worker(index, difficulty, prompt):
            nonlocal active, peak
            await gate.wait()
            async with semaphore:
                active += 1
                peak = max(peak, active)
                try:
                    return await call_endpoint(client, args, index, difficulty, prompt, epoch, api_key)
                finally:
                    active -= 1

        tasks = [asyncio.create_task(worker(i, level, prompt))
                 for i, (level, prompt) in enumerate(prompts(args.requests), 1)]
        await asyncio.sleep(0)  # Let all workers reach the shared start gate.
        epoch = time.perf_counter()
        gate.set()
        rows = []
        with (output / "responses.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            for task in asyncio.as_completed(tasks):
                row = await task
                rows.append(row)
                writer.writerow(row)
                handle.flush()
                if len(rows) % 10 == 0 or len(rows) == args.requests:
                    print(f"Completed {len(rows)}/{args.requests}", flush=True)
        duration = time.perf_counter() - epoch
    successful = [row for row in rows if row["success"]]
    statuses = {}
    for row in rows:
        key = str(row["http_status"] or "no HTTP response")
        statuses[key] = statuses.get(key, 0) + 1
    summary = {
        "base_url": args.base_url, "model": args.model, "requests": args.requests,
        "concurrency": args.concurrency, "peak_client_inflight": peak, "stream": args.stream,
        "max_tokens": args.max_tokens, "temperature": args.temperature, "timeout_seconds": args.timeout,
        "automatic_retries": 0, "successful": len(successful), "failed": len(rows) - len(successful),
        "truncated": sum(row["truncated"] for row in rows), "http_status_counts": statuses,
        "duration_seconds": round(duration, 3),
        "successful_responses_per_second": round(len(successful) / duration, 3),
        "launch_spread_ms": round(max(row["start_offset_ms"] for row in rows)
                                  - min(row["start_offset_ms"] for row in rows), 3),
        "successful_total_latency_ms": latency_stats([row["total_ms"] for row in successful]),
        "successful_first_delta_ms": latency_stats([row["first_delta_ms"] for row in successful
                                                     if row["first_delta_ms"] != ""]),
        "successful_first_answer_ms": latency_stats([row["first_answer_ms"] for row in successful
                                                      if row["first_answer_ms"] != ""]),
        "notes": ["Exactly the requested number of API calls; no warm-up or retries.",
                  "Latency is client-observed: network, queuing and generation are included.",
                  "First delta/answer timing requires --stream; it measures receipt of a text chunk, not server token timing.",
                  "HTTP success alone is insufficient: an empty answer is counted as failure.",
                  "A length-limited answer counts as successful but is also marked truncated.",
                  "Client concurrency does not prove the server generated every response simultaneously."],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (output / "summary.md").write_text(
        "# Qwen direct endpoint benchmark\n\n```json\n" + json.dumps(summary, indent=2) + "\n```\n",
        encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://100.107.80.79:8000/v1")
    parser.add_argument("--model", default="qwen3.8-27b")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=100)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--stream", action="store_true", help="Measure first text-chunk latency using SSE")
    parser.add_argument("--api-key-env", help="Optional environment variable containing a Bearer API key")
    parser.add_argument("--output", type=Path, help="New output directory; must not already exist")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts only; no files or API calls")
    args = parser.parse_args()
    if not 1 <= args.requests <= 100 or args.concurrency < 1 or args.max_tokens < 1 or args.timeout <= 0:
        parser.error("Use 1–100 requests, positive concurrency/max-tokens/timeout")
    if not args.base_url.startswith(("http://", "https://")):
        parser.error("base-url must start with http:// or https://")
    if args.dry_run:
        print(json.dumps(prompts(args.requests), indent=2))
        return 0
    api_key = os.environ.get(args.api_key_env, "") if args.api_key_env else ""
    if args.api_key_env and not api_key:
        parser.error(f"Environment variable {args.api_key_env} is empty")
    output = args.output or Path("outputs") / datetime.now(timezone.utc).strftime("qwen-load-%Y%m%dT%H%M%S-%fZ")
    output.mkdir(parents=True, exist_ok=False)
    print(f"Sending {args.requests} requests with concurrency {args.concurrency}. Results: {output.resolve()}")
    summary = asyncio.run(run_burst(args, api_key, output))
    print(json.dumps(summary, indent=2))
    return 0 if not summary["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
