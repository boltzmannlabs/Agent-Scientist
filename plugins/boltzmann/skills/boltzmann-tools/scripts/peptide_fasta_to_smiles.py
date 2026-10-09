#!/usr/bin/env python3
"""Convert peptide FASTA records to a validated identity-preserving SMILES CSV."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FastaRecord:
    record_id: str
    sequence: str


def parse_fasta(path: Path) -> list[FastaRecord]:
    records: list[FastaRecord] = []
    header: str | None = None
    sequence_parts: list[str] = []

    def finish_record() -> None:
        if header is None:
            return
        record_id = header.split("|", 1)[0].strip()
        sequence = "".join(sequence_parts)
        if not record_id:
            raise ValueError("Every FASTA record requires a non-empty identifier")
        if not sequence:
            raise ValueError(f"FASTA record {record_id!r} has no sequence")
        if any(character.isspace() for character in sequence):
            raise ValueError(f"FASTA record {record_id!r} contains embedded whitespace")
        records.append(FastaRecord(record_id, sequence))

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            finish_record()
            header = line[1:].strip()
            sequence_parts = []
        else:
            if header is None:
                raise ValueError(f"Sequence data appears before a FASTA header on line {line_number}")
            sequence_parts.append(line)
    finish_record()

    if not records:
        raise ValueError("The input FASTA contains no records")
    id_counts = Counter(record.record_id for record in records)
    duplicates = sorted(record_id for record_id, count in id_counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"FASTA identifiers must be unique: {duplicates}")
    return records


def parse_p2smi_output(path: Path, records: list[FastaRecord]) -> list[str]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != len(records):
        raise RuntimeError(
            f"p2smi converted {len(lines)} of {len(records)} records; refusing a partial mapping"
        )
    smiles_values: list[str] = []
    for index, (record, line) in enumerate(zip(records, lines, strict=True)):
        if not line.startswith(f"{record.sequence}-") or ": " not in line:
            raise RuntimeError(
                f"p2smi output row {index} does not map to FASTA record {record.record_id!r}"
            )
        smiles = line.split(": ", 1)[1].strip()
        if not smiles:
            raise RuntimeError(f"p2smi returned an empty SMILES for {record.record_id!r}")
        smiles_values.append(smiles)
    return smiles_values


def validate_smiles(smiles_values: list[str], records: list[FastaRecord]) -> None:
    try:
        from rdkit import Chem
    except ImportError as exc:
        raise RuntimeError("RDKit is required to validate p2smi output") from exc
    invalid = [
        record.record_id
        for record, smiles in zip(records, smiles_values, strict=True)
        if Chem.MolFromSmiles(smiles) is None
    ]
    if invalid:
        raise RuntimeError(f"p2smi returned invalid SMILES for FASTA records: {invalid}")


def write_csv(
    path: Path,
    records: list[FastaRecord],
    smiles_values: list[str],
    *,
    omit_id: bool,
    id_column: str,
    sequence_column: str,
    smiles_column: str,
) -> None:
    columns = [sequence_column, smiles_column] if omit_id else [id_column, sequence_column, smiles_column]
    if any(not column.strip() for column in columns) or len(set(columns)) != len(columns):
        raise ValueError("Output column names must be non-empty and unique")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(path.name + ".tmp")
    with temporary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for record, smiles in zip(records, smiles_values, strict=True):
            row = {sequence_column: record.sequence, smiles_column: smiles}
            if not omit_id:
                row[id_column] = record.record_id
            writer.writerow(row)
    temporary_path.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert peptide FASTA with p2smi and preserve record identity in a validated CSV."
    )
    parser.add_argument("--input-fasta", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--raw-output", type=Path, help="Path for unmodified p2smi text output")
    parser.add_argument("--omit-id", action="store_true", help="Write only sequence and SMILES columns")
    parser.add_argument("--id-column", default="Sequence_ID")
    parser.add_argument("--sequence-column", default="Sequence")
    parser.add_argument("--smiles-column", default="SMILES")
    args = parser.parse_args()

    input_path = args.input_fasta.resolve()
    output_path = args.output_csv.resolve()
    raw_path = (args.raw_output or output_path.with_suffix(".p2smi")).resolve()
    if len({input_path, output_path, raw_path}) != 3:
        raise ValueError("Input FASTA, output CSV, and raw p2smi output must use different paths")

    records = parse_fasta(input_path)
    sequence_counts = Counter(record.sequence for record in records)
    duplicate_sequences = sorted(sequence for sequence, count in sequence_counts.items() if count > 1)
    if args.omit_id and duplicate_sequences:
        raise ValueError("Cannot omit stable IDs when duplicate peptide sequences are present")

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [
            sys.executable, "-m", "p2smi.fasta2smi",
            "--input_fasta", str(input_path), "--out_file", str(raw_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("p2smi conversion failed: " + (completed.stderr or completed.stdout).strip())

    smiles_values = parse_p2smi_output(raw_path, records)
    validate_smiles(smiles_values, records)
    write_csv(
        output_path,
        records,
        smiles_values,
        omit_id=args.omit_id,
        id_column=args.id_column,
        sequence_column=args.sequence_column,
        smiles_column=args.smiles_column,
    )
    print(json.dumps({
        "input_records": len(records),
        "converted_records": len(smiles_values),
        "duplicate_sequence_count": sum(count - 1 for count in sequence_counts.values()),
        "output_csv": str(output_path),
        "raw_p2smi": str(raw_path),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
