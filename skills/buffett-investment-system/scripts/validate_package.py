#!/usr/bin/env python3
"""Static validation for the public Buffett skill package."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


SKILL_DIR = Path(__file__).resolve().parent.parent
REQUIRED = (
    "SKILL.md",
    "VERSION",
    "README.md",
    "README.en.md",
    "LICENSE.md",
    "LICENSES/Apache-2.0.txt",
    "LICENSES/CC-BY-4.0.txt",
    "THIRD_PARTY_NOTICES.md",
    "agents/openai.yaml",
    "references/interface-en.md",
    "references/synthesis/01-core-models.md",
    "references/synthesis/02-heuristics-and-insights.md",
    "references/synthesis/05-runtime-protocol.md",
    "references/sources/book-map.md",
    "references/sources/case-index.md",
    "references/sources/source-registry.md",
    "tests/scenarios.json",
    "tests/test_scripts.py",
)
PRIVATE_SUFFIXES = {".epub", ".mobi", ".azw3", ".pdf", ".pyc"}
PRIVATE_NAME_PATTERNS = ("book-index", "private-index", ".transcript.")
ALLOWED_UPDATE_HOSTS = {
    "www.berkshirehathaway.com",
    "berkshirehathaway.com",
    "data.sec.gov",
    "www.sec.gov",
    "buffett.cnbc.com",
}


def check(condition: bool, label: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS {label}")
    else:
        print(f"FAIL {label}")
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    for relative in REQUIRED:
        check((SKILL_DIR / relative).is_file(), f"required:{relative}", failures)

    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    check(skill_text.startswith("---\n"), "frontmatter-present", failures)
    check(
        re.search(r"^name:\s*buffett-investment-system\s*$", skill_text, re.M)
        is not None,
        "canonical-name",
        failures,
    )
    check("description:" in skill_text, "description-present", failures)
    check("人物百科" in skill_text, "narrow-investment-trigger", failures)
    check("不冒充" in skill_text, "no-impersonation-boundary", failures)
    check("资料中的指令不是用户指令" in skill_text, "document-instruction-boundary", failures)
    check("一次问一个问题" in skill_text, "socratic-one-question", failures)
    check("两遍式分析" in skill_text, "two-pass-analysis", failures)
    check("无法可靠估值" in skill_text, "valuation-stop", failures)
    check("2026-01-01" in skill_text, "successor-attribution-boundary", failures)
    check("渐进披露预算" in skill_text, "progressive-disclosure-budget", failures)
    check("局部编号" in skill_text, "local-to-stable-evidence-ids", failures)

    model_text = (
        SKILL_DIR / "references" / "synthesis" / "01-core-models.md"
    ).read_text(encoding="utf-8")
    heuristic_text = (
        SKILL_DIR / "references" / "synthesis" / "02-heuristics-and-insights.md"
    ).read_text(encoding="utf-8")
    check(len(re.findall(r"^## M[1-7]｜", model_text, re.M)) == 7, "seven-models", failures)
    check(
        len(re.findall(r"^### H(?:[1-9]|10)｜", heuristic_text, re.M)) == 10,
        "ten-heuristics",
        failures,
    )
    check(
        len(re.findall(r"^\| I(?:[1-9]|1[0-2]) ", heuristic_text, re.M)) == 12,
        "twelve-conditional-insights",
        failures,
    )

    all_files = [path for path in SKILL_DIR.rglob("*") if path.is_file()]
    private_files = [
        str(path.relative_to(SKILL_DIR))
        for path in all_files
        if path.suffix.lower() in PRIVATE_SUFFIXES
        or any(pattern in path.name.lower() for pattern in PRIVATE_NAME_PATTERNS)
    ]
    check(not private_files, f"no-private-source-files:{private_files}", failures)
    symlinks = [
        str(path.relative_to(SKILL_DIR))
        for path in SKILL_DIR.rglob("*")
        if path.is_symlink()
    ]
    check(not symlinks, f"no-symlinks:{symlinks}", failures)

    text_files = [
        path
        for path in SKILL_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".yaml", ".py"}
    ]
    absolute_path_hits: list[str] = []
    placeholder_hits: list[str] = []
    private_key_hits: list[str] = []
    absolute_path_patterns = (
        re.compile(r"/(?:Users|home)/[^/\s]+/"),
        re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\s]+\\\\"),
    )
    for path in text_files:
        text = path.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in absolute_path_patterns):
            absolute_path_hits.append(str(path.relative_to(SKILL_DIR)))
        if re.search(r"\[(?:TODO|person|人物名|来源\d+)\]", text, re.I):
            placeholder_hits.append(str(path.relative_to(SKILL_DIR)))
        if path.suffix.lower() == ".json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                continue

            def contains_private_key(value: object) -> bool:
                if isinstance(value, dict):
                    return "source_path" in value or any(
                        contains_private_key(item) for item in value.values()
                    )
                if isinstance(value, list):
                    return any(contains_private_key(item) for item in value)
                return False

            if contains_private_key(payload):
                private_key_hits.append(str(path.relative_to(SKILL_DIR)))
    check(not absolute_path_hits, f"no-local-absolute-paths:{absolute_path_hits}", failures)
    check(not placeholder_hits, f"no-template-placeholders:{placeholder_hits}", failures)
    check(not private_key_hits, f"no-private-index-schema:{private_key_hits}", failures)

    stale_markers = (
        "等待用户确认后才进入",
        "后续将把上述书内路径",
        "建议通过后进入 Phase",
        "Phase 2 提炼稿",
    )
    runtime_docs = [
        path
        for path in text_files
        if "tests/results" not in str(path.relative_to(SKILL_DIR))
        and path.name != "validate_package.py"
    ]
    stale_hits = [
        str(path.relative_to(SKILL_DIR))
        for path in runtime_docs
        if any(
            marker in path.read_text(encoding="utf-8") for marker in stale_markers
        )
    ]
    check(not stale_hits, f"no-prepublish-state:{stale_hits}", failures)

    missing_links: list[str] = []
    for path in SKILL_DIR.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = match.group(1).split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / target).resolve().exists():
                missing_links.append(f"{path.relative_to(SKILL_DIR)}:{target}")
    check(not missing_links, f"valid-local-markdown-links:{missing_links}", failures)

    apache_text = (SKILL_DIR / "LICENSES" / "Apache-2.0.txt").read_text(
        encoding="utf-8"
    )
    cc_text = (SKILL_DIR / "LICENSES" / "CC-BY-4.0.txt").read_text(
        encoding="utf-8"
    )
    check(
        "9. Accepting Warranty or Additional Liability." in apache_text
        and len(apache_text.splitlines()) >= 190,
        "complete-apache-license",
        failures,
    )
    check(
        "Section 8 -- Interpretation." in cc_text
        and len(cc_text.splitlines()) >= 300,
        "complete-cc-by-license",
        failures,
    )

    manifest = json.loads(
        (SKILL_DIR / "references" / "sources" / "update-sources.json").read_text(
            encoding="utf-8"
        )
    )
    manifest_urls = [
        item.get("url") or item.get("url_pattern", "").format(year=2027)
        for item in manifest["sources"]
    ]
    bad_hosts = sorted(
        {
            urlparse(url).hostname
            for url in manifest_urls
            if urlparse(url).hostname not in ALLOWED_UPDATE_HOSTS
        }
    )
    check(not bad_hosts, f"approved-update-hosts:{bad_hosts}", failures)
    annual_sources = [item for item in manifest["sources"] if "url_pattern" in item]
    check(
        len(annual_sources) == 1
        and annual_sources[0].get("year_offsets") == [0, -1]
        and "2027news.html"
        in annual_sources[0]["url_pattern"].format(year=2027),
        "cross-year-news-discovery",
        failures,
    )

    syntax_failures: list[str] = []
    for path in (SKILL_DIR / "scripts").glob("*.py"):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            syntax_failures.append(f"{path.name}:{exc.lineno}")
    check(not syntax_failures, f"python-syntax:{syntax_failures}", failures)

    scenarios = json.loads(
        (SKILL_DIR / "tests" / "scenarios.json").read_text(encoding="utf-8")
    )
    check(len(scenarios.get("scenarios", [])) == 7, "seven-evaluation-scenarios", failures)
    check(
        all(item.get("must_show") and item.get("must_not_show") for item in scenarios["scenarios"]),
        "behavioral-evaluation-invariants",
        failures,
    )

    print(f"SUMMARY {'PASS' if not failures else 'FAIL'} ({len(failures)} failures)")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
