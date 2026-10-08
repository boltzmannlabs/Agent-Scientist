"""Own profile worker lifetimes without switching the parent agent's prompt/state."""

import atexit
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

from sci_cli.skill_add import WizardUI, Cancelled


class Worker:
    def __init__(self, home: Path, cli, ui):
        from tools.environments.local import served_profile_child_env
        from agent.memory_provider import spawn_context_thread
        from sci_cli.science_profiles_sandbox import validate_runtime
        self.spec = validate_runtime(home)
        self.home, self.cli, self.ui = home, cli, ui
        self.session = None
        self.events = queue.Queue()
        self.cancel = getattr(cli, "_science_cancel", None) or threading.Event()
        env = served_profile_child_env(target_home=home)
        # The runner is Sci, not a generated adapter or a user-supplied shell command.
        self.proc = subprocess.Popen([sys.executable, "-m", "sci_cli.science_profile_worker"],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, text=True, bufsize=1, env=env,
                                     cwd=Path(__file__).resolve().parents[1])
        self.reader = spawn_context_thread(self._read, daemon=True, name="science-profile-reader")
        self.reader.start()
        atexit.register(self.close)
        try:
            self.session = self.receive("ready", 60)["session"]
            self.ui.show(f"[{self.spec.name}] Profile ready.")
        except BaseException:
            self.close()
            raise

    def _read(self):
        try:
            while line := self.proc.stdout.readline(1_000_001):
                if len(line) > 1_000_000:
                    raise ValueError("Profile response exceeds transport limit.")
                self.events.put(json.loads(line))
        except Exception as exc:
            self.events.put({"kind": "error", "message": str(exc)})
        finally:
            self.events.put({"kind": "error", "message": "Profile worker exited."})

    def send(self, value):
        self.proc.stdin.write(json.dumps(value) + "\n")
        self.proc.stdin.flush()

    def receive(self, expected, limit):
        start, heartbeat = time.monotonic(), 0
        while True:
            elapsed = time.monotonic() - start
            if self.cancel.is_set():
                raise Cancelled()
            if elapsed > limit:
                raise TimeoutError(f"{self.spec.name} exceeded {limit} seconds; execution stopped.")
            if elapsed >= heartbeat:
                stage = "Starting profile" if expected == "ready" else "Processing request"
                self.ui.show(f"[{self.spec.name}] {stage}: {elapsed:.0f}s elapsed. Ctrl+C cancels.")
                heartbeat += 10
            try:
                item = self.events.get(timeout=0.2)
            except queue.Empty:
                continue
            kind = item.get("kind")
            if kind == expected:
                return item
            if kind in {"error", "stopped"}:
                raise RuntimeError(item.get("message", "Worker stopped."))
            if kind == "clarify":
                answer = self.cli._clarify_callback(item["questions"])
            elif kind in {"external", "approval"}:
                self.ui.show(json.dumps({k: v for k, v in item.items() if k != "kind"}, indent=2))
                answer = self.ui.choose(f"[{self.spec.name}] Approve this specific action/data transfer?", ("Deny", "Approve once", "Cancel")) == "Approve once"
            else:
                raise ValueError("Unexpected profile transport event.")
            self.send({"answer": answer})

    def turn(self, text):
        self.cancel = getattr(self.cli, "_science_cancel", None) or threading.Event()
        if self.cancel.is_set():
            raise Cancelled()
        self.send({"kind": "turn", "text": text})
        try:
            result = self.receive("result", self.spec.max_seconds)
            from sci_cli.science_profiles_sandbox import cleanup_owned_containers
            if not self.spec.setup_pending:
                cleanup_owned_containers(self.spec.name, self.session)
            return result
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        for stream in (self.proc.stdin, self.proc.stdout):
            if stream is not None:
                stream.close()
        atexit.unregister(self.close)
        if self.session and not self.spec.setup_pending:
            from sci_cli.science_profiles_sandbox import cleanup_owned_containers
            try:
                cleanup_owned_containers(self.spec.name, self.session)
            except Exception:
                self.ui.show(f"[{self.spec.name}] Worker stopped, but Docker cleanup could not be verified for session {self.session}. Check Docker before assuming its processes stopped.")
            self.session = None


def cancel_running(cli):
    event = getattr(cli, "_science_cancel", None)
    if event is None:
        return False
    event.set()
    # Cancel any modal so the controller can observe the cancellation promptly.
    clear = getattr(cli, "_clear_active_overlays_for_interrupt", None)
    if callable(clear):
        clear()
    return True


def worker_for(cli, name, ui=None):
    from sci_cli.profiles import get_profile_dir
    from sci_constants import sci_home_key
    key = (sci_home_key(), name)
    workers = getattr(cli, "_science_workers", None)
    if workers is None:
        cli._science_workers = workers = {}
    worker = workers.get(key)
    if worker is None or worker.proc.poll() is not None:
        worker = Worker(get_profile_dir(name), cli, ui or WizardUI(cli))
        workers[key] = worker
    return worker
