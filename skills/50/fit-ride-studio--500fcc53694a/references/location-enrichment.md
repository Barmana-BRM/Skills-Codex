# Place-aware activity enrichment

Use this workflow only when place context would improve route preparation, safety advice, storytelling, or export labeling.

## 1. Resolve a public place name

- Read the track title, KML document metadata, start/end names, and locally derived coarse area.
- Never send the full track or exact coordinates to a search service.
- Prefer a place candidate such as `北灵山 · 京冀交界` over a precise trailhead or parking location.
- If the name is ambiguous, ask one short confirmation question before using location-specific advice: `这条“北灵山”是京冀交界、怀来一侧的北灵山吗？`
- Skip the confirmation only when the user already supplied an unambiguous place and region.

## 2. Search public information

Use current web research for claims that can change. Prioritize sources in this order:

1. Government, park, scenic-area, emergency-management, fire, transport, and meteorological authorities.
2. Official tourism or protected-area pages for stable geography and environment facts.
3. Recent route reports only for clearly attributed experiential details; do not treat them as access authorization.

Check publication date, event date, current validity, and jurisdiction. A warning from the Beijing side may not govern a Hebei-side entrance. Label expired notices as historical context rather than current restrictions.

## 3. Produce grounded advice

- Separate stable facts from live conditions.
- Tie advice to both the deterministic track metrics and the verified place context.
- For hiking, prefer actionable checks such as route opening, fire or flood restrictions, daylight, temperature change, water availability, navigation, and retreat options.
- For cycling or running, consider surface, traffic restrictions, elevation, exposure, supply points, and transport access when verified.
- Never claim that a route is safe, open, or legal solely because an uploaded activity completed it in the past.
- Include source titles, direct URLs, and retrieval dates. Say when the place is only a candidate.

## 4. Enrich the local report and export

When writing the temporary report JSON described by `ui-report-contract.md`, add an optional `location` object:

```json
{
  "name": "北灵山",
  "region": "北京门头沟—河北怀来交界山地",
  "exportLabel": "北灵山 · 京冀交界",
  "confidenceLabel": "用户已确认",
  "summary": "Two or three grounded sentences.",
  "facts": ["Stable or time-stamped fact", "Practical local note"],
  "sources": [
    {
      "title": "Direct source title",
      "url": "https://example.gov/source",
      "retrievedAt": "2026-08-09"
    }
  ]
}
```

Keep `exportLabel` short and public-safe. Do not put exact coordinates, a private meeting point, a vehicle location, or a home address in the report or exported overlay.
