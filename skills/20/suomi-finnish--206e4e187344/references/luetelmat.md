# Luetelmat

Luetelma on allekkain kirjoitettu luettelo, jonka osat erotetaan luetelmamerkillä. Tämä on kielimallien yleisimpiä virhealueita, koska englannin ja suomen käytännöt eroavat toisistaan.

Lähde: Kielitoimiston ohjepankki, ohje [Luetelma](https://kielitoimistonohjepankki.fi/ohje/luetelma/).

---

## 1. Perusperiaate: samanmuotoisuus

Luetelman osien on oltava keskenään samanmuotoisia. Älä sekoita samassa luetelmassa yksittäisiä sanoja, lauseenkatkelmia ja täysiä virkkeitä.

VÄÄRIN:

```
Palvelu sisältää:
- Neuvonta
- autamme sopimuksen laadinnassa
- Asiakirjojen tarkistus tehdään kahden työpäivän kuluessa.
```

OIKEIN:

```
Palvelu sisältää:
- neuvonnan
- avun sopimuksen laadinnassa
- asiakirjojen tarkistuksen
```

---

## 2. Alkukirjain ja loppupiste

Ratkaisevaa on, ovatko luetelman osat täysiä virkkeitä vai johdantolauseen jatkoja.

### 2.1 Osat ovat täysiä virkkeitä

Iso alkukirjain, piste loppuun:

```
Käsittelyssä otetaan huomioon seuraavat seikat:

- Hakemus on jätettävä määräajassa.
- Liitteet tarkistetaan ennen käsittelyä.
- Päätöksestä voi valittaa 30 päivän kuluessa.
```

### 2.2 Osat ovat johdantolauseen jatkoja tai katkelmia

Pieni alkukirjain, ei välimerkkejä osien välissä. Viimeisen osan jälkeen voi laittaa pisteen, mutta se ei ole pakollinen:

```
Maali

- sopii käsittelemättömälle puulle
- kuivuu kahdessa tunnissa
- riittää noin 10 neliömetrille.
```

---

## 3. Osien välissä EI käytetä välimerkkejä

Luetelmamerkki toimii jo erottimena, joten osien väliin ei tule pilkkua eikä puolipistettä — ei silloinkaan, kun sama teksti juoksevassa muodossa vaatisi ne.

VÄÄRIN:

```
- neuvonnan,
- avun sopimuksen laadinnassa,
- asiakirjojen tarkistuksen.
```

Samoin viimeisen osan eteen EI kirjoiteta rinnastuskonjunktiota **ja**, **tai** tai **vai**. Tämä on suora englannin mallista periytyvä virhe:

VÄÄRIN:

```
- neuvonnan
- avun sopimuksen laadinnassa
- ja asiakirjojen tarkistuksen
```

---

## 4. Johdantolause ja kaksoispiste

**Kaksoispiste tulee**, kun johdantolause on rakenteeltaan kokonainen virke tai muuten itsenäinen:

```
Hakemukseen liitetään seuraavat asiakirjat:

- ote kaupparekisteristä
- tilinpäätös
```

**Kaksoispistettä ei tule**, kun johdanto on katkelmallinen ja luetelman osat täydentävät sen lauseeksi, tai kun johdanto on selvästi otsikko:

```
Maali

- sopii käsittelemättömälle puulle
- kuivuu kahdessa tunnissa
```

---

## 5. Luetelmamerkit

Käytettäviä merkkejä ovat ajatusviiva (–), pallukka (•), numero ja graafinen merkki. Merkin ja tekstin väliin tulee välilyönti.

Huomaa, että suomalaisessa typografiassa luetelmaviiva on **ajatusviiva** (–, U+2013), ei yhdysmerkki (-). Markdownissa ja koodissa yhdysmerkki on tietysti oikea merkintätapa, mutta julkaistavassa leipätekstissä ajatusviiva.

Numeroidussa luetelmassa numeron jälkeen tulee piste tai sulkumerkki:

```
1. ensimmäinen vaihe
2. toinen vaihe
```

---

## 6. Tekoälylle tyypilliset luetelmavirheet

Tarkista nämä aina, kun tuotat suomenkielisen luetelman:

| Virhe | Korjaus |
|---|---|
| Iso alkukirjain lauseenkatkelmissa | Pieni alkukirjain, jos osa jatkaa johdantolausetta |
| Piste jokaisen katkelman perässä | Ei pisteitä, korkeintaan viimeisen perässä |
| Pilkku tai puolipiste osien välissä | Ei välimerkkiä |
| **ja** viimeisen osan edessä | Poista |
| Osat eri muodoissa | Yhtenäistä sijamuoto ja rakenne |
| Yhdysmerkki luetelmamerkkinä leipätekstissä | Ajatusviiva – |
