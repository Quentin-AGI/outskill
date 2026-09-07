#!/usr/bin/env python3
"""Run isolated security and portability smoke tests for this Skill package."""

from __future__ import annotations

import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def write_epub(path: Path, epub3: bool) -> None:
    container = """<?xml version="1.0"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles><rootfile full-path="OPS/book.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""
    chapter = """<html xmlns="http://www.w3.org/1999/xhtml"><body>
<h1 id="start">Start</h1><p>ABCDE FGHIJ KLMNO PQRST UVWXYZ.</p>
</body></html>"""
    if epub3:
        opf = """<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Nav Test</dc:title></metadata>
<manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="c1" href="ch1.xhtml" media-type="application/xhtml+xml"/></manifest>
<spine><itemref idref="c1"/></spine></package>"""
        toc_name = "OPS/nav.xhtml"
        toc = """<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><body>
<nav epub:type="toc"><ol><li><a href="ch1.xhtml#start">Chapter One</a></li></ol></nav>
</body></html>"""
    else:
        opf = """<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>NCX Test</dc:title></metadata>
<manifest><item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/><item id="c1" href="ch1.xhtml" media-type="application/xhtml+xml"/></manifest>
<spine toc="ncx"><itemref idref="c1"/></spine></package>"""
        toc_name = "OPS/toc.ncx"
        toc = """<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/"><navMap><navPoint id="n1">
