"""Display-only replay of a saved transcript. Never stages a message or executes a tool."""

from rich.text import Text
from rich.panel import Panel

import json


def tool_summary(body):
    """A factual preview, never a claim that a saved tool ran successfully."""
    heading, _, payload = body.partition("\n")
    try:
        data = json.loads(payload)
    except (ValueError, TypeError):
        data = None
    preview = ""
    if isinstance(data, dict):
        if heading.startswith("Call "):
            from agent.display import build_tool_preview
            preview = build_tool_preview(heading.removeprefix("Call "), data, max_len=90) or ""
        elif data.get("error"):
            preview = "error: " + str(data["error"])
    preview = " ".join(preview.split())
    if len(preview) > 90:
        preview = preview[:89] + "…"
    return heading + (" · " + preview if preview else "") + f" · {len(payload):,} chars saved"


def render_transcript(cli, entries):
    from cli import _record_output_history_entry, _suspend_output_history
    from sci_cli.cli_render import _render_final_assistant_content
    from sci_cli.cli_agent_setup_mixin import _resume_panel_colors
    text_color, user_color, border_color, assistant_color = _resume_panel_colors()
    # The chat surface shows conversation only. Detailed activity remains in the
    # read-only viewer; filtering here must never change the saved transcript.
    entries = [(role, body) for role, body in entries if role in ("user", "assistant")]
    labels = {"user": ("● You: ", user_color), "assistant": ("◆ Sci: ", assistant_color)}
    if not entries:
        cli._console_print(Text("No retained conversation text is available for this session."))
        return
    for role, body in entries:
        label, color = labels[role]
        if role == "assistant":
            rendered = Panel(_render_final_assistant_content(
                body, mode=getattr(cli, "final_response_markdown", "render")),
                title=Text(label.strip(), style=assistant_color),
                             title_align="left", border_style=border_color)
        else:
            rendered = Text(label, style="bold " + color)
            rendered.append(body, style=text_color)
            rendered.append("\n")
        # One resize-aware entry per message, not one bounded/giant recap. Terminal
        # scrollback contains every emitted message even when the repaint cache rolls over.
        _record_output_history_entry(lambda entry=rendered: cli._render_resume_history_panel_lines(entry))
        with _suspend_output_history():
            cli._console_print(rendered)
    cli._console_print(Text("Conversation restored. Ctrl+O / F8: browse transcript and expand tool details. "
                            "Scroll up to review; continue below. Nothing was rerun.", style="dim"))
