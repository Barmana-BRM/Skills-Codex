---
name: sales-deck
description: Creates B2B sales narrative decks using April Dunford's methodology. Outputs slide-by-slide Markdown outline plus optional PPTX generation. For external sales prospects.
autoload: false
---

# Sales Deck Creator

This skill creates highly effective B2B sales decks using April Dunford's 8-step sales pitch methodology. It produces a slide-by-slide Markdown outline and can generate a PPTX file.

## Core Philosophy

The goal of a sales pitch is not to list product features. It is to help customers understand their choices, evaluate trade-offs, and realize exactly when and why they should choose your solution.

The framework has two distinct phases:
1. **The Setup** (Slides 1 to 10): Establish market context and "Perfect World" criteria. Do not mention your product.
2. **The Follow-Through** (Slides 11 to 17): Introduce your product and map it directly to the criteria established in the Setup.

This structure combats "no decision" paralysis by giving buyers a clear framework before asking them to evaluate your solution.

> **SCQA alignment:** This framework naturally follows the McKinsey SCQA pattern. Status Quo = Situation, Disruption = Complication, Perfect World = Question, Product Introduction = Answer. The narrative logic should feel inevitable by the time you reveal your product.

---

## Step 1: Gather Inputs

**Read from repo automatically:**

| File | What to extract |
|------|-----------------|
| `docs/inputs/product_brief.md` | Product name, key capabilities, limitations, customer names |
| `docs/inputs/messaging_positioning.md` | Positioning statements, pain points, value propositions |
| `docs/inputs/competitor_intel.md` | Competitor approaches, weaknesses, market categories |
| `docs/inputs/testimonials.md` | Approved quotes, customer results, case study data |
| `docs/inputs/target_personas.md` | Who feels the pain, titles, buying triggers |

Read these files BEFORE asking for additional inputs.

**Then ask the user:**

1. **Who is this deck for?** (e.g., "Series B fintech CISOs" or "Enterprise DevOps leads evaluating CI/CD")
2. **What is your provocative insight?** The bold claim about what is fundamentally shifting in the market. If the user does not have one, help them derive it from the messaging doc.
3. **What alternatives will buyers consider?** (e.g., "do nothing," "incumbent vendor," "build in-house," "point solution competitor")
4. **What is the ask at the end?** (e.g., "15-minute technical deep dive," "POC," "security review")

Wait for answers before generating.

---

## Step 2: Build the Narrative Arc

Construct the deck following the 8-step structure below. Each step maps to specific slides.

---

## The 8-Step Slide Structure

### Part 1: The Setup

**Do not mention your product during the Setup phase.**

---

#### Step 1: The Provocative Insight (Slides 1 and 2)

**Purpose:** Open with a bold claim about what is fundamentally shifting. This frames the conversation and points toward your differentiated value.

**Slide 1: Title/Thesis**
- One bold statement (the provocative insight)
- No product name, no company name
- Example: "The perimeter is dead. Identity is the new firewall."

**Slide 2: TLDR / Executive Summary**
- 3 to 5 bullet summary of the entire argument
- Ensures the buyer understands the narrative arc immediately
- Include: the shift, why it matters, what the new criteria are, what you offer

---

#### Step 2: The Status Quo Context (Slides 3 and 4)

**Purpose:** Acknowledge how the current world was built and why those choices were rational at the time. This builds credibility with experienced buyers.

**Slide 3: How We Got Here**
- Describe the architectural or operational choices that defined the market
- Use respectful framing: "This approach made sense when..."

**Slide 4: The Architecture of Today's Leaders**
- Table showing how incumbents are structured
- Demonstrates deep market understanding
- Columns: Approach | Why It Won | Core Assumption

---

#### Step 3: The Disruption / Catalyst (Slides 5 and 6)

**Purpose:** Explain exactly what changed to make the status quo no longer viable.

**Slide 5: What Changed**
- List 3 to 4 new characteristics of the market or threat landscape
- Be specific: regulation, technology shift, attacker capability, scale

**Slide 6: Why Legacy Fails Now**
- Punchline statement about how this stresses legacy systems
- Example: "MFA was designed for humans. Agents don't wait for push notifications."

---

#### Step 4: The Alternatives Evaluation (Slides 7 and 8)

**Purpose:** Survey other approaches buyers will consider. Group by approach, not vendor name.

**Slide 7: Right Then vs. Wrong Now**
- Pivot table mapping status quo strengths to their new fatal weaknesses
- Columns: What Made It Strong | Why It Fails Now

**Slide 8: The Alternatives Landscape**
- Evaluate: Do nothing | Incumbent vendor | Point solution | Build in-house
- For each: What it offers, why it falls short
- Acknowledge new contenders are incremental updates, not architectural resets

---

#### Step 5: The Perfect World (Slides 9 and 10)

**Purpose:** The "and therefore..." step. Describe what the ideal solution must look like.

