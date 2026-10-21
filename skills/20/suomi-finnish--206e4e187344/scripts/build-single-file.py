#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kokoaa SKILL.md:n ja references/-tiedostot yhdeksi tiedostoksi.

Tuottaa tiedoston suomi-finnish-full.md, joka toimii alustoilla, jotka
odottavat skillin olevan yksi tiedosto. Aja repon juuresta:

    python3 scripts/build-single-file.py
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "suomi-finnish-full.md")

# Järjestys on sama kuin SKILL.md:n reititystaulukossa.
REFS = [
    ("A", "luetelmat.md",    "Luetelmat"),
    ("B", "lauserakenne.md", "Lauserakenne"),
    ("C", "taivutus.md",     "Taivutus ja rektiot"),
    ("D", "valimerkit.md",   "Välimerkit"),
    ("E", "merkinnat.md",    "Sovinnaiset merkinnät"),
    ("F", "sanojen-asu.md",  "Sanojen asu ja sananvalinta"),
]

def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

def demote(text):
    """Siirtää otsikkotasot yhden alaspäin, jotta liite asettuu ## -tason alle."""
    out = []
    fenced = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        if not fenced and re.match(r"^#{1,5} ", line):
            line = "#" + line
        out.append(line)
    return "\n".join(out)

skill = read(os.path.join(ROOT, "SKILL.md"))

# Reititystaulukko osoittaa tässä versiossa liitteisiin, ei erillisiin tiedostoihin.
skill = skill.replace(
    "Kun työ koskee alla olevaa aihetta, **lue myös vastaava tiedosto "
    "`references/`-kansiosta, jos se on saatavilla**, ennen kuin tuotat tai korjaat tekstin.",
    "Tämä on koontiversio: tarkemmat ohjeet ovat mukana samassa tiedostossa "
    "liitteinä A–F. Kun työ koskee alla olevaa aihetta, lue myös vastaava liite.")

for letter, fname, title in REFS:
    skill = skill.replace("`references/%s`" % fname, "Liite %s: %s" % (letter, title))

skill = skill.replace(
    "**Nämä tiedostot ovat valinnaisia.** Jos `references/`-kansiota ei löydy — "
    "esimerkiksi kun skill on asennettu yhtenä tiedostona — älä pidä sitä virheenä "
    "äläkä keskeytä työtä. Tämän tiedoston säännöt toimivat itsenäisesti, joten "
    "jatka niiden varassa.",
    "Kaikki liitteet ovat tässä tiedostossa, joten erillisiä tiedostoja ei tarvita.")

skill = skill.replace(
    "Tämän skillin omat tarkemmat ohjeet ovat `references/`-kansiossa: luetelmat, "
    "lauserakenne, taivutus ja rektiot, välimerkit, sovinnaiset merkinnät sekä "
    "sanojen asu ja sananvalinta.",
    "Tämän skillin tarkemmat ohjeet ovat tämän tiedoston liitteissä A–F.")

parts = [skill.rstrip(), ""]
for letter, fname, title in REFS:
    body = read(os.path.join(ROOT, "references", fname))
    body = re.sub(r"^# .*\n", "", body, count=1)   # poista liitteen oma H1
    parts.append("---\n")
    parts.append("## LIITE %s: %s\n" % (letter, title))
    parts.append(demote(body).strip())
    parts.append("")

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(parts).rstrip() + "\n")

print("Kirjoitettu %s (%d tavua)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT)))
