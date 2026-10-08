"""Real provider adapters are isolated from the agent and never fall back."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

from sci_cli import skill_add_draft as drafting
from sci_cli.skill_add_sources import Source


SKILL = "---\nname: research-check\ndescription: Check research inputs.\n---\n# Check\nReport missing inputs.\n"


def test_selected_provider_real_adapter_and_failure_without_fallback(monkeypatch):
    from openai import OpenAI, InternalServerError
    import agent.auxiliary_client as auxiliary
    import agent.model_metadata as metadata

    requests = []
    fail = False

    def transport(request):
        deadline = auxiliary._current_aux_stream_deadline()
        import time
        assert deadline is not None and 0 < deadline - time.monotonic() <= drafting.DRAFT_TIMEOUT_SECONDS
        requests.append(request)
        if fail:
            return httpx.Response(500, json={"error": {"message": "fixture failure"}})
        return httpx.Response(200, json={"id": "fixture", "object": "chat.completion",
            "created": 0, "model": "fixture-model", "choices": [{"index": 0,
            "finish_reason": "stop", "message": {"role": "assistant",
                "content": json.dumps({"SKILL.md": SKILL})}}]})

    def factory(**kwargs):
        return OpenAI(**kwargs, max_retries=0,
                      http_client=httpx.Client(transport=httpx.MockTransport(transport)))

    monkeypatch.setattr(auxiliary, "_create_openai_client", factory)
    monkeypatch.setattr(metadata, "get_model_context_length", lambda *a, **k: 131072)
    fallback = Mock(side_effect=AssertionError("Fallback must not be used"))
    monkeypatch.setattr(auxiliary, "_resolve_api_key_provider", fallback)
    shell = SimpleNamespace(provider="custom", model="fixture-model", api_key="fixture-only",
                            base_url="https://fixture.invalid/v1")
    route = drafting.prepare_route(shell)
    try:
        assert not requests  # Preparing/reviewing a route never sends source text.
        source = Source("fixture notes", "Review missing laboratory inputs.")
        messages = drafting.draft_messages(source, "Research only")
        assert drafting.generate(route, messages, source).name == "research-check"
        body = json.loads(requests[-1].content)
        assert body["model"] == shell.model and body["tools"] == []
        assert body["messages"] == messages
        fail = True
        with pytest.raises(InternalServerError):
            drafting.generate(route, messages, source)
        assert auxiliary._current_aux_stream_deadline() is None
        assert len(requests) == 2  # No retry hidden behind a failed request.
        assert all(r.url.host == "fixture.invalid" for r in requests)
        fallback.assert_not_called()
    finally:
        route.close()


def test_budget_and_generated_executable_files_are_rejected():
    source = Source("fixture notes", "Review inputs.")
    messages = drafting.draft_messages(source, "Research only")
    with pytest.raises(ValueError, match="context budget"):
        drafting.validate_budget(messages, 8192)
    with pytest.raises(ValueError, match="100,000"):
        drafting.validate_budget([{"content": "x" * 100001}], 1000000)
    for files in ({"SKILL.md": SKILL, "scripts/run.py": "raise RuntimeError()"},
                  {"SKILL.md": SKILL, "references/../../escape.md": "unsafe"}):
        response = SimpleNamespace(choices=[SimpleNamespace(finish_reason="stop",
            message=SimpleNamespace(content=json.dumps(files), tool_calls=None))])
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
            create=Mock(return_value=response))))
        with pytest.raises(ValueError):
            drafting.generate(drafting.DraftRoute(client, "fixture", "fixture", "fixture", 131072),
                              messages, source)
