"""Context fill tracks usage, while the framed status never overlaps the input."""
from cli import SciCLI
from sci_cli.cli_context_meter import context_meter


def make_cli(width=100):
    cli = SciCLI.__new__(SciCLI)
    cli.model = "test-model"
    cli._status_bar_visible = True
    cli._status_bar_field_set_cache = None
    cli._get_tui_terminal_width = lambda: width
    cli._is_session_yolo_active = lambda: False
    return cli


def test_fill_is_monotonic_and_preserves_endpoints_at_every_meter_width(monkeypatch):
    monkeypatch.setattr("sci_cli.cli_context_meter.monotonic", lambda: 0)
    for width in (6, 12, 16, 18, 20, 22):
        previous = -1
        for percent in range(101):
            fragments = context_meter(percent, width)
            text = "".join(v for _, v in fragments)
            assert SciCLI._status_bar_display_width(text) == width
            full = int(percent * width / 100)
            assert full >= previous
            assert text == "▰" * full + ("▱" + "·" * (width - full - 1) if full < width else "")
            previous = full
        assert context_meter(None, width) == context_meter(0, width)
        assert context_meter(-1, width) == context_meter(0, width)
        assert context_meter(101, width) == context_meter(100, width)

    for percent in (0, 1, 45, 61, 99, 100):
        monkeypatch.setattr("sci_cli.cli_context_meter.monotonic", lambda: 0)
        first = context_meter(percent)
        monkeypatch.setattr("sci_cli.cli_context_meter.monotonic", lambda: 0.6)
        second = context_meter(percent)
        assert [v for _, v in first] == [v for _, v in second]
        assert first[0] == second[0]
        if percent < 100:
            assert first[1][0] != second[1][0]
            assert first[2] == second[2]
        else:
            assert first == second


def test_frame_fits_on_resize_preserves_usage_and_leaves_input_below(monkeypatch):
    monkeypatch.setattr("sci_cli.cli_context_meter.monotonic", lambda: 0)
    from prompt_toolkit.application import Application
    from prompt_toolkit.application.current import set_app
    from prompt_toolkit.layout import HSplit, Layout, Window
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.layout.mouse_handlers import MouseHandlers
    from prompt_toolkit.layout.screen import Screen, WritePosition
    from prompt_toolkit.output import DummyOutput

    cli = make_cli()
    snapshot = dict(model_short="test-model", duration="1m", context_percent=74,
                    context_tokens=74400, context_length=100000, session_title="",
                    avg_velocity_label="3 t/s", prompt_elapsed="⏲ 5s", idle_since="✓ 4s")
    cli._get_status_bar_snapshot = lambda: snapshot
    for width in (140, 100, 80, 76, 60, 40, 100):
        cli._get_tui_terminal_width = lambda: width
        fragments = cli._get_status_bar_fragments()
        lines = "".join(v for _, v in fragments).splitlines()
        height = cli._status_bar_height()
        assert len(lines) == height == 1
        assert all(cli._status_bar_display_width(line) <= width for line in lines)
        middle = lines[height // 2]
        assert "test-model" in middle
        if width >= 76:
            assert "74%" in middle
            # Fill uses the unrounded token ratio, not the integer label.
            start = next(i for i, (_, value) in enumerate(fragments) if "▰" in value)
            meter = "".join(value for _, value in fragments[start:start + 3])
            expected = context_meter(74.4, len(meter))
            assert fragments[start:start + len(expected)] == expected
            assert set(meter) <= set("▰▱·")
        if width == 140:
            assert "3 t/s" in middle and "1m" in middle
        if width == 76:
            assert "3 t/s" not in middle

        root = HSplit([
            Window(FormattedTextControl(cli._get_status_bar_fragments),
                   height=cli._status_bar_height, wrap_lines=False),
            Window(FormattedTextControl("INPUT"), height=1),
        ])
        app = Application(layout=Layout(root), output=DummyOutput())
        screen = Screen()
        with set_app(app):
            root.write_to_screen(screen, MouseHandlers(), WritePosition(0, 0, width, height + 1),
                                 "", True, None)
        if width >= 76:
            cells = [screen.data_buffer[0][x].char for x in range(width)]
            assert cells.count("▰") == meter.count("▰")
            assert cells.count("▱") == 1
        assert "".join(screen.data_buffer[height][x].char for x in range(5)) == "INPUT"

    cli._status_bar_field_set_cache = frozenset({"model", "duration"})
    assert cli._status_bar_height() == 1
    assert "┌" not in "".join(v for _, v in cli._get_status_bar_fragments())
