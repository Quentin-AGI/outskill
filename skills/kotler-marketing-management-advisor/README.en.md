# Kotler-Style Marketing Management Advisor

[中文](README.md)

A cross-platform Agent Skill for Codex and Claude Code. It turns the framework of the 16th edition of *Marketing Management* by Philip Kotler, Kevin Lane Keller, and Alexander Chernev into an auditable operating system for enterprise marketing decisions.

It is an AI advisor simulation, not Philip Kotler or an official representative. The Chinese `SKILL.md` is authoritative; English marketing terms are retained on first use to support international research and team collaboration.

## What it provides

- A three-layer operating system: stable book-based core, seven callable workflows, and a private enterprise workspace with consent-based extensions
- Six linked mental models and ten decision heuristics governed by G-STIC, 5C, 3V, and 7T
- Deep workflows for customer insight, target markets, brand positioning, product portfolios, pricing, channels and investment, and marketing team management
- One-question-at-a-time clarification using the smallest evidence set that can change the current decision
- Decision boards, action plans, RACI, metrics, review cycles, case continuity, and controlled knowledge promotion
- Explicit evidence labels for book concepts, external facts, company facts, advisor inferences, and unverified assumptions
- Chinese-first consultant and learning modes with progressive disclosure

External market facts may be researched and dated, but external methods require explicit user consent and never silently rewrite the book-based core. Private company information is redacted by default and cannot be sent to external search without authorization.

## Install

Commands are dry-run unless `--apply` is supplied. From the `outskill` repository root:

```bash
python3 skills/kotler-marketing-management-advisor/scripts/install.py --platform codex
python3 skills/kotler-marketing-management-advisor/scripts/install.py --platform codex --apply
```

```bash
python3 skills/kotler-marketing-management-advisor/scripts/install.py --platform claude
python3 skills/kotler-marketing-management-advisor/scripts/install.py --platform claude --apply
```

For project-scoped installation, add `--scope project --project-dir <project-directory>`. Existing installations are not overwritten unless `--force` is explicitly supplied; forced updates create a timestamped backup first.

## Use

```text
Use $kotler-marketing-management-advisor to decide which U.S. customer segment our brand should serve first. Ask only for evidence that can change the decision.
```

```text
Switch to learn-while-doing mode and guide our team through a brand-positioning decision, citing the relevant chapter and explaining one core concept at a time.
```

## Optional local book enhancement

The public package does not include the book. Users who lawfully possess an EPUB may create a private metadata-and-locator index outside the repository:

```bash
python3 skills/kotler-marketing-management-advisor/scripts/epub_locator.py index \
  --epub <book.epub> \
  --output <private-workspace>/book/index.json
```

Anchored local excerpts are capped at 800 Unicode characters and cannot export an entire XHTML item. Never commit the EPUB, private index, company workspace, or local source paths.

## Validation and licensing

Run:

```bash
python3 skills/kotler-marketing-management-advisor/scripts/validate_package.py
python3 skills/kotler-marketing-management-advisor/scripts/smoke_test.py
```

Original code under `scripts/` is Apache-2.0. Other original documentation and structured knowledge are CC BY 4.0. Third-party books, translations, cases, interviews, trademarks, linked materials, and private data are not relicensed. See [LICENSE.md](LICENSE.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Author and maintainer: [一笑而过](https://github.com/Quentin-AGI)
Method support: [Nuwa Skill](https://github.com/alchaincyf/nuwa-skill)
