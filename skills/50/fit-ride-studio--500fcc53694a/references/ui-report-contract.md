# Ride Relief UI enrichment contract

Use this contract after every successful analysis before opening the local Ride Relief report page. The deterministic analyzer remains the source of numeric facts; this file carries model-written interpretation.

Write a temporary JSON file with this shape. Keep per-user analysis out of the Skill source directory:

```json
{
  "schemaVersion": 1,
  "reports": [
    {
      "source": "exact-track-basename.fit-or-kml",
      "provider": "Fit Ride Studio Skill",
      "generatedAt": "2026-08-08T12:00:00.000Z",
      "location": {
        "name": "Public place name",
        "region": "Coarse public region",
        "exportLabel": "Short public-safe label",
        "confidenceLabel": "用户已确认 or 地点候选 · 待用户确认",
        "summary": "Grounded place context with uncertainty.",
        "facts": ["Stable or time-stamped fact"],
        "sources": [{ "title": "Source title", "url": "https://...", "retrievedAt": "2026-08-09" }]
      },
      "deepAnalysis": [
        {
          "category": "路线负荷",
          "evidence": "18.2 m/km · 3 段主要爬坡",
          "title": "起伏集中在后半程",
          "body": "Explain the pattern and its limits in two or three grounded sentences.",
          "findings": ["One supporting observation", "One caveat or comparison"]
        }
      ],
      "recommendations": [
        {
          "category": "节奏",
          "evidence": "82% 移动占比",
          "title": "Reduce avoidable interruptions",
          "body": "Explain why this matters for this ride.",
          "actions": ["Concrete next action", "A second practical action"]
        }
      ],
      "note": "Optional short scope or confidence note."
    }
  ]
}
```

## Rules

- Match `source` to the exact FIT or KML basename emitted by the analyzer. The page ignores non-matching reports.
- Add `location` only after following `location-enrichment.md`. Keep the region coarse, label unconfirmed candidates, and attach direct public sources with retrieval dates. The page uses `exportLabel` in the export card.
- A temporary file may contain only the selected report. When retaining multiple reports, replace the entry for the same source instead of duplicating it.
- Produce two to six `deepAnalysis` sections chosen from the available evidence. Do not force empty dimensions.
- Use `category` and `evidence` as compact labels. Put interpretation in `body`; put supporting facts or caveats in `findings`.
- Produce two to eight recommendations ordered by impact. Each should include one to three practical `actions` when action is justified.
- Do not repeat the fixed totals card. Prefer relationships, anomalies, coverage limits, route segments, cross-metric patterns, and exceptions.
- Never expose coordinates. Do not invent zones, thresholds, health claims, FTP, VO₂max, training load, or recovery status.
- Distinguish absent data from zero and retain the analyzer's weighting and coverage rules.
- Keep each body concise enough for the report sidebar: normally 45–120 Chinese characters or one short paragraph.

After writing the file, stage it with the matching track:

```bash
node scripts/prepare-report.mjs --track <track.fit-or-kml> --analysis <temporary-report.json>
```

Open the returned URL. It loads both resources from a private OS temporary directory and does not require browser automation of the file input. With visual capability, verify that the **深度分析** badge reads `Fit Ride Studio Skill` and recommendation actions render without clipping. Without visual capability, ask the user to inspect the page and do not claim visual verification.
