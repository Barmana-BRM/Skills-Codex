# Välimerkit

Täydentää `SKILL.md`:n lukuja 2 (pilkutus), 6 (viivat) ja 8 (lainausmerkit). Tässä käsitellään ne välimerkit, joita ydinohje ei kata.

Lähteet: Kielitoimiston ohjepankki, ohjeet [Puolipiste](https://kielitoimistonohjepankki.fi/ohje/puolipiste/), [Kaksoispiste](https://kielitoimistonohjepankki.fi/ohje/kaksoispiste/) ja [Ajatusviiva poiston merkkinä](https://kielitoimistonohjepankki.fi/ohje/ajatusviiva-poiston-merkkina/).

---

## 1. Puolipiste ;

Puolipistettä käytetään kahden virkkeen veroisen ilmauksen välissä, kun piste tuntuu liian vahvalta ja pilkku liian heikolta erottimelta. Se osoittaa, että virkkeet liittyvät toisiinsa sisällöllisesti tiiviimmin kuin ympäröivät virkkeet.

> Piste tekee virkkeestä itsenäisen; puolipiste sitoo sen toiseen virkkeeseen.

Toinen käyttö on luettelo, jonka osat sisältävät itse pilkkuja:

> Kokoukseen osallistuivat Virtanen, puheenjohtaja; Koskinen, sihteeri; ja Laine, varajäsen.

**Käytä säästeliäästi.** Puolipiste on suomessa selvästi harvinaisempi kuin englannissa, ja kielimalli yliannostelee sitä englannin mallin mukaan. Käytä sitä vain, kun se todella selventää kokonaisuuksien rajoja; muuten piste tai pilkku.

---

## 2. Kaksoispiste :

Kaksoispiste osoittaa, että sitä seuraava osa täydentää, täsmentää tai perustelee edellä sanottua.

Käyttötilanteet:

- täydentävä tai perusteleva jakso: "Paikalle tulijoita yhdisti yksi asia: kiinnostus elokuviin."
- luettelon edellä, kun edeltävä jakso on kokonainen lause
- suoran lainauksen edellä: "Opettaja kysyi: ”Minne olet menossa?”"
- mittakaavoissa ja lähdeviitteissä: "Kartan mittakaava on 1:20 000"

### Alkukirjain kaksoispisteen jälkeen

- **Pieni alkukirjain**, kun kaksoispisteen jälkeen tulee yksi sana tai yksi lause
- **Iso alkukirjain**, kun jäljessä on kaksi tai useampia virkkeitä

Tämä eroaa englannin käytännöstä, ja kielimalli kirjoittaa usein ison alkukirjaimen yhdenkin lauseen eteen.

---

## 3. Sulkeet ( )

Välilyönti tulee sulkeiden ulkopuolelle, ei sisäpuolelle:

```
OIKEIN:  teksti (lisäys) jatkuu
VÄÄRIN:  teksti ( lisäys ) jatkuu
```

Jos sulkeissa on kokonainen virke, piste tulee sulkeiden sisään. Jos sulkeet ovat virkkeen lopussa osana sitä, piste tulee sulkeiden jälkeen:

```
Asia käsiteltiin kokouksessa (pöytäkirja liitteenä).
Asia käsiteltiin kokouksessa. (Pöytäkirja on liitteenä.)
```

Hakasulkeita [ ] käytetään sulkeiden sisäisissä sulkeissa ja lainaukseen tehdyissä lisäyksissä tai poistoissa.

---

## 4. Kolme pistettä … ja poisjätön merkintä

Tässä on suomalainen erikoisuus, jonka kielimalli lähes aina tekee väärin.

**Kolme pistettä** merkitsee kesken jätettyä ilmausta:

> En oikein tiedä, pitäisikö…

**Poisjättö lainauksesta** merkitään sen sijaan **kahdella ajatusviivalla**, ei kolmella pisteellä:

> – – oikeus ylläpitää ja kehittää omaa kieltään ja kulttuuriaan.

Ajatusviivat voi merkitä hakasulkeisiin, etenkin jos poistettu on kokonainen virke tai useampia. Hakasulkeet eivät ole pakolliset:

> [– –] oikeus ylläpitää ja kehittää omaa kieltään ja kulttuuriaan.

Siis: `...` on kesken jättämisen merkki, `– –` on poiston merkki. Englannin `[...]` ei ole suomen käytäntö.

---

## 5. Sitova välilyönti

Sitova välilyönti (engl. non-breaking space, U+00A0) estää rivinvaihdon kohdassa, jossa se hajottaisi kokonaisuuden. Tämä on olennaista erityisesti verkkosisällössä, jossa rivitys vaihtelee näytön leveyden mukaan.

Käytä sitovaa välilyöntiä näissä:

| Kohta | Esimerkki |
|---|---|
| Luku ja mittayksikkö | 5 kg, 100 km, 3,5 m |
| Luku ja prosenttimerkki | 15 % |
| Luku ja valuutta | 100 € |
| Kellonajan tunnus | klo 14.30 |
| Etunimen kirjainlyhenne ja sukunimi | J. K. Korpela |
| Lyhenne ja siihen liittyvä luku | nro 5, s. 12 |
| Tuhaterottimena toimiva välilyönti | 1 000 000 |

HTML:ssä merkintä on `&nbsp;` tai suoraan merkki U+00A0. Markdownissa ja pelkässä tekstissä sitovaa välilyöntiä ei yleensä käytetä, koska rivitys tehdään vasta julkaisuvaiheessa.

---

## 6. Viivat: yhdysmerkki, ajatusviiva ja miinusmerkki

Kolme eri merkkiä, joita ei saa sekoittaa:

| Merkki | Nimi | Koodi | Käyttö |
|---|---|---|---|
| - | yhdysmerkki | U+002D | yhdyssanat, tavutus: EU-maa, A-rappu |
| – | ajatusviiva | U+2013 | välit ja tauot: sivut 10–15, klo 8–16 |
| − | miinusmerkki | U+2212 | matematiikka: −5 °C |

Kielimalli käyttää tyypillisesti yhdysmerkkiä kaikkiin kolmeen tehtävään ja tuottaa lisäksi englannin pitkän ajatusviivan — (em dash, U+2014), jota suomessa ei käytetä.

### Ajatusviivan välilyönnit

- Väliä ilmaisevassa käytössä **ei** välilyöntejä: `sivut 10–15`, `vuosina 2020–2025`
- Lauseen sisäisenä taukona **välilyönnit molemmin puolin**: `Asiaa pohdittiin – eikä vähiten siksi, että –`
