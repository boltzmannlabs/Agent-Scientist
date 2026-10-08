"""Source parsing never executes a package or trusts archive paths."""

from contextlib import contextmanager
import io
import stat
from types import SimpleNamespace
from unittest.mock import Mock
import zipfile

import pytest
from sci_cli import skill_add_sources as sources

SKILL = "---\nname: safe-workflow\ndescription: Check research inputs.\n---\n# Check\nRead inputs.\n"


def archive(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as z:
        for name, value in files:
            z.writestr(name, value)
    return stream.getvalue()


def test_local_imports_preserve_support_files(tmp_path):
    root = tmp_path / "workflow"
    root.mkdir()
    (root / "references").mkdir()
    (root / "SKILL.md").write_text(SKILL + "[Guide](references/guide.md)\n")
    (root / "references/guide.md").write_text("reference")
    for path in (root, root / "SKILL.md"):
        bundle = sources.load_source(str(path)).bundle
        assert bundle.files["SKILL.md"] == (root / "SKILL.md").read_bytes()
        assert bundle.files["references/guide.md"] == b"reference"
    zipped = tmp_path / "workflow.zip"
    zipped.write_bytes(archive([("bundle/SKILL.md", SKILL), ("bundle/scripts/do-not-run.py", "raise RuntimeError('never execute')")]))
    bundle = sources.load_source(str(zipped)).bundle
    assert "scripts/do-not-run.py" in bundle.files


@pytest.mark.parametrize("entries", [
    [("../SKILL.md", SKILL)], [("/SKILL.md", SKILL)],
    [("a/SKILL.md", SKILL), ("b/SKILL.md", SKILL)],
    [("SKILL.md", SKILL), ("SKILL.md", SKILL)],
    [("SKILL.md", SKILL), ("C:secret", "x")],
])
def test_rejects_unsafe_archives(entries):
    with pytest.raises(ValueError):
        sources.zip_bundle(archive(entries), "fixture")


def test_rejects_symlinks_and_size_limits(tmp_path, monkeypatch):
    link = zipfile.ZipInfo("link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with pytest.raises(ValueError, match="symlinks"):
        sources.zip_bundle(archive([("SKILL.md", SKILL), (link, "outside")]), "fixture")
    monkeypatch.setattr(sources, "MAX_BYTES", 8)
    with pytest.raises(ValueError, match="50 MiB"):
        sources.zip_bundle(archive([("SKILL.md", SKILL)]), "fixture")
    path = tmp_path / "large.txt"
    path.write_text("123456789")
    with pytest.raises(ValueError, match="50 MiB"):
        sources.load_source(str(path))


def test_web_and_skill_url_use_existing_fetch_boundaries(monkeypatch):
    import tools.skills_hub as hub
    import tools.skills_hub_search as search
    bundle = sources.bundle_from_files({"SKILL.md": SKILL}, "fixture")
    adapter = SimpleNamespace(fetch=Mock(return_value=bundle))
    monkeypatch.setattr(search, "create_source_router", lambda: [adapter])
    assert sources.load_source("https://example.org/SKILL.md").bundle == bundle
    adapter.fetch.assert_called_once_with("https://example.org/SKILL.md")
    @contextmanager
    def page(url, **kwargs):
        yield SimpleNamespace(status_code=200, headers={"content-type": "text/html"},
                              iter_bytes=lambda: iter([b"<h1>Procedure</h1><script>ignore</script><p>Check inputs.</p>"]))
    monkeypatch.setattr(hub, "_guarded_http_stream", page)
    source = sources.load_source("https://example.org/procedure")
    assert "Check inputs." in source.text and "ignore" not in source.text
    with pytest.raises(ValueError, match="Authenticated"):
        sources.load_source("https://user:password@example.org/procedure")


def test_pdf_is_local_no_install_no_ocr_and_unsupported_formats_fail(tmp_path, monkeypatch):
    converter = Mock(return_value="Research text")
    monkeypatch.setattr(sources.importlib, "import_module", lambda name: SimpleNamespace(to_markdown=converter))
    assert sources.pdf_text(b"%PDF fixture") == "Research text"
    assert converter.call_args.kwargs == {"ocr": "reject"}
    converter.side_effect = ValueError("scanned")
    with pytest.raises(ValueError, match="Scanned/encrypted"):
        sources.pdf_text(b"%PDF fixture")
    monkeypatch.setattr(sources.importlib, "import_module", Mock(side_effect=ImportError))
    with pytest.raises(ValueError, match="no dependency was installed"):
        sources.pdf_text(b"%PDF fixture")
    word = tmp_path / "procedure.docx"
    word.write_bytes(b"fixture")
    with pytest.raises(ValueError, match="text-based PDF"):
        sources.load_source(str(word))
    with pytest.raises(ValueError, match="nothing was truncated"):
        sources.bounded_text("x" * (sources.MAX_CHARS + 1))


def test_archive_encryption_file_count_and_missing_support_are_rejected(monkeypatch):
    data = bytearray(archive([("SKILL.md", SKILL)]))
    # Set the ZIP encryption bit in both real headers, without constructing an
    # encrypted payload: validation must reject before attempting decryption.
    import struct
    for signature, offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
        position = data.index(signature) + offset
        flags = struct.unpack_from("<H", data, position)[0]
        struct.pack_into("<H", data, position, flags | 1)
    with pytest.raises(ValueError, match="Encrypted"):
        sources.zip_bundle(bytes(data), "fixture")
    monkeypatch.setattr(sources, "MAX_FILES", 1)
    with pytest.raises(ValueError, match="1,000"):
        sources.zip_bundle(archive([("SKILL.md", SKILL), ("extra.md", "text")]), "fixture")
    with pytest.raises(ValueError, match="missing supporting"):
        sources.bundle_from_files({"SKILL.md": SKILL + "[Guide](references/missing.md)"}, "fixture")


def test_real_text_pdf_extraction():
    pytest.importorskip("anydoc", reason="Optional PDF converter is not installed")
    # Minimal real text-layer PDF, generated locally (no network or private input).
    stream = b"BT /F1 12 Tf 30 100 Td (Research fixture text) Tj ET"
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 150] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"]
    data, offsets = b"%PDF-1.4\n", [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += str(index).encode() + b" 0 obj\n" + obj + b"\nendobj\n"
    xref = len(data)
    data += b"xref\n0 6\n0000000000 65535 f \n"
    data += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
    data += b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n" + str(xref).encode() + b"\n%%EOF\n"
    assert "Research fixture text" in sources.pdf_text(data)
