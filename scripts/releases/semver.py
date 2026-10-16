"""Compare stable and canary versions accepted by release feeds.

SCI identities use ``1.M.m.p``; legacy ``X.Y.Z`` remains readable.
Canary identity adds build metadata (``1.M.m.p+canary.<stamp>``) and
compares equal to its stable. Channel records, not SemVer precedence, decide
which canary is newer.
"""
from __future__ import annotations

import re

from sci_cli.update_channel import STABLE_TAG_RE

_CANARY_VERSION_RE = re.compile(r"^[0-9.]+[+]canary[.]20\d{6}T\d{6}Z$")


def is_canary_version(version: str) -> bool:
    """True for the canonical build-metadata canary identity."""
    if not isinstance(version, str) or not _CANARY_VERSION_RE.fullmatch(version):
        return False
    return bool(STABLE_TAG_RE.fullmatch("v" + version.split("+", 1)[0]))


def is_stable_version(version: str) -> bool:
    """True for a final stable version."""
    return isinstance(version, str) and bool(STABLE_TAG_RE.fullmatch("v" + version))


def is_valid_version(version: str) -> bool:
    """True for a stable version or canonical canary identity."""
    return is_stable_version(version) or is_canary_version(version)


def is_release_version(version: str) -> bool:
    """True for a stable version or canonical canary identity."""
    return is_valid_version(version)


def _core(version: str) -> list[int]:
    return [int(part) for part in version.split("+", 1)[0].split(".")]


def package_version(version: str) -> str:
    """Map SCI's identity to ordered SemVer for Electron/Cargo/Tauri only.

    1.M.m.p -> 1.(M*1000+m).p, with m < 1000. Keep source identities and
    provenance unchanged. Existing three-part versions pass through.
    """
    if not is_release_version(version):
        raise ValueError(f"invalid release version: {version!r}")
    parts = _core(version)
    if len(parts) == 3:
        return version
    major, milestone, minor, patch = parts
    if minor >= 1000 or milestone * 1000 + minor > 9007199254740991 or patch > 9007199254740991:
        raise ValueError("Native packaging requires minor < 1000 and safe SemVer numeric fields; advance the milestone")
    suffix = "+" + version.split("+", 1)[1] if "+" in version else ""
    return f"{major}.{milestone * 1000 + minor}.{patch}{suffix}"


def compare(a: str, b: str) -> int:
    """Compare release versions while ignoring build metadata."""
    if not is_release_version(a) or not is_release_version(b):
        raise ValueError(f"invalid release version(s): {a!r}, {b!r}")
    ka, kb = _core(a), _core(b)
    return (ka > kb) - (ka < kb)
