# tools.py — unified plugin tool handlers
# 5 handlers: 4 from sci-service (with server-side logging) + boltzmann_log_workflow from hermomics

import json
import os
import time
from agent.memory_provider import spawn_context_thread

from .nodeapi_helpers import (
    submit_request,
    fetch_status,
    download_from_signed_url,
    file_upload,
    fetch_tool_log,
)
from .auth import current_key, fingerprint, require_authorized

# In-memory cache for completed job results: (job_name, doc_id) -> (timestamp, result)
_status_cache: dict[tuple[str, str, str], tuple[float, dict]] = {}
_STATUS_CACHE_TTL = 3600  # 1 hour

# ───────────────────────────────────────────────
# Tool-level timeouts (env var override, sensible defaults)
# ───────────────────────────────────────────────

_TOOL_TIMEOUTS = {
    "boltzmann_submit":        int(os.getenv("TOOL_TIMEOUT_SUBMIT", "120")),       # 2 min
    "boltzmann_status":        int(os.getenv("TOOL_TIMEOUT_STATUS", "600")),       # 10 min (long poll)
    "boltzmann_download":      int(os.getenv("TOOL_TIMEOUT_DOWNLOAD", "300")),     # 5 min (large files)
    "boltzmann_upload":        int(os.getenv("TOOL_TIMEOUT_UPLOAD", "180")),       # 3 min
    "boltzmann_fetch_tool_log": int(os.getenv("TOOL_TIMEOUT_FETCH_LOG", "120")),
}


def _run_with_timeout(fn, tool_name: str, kwargs: dict):
    """Run fn(**kwargs) with a tool-level timeout.

    Returns the function result. On timeout, returns a clean error dict
    so the LLM can understand and retry.
    """
    try:
        require_authorized()
    except PermissionError as exc:
        return json.dumps({"error": str(exc), "authorization_required": True})
    timeout = _TOOL_TIMEOUTS.get(tool_name, 300)
    result_holder = [None]
    error_holder = [None]

    def _worker():
        try:
            result_holder[0] = fn(**kwargs)
        except Exception as exc:
            error_holder[0] = exc

    thread = spawn_context_thread(_worker, name=f"boltzmann-{tool_name}")
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        # Thread is still running — it timed out
        print(f"[{tool_name}] Timed out after {timeout}s")
        return json.dumps({
            "error": f"{tool_name} timed out after {timeout}s. The operation may still be running on the server. Try again or check status separately.",
            "timeout": True,
            "timeout_seconds": timeout,
        })

    if error_holder[0] is not None:
        raise error_holder[0]

    return result_holder[0]


def _get_api_key():
    """Resolve the API key at call time from the active profile scope."""
    return current_key()


def _get_conv_id(kwargs):
    return kwargs.get("conv_id") or ""


def _cache_key(job_name, doc_id):
    return (fingerprint(current_key()), job_name, doc_id)


def _check_cache(job_name, doc_id):
    entry = _status_cache.get(_cache_key(job_name, doc_id))
    if entry is None:
        return None
    ts, result = entry
    if time.monotonic() - ts > _STATUS_CACHE_TTL:
        del _status_cache[_cache_key(job_name, doc_id)]
        return None
    return result


def _store_cache(job_name, doc_id, result):
    status = str(result.get("status", "")).lower().strip()
    if status in ("completed", "success", "100%completed", "failed"):
        _status_cache[_cache_key(job_name, doc_id)] = (time.monotonic(), result)


# ───────────────────────────────────────────────
# Boltzmann platform tools (from sci-service, with server-side logging)
# ───────────────────────────────────────────────

def _handle_boltzmann_submit_inner(**kwargs):
    """Inner logic — extracted so _run_with_timeout can wrap it."""
    job_name = kwargs.get("job_name")
    experiment_data = kwargs.get("experiment_data")
    experiment_name = kwargs.get("experiment_name")

    if isinstance(experiment_data, str):
        try:
            experiment_data = json.loads(experiment_data)
        except json.JSONDecodeError:
            return json.dumps({"error": "experiment_data must be an object, not a JSON string"})

    if isinstance(experiment_data, dict) and not experiment_name:
        experiment_name = experiment_data.pop("experiment_name", None)

    missing = []
    if not job_name:
        missing.append("job_name")
    if not experiment_data:
        missing.append("experiment_data")
    if not experiment_name:
        missing.append("experiment_name")
    if missing:
        return json.dumps({"error": f"Missing required arguments: {', '.join(missing)}"})

    conv_id = _get_conv_id(kwargs)
    token = _get_api_key()

    doc_id = submit_request(experiment_data, job_name, experiment_name, token=token, conv_id=conv_id)

    # Allow the auto-logged pending write to propagate before the next tool
    # call triggers another read-modify-write (critical for multi-step workflows).
    time.sleep(1)

    # submit_request now returns an error dict on auth failures instead of raising
    if isinstance(doc_id, dict) and "error" in doc_id:
        return json.dumps(doc_id)

    return json.dumps({"doc_id": doc_id, "job_name": job_name, "experiment_name": experiment_name})


