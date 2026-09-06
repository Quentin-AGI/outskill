#!/usr/bin/env python3
"""Deterministic regression tests for privacy, installation, and year rollover."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent


def load_script(name: str):
    path = SKILL_DIR / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScriptRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.updates = load_script("check_updates")
        cls.epub = load_script("epub_locator")
        cls.installer = load_script("install")

    def test_cross_year_sources_include_current_and_previous_year(self) -> None:
        manifest = json.loads(
            (SKILL_DIR / "references/sources/update-sources.json").read_text(
                encoding="utf-8"
            )
        )
        expanded = self.updates.expand_sources(manifest["sources"], year=2027)
        ids = {item["id"] for item in expanded}
        self.assertIn("BRK-NEWS-2027", ids)
        self.assertIn("BRK-NEWS-2026", ids)

    def test_private_epub_index_omits_source_path(self) -> None:
        ncx = b'''<?xml version="1.0" encoding="UTF-8"?>
        <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/">
          <navMap><navPoint><navLabel><text>Test</text></navLabel>
          <content src="item.xhtml"/></navPoint></navMap>
        </ncx>'''
        opf = b'''<?xml version="1.0" encoding="UTF-8"?>
        <package xmlns:dc="http://purl.org/dc/elements/1.1/">
          <metadata><dc:title>Fixture</dc:title></metadata>
        </package>'''
        with tempfile.TemporaryDirectory() as directory:
            epub_path = Path(directory) / "fixture.epub"
            with zipfile.ZipFile(epub_path, "w") as archive:
                archive.writestr("toc.ncx", ncx)
                archive.writestr("book.opf", opf)
                archive.writestr("item.xhtml", "<p>fixture text</p>")
            index = self.epub.build_index(epub_path)
        self.assertNotIn("source_path", index)
        self.assertIn("source_sha256", index)

    def test_private_index_cannot_target_public_skill(self) -> None:
        self.assertTrue(
            self.epub.is_within(SKILL_DIR / "private-index.json", SKILL_DIR)
        )

    def test_installer_filters_private_metadata(self) -> None:
        self.assertTrue(self.installer.is_private_metadata("my-book-index.json"))
        self.assertTrue(self.installer.is_private_metadata("call.transcript.txt"))
        self.assertFalse(self.installer.is_private_metadata("update-baseline.json"))

    def test_installer_rejects_destination_inside_source(self) -> None:
        with self.assertRaises(ValueError):
            self.installer.validate_target(
                SKILL_DIR / "nested" / "buffett-investment-system"
            )


if __name__ == "__main__":
    unittest.main()
