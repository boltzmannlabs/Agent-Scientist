"""Run provider setup off-turn with exclusive ownership of the user's terminal."""

import asyncio
import subprocess
import sys


async def _stop_setup(process):
    if process is None or process.returncode is not None:
        return
    try:
        process.terminate()
    except ProcessLookupError:
        pass  # It exited between the returncode check and the signal.
    try:
        await asyncio.wait_for(process.wait(), timeout=3)
    except asyncio.TimeoutError:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        await process.wait()


def open_model_setup(cli):
    from cli import _cprint
    from sci_constants import get_sci_home
    from sci_cli.relaunch import build_relaunch_argv
    from tools.environments.local import served_profile_child_env

    if getattr(cli, "_agent_running", False) or getattr(cli, "_background_tasks", None):
        _cprint("Finish or cancel running work before opening model setup.")
        return
    if getattr(cli, "_login_setup_open", False):
        _cprint("SCI model setup is already open.")
        return
    app = getattr(cli, "_app", None)
    if not sys.stdin.isatty() or (app is not None and not app.is_running):
        _cprint("Model sign-in requires an interactive terminal. Run `sci model` there.")
        return
    # Snapshot the owning scope BEFORE crossing to the UI loop. Never inherit a
    # launch profile's secrets or chat flags (--resume, --model, --tui).
    env = served_profile_child_env(target_home=get_sci_home(), inherit_credentials=True)
    for key in ("SCI_PROFILE", "SCI_PROFILE_NAME"):
        env.pop(key, None)
    argv = build_relaunch_argv(["model"], preserve_inherited=False)
    cli._login_setup_open = True
    _cprint("Opening SCI model setup: sign in, add providers, or manage saved defaults. "
            "Your current conversation and selected model remain unchanged.")

    def outcome(code):
        if code == 0:
            _cprint("SCI model setup closed. Any saved defaults apply to new sessions. "
                    "Use /model to explicitly switch this conversation.")
        elif code in (130, -2):
            _cprint("SCI model setup cancelled. Your conversation is unchanged. "
                    "Any settings already saved are retained.")
        else:
            _cprint(f"SCI model setup failed (exit {code}). Your conversation is unchanged. "
                    "Any settings already saved are retained. Run /login to try again.")

    if app is None:
        try:
            outcome(subprocess.run(argv, env=env, check=False).returncode)
        except KeyboardInterrupt:
            outcome(130)
        except OSError:
            _cprint("Could not start SCI model setup. Run `sci model` in your terminal.")
        finally:
            cli._login_setup_open = False
        return

    async def run():
        from prompt_toolkit.application import in_terminal
        process = None
        try:
            # The setup child, not prompt_toolkit's composer, owns stdin until
            # it exits. No raw input(), secret capture or model setup in chat.
            async with in_terminal():
                try:
                    process = await asyncio.create_subprocess_exec(*argv, env=env)
                    outcome(await process.wait())
                finally:
                    # Reap the child BEFORE the composer regains terminal input.
                    await _stop_setup(process)
        except asyncio.CancelledError:
            _cprint("SCI model setup cancelled. Any settings already saved are retained.")
            raise
        except OSError:
            _cprint("Could not start SCI model setup. Run `sci model` in your terminal.")
        except Exception as exc:
            _cprint(f"SCI model setup stopped ({type(exc).__name__}). "
                    "Any settings already saved are retained. Run `sci model` in your terminal.")
        finally:
            cli._login_setup_open = False
            cli._invalidate()

    # Slash commands normally arrive on the process-loop worker. Schedule the
    # handoff on the application's loop, never orphan run_in_terminal there.
    app.loop.call_soon_threadsafe(lambda: app.create_background_task(run()))
