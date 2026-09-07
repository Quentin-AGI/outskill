#!/usr/bin/env python3
"""Print one scenario prompt without exposing evaluator assertions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario_id")
    args = parser.parse_args()
    data = json.loads((ROOT / "tests/scenarios.json").read_text(encoding="utf-8"))
    for item in data["scenarios"]:
        if item["id"] == args.scenario_id:
            print(item["prompt"])
            return 0
    parser.error(f"unknown scenario: {args.scenario_id}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
