"""SCI login opens provider setup, never a vendor portal or a conversation turn."""

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from sci_cli.cli_commands_mixin import CLICommandsMixin
from sci_cli.commands import COMMANDS, resolve_command


@pytest.mark.platforms("posix")
def test_login_real_model_setup_handoff_preserves_profile_and_cached_conversation(tmp_path, monkeypatch):
    import os
    import pty
    import select
    import threading
    from prompt_toolkit import Application
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput
    from sci_cli import relaunch
    from sci_cli.config import atomic_config_replace, read_user_config_raw
    from sci_cli.native_profile_creation import profile_scope

    main = tmp_path / ".sci"
    homes = [main, main / "profiles/a", main / "profiles/b"]
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SCI_HOME", str(main))
    for home in homes:
        home.mkdir(parents=True)
        atomic_config_replace(home / "config.yaml", {"model": {"provider": "fixture", "default": "old"}})
    output = []
    monkeypatch.setattr("cli._cprint", lambda *lines: output.extend(lines))
    # The REAL model command and loaders run in a child. Only its picker is
    # controlled: select no provider, then record a harmless reviewed default.
    code = """
print('fixture setup output ' * 8192, flush=True)
from sci_cli import main
from sci_cli.config import atomic_config_replace, read_user_config_raw
from sci_constants import get_sci_home
from types import SimpleNamespace
main._pick_provider = lambda *args: None
main.cmd_model(SimpleNamespace())
path = get_sci_home() / 'config.yaml'
cfg = read_user_config_raw(path)
cfg['model']['default'] = 'fixture-reviewed-default'
atomic_config_replace(path, cfg)
"""
    monkeypatch.setattr(relaunch, "build_relaunch_argv", lambda args, **kw: [sys.executable, "-c", code])
    master, slave = pty.openpty()
    terminal = os.fdopen(os.dup(slave), "r")
    # A real terminal emulator consumes output continuously. Without a reader,
    # setup can block on the PTY buffer rather than reach its controlled picker.
    stop_reader = threading.Event()
    drained = []

    def drain_terminal():
        while not stop_reader.is_set():
            if select.select([master], [], [], 0.1)[0]:
                data = os.read(master, 65536)
                if not data:
                    break
                drained.append(len(data))

    reader = threading.Thread(target=drain_terminal, daemon=True)
    reader.start()
    monkeypatch.setattr(sys, "stdin", terminal)
    real_spawn = asyncio.create_subprocess_exec
    spawns = []

    async def spawn(*args, **kwargs):
        spawns.append(kwargs["env"]["SCI_HOME"])
        return await real_spawn(*args, **kwargs, stdin=slave, stdout=slave, stderr=slave)

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)

    async def exercise(home):
        with create_pipe_input() as user_input:
            app = Application(input=user_input, output=DummyOutput())
            cli = SimpleNamespace(_app=app, _invalidate=lambda: None, model="cached-model",
                                  conversation_history=[{"role": "user", "content": "hello"}],
                                  agent=SimpleNamespace(system_prompt="cached-prefix", tools=[{"name": "fixture"}]))
            before = json.dumps([cli.model, cli.conversation_history, vars(cli.agent)])
            errors = []

            async def launch():
                try:
                    with profile_scope(home):
                        # Production slash commands enter on a worker thread.
                        await asyncio.to_thread(CLICommandsMixin._handle_login_command, cli, "/LOGIN")
                    while getattr(cli, "_login_setup_open", False):
                        await asyncio.sleep(0.01)
                    assert json.dumps([cli.model, cli.conversation_history, vars(cli.agent)]) == before
                    assert read_user_config_raw(home / "config.yaml")["model"]["default"] == "fixture-reviewed-default"
                except Exception as exc:
                    errors.append(exc)
                finally:
                    app.exit()

            await asyncio.wait_for(app.run_async(pre_run=lambda: app.create_background_task(launch())), timeout=30)
            if errors:
                raise errors[0]

    try:
        for home in (main, homes[1], homes[2], homes[1]):
            asyncio.run(exercise(home))
        assert spawns == [str(home) for home in (main, homes[1], homes[2], homes[1])]
        assert sum("SCI model setup closed" in line for line in output) == 4
        assert resolve_command("LOGIN").name == "login"
        assert "/login" in COMMANDS
        assert "Nous" not in resolve_command("login").describe()
        assert sum(drained) >= 4 * 8192 * len('fixture setup output ')
    finally:
        stop_reader.set()
        reader.join(timeout=5)
        terminal.close()
        os.close(master)
        os.close(slave)


@pytest.mark.parametrize("case", ["busy", "already_open", "noninteractive", "failed", "cancelled", "async_cancel"])
def test_login_honest_outcomes_and_no_implicit_portal(case, monkeypatch):
    from sci_cli import cli_login, relaunch
    from tools.environments import local
    output, spawned = [], []
    monkeypatch.setattr("cli._cprint", lambda *lines: output.extend(lines))
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(isatty=lambda: case != "noninteractive"))
    monkeypatch.setattr(relaunch, "build_relaunch_argv", lambda args, **kw: [sys.executable, "-m", "sci_cli.main", *args])
    monkeypatch.setattr(local, "served_profile_child_env", lambda **kw: {})

    def run(argv, **kwargs):
        spawned.append(argv)
        if case == "cancelled":
            raise KeyboardInterrupt
        return SimpleNamespace(returncode=1)

    monkeypatch.setattr(cli_login.subprocess, "run", run)
    if case == "async_cancel":
        from contextlib import asynccontextmanager

        async def cancel_setup():
            started = asyncio.Event()
            process = SimpleNamespace(returncode=None)
            tasks = []

            async def wait():
                if process.returncode is None:
                    started.set()
                    await asyncio.Event().wait()
                return process.returncode

            def terminate():
                process.returncode = -15

            process.wait, process.terminate = wait, terminate

            async def spawn(*args, **kwargs):
                return process

            @asynccontextmanager
            async def terminal():
                try:
                    yield
                finally:
                    assert process.returncode == -15

            def create_task(coro):
                tasks.append(asyncio.create_task(coro))

            monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
            monkeypatch.setattr("prompt_toolkit.application.in_terminal", terminal)
            app = SimpleNamespace(is_running=True, loop=asyncio.get_running_loop(), create_background_task=create_task)
            cli = SimpleNamespace(_app=app, _invalidate=lambda: None)
            CLICommandsMixin._handle_login_command(cli, "/login")
            await asyncio.wait_for(started.wait(), timeout=2)
            tasks[0].cancel()
            with pytest.raises(asyncio.CancelledError):
                await tasks[0]
            assert not cli._login_setup_open
            assert "cancelled" in output[-1]

        asyncio.run(cancel_setup())
        return
    cli = SimpleNamespace(_app=None, _agent_running=case == "busy", _login_setup_open=case == "already_open")
    CLICommandsMixin._handle_login_command(cli, "/login")
    assert bool(spawned) == (case in {"failed", "cancelled"})
    assert all("nous" not in line.lower() for line in output)
    if spawned:
        assert spawned[0][-1] == "model"
        assert not cli._login_setup_open
        assert ("failed" if case == "failed" else "cancelled") in output[-1]
    else:
        assert len(output) == 1
