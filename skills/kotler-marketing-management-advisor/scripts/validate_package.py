#!/usr/bin/env python3
"""Static package validation for kotler-marketing-management-advisor."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PRIVATE_SUFFIXES = {".epub", ".mobi", ".azw", ".azw3", ".pdf", ".pyc"}


def check(value: bool, label: str, failures: list[str]) -> None:
    print(f"{'PASS' if value else 'FAIL'} {label}")
    if not value:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    required = [
        "SKILL.md", "agents/openai.yaml", "glossary.md", "patterns.md", "cheatsheet.md",
        "references/sources/book-map.md", "references/sources/source-registry.md",
        "references/protocols/evidence-and-boundaries.md", "references/protocols/case-and-knowledge.md",
        "tests/scenarios.json", "tests/voice-snapshots.json", "tests/fixtures/anker-2011-evaluator.md",
        "examples/mock-brand/end-to-end-tutorial.md", "examples/anker-2011/frozen-case.md",
        "examples/anker-2011/t0-input.md", "scripts/smoke_test.py", "README.md", "README.en.md",
        "LICENSE.md", "LICENSES/Apache-2.0.txt", "LICENSES/CC-BY-4.0.txt", "VERSION",
    ]
    for relative in required:
        check((ROOT / relative).is_file(), f"required:{relative}", failures)

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    checks = {
        "frontmatter": skill.startswith("---\n"),
        "canonical-name": bool(re.search(r"^name:\s*kotler-marketing-management-advisor$", skill, re.M)),
        "three-authors": all(name in skill for name in ("Kotler", "Keller", "Chernev")),
        "identity-boundary": "不是 Philip Kotler 本人" in skill,
        "gstic-core": all(term in skill for term in ("G-STIC", "5C", "3V", "7T")),
        "privacy-boundary": "未经明确授权" in skill and "外部搜索" in skill,
        "extension-consent": "用户明确同意" in skill and "扩展方法" in skill,
        "critical-evidence-gate": "致命缺口" in skill and "致命于哪项结论/动作" in skill,
        "public-attribution": "Quentin-AGI" in skill,
    }
    for label, value in checks.items():
        check(value, label, failures)

    openai_yaml = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
    short_match = re.search(r'^\s*short_description:\s*"([^"]+)"\s*$', openai_yaml, re.M)
    prompt_match = re.search(r'^\s*default_prompt:\s*"([^"]+)"\s*$', openai_yaml, re.M)
    check(bool(short_match and 25 <= len(short_match.group(1)) <= 64), "openai-short-description-length", failures)
    check(bool(prompt_match and "$kotler-marketing-management-advisor" in prompt_match.group(1) and re.search(r"[\u4e00-\u9fff]", prompt_match.group(1))), "openai-default-prompt", failures)

    chapter_files = sorted((ROOT / "chapters").glob("ch??-*.md"))
    module_files = sorted((ROOT / "modules").glob("*.md"))
    template_files = sorted((ROOT / "templates").glob("*.md"))
    check(len(chapter_files) == 21, "twenty-one-chapters", failures)
    check(len(module_files) == 8, "router-plus-seven-modules", failures)
    check(len(template_files) >= 12, "fillable-templates", failures)

    models = (ROOT / "references/synthesis/02-mental-models.md").read_text(encoding="utf-8")
    heuristics = (ROOT / "references/synthesis/03-decision-heuristics.md").read_text(encoding="utf-8")
    check(len(re.findall(r"^## M[1-6]｜", models, re.M)) == 6, "six-models", failures)
    check(len(re.findall(r"^## H(?:[1-9]|10)｜", heuristics, re.M)) == 10, "ten-heuristics", failures)

    all_files = [path for path in ROOT.rglob("*") if path.is_file()]
    private = [str(path.relative_to(ROOT)) for path in all_files if path.suffix.lower() in PRIVATE_SUFFIXES or "private-index" in path.name.lower()]
    symlinks = [str(path.relative_to(ROOT)) for path in ROOT.rglob("*") if path.is_symlink()]
    check(not private, f"no-private-source-files:{private}", failures)
    check(not symlinks, f"no-symlinks:{symlinks}", failures)

    public_files = [path for path in all_files if path.suffix.lower() in {".md", ".json", ".yaml", ".py"}]
    absolute_hits: list[str] = []
    placeholder_hits: list[str] = []
    fingerprint_hits: list[str] = []
    for path in public_files:
        content = path.read_text(encoding="utf-8")
        if re.search(r"/(?:Users|home)/[^/\s]+/", content) or re.search(r"[A-Za-z]:\\\\Users\\\\", content):
            absolute_hits.append(str(path.relative_to(ROOT)))
        if re.search(r"\[(?:TODO|人物名|来源\d+)\]", content, re.I):
            placeholder_hits.append(str(path.relative_to(ROOT)))
        if re.search(r"\b[0-9a-fA-F]{64}\b", content):
            fingerprint_hits.append(str(path.relative_to(ROOT)))
    check(not absolute_hits, f"no-local-absolute-paths:{absolute_hits}", failures)
    check(not placeholder_hits, f"no-scaffold-placeholders:{placeholder_hits}", failures)
    check(not fingerprint_hits, f"no-public-source-fingerprints:{fingerprint_hits}", failures)

    missing_links: list[str] = []
    for path in ROOT.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", content):
            target = match.group(1).split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / target).resolve().exists():
                missing_links.append(f"{path.relative_to(ROOT)}:{target}")
    check(not missing_links, f"valid-local-links:{missing_links}", failures)

    syntax_errors: list[str] = []
    for path in (ROOT / "scripts").glob("*.py"):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            syntax_errors.append(f"{path.name}:{exc.lineno}")
    check(not syntax_errors, f"python-syntax:{syntax_errors}", failures)

    locator_source = (ROOT / "scripts/epub_locator.py").read_text(encoding="utf-8")
    check('add_parser("read")' not in locator_source and 'add_parser("excerpt")' in locator_source, "bounded-epub-interface", failures)
    check("MAX_EXCERPT_CHARS = 800" in locator_source and 'add_argument("--anchor", required=True)' in locator_source, "epub-hard-cap-and-anchor", failures)
    check("not output.is_file()" in locator_source and "tempfile.mkstemp" in locator_source, "epub-regular-atomic-output", failures)

    workspace_source = (ROOT / "scripts/init_workspace.py").read_text(encoding="utf-8")
    check('"--merge"' not in workspace_source and "destination must be new or empty" in workspace_source, "workspace-no-merge", failures)

    installer_source = (ROOT / "scripts/install.py").read_text(encoding="utf-8")
    check("def find_symlinks" in installer_source and "source_links" in installer_source and "staged_links" in installer_source, "installer-symlink-guard", failures)

    apache_text = (ROOT / "LICENSES/Apache-2.0.txt").read_text(encoding="utf-8")
    cc_text = (ROOT / "LICENSES/CC-BY-4.0.txt").read_text(encoding="utf-8")
    check("9. Accepting Warranty or Additional Liability." in apache_text and len(apache_text.splitlines()) >= 190, "complete-apache-license", failures)
    check("Section 8 -- Interpretation." in cc_text and len(cc_text.splitlines()) >= 300, "complete-cc-by-license", failures)

    try:
        scenarios = json.loads((ROOT / "tests/scenarios.json").read_text(encoding="utf-8"))
        items = scenarios["scenarios"]
        valid_scenarios = len(items) >= 16 and all(item.get("must_show") and item.get("must_not_show") for item in items)
    except (OSError, KeyError, json.JSONDecodeError):
        valid_scenarios = False
    check(valid_scenarios, "behavioral-scenarios", failures)

    try:
        snapshots = json.loads((ROOT / "tests/voice-snapshots.json").read_text(encoding="utf-8"))["snapshots"]
        valid_snapshots = len(snapshots) >= 4 and all(item.get("expect") and item.get("avoid") for item in snapshots)
    except (OSError, KeyError, json.JSONDecodeError):
        valid_snapshots = False
    check(valid_snapshots, "voice-snapshots", failures)

    print(f"SUMMARY {'PASS' if not failures else 'FAIL'} ({len(failures)} failures)")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
