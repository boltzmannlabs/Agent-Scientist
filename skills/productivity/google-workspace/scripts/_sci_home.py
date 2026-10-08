"""Resolve SCI_HOME for standalone skill scripts.

Skill scripts may run outside the Sci process (e.g. system Python,
nix env, CI) where ``sci_constants`` is not importable.  This module
provides the same ``get_sci_home()`` and ``display_sci_home()``
contracts as ``sci_constants`` without requiring it on ``sys.path``.

When ``sci_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``sci_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``SCI_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from sci_constants import display_sci_home as display_sci_home
    from sci_constants import get_sci_home as get_sci_home
except (ModuleNotFoundError, ImportError):

    def get_sci_home() -> Path:
        """Return the Sci home directory (default: ~/.sci).

        Mirrors ``sci_constants.get_sci_home()``."""
        val = os.environ.get("SCI_HOME", "").strip()
        return Path(val) if val else Path.home() / ".sci"

    def display_sci_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``sci_constants.display_sci_home()``."""
        home = get_sci_home()
        try:
            return "~/" + home.relative_to(Path.home()).as_posix()
        except ValueError:
            return str(home)
