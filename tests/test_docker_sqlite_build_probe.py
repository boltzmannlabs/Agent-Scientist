"""The actual Docker build probe must query the text it inserted."""

from pathlib import Path
import re
import sqlite3


def test_docker_sqlite_probe_matches_its_inserted_text():
    source = (Path(__file__).resolve().parents[1] / "Dockerfile").read_text()
    statements = re.findall(r'db\.execute\(\\"([^"\n]+)\\"\)', source)
    assert statements, "Docker's SQLite qualification statements were not found"
    with sqlite3.connect(":memory:") as db:
        results = []
        for statement in statements:
            cursor = db.execute(statement)
            if statement.startswith("SELECT"):
                results.append(cursor.fetchone()[0])
    assert results and all(count == 1 for count in results)
