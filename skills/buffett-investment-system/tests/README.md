# Evaluation suite

`scenarios.json` contains the seven user-approved core acceptance scenarios. They are behavioral specifications, not exact-answer snapshots.

For each scenario, an evaluator should load the canonical `SKILL.md`, answer the prompt in an isolated workspace, and assess every `must_show` and `must_not_show` item. Wording may vary; the decision behavior must not.

The scenarios jointly cover active learning, chapter teaching, thesis audit, global company and management analysis, valuation refusal, credit and personal constraints, and a decision post-mortem.

Phase 4 also requires three known-position checks, one edge case and one voice check. Those evaluations should reuse these invariants rather than compare exact prose.

Run deterministic script regressions from the `outskill` repository root:

```bash
python3 -B skills/buffett-investment-system/tests/test_scripts.py
```

These tests cover annual source rollover, private EPUB-index metadata, install filtering and unsafe destination rejection. The behavioral JSON still requires an Agent evaluator because it specifies decision behavior rather than exact strings.
