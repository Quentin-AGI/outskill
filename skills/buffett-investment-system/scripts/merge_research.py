#!/usr/bin/env python3
"""Summarize Phase 1 research files without sending their prose elsewhere."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FILE_LABELS = {
    "01": "著作与系统思考",
    "02": "长对话与演讲",
    "03": "表达 DNA",
    "04": "外部审计与反证",
    "05": "真实决策与案例",
    "06": "时间线与更新",
}

URL_RE = re.compile(r"https?://[^\s)>\]]+")
EPUB_RE = re.compile(r"(?:E4:)?text/part\d{4}\.html(?:#[\w-]+)?")
LABEL_RE = re.compile(
    r"【(?:巴菲特)?明确说】|【(?:巴菲特)?实际做】|【(?:研究|框架)?推断】|"
    r"【芒格补充(?:｜[^】]+)?】|【领域事实】"
)


def first_summary(text: str) -> str:
    lines = text.splitlines()
    anchors = ("核心结论", "研究结论摘要", "核心发现摘要", "摘要")
    start = 0
    for index, line in enumerate(lines):
        if line.startswith("#") and any(anchor in line for anchor in anchors):
            start = index + 1
            break
    collected: list[str] = []
    for line in lines[start:]:
        value = line.strip()
        if not value or value.startswith(">"):
            continue
        if value.startswith("#") and collected:
            break
        value = re.sub(r"^[-*]\s+", "", value)
        collected.append(value)
        if sum(len(item) for item in collected) >= 180:
            break
    return " ".join(collected)[:220]


def analyze(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    urls = sorted(set(URL_RE.findall(text)))
    epub_items = sorted(set(EPUB_RE.findall(text)))
    return {
        "file": path.name,
        "lines": len(text.splitlines()),
        "official_url_count": len(urls),
        "epub_locator_count": len(epub_items),
        "evidence_label_count": len(LABEL_RE.findall(text)),
        "summary": first_summary(text),
    }


def render_markdown(records: list[dict[str, object]]) -> str:
    lines = [
        "# Phase 1.5 调研质量摘要",
        "",
        "| 维度 | 文件 | 行数 | 官方 URL | EPUB 定位 | 证据标签 | 关键发现 |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for record in records:
        prefix = str(record["file"])[:2]
        summary = str(record["summary"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {FILE_LABELS.get(prefix, prefix)} | `{record['file']}` | "
            f"{record['lines']} | {record['official_url_count']} | "
            f"{record['epub_locator_count']} | {record['evidence_label_count']} | {summary} |"
        )
    lines.extend(
        [
            "",
            "> 计数用于审计覆盖，不代表来源彼此独立，也不替代人工质量判断。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    research_dir = args.skill_dir / "references" / "research"
    paths = sorted(research_dir.glob("0[1-6]-*.md"))
    records = [analyze(path) for path in paths]
    output = json.dumps(records, ensure_ascii=False, indent=2) if args.json else render_markdown(records)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
