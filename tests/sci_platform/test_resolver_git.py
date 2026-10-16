"""Git recovery searches managed and host layouts without executing them."""

from types import SimpleNamespace

import pm

from sci_platform.resolver import Candidate, Resolution
from sci_platform.resolver import git


def test_managed_and_path_git_layouts_are_passive_candidates(tmp_path, monkeypatch):
    managed = tmp_path / "managed-git"
    host = tmp_path / "host-git"
    monkeypatch.setattr(pm, "installed_package", lambda *a, **kw: SimpleNamespace(path=managed))
    monkeypatch.setattr(git, "locate_command", lambda name: Resolution(
        "path_executable", (Candidate(str(host / "cmd/git.exe"), "PATH", True),)))

    def forbidden(*args, **kwargs):
        raise AssertionError("candidate lookup must not install or execute")

    monkeypatch.setattr(pm, "ensure", forbidden)
    monkeypatch.setattr("subprocess.run", forbidden)
    candidates = git.windows_git_candidates()
    for root in (managed, host):
        for arch in ("clangarm64", "mingw64", "mingw32"):
            assert root / arch / "bin/git.exe" in candidates
            assert root / arch / "libexec/git-core/git.exe" in candidates
    assert candidates[0].is_relative_to(managed)
    assert len(candidates) == len(set(candidates))