def handle_boltzmann_submit(**kwargs):
    return _run_with_timeout(_handle_boltzmann_submit_inner, "boltzmann_submit", kwargs)


def _handle_boltzmann_status_inner(**kwargs):
    """Inner logic — extracted so _run_with_timeout can wrap it."""
    job_name = kwargs.get("job_name")
    doc_id = kwargs.get("doc_id")
    if not job_name or not doc_id:
        missing = [k for k in ("job_name", "doc_id") if not kwargs.get(k)]
        return json.dumps({"error": f"Missing required arguments: {', '.join(missing)}. You must provide the job_name and doc_id returned by boltzmann_submit."})

    conv_id = _get_conv_id(kwargs)
    token = _get_api_key()
    output_folder = kwargs.get("output_folder") or os.getenv("output_folder") or None

    cached = _check_cache(job_name, doc_id)
    if cached is not None:
        print(f"[boltzmann_status] Returning cached result for {job_name}/{doc_id}")
        return json.dumps(cached) if isinstance(cached, dict) else cached

    result = fetch_status(job_name, doc_id, token=token, conv_id=conv_id, output_folder=output_folder)

    # Allow the auto-logged terminal write to propagate before the next tool
    # call triggers another read-modify-write (critical for multi-step workflows).
    time.sleep(1)

    # fetch_status now returns an error dict on auth failures instead of raising
    if isinstance(result, dict) and "error" in result:
        return json.dumps(result)

    _store_cache(job_name, doc_id, result)

    if isinstance(result, dict):
        return json.dumps(result)
    return result


def handle_boltzmann_status(**kwargs):
    return _run_with_timeout(_handle_boltzmann_status_inner, "boltzmann_status", kwargs)


def _handle_boltzmann_download_inner(**kwargs):
    """Inner logic — extracted so _run_with_timeout can wrap it."""
    download_url = kwargs.get("download_url")
    output_folder = kwargs.get("output_folder")
    if not download_url or not output_folder:
        missing = [k for k in ("download_url", "output_folder") if not kwargs.get(k)]
        return json.dumps({"error": f"Missing required arguments: {', '.join(missing)}"})
    output_folder = os.path.expanduser(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    token = _get_api_key()
    result = download_from_signed_url([download_url], output_folder, token=token)
    if isinstance(result, dict):
        return json.dumps(result)
    return result


def handle_boltzmann_download(**kwargs):
    return _run_with_timeout(_handle_boltzmann_download_inner, "boltzmann_download", kwargs)


def _handle_boltzmann_upload_inner(**kwargs):
    """Inner logic — extracted so _run_with_timeout can wrap it."""
    local_path = kwargs.get("local_path")
    if not local_path:
        return json.dumps({"error": "Missing required argument: local_path"})
    token = _get_api_key()
    s3_path = file_upload(os.path.expanduser(local_path), token=token)
    # file_upload now returns an error dict on auth failures
    if isinstance(s3_path, dict) and "error" in s3_path:
        return json.dumps(s3_path)
    return json.dumps({"s3_path": s3_path})


def handle_boltzmann_upload(**kwargs):
    return _run_with_timeout(_handle_boltzmann_upload_inner, "boltzmann_upload", kwargs)


# ───────────────────────────────────────────────
# Read-only durable tool log lookup
# ───────────────────────────────────────────────

def _handle_boltzmann_fetch_tool_log_inner(**kwargs):
    collection = kwargs.get("collection")
    experiment_id = kwargs.get("experiment_id")
    if not collection or not experiment_id:
        missing = [k for k in ("collection", "experiment_id") if not kwargs.get(k)]
        return json.dumps({"error": f"Missing required arguments: {', '.join(missing)}"})
    result = fetch_tool_log(collection, experiment_id, token=_get_api_key())
    return json.dumps(result) if isinstance(result, dict) else result


def handle_boltzmann_fetch_tool_log(**kwargs):
    return _run_with_timeout(
        _handle_boltzmann_fetch_tool_log_inner,
        "boltzmann_fetch_tool_log",
        kwargs,
    )
