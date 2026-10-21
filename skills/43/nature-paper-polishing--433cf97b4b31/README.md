# Nature Paper Polishing Codex Skill

Codex skill for polishing academic manuscript text with Nature-aware scientific style.

It is useful for:

- Chinese-to-English academic manuscript polishing
- Abstract, introduction, results, discussion, conclusion, methods, and title edits
- Claim calibration, hedging, citation wording, and overclaim detection
- British English and concise scientific prose checks

This skill does not generate scientific facts, references, results, or acceptance guarantees. It preserves the author's content and flags missing evidence or citation issues.

## Install

Clone this repository into your Codex skills directory:

```powershell
git clone https://github.com/AlexZander-666/nature-paper-polishing-codex-skill C:\Users\black\.codex\skills\nature-paper-polishing
```

Or copy the repository folder to:

```text
C:\Users\black\.codex\skills\nature-paper-polishing
```

Then invoke it with prompts such as:

```text
Use $nature-paper-polishing to polish this manuscript section for clarity, calibrated claims, citations, and Nature-aware academic style.
```

## Attribution

Adapted from Yuan Yizhe's MIT-licensed `nature-polishing` skill:

https://github.com/Yuan1z0825/nature-polishing

This Codex version keeps the useful academic writing guidance while changing the frontmatter, trigger description, output workflow, safety boundaries, and Codex UI metadata.
