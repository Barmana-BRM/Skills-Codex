---
name: app-namer
description: Generate creative, memorable, and appropriate names for software applications, products, and services. Use when users need to name their app, software, product, or service. Considers functionality, target audience, brand positioning, cultural factors, and language requirements. Supports naming in any language specified by the user.
---

# App Namer

## Overview

Generate memorable, appropriate, and marketable names for software applications. This skill provides structured naming suggestions that consider functionality, target audience, brand positioning, and cultural factors.

## Naming Workflow

Follow this workflow when generating application names:

### 1. Gather Information

Collect key information from the user's request:

- **Functionality**: What does the software do? Core features?
- **Target Audience**: Who will use it? Age group, profession, technical level?
- **Positioning**: Market position, competitors, unique value proposition
- **Language**: Which language(s) for the name? (Default: user's conversation language)
- **Brand Tone**: Professional, playful, technical, friendly, innovative, trustworthy?
- **Constraints**: Any specific requirements? Length, keywords to include/avoid?
- **Quantity**: How many suggestions? (Default: 10)

If critical information is missing, ask the user before proceeding.

### 2. Generate Candidate Names

Create diverse candidates across different naming types:

**Naming Types:**

1. **Descriptive** (功能描述型)
   - Clearly describes what the app does
   - Example: TaskMaster, CodeReview, HealthTracker
   - Best for: Professional tools, B2B software

2. **Metaphorical** (隐喻型)
   - Uses metaphor or imagery to convey meaning
   - Example: Compass (navigation app), Nest (home app), Phoenix (recovery tool)
   - Best for: Consumer apps, lifestyle products

3. **Invented/Coined** (创造型)
   - New words that are catchy and unique
   - Example: Spotify, Pinterest, Snapchat
   - Best for: Consumer brands wanting strong identity

4. **Compound** (组合型)
   - Combines two words or concepts
   - Example: Facebook, WhatsApp, LinkedIn, 知乎, 钉钉
   - Best for: Tech products, social platforms

5. **Abbreviated** (缩写型)
   - Acronyms or shortened forms
   - Example: npm, AWS, JIRA
   - Best for: Technical tools, enterprise software

6. **Personal/Name-based** (人名型)
   - Based on founders or characters
   - Example: Adobe, Mercedes, 小红书
   - Best for: Premium brands, storytelling brands

7. **Action-oriented** (动作型)
   - Verb-based or action-focused
   - Example: Slack, Zoom, Run, 飞书
   - Best for: Productivity tools, active engagement apps

Generate a diverse mix unless user specifies preferred types.

### 3. Evaluate Each Name

For each candidate, assess:

- **Memorability**: Easy to remember?
- **Pronounceability**: Easy to say in target language(s)?
- **Meaning**: Clear connection to purpose? Positive associations?
- **Uniqueness**: Stands out from competitors?
- **Domain Availability**: Likely available as .com/.cn/.app domain?
- **Trademark**: Low risk of conflicts? (general assessment, not legal advice)
- **Cultural Sensitivity**: Appropriate across cultures? No negative meanings?
- **Scalability**: Works if product expands beyond initial scope?

### 4. Format Output

Present names in this structure:

```
## [Language] 软件命名建议

### 1. [Name] ([Naming Type])
**含义**: [What it means/represents]
**优势**: [2-3 key strengths]
**域名建议**: [suggested domains like name.com, name.app]
**适用场景**: [Why it fits this particular software]

### 2. [Name] ([Naming Type])
...
```

## Evaluation Criteria

Prioritize these qualities (adjust based on user needs):

1. **Clarity**: Name clearly relates to software purpose
2. **Simplicity**: Easy to spell, remember, and share
3. **Uniqueness**: Distinctive in the market
4. **Positive Associations**: Evokes appropriate emotions/imagery
5. **Versatility**: Works across platforms (app stores, domains, social media)
6. **Longevity**: Won't feel dated quickly

## Language-Specific Considerations

### Chinese Names (中文命名)
- Consider tones and pronunciation flow
- Check for unintended homophone meanings
- Balance modern feel with cultural resonance
- Consider both simplified and traditional characters
- Think about English transliteration (pinyin) for international use

### English Names
- Check phonetic clarity across accents
- Avoid words that are hard to spell phonetically
- Consider global English speakers (avoid idioms/slang)
- Check for negative meanings in other languages

### Other Languages
- Verify pronunciation by native speakers
- Check cultural appropriateness
- Consider script/alphabet compatibility with tech platforms
- Evaluate translation/transcription to English if needed

## Special Considerations

### Domain & Trademark
- Note if common domains (.com/.cn/.app) are likely available
- Mention if name is generic (harder to trademark)
- Warn about potential conflicts with known brands
- Suggest alternatives if preferred domains unavailable

### User Requirements Override Defaults
If user specifies requirements that conflict with defaults:
- **Follow user requirements**
- Acknowledge the deviation: "Note: Generating [X] names as requested, instead of default 10"
- Adjust evaluation criteria to match user priorities

## Output Guidelines

**Default Output:**
- 10 diverse candidates covering multiple naming types
- Each with explanation, advantages, and domain suggestions
- Ranked by overall fit and quality

**Custom Output:**
- If user specifies quantity: provide that exact number
- If user specifies preferred types: focus on those types
- If user specifies other constraints: prioritize accordingly

**Always:**
- Explain reasoning behind each suggestion
- Be honest about trade-offs (e.g., "highly unique but may need explanation")
- Provide actionable next steps (e.g., "check domain availability at...")
