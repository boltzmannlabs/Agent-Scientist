"""Apply a reviewed SCI source stage after writers stop and a backup is verified."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil

from scripts.sci_namespace_migration import source_files, source_path, replace_names


def apply_stage(root: Path, stage: Path, backup: Path):
    root, stage, backup = root.resolve(), stage.resolve(), backup.resolve()
    if not (backup / "source-before.tar").is_file():
        raise ValueError("Verified source backup is required before applying")
    report = json.loads((stage / "sci-migration-report.json").read_text())
    if Path(report["source"]).resolve() != root or Path(report["stage"]).resolve() != stage:
        raise ValueError("Stage does not belong to this checkout")
    for row in report["changes"]:
        old = root / row["from"]
        if not old.is_file() or hashlib.sha256(old.read_bytes()).hexdigest() != row["before_sha256"]:
            raise ValueError(f"Source changed after rehearsal: {row['from']}")
    names = source_files(root)
    moves = [(name, source_path(name)) for name in names if source_path(name) != name]
    for old, new in moves:
        if (root / new).exists() or (root / new).is_symlink():
            raise ValueError(f"Destination already exists: {new}")
    # Originals remain in a private recovery area. No git checkout/reset and no
    # directory-wide deletion can erase unrelated user changes or research files.
    saved = backup / "moved-files"
    saved.mkdir(exist_ok=False)
    for old, _ in moves:
        path = root / old
        target = saved / old
        target.parent.mkdir(parents=True, exist_ok=True)
        path.rename(target)
    count = 0
    for name in source_files(stage):
        if name == "sci-migration-report.json":
            continue
        source, target = stage / name, root / name
        if source.is_dir() and not source.is_symlink():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".sci-migrate-tmp")
        if temporary.exists() or temporary.is_symlink():
            raise ValueError(f"Unexpected migration temporary file: {temporary}")
        if source.is_symlink():
            linked = Path(os.path.abspath(source.parent / os.readlink(source)))
            link = (os.path.relpath(root / linked.relative_to(stage), target.parent)
                    if linked.is_relative_to(stage) else os.readlink(source))
            temporary.symlink_to(link)
        else:
            shutil.copy2(source, temporary)
        temporary.replace(target)
        count += 1
    # Retain ignored build outputs inside moved namespaces (web_dist etc.).
    # Bytecode and old backup files are recovery material, not active source.
    leftovers = []
    for directory, dirs, files in os.walk(root, topdown=False, followlinks=False):
        parent = Path(directory)
        if ".git" in parent.relative_to(root).parts:
            continue
        for name in [*files, *dirs]:
            path = parent / name
            if path.name == "__pycache__" or path.name.endswith(".orig"):
                target = backup / "generated-and-originals" / path.relative_to(root)
                if path.exists() and not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(path), target)
                continue
            renamed = replace_names(name)
            if renamed == name or not (path.exists() or path.is_symlink()):
                continue
            target = path.with_name(renamed)
            if path.is_dir() and not path.is_symlink() and target.is_dir():
                if not any(path.iterdir()):
                    path.rmdir()
                    continue
                for child in list(path.iterdir()):
                    if (target / child.name).exists():
                        leftovers.append(str(child.relative_to(root)))
                        continue
                    child.rename(target / child.name)
                if not any(path.iterdir()):
                    path.rmdir()
            elif not target.exists():
                path.rename(target)
            else:
                leftovers.append(str(path.relative_to(root)))
    result = {"source": str(root), "backup": str(backup), "files_written": count,
              "leftovers_requiring_review": leftovers}
    (backup / "source-cutover.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--backup", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(apply_stage(args.source, args.stage, args.backup), indent=2))
