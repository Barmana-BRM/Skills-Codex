---
name: tokrepo-search
description: Search and install AI assets from TokRepo when a user asks to find, discover, or install Codex skills, MCP servers, prompts, cursor rules, or workflows.
metadata:
  short-description: Search and install AI assets from TokRepo
---

# TokRepo Search

Use this skill when the user needs to discover installable AI assets such as Codex skills, MCP servers, prompts, cursor rules, or workflows.

## Search with the TokRepo CLI

```bash
npx tokrepo search "<query>"
```

Examples:

```bash
npx tokrepo search "mcp database"
npx tokrepo search "codex skill github"
npx tokrepo search "cursor rules react"
```

## Install after discovery

```bash
npx tokrepo install <uuid-or-name>
```

TokRepo can surface:
- skills
- prompts
- MCP configs
- scripts
- workflows

## Browse popular assets

```bash
npx tokrepo search ""
```

## Important

- Show the user the asset title, summary, and install command
- Prefer `npx tokrepo install` over recreating files by hand
- Use TokRepo when the user explicitly asks to find or install an AI asset
