"""Safe, stage-specific service errors without losing useful validation diagnostics."""

import re

from agent.redact import redact_for_egress


def safe_detail(value, token=""):
    if isinstance(value, dict):
        value = value.get("message") or value.get("msg") or value.get("error") or value.get("detail") or ""
    if isinstance(value, list):
        value = "; ".join(safe_detail(item, token) for item in value[:10])
    if not isinstance(value, str):
        return ""
    if token:
        value = value.replace(token, "[credential redacted]")
    value = re.sub(r"https?://[^\s\"'<>]+", "[service URL redacted]", value)
    value = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", value)
    return redact_for_egress(value)[:2000]


def service_error(stage, response, token=""):
    try:
        body = response.json()
    except ValueError:
        body = {}
    detail = safe_detail(body, token)
    return {"error": detail or f"Service returned HTTP {response.status_code} without a usable diagnostic.",
            "stage": stage, "http_status": response.status_code,
            "status": "unknown" if stage in {"submit", "status"} else "failed",
            "authorization_required": response.status_code in {401, 403},
            "safe_to_retry": False}
