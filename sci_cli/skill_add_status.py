"""CLI-local skill workflow receipts and honest, content-free waiting updates."""

from contextlib import contextmanager
from dataclasses import dataclass
import logging
import threading
import time

logger = logging.getLogger(__name__)
HEARTBEAT_SECONDS = 15
DRAFT_TIMEOUT_SECONDS = 120


class WizardInputTimeout(TimeoutError):
    """Distinguish an expired consent/input modal from a provider timeout."""


@dataclass
class SkillAddStatus:
    phase: str = "NOT STARTED"
    detail: str = "No /Add_skill attempt is recorded in this CLI process."
    pending: tuple | None = None
    provider: str = ""
    model: str = ""
    elapsed: float = 0
    last_progress: float | None = None

    def set(self, phase, detail):
        self.phase, self.detail = phase, detail

    def render(self):
        route = f"\nModel: {self.provider} / {self.model}" if self.provider else ""
        retry = ("\nAnswers retained in this CLI only. Use /Add_skill retry (fresh consent required)."
                 if self.pending is not None and self.phase == "FAILED" else "")
        return f"[Add_skill] {self.phase}: {self.detail}{route}{retry}"


def status_for(cli):
    from sci_constants import sci_home_key
    if not hasattr(cli, "_skill_add_statuses"):
        cli._skill_add_statuses = {}
    return cli._skill_add_statuses.setdefault(sci_home_key(), SkillAddStatus())


def error_detail(exc, stage):
    """Classify provider failures without leaking exception bodies or credentials."""
    if isinstance(exc, WizardInputTimeout):
        return f"{stage}: Waiting for user input timed out. No approval was given for the pending step."
    from agent.auxiliary_client import (
        _is_timeout_error, _is_connection_error, _is_auth_error,
        _is_payment_error, _is_rate_limit_error,
    )
    checks = (
        (_is_timeout_error, "The operation timed out before a usable result arrived. Check connectivity or retry explicitly."),
        (_is_auth_error, "The provider rejected authentication. Check the selected provider's credentials before retrying."),
        (_is_payment_error, "The provider reported a billing or quota problem. Check your account before retrying."),
        (_is_rate_limit_error, "The provider rate-limited this request. Wait before retrying."),
        (_is_connection_error, "The provider or source could not be reached. Check your connection and endpoint before retrying."),
    )
    for matches, explanation in checks:
        if matches(exc):
            return f"{stage}: {explanation}"
    if isinstance(exc, (ValueError, FileNotFoundError, FileExistsError)):
        return f"{stage}: {exc}"
    return f"{stage}: {type(exc).__name__}. The operation failed; no automatic retry was started."


def report_failure(ui, state, exc, stage):
    state.set("FAILED", error_detail(exc, stage) +
              " This attempt has stopped. Nothing was saved or enabled; no draft is running in the background.")
    logger.warning("Add_skill failed stage=%s provider=%s model=%s elapsed=%.1fs error_type=%s",
                   stage, state.provider, state.model, state.elapsed, type(exc).__name__)
    ui.show(state.render())
    ui.show("For this workflow use /Add_skill status. A running Sci process or an unrelated polling script is not evidence that drafting is continuing.")


@contextmanager
def drafting_progress(ui, state):
    """Only the reporting thread is backgrounded; the provider call stays owned
    by the wizard. Stop/join reporting BEFORE printing a terminal outcome."""
    from agent.memory_provider import spawn_context_thread
    started = time.monotonic()
    stopped = threading.Event()
    state.elapsed, state.last_progress = 0, None
    state.set("DRAFTING", "Waiting for the selected provider. Nothing has been saved.")
    ui.show(state.render())
    ui.show(f"Provider request timeout: {DRAFT_TIMEOUT_SECONDS}s; it may fail earlier. "
            "Elapsed-time updates are not percentage-complete estimates. No automatic retry or provider fallback.")

    def notify_progress():
        state.last_progress = time.monotonic()

    def report_wait():
        while not stopped.wait(HEARTBEAT_SECONDS):
            now = time.monotonic()
            state.elapsed = now - started
            detail = ("Waiting for provider output; no result yet." if state.last_progress is None else
                      f"Provider output received; waiting for a complete draft (last signal {now - state.last_progress:.0f}s ago).")
            ui.show(f"[Add_skill] DRAFTING — {state.elapsed:.0f}s elapsed. {detail} Nothing has been saved.")

    reporter = spawn_context_thread(report_wait, name="skill-add-progress")
    reporter.start()
    try:
        yield notify_progress
    finally:
        stopped.set()
        reporter.join()
        state.elapsed = time.monotonic() - started