**Slide 9: The New Purchase Criteria**
- Bulleted list of what any solution must do
- Frame as requirements, not features
- Example: "Must eliminate shareable secrets entirely"

**Slide 10: The Design Primitives**
- Speculative but concrete principles for the new architecture
- Example: "Cryptographic device binding, not knowledge factors"

---

### Part 2: The Follow-Through

**Now that the buyer agrees with the Perfect World criteria, introduce your solution.**

---

#### Step 6: The Introduction (Slide 11)

**Purpose:** Introduce your company and product in context.

**Slide 11: [Product Name]**
- One-sentence positioning statement
- Platform overview or marketecture diagram
- Where you fit in the ecosystem
- Keep text minimal

---

#### Step 7: Differentiated Value (Slides 12 to 14)

**Purpose:** Map your unique capabilities directly back to the Perfect World criteria.

**Slide 12: Capability 1**
- One capability per slide
- Show how it directly addresses a Perfect World criterion
- Include: feature name, what it does, why it matters (mapped to criterion)
- Visual: screenshot, diagram, or code snippet if relevant

**Slide 13: Capability 2**
- Same structure

**Slide 14: Capability 3**
- Same structure

**Rules:**
- Only include capabilities that are both unique AND directly mapped to Perfect World
- Do not list generic features
- Evidence over claims: show, do not tell

---

#### Step 8: Proof (Slide 15)

**Purpose:** Validate claims with evidence aligned to the prospect's situation.

**Slide 15: Proof Points**
- 2 to 3 customer results with specific outcomes
- Use only approved customers from `testimonials.md`
- Include: company name, what they achieved, relevant quote if available
- Align proof to the differentiated value claims, not generic success

---

#### Step 9: Objections (Slide 16, Optional)

**Purpose:** Proactively address common unspoken concerns.

**Slide 16: Common Questions**
- 2 to 3 objections with direct answers
- Examples: implementation time, integration complexity, pricing model, security review
- Handling objections head-on builds trust

---

#### Step 10: The Ask / Conclusion (Slide 17)

**Purpose:** Recap with urgency and secure commitment to next step.

**Slide 17: Next Steps**
- Progressive recap: the shift, the new criteria, how you meet them
- Clear call to action (the ask from Step 1)
- Optional: existential question that forces a decision
- Example: "Your auditors will ask how you secured AI agents. What will you tell them?"

---

## Design Principles

Apply these to every slide:

| Principle | Implementation |
|-----------|----------------|
| **Action titles** | Every slide title is a thesis, not a label. "A $40B market with no dominant player below enterprise" not "Market Opportunity." A reader who sees only the titles can reconstruct the full argument. Keep titles to two lines maximum. |
| **One slide, one message** | Each slide carries exactly one insight. If a slide has two conclusions, split it into two slides. Every element on the slide exists to serve the title. |
| **Minimalist text** | No paragraphs. Maximum 6 bullets per slide, 10 words per bullet. |
| **Punchline statements** | Anchor the bottom of most slides with a bold summary that drives the narrative forward. |
| **Typographic emphasis** | Bold key phrases within statements to make them scannable. |
| **Evidence via tables** | Use comparison tables for alternatives, architectures, before/after. |
| **Respectful framing** | Acknowledge why the status quo was rational before explaining why it fails. |
| **No product in Setup** | The product name appears only in Slide 11 and later. |

---

## Output Format

Generate the deck as a Markdown outline with this structure:

```markdown
# [Deck Title: The Provocative Insight]

## Metadata
- **Target audience:** [From Step 1]
- **The ask:** [From Step 1]
- **Alternatives addressed:** [From Step 1]

---

## Part 1: The Setup

### Slide 1: [Action title: the provocative thesis as a statement of fact]
**[Bold thesis statement]**

Speaker notes: [What to say when presenting this slide]

---

### Slide 2: [Action title: TLDR framed as the argument's conclusion]
- [Bullet 1]
- [Bullet 2]
- [Bullet 3]
- [Bullet 4]

Speaker notes: [What to say]

---

[Continue for all slides...]

---

## Part 2: The Follow-Through

### Slide 11: [Action title: product positioning as a thesis statement]
[Content]

Speaker notes: [What to say]

---

[Continue for all slides...]

---

## Review Checklist

[Auto-generated checklist - see below]
```

---

## Self-Review Checklist

After generating the deck, verify it passes these checks:

### Narrative Structure
- [ ] Product name does NOT appear in Slides 1 to 10
- [ ] Slide 2 TLDR summarizes the entire argument arc
- [ ] Status Quo (Slides 3 to 4) acknowledges why the old approach was rational
- [ ] Disruption (Slides 5 to 6) names specific catalysts, not vague "change"
- [ ] Perfect World (Slides 9 to 10) establishes clear criteria before product intro
- [ ] Differentiated Value (Slides 12 to 14) maps directly to Perfect World criteria
- [ ] Proof (Slide 15) uses only approved customers from testimonials.md
- [ ] MECE: no two slides make the same point, no logical step is skipped

