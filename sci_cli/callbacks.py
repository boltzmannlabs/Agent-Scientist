"""Secret-capture prompt for the interactive CLI (``_secret_capture_callback`` backend)."""

import queue
import time as _time

from sci_cli.banner import cprint, _DIM, _RST
from sci_cli.config import save_env_value_secure
from sci_cli.secret_prompt import masked_secret_prompt
from sci_constants import display_sci_home


def _invalidate(cli) -> None:
    if hasattr(cli, "_paint_now"):
        cli._paint_now()
    elif getattr(cli, "_app", None):
        cli._app.invalidate()


def _clear_secret_input(cli) -> None:
    """Drop stale draft input so Enter never stores it as the secret."""
    try:
        if hasattr(cli, "_clear_secret_input_buffer"):
            cli._clear_secret_input_buffer()
        elif getattr(cli, "_app", None):
            cli._app.current_buffer.reset()
    except Exception:
        pass


def _skipped(var_name: str, reason: str, message: str) -> dict:
    return {
        "success": True, "reason": reason, "stored_as": var_name,
        "validated": False, "skipped": True, "message": message}


def _secret_result(var_name: str, value: str, *, persist: bool = True, validator=None) -> dict:
    """Store ``value`` (or report a skip when empty) and build the callback result dict."""
    if not value:
        cprint(f"\n{_DIM}  ⏭ Secret entry skipped{_RST}")
        return _skipped(var_name, "cancelled", "Secret setup was skipped.")
    if validator is not None:
        try:
            valid = validator(value) is True
        except Exception:
            valid = False
        if not valid:
            return {"success": False, "skipped": False, "validated": False,
                    "message": "Credential validation failed or the service was unreachable. Nothing was saved."}
    if not persist:
        return {"success": True, "skipped": False, "value": value}
    try:
        stored = save_env_value_secure(var_name, value)
    except ValueError as exc:  # a locked or denylisted key: the skill setup only logs it, so say why here
        cprint(f"\n  ✗ {exc}")
        raise
    cprint(f"\n{_DIM}  ✓ Stored secret in {display_sci_home()}/.env as {var_name}{_RST}")
    return {
        **stored,
        "validated": validator is not None,
        "skipped": False,
        "message": "Secret stored securely. The secret value was not exposed to the model."}


def prompt_for_secret(cli, var_name: str, prompt: str, metadata=None, *, persist: bool = True, validator=None) -> dict:
    """Prompt for a secret value through the TUI (e.g. API keys for skills).

    Returns a dict with keys: success, stored_as, validated, skipped, message. The secret is stored
    in ~/.sci/.env and never exposed to the model.
    Internal setup wizards may set persist=False to receive the value in memory
    for testing, then commit it only after a separate save confirmation.
    """
    if not getattr(cli, "_app", None):
        if not hasattr(cli, "_secret_state"):
            cli._secret_state = None
        if not hasattr(cli, "_secret_deadline"):
            cli._secret_deadline = 0
        try:
            value = masked_secret_prompt(f"{prompt} (hidden, ESC or empty Enter to skip): ")
        except (EOFError, KeyboardInterrupt):
            value = ""
        return _secret_result(var_name, value, persist=persist, validator=validator)

    response_queue = queue.Queue()
    cli._secret_state = {
        "var_name": var_name,
        "prompt": prompt,
        "metadata": metadata or {},
        "response_queue": response_queue}
    cli._secret_deadline = _time.monotonic() + 120
    if hasattr(cli, "_ring_bell"):
        cli._ring_bell(prompt=True, context=f"secret needed ({var_name})")
    _clear_secret_input(cli)
    _invalidate(cli)

    while True:
        try:
            value = response_queue.get(timeout=1)
        except queue.Empty:
            if cli._secret_deadline - _time.monotonic() <= 0:
                break
            _invalidate(cli)
            continue
        cli._secret_state = None
        cli._secret_deadline = 0
        _invalidate(cli)
        return _secret_result(var_name, value, persist=persist, validator=validator)

    cli._secret_state = None
    cli._secret_deadline = 0
    _clear_secret_input(cli)
    _invalidate(cli)
    cprint(f"\n{_DIM}  ⏱ Timeout — secret capture cancelled{_RST}")
    return _skipped(var_name, "timeout", "Secret setup timed out and was skipped.")
