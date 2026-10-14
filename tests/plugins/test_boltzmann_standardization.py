"""All-catalog contract invariants; fixtures are synthetic, never scientific jobs."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2] / "plugins/boltzmann/skills/boltzmann-tools/references"
CATALOG = json.loads((ROOT / "tool-contracts.v1.json").read_text())


def shape_fixture(schema):
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type", "string")
    if isinstance(kind, list):
        kind = kind[0]
    if kind == "object":
        return {name: shape_fixture(prop) for name, prop in schema.get("properties", {}).items()}
    if kind == "array":
        return [shape_fixture(schema["items"])] if schema.get("items") else []
    if kind in {"integer", "number"}:
        return schema.get("minimum", 1)
    if kind == "boolean":
        return False
    return "1" if schema.get("x-numeric-string") else "fixture"


@pytest.mark.parametrize("job", sorted(CATALOG["tools"]))
def test_every_job_has_one_input_definition_and_accepts_its_documented_shape(job):
    from plugins.boltzmann.contracts import ContractStore
    from plugins.boltzmann.preflight import _contract_digest

    store = ContractStore(ROOT)
    tool = store.tool(job)
    schema = tool["request_schema"]
    props = schema["properties"]
    assert "file_fields" not in tool
    assert set(schema.get("required", [])) <= set(props)
    fixture = shape_fixture(schema)
    for name, bound in store.limits.get(job, {}).get("fields", {}).items():
        assert name in props
        assert "required" not in bound and "type" not in bound
        if "minimum" in bound:
            fixture[name] = bound["minimum"]
        elif "exclusive_minimum" in bound:
            fixture[name] = bound["exclusive_minimum"] + 1
        elif "maximum" in bound:
            fixture[name] = min(1, bound["maximum"])
        if props[name].get("x-numeric-string"):
            fixture[name] = str(fixture[name])
    for group in store.limits.get(job, {}).get("any_of_nonempty", []):
        assert set(group) <= set(props)
        if not any(fixture.get(name) for name in group):
            fixture[group[0]] = ["fixture"]
    for left, right in schema.get("x-equal-fields", []):
        fixture[right] = fixture[left]
    report = store.validate_payload(job, fixture)
    assert not report.errors, (job, report.errors)
    for name in schema.get("required", []):
        missing = dict(fixture)
        del missing[name]
        assert store.validate_payload(job, missing).errors, (job, name, "missing required field accepted")
    for name, prop in props.items():
        # The same schema must reject incompatible wire types, not merely accept
        # the generated happy path. No scientific values are inferred here.
        bad = [] if prop.get("type") == "object" else {}
        assert store.validate_payload(job, dict(fixture, **{name: bad})).errors, (job, name)
        if prop.get("x-numeric-string"):
            assert "string" in prop["type"]
    for condition in schema.get("x-required-if", []):
        assert set(condition["when"]) | set(condition["required"]) <= set(props)
        selected = dict(fixture, **condition["when"])
        for name in condition["required"]:
            missing = dict(selected)
            missing.pop(name, None)
            assert any(name in error for error in store.validate_payload(job, missing).errors)
    for name, prop in store.file_fields(job).items():
        assert prop["type"] == "string"
        if prop["x-input-kind"] != "artifact":
            assert isinstance(store.file_rule(job, name), dict)
    for field in store.files.get(job, {}).get("files", {}):
        assert field in store.file_fields(job)
    # Documentation edits must not invalidate uploaded-byte validation receipts.
    before = _contract_digest(store, job)
    tool["description"] = "Changed documentation only"
    for prop in props.values():
        prop["description"] = "Changed documentation only"
    assert _contract_digest(store, job) == before


def test_file_modes_nested_models_and_known_invalid_values(tmp_path):
    from plugins.boltzmann.contracts import ContractStore
    from plugins.boltzmann.file_validation import validate_file

    store = ContractStore(ROOT)
    assert store.file_rule("rna_siRNA_gen", "input_fasta")["formats"]
    assert not store.file_fields("Multimer_Structure_Prediction")
    with pytest.raises(ValueError):
        store.file_rule("Multimer_Structure_Prediction", "input_path")
    assert store.file_rule("Geometry_Optimization", "molecule_path")
    job = "Lead_Generation_Graph_GA"
    payload = {"smiles": "fixture", "n_mols": 1, "n_steps": 1,
               "global_models": [{"name": "Solubility", "min_threshold": "", "max_threshold": ""}]}
    assert not store.validate_payload(job, payload).errors
    payload["global_models"] = ["Solubility"]
    assert store.validate_payload(job, payload).errors
    fasta = tmp_path / "fixture.fasta"
    fasta.write_text(">fixture\nACGU\n")
    assert not validate_file(fasta, {"formats": ["fasta"]}, {}).errors
    fasta.write_text("ACGU\n")
    assert validate_file(fasta, {"formats": ["fasta"]}, {}).errors
    pdb = tmp_path / "fixture.pdb"
    pdb.write_text("ATOM      1  O   HOH A   1       0.000   0.000   0.000  1.00  0.00           O\nEND\n")
    assert not validate_file(pdb, {"formats": ["pdb"]}, {}).errors
    pdb.write_text("not a coordinate file\n")
    assert validate_file(pdb, {"formats": ["pdb"]}, {}).errors
