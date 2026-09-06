# Buffett Investment Cognition System

[中文](README.md)

A cross-platform Agent Skill for Codex and Claude Code. Its authoritative core is derived from the Buffett-authored material selected in the fourth edition of *The Essays of Warren Buffett: Lessons for Investors and Managers*, with later first-party materials kept as separately labeled extensions and evolution records.

This is not a quote bot and does not impersonate Warren Buffett. It turns the framework into an auditable decision system for company analysis, management assessment, capital allocation, valuation, M&A, credit, portfolio discipline, learning, thesis review, and post-mortems.

## Key properties

- Seven linked models with explicit stop conditions
- One-question-at-a-time context clarification
- Full scan followed by selective deep analysis
- Qualitative gates before range-based valuation
- Separate labels for statements, actions, inferences, domain facts, and Munger supplements
- First-party update checks with human approval before knowledge changes
- Institutional correction for non-U.S. markets
- Chinese authoritative core and English interaction layer using one evidence graph

## Install

The repository directory is the single canonical source. Run the following commands from the `outskill` repository root; commands are dry-run unless `--apply` is supplied. If you are already inside this Skill directory, shorten the script path to `scripts/install.py`.

```bash
python3 skills/buffett-investment-system/scripts/install.py --platform codex
python3 skills/buffett-investment-system/scripts/install.py --platform codex --apply
```

```bash
python3 skills/buffett-investment-system/scripts/install.py --platform claude
python3 skills/buffett-investment-system/scripts/install.py --platform claude --apply
```

For project-scoped installation:

```bash
python3 skills/buffett-investment-system/scripts/install.py --platform codex --scope project --project-dir /path/to/project --apply
python3 skills/buffett-investment-system/scripts/install.py --platform claude --scope project --project-dir /path/to/project --apply
```

## Use

```text
Use $buffett-investment-system to audit my investment thesis. Ask one material question at a time before analyzing it.
```

```text
Apply the Buffett Investment Cognition System to this company. Check current first-party filings and decide whether the business is knowable before valuing it.
```

The English interaction contract is in [references/interface-en.md](references/interface-en.md). The Chinese `SKILL.md` remains authoritative; both languages use the same evidence IDs.

## Bring your own lawful book copy

The public package does not contain an EPUB or long source text. Users may create a non-reconstructive local index outside the repository:

```bash
python3 skills/buffett-investment-system/scripts/epub_locator.py index \
  --epub /absolute/path/to/your-book.epub \
  --output /absolute/private/path/buffett-book-index.json
```

The index omits the book path, and the script refuses to write an index inside the Skill directory. Do not commit the book, full transcripts, private indexes, or local paths.

## Update check

```bash
python3 skills/buffett-investment-system/scripts/check_updates.py
```

A changed source hash is a discovery signal, not an attribution decision. Knowledge updates require review of authorship, date, completeness, and relationship to the book, followed by explicit human confirmation.

## Licensing

- Original code under `scripts/`: Apache License 2.0
- Other original documentation and structured content: CC BY 4.0
- Third-party books, speeches, interviews, trademarks, and linked materials are not relicensed
- Private corpus layers are excluded from the distribution

See [LICENSE.md](LICENSE.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Author and maintainer: [一笑而过](https://github.com/Quentin-AGI)
Method support: [Nuwa Skill](https://github.com/alchaincyf/nuwa-skill)
