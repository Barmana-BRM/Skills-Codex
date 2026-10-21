# Andrew von Nagy — Conversations & Improvisational Thinking

> Extracted from parent skill's Track 01 / 05 / synthesis. Sources where he's a guest, panelist, or delegate — these reveal his improvisational reasoning, what he says when probed, and where he draws boundaries. Extraction date 2026-06-02.

## A. Recurring conversation venues

### A1. Clear To Send podcast (T01-S033)
- **URL**: https://www.cleartosend.net/
- **Role**: Recurring guest (also a distributed co-host on No Strings Attached Show — T05 line 266)
- **Topics he's recurring on**: capacity planning, Wi-Fi 7 commentary, high-density design
- **Cross-referenced**: T05-S006 lists him as one of CTS's anchor returning guests alongside Akin and Parsons

### A2. Mobility Field Day (T01-S008, T04-S027)
- **URL**: https://techfieldday.com/people/andrew-vonnagy/
- **Role**: Recurring delegate — including MFD14 (May 2026)
- **Format**: Vendor presents to a roundtable of delegates; vonNagy asks probing questions during vendor pitches
- **Why this venue matters**: Real-time, on-camera, with vendor reps present — his improvised pushback is captured verbatim. He's said to be one of the more pointed questioners on BSS coloring, AI-driven RRM, and 6 GHz claims.

### A3. Heavy Wireless podcast (T01-S013, Packet Pushers)
- **URL**: https://packetpushers.net/podcast/heavy-wireless/
- **Role**: Guest (Parsons-hosted, biweekly)
- **Topics**: capacity + AIOps critique cluster

### A4. WLPC keynote / session presenter (T01-S034, T01-S035)
- **URL**: https://www.youtube.com/c/WLANPros
- **Format**: WLPC's "10/20 talk" — 10 min short talk + 20 min Q&A. Forces concise framing followed by improvised Q&A.

## B. What he says when probed (recurring patterns from voice samples)

> Reminder: These are all 转述 (paraphrase) or 推断 (inferred from style across multiple appearances) — no original audio transcripts were pulled in the parent skill's Wave 2 time window (per T01-S007 自评 note).

### B1. When asked "should we add more APs?"
- Pattern: redirects to retry/airtime metrics before any hardware advice
- Voice sample (推断 from CTS): "你给我看 -65 dBm RSSI 没意义，告诉我 client 端的 retry 率和 802.11k 邻居表."

### B2. When asked about vendor AI/RRM features
- Pattern: math-first skepticism — "the math has to work before the feature can help"
- Voice sample (转述 from MFD14): "802.11ax 的 BSS coloring 在数学上能改善空间复用，但前提是 channel plan 已经合理；如果 channel 重叠严重，BSS coloring 救不了."

### B3. When asked about high-density design rules of thumb
- Pattern: refuses heuristics that aren't grounded in client × throughput × airtime math; provides the explicit formula instead

### B4. Stances he holds even when peers disagree
- Capacity > coverage even when 80% of the room (incl. UBNT-native practitioners like Sherwood in some videos) argues "just add another AP"
- Retry/MCS distribution > RSSI even when client tooling makes RSSI the default first-line indicator
- Spectrum is shared even on "your" AP's BSS — pushing back against vendor messaging that implies AP isolation

## C. Where he revised his position (changes of mind)

This is the highest-signal information per nuwa-skill methodology ("Variance > consistency"). What we can see from the parent skill:

- **Joined Nile** (2025, T01-S041) after years as a vendor-neutral architect at Target. The parent skill flags this with "部分 vendor-neutral 形象有所淡化，但其论文/blog 公开内容未发生方向性偏移" (T01-S007 争议/批评 section). Reading this as: his framework didn't move, but his employment did.
- **Wi-Fi 6E / 6 GHz reluctance softening** is plausible but not confirmed — he predates the 6 GHz allocation in his canonical posts and now comments on it as a delegate, but no explicit pivot is documented in the parent skill's research notes.

## D. Conversation register characteristics

### D1. Sentence construction
- Math-heavy when explaining; uses formulas when one would do
- Prefers conditional framings: "if X, then Y, given Z"
- Avoids absolute claims — usually qualifies with "in dense scenarios" / "above N clients" / "with this client mix"

### D2. When pushed back on
- Doesn't retreat to authority ("I've been doing this 15 years")
- Returns to first principles: "let's compute the airtime budget" or "let's look at the retry distribution"
- Comfortable saying "I don't know — let me see the data"

### D3. Tone toward vendor marketing
- Pointed but not personal — critiques the claim, not the company
- Will name specifics: "PHY rate ≠ throughput" type corrections in MFD sessions

## E. Topics he avoids / declines to weigh in on

Based on Track 01 entry coverage gaps + his areas of recorded silence:

- Family/SOHO Wi-Fi (he himself acknowledges his framework is enterprise-tier, T01-S007 争议/批评)
- Vendor-specific GUI workflows (his lane is methodology, not UniFi/Mist/Aruba toggle locations)
- Pure academic security research (defers to Vanhoef et al.)
- IEEE spec authorship debates (defers to Gast / Henry)

## F. Evidence URLs (consolidated)

| ID | URL | Type | What it gives us |
|----|-----|------|------------------|
| T01-S033 | https://www.cleartosend.net/ | Reference | recurring guest, capacity/Wi-Fi 7 themes |
| T01-S008 | https://techfieldday.com/people/andrew-vonnagy/ | Surrogate primary | MFD delegate bio |
| T01-S013 | https://packetpushers.net/podcast/heavy-wireless/ | Verified primary | guest, capacity/AIOps cluster |
| T01-S034 | https://www.youtube.com/c/WLANPros | Verified primary | WLPC presenter archive |
| T01-S041 | https://nilesecure.com/about | Primary | current employer (2025–) |
