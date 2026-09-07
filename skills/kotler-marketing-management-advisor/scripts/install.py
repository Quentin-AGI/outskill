#!/usr/bin/env python3
"""Install the canonical Skill into Codex or Claude Code; dry-run by default."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


SKILL_NAME = "kotler-marketing-management-advisor"
SOURCE_DIR = Path(__file__).resolve().parent.parent
IGNORED_NAMES = {".git", "__pycache__", ".DS_Store", ".book_skill_work"}
IGNORED_SUFFIXES = {".epub", ".mobi", ".azw", ".azw3", ".pdf", ".pyc"}


def private_name(name: str) -> bool:
    lowered = name.lower()
    return "private-index" in lowered or "book-index" in lowered or ".transcript." in lowered


def within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def default_root(platform: str, scope: str, project_dir: Path | None) -> Path:
    product = ".codex" if platform == "codex" else ".claude"
    if scope == "user":
        return Path.home() / product / "skills"
    if project_dir is None:
        raise ValueError("--project-dir is required for project scope")
    return project_dir.resolve() / product / "skills"


def ignore_filter(_: str, names: list[str]) -> set[str]:
    return {
        name for name in names
        if name in IGNORED_NAMES or Path(name).suffix.lower() in IGNORED_SUFFIXES or private_name(name)
    }


def find_symlinks(root: Path) -> list[Path]:
    """Return package entries that could escape or alias the copied tree."""
    return [path for path in root.rglob("*") if path.is_symlink()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=("codex", "claude"), required=True)
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--target-root", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force", action="store_true", help="Back up an existing installation before copying.")
    args = parser.parse_args()

    try:
        if args.scope == "project" and args.target_root is None and (
            args.project_dir is None or not args.project_dir.is_dir()
        ):
            raise ValueError("--project-dir must be an existing directory")
        root = args.target_root.expanduser().resolve() if args.target_root else default_root(args.platform, args.scope, args.project_dir)
        destination = root / SKILL_NAME
        if destination.name != SKILL_NAME or within(destination, SOURCE_DIR):
            raise ValueError("invalid installation destination")
        if destination.is_symlink():
            raise ValueError("installation destination must not be a symbolic link")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"source: {SOURCE_DIR}")
    print(f"destination: {destination}")
    print(f"mode: {'apply' if args.apply else 'dry-run'}")
    if not args.apply:
        print("No files changed. Re-run with --apply after reviewing the target.")
        return 0

    if destination.exists():
        if not args.force:
            print("error: destination exists; use --force to create a timestamped backup", file=sys.stderr)
            return 3

    root.mkdir(parents=True, exist_ok=True)
    stage_root = Path(tempfile.mkdtemp(prefix=f".{SKILL_NAME}.stage-", dir=root))
    staged = stage_root / SKILL_NAME
    backup: Path | None = None
    try:
        source_links = find_symlinks(SOURCE_DIR)
        if source_links:
            raise ValueError(f"source package contains a symbolic link: {source_links[0].relative_to(SOURCE_DIR)}")
        shutil.copytree(SOURCE_DIR, staged, ignore=ignore_filter)
        if not (staged / "SKILL.md").is_file() or not (staged / "agents/openai.yaml").is_file():
            raise ValueError("staged package failed minimum structure validation")
        if any(path.suffix.lower() in IGNORED_SUFFIXES or private_name(path.name) for path in staged.rglob("*")):
            raise ValueError("staged package contains private or excluded files")
        staged_links = find_symlinks(staged)
        if staged_links:
            raise ValueError(f"staged package contains a symbolic link: {staged_links[0].relative_to(staged)}")

        if destination.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            backup = root / f"{SKILL_NAME}.backup-{stamp}-{uuid.uuid4().hex[:8]}"
            os.replace(destination, backup)
            print(f"backup: {backup}")
        try:
            os.replace(staged, destination)
        except Exception:
            if backup is not None and backup.exists() and not destination.exists():
                os.replace(backup, destination)
            raise
        print("Installed successfully with an atomic destination switch.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: installation failed: {exc}", file=sys.stderr)
        return 4
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
