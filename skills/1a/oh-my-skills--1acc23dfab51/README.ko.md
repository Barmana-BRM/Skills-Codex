oh-my-skills

README

## Demo

! [oh-my-skills demo preview](docs/assets/oh-my-skills-demo-preview.gif)

View full demo video:
[docs/assets/oh-my-skills-demo. (docs/assets/oh-my-skills-demo.mp4)

Codex, Claude, Agent Skills, `SKILL.md` is a local GUI/CLI that manages folders at once.

oh-my-skills is very simple.

> "What skill can I do on my computer, and what skill can I edit safely?"

Scan local skill directories, show duplicates, and edit user-owned skills safely. System/Plug-in skill is placed exclusively for reading.

## Function

- Local browser GUI: search, filter, check, edit, generate, archive
- English/Korean GUI Toggle
- Light/Dark GUI Theme Toggles to keep the same mono README style
- CLI inventory: Export Markdown or JSON reports
- Detect duplicate skill between Codex, Claude, Agents, and Plugin Cache
- Safe editing: `SKILL.md` auto backup before storage
- Safe clearance: Move to archive folder instead of permanent deletion
- Local priority: `127.0.0.1` running, account/cloud synchronization/DB/telametri
- Light dependency: only use Python standard library

## Basic Scan Location

| Source | Location | Edit |
| --- | --- | --- |
| `codex-user` | `~/.codex/skills` | Available |
| `claude-user` | `~/.claude/skills` | Available |
| `agents-user` | `~/.agents/skills` | Available |
| `codex-system` | `~/.codex/skills/.system` | Read Only |
| `plugin-cache` | `~/.codex/plugins/cache` | Read Only |

## Quick Start

### Run in source

```bash
git clone https://github.com/AIjunja/oh-my-skills.git
cd oh-my-skills
python -m skill_ledger gui
```

Please leave your local address in your browser. The default address is as follows:

```text
http://127.0.0.1:8765/
```

If the `8765` port is used, you will find the following empty ports automatically.

### Install on GitHub

The following can be installed in the public repository.

```bash
pipx install git+https://github.com/AIjunja/oh-my-skills.git
oh-my-skills gui
```

To install without `pipx`:

```bash
python -m pip install git+https://github.com/AIjunja/oh-my-skills.git
oh-my-skills gui
```

`skill-ledger` command remains alias for existing compatibility.

### Installation for development

```bash
git clone https://github.com/AIjunja/oh-my-skills.git
cd oh-my-skills
python -m pip install -e .
oh-my-skills gui
```

## CLI

Create Markdown inventory:

```bash
python -m skill_ledger scan --format markdown --out inventory/skills.md
```

JSON Generating:

```bash
python -m skill_ledger scan --format json --out inventory/skills.json
```

Check the redundancy and metadata warning:

```bash
python -m skill_ledger doctor
```

Scan only for specific folders:

```bash
python -m skill_ledger scan \
  --root ~/.codex/skills \
  --root ~/.claude/skills \
  --format markdown
```

## GUI Usage

```bash
python -m skill_ledger gui
```

What can be done in GUI:

- See all the skills found
- Name, description, route, search as source
- Filter by source
- Check `SKILL.md`
- Edit user-owned skill
- Create new skills for Codex, Claude, Agents
- No need for user skill storage
- Export Inventory Report
- Switch to EN/KR language
- Switching light/dark theme

## Set Browser CTA

The creator CTA is displayed on the top and sidebars. `제작자 구독하기`

Type:

- [Threads](https://www.threads.com/@ai_jjuun)
- [Instagram](https://www.instagram.com/ai_jjuun/)
- [YouTube](https://www.youtube.com/@AI%EC%AD%8C)
- [GitHub](https://github.com/AIjunja)

The representative CTA phrase or URL can be changed to the environment variable.

```bash
OH_MY_SKILLS_CTA_LABEL="제작자 구독하기" \
OH_MY_SKILLS_CTA_URL="https://www.threads.com/@ai_jjuun" \
OH_MY_SKILLS_CTA_NOTE="Threads, Instagram, YouTube, GitHub에서 제작자를 구독해 주세요." \
python -m skill_ledger gui
```

PowerShell:

```powershell
$env:OH_MY_SKILLS_CTA_LABEL = "제작자 구독하기"
$env:OH_MY_SKILLS_CTA_URL = "https://www.threads.com/@ai_jjuun"
$env:OH_MY_SKILLS_CTA_NOTE = "Threads, Instagram, YouTube, GitHub에서 제작자를 구독해 주세요."
python -m skill_ledger gui
```

## Safety Model

oh-my-skills works stably.

- `codex-system`, `plugin-cache` skill is read only.
- User skill is edited only within the known user skill root.
- Create backups under `~/.oh-my-skills/backups` when saving.
- Move the skill folder to `~/.oh-my-skills/archive` when stored.
- Inventory reports may include local routes and prompts, so `inventory/` is basically excluded from Git.

## Agent Skill

This repository contains `SKILL.md` on the root and can also be installed with Agent Skill.

Codex:

```bash
git clone https://github.com/AIjunja/oh-my-skills.git ~/.codex/skills/oh-my-skills
```

Tag:

```bash
git clone https://github.com/AIjunja/oh-my-skills.git ~/.claude/skills/oh-my-skills
```

PowerShell:

```powershell
git clone https://github.com/AIjunja/oh-my-skills.git "$env:USERPROFILE\.codex\skills\oh-my-skills"
git clone https://github.com/AIjunja/oh-my-skills.git "$env:USERPROFILE\.claude\skills\oh-my-skills"
```

################################################################################################################################################################################################################################################################

- [`openai/skills`](https://github.com/openai/skills): Official Codex Skill Catalog
- [`luongnv89/asm`](https://github.com/luongnv89/asm): Universal Skill Manager CLI/TUI
- [`siddhantparadox/codexmanager`](https://github.com/siddhantparadox/codexmanager): Codex Desktop Manager

oh-my-skills focuses on smaller and clear purposes. It is a tool that already reports, organizes, and securely edits the skills installed on my computer.

## License

MIT
