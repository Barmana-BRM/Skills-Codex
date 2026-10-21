# Output Risk Profile

## High-Risk Failures

- Treating a knowledge base as a long brand introduction instead of reusable fact cards.
- Omitting the systematic knowledge-base body and leaving only audit tables.
- Omitting the complete entity inventory, which causes downstream skills to miss products, aliases, competitors, channels, and pending boundaries.
- Producing a detailed report without a visible completeness self-check, making gaps hard to audit.
- Mixing brand self-description, official evidence, third-party evidence, and pending facts into one confidence level.
- Omitting source IDs, verification dates, or update cadence.
- Implying the skill can always retrieve private, login-gated, paid, or region-specific data.
- Letting wide fact-card/source-index tables overflow in Word or PDF.
- Copying unverified China-market claims into the strong-evidence or prompt-input area.

## Controls

- Official-source-first evidence collection.
- A/B/C/D confidence tiers with pending-confirmation separation.
- Mandatory fact cards with source ID, update time, confidence, and use scenario.
- Mandatory systematic KB sections and complete entity inventory checks.
- Mandatory real-data access and freshness boundary with acquisition mode, inaccessible sources, and next data-access actions.
- Mandatory authoritative reference alignment and analysis completeness self-check.
- HTML sticky menu for long report navigation.
- Fixed-layout four-format renderer with DOCX and PDF overflow checks.
- Prohibited-expression section for claims that cannot be safely reused.

## Review Signals

- `quality-report.json` must pass.
- DOCX must report fixed tables, body-width `dxa`, no `w:noWrap`, and no long unbreakable token.
- PDF must be preview-rendered and pass the right-edge scan.
- Source index must keep publisher, source type, verification date, and URL.
- Strong facts must come from accessible, cited, time-stamped sources; unavailable sources stay in pending confirmation.
