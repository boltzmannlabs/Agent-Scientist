"""Prepare a separate SCI source tree; never edit the running checkout or user home.

This is a one-time mechanical refactor tool, not a runtime compatibility layer.
External service identities and legal notices are intentionally preserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


REPLACEMENTS = {"hermes": "sci", "Hermes": "Sci", "HERMES": "SCI"}
NAME = re.compile("hermes|Hermes|HERMES")
EXTERNAL = re.compile(
    r"(?:https?://|git@)[^\s<>\"'`]+"
    r"|(?:NousResearch|nousresearch|nous)/[^\s<>\"'`]+"
    r"|(?:Hermes|hermes)-\d[^\s<>\"'`,)]*"
    r"|hermes-(?:parser|estree)\b"  # Third-party npm package identities, not our branding.
)
SKIP_ROOTS = {"artifacts", "outputs", "ref_imgs", "science-library"}
LEGAL_NAMES = {"LICENSE", "LICENSE.md", "LICENSE.txt", "NOTICE", "NOTICE.md", "COPYING"}
SELF = Path("scripts/sci_namespace_migration.py")


def replace_names(text: str) -> str:
    return NAME.sub(lambda match: REPLACEMENTS[match[0]], text)


def source_path(path: str) -> str:
    # Catalog filenames are ours; their external repository/name fields are not.
    return replace_names(path)


def rewrite(text: str, path: str) -> str:
    if Path(path).name in LEGAL_NAMES or path == str(SELF):
        return text
    protected: list[str] = []

    def hold(match):
        protected.append(match[0])
        return f"__SCI_MIGRATION_LITERAL_{len(protected) - 1}__"

    text = EXTERNAL.sub(hold, text)
    lines = []
    for line in text.splitlines(keepends=True):
        # Legal/authorship metadata and registered OAuth client IDs are not branding.
        preserve = (re.search(r"(?i)copyright|SPDX-|^\s*author[s]?\s*[:=]", line)
                    or ("CLIENT_ID" in line and re.search(r'[= :]\s*[\"\']hermes', line)))
        if path.startswith("plugin-catalog/") and re.match(r"^(name|repository|url|repo):", line):
            preserve = True
        lines.append(line if preserve else replace_names(line))
    text = "".join(lines)
    text = re.sub(r"__SCI_MIGRATION_LITERAL_(\d+)__",
                  lambda match: protected[int(match[1])], text)
    if path == "hermes_cli/_parser.py":
        text = text.replace('prog="sci"', 'prog="agent-sci"')
        text = re.sub(r"(?m)^(\s+)sci(?=\s|$)", r"\1agent-sci", text)
    return text


def source_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True, capture_output=True,
    )
    return sorted({name for raw in result.stdout.split(b"\0") if raw
                   for name in [os.fsdecode(raw)]
                   if Path(name).parts[0] not in SKIP_ROOTS
                   and not name.endswith(".orig")
                   and ((root / name).exists() or (root / name).is_symlink())})


def prepare(root: Path, destination: Path) -> dict:
    root, destination = root.resolve(), destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination must not exist; no existing tree will be overwritten")
    if destination.is_relative_to(root):
        raise ValueError("Stage outside the running checkout")
    names = source_files(root)
    mapped = {name: source_path(name) for name in names}
    if len(set(mapped.values())) != len(mapped):
        raise ValueError("Rename collision; review the path map before proceeding")
    estimate = sum((root / name).lstat().st_size for name in names)
    if shutil.disk_usage(destination.parent).free < estimate * 2 + 2 * 1024**3:
        raise ValueError("Insufficient free space for staged sources and a safety margin")
    subprocess.run(["git", "clone", "--shared", "--no-checkout", str(root), str(destination)], check=True)
    rows = []
    for name in names:
        source, target = root / name, destination / mapped[name]
        if source.is_dir() and not source.is_symlink():  # submodules are independently owned
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            resolved = source.resolve()
            if resolved.is_relative_to(root):
                new_target = destination / source_path(str(resolved.relative_to(root)))
                target.symlink_to(os.path.relpath(new_target, target.parent))
            else:
                target.symlink_to(os.readlink(source))
            continue
        before = source.read_bytes()
        after = before
        if b"\0" not in before:
            try:
                after = rewrite(before.decode("utf-8"), name).encode("utf-8")
            except UnicodeDecodeError:
                pass  # opaque binary assets are not renamed internally
        target.write_bytes(after)
        shutil.copystat(source, target)
        if before != after or name != mapped[name]:
            rows.append({"from": name, "to": mapped[name],
                         "before_sha256": hashlib.sha256(before).hexdigest(),
                         "after_sha256": hashlib.sha256(after).hexdigest()})
    # The public launcher keeps the user's established spelling.
    launcher = destination / "agent-sci"
    shutil.copy2(destination / "sci", launcher)
    project = destination / "pyproject.toml"
    text = project.read_text()
    text = text.replace('[project.scripts]\n', '[project.scripts]\nagent-sci = "sci_cli.main:main"\n', 1)
    project.write_text(text)
    report = {"source": str(root), "stage": str(destination), "files": len(names),
              "changed": len(rows), "changes": rows, "live_home_modified": False}
    (destination / "sci-migration-report.json").write_text(json.dumps(report, indent=2) + "\n")
    return {key: value for key, value in report.items() if key != "changes"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.stage), indent=2))


if __name__ == "__main__":
    main()
