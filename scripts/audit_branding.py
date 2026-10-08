"""Read-only inventory of inherited names in the distributable working tree.

Print JSON to stdout. Categories are triage, not automatic permission to delete
or a certification that every remaining line has received human review.
Git history, ignored local state and binary assets are outside this text scan.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess

PATTERN = re.compile(r"hermes|nous[ -]?research", re.I)
REPORT = "BRANDING_INVENTORY.json"


def category(path: str, line: str) -> str:
    """Keep functional/vendor identifiers distinct from unresolved product copy."""
    low = line.lower()
    parts = Path(path).parts
    if path == REPORT:
        raise ValueError("the inventory must not inventory itself")
    if (
        "license" in Path(path).name.lower()
        or path == ".mailmap" or path.startswith("contributors/")
        or re.search(r"^\s*(author[s]?\s*[:=]|copyright|#?\s*originally authored)", line, re.I)
        or "provenance" in Path(path).name.lower()
    ):
        return "preserve_attribution"
    if parts[0] in {"tests", "tests-js", "evals"} or re.search(r"\.(test|spec)\.", path):
        return "test_or_fixture_review_with_runtime"
    if path in {"scripts/sci_home_migration.py", "scripts/sci_namespace_migration.py", "sci_cli/default_soul.py"}:
        return "preserve_migration_identity"
    if "hermes-0day" in low or "ghsa-" in low or "cve-" in low:
        return "preserve_security_reference"
    if path.startswith("plugin-catalog/"):
        return "preserve_external_catalog_identity"
    if Path(path).name in {"uv.lock", "package-lock.json", "Cargo.lock", "flake.lock"} or re.search(
        r"@nous-research/|hermes-parser|hermes-estree|nousresearch/(?:misaki|atropos|hermes-[234])", low
    ):
        return "external_dependency_review"
    if re.search(r"github\.com/nousresearch/hermes-agent/(?:issues|pull|commit)/", low):
        return "preserve_historical_reference"
    if path in {"SCI_MIGRATION.md", "BRANDING_REVIEW.md", "scripts/audit_branding.py"}:
        return "audit_record"
    if re.search(r"https?://[^\s\"'<>)]*nousresearch|nousresearch/hermes-sandbox", low):
        return "service_or_source_review"
    if path.startswith(("website/", "skills/", "optional-skills/")) or path.endswith(".md"):
        return "documentation_review"
    return "runtime_or_vendor_identity_review"


def inventory(root: Path) -> dict:
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root, check=True, capture_output=True,
    ).stdout.decode().split("\0")
    files = []
    counts: Counter = Counter()
    scanned = 0
    for name in sorted(set(listed) - {"", REPORT}):
        path = root / name
        if path.is_symlink() or not path.is_file():
            continue
        scanned += 1
        raw = path.read_bytes()
        if b"\0" in raw:
            continue
        matches: dict[str, list[int]] = {}
        for number, line in enumerate(raw.decode("utf-8", errors="replace").splitlines(), 1):
            if not PATTERN.search(line):
                continue
            key = category(name, line)
            matches.setdefault(key, []).append(number)
            counts[key] += 1
        if matches:
            files.append({"path": name, "categories": matches})
    return {
        "scope": "existing tracked and untracked non-ignored regular files; no Git history or binary inspection",
        "policy": "BRANDING_REVIEW.md; review categories are unresolved, not approved exceptions",
        "scanned_files": scanned,
        "matched_files": len(files),
        "matching_lines_by_category": dict(sorted(counts.items())),
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(inventory(args.root), indent=2))


if __name__ == "__main__":
    main()
