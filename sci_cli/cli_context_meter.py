"""Single-row context occupancy; only the boundary brightness is animated."""

from math import cos, tau
from time import monotonic
from prompt_toolkit.utils import get_cwidth

WHITE = "fg:#FFFFFF bg:#000000"
EMPTY = WHITE + " dim"


def context_meter(percent: float | None, width: int = 16) -> list:
    """Fill left-to-right from usage, never elapsed time; width includes all cells.

    Existing UI redraws drive a subtle boundary-only pulse. No animation state,
    timer, or interpolation may advance the occupied count beyond actual usage.
    """
    percent = max(0, min(100, percent or 0))
    full = int(percent * width / 100)
    fragments = [(WHITE, "▰" * full)]
    if full < width:
        brightness = round(215 + 40 * (1 + cos(tau * monotonic() / 1.2)) / 2)
        fragments.append((f"fg:#{brightness:02X}{brightness:02X}{brightness:02X} bg:#000000", "▱"))
        fragments.append((EMPTY, "·" * (width - full - 1)))
    return fragments


def frame_status(fragments: list, width: int) -> list:
    """Keep the inline meter and surrounding status within the terminal width."""
    used = 0
    middle = []
    for style, text in fragments:
        visible = []
        for char in text:
            cells = get_cwidth(char)
            if used + cells > width:
                break
            visible.append(char)
            used += cells
        middle.append((style, "".join(visible)))
    return middle
