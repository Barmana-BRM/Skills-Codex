<div align="center">

# Nuwa.skill for Codex

**Other Languages:**

[中文](README.md) · [日本語](README_JA.md) · [한국어](README_KO.md) · [Español](README_ES.md)

</div>

> [!IMPORTANT]
> This document was generated with AI based on the current repository content. If you spot mistakes, issues and PRs are welcome.

This repository is a Codex adaptation of the upstream project [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill). The original project was created by Huashu, and this adaptation is currently maintained by [yuc](https://github.com/Cyxxxxx). It exists to fit Codex workflows and directory conventions, and it is not the author's official release.

It keeps the core methodology of the original project:

- If the user provides a clear person or topic, distill directly.
- If the request is vague, diagnose the need first and then recommend the most suitable thinking framework.
- Extract mental models, decision heuristics, expression DNA, values, anti-patterns, and honest limits from multi-source research.
- Generate runnable `*-perspective` or `*-framework` skills instead of a collage of quotes.

At the same time, it rewires the platform-specific parts for Codex:

- The skill directory becomes `$CODEX_HOME/skills` or `~/.agents/skills/`
- The sub-agent workflow becomes `spawn_agent`
- Online retrieval becomes the `web` / browsing capability available in the current session
- If multi-agent support is unavailable, the workflow can degrade to the same sequence in serial

## Source And Attribution

- Upstream project: [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)
- Original author: Huashu
- Codex adaptation and maintenance: [yuc](https://github.com/Cyxxxxx)
- Repository positioning: a Codex adaptation maintained by yuc
- Release principle: preserve upstream attribution and do not present this repository as the author's official version

## It Is Not About Imitating Celebrities

Nuwa distills a cognitive operating system, not a catchphrase generator.

A solid person-based skill should answer at least six questions:

- What mental models does this person use to see the world?
- What decision heuristics do they use to judge quickly?
- What stable expression DNA appears in their language?
- What do they explicitly oppose?
- What tensions and contradictions exist inside their worldview?
- What can this skill explicitly not do?

If it can only imitate tone, that is role-play, not a usable thinking framework.

## How To Use It In Codex

### Install Location

Choose one:

1. Install to `$CODEX_HOME/skills/nuwa-skill`
2. Install to `~/.codex/skills/nuwa-skill`
3. If your Codex setup discovers skills from `~/.agents/skills/`, symlink this directory to `~/.agents/skills/nuwa-skill`

If you want the multi-agent workflow, make sure Codex has multi-agent support enabled.

### Repository Structure

```text
nuwa-skill/
├── SKILL.md
├── README.md
├── LICENSE
├── references/
│   ├── extraction-framework.md
│   └── skill-template.md
└── scripts/
    ├── download_subtitles.sh
    ├── merge_research.py
    ├── quality_check.py
    └── srt_to_transcript.py
```

`examples/` was not migrated into this Codex version. See the upstream project [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill) for those examples.

## Typical Triggers

These requests are a good fit for Nuwa:

- `Distill Paul Graham`
- `Build a Zhang Xiaolong perspective skill`
- `Update the Munger skill I made before`
- `My business judgment feels unstable. Recommend a thinking advisor for me`
- `I want a topic skill, not a person, something like "antifragile decision-making"`

## Workflow Overview

1. Phase 0: decide whether to distill directly or diagnose the need first.
2. Phase 0.5: create the target skill directory and keep all research files inside that skill.
3. Phase 1: collect information from six dimensions: works, conversations, expression, external perspectives, decisions, and timeline.
4. Phase 1.5: run research quality checks for source count, key findings, gaps, and contradictions.
5. Phase 2: extract mental models through triple verification.
6. Phase 2.5: present the extraction summary and confirm the direction.
7. Phase 3: assemble the final `SKILL.md` from the template.
8. Phase 4: validate quality with known questions, edge questions, and style checks.
9. Phase 5: refine with dual reviewers to improve triggers, workflow execution, and boundary conditions.

## Reference Files

- [references/extraction-framework.md](references/extraction-framework.md): how to tell a real mental model from a one-off opinion
- [references/skill-template.md](references/skill-template.md): template skeleton for person or topic skills
- [scripts/merge_research.py](scripts/merge_research.py): merge six research streams
- [scripts/quality_check.py](scripts/quality_check.py): check mental model count, boundaries, tensions, and other quality signals

## Adaptation Notes

This directory is not a line-by-line copy of the Claude Code version. It was adapted for Codex in the following ways:

- Abstract all `.claude/skills/...` paths into `<skills_root>`
- Replace the `subagent` / `Task` mental model with `spawn_agent`
- Replace `WebSearch` with the current session's available online tools
- Add a serial fallback when multi-agent support is unavailable
- Keep `references/` and `scripts/` because they are methodology and execution helpers, not platform-coupled assets

## License

This repository keeps the upstream MIT license. See `LICENSE` for details.

If you redistribute or adapt it further, keep the original copyright and license notices, and clearly distinguish between the original author and the maintainer of the current adaptation or derivative version.
