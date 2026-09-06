#!/usr/bin/env python3
"""Inspect a user-owned EPUB without copying it into the public Skill.

The ``index`` command writes only metadata, table-of-contents locators, byte
lengths, and SHA-256 digests. It does not persist book prose. The ``read``
command streams one XHTML item to stdout for private, local research.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET


SKILL_DIR = Path(__file__).resolve().parent.parent


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        value = re.sub(r"\s+", " ", data).strip()
        if value:
            self.parts.append(value)

    def text(self) -> str:
        return "\n".join(self.parts)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_ncx_name(archive: zipfile.ZipFile) -> str:
    for name in archive.namelist():
        if name.lower().endswith(".ncx"):
            return name
    raise ValueError("EPUB does not contain an NCX table of contents")


def parse_toc(data: bytes) -> list[dict[str, object]]:
    root = ET.fromstring(data)
    namespace = {"n": "http://www.daisy.org/z3986/2005/ncx/"}
    nav_map = root.find("n:navMap", namespace)
    if nav_map is None:
        return []

    entries: list[dict[str, object]] = []

    def walk(node: ET.Element, depth: int) -> None:
        label = node.findtext("n:navLabel/n:text", default="", namespaces=namespace)
        content = node.find("n:content", namespace)
        src = content.get("src", "") if content is not None else ""
        entries.append({"depth": depth, "title": label.strip(), "src": src})
        for child in node.findall("n:navPoint", namespace):
            walk(child, depth + 1)

    for top in nav_map.findall("n:navPoint", namespace):
        walk(top, 0)
    return entries


def metadata(archive: zipfile.ZipFile) -> dict[str, object]:
    opf_names = [name for name in archive.namelist() if name.lower().endswith(".opf")]
    if not opf_names:
        return {}
    root = ET.fromstring(archive.read(opf_names[0]))
    ns = {"dc": "http://purl.org/dc/elements/1.1/"}
    return {
        "opf_path": opf_names[0],
        "title": root.findtext(".//dc:title", default="", namespaces=ns),
        "creators": [node.text or "" for node in root.findall(".//dc:creator", ns)],
        "language": root.findtext(".//dc:language", default="", namespaces=ns),
        "publisher": root.findtext(".//dc:publisher", default="", namespaces=ns),
        "date": root.findtext(".//dc:date", default="", namespaces=ns),
    }


def build_index(epub: Path) -> dict[str, object]:
    with zipfile.ZipFile(epub) as archive:
        toc_name = find_ncx_name(archive)
        toc = parse_toc(archive.read(toc_name))
        items: list[dict[str, object]] = []
        for entry in toc:
            src = str(entry["src"]).split("#", 1)[0]
            if not src or src not in archive.namelist():
                continue
            data = archive.read(src)
            items.append(
                {
                    **entry,
                    "item": src,
                    "bytes": len(data),
                    "sha256": sha256(data),
                }
            )
        return {
            "schema_version": 1,
            "source_bytes": epub.stat().st_size,
            "source_sha256": sha256(epub.read_bytes()),
            "metadata": metadata(archive),
            "toc_path": toc_name,
            "toc": items,
            "privacy": "No book prose is stored in this index.",
        }


def read_item(epub: Path, item: str) -> None:
    normalized = item.split("#", 1)[0]
    with zipfile.ZipFile(epub) as archive:
        if normalized not in archive.namelist():
            raise ValueError(f"EPUB item not found: {normalized}")
        parser = TextExtractor()
        parser.feed(archive.read(normalized).decode("utf-8", errors="replace"))
        sys.stdout.write(html.unescape(parser.text()))
        sys.stdout.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index")
    index_parser.add_argument("--epub", type=Path, required=True)
    index_parser.add_argument("--output", type=Path, required=True)

    read_parser = subparsers.add_parser("read")
    read_parser.add_argument("--epub", type=Path, required=True)
    read_parser.add_argument("--item", required=True)

    args = parser.parse_args()
    if not args.epub.is_file():
        parser.error(f"EPUB not found: {args.epub}")

    if args.command == "index":
        if is_within(args.output, SKILL_DIR):
            parser.error(
                "private index output must be outside the public Skill directory"
            )
        result = build_index(args.epub)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return 0
    if args.command == "read":
        read_item(args.epub, args.item)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