### Design and Text
- [ ] Every slide title is an action title (thesis, not label). Readable as a standalone argument from titles alone
- [ ] No slide title exceeds two lines
- [ ] Each slide carries exactly one message. If two conclusions exist, split the slide
- [ ] No slide has more than 6 bullets
- [ ] No bullet exceeds 10 words
- [ ] Punchline statements present on key slides (2, 6, 10, 17)
- [ ] Tables used for comparisons (Slides 4, 7, 8)
- [ ] No dashes in slide text (rewrite if needed)
- [ ] No banned words (robust, seamless, leverage, cutting-edge, revolutionary)
- [ ] No passive voice
- [ ] No hedging ("we believe", "consider")

### Factual Accuracy
- [ ] All product capabilities match `product_brief.md` exactly
- [ ] All customer names from `testimonials.md` only
- [ ] No fabricated quotes or results
- [ ] Competitor framing aligns with `competitor_intel.md`

---

## PPTX Generation

After the Markdown outline is approved, generate a PPTX file.

**To generate PPTX, run this Python script:**

```python
# Save as generate_deck.py
# Requires: pip install python-pptx

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import re

def create_sales_deck(outline_path: str, output_path: str):
    """
    Generate a PPTX from a Markdown outline.

    Args:
        outline_path: Path to the Markdown outline file
        output_path: Path for the output PPTX file
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Define layouts
    blank_layout = prs.slide_layouts[6]  # Blank

    # Parse the Markdown outline
    with open(outline_path, 'r') as f:
        content = f.read()

    # Split into slides (### Slide N: Title)
    slide_pattern = r'### Slide \d+: (.+?)\n(.*?)(?=### Slide|\Z)'
    slides = re.findall(slide_pattern, content, re.DOTALL)

    for title, body in slides:
        slide = prs.slides.add_slide(blank_layout)

        # Add title
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.5), Inches(12.333), Inches(1)
        )
        title_frame = title_box.text_frame
        title_para = title_frame.paragraphs[0]
        title_para.text = title.strip()
        title_para.font.size = Pt(36)
        title_para.font.bold = True

        # Extract bullets (lines starting with -)
        bullets = re.findall(r'^- (.+)$', body, re.MULTILINE)

        if bullets:
            body_box = slide.shapes.add_textbox(
                Inches(0.5), Inches(1.75), Inches(12.333), Inches(5)
            )
            body_frame = body_box.text_frame
            body_frame.word_wrap = True

            for i, bullet in enumerate(bullets):
                if i == 0:
                    para = body_frame.paragraphs[0]
                else:
                    para = body_frame.add_paragraph()
                para.text = bullet.strip()
                para.font.size = Pt(24)
                para.level = 0

        # Extract bold statement (lines starting with **)
        punchline = re.search(r'\*\*(.+?)\*\*', body)
        if punchline and not bullets:
            body_box = slide.shapes.add_textbox(
                Inches(0.5), Inches(3), Inches(12.333), Inches(2)
            )
            body_frame = body_box.text_frame
            para = body_frame.paragraphs[0]
            para.text = punchline.group(1)
            para.font.size = Pt(32)
            para.font.bold = True
            para.alignment = PP_ALIGN.CENTER

    prs.save(output_path)
    print(f"Deck saved to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python generate_deck.py <outline.md> <output.pptx>")
        sys.exit(1)
    create_sales_deck(sys.argv[1], sys.argv[2])
```

**Usage:**
```bash
pip install python-pptx
python generate_deck.py output/decks/outline.md output/decks/sales-deck.pptx
```

---

## Adaptation Notes

**When docs are incomplete:**
- If `product_brief.md` is empty, ask user for product name, 3 capabilities, and limitations
- If `messaging_positioning.md` is empty, ask user for the provocative insight and 3 pain points
- If `competitor_intel.md` is empty, ask user to describe 2 to 3 alternatives buyers consider
- If `testimonials.md` is empty, use generic framing ("[Industry] teams") or ask for customer names

**When the provocative insight is unclear:**
- Help the user derive it: "What do you believe about this market that most people get wrong?"
- Or: "If you could change one assumption buyers have, what would it be?"

**When the deck needs to be shorter:**
- Minimum viable deck: Slides 1, 2, 6, 9, 11, 12, 15, 17 (8 slides)
- Combine Status Quo into one slide
- Combine Alternatives into one slide
- Keep only the strongest capability

**When the deck needs more depth:**
- Add slides between 12 to 14 for additional capabilities (maximum 5 total)
- Add a demo walkthrough slide after Slide 14
- Add competitive comparison table as Slide 8b
- Add implementation timeline as Slide 16b

---

## File Output

Save the Markdown outline to: `output/decks/[product-name]-sales-deck.md`
Save the PPTX to: `output/decks/[product-name]-sales-deck.pptx`

Create the `output/decks/` directory if it does not exist.
