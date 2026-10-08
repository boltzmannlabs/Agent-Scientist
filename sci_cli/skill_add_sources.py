"""Bounded, non-executing source loading for /Add_skill."""

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
import importlib
import io
import re
import stat
import tempfile
import zipfile

from tools.skills_hub_models import (
    SkillBundle, _parse_frontmatter, _validate_bundle_rel_path, _validate_skill_name,
    _referenced_support_paths,
)

MAX_BYTES = 50 * 1024 * 1024
MAX_FILES = 1000
MAX_CHARS = 100_000


@dataclass
class Source:
    label: str
    text: str = ""
    bundle: SkillBundle | None = None


def bounded_text(text: str) -> str:
    if not text.strip():
        raise ValueError("No readable text found. Paste the relevant text instead.")
    if len(text) > MAX_CHARS:
        raise ValueError("Source exceeds 100,000 characters. Provide a smaller excerpt; nothing was truncated.")
    return text


def validate_bundle(bundle: SkillBundle) -> SkillBundle:
    _validate_skill_name(bundle.name)
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", bundle.name):
        raise ValueError("Skill name must be lowercase, up to 64 characters, with hyphens/underscores only.")
    if not bundle.files or len(bundle.files) > MAX_FILES:
        raise ValueError("Skill packages must contain 1–1,000 files.")
    total = 0
    for name, content in bundle.files.items():
        if _validate_bundle_rel_path(name) != name or "\\" in name:
            raise ValueError(f"Non-canonical package path: {name}")
        if PurePosixPath(name).name == "SKILL.md" and name != "SKILL.md":
            raise ValueError("Multiple skills found. Select one skill folder.")
        total += len(content.encode("utf-8") if isinstance(content, str) else content)
    if total > MAX_BYTES:
        raise ValueError("Skill package exceeds 50 MiB.")
    raw = bundle.files.get("SKILL.md", "")
    text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
    from tools.skill_manager_tool import _validate_frontmatter
    if error := _validate_frontmatter(text):
        raise ValueError(error)
    if _parse_frontmatter(text).get("name") != bundle.name:
        raise ValueError("Frontmatter name must match the skill name. Use Rename to change it.")
    referenced = _referenced_support_paths(text)
    if referenced is None or any(name not in bundle.files for name in referenced):
        raise ValueError("Skill has unsafe or missing supporting files. Provide the complete skill folder/package.")
    return bundle


def bundle_from_files(files: dict, label: str) -> SkillBundle:
    raw = files.get("SKILL.md", "")
    text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
    name = _parse_frontmatter(text).get("name", "")
    return validate_bundle(SkillBundle(name, files, "local", label, "community"))


