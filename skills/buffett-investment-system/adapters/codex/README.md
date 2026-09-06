# Codex adapter

The canonical Skill is `skills/buffett-investment-system/` in the `outskill` repository. Do not maintain a second Codex-specific copy in this directory. Run the commands below from the repository root.

Preview a user-level installation:

```bash
python3 skills/buffett-investment-system/scripts/install.py --platform codex
```

Install after reviewing the destination:

```bash
python3 skills/buffett-investment-system/scripts/install.py --platform codex --apply
```

For a project-scoped installation, pass `--scope project --project-dir /absolute/project/path`. The installed location is `.codex/skills/buffett-investment-system` inside that project.

Codex UI metadata is stored in `agents/openai.yaml`. Automatic discovery remains enabled; explicit invocation is available as `$buffett-investment-system`.
