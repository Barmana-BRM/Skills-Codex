# Finnish language skill for Claude, Codex and any other AI that supports skills

**Teach AI to write correct Finnish.** This skill provides comprehensive Finnish language rules — spelling, grammar, punctuation, compound words, and style — so AI produces natural, publication-ready Finnish instead of the awkward, anglicism-filled output LLMs typically generate.

Works with Claude Code, Codex, and any other AI agent platform that supports skills.

Built on the official [Kielitoimiston ohjepankki](https://kielitoimistonohjepankki.fi/) (Institute for the Languages of Finland).

---

## Why this exists

LLMs make predictable mistakes when writing Finnish:

- **Compound words split apart**: "verkko sivusto" instead of *verkkosivu*, "asiakas palvelu" instead of *asiakaspalvelu*
- **Anglicisms everywhere**: "sukella syvemmalle", "implementoida", "adressoida"
- **Wrong punctuation**: English-style decimals (3.14 instead of 3,14), Oxford commas, missing commas before subordinate clauses
- **Overly pompous tone**: American corporate rhetoric translated literally into Finnish
- **Capitalization errors**: weekdays, months, and nationalities capitalized (English rules applied to Finnish)
- **Broken inflection**: Finnish has 15 grammatical cases and complex word inflection — LLMs frequently produce wrong case endings, garbled possessive suffixes, and incorrect verb conjugations
- **Mangled ä and ö**: LLMs drop or swap Finnish diacritics, writing "a" instead of "ä" and "o" instead of "ö", which changes word meanings entirely and leads to incorrect translations

This skill catches and prevents all of these. It's been used in production to generate hundreds of pages of Finnish web content.

## Installation

### Option 1: Add to a project (recommended)

Copy the whole skill — `SKILL.md` and the `references/` folder — into your project's skills directory:

```bash
mkdir -p .claude/skills/suomi-finnish
cp -R SKILL.md references .claude/skills/suomi-finnish/
```

`SKILL.md` also works on its own as a single file. You then lose the reference files, which cover lists, sentence structure, inflection and rections, punctuation, conventional notation, and word choice in more detail.

The skill will automatically activate when Claude Code detects Finnish language work.

### Option 2: Add globally (all projects)

```bash
mkdir -p ~/.claude/skills/suomi-finnish
cp -R SKILL.md references ~/.claude/skills/suomi-finnish/
```

### Option 3: One-liner install from GitHub

```bash
git clone --depth 1 https://github.com/akunikkola/suomi-finnish-skill.git /tmp/sfs && mkdir -p .claude/skills/suomi-finnish && cp -R /tmp/sfs/SKILL.md /tmp/sfs/references .claude/skills/suomi-finnish/ && rm -rf /tmp/sfs
```

Replace `.claude` with `~/.claude` to install globally.

### Option 4: Install with AI

Give Claude, Codex, or any other skill-supporting AI the repo URL and ask it to install the skill:

```
Install this skill: https://github.com/akunikkola/suomi-finnish-skill
```

### Option 5: Download the ready-made package

A zip containing the whole skill — `SKILL.md` and the `references/` folder:

[Download suomi-finnish.zip (Google Drive)](https://drive.google.com/file/d/1GQAGPkyoHvPzzFL0NHT7kmbcz6IrsMLc/view?usp=sharing)

On claude.ai: Settings → Skills → **+ Create skill**, then upload the zip. In Claude Code, unpack it into `.claude/skills/`.

To rebuild the package from source:

```bash
./scripts/build-skill-package.sh
```

### Option 6: Single file with everything included

`suomi-finnish-full.md` is a generated bundle containing `SKILL.md` and all six reference files in one document. Use it on platforms that expect a skill to be a single file:

```bash
curl -sL https://raw.githubusercontent.com/akunikkola/suomi-finnish-skill/main/suomi-finnish-full.md -o suomi-finnish-full.md
```

Regenerate it after editing any source file:

```bash
python3 scripts/build-single-file.py
```

## Upgrading from an earlier install

The skill used to be distributed as a single `SKILL.md` copied to `.claude/skills/suomi-finnish.md`. It is now a directory, because the reference files live beside `SKILL.md`.

Worth knowing: **Claude Code loads a skill from a directory containing a `SKILL.md`.** A bare `.md` file sitting directly in `.claude/skills/` is not picked up as a skill. If you installed with the old instructions, that file was most likely never loading as a skill at all.

To move to the current layout:

```bash
# Remove the old flat file, if you have one
rm -f .claude/skills/suomi-finnish.md ~/.claude/skills/suomi-finnish.md

# Install the current version
git clone --depth 1 https://github.com/akunikkola/suomi-finnish-skill.git /tmp/sfs && mkdir -p .claude/skills/suomi-finnish && cp -R /tmp/sfs/SKILL.md /tmp/sfs/references .claude/skills/suomi-finnish/ && rm -rf /tmp/sfs
```

Check that it worked:

```bash
ls .claude/skills/suomi-finnish/
# SKILL.md  references/
```

Older copies of `SKILL.md` keep working as before — nothing was removed from it, only corrected and added to. If you pull a newer `SKILL.md` without the `references/` folder, the skill notes that the reference files are optional and continues on its own rules.

## What it covers

| Area | Examples |
|---|---|
| Compound words | When to join vs. separate, hyphenation rules |
| Punctuation | Comma rules, decimal comma, no Oxford comma |
| Capitalization | Lowercase weekdays, months, nationalities |
| Numbers & units | Space as thousands separator, unit spacing (5 kg, 15 %) |
| Abbreviations | Dot rules, inflection with colons (EU:n) |
| Dashes | Hyphen (-) vs. en dash (--) usage |
| Sentence structure | Case agreement, postpositions, possessive suffixes |
| AI-specific errors | Anglicisms, overly formal tone, filler text |
| Proofreading | Step-by-step review checklist |

Plus detailed reference files loaded on demand:

| File | Covers |
|---|---|
| `references/luetelmat.md` | List punctuation, capitalization, parallel form |
| `references/lauserakenne.md` | Locative attributes, dangling essives, joka vs. mikä, nominalization |
| `references/taivutus.md` | Foreign name inflection, rections, abbreviation inflection |
| `references/valimerkit.md` | Semicolon, colon, brackets, omission marks, non-breaking space |
| `references/merkinnat.md` | Dates, times, units, contact details, alphabetical order |
| `references/sanojen-asu.md` | Loanword spelling, anglicisms, parallel accepted forms |

## Usage

Once installed, the skill activates automatically when you:

- Write or generate Finnish text
- Proofread or review Finnish content
- Translate content into Finnish
- Create content for Finnish websites or services

You can also invoke it manually:

```
/suomi-finnish
```

## Sources

All rules are based on:

- [Kielitoimiston ohjepankki](https://kielitoimistonohjepankki.fi/) (Institute for the Languages of Finland)
- [Kielitoimiston sanakirja](https://www.kielitoimistonsanakirja.fi/) (Dictionary of Contemporary Finnish)
- [Iso suomen kielioppi](https://kaino.kotus.fi/visk/etusivu.php) (Comprehensive Finnish Grammar)

## Contributing

Found a rule that's missing or incorrect? Open an issue or PR. Finnish language nerds welcome.

## License

MIT

---

# Suomen kielen skills-tiedosto Claudelle, Codexille tai mille tahansa muulle skills-ominaisuutta tukevalle työkalulle

**Opeta tekoäly kirjoittamaan oikeaa suomea.** Tämä skill antaa tekoälylle kattavat suomen kielen säännöt — oikeinkirjoituksen, kieliopin, pilkutuksen, yhdyssanat ja tyylin — jotta se tuottaa luonnollista, julkaisukelpoista suomea anglismien täyttämän konekielen sijaan.

Toimii Claude Coden, Codexin ja minkä tahansa muun skillejä tukevan tekoälyagentin kanssa.

Perustuu [Kielitoimiston ohjepankin](https://kielitoimistonohjepankki.fi/) virallisiin ohjeisiin.

## Asennus

### Vaihtoehto 1: Projektitasoinen asennus (suositeltu)

Kopioi koko skill eli `SKILL.md` ja `references/`-kansio:

```bash
mkdir -p .claude/skills/suomi-finnish
cp -R SKILL.md references .claude/skills/suomi-finnish/
```

Pelkkä `SKILL.md` toimii myös yksinään, mutta silloin tarkemmat ohjeet jäävät pois.

### Vaihtoehto 2: Globaali asennus (kaikki projektit)

```bash
mkdir -p ~/.claude/skills/suomi-finnish
cp -R SKILL.md references ~/.claude/skills/suomi-finnish/
```

### Vaihtoehto 3: Suora asennus GitHubista

```bash
git clone --depth 1 https://github.com/akunikkola/suomi-finnish-skill.git /tmp/sfs && mkdir -p .claude/skills/suomi-finnish && cp -R /tmp/sfs/SKILL.md /tmp/sfs/references .claude/skills/suomi-finnish/ && rm -rf /tmp/sfs
```

Globaaliin asennukseen korvaa `.claude` polulla `~/.claude`.

### Vaihtoehto 4: Asenna tekoälyllä

Anna Claudelle, Codexille tai muulle skillejä tukevalle tekoälylle repon osoite ja pyydä asentamaan skill:

```
Asenna tämä skill: https://github.com/akunikkola/suomi-finnish-skill
```

### Vaihtoehto 5: Lataa valmis paketti

Zip-tiedosto, joka sisältää koko skillin eli `SKILL.md`:n ja `references/`-kansion:

[Lataa suomi-finnish.zip (Google Drive)](https://drive.google.com/file/d/1GQAGPkyoHvPzzFL0NHT7kmbcz6IrsMLc/view?usp=sharing)

claude.ai:ssa: Asetukset → Skills → **+ Create skill**, ja lataa zip. Claude Codessa pura se `.claude/skills/`-kansioon.

Paketin rakentaminen lähdekoodista:

```bash
./scripts/build-skill-package.sh
```

### Vaihtoehto 6: Yksi tiedosto, joka sisältää kaiken

`suomi-finnish-full.md` on koontiversio, jossa `SKILL.md` ja kaikki kuusi referenssitiedostoa ovat samassa dokumentissa. Käytä sitä alustoilla, jotka odottavat skillin olevan yksi tiedosto:

```bash
curl -sL https://raw.githubusercontent.com/akunikkola/suomi-finnish-skill/main/suomi-finnish-full.md -o suomi-finnish-full.md
```

Koontiversio luodaan uudelleen lähdetiedostojen muutosten jälkeen:

```bash
python3 scripts/build-single-file.py
```

## Päivitys vanhasta asennuksesta

Skill jaettiin aiemmin yhtenä `SKILL.md`-tiedostona, joka kopioitiin nimelle `.claude/skills/suomi-finnish.md`. Nyt se on hakemisto, koska referenssitiedostot sijaitsevat `SKILL.md`:n rinnalla.

Huomionarvoista: **Claude Code lataa skillin hakemistosta, jossa on `SKILL.md`.** Pelkkä `.md`-tiedosto suoraan `.claude/skills/`-kansiossa ei lataudu skillinä. Jos asensit vanhan ohjeen mukaan, tiedosto ei todennäköisesti ole latautunut skillinä lainkaan.

Siirtyminen nykyiseen rakenteeseen:

```bash
# Poista vanha litteä tiedosto, jos sellainen on
rm -f .claude/skills/suomi-finnish.md ~/.claude/skills/suomi-finnish.md

# Asenna nykyinen versio
git clone --depth 1 https://github.com/akunikkola/suomi-finnish-skill.git /tmp/sfs && mkdir -p .claude/skills/suomi-finnish && cp -R /tmp/sfs/SKILL.md /tmp/sfs/references .claude/skills/suomi-finnish/ && rm -rf /tmp/sfs
```

Tarkistus:

```bash
ls .claude/skills/suomi-finnish/
# SKILL.md  references/
```

Vanhat `SKILL.md`-kopiot toimivat edelleen kuten ennenkin: tiedostosta ei ole poistettu mitään, vaan sitä on korjattu ja täydennetty. Jos haet uuden `SKILL.md`:n ilman `references/`-kansiota, skill toteaa referenssitiedostot valinnaisiksi ja jatkaa omien sääntöjensä varassa.

## Mitä skill kattaa

- Yhdyssanasäännöt (yleisin virhetyyppi)
- Pilkutus (sivulauseet, päälauseet, luettelot)
- Iso ja pieni alkukirjain
- Numerot, lyhenteet ja mittayksiköt
- Ajatusviiva vs. yhdysviiva
- Lauserakenne ja kielioppi
- Tekoälylle tyypilliset virheet (anglismit, mahtipontisuus, täytesanat)
- Vaiheittainen oikolukuprosessi

Lisäksi `references/`-kansiossa tarkemmat ohjeet, jotka ladataan tarvittaessa:

- `luetelmat.md` — luetelmien välimerkit, alkukirjaimet ja samanmuotoisuus
- `lauserakenne.md` — paikallissija-attribuutit, kelluva essiivi, joka/mikä, substantiivitauti
- `taivutus.md` — vieraskielisten nimien taivutus, rektiot, lyhenteiden taivutus
- `valimerkit.md` — puolipiste, kaksoispiste, sulkeet, poisjätön merkintä, sitova välilyönti
- `merkinnat.md` — päivämäärät, kellonajat, suureet, yhteystiedot, aakkostus
- `sanojen-asu.md` — vierassanojen asu, anglismit, rinnakkain hyväksytyt muodot

## Lisenssi

MIT