def read_bytes(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular, non-symlink file: {path}")
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Source exceeds 50 MiB.")
    return data


def folder_bundle(root: Path) -> SkillBundle:
    files, total = {}, 0
    for path in root.rglob("*"):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError(f"Symlinks/junctions are not allowed: {path}")
        if path.is_dir():
            continue
        if len(files) >= MAX_FILES:
            raise ValueError("Skill package exceeds 1,000 files.")
        data = read_bytes(path)
        total += len(data)
        if total > MAX_BYTES:
            raise ValueError("Skill package exceeds 50 MiB.")
        files[path.relative_to(root).as_posix()] = data
    return bundle_from_files(files, str(root))


def zip_bundle(data: bytes, label: str) -> SkillBundle:
    if len(data) > MAX_BYTES:
        raise ValueError("ZIP exceeds 50 MiB input size.")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        if len(entries) > MAX_FILES or sum(e.file_size for e in entries) > MAX_BYTES:
            raise ValueError("ZIP exceeds 1,000 entries or 50 MiB expanded size.")
        files = {}
        for entry in entries:
            name = entry.filename.rstrip("/")
            if _validate_bundle_rel_path(name) != name or "\\" in name:
                raise ValueError("Non-canonical ZIP path.")
            mode = entry.external_attr >> 16
            if entry.flag_bits & 1 or stat.S_ISLNK(mode):
                raise ValueError("Encrypted ZIP entries and symlinks are not supported.")
            if entry.is_dir():
                continue
            if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise ValueError("ZIP contains a special file.")
            if name in files:
                raise ValueError("ZIP contains duplicate paths.")
            files[name] = archive.read(entry)
    roots = [PurePosixPath(p).parent for p in files if PurePosixPath(p).name == "SKILL.md"]
    if len(roots) != 1:
        raise ValueError("ZIP must contain exactly one SKILL.md. Select one skill package.")
    root = roots[0]
    if any(not PurePosixPath(p).is_relative_to(root) for p in files):
        raise ValueError("ZIP has files outside its skill folder.")
    return bundle_from_files({PurePosixPath(p).relative_to(root).as_posix(): v
                              for p, v in files.items()}, label)


def pdf_text(data: bytes) -> str:
    # Bypass read_file's auto-install/hosted-OCR wrapper, not its converter.
    try:
        anydoc = importlib.import_module("anydoc")
    except ImportError as exc:
        raise ValueError("PDF extraction needs the optional doc-extract dependency. Paste text instead; no dependency was installed.") from exc
    with tempfile.TemporaryDirectory(prefix="skill-add-pdf-") as directory:
        path = Path(directory) / "source.pdf"
        path.write_bytes(data)
        try:
            text = anydoc.to_markdown(str(path), ocr="reject")
        except Exception as exc:
            raise ValueError("PDF could not be extracted locally. Scanned/encrypted PDFs are unsupported; paste text instead.") from exc
    if "NEEDS OCR" in text or "NEEDS-OCR" in text:
        raise ValueError("PDF has scanned pages. Provide a text-only source instead.")
    return bounded_text(text)


class _PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.hidden += 1
        elif tag in {"p", "br", "div", "li", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def remote_source(identifier: str) -> Source:
    from tools.skills_hub import _guarded_http_stream, skills_hub_http_session
    from tools.skills_hub_search import create_source_router
    parsed = urlsplit(identifier)
    is_url = parsed.scheme in {"http", "https"}
    if is_url and (parsed.username or parsed.password):
        raise ValueError("Authenticated URLs are not supported. Remove embedded credentials.")
    # Preserve existing adapters for prepared skills and GitHub identifiers.
    if not is_url or parsed.path.lower().endswith(".md") or parsed.hostname in {"github.com", "raw.githubusercontent.com"}:
        with skills_hub_http_session():
            for adapter in create_source_router():
                if bundle := adapter.fetch(identifier):
                    raw = bundle.files.get("SKILL.md", "")
                    body = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
                    if is_url and Path(parsed.path).name != "SKILL.md" and not _parse_frontmatter(body).get("description"):
                        return Source(identifier, text=bounded_text(body))
                    return Source(identifier, bundle=validate_bundle(bundle))
        if not is_url:
            raise ValueError("Skill identifier not found. Use the exact Skills Hub identifier or a URL.")
    with _guarded_http_stream(identifier, timeout=30) as response:
        if response is None or response.status_code != 200:
            raise ValueError("Public source could not be fetched or was blocked by network policy.")
        data = bytearray()
        for chunk in response.iter_bytes():
            data.extend(chunk)
            if len(data) > MAX_BYTES:
                raise ValueError("Download exceeds 50 MiB.")
        content_type = response.headers.get("content-type", "").lower()
    payload = bytes(data)
    suffix = Path(parsed.path).suffix.lower()
    if suffix == ".zip":
        return Source(identifier, bundle=zip_bundle(payload, identifier))
    if suffix == ".pdf" or "application/pdf" in content_type:
        return Source(identifier, text=pdf_text(payload))
    if suffix in {".doc", ".docx"}:
        raise ValueError("Word documents are not supported. Export text or a text-based PDF.")
    text = payload.decode("utf-8-sig")
    if "html" in content_type:
        page = _PageText()
        page.feed(text)
        text = "".join(page.parts)
    return Source(identifier, text=bounded_text(text))


def load_source(value: str) -> Source:
    if value.startswith(("http://", "https://")):
        return remote_source(value)
    path = Path(value).expanduser()
    if path.is_symlink():
        raise ValueError("Choose a regular source, not a symlink.")
    if path.exists():
        path = path.resolve()
        if path.is_dir():
            return Source(str(path), bundle=folder_bundle(path))
        data = read_bytes(path)
        if path.suffix.lower() == ".zip":
            return Source(str(path), bundle=zip_bundle(data, str(path)))
        if path.suffix.lower() == ".pdf":
            return Source(str(path), text=pdf_text(data))
        if path.suffix.lower() not in {".md", ".txt"}:
            raise ValueError("Use SKILL.md, a skill folder/ZIP, text/Markdown, or a text-based PDF.")
        text = data.decode("utf-8-sig")
        if path.name == "SKILL.md":
            files = {"SKILL.md": data}
            relatives = _referenced_support_paths(text)
            if relatives is None:
                raise ValueError("Skill has unsafe supporting-file paths.")
            for relative in relatives:
                candidate = path.parent / relative
                if not candidate.resolve().is_relative_to(path.parent.resolve()):
                    raise ValueError("Skill support file escapes the source folder.")
                files[relative] = read_bytes(candidate)
            return Source(str(path), bundle=bundle_from_files(files, str(path)))
        return Source(str(path), text=bounded_text(text))
    if value.startswith(("http://", "https://")) or ("/" in value and not value.startswith(("/", "~", "."))):
        return remote_source(value)
    raise ValueError("Source path does not exist. Use 'Describe a workflow' for free text.")
