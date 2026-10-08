"""Failure receipts distinguish actionable errors without exposing provider bodies."""

from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from openai import AuthenticationError, RateLimitError, APIConnectionError, APIStatusError

from sci_cli.skill_add_status import SkillAddStatus, report_failure


@pytest.mark.parametrize("kind, expected", [
    ("timeout", "timed out"), ("read-timeout", "timed out"),
    ("auth", "authentication"), ("rate", "rate-limited"),
    ("quota", "billing or quota"), ("network", "could not be reached"),
    ("unknown", "RuntimeError"),
])
def test_error_receipt_is_actionable_and_does_not_leak_response_body(kind, expected):
    request = httpx.Request("POST", "https://fixture.invalid")
    private = "secret-provider-response"
    errors = {
        "timeout": TimeoutError(private),
        "read-timeout": httpx.ReadTimeout(private, request=request),
        "auth": AuthenticationError(private, response=httpx.Response(401, request=request), body=None),
        "rate": RateLimitError(private, response=httpx.Response(429, request=request), body=None),
        "quota": APIStatusError(private, response=httpx.Response(402, request=request), body=None),
        "network": APIConnectionError(message=private, request=request),
        "unknown": RuntimeError(private),
    }
    ui = SimpleNamespace(show=Mock())
    state = SkillAddStatus(provider="fixture", model="fixture", pending=("private inputs",))
    report_failure(ui, state, errors[kind], "DRAFTING")
    receipt = state.render()
    assert expected in receipt and "FAILED" in receipt and "stopped" in receipt
    assert "Nothing was saved or enabled" in receipt and "/Add_skill retry" in receipt
    assert private not in receipt and "private inputs" not in receipt


def test_cleanup_failure_cannot_mask_original_timeout_or_completed_draft(caplog):
    from sci_cli.skill_add_draft import DraftRoute
    client = SimpleNamespace(close=Mock(side_effect=RuntimeError("secret-cleanup-body")))
    route = DraftRoute(client, "fixture", "fixture", "fixture", 131072)
    with pytest.raises(TimeoutError, match="original timeout"):
        try:
            raise TimeoutError("original timeout")
        finally:
            route.close()
    route.close()  # Successful-call cleanup must also remain non-fatal.
    assert "cleanup failed" in caplog.text and "secret-cleanup-body" not in caplog.text
