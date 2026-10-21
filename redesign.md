# AI Redesign Guide
## The Curse of Insecure Packets

Dette dokument beskriver den ønskede designretning for videreudviklingen af spillet.

Formålet er IKKE at ændre spillets faglige fundament inden for OT, ICS, IEC 62443, Purdue-modellen, NIS2 og digital forensics.

Formålet er at gøre spillet til et stærkere SPIL uden at miste den faglige værdi.

---

# Overordnet vision

"The Curse of Insecure Packets" skal udvikles fra at være en simulering med quiz-elementer til at blive et narrativt, undersøgende cybersecurity-eventyr.

Spilleren skal opleve:

1. Nysgerrighed
2. Mystik
3. Efterforskning
4. Beslutningstagning
5. Konsekvenser

før spilleren oplever:

1. Faglig teori
2. Compliance
3. Standarder
4. Korrekte svar

Målet er:

> Spilleren skal ønske at løse mysteriet.
>
> Læringen er belønningen for at gøre det.

---

# Kernedesignprincip

## Fra undervisning til oplevelse

Undgå:

"Her er problemet. Vælg den korrekte løsning."

Foretræk:

"Noget virker forkert. Find årsagen."

---

# Story First

## Nuværende udfordring

Spillet indeholder stærk OT-faglighed.

Det mangler en tydelig central fortælling.

---

## Ny retning

Spillet skal opbygges omkring et overordnet mysterium.

Eksempel:

En række mærkelige hændelser opstår på vandværket.

- Pumper ændrer adfærd
- PLC'er går i STOP
- Netværkstrafik ser forkert ud
- En ukendt Raspberry Pi dukker op
- Dokumentation mangler
- Audit nærmer sig

Spilleren ved ikke:

- Om det er et cyberangreb
- En fejlkonfiguration
- En tidligere medarbejder
- En ekstern leverandør
- Insidertrussel

Sandheden afsløres gradvist.

---

# Show Don't Tell

## Regel

Vis konsekvenser før forklaringer.

Undgå:

"Trykket er steget til 14.8 bar."

Foretræk:

- Blinkende alarmer
- Visuelle målere
- Bekymrede NPC'er
- Ustabile systemer
- Ændret miljø

Forklar først bagefter.

---

# Mere levende karakterer

Karakterer skal være mere end informationskilder.

---

## Hans

Udvikles til mentorfigur.

Hans:

- Husker tidligere valg
- Kommenterer spillerens handlinger
- Reagerer følelsesmæssigt på fejl
- Deler historier fra virkelige anlæg

Spilleren skal opbygge tillid til Hans.

---

## Kirsten

Udvikles til en reel antagonistisk kraft.

Ikke ond.

Men krævende.

Spørgsmål:

- Er dokumentationen på plads?
- Hvorfor blev den beslutning taget?
- Hvor er beviserne?

Spilleren skal føle audit-presset.

---

# Mysterie- og spor-system

Indfør et egentlig investigationsystem.

Hver hændelse bør generere spor.

Eksempel:

- Logfiler
- Netværkspakker
- Fysiske spor
- Vidneudsagn
- Konfigurationsændringer

Spilleren samler spor.

Spor samles i en sagstavle.

---

# Introducer mistænkte

Spillet skal ikke afsløre årsagen tidligt.

Mulige mistænkte:

- Leverandør
- Tidligere medarbejder
- Utilfreds operatør
- Ekstern angriber
- Fejlkonfiguration

Spilleren skal undersøge.

Ikke gætte.

---

# Meningsfulde valg

Undgå binære valg.

Dårligt eksempel:

- Rigtigt svar
- Forkert svar

Foretræk:

- Sikkert men dyrt
- Hurtigt men risikabelt
- Driftssikkert men usikkert
- Compliance-rigtigt men operationelt besværligt

Alle valg skal have konsekvenser.

---

# Konsekvenssystem

Alle større beslutninger skal påvirke verden.

Spilleren skal mærke effekten.

Eksempler:

## Drift

Måles separat.

Påvirkes af:

- Produktionsstop
- Utilgængelige systemer
- Fejlkonfigurationer

---

## Sikkerhed

Måles separat.

Påvirkes af:

- Segmentering
- Firewalls
- Hardening
- Adgangskontrol

---

## Compliance

Måles separat.

Påvirkes af:

- Dokumentation
- Incident Response
- Forensics
- Rapportering

---

## Tillid

Måles separat.

Påvirkes af:

- Relation til karakterer
- Kommunikation
- Reaktion på hændelser

---

# Fra quiz til problemløsning

Undgå at spilleren løser problemer ved at huske svar.

Spilleren skal:

- Observere
- Samle data
- Undersøge
- Danne hypotese
- Teste hypotesen
- Træffe beslutning

---

# Dynamiske dage

Spillerens handlinger skal ændre fremtiden.

Eksempel

Dag 1:
Mistænkelig aktivitet.

Dag 2:
Angriberen eskalerer.

Dag 3:
Fysiske konsekvenser opstår.

Dag 4:
Ledelsen bliver involveret.

Dag 5:
Audit og evaluering.

Ingen gennemspilning skal være helt ens.

---

# Rogue Pi redesign

Rogue Pi må ikke blot være et objekt.

Den skal være et mysterium.

Først ser spilleren:

- Ukendte MAC-adresser
- Mærkelig trafik
- Tidsmæssige anomalier

Senere:

- Mistænkt fysisk placering

Til sidst:

- Fund af enheden

Dette skaber payoff.

---

# Progression

Hver zone skal fungere som et kapitel.

## Kapitel 1
Pumpehuset

Lær det grundlæggende.

---

## Kapitel 2
Ventil-øen

Introducer efterforskning.

---

## Kapitel 3
El-tavlen

Introducer teknisk kompleksitet.

---

## Kapitel 4
Kontrolrummet

Introducer koordinering.

---

## Kapitel 5
Den endelige hændelse

Kombiner alt tidligere lært.

---

# Teach Mode

Teach Mode skal fortsat eksistere.

Målet er:

- Forklaringer
- Hint
- Pædagogiske advarsler

Teach Mode bruges til læring.

---

# Exam Mode

Exam Mode skal fokusere på transfer.

Ingen tydelige hints.

Scenarier og svar bør randomiseres.

Spilleren skal anvende viden fremfor at huske.

---

# Designmål

For hvert nyt gameplayelement skal følgende spørgsmål besvares:

1. Gør dette verden mere levende?
2. Skaber dette nysgerrighed?
3. Kræver dette efterforskning?
4. Har valget konsekvenser?
5. Understøtter det OT-sikkerhedslæring?
6. Er det sjovt?

Hvis svaret på de sidste to spørgsmål ikke begge er JA, skal designet genovervejes.

---

# Endelig vision

Målet er ikke at bygge endnu en cybersecurity-quiz.

Målet er at bygge:

"Disco Elysium møder industrielle kontrolsystemer."

Et narrativt OT-cybersikkerhedseventyr hvor spilleren:

- undersøger
- analyserer
- foretager risikovurderinger
- beskytter kritisk infrastruktur

og samtidig oplever en engagerende historie.