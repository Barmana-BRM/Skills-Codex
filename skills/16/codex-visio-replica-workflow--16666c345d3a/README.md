# Codex Visio Replica Workflow

This repository contains a Codex skill for recreating reference diagrams, screenshots, whiteboard diagrams, architecture diagrams, flowcharts, and business diagrams in Microsoft Visio.

It includes:

- `SKILL.md`: the main skill instructions.
- `agents/openai.yaml`: marketplace/display metadata.
- `references/plan_schema_and_qa.md`: JSON plan schema and QA checklist.
- `scripts/check_visio_environment.ps1`: Visio and export environment checker.
- `scripts/create_visio_from_plan.ps1`: script for generating editable `.vsdx` files from a JSON plan.

## Install

Copy the `codex-visio-replica-workflow` folder into your Codex skills directory:

```powershell
$skills = "$env:USERPROFILE\.codex\skills"
New-Item -ItemType Directory -Force -Path $skills | Out-Null
Copy-Item -Recurse -Force ".\codex-visio-replica-workflow" $skills
```

Then restart Codex or reload skills.

## Example Prompt

```text
Use $codex-visio-replica-workflow to recreate this reference image as an editable Visio file, export a preview, and prepare a screen-recording friendly workflow.
```

## Notes

This skill is designed for Windows environments with Microsoft Visio installed. The scripts use PowerShell and Visio COM automation.
