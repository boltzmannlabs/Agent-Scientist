"""Passive Git-for-Windows executable candidates, including managed tool stores."""

from pathlib import Path

from sci_platform.resolver.core import locate_command


def windows_git_candidates() -> list[Path]:
    from pm import installed_package

    managed = installed_package("git", allow_outdated=True)
    roots = [Path(base) / "Git" for base in (r"C:\Program Files", r"C:\Program Files (x86)")]
    if managed is not None:
        roots.insert(0, managed.path)
    for candidate in locate_command("git").present:
        executable = Path(candidate.value)
        if executable.parent.name.lower() in {"bin", "cmd"}:
            roots.append(executable.parent.parent)
    # Recent Git distributions place the real executable in <arch>/bin,
    # whereas older layouts used <arch>/libexec/git-core.
    return list(dict.fromkeys(
        root / arch / relative / "git.exe"
        for root in roots
        for arch in ("clangarm64", "mingw64", "mingw32")
        for relative in ("bin", "libexec/git-core")
    ))
