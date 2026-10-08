"""Resolve SCI_HOME for standalone skill scripts.

Skill scripts may run outside the Sci process (system Python, nix env,
CI) where ``sci_constants`` is not importable.  This module provides the
same ``get_sci_home()`` contract without requiring it on ``sys.path``.

When ``sci_constants`` IS available it is used directly so profile
resolution and any future enhancements are picked up automatically.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from sci_constants import get_sci_home as get_sci_home
except (ModuleNotFoundError, ImportError):

    def get_sci_home() -> Path:
        """Return the Sci home directory (default: ``~/.sci``)."""
        val = os.environ.get("SCI_HOME", "").strip()
        return Path(val) if val else Path.home() / ".sci"
