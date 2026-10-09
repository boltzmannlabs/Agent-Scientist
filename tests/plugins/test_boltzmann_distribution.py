"""Workflow knowledge survives package-data copying without private state."""

import csv
import json
import re
import tomllib
from pathlib import Path


def test_packaged_knowledge_resolves_registry_and_preserves_contract_limits(tmp_path, monkeypatch):
    from setuptools import Distribution
    from setuptools.command.build_py import build_py

    root = Path(__file__).resolve().parents[2]
    monkeypatch.chdir(root)
    config = tomllib.loads((root / "pyproject.toml").read_text())
    patterns = config["tool"]["setuptools"]["package-data"]["plugins"]
    dist = Distribution({"packages": ["plugins"], "package_data": {"plugins": patterns}})
    dist.script_name = "setup.py"
    command = build_py(dist)
    command.build_lib = str(tmp_path / "build")
    command.ensure_finalized()
    command.run()
    relative = Path("plugins/boltzmann/skills/boltzmann-tools")
    source, packaged = root / relative, tmp_path / "build" / relative
    for path in source.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json", ".csv", ".py"}:
            copy = packaged / path.relative_to(source)
            assert copy.read_bytes() == path.read_bytes()
            text = copy.read_text()
            assert not re.search(r"/home/|X-Goog-Signature=|X-Amz-Signature=|\b[a-f0-9]{24}\b", text)
            if path.suffix == ".json":
                json.loads(text)
    refs = packaged / "references"
    registry = json.loads((refs / "module-registry.v1.json").read_text())
    modules = {entry["id"]: entry for entry in registry["modules"]}
    for entry in modules.values():
        module = refs / entry["path"]
        assert module.resolve().is_relative_to(refs.resolve()) and module.is_file()
    for tool in registry["tools"]:
        if tool.get("status") == "active":
            assert tool["module_id"] in modules
    contracts = json.loads((refs / "tool-contracts.v1.json").read_text())
    assert contracts["status"] == "scaffold"
    assert all(t["contract_status"] == "needs_audit" for t in contracts["tools"].values())
    with (refs / "tool-collection-inventory.csv").open() as handle:
        assert list(csv.DictReader(handle))
    script = packaged / "scripts/peptide_fasta_to_smiles.py"
    compile(script.read_text(), str(script), "exec")  # Inspection does not execute scientific software.
