#!/usr/bin/env python3
"""Install this canonical skill into Codex or Claude Code.

Dry-run is the default. Existing installations are never deleted; --force moves
them to a timestamped sibling backup before copying.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


SKILL_NAME = "buffett-investment-system"
SOURCE_DIR = Path(__file__).resolve().parent.parent
IGNORED_NAMES = {
    ".git",
    ".private",
    "__pycache__",
    ".DS_Store",
}
IGNORED_SUFFIXES = {
    ".epub",
    ".mobi",
    ".azw3",
    ".pdf",
    ".pyc",
}


def is_private_metadata(name: str) -> bool:
    lowered = name.lower()
    return (
        ".transcript." in lowered
        or (lowered.endswith(".json") and "book-index" in lowered)
        or (lowered.endswith(".json") and "private-index" in lowered)
    )


def default_root(platform: str, scope: str, project_dir: Path | None) -> Path:
    platform_dir = ".codex" if platform == "codex" else ".claude"
    if scope == "user":
        return Path.home() / platform_dir / "skills"
    if project_dir is None:
        raise ValueError("--project-dir is required when --scope project is used")
    return project_dir.resolve() / platform_dir / "skills"


def ignore_filter(_: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        path = Path(name)
        if (
            name in IGNORED_NAMES
            or path.suffix.lower() in IGNORED_SUFFIXES
            or is_private_metadata(name)
        ):
            ignored.add(name)
    return ignored


def validate_target(destination: Path) -> None:
    if destination.name != SKILL_NAME:
        raise ValueError(f"destination must end with {SKILL_NAME!r}")
    if destination.resolve() == SOURCE_DIR:
        raise ValueError("source and destination are the same directory")
    try:
        destination.resolve().relative_to(SOURCE_DIR)
    except ValueError:
        pass
    else:
        raise ValueError("destination cannot be inside the canonical source directory")
    if not (SOURCE_DIR / "SKILL.md").is_file():
        raise ValueError("canonical source is missing SKILL.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=("codex", "claude"), required=True)
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument(
        "--target-root",
        type=Path,
        help="Override the platform skills root; the skill name is appended.",
    )
    parser.add_argument("--apply", action="store_true", help="Perform the copy.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Back up an existing installation before copying.",
    )
    args = parser.parse_args()

    try:
        if args.scope == "project" and args.target_root is None and (
            args.project_dir is None
            or not args.project_dir.exists()
            or not args.project_dir.is_dir()
        ):
            raise ValueError(
                "--project-dir must name an existing directory for project scope"
            )
        root = (
            args.target_root.expanduser().resolve()
            if args.target_root
            else default_root(args.platform, args.scope, args.project_dir)
        )
        destination = root / SKILL_NAME
        validate_target(destination)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"source:      {SOURCE_DIR}")
    print(f"destination: {destination}")
    print(f"mode:        {'apply' if args.apply else 'dry-run'}")

    if not args.apply:
        print("No files changed. Re-run with --apply after reviewing the target.")
        return 0

    root.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if not args.force:
            print("error: destination exists; use --force to create a backup", file=sys.stderr)
            return 3
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = root / f"{SKILL_NAME}.backup-{stamp}"
        if backup.exists():
            print(f"error: backup path already exists: {backup}", file=sys.stderr)
            return 4
        destination.rename(backup)
        print(f"backup:      {backup}")

    shutil.copytree(SOURCE_DIR, destination, ignore=ignore_filter)
    print("Installed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
