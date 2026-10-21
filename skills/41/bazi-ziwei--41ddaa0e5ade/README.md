# bazi-ziwei-skills

AI BaZi (Four Pillars) + Zi Wei Dou Shu chart calculation & cross-verification Skill

Precise algorithmic charting (no LLM guessing) · Three analysis modes · One-click ink-wash-style HTML poster

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

[简体中文](./README.md) | English

<br>

<a href="./docs/jietu.png" target="_blank"><img src="./docs/jietu.png" alt="Cross-verification poster example" width="680"></a>

<sub>Cross-verification poster example (synthetic subject, for demonstration only)</sub>

---

## What is this

A fortune-telling analysis Skill following the [SKILL.md open standard](https://code.claude.com/docs/en/skills), installable into any Agent that supports it — Claude Code, Claude Desktop, Codex, Cursor, Workbuddy, etc.

It does three things a raw LLM is bad at:

1. **Precise charting**: BaZi four pillars, Zi Wei Dou Shu's twelve palaces, decade/annual luck cycles are computed by a deterministic algorithm engine — **the LLM never charts on its own**. Pure-LLM charting frequently gets the day pillar, day master, or pattern wrong, and one wrong step invalidates the entire reading.
2. **Enrichment layer**: on top of the raw chart, a second layer computes pattern (格局) / strength (旺衰) / climate balance (调候) / clashes & combinations (刑冲合害) / canopy-cutting (盖头截脚) — giving the LLM a grounded basis for analysis.
3. **Cross-verification**: cross-checks the conclusions from the two independent systems (BaZi and Zi Wei Dou Shu) — do the main themes agree, do the life-stage windows align, and which system to trust when they conflict.

## ✨ Features

- 🎯 **Accurate charting**: powered by open-source projects mingpan (BaZi, Apache-2.0) + iztro (Zi Wei Dou Shu, MIT), verified against test cases; enrichment layer regression-tested across 7 cases
- 🧭 **Three analysis modes**: BaZi only / Zi Wei Dou Shu only / BaZi + Zi Wei Dou Shu cross-verification
- 📜 **Two output formats**: in-depth Markdown essay + 🎴 single-file HTML poster (cross-verification exclusive)
- 🖼️ **Ink-wash-style chart poster**: modern minimalist × Chinese ink-wash aesthetic, with a 12-palace Zi Wei chart + BaZi four-pillar chart + six-dimension cross-check, screenshot-friendly
- 🛠️ **Cross-Agent**: one SKILL.md, works across mainstream Agents
- 🔒 **Privacy-first**: all charting runs locally, no network required; run artifacts are gitignored by default

## Installation

1. Clone this repository
2. `cd calculator && npm install`
3. Register it with your Agent (see your Agent's SKILL.md loading instructions)

## Usage

See [SKILL.md](./SKILL.md). To chart directly from the command line (without an Agent):

```bash
cd calculator
npx tsx run-chart.ts --year=2000 --month=1 --day=1 --hour=12 --minute=0 --gender=male
```

## Directory structure

```
├── SKILL.md          ← Skill definition (trigger conditions, execution flow)
├── calculator/         ← Charting engine (mingpan for BaZi + iztro for Zi Wei Dou Shu + enrichBazi layer)
├── prompts/             ← Analysis prompts
└── templates/            ← Poster templates
```

## 🏗️ How it works

Charting (algorithmic layer, deterministic) → text conversion (structured text) → LLM analysis (produces conclusions from prompts) → (optional) HTML poster rendering.

**Key design**: the LLM is only responsible for "analysis," never for "charting" or "drawing HTML." Charting is handled by deterministic algorithms, visual presentation by a fixed template, and the LLM's structured output fills the template's slots — each layer stays in its lane.

## 🙏 Acknowledgements

- BaZi charting engine: [mingpan](https://github.com/ChesterRa/mingpan) (Apache-2.0)
- Zi Wei Dou Shu charting engine: [iztro](https://github.com/SylarLong/iztro) (MIT)
- Lunar calendar conversion: [lunar-typescript](https://github.com/6tail/lunar-typescript) (MIT)

## ⚠️ Disclaimer

This analysis is based on traditional BaZi and Zi Wei Dou Shu theoretical frameworks. It is provided for cultural research and entertainment purposes only, and does not constitute medical, financial, marital, or legal advice. One's destiny is shaped by personal choice and circumstance, not predetermined.

## 📄 License

This project is licensed under the [MIT License](./LICENSE).
