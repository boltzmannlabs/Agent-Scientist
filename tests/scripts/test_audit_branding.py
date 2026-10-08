"""Branding triage must retain evidence without calling unknown references safe."""
import subprocess

from scripts.audit_branding import category, inventory


def test_inventory_respects_git_exclusions_and_reports_unknown_copy(tmp_path):
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("private/\n")
    (tmp_path / "private").mkdir()
    (tmp_path / "private" / "notes.txt").write_text("Hermes private research")
    (tmp_path / "guide.md").write_text("# Guide\nUse Hermes login\n")
    (tmp_path / "LICENSE").write_text("Copyright Nous Research\n")
    before = (tmp_path / "guide.md").read_bytes()
    report = inventory(tmp_path)
    rows = {row["path"]: row["categories"] for row in report["files"]}
    assert rows["guide.md"] == {"documentation_review": [2]}
    assert rows["LICENSE"] == {"preserve_attribution": [1]}
    assert "private/notes.txt" not in rows
    assert (tmp_path / "guide.md").read_bytes() == before


def test_vendor_security_and_unclassified_runtime_are_not_product_renames():
    assert category("skill/SKILL.md", "author: Nous Research") == "preserve_attribution"
    assert category("tools/security.py", 'signature = "hermes-0day"') == "preserve_security_reference"
    assert category("ui/package.json", '"@nous-research/ui": "1.0.0"') == "external_dependency_review"
    assert category("cli.py", 'print("Welcome to Hermes")') == "runtime_or_vendor_identity_review"