<navLabel><text>Chapter One</text></navLabel><content src="ch1.xhtml#start"/>
</navPoint></navMap></ncx>"""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("META-INF/container.xml", container)
        archive.writestr("OPS/book.opf", opf)
        archive.writestr("OPS/ch1.xhtml", chapter)
        archive.writestr(toc_name, toc)


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)
    print(f"PASS {label}")


def main() -> int:
    locator = load_module("epub_locator", SCRIPTS / "epub_locator.py")
    installer = load_module("skill_installer", SCRIPTS / "install.py")
    with tempfile.TemporaryDirectory(prefix="kotler-skill-smoke-") as raw:
        temp = Path(raw)
        ncx = temp / "ncx.epub"
        nav = temp / "nav.epub"
        write_epub(ncx, epub3=False)
        write_epub(nav, epub3=True)

        ncx_index = locator.build_index(ncx)
        nav_index = locator.build_index(nav)
        assert_true(ncx_index["toc"][0]["anchor"] == "start", "NCX index")
        assert_true(nav_index["toc"][0]["anchor"] == "start", "EPUB3 nav index")
        assert_true("source_path" not in ncx_index and "excerpt" not in json.dumps(ncx_index), "index omits path and prose")

        excerpt = locator.extract_excerpt(nav, "OPS/ch1.xhtml", "start", 12)
        assert_true(excerpt["characters"] <= 12 and excerpt["truncated"], "bounded anchored excerpt")
        for item, anchor, limit in (
            ("OPS/book.opf", "start", 12),
            ("OPS/ch1.xhtml", "missing", 12),
            ("OPS/ch1.xhtml", "", 12),
            ("OPS/ch1.xhtml", "x" * 257, 12),
            ("OPS/ch1.xhtml", "start", 801),
        ):
            try:
                locator.extract_excerpt(nav, item, anchor, limit)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid excerpt request was accepted")
        print("PASS excerpt rejects non-HTML, invalid/missing anchor, and excessive limit")

        index_file = temp / "private-index.json"
        locator.write_index(index_file, nav_index, force=False)
        try:
            locator.write_index(index_file, nav_index, force=False)
        except ValueError:
            pass
        else:
            raise AssertionError("existing index was overwritten without --force")
        locator.write_index(index_file, nav_index, force=True)
        assert_true(len(list(temp.glob("private-index.json.backup-*"))) == 1, "index overwrite requires force and creates backup")
        directory_index = temp / "directory-index"
        directory_index.mkdir()
        try:
            locator.write_index(directory_index, nav_index, force=True)
        except ValueError:
            pass
        else:
            raise AssertionError("index --force accepted a directory target")
        assert_true(directory_index.is_dir(), "index rejects directory target without moving it")

        suspicious = temp / "suspicious.epub"
        with zipfile.ZipFile(suspicious, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("huge.xhtml", "A" * 2_000_000)
        try:
            with zipfile.ZipFile(suspicious) as archive:
                locator.validate_archive(archive)
        except ValueError:
            pass
        else:
            raise AssertionError("suspicious compression ratio was accepted")
        print("PASS suspicious compression ratio rejected")

        workspace = temp / "private-workspace"
        created = run(sys.executable, str(SCRIPTS / "init_workspace.py"), str(workspace), "--apply")
        assert_true(created.returncode == 0, "private workspace initializes")
        if os.name == "posix":
            assert_true(stat.S_IMODE(workspace.stat().st_mode) == 0o700, "workspace root mode 0700")
            assert_true(stat.S_IMODE((workspace / "company-profile/company.md").stat().st_mode) == 0o600, "workspace file mode 0600")
        repeated = run(sys.executable, str(SCRIPTS / "init_workspace.py"), str(workspace), "--apply")
        assert_true(repeated.returncode != 0, "workspace refuses non-empty target")
        outside = temp / "outside"
        outside.mkdir()
        outside.chmod(0o755)
        hostile_workspace = temp / "hostile-workspace"
        hostile_workspace.mkdir()
        (hostile_workspace / "company-profile").symlink_to(outside, target_is_directory=True)
        hostile = run(sys.executable, str(SCRIPTS / "init_workspace.py"), str(hostile_workspace), "--apply")
        assert_true(
            hostile.returncode != 0
            and not (outside / "company.md").exists()
            and (os.name != "posix" or stat.S_IMODE(outside.stat().st_mode) == 0o755),
            "workspace rejects non-empty target with internal symlink without outside writes",
        )
        linked_workspace = temp / "linked-workspace"
        linked_workspace.symlink_to(outside, target_is_directory=True)
        linked_workspace_result = run(sys.executable, str(SCRIPTS / "init_workspace.py"), str(linked_workspace), "--apply")
        assert_true(linked_workspace_result.returncode != 0, "workspace rejects symbolic-link destination")

        install_root = temp / "install"
        installed = run(sys.executable, str(SCRIPTS / "install.py"), "--platform", "codex", "--target-root", str(install_root), "--apply")
        assert_true(installed.returncode == 0 and (install_root / ROOT.name / "SKILL.md").is_file(), "atomic install")
        updated = run(sys.executable, str(SCRIPTS / "install.py"), "--platform", "codex", "--target-root", str(install_root), "--apply", "--force")
        backups = list(install_root.glob(f"{ROOT.name}.backup-*"))
        assert_true(updated.returncode == 0 and len(backups) == 1, "forced install creates unique backup")

        equal_source = run(sys.executable, str(SCRIPTS / "install.py"), "--platform", "codex", "--target-root", str(ROOT.parent))
        inside_source = run(sys.executable, str(SCRIPTS / "install.py"), "--platform", "codex", "--target-root", str(ROOT / ".smoke-inside"))
        assert_true(equal_source.returncode != 0 and inside_source.returncode != 0 and not (ROOT / ".smoke-inside").exists(), "installer rejects source and descendant targets")
        if os.name == "posix":
            linked_root = temp / "linked"
            linked_root.mkdir()
            (linked_root / ROOT.name).symlink_to(ROOT, target_is_directory=True)
            linked = run(sys.executable, str(SCRIPTS / "install.py"), "--platform", "codex", "--target-root", str(linked_root))
            assert_true(linked.returncode != 0, "installer rejects symlink destination")
            linked_source = temp / "linked-source"
            linked_source.mkdir()
            (linked_source / "escape").symlink_to(ROOT / "SKILL.md")
            assert_true(bool(installer.find_symlinks(linked_source)), "installer detects source-tree symbolic links")

    print("SUMMARY PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
