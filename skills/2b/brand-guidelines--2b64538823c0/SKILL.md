# Brand Guidelines

The canonical reference for [your-company]'s brand identity. Load this before creating any branded content.

## MCP connectors

None required. This skill operates on local repo files only.

## Personality traits

| Trait | What it means | What it's NOT |
|-------|--------------|---------------|
| **Direct** | Say it plainly, skip the preamble | Blunt or rude |
| **Technical** | Grounded in real engineering | Jargon-heavy or gatekeeping |
| **Warm** | Peer-to-peer, peer conversation | Corporate or sycophantic |
| **Opinionated** | Take a clear stance, back it up | Arrogant or dismissive |
| **Playful** | Light touches of humor, not forced | Goofy or unprofessional |

## Writing rules

1. **No em dashes** - never use --- or --; replace with `-` or `:`
2. **No ghostwriter tells** - avoid "had a blast", "banger", "nails it", "game-changer"
3. **First person** - "we" for the company, "I" for the CAO's personal content
4. **Short sentences** - cut filler, tighten every line, one idea per sentence
5. **Specific over generic** - numbers over adjectives, examples over claims
6. **CAO's name** - always spell the CAO's name correctly (check CONTEXT.md)

## Tone spectrum

| Context | Tone | Example |
|---------|------|---------|
| LinkedIn post | Conversational, peer-to-peer | "Here's what broke when we..." |
| Blog article | Technical, teaching | "The query runs in 200ms because..." |
| Substack | Reflective, leadership journey | "Three months in, the numbers say..." |
| Sales email | Warm, direct, concise | "Saw your team ships dbt models - we built [your-product] for exactly this" |
| Product docs | Clear, precise, minimal | "Run `[your-cli] init` to connect your warehouse" |
| Slack community | Casual, helpful, brief | "Just shipped this - let us know what you think" |

## Visual system

### Colors

| Name | Hex | Usage |
|------|-----|-------|
| Primary Black | `#1A1A1A` | Primary text, headings |
| Primary White | `#FAFAFA` | Backgrounds |
| Accent Blue | `#2563EB` | Primary accent, CTAs, links |
| Secondary Gray | `#6B7280` | Secondary text, borders |
| Light Gray | `#F3F4F6` | Card backgrounds, code blocks |

### Typography

| Element | Font | Weight |
|---------|------|--------|
| Headings | Inter | 600 (Semi-bold) |
| Body | Inter | 400 (Regular) |
| Code | JetBrains Mono | 400 |

### Logo

- Primary: horizontal lockup (icon + wordmark)
- Icon only: for small sizes (favicons, avatars)
- Minimum clear space: 1x icon height on all sides
- Never stretch, rotate, recolor, or add effects

## Asset locations

| Asset | Location |
|-------|----------|
| Logo files | `brand/assets/logo/` |
| Color palette | `brand/assets/colors/` |
| Font files | `brand/assets/fonts/` |
| Templates | `brand/assets/templates/` |
| Slide deck template | Canva template `[your-canva-template-id]` |
| Social media templates | `brand/assets/social/` |

## Self-improvement

After the CAO corrects brand usage in any content:

1. Identify which guideline was violated or missing
2. If the correction reveals a rule not captured here, add it to the appropriate section
3. If a tone example is outdated, replace it with the corrected version
4. Update `brand/_insights.md` with the pattern (what was wrong, what the CAO wanted)
5. If the correction applies across channels, update the Writing rules or Tone spectrum tables
