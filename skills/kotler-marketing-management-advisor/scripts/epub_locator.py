#!/usr/bin/env python3
"""Build a private EPUB locator or emit one bounded, anchored excerpt.

The index stores metadata and locators, never book prose or the source path.
`excerpt` has a non-configurable ceiling and cannot emit a whole XHTML item.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import sys
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


SKILL_DIR = Path(__file__).resolve().parent.parent
MAX_MEMBERS = 20_000
MAX_TOTAL_UNCOMPRESSED = 1_000_000_000
MAX_MEMBER_UNCOMPRESSED = 100_000_000
MAX_MARKUP_BYTES = 8_000_000
MAX_COMPRESSION_RATIO = 200
DEFAULT_EXCERPT_CHARS = 500
MAX_EXCERPT_CHARS = 800


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def normalized_member(name: str) -> str:
    if "\x00" in name:
        raise ValueError("EPUB member contains a null byte")
    normalized = posixpath.normpath(name.replace("\\", "/"))
    if normalized.startswith(("/", "../")) or normalized == "..":
        raise ValueError(f"unsafe EPUB member path: {name}")
    return normalized


def joined_member(base: str, href: str) -> str:
    path_part = href.split("#", 1)[0]
    return normalized_member(posixpath.join(base, path_part))


def stream_digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def validate_archive(archive: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    infos = archive.infolist()
    if len(infos) > MAX_MEMBERS:
        raise ValueError(f"EPUB has too many members ({len(infos)} > {MAX_MEMBERS})")
    total = 0
    result: dict[str, zipfile.ZipInfo] = {}
    for info in infos:
        name = normalized_member(info.filename)
        if info.flag_bits & 0x1:
            raise ValueError(f"encrypted EPUB member is not supported: {name}")
        if info.file_size > MAX_MEMBER_UNCOMPRESSED:
            raise ValueError(f"EPUB member exceeds size limit: {name}")
        total += info.file_size
        if total > MAX_TOTAL_UNCOMPRESSED:
            raise ValueError("EPUB cumulative uncompressed size exceeds limit")
        if info.file_size > 1_000_000 and info.compress_size:
            if info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
                raise ValueError(f"EPUB member has suspicious compression ratio: {name}")
        result[name] = info
    return result


def read_markup(
    archive: zipfile.ZipFile,
    members: dict[str, zipfile.ZipInfo],
    name: str,
) -> bytes:
    normalized = normalized_member(name)
    info = members.get(normalized)
    if info is None:
        raise ValueError(f"EPUB member not found: {normalized}")
    if info.file_size > MAX_MARKUP_BYTES:
        raise ValueError(f"markup member exceeds {MAX_MARKUP_BYTES} bytes: {normalized}")
    return archive.read(info)


def package_document(
    archive: zipfile.ZipFile,
    members: dict[str, zipfile.ZipInfo],
) -> tuple[str, ET.Element]:
    container = ET.fromstring(read_markup(archive, members, "META-INF/container.xml"))
    rootfile = next((node for node in container.iter() if node.tag.rsplit("}", 1)[-1] == "rootfile"), None)
    if rootfile is None or not rootfile.get("full-path"):
        raise ValueError("EPUB container does not identify an OPF package")
    opf_name = normalized_member(rootfile.get("full-path", ""))
    return opf_name, ET.fromstring(read_markup(archive, members, opf_name))


def package_inventory(opf_name: str, root: ET.Element) -> tuple[dict[str, dict[str, str]], list[str], str]:
    base = str(PurePosixPath(opf_name).parent)
    if base == ".":
        base = ""
    manifest: dict[str, dict[str, str]] = {}
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] != "item" or not node.get("id"):
            continue
        manifest[node.get("id", "")] = {
            "item": joined_member(base, node.get("href", "")),
            "media_type": node.get("media-type", ""),
            "properties": node.get("properties", ""),
        }
    spine_node = next((node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "spine"), None)
    spine: list[str] = []
    toc_id = ""
    if spine_node is not None:
        toc_id = spine_node.get("toc", "")
        spine = [node.get("idref", "") for node in spine_node if node.tag.rsplit("}", 1)[-1] == "itemref"]
    return manifest, spine, toc_id


def metadata(opf_name: str, root: ET.Element) -> dict[str, object]:
    values: dict[str, list[str]] = {}
    for node in root.iter():
        local = node.tag.rsplit("}", 1)[-1]
        if local in {"title", "creator", "language", "publisher", "date"} and node.text:
            values.setdefault(local, []).append(node.text.strip())
    return {
        "opf_path": opf_name,
        "title": (values.get("title") or [""])[0],
        "creators": values.get("creator", []),
        "language": (values.get("language") or [""])[0],
        "publisher": (values.get("publisher") or [""])[0],
        "date": (values.get("date") or [""])[0],
    }


def parse_ncx(data: bytes, toc_name: str) -> list[dict[str, object]]:
    root = ET.fromstring(data)
    base = str(PurePosixPath(toc_name).parent)
    if base == ".":
        base = ""
    nav_map = next((node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "navMap"), None)
    entries: list[dict[str, object]] = []

    def walk(node: ET.Element, depth: int) -> None:
        label_node = next((child for child in node.iter() if child.tag.rsplit("}", 1)[-1] == "text"), None)
        content = next((child for child in node if child.tag.rsplit("}", 1)[-1] == "content"), None)
        src = content.get("src", "") if content is not None else ""
        path_part, _, anchor = src.partition("#")
        entries.append({
            "depth": depth,
            "title": (label_node.text or "").strip() if label_node is not None else "",
            "src": src,
            "item": joined_member(base, path_part) if path_part else "",
            "anchor": anchor,
        })
        for child in node:
            if child.tag.rsplit("}", 1)[-1] == "navPoint":
                walk(child, depth + 1)

    if nav_map is not None:
        for child in nav_map:
            if child.tag.rsplit("}", 1)[-1] == "navPoint":
                walk(child, 0)
    return entries


def parse_nav(data: bytes, nav_name: str) -> list[dict[str, object]]:
    root = ET.fromstring(data)
    base = str(PurePosixPath(nav_name).parent)
    if base == ".":
        base = ""
    navs = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "nav"]
    toc = next(
        (node for node in navs if "toc" in (node.get("{http://www.idpf.org/2007/ops}type", "") + " " + node.get("type", "")).split()),
        navs[0] if navs else None,
    )
    entries: list[dict[str, object]] = []

    def walk(node: ET.Element, depth: int) -> None:
        for child in node:
            local = child.tag.rsplit("}", 1)[-1]
            if local == "li":
                link = next((item for item in child if item.tag.rsplit("}", 1)[-1] == "a"), None)
                if link is not None:
                    href = link.get("href", "")
                    path_part, _, anchor = href.partition("#")
                    entries.append({
                        "depth": depth,
                        "title": re.sub(r"\s+", " ", "".join(link.itertext())).strip(),
                        "src": href,
                        "item": joined_member(base, path_part) if path_part else "",
                        "anchor": anchor,
                    })
                for nested in child:
                    if nested.tag.rsplit("}", 1)[-1] in {"ol", "ul"}:
                        walk(nested, depth + 1)
            else:
                walk(child, depth)

    if toc is not None:
        walk(toc, 0)
    return entries


def table_of_contents(
    archive: zipfile.ZipFile,
    members: dict[str, zipfile.ZipInfo],
    manifest: dict[str, dict[str, str]],
    spine: list[str],
    toc_id: str,
) -> tuple[str, list[dict[str, object]]]:
    ncx = manifest.get(toc_id, {}) if toc_id else {}
    if not ncx:
        ncx = next((value for value in manifest.values() if value["media_type"] == "application/x-dtbncx+xml"), {})
    if ncx:
        name = ncx["item"]
        return name, parse_ncx(read_markup(archive, members, name), name)
    nav = next((value for value in manifest.values() if "nav" in value["properties"].split()), {})
    if nav:
        name = nav["item"]
        return name, parse_nav(read_markup(archive, members, name), name)
    fallback = []
    for depth, idref in enumerate(spine):
        item = manifest.get(idref, {}).get("item", "")
        if item:
            fallback.append({"depth": 0, "title": idref or f"spine-{depth + 1}", "src": item, "item": item, "anchor": ""})
    return "spine", fallback


def build_index(epub: Path) -> dict[str, object]:
    with zipfile.ZipFile(epub) as archive:
        members = validate_archive(archive)
        opf_name, opf_root = package_document(archive, members)
        manifest, spine, toc_id = package_inventory(opf_name, opf_root)
        toc_name, toc = table_of_contents(archive, members, manifest, spine, toc_id)
        entries: list[dict[str, object]] = []
        for entry in toc:
            info = members.get(str(entry["item"]))
            entries.append({
                **entry,
                "bytes": info.file_size if info else None,
                "crc32": f"{info.CRC:08x}" if info else None,
            })
        return {
            "schema_version": 2,
            "source_bytes": epub.stat().st_size,
            "source_sha256": stream_digest(epub),
            "metadata": metadata(opf_name, opf_root),
            "toc_path": toc_name,
            "toc": entries,
            "privacy": "No book prose or source path is stored in this index.",
        }


class AnchoredTextExtractor(HTMLParser):
    def __init__(self, anchor: str) -> None:
        super().__init__(convert_charrefs=True)
        self.anchor = anchor
        self.found = False
        self.parts: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id") == self.anchor or values.get("name") == self.anchor:
            self.found = True

    def handle_data(self, data: str) -> None:
        if self.found and data.strip():
            self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


def extract_excerpt(epub: Path, item: str, anchor: str, max_chars: int) -> dict[str, object]:
    if not 1 <= max_chars <= MAX_EXCERPT_CHARS:
        raise ValueError(f"--max-chars must be between 1 and {MAX_EXCERPT_CHARS}")
    anchor = anchor.strip()
    if not anchor or len(anchor) > 256:
        raise ValueError("--anchor must contain 1 to 256 non-whitespace characters")
    normalized = normalized_member(item.split("#", 1)[0])
    if PurePosixPath(normalized).suffix.lower() not in {".html", ".xhtml", ".htm"}:
        raise ValueError("excerpt only supports HTML/XHTML content items")
    with zipfile.ZipFile(epub) as archive:
        members = validate_archive(archive)
        data = read_markup(archive, members, normalized)
    parser = AnchoredTextExtractor(anchor)
    parser.feed(data.decode("utf-8", errors="replace"))
    if not parser.found:
        raise ValueError(f"anchor not found in EPUB item: {anchor}")
    text = parser.text()
    excerpt = text[:max_chars]
    return {
        "locator": f"{normalized}#{anchor}",
        "characters": len(excerpt),
        "truncated": len(text) > max_chars,
        "excerpt": excerpt,
        "notice": "Bounded local excerpt for verification; do not use to reconstruct the book.",
    }


def write_index(output: Path, payload: dict[str, object], force: bool) -> None:
    if output.is_symlink() or (output.exists() and not output.is_file()):
        raise ValueError("index output must be a regular file path, not a directory or symbolic link")
    if output.exists() and not force:
        raise ValueError("index output exists; use --force to create a backup before replacing it")
    output.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if os.name == "posix":
            temporary.chmod(0o600)
        if output.is_symlink() or (output.exists() and not output.is_file()):
            raise ValueError("index output changed and is no longer a regular file path")
        if output.exists():
            if not force:
                raise ValueError("index output appeared during write; refusing to replace it")
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            backup = output.with_name(f"{output.name}.backup-{stamp}-{uuid.uuid4().hex[:8]}")
            os.replace(output, backup)
            if os.name == "posix":
                backup.chmod(0o600)
            print(f"Backed up previous index: {backup}")
        try:
            os.replace(temporary, output)
        except Exception:
            if backup is not None and backup.exists() and not output.exists():
                os.replace(backup, output)
            raise
    except Exception:
        if backup is not None and backup.exists() and not output.exists():
            os.replace(backup, output)
        raise
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index")
    index_parser.add_argument("--epub", type=Path, required=True)
    index_parser.add_argument("--output", type=Path, required=True)
    index_parser.add_argument("--force", action="store_true")

    excerpt_parser = subparsers.add_parser("excerpt")
    excerpt_parser.add_argument("--epub", type=Path, required=True)
    excerpt_parser.add_argument("--item", required=True)
    excerpt_parser.add_argument("--anchor", required=True)
    excerpt_parser.add_argument("--max-chars", type=int, default=DEFAULT_EXCERPT_CHARS)

    args = parser.parse_args()
    if not args.epub.is_file():
        parser.error(f"EPUB not found: {args.epub}")

    try:
        if args.command == "index":
            if is_within(args.output, SKILL_DIR):
                raise ValueError("private index output must be outside the public Skill directory")
            write_index(args.output, build_index(args.epub), args.force)
            print(f"Wrote private metadata index: {args.output}")
            return 0
        print(json.dumps(extract_excerpt(args.epub, args.item, args.anchor, args.max_chars), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
