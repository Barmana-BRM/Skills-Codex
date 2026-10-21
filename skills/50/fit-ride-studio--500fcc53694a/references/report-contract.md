# FIT/KML activity report contract

The analyzer prints either JSON or Markdown. JSON uses schema version `1` and contains basenames only; it does not expose GPS coordinates.

## Shared rules

- Distance is meters in JSON and kilometers in Markdown.
- Duration values are seconds in JSON and clock-formatted in Markdown.
- Speed is km/h, running/hiking pace is seconds per kilometer, ascent/descent is meters, cycling cadence is rpm, running step cadence is spm when the device convention is known, heart rate is bpm, power is watts, and temperature is °C.
- `null` means unavailable. A numeric zero is kept only when it is a meaningful recorded or session value.
- Coverage is the percentage of GPS records with a valid non-zero sensor value, except temperature and grade, where zero is valid.
- The parser only analyzes activities with at least two GPS records. Supported inputs are FIT and KML.
- A geometry-only KML has `hasTimeData: false`; duration, pause, speed, and pace fields stay `null`. Never turn these nulls into zero.
- For KML, use the declared `SportTypeName` when available, otherwise infer conservatively. Prefer declared distance/ascent/descent metadata and the longest LineString or `gx:Track` for geometry.

## Single report

`mode` is `single`. The `ride` object contains:

- `source`, `startTime`, and normalized `sport` (`cycling`, `running`, `hiking`, or `other`)
- `summary`: totals, availability flags, sport-appropriate averages/maxima, terrain classification, and route-shape information
- `dataQuality`: record count and cadence/heart-rate/power/temperature/grade coverage
- `distributions`: speed, cadence, and distance-weighted grade bands when supported
- `climbs`: up to three continuous climbs with start distance, length, elevation gain, average grade, and a representative peak grade
- `recommendations`: evidence-backed suggestions inherited from the application analyzer

The deterministic report may be enriched for the local UI without changing these numeric fields. Read `ui-report-contract.md` when writing model-generated deep-analysis sections or expanded recommendations to the Ride Relief page.

Effective cadence excludes zero values. For cycling, this avoids treating coasting as low pedaling cadence; for running, confirm whether the device reports single-leg or total step cadence. Always show coverage alongside it.
Grade bands are `<−3%` descent, `−3–3%` flat, `3–6%` climb, and `>6%` steep, weighted by analyzed distance rather than sample count. `representativeGradePercent` is the smoothed P99; `maxGradePercent` preserves the recorded or spatially derived maximum and may be sensitive to altitude noise. A key climb must be at least 200 m long, average at least 2.5%, and gain at least 8 m.

## Aggregate report

`mode` is `aggregate`. The report contains:

- `summary`: unique activity count, sport counts, time-data coverage, totals, weighted metrics, and sensor coverage
- `rides`: compact per-activity rows including sport
- `bests`: sources for longest, fastest-average, and highest-ascent rides
- `trend`: earliest-to-latest deltas; these are descriptive comparisons, not causal training claims
- `insights`: batch-level observations and recommendations
- `duplicates`: excluded likely duplicate files
- `failed`: files that could not be parsed

Aggregate weighting:

- Average speed = distance from activities with valid time ÷ their total moving time. Never include geometry-only KML distance in the numerator.
- Cadence, heart rate, power, and temperature are weighted by valid sample count.
- Total calories sum only available device estimates and report ride coverage separately.
- Record-level coverage uses valid sensor samples ÷ all GPS records.

Duplicate key: sport + normalized start time + rounded distance + rounded moving duration. A track without time is not deduplicated solely by distance because that would create false matches.
Pass `--keep-duplicates` to override this protection after confirming the activities are genuinely distinct.

## Interpretation limits

- FIT device fields and firmware behavior vary. KML exporters vary in metadata and timestamp coverage. Treat calories as estimates.
- Grade can be missing even when altitude exists. Do not infer exact grade distribution from ascent alone.
- Treat key-climb start distance as approximate and do not expose coordinates.
- GPS and barometric altitude can drift. KML altitude-derived grade is spatially smoothed but can still overstate short steep segments.
- Heart rate and power are useful only when their coverage is adequate. Do not create personal zones without the user's thresholds.
- Privacy risk is inferred from route closure and start/end proximity. Never reveal the underlying coordinates in the response.
