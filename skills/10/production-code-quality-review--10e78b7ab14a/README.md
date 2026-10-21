# Production Code Quality Review Skill

This directory is the shippable Codex skill package.

Use it when installing, copying, testing, or reviewing the skill itself. Repository-level docs live outside this directory, but this directory is the source of truth for the runtime skill asset.

## Skill Hierarchy

```text
production-code-quality-review/
  SKILL.md              # Required Codex entrypoint and trigger instructions
  README.md             # Human guide for this skill package
  agents/
    openai.yaml         # Codex UI metadata
    synthesizer.md      # Specialist-review synthesis prompt
  references/
    review-framework.md
    output-contract.md
    false-positive-control.md
    review-context.schema.json
    finding.schema.json
    security.md
    typescript.md
    python.md
    backend-and-integrations.md
    verification-and-operations.md
    database.md
  scripts/
    collect-review-context.py
    review-entrypoint.py
    diff-line-map.py
    detect-stack.py
    run-safe-checks.py
    install-local-skill.sh
    update-local-skill.sh
    verify-release.sh
  tests/
    test_collect_review_context_cli.py
    test_review_skill_lib.py
```

## Protected Asset Contract

Keep these files present and versioned:

- `SKILL.md`
- `agents/openai.yaml`
- `references/review-framework.md`
- `references/output-contract.md`
- `references/false-positive-control.md`
- `references/review-context.schema.json`
- `references/finding.schema.json`
- `scripts/collect-review-context.py`
- `scripts/review-entrypoint.py`
- `scripts/review_skill_lib.py`
- `scripts/install-local-skill.sh`
- `scripts/update-local-skill.sh`
- `scripts/verify-release.sh`
- `tests/test_collect_review_context_cli.py`
- `tests/test_review_skill_lib.py`

Do not move development notes into this directory unless they are needed at runtime by the skill. Use `docs/dev/` for implementation notes and planning.

## Install

From the repository checkout:

```bash
bash production-code-quality-review/scripts/install-local-skill.sh
```

The default Codex user-scope install path is:

```text
~/.agents/skills/production-code-quality-review
```

When running commands from this checkout, use the active Python interpreter for your environment:

```bash
# Windows
python production-code-quality-review/scripts/collect-review-context.py --repo .

# POSIX
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

When running commands from an installed copy outside the checkout, use the same interpreter rule:

```bash
python "$HOME/.agents/skills/production-code-quality-review/scripts/collect-review-context.py" --repo .
python3 "$HOME/.agents/skills/production-code-quality-review/scripts/collect-review-context.py" --repo .
```

## Validate

Run the full skill verification bundle before publishing:

```bash
bash production-code-quality-review/scripts/verify-release.sh
```

For faster local iteration:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover production-code-quality-review/tests -v
git diff --check
```
