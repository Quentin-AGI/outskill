#!/usr/bin/env python3
"""Check approved first-party source indexes for content changes.

The default operation is read-only: fetch sources and compare their hashes with
the last human-approved baseline. Writing a baseline requires both
--write-baseline and --confirm-reviewed. This script never edits the knowledge
base or decides that changed content is Buffett-authored.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES = SKILL_DIR / "references" / "sources" / "update-sources.json"
DEFAULT_BASELINE = SKILL_DIR / "references" / "sources" / "update-baseline.json"
USER_AGENT = "buffett-investment-system/0.1 (+https://github.com/Quentin-AGI/outskill)"
MAX_BYTES = 5 * 1024 * 1024
ALLOWED_HOSTS = {
    "berkshirehathaway.com",
    "www.berkshirehathaway.com",
    "data.sec.gov",
    "www.sec.gov",
    "buffett.cnbc.com",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected an object in {path}")
    return value


def validate_source(source: dict[str, Any]) -> None:
    source_id = source.get("id")
    url = source.get("url")
    if not isinstance(source_id, str) or not source_id:
        raise ValueError("every source requires a non-empty id")
    if not isinstance(url, str):
        raise ValueError(f"source {source_id} requires a URL")
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"source {source_id} is outside the approved host list")


def expand_sources(
    raw_sources: list[dict[str, Any]], year: int | None = None
) -> list[dict[str, Any]]:
    """Expand annual discovery pages without hard-coding the release year."""
    current_year = year or datetime.now(timezone.utc).year
    expanded: list[dict[str, Any]] = []
    for source in raw_sources:
        if not isinstance(source, dict):
            raise ValueError("every source entry must be an object")
        if "url" in source:
            expanded.append(dict(source))
            continue

        id_pattern = source.get("id_pattern")
        url_pattern = source.get("url_pattern")
        offsets = source.get("year_offsets")
        if not isinstance(id_pattern, str) or "{year}" not in id_pattern:
            raise ValueError("annual source requires id_pattern containing {year}")
        if not isinstance(url_pattern, str) or "{year}" not in url_pattern:
            raise ValueError("annual source requires url_pattern containing {year}")
        if not isinstance(offsets, list) or not offsets or not all(
            isinstance(offset, int) for offset in offsets
        ):
            raise ValueError("annual source requires integer year_offsets")

        for offset in offsets:
            source_year = current_year + offset
            item = {
                key: value
                for key, value in source.items()
                if key not in {"id_pattern", "url_pattern", "year_offsets"}
            }
            item["id"] = id_pattern.format(year=source_year)
            item["url"] = url_pattern.format(year=source_year)
            expanded.append(item)
    return expanded


def fetch(source: dict[str, Any], timeout: float) -> dict[str, Any]:
    validate_source(source)
    request = Request(
        source["url"],
        headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"},
    )
    with urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        parsed = urlparse(final_url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError(f"redirected outside approved hosts: {final_url}")
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError(f"response exceeds {MAX_BYTES} bytes")
        return {
            "id": source["id"],
            "kind": source.get("kind", "unknown"),
            "required": source.get("required", True),
            "url": source["url"],
            "final_url": final_url,
            "http_status": getattr(response, "status", 200),
            "content_type": response.headers.get("Content-Type"),
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "attribution_rule": source.get("attribution_rule"),
        }


def fetch_all(
    sources: list[dict[str, Any]], timeout: float, workers: int
) -> list[dict[str, Any]]:
    """Fetch in parallel so one slow endpoint does not multiply run latency."""
    results: list[dict[str, Any] | None] = [None] * len(sources)
    with ThreadPoolExecutor(max_workers=min(workers, len(sources))) as executor:
        futures = {
            executor.submit(fetch, source, timeout): (index, source)
            for index, source in enumerate(sources)
        }
        for future in as_completed(futures):
            index, source = futures[future]
            try:
                results[index] = future.result()
            except Exception as exc:  # keep other sources checkable
                results[index] = {
                    "id": source.get("id", "unknown"),
                    "kind": source.get("kind", "unknown"),
                    "required": source.get("required", True),
                    "url": source.get("url"),
                    "error": f"{type(exc).__name__}: {exc}",
                }
    return [item for item in results if item is not None]


def compare(
    current: list[dict[str, Any]], baseline: dict[str, Any]
) -> list[dict[str, Any]]:
    old_items = {
        item.get("id"): item
        for item in baseline.get("sources", [])
        if isinstance(item, dict) and item.get("id")
    }
    records: list[dict[str, Any]] = []
    for item in current:
        old = old_items.get(item["id"])
        record = dict(item)
        if "error" in item:
            record["change_status"] = "check-error"
        elif old is None or not old.get("sha256"):
            record["change_status"] = "no-approved-baseline"
        elif old.get("sha256") == item.get("sha256"):
            record["change_status"] = "unchanged"
        else:
            record["change_status"] = "changed-pending-review"
            record["previous_sha256"] = old.get("sha256")
            record["previous_approved_at"] = baseline.get("approved_at")
        records.append(record)
    return records


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Buffett official-source update check",
        "",
        f"Checked at: {report['checked_at']}",
        "",
        "| ID | Required | Status | HTTP | Bytes | Last-Modified |",
        "|---|---|---|---:|---:|---|",
    ]
    for item in report["sources"]:
        lines.append(
            f"| {item['id']} | {'yes' if item.get('required', True) else 'no'} | "
            f"{item['change_status']} | "
            f"{item.get('http_status', '-')} | {item.get('bytes', '-')} | "
            f"{item.get('last_modified') or '-'} |"
        )
        if item.get("error"):
            lines.append(f"|  |  | error: {item['error']} |  |  |  |")
    lines.extend(
        [
            "",
            "> A changed hash is only a discovery signal. Review authorship, date,",
            "> completeness and relationship to the book before updating knowledge.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument(
        "--confirm-reviewed",
        action="store_true",
        help="Confirm a human reviewed the fetched source identity and scope.",
    )
    args = parser.parse_args()

    if args.write_baseline and not args.confirm_reviewed:
        print(
            "error: --write-baseline requires --confirm-reviewed",
            file=sys.stderr,
        )
        return 2

    try:
        manifest = load_json(args.sources)
        raw_sources = manifest.get("sources", [])
        if not isinstance(raw_sources, list) or not raw_sources:
            raise ValueError("source manifest must contain a non-empty sources list")
        if args.workers < 1:
            raise ValueError("--workers must be at least 1")
        sources = expand_sources(raw_sources)
        baseline = load_json(args.baseline) if args.baseline.exists() else {}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    fetched = fetch_all(sources, args.timeout, args.workers)

    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    report = {
        "schema_version": 1,
        "checked_at": checked_at,
        "baseline_approved_at": baseline.get("approved_at"),
        "sources": compare(fetched, baseline),
    }

    if args.write_baseline:
        if any("error" in item and item.get("required", True) for item in fetched):
            if args.format == "json":
                print(json.dumps(report, ensure_ascii=False, indent=2))
            else:
                print(render_markdown(report))
            print("error: refusing to write an incomplete baseline", file=sys.stderr)
            return 3
        baseline_payload = {
            "schema_version": 1,
            "approved_at": checked_at,
            "approval_note": "Initial or human-reviewed official-source baseline.",
            "sources": [item for item in fetched if "error" not in item],
        }
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(
            json.dumps(baseline_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        for item in report["sources"]:
            if "error" not in item:
                item["change_status"] = "baseline-recorded"

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))

    if args.write_baseline:
        return 0
    needs_attention = any(
        item["change_status"] in {"changed-pending-review", "no-approved-baseline"}
        or (
            item["change_status"] == "check-error"
            and item.get("required", True)
        )
        for item in report["sources"]
    )
    return 1 if needs_attention else 0


if __name__ == "__main__":
    raise SystemExit(main())
