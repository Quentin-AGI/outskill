# Claude Code adapter

The canonical Skill is `skills/buffett-investment-system/` in the `outskill` repository. Do not edit a separate Claude-specific knowledge copy. Run the commands below from the repository root.

Preview a user-level installation:

```bash
python3 skills/buffett-investment-system/scripts/install.py --platform claude
```

Install after reviewing the destination:

```bash
python3 skills/buffett-investment-system/scripts/install.py --platform claude --apply
```

For a project-scoped installation, pass `--scope project --project-dir /absolute/project/path`. The installed location is `.claude/skills/buffett-investment-system` inside that project.

Invoke the installed skill with `$buffett-investment-system`. The same `SKILL.md`, references, evidence IDs, and update rules are used on both platforms.
