---
name: codex-exec
description: Run OpenAI Codex CLI non-interactively to execute tasks, generate code, or get a second opinion. Use this skill whenever the user says "run codex", "ask codex", "codex exec", "have codex do", "send to codex", "pipe to codex", or wants to delegate a task to Codex for a second implementation, cross-model validation, or parallel AI execution. Also use when the user wants structured output from Codex, to resume a Codex session headlessly, or to run Codex with specific sandbox permissions.
---

# Codex Exec

Run OpenAI's Codex CLI non-interactively to execute tasks. This is the headless workhorse of Codex — it takes a prompt, runs it, and returns the result without an interactive TUI.

## Basic usage

```bash
codex exec "your prompt here" 2>/dev/null
```

Always append `2>/dev/null` to suppress thinking tokens on stderr.

## Prompt patterns

### Inline prompt

```bash
codex exec "Refactor the User model to add email validation" 2>/dev/null
```

### Piped prompt (for longer instructions or dynamic content)

```bash
echo "Review this function and suggest improvements:" | codex exec - 2>/dev/null
```

When stdin is piped and a prompt is also provided, stdin is appended as a `<stdin>` block:

```bash
cat some_file.py | codex exec "Review this code for security issues" 2>/dev/null
```

### With images

```bash
codex exec -i screenshot.png "What UI issues do you see?" 2>/dev/null
```

## Sandbox modes

Control what Codex can do on the filesystem:

| Mode | Flag | Use case |
|------|------|----------|
| Read-only | `-s read-only` | Safe analysis, review, questions |
| Workspace write | `-s workspace-write` | Code generation, file edits |
| Full access | `-s danger-full-access` | System-level tasks (use with caution) |
| Full auto | `--full-auto` | Shortcut for `-s workspace-write` with minimal approval prompts |

Default to `read-only` or `workspace-write` unless the user explicitly needs more.

## Structured output

Use `--output-schema` to get Codex to return JSON matching a schema:

```bash
codex exec "Analyze this codebase for security issues" \
  --output-schema schema.json \
  -o result.json \
  2>/dev/null
```

Use `--json` to get all events as JSONL stream (useful for programmatic parsing):

```bash
codex exec "List all TODO comments" --json 2>/dev/null
```

Use `-o <file>` to save just the last message to a file:

```bash
codex exec "Summarize the recent changes" -o summary.txt 2>/dev/null
```

## Resuming sessions headlessly

Continue a previous Codex session without the TUI:

```bash
codex exec resume --last 2>/dev/null
```

Or with a follow-up prompt:

```bash
echo "Now apply the fix you suggested" | codex exec --skip-git-repo-check resume --last 2>/dev/null
```

## Model selection

Override the default model:

```bash
codex exec -m o3 "your prompt" 2>/dev/null
```

## Working directory

Run Codex in a specific directory:

```bash
codex exec -C /path/to/project "your prompt" 2>/dev/null
```

## Common patterns for Claude

### Get a second opinion on code you wrote

```bash
codex exec -s read-only "Review the changes in the last commit. Are there any bugs or edge cases missed?" 2>/dev/null
```

### Delegate a subtask

```bash
codex exec --full-auto "Write unit tests for src/utils/parser.py and save them to tests/test_parser.py" 2>/dev/null
```

### Cross-model validation

```bash
codex exec -s read-only "I believe this function has O(n log n) complexity. Verify my analysis: $(cat src/sort.py)" 2>/dev/null
```

## Edge cases

- **Timeout**: `codex exec` can take 30-120+ seconds depending on the task. Use a 300s timeout for complex tasks.
- **Large output**: For tasks generating lots of output, use `-o <file>` to capture the last message rather than parsing stdout.
- **No git repo**: If running outside a git repo, add `--skip-git-repo-check`.
- **Ephemeral**: Add `--ephemeral` if you don't need the session persisted for later resume/fork.
