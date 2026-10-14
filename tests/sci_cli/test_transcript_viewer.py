"""Transcript disclosure is a read-only UI operation, not tool execution or a model turn."""

import asyncio
import copy


def test_keyboard_walkthrough_expands_searches_and_collapses_retained_output():
    from sci_cli.transcript_viewer import build_transcript_application
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    entries = [("user", "Read the fixture"), ("tool", 'Call read_file\n{"path":"fixture.txt"}'),
               ("tool", "Result read_file\n" + "saved line\n" * 2000 + "unique-tail"),
               ("assistant", "**Finished** reading the fixture.")]
    original = copy.deepcopy(entries)

    async def run():
        with create_pipe_input() as pipe:
            app, view = build_transcript_application(entries, input=pipe, output=DummyOutput())
            rendered = asyncio.Event()
            app.after_render += lambda _: rendered.set()
            task = asyncio.create_task(app.run_async())
            await asyncio.wait_for(rendered.wait(), 5)

            async def send(keys):
                rendered.clear()
                pipe.send_text(keys)
                await asyncio.wait_for(rendered.wait(), 5)

            try:
                assert "unique-tail" not in view.area.text
                assert "Finished" in view.area.text
                await send("\t\t\r")
                assert "unique-tail" in view.area.text
                assert view.area.text.count("saved line") == 2000
                assert view.expanded == {2}
                await send("/unique-tail\r")
                assert app.layout.has_focus(view.area)
                assert "unique-tail" in view.area.buffer.document.current_line
                await send("\r")
                assert "unique-tail" not in view.area.text
                assert not view.expanded
                await send("\x05")
                assert view.expanded == {1, 2}
                assert '"path":"fixture.txt"' in view.area.text
                await send("\x05")
                assert not view.expanded
                # A read-only TextArea must not accept edits or trigger any action.
                before = view.area.text
                # A rejected edit alone does not repaint; follow with navigation.
                await send("z\x1b[A")
                assert view.area.text == before
                await send("\x1b[1;5F\r")  # Ctrl+End + Enter on the trailing empty line.
                assert view.area.text == before
                pipe.send_text("q")
                await asyncio.wait_for(task, 5)
            finally:
                if not task.done():
                    app.exit()
                    await task
    asyncio.run(run())
    assert entries == original


def test_cli_shortcuts_preserve_draft_and_are_gated_during_work(monkeypatch):
    from cli import SciCLI
    from sci_cli import transcript_viewer
    from prompt_toolkit.application import Application
    from prompt_toolkit.document import Document
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.output import DummyOutput

    monkeypatch.setenv("SCI_DEFER_AGENT_STARTUP", "1")
    cli = SciCLI(model="fixture", provider="openai-compat", api_key="fixture",
                 base_url="http://127.0.0.1:1/v1")
    cli._tui_init_run_state()
    editor = cli._tui_build_input_area()
    cli._input_area = editor
    cli.conversation_history = [{"role": "user", "content": "retained fixture question"}]
    build = transcript_viewer.build_transcript_application

    async def run():
        with create_pipe_input() as pipe:
            app = Application(layout=Layout(editor), key_bindings=cli._tui_build_key_bindings(),
                              input=pipe, output=DummyOutput())
            cli._app = app
            painted = asyncio.Event()
            viewer_painted = asyncio.Event()
            closed = asyncio.Event()

            def build_viewer(entries, **kwargs):
                viewer, view = build(entries, input=pipe, output=DummyOutput(), **kwargs)
                assert "retained fixture question" in view.area.text
                viewer.after_render += lambda _: viewer_painted.set()
                return viewer, view

            monkeypatch.setattr(transcript_viewer, "build_transcript_application", build_viewer)
            # open_transcript finishes by invalidating the parent, after closing
            # the nested app and releasing the shared terminal input.
            monkeypatch.setattr(cli, "_invalidate", lambda: (closed.set(), app.invalidate()))
            app.after_render += lambda _: painted.set()
            task = asyncio.create_task(app.run_async())
            await asyncio.wait_for(painted.wait(), 5)
            try:
                for key in ("\x0f", "\x1b[19~"):
                    editor.buffer.document = Document("keep my draft", 5)
                    viewer_painted.clear()
                    closed.clear()
                    pipe.send_text(key)
                    await asyncio.wait_for(viewer_painted.wait(), 5)
                    assert cli._transcript_open
                    if key == "\x0f":
                        pipe.send_text("q")
                    else:
                        # A newly arriving approval must reclaim input from the viewer.
                        cli._approval_state = {"pending": True}
                    await asyncio.wait_for(closed.wait(), 5)
                    cli._approval_state = None
                    assert not cli._transcript_open
                    assert (editor.text, editor.buffer.cursor_position) == ("keep my draft", 5)
                for flag in ("_approval_state", "_connection_state", "_agent_running", "_command_running"):
                    previous = getattr(cli, flag, None)
                    setattr(cli, flag, True)
                    for key in ("c-o", "f8"):
                        assert not any(b.filter() for b in app.key_bindings.get_bindings_for_keys((key,)))
                    setattr(cli, flag, previous)
            finally:
                app.exit()
                await task
    asyncio.run(run())
