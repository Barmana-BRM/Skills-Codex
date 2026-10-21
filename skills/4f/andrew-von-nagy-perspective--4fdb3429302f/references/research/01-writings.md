# Andrew von Nagy — Writings & Long-form Material

> Source extraction for the von Nagy person-perspective sub-skill. Materials are pulled from the parent ubnt-wifi-master skill's Phase 1 research (Tracks 01, 04, 05). No fresh web search performed — Phase 1 already inventoried these. Marked extraction date 2026-06-02.

## A. Primary long-form (his own writing)

### A1. Revolution Wi-Fi blog (2009–present)
- **URL**: http://revolutionwifi.blogspot.com/ (T01-S007 / T05-S024)
- **Cadence**: rolling, low frequency; sparse 2024–2025 posts. He now ships more content via podcast guest + Tech Field Day delegate footage than blog posts.
- **Why it's canon**: This is where capacity-first design was first articulated in long form (2009–2013 most prolific). The community treats specific posts as canonical — they get re-cited by NETGEAR / Cisco / Aruba design WP authors years later.
- **Signal note**: Slow cadence flagged in Track 05 sources review — "high-signal-but-low-frequency, retain mainly for canonical references." (T05 lines 559, 573)

### A2. "Design Your WLAN for High Capacity" (Dec 2012)
- **URL**: http://revolutionwifi.blogspot.com/2012/12/design-your-wlan-for-high-capacity_10.html (T04-S029)
- **Why it matters**: The single most cited post in the parent skill's canon — listed as Tier-1 mental model #11 "High-density / capacity-first design" (T04 line 657-664). Cited by NETGEAR High-Density Best Practices white paper (T04-S031). Forms the math template re-used in the parent skill's Playbook rule #2 ("clients × per-client throughput ÷ AP capacity × 30-50% concurrency factor = AP count").
- **Core argument** (per the citing canon entry): density × per-user throughput SLA → total capacity demand → AP count. NOT "1 AP per X sqm coverage."

### A3. Capacity planning spreadsheets
- Referenced repeatedly in synthesis.md (line 122): "optimize 复用 vonNagy capacity-budget spreadsheet 跨项目"
- These are explicit math artifacts — not prose, but reusable templates that turned "capacity-first" from intuition into computation.

## B. Recurring core arguments (≥3 instances = real belief)

Cross-referenced across canon (T04) + synthesis (§1.1, §1.2) + figure entry (T01-S007 voice samples):

### B1. "More APs ≠ better Wi-Fi in dense scenarios"
- Stated in: capacity blog series, MFD delegate commentary, CTS podcast guest spots, voice_sample 1
- Direct quote (转述): "在高密度场景，加 AP 反而让 Wi-Fi 更慢是常见误区 — 真正的瓶颈是同信道干扰 (CCI)，而不是覆盖。"
- Crystallizes into mental model: **Capacity-first, coverage second** (parent synthesis §1.1)

### B2. "Retry rate is the diagnostic signal, not RSSI"
- Stated in: blog series, MFD delegate commentary, CTS podcast guest, voice_sample 2
- Direct quote (推断): "你给我看 -65 dBm RSSI 没意义，告诉我 client 端的 retry 率和 802.11k 邻居表."
- Note: Mackenzie also says this — but the parent synthesis (§1.2) attributes the framing to vonNagy as primary, Mackenzie as confirming/applying.

### B3. "Predictive ≠ delivered" (validation is non-negotiable)
- 思想关键词 #5 in T01-S007: "validation > prediction (predictive design ≠ delivered design)"
- Reinforced by synthesis §6.1 #2: "「好」 = 设计有 predictive 闭环 validation (post-install survey 与设计对比)"
- This is not unique to vonNagy (Mackenzie + CWDP also push it) but vonNagy frames it specifically as "your spreadsheet model is a hypothesis until the AP-on-a-stick says it's true."

### B4. "Client diversity is the dominant uncertainty"
- Implicit across his client-airtime-budget math: per-client throughput SLA is computed from worst expected client, not best.
- Also surfaces in his Tx power asymmetry framing (T04 canon entry #20, T04-S029): "AP 信号强不等于客户端能回包 — 客户端通常 Tx power 仅 14-18 dBm" — credited to vonNagy.

### B5. "Spectrum is shared, not private"
- Foundational to his channel reuse math (T01 思想关键词 #3: "channel reuse math (距离 × dB × overlap threshold)")
- Tx power asymmetry mental model (T04 #20) is a downstream consequence — your neighbor's AP and your client's transmit power both matter.

## C. Self-coined terms / signature vocabulary

Pulled from T01-S007 思想关键词 + synthesis §1.1/§1.2 + canon §11/§19/§20:

- **"airtime budget per client"** — his framing for client capacity, not Mbps but seconds of airtime / sec
- **"capacity envelope"** — the throughput × concurrent client ceiling per AP
- **"channel reuse math"** — distance × dB × overlap threshold (formula, not prose)
- **"high-density antenna pattern"** — directional + downtilt as opposed to omni
- **"Tx asymmetry" / "client transmit budget"** — credited directly to vonNagy in T04-S029
- **"validation > prediction"** — repeated formulation

## D. Recommended reading / intellectual lineage clues

- He cites and is cited alongside CWDP-304 (the certified wireless design pro book) — strong overlap with Coleman / Westcott / Mackenzie material
- He is a regular Mobility Field Day (MFD) delegate — peer reviewers include Lee Badman, Sam Clements, Keith Parsons
- He guests on Clear To Send podcast (capacity + Wi-Fi 7 themes) — Akin / Parsons / Mackenzie are co-guests, suggesting the CWNP / CWNE / WLPC orbit is his peer set
- He does NOT publish in academic venues — his lineage is industry-practitioner, not IEEE 802.11 spec authorship (which is Gast / Henry / Vanhoef's lane)

## E. Coverage gaps / what's NOT in his long-form output

- No book — no Sybex / O'Reilly / Wiley title under his name
- Sparse 2024–2026 blog activity; most recent thinking is in podcast / MFD video form
- Light coverage of Wi-Fi 6E / 6 GHz specifics in long-form (older posts predate 6 GHz allocation in 2020)
- No public-facing material on his current Nile role's product internals (NDA, presumably)

## F. Evidence URLs (consolidated)

| ID | URL | Type |
|----|-----|------|
| T01-S007 | http://revolutionwifi.blogspot.com/ | Primary |
| T04-S029 | http://revolutionwifi.blogspot.com/2012/12/design-your-wlan-for-high-capacity_10.html | Primary (anchor post) |
| T04-S031 | https://www.netgear.com/images/pdf/High_Density_Best_Practices.pdf | Secondary (cites his work) |
| T01-S008 | https://techfieldday.com/people/andrew-vonnagy/ | Surrogate primary (bio) |
| T01-S033 | https://www.cleartosend.net/ | Reference (recurring guest) |
| T01-S041 | https://nilesecure.com/about | Primary (current employer) |
