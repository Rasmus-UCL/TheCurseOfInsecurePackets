# The Curse of Insecure Packets – Komplet Spil-, Scenarie- & Løsningsdokumentation

En interaktiv, spilbar OT-cybersikkerheds- og efterforskningssimulation udviklet til undervisning og eksamination på **UCL Erhvervsakademi og Professionshøjskole** (*Automationsteknolog*, *IT-Teknologi* og *PBA i Cybersikkerhed*).  
Spillet er kodet i **100 % ren Python standardbibliotek** (`tkinter`, `json`, `hashlib`, `shlex`, `dataclasses`) uden eksterne pakkeafhængigheder.

Denne `README.md` fungerer både som **teknisk dokumentation** og som **komplet underviser- og løsningskatalog** over samtlige scenarier, angrebsvariationer, korrekte løsninger, fejlvalg/faldgruber (i både *Teach Mode* og *Eksamens-Mode*) samt kriminaltekniske spor og gerningsmænd.

---

## 📑 Indholdsfortegnelse

1. [Spillets Koncept & Pædagogiske Opbygning](#-1-spillets-koncept--pædagogiske-opbygning)
2. [Sådan Starter og Betjener Du Spillet](#-2-sådan-starter-og-betjener-du-spillet)
3. [De 2 Tilstande: Teach Mode vs. Eksamens-Mode](#-3-de-2-tilstande-teach-mode-vs-eksamens-mode)
4. [De 4 Nøglemetrikker (Drift, Sikkerhed, Compliance, Tillid)](#-4-de-4-nøglemetrikker-drift-sikkerhed-compliance-tillid)
5. [Kapitel 0: Den Interaktive 5-Trins Intro-Tutorial](#-5-kapitel-0-den-interaktive-5-trins-intro-tutorial)
6. [Komplet Scenarie- & Løsningskatalog for de 4 Proceszoner (12 Scenarier + Alle Fejlveje)](#-6-komplet-scenarie--løsningskatalog-for-de-4-proceszoner-12-scenarier--alle-fejlveje)
   - [Zone A: Pumpehuset (3 Variationer + 3-Trins Workbench + Fejlvalg)](#-zone-a-pumpehuset-purdue-level-1--vfd--procespumper)
   - [Zone B: Ventil-øen (3 Variationer + Faraday Forensik + Fejlvalg)](#-zone-b-ventil-øen-purdue-level-1--decentralt-io--layer-2-feltbus)
   - [Zone C: Hoved-el-tavlen (3 Variationer + 5 Ingeniørveje & Fejlvalg)](#-zone-c-hoved-el-tavlen-purdue-level-12--s7-1500-f-plc--tia-portal)
   - [Zone D: Kontrolrummet / IDMZ (3 Variationer + OPC UA PKI & Fejlvalg)](#-zone-d-kontrolrummet--idmz-purdue-level-35--scada--opc-ua-pki)
7. [Efterforskningen, Sagstavlen & De 4 Dynamiske Syndere](#-7-efterforskningen-sagstavlen--de-4-dynamiske-syndere)
   - [De 4 Mulige Bagmænd (+ 1 Teknisk Vildspor)](#de-4-mulige-bagmænd--1-teknisk-vildspor)
   - [Komplet Tabel over Alle 11 Forensiske Spor](#komplet-tabel-over-alle-11-forensiske-spor)
8. [Kapitel 5: Konfrontation, NIS2-Revision & Bedømmelsesmatrix](#-8-kapitel-5-konfrontation-nis2-revision--bedømmelsesmatrix)
9. [Komplet Liste over Terminalkommandoer & `tshark`-Syntaks](#-9-komplet-liste-over-terminalkommandoer--tshark-syntaks)
10. [Kodearkitektur & Automatiserede Test-Suiter](#-10-kodearkitektur--automatiserede-test-suiter)

---

## 🎯 1. Spillets Koncept & Pædagogiske Opbygning

Drikkevandsværket **Nordic H2O Utility** (klassificeret som en *Væsentlig Enhed* under EU's **NIS2-direktiv**) rammes af mystiske driftsforstyrrelser og cyberangreb blot 5 arbejdsdage før et anmeldt tilsyn fra **Miljø- og Cybersikkerhedstilsynet** ved chefinspektør **Kirsten**.

Som nyankommet **Lead OT-Cybersikkerhedskonsulent** arbejder den studerende tæt sammen med værkets erfarne senior driftstekniker **Hans McDonald**. Spilleren skal løse to sideløbende hovedopgaver:
1. **Teknisk Hærdning & Driftsredning (IEC 62443 & NIS2 Art. 21):** Stoppe de aktive angreb i anlæggets 4 proceszoner uden at forårsage fysisk rørbrud, kavitation, F-I/O passivering eller SCADA-blindhed.
2. **Forensisk Efterforskning (NIS2 Art. 21.2.b & ISO/IEC 27037):** Opsamle tekniske og fysiske spor i hver zone, analysere beviserne på **Sagstavlen**, sikre beslaglagt hardware i antistatisk Faraday-pose og udpege den rigtige gerningsmand i Kapitel 5.

### Dynamisk Kampagne-Generator (Ingen gennemspilninger er ens)
Når spilleren trykker **🚀 Start Mission** på startskærmen, genererer [`GameEngine.randomize_campaign()`](./core/engine.py) automatisk en unik kampagne:
- **Automatisk tilfældig missionsrækkefølge:** De 4 proceszoner (`pumpehuset`, `ventil-oen`, `el-tavlen`, `kontrolrummet`) blandes automatisk i en tilfældig rækkefølge (spilleren vælger *ikke* selv rækkefølgen). Kapitel 5-konfrontationen med Revisor Kirsten ved `indgangen` ligger altid som den afsluttende finale, når alle 4 zoner er sikret.
- **3 tekniske angrebs-variationer (`A`, `B`, `C`) i hvert rum:** Hver zone trækker én af 3 forskellige tekniske angrebsvektorer ($3^4 = 81$ mulige tekniske kombinationer).
- **4 mulige dynamiske gerningsmænd:** Den sande synder bag angrebet trækkes tilfældigt blandt 4 mistænkte, og alle forensiske spor tilpasses automatisk, så beviserne peger logisk på netop den gennemspilnings gerningsmand.

---

## 🚀 2. Sådan Starter og Betjener Du Spillet

### Start i Grafisk Cockpit (Anbefalet)
```powershell
python .\game.py
```

### Start i Ren Tekstterminal (Headless / CLI)
```powershell
python .\game.py --cli
```

### Oversigt over Cockpittet (Fastlåst `1180x840` Vindue)
Brugerfladen i [`gui/app.py`](./gui/app.py) er låst til `1180x840` pixels med faste panelstørrelser, så hverken 2D-skærmen eller terminalen nogensinde forsvinder:
- **Startskærm / Hovedmenu:** Har 4 faner: `🚀 Nyt Spil`, `📂 Indlæs Gemt Spil`, `📖 Om Spillet & Lore` og `❌ Afslut`.
- **Top-bjælke (Purdue Zone-Navigator):** Viser arbejdsdag/time, nedtællingsur, zone-knapper (den aktive missionszone er fremhævet med `📍`), tilstandsknap (`🎓 Tilstand: TEACH / EKSAMEN`), `💾 Gem` og `🏠 Menu`.
- **4-Metrik HUD & Værktøjsbjælke:** Viser `🔧 Drift`, `🛡️ Sikkerhed`, `📜 Compliance` og `🤝 Tillid` samt knapperne:
  - `🕵️ Sagstavle (X spor)` — skifter til **orangerød (`⚠️ NYE!`)**, når du har fundet spor, der mangler analyse!
  - `🦈 Kør tshark CLI` — kører netværkssnifferen i den aktuelle zone.
  - `📞 TechSupport (3/3)` — tydelig blå knap, der giver et fagligt hint til den aktuelle zone (maks. 3 opkald pr. spil).
- **2D Visuel Skærm (`GameCanvas`, fast 310px højde):**
  - Klik direkte på **stiplede hotspots** på 2D-skærmen for at inspicere udstyr eller åbne arbejdsbænke.
  - Når **Sagstavlen** er åben, kan du klikke direkte på **Mistænkte-kort** (venstre) og **Spor-kort** (højre).
- **Klikbart Handlingspanel (`⚡ HANDLINGER I ZONEN`):** Viser de aktuelle valgmuligheder som klikbare knapper i 2 kolonner. Hvert klik rydder gammel tekst i terminalen, så kun det nye afsnit vises.
- **CRT-Terminal i bunden:** Fastlåst kommandoprompt (`>`), hvor man kan taste valgnumre (`1`–`8`) eller skrive autentiske CLI-kommandoer (`tshark`, `firewall rule add ...`, `gem`, `hovedmenu`).

---

## 🎓 3. De 2 Tilstande: Teach Mode vs. Eksamens-Mode

Spillet har **ingen spoilers** som `(Faldgrube)` eller `(Fælde)` i selve valgmulighederne i nogen af tilstandene — den studerende skal altid vurdere valgmulighederne fagligt. Forskellen ligger i, hvordan senior driftstekniker **Hans McDonald** reagerer, hvis man vælger en forkert eller farlig handling:

| Funktion | 🎓 Teach Mode (Undervisning & Træning) | 📝 Eksamens-Mode (Fuld Alvor & Test) |
| :--- | :--- | :--- |
| **Markering på knapper** | Ingen spoilers — alle valg præsenteres neutralt. | Ingen spoilers — alle valg præsenteres neutralt og i tilfældig rækkefølge. |
| **Ved forkert/farligt valg** | **Hans McDonald griber ind og stopper dig**, *før* handlingen udføres! Han forklarer pædagogisk, hvorfor valget er farligt for driften/sikkerheden, og henviser præcist til den rette procedure jf. **NIS2 Artikel 21/23**, **IEC 62443** eller **ISO/IEC 27037**. | **Hans griber IKKE ind.** Han kommer blot med en tør bemærkning (*"Det dér havde jeg nok ikke gjort, konsulent... men lad os komme videre"*), og **den fulde ulykke/konsekvens udløses** med tab af metrikker! |
| **Metrik-tab ved fejl** | **0 % tab** (da Hans afbryder handlingen før skaden sker). | **Fuldt tab** på `🔧 Drift`, `🛡️ Sikkerhed`, `📜 Compliance` og/eller `🤝 Tillid`. |

---

## 📊 4. De 4 Nøglemetrikker (Drift, Sikkerhed, Compliance, Tillid)

Alle beslutninger i spillet påvirker fire centrale metrikker i [`MetricValues`](./models.py):

1. **🔧 Drift (Start: 80 %):** Udtrykker vandværkets oppetid, stabile vandtryk og fysiske tilstand. Falder drastisk ved panik-nedlukninger, rå portblokeringer der blinder SCADA/PROFIsafe, eller korrupte PLC-overførsler.
2. **🛡️ Sikkerhed (Start: 25 %):** Udtrykker anlæggets tekniske modstandsdygtighed efter **IEC 62443** (Zoner & Conduits, L7 Deep Packet Inspection, Port Security, MRP-ring, TIA Protection Level 3 og OPC UA `Basic256Sha256`).
3. **📜 Compliance (Start: 40 %):** Udtrykker overholdelse af **NIS2 Artikel 21 & 23** (24-timers Early Warning til CSIRT, offline gylden backup, X.509 PKI-validering, Faraday-bevissikring med SHA-256 og korrekt identifikation af gerningsmanden).
4. **🤝 Tillid (Start: 50 %):** Udtrykker samarbejdet med driftstekniker Hans McDonald. Stiger når man inddrager driften, finder spor og sikrer backup; falder når man handler overilet og skader anlægget.

---

## 🎓 5. Kapitel 0: Den Interaktive 5-Trins Intro-Tutorial

Hvis fluebenet **"Start med kort interaktiv Intro-Tutorial"** er slået til på startskærmen, starter spillet i **Kapitel 0** ved `Hovedindgangen` med nedtællingsuret sat på pause (`00:00` brugt tid). Tutorialen kan til enhver tid springes over med valg `[2] Spring intro-tutorialen over`.

| Trin | Formål | Hvad skal spilleren gøre? | Hvad lærer spilleren? |
| :--- | :--- | :--- | :--- |
| **Trin 1/5** | Inspektion & Hotspots | Klik på `EMALJESKILT (Zoner)` på 2D-skærmen eller tast `1` (`undersøg skilt`). | At fysiske komponenter kan inspiceres ved at klikke direkte på 2D-skærmen eller via handlingspanelet. |
| **Trin 2/5** | Netværksanalyse med `tshark` | Klik på `🦈 Kør tshark CLI`, tast `1` eller skriv `tshark` i terminalen. | At `tshark` opsnapper netværkspakker på zonens VLAN og automatisk registrerer tekniske spor (`spor_morten_rapport`). |
| **Trin 3/5** | Åbn Sagstavlen | Klik på den blinkende orange knap `🕵️ Sagstavle` eller tast `1` (`sagstavle`). | At nyopdagede spor markeres tydeligt på Sagstavlen, så man husker at efterforske synderen. |
| **Trin 4/5** | 2-Trins Bevisanalyse & Mistænkt | Klik på det nye spor på Sagstavlen (`analyser spor spor_morten_rapport`) **OG** klik på en mistænkt (`anklag morten_pumper`). | At et spor først afslører, hvem det peger på, når det er **analyseret**, og hvordan man vælger en foreløbig `⭐ Hovedmistænkt`. |
| **Trin 5/5** | De 4 Metrikker & Start | Tast `1` (`afslut tutorial`). | Gennemgang af Drift, Sikkerhed, Compliance og Tillid, hvorefter Kapitel 1 og uret starter i den første udtrukne alarm-zone! |

---

## 🛠️ 6. Komplet Scenarie- & Løsningskatalog for de 4 Proceszoner (12 Scenarier + Alle Fejlveje)

Herunder gennemgås samtlige **4 proceszoner**, deres **3 mulige angrebs-variationer (`A`, `B`, `C`)**, den præcise **korrekte løsning** samt **alle fejlvalg/faldgruber** og deres konsekvenser.

---

### 🚰 Zone A: Pumpehuset (Purdue Level 1 — VFD & Procespumper)

**Fysisk situation:** Centrifugalpumpe 2 skriger i lejerne under voldsom kavitation, og manometeret hamrer i rød zone ved `14.8 Bar` (på vej mod sprængningsgrænsen på `150 Bar` i hovedrøret). Når spilleren træder ind i Pumpehuset, starter en akut **3-minutters sprængnings-deadline**.

#### De 3 mulige angrebs-variationer i Pumpehuset (`room_variants["pumpehuset"]`)

| Variant | Angrebets Navn & Protokol | Hvad sker der teknisk? | Hvad viser `tshark` i Pumpehuset? | Spor der opdages |
| :--- | :--- | :--- | :--- | :--- |
| **Variant A** | **Modbus TCP Register Flood (TCP Port 502)** | En uautoriseret vært (`10.20.1.77` / `192.168.1.99`) oversvømmer SINAMICS VFD'en med `Modbus FC 06 (Write Single Register)` til Holding Register `0x0000 = 1337` (120 Hz) hvert 20. ms. | `Query: Write Single Register (FC 06) [SABOTAGE REG 0x0000=1337]` på TCP Port 502 samt legitim `FC 03 Read Holding Registers` fra SCADA (`10.20.1.5`). | `spor_modbus_flood` *(Højhastigheds Modbus FC06 skrivninger)* |
| **Variant B** | **SNMPv1 Default Community (`private`) & ARP-Poisoning (UDP Port 161)** | **Ikke et Modbus-angreb!** Angriberen sender falske ARP-svar (`ARP Poisoning`) for at isolere PLC'en og bruger en åben SNMPv1-agent med fabriks-community `'private'` på UDP port 161 til at overskrive `OID 1.3.6.1.4.1.4329.2.1 (MaxFrequency) = 120 Hz`. | `ARP Reply: 10.20.1.1 is at dc:a6:32:99:88:77 [ARP POISONING]` samt `SNMPv1 SetRequest community='private' OID ... = 120Hz [SABOTAGE]`. | `spor_modbus_flood` *(Uautoriseret SNMPv1 SetRequest 'private' & ARP-Spoofing)* |
| **Variant C** | **Ubeskyttet VFD HTTP Web-API Override (`admin/admin` på TCP Port 80)** | **Ikke et Modbus-angreb!** Angriberen er logget ind på VFD'ens indbyggede HTTP-diagnoseserver (TCP Port 80) med standard-login `admin:admin` (`Basic YWRtaW46YWRtaW4=`) og tvinger setpunktet i 120 Hz manuel tvangsdrift via REST API. | `HTTP POST /api/vfd/override HTTP/1.1 (Basic Auth: admin:admin) [120 Hz TVANGSDRIFT]` på TCP Port 80. | `spor_modbus_flood` *(Ukrypteret HTTP Web-API Override på VFD Port 80)* |

#### ✅ Korrekt Løsning i Pumpehuset (Sekventiel 3-Trins DIN-Skinne Arbejdsbænk)
Uanset om Variant A, B eller C er aktiv, skal frekvensomformeren isoleres i en **IEC 62443 Conduit** bag en industriel **Siemens SCALANCE S615** sikkerhedsrouter på TS35 DIN-skinnen:
1. **Åbn arbejdsbænken:** Klik på `TS35 DIN-SKINNE` på 2D-skærmen, vælg `[Åbn arbejdsbænk for TS35 DIN-skinne & SCALANCE S615 firewall]` eller skriv `firewall workbench`.
2. **Trin 1/3 (Fysisk montage):** Vælg `[1] 🔌 [Trin 1/3] Fastgør SCALANCE S615 sikkerhedsrouteren på TS35 DIN-skinnen` (`monter scalance på din-skinne`).
3. **Trin 2/3 (Korrekt Zone/Conduit-kabling):** Vælg `[1] 🔀 [Trin 2/3] Forbind VFD til LAN-port (P1) og anlægsnetværk til WAN-port (P5)` (`kobl kabler til scalance`).
4. **Trin 3/3 (Aktivér DPI / Conduit-regel MED tilladelse til SCADA FC 03):**
   - **Variant A:** Vælg `[1] 🛡️ [Trin 3/3] Opret regel: 'firewall rule add --allow-fc 3 --drop-fc 6'`.
   - **Variant B:** Vælg `[1] 🛡️ [Trin 3/3] Spær SNMPv1 Write ('private'), aktivér ARP Inspection (DAI) og tillad SCADA FC 03`.
   - **Variant C:** Vælg `[1] 🛡️ [Trin 3/3] Spær ukrypteret HTTP Port 80, lås VFD-setpunkt til PLC og tillad SCADA FC 03`.
   - **Resultat & Belønning:** Pumpe 2 falder til ro på `42.0 Bar` (`50 Hz`), sprængnings-timeren stoppes, og spilleren modtager **`+10 % Drift`**, **`+25 % Sikkerhed`**, **`+15 % Compliance`** og **`+15 % Tillid`**.

#### ❌ Fejlvalg & Faldgruber i Pumpehuset

| Fejlvalg / Handling | 🎓 Hvad gør Hans i Teach Mode? | 📝 Konsekvens i Eksamens-Mode & Udbedring |
| :--- | :--- | :--- |
| **Afbryd forsyningen på hovedafbryderen (`hård nødnedlukning af vfd`)** | Hans griber dit håndled og stopper dig: Forklarer at 12 tons vand under 146 Bar skaber et destruktivt **hydraulisk vandslag**, og henviser til **NIS2 Art. 21.2.c (Driftskontinuitet)**. | **Hydraulisk vandslag!** Sikkerhedsrelæ **K1** i Hoved-el-tavlen sprænger (`breaker_tripped = True`), og Pumpehuset bliver strømløst. **Udbedring:** Du *skal* gå til `Hoved-el-tavlen` og vælge `⚡ Nulstil sikkerhedsrelæ K1` (`nulstil relæ`), før du kan arbejde videre i Pumpehuset! |
| **Blokér al Port 502 trafik råt (`bloker port 502`) ELLER glem `--allow-fc 3` (`firewall rule add --drop-fc 6`)** | Hans stopper dig ved tastaturet: Forklarer at `SCALANCE S615` kører med *Default Deny*, og at blokering uden `--allow-fc 3` kapper `Read Holding Registers (FC 03)` til WinCC SCADA jf. **NIS2 Art. 21 & IEC 62443-3-3**. | **SCADA Blindhed (`scada_blind = True`)!** Kontrolrummet mister al overvågning af Pumpe 2 (`-25 % Drift`, `-15 % Tillid`, `-10 % Compliance`). **Udbedring:** Kør den fulde regel med `--allow-fc 3 --drop-fc 6`. |
| **Byt om på LAN og WAN (`byt om på lan og wan`)** | Hans peger på portene og stopper dig: Forklarer at det sårbare aktiv (VFD'en) altid skal ligge på den beskyttede interne **LAN Port P1**, mens det usikre anlægsnet kobles på **WAN Port P5** jf. **IEC 62443-3-2**. | `wrong_cabling = True`. VFD'en er fortsat eksponeret på WAN-siden, og firewall-regler kan ikke aktiveres, før du vælger korrekt kabling. |
| **Drej manuelt på frontpanelets potentiometer (`juster setpunkt`)** | Hans stopper dig: Forklarer at netværksloopet overskriver værdien igen efter 20 ms. | VFD'en tvinges straks tilbage på 120 Hz, og du mister **20 kostbare sekunder** på sprængnings-uret! |

---

### 💨 Zone B: Ventil-øen (Purdue Level 1 — Decentralt I/O & Layer 2 Feltbus)

**Fysisk situation:** Festo-magnetventilerne og de decentrale Siemens ET 200SP I/O-stationer smælder ukontrolleret op og i. På DIN-skinnen sidder en billig, uadministreret D-Link switch, og bag stålrammen løber **kabelbakke K-04**.

#### De 3 mulige angrebs-variationer på Ventil-øen (`room_variants["ventil-oen"]`)

| Variant | Fysisk Implantat & Protokol-Sabotage | Hvad sker der teknisk? | Hvad viser `tshark` på Ventil-øen? | Spor der opdages |
| :--- | :--- | :--- | :--- | :--- |
| **Variant A** | **Rogue Raspberry Pi 4 med PROFINET DCP Name-Spoofing** | En optapet Raspberry Pi 4 under kabelbakken sender Layer 2 `PROFINET DCP Set NameOfStation='rogue-io'` broadcast-storme og ARP-poisoning. | `PN-DCP Set: NameOfStation='rogue-io' [HIJACKING]` og `ARP Spoof` fra MAC `b8:27:eb:d4:11:22`. | `spor_sort_boks`, `spor_dcp_storm`, `spor_mac_oui` |
| **Variant B** | **Skjult Aktiv LAN-Tap i ventil-klemkassen med IEEE 802.1Q Priority-Stripping & LLDP-Spoofing** | En sort aktiv mikro-tap i klemkassen stripper `IEEE 802.1Q Priority 6` QoS-tags fra de deterministiske PROFINET RT-rammer og forgifter topologien med falske `LLDP`-pakker. | `LLDP Chassis ID='rogue-tap' [TOPOLOGI-FORGIFTNING]` og `PROFINET RT [802.1Q PRIORITY TAG STRIPPED -> JITTER!]`. | `spor_sort_boks`, `spor_dcp_storm`, `spor_mac_oui` |
| **Variant C** | **Uautoriseret ESP32/MQTT-Bro med ukrypteret MQTT Kommandostorm (TCP Port 1883)** | Et hjemmebygget ESP32/Pi-modul under kabelbakken pumper uautentificerede `MQTT PUBLISH` pakker ind på smart-ventilernes IIoT-sidekanal (Port 1883 uden TLS). | `MQTT PUBLISH Topic='nordic/valves/all/set' Payload='OSCILLATE_MAX' [PORT 1883]`. | `spor_sort_boks`, `spor_dcp_storm`, `spor_mac_oui` |

#### ✅ Korrekt Løsning på Ventil-øen (3 Trin)
1. **Find det skjulte implantat:** Vælg `🔦 Undersøg kabelbakke K-04 bag ventilstativerne for skjult kabling` (`undersøg kabelbakke`). Dette afslører den sorte boks og registrerer `spor_sort_boks`.
2. **Forensisk bevissikring (Chain of Custody):** Vælg `🛡️ Frakobl enheden, forsegl den i antistatisk Faraday-pose og log SHA-256` (`sikr pi i faraday-pose`).
   - Enheden isoleres radiomæssigt i en Faraday-pose, dens hukommelse hashes med `SHA-256`, og der oprettes et plomberingsnummer i evidensloggen (`+20 % Sikkerhed`, `+25 % Compliance`, `+10 % Tillid`).
3. **Etablér deterministisk MRP-ring & Port Security:** Vælg `🔄 Monter SCALANCE XB-200 managed switch og etabler redundant PROFINET MRP-ring` (`udskift switch med scalance`).
   - Giver yderligere **`+20 % Sikkerhed`**, **`+15 % Compliance`** og **`+10 % Tillid`**, og udløser `spor_dcp_storm` og `spor_mac_oui`.

#### ❌ Fejlvalg & Faldgruber på Ventil-øen

| Fejlvalg / Handling | 🎓 Hvad gør Hans i Teach Mode? | 📝 Konsekvens i Eksamens-Mode & Udbedring |
| :--- | :--- | :--- |
| **Træk alle patchkabler ud af D-Link switchen med det samme (`pille switch fra`)** | Hans holder dine hænder væk fra kablerne: Forklarer at brat tab af modtryk udløser destruktiv **kavitation** i pumperne, og henviser til **NIS2 Art. 21.2.c** og **IEC 62439-2 (MRP)**. | **Akut Kavitations-Alarm (90 sekunders nedtælling)!** Ventilerne låser, pumperne kaviterer voldsomt (`-20 % Drift`, `-10 % Tillid`), og du har 90 sekunder til at fjerne implantatet og montere SCALANCE-switchen, før pumpehjulet smadres! |
| **Smid boksen i skraldespanden (`smid pi i skraldespand`)** | Hans griber din arm: Forklarer at destruktion af bevismateriale under en cyberhændelse er i strid med **NIS2 Art. 21.2.b / Art. 23** og **ISO/IEC 27037**. | **Tab af retsmedicinsk bevis (`pi_handling_state = "trashed"`)!** Koster **`-30 % Compliance`** og **`-10 % Tillid`**, og udløser en tung straf (-25 point) hos Revisor Kirsten i Kapitel 5! |
| **Gem boksen på hylden til genbrug (`gem pi til genbrug`)** | Hans stopper dig: Forklarer at kompromitteret hardware aldrig må genbruges uden fuld retsmedicinsk analyse. | **Sikkerhedsbrud (`pi_handling_state = "reused"`)!** Koster **`-25 % Sikkerhed`** og **`-25 % Compliance`**. |
| **Sæt MicroSD-kortet direkte i din egen bærbare PC (`indsæt sd-kort i bærbar`)** | Hans smækker låget på din laptop i: Advarsel mod **USB/SD Rubber Ducky / auto-mount malware** og kontaminering af tidsstempler jf. **ISO/IEC 27037**. | **Kompromitteret ingeniør-PC (`pi_handling_state = "infected"`)!** Koster **`-25 % Sikkerhed`** og **`-25 % Compliance`**. |

---

### ⚡ Zone C: Hoved-el-tavlen (Purdue Level 1/2 — S7-1500 F-PLC & TIA Portal)

**Fysisk situation:** Vandværkets centrale sikkerheds-PLC (**Siemens S7-1500 CPU 1516F**) står i rød `STOP`-mode, så buffertankene ikke reguleres. I tavlens dokumentlomme ligger et efterladt USB-stik.

#### De 3 mulige angrebs-variationer i Hoved-el-tavlen (`room_variants["el-tavlen"]`)

| Variant | Angrebsvektor mod S7-1500 PLC | Hvad sker der teknisk? | Hvad viser `tshark` & PLC-loggen? | Spor der opdages |
| :--- | :--- | :--- | :--- | :--- |
| **Variant A** | **Uautoriseret S7comm PUT/GET Blok-overskrivning (TCP Port 102)** | Angriberen sender rå `S7comm Write Variable (PUT)`-kald på port 102 direkte ind i kalibreringsblokken `DB1.DBX0.0`, fordi *Permit access with PUT/GET* står åben uden kodeord. | `S7comm PUT: Write Variable (PUT to DB1.DBX0.0) [UAUTORISERET]` efterfulgt af `Error Code 0x8104 (CPU STOP)`. | `spor_plc_stop_buffer`, `spor_usb_backup` |
| **Variant B** | **Manipuleret F-Safety Watchdog & Cyklustids-sabotage i OB35 (`0x75E1`)** | Angriberen har udnyttet manglende F-Safety adgangskode til at ændre `OB35` cyklustiden til `500 ms` (over grænsen på `100 ms`), så Fail-Safe watchdoggen udløser Safety-STOP. | `S7comm Download: Modify OB35 Cyclic Interrupt (Watchdog = 500ms > Max 100ms)` og `Diagnostic Event 0x75E1`. | `spor_plc_stop_buffer`, `spor_usb_backup` |
| **Variant C** | **NTP Time-Spoofing (UDP Port 123) & Ugyldiggjorte PLC TLS-Certifikater** | Angriberen sender usignerede `NTP Stratum 1`-svar på UDP port 123, der tvinger PLC-uret tilbage til `1970-01-01`, så CPU'ens X.509/TLS-sikkerhedscertifikater fejler tidsvalidering. | `NTP Server Response: Time='1970-01-01 00:00:01 UTC' [TIME-SPOOFING]` og `TLS Certificate Not Yet Valid -> CPU STOP`. | `spor_plc_stop_buffer`, `spor_usb_backup` |

#### ✅ Korrekt Løsning i Hoved-el-tavlen (2 Obligatoriske Trin + Forensisk Inspektion)
1. *(Anbefalet)* **Inspicér USB-stikket i tavlens lomme (`undersøg usb`) og kør `tshark`:** Sikrer de to vigtige spor `spor_usb_backup` og `spor_plc_stop_buffer`.
2. **Trin 1 (Lovpligtig Offline Backup — NIS2 Art. 21.2.c):** Vælg `💾 Opret offline sikkerhedskopi af CPU 1516F projekt og DB1 til USB-stik` (`tag offline backup`).
   - Logger en kryptografisk verificeret backup i evidensjournalen og giver **`+10 % Compliance`** og **`+5 % Tillid`**.
3. **Trin 2 (TIA Portal Security Hardening):** Vælg `⚙️ Konfigurer TIA Portal...` (`konfigurer tia portal`).
   - Deaktiverer PUT/GET (Variant A), gendanner OB35 & F-Safety kode (Variant B) eller låser NTP til autentificeret GPS-server med SHA-256 (Variant C), og aktiverer **Protection Level 3**.
   - CPU 1516F skifter til grøn `RUN`-diode! Belønning: **`+15 % Drift`**, **`+20 % Sikkerhed`**, **`+15 % Compliance`** og **`+10 % Tillid`**.

#### ❌ De 5 Fejlvalg & Ingeniør-Fælder i Hoved-el-tavlen

| Fejlvalg / Handling | 🎓 Hvad gør Hans i Teach Mode? | 📝 Konsekvens i Eksamens-Mode & Udbedring |
| :--- | :--- | :--- |
| **1. Konfigurér TIA Portal UDEN først at have taget offline backup (`konfigurer tia portal` før `tag offline backup`)** | Hans lægger hånden over musen: Forklarer at download til en PLC under et aktivt netværksangreb uden backup risikerer CRC-fejl, og henviser til **NIS2 Art. 21.2.c (Backup Management)**. | **Korrupt overførsel (`plc_defect_stop = True`)!** Et netværkshak under overførslen korrumperer `DB1` (`0x4542 DEFECTIVE STOP`), og du mister **`-25 % Drift`** og **`-15 % Tillid`**. **Udbedring:** Du skal vælge `💾 Indsæt autoriseret USB-stik og gendan fabrikskalibreret DB1` (`gendan plc db1`), før du kan konfigurere TIA Portal! |
| **2. Tving CPU 1516F i RUN med den fysiske nøgleomskifter (`tving cpu i run`)** | Hans stopper din hånd ved nøglekontakten: Forklarer at sårbarheden på Port 102 stadig står åben, så angriberen straks overskriver PLC'en igen (**IEC 62443-4-2**). | **Koldstart fejler!** Angriberens loop tvinger øjeblikkeligt CPU'en tilbage i STOP. Koster **`-25 % Drift`** og **`-15 % Tillid`**. |
| **3. Blokér al TCP Port 102 trafik i celle-firewallen (`bloker port 102`)** | Hans stiller sig foran firewallen: Forklarer at blokering af Port 102 også kapper **PROFIsafe**-kommunikationen til nødstop-modulerne (**EN ISO 13849 / IEC 62061**). | **Total F-I/O Passivering & Nødstop (`plc.f_passivated = True`)!** Sikkerheds-I/O går i passiveret fejltilstand. Koster **`-35 % Drift`** og **`-20 % Tillid`**! |
| **4. Overfør ny firmware live over netværket (`opdater firmware live`)** | Hans afbryder downloaden: Advarsel mod uverificeret live firmware-opdatering over et kompromitteret netværk uden SHA-256 kontrol (**NIS2 Art. 21.2.d Supply Chain Security**). | **Bootloader låst (`plc.bootloader_locked = True`)!** MitM-korruption under firmware-flash koster **`-30 % Drift`** og **`-20 % Compliance`**. |
| **5. Tilslut tekniker-laptop direkte i CPU Port X1 under drift (`kobl laptop i plc port`)** | Hans holder igen i dit patchkabel: Advarsel mod uisoleret tilkobling under aktiv ARP-spoofing. | **ARP-spoofing kaprer TIA-sessionen!** Koster **`-15 % Sikkerhed`** og **`-15 % Drift`**. |

---

### 🖥️ Zone D: Kontrolrummet / IDMZ (Purdue Level 3.5 — SCADA & OPC UA PKI)

**Fysisk situation:** WinCC SCADA-skærmene flimrer med alarmer. En ulovlig fysisk kommunikationsvej omgår perimeter-firewallen i Industrial DMZ (IDMZ), og anlæggets **OPC UA-server på TCP port 4840** kører med `SecurityPolicy: None` og tillader `Anonymous` adgang.

#### De 3 mulige angrebs-variationer i Kontrolrummet (`room_variants["kontrolrummet"]`)

| Variant | Fysisk IDMZ-Bagdør & OPC UA Sårbarhed | Hvad sker der teknisk? | Hvad viser `tshark` i Kontrolrummet? | Spor der opdages |
| :--- | :--- | :--- | :--- | :--- |
| **Variant A** | **Teltonika RUT950 4G-Router bag SCADA-racket + Åben OPC UA** | En cellulær 4G-router sat i vægstikket bag server-racket skaber en direkte VPN-tunnel udefra ind i SCADA-switchen, mens OPC UA står åben uden kryptering. | `Inbound TCP connection fra Teltonika 4G VPN tunnel [BACKDOOR]` samt `OPC.TCP OpenSecureChannel: SecurityPolicy='None'` & `UserTokenType=Anonymous`. | `spor_4g_dongle`, `spor_opc_leak`, `spor_kim_nattevagt` |
| **Variant B** | **Skjult Wi-Fi Access Point under gulvet ved patchpanelet + Stjålet Leverandør-Certifikat** | Et skjult dual-band Wi-Fi AP under det hævede gulv giver trådløs adgang fra parkeringspladsen, og en klient bruger et kompromitteret leverandør-certifikat + `SecurityPolicy='None'`. | `OPC.TCP OpenSecureChannel: Stjålet Leverandør-Certifikat + SecurityPolicy='None' [DATA-LÆK]` fra `192.168.88.10`. | `spor_4g_dongle`, `spor_opc_leak`, `spor_kim_nattevagt` |
| **Variant C** | **Uautoriseret RDP/VPN Hardware-Tunnelboks (TCP Port 3389 uden MFA) + Åben OPC UA** | En mini-tunnelboks bag IDMZ-patchpanelet eksponerer Remote Desktop (`TCP 3389`) direkte til SCADA-stationen uden Multi-Factor Authentication (**NIS2 Art. 21.2.j**). | `RDP Connect: TCP Port 3389 Remote Desktop Session (Ingen MFA!) + OPC UA SecurityPolicy='None'`. | `spor_4g_dongle`, `spor_opc_leak`, `spor_kim_nattevagt` |

#### ✅ Korrekt Løsning i Kontrolrummet (4 Hærdningstrin + Forensisk Log-Inspektion)
For at gennemføre Kontrolrummet skal alle **4 sikkerhedskrav** opfyldes (rækkefølgen af de 4 trin er valgfri):
1. *(Anbefalet)* **Inspicér WinCC SCADA PC (`undersøg scada pc`) og kør `tshark`:** Sikrer `spor_kim_nattevagt` (natlige logins kl. 03:14) og `spor_opc_leak`.
2. **Krav 1 — Fjern den fysiske IDMZ-bagdør (`frakobl 4g-router`):** Frakobler 4G-routeren (Variant A), det skjulte Wi-Fi AP (Variant B) eller RDP-tunnelboksen (Variant C). Giver **`+20 % Sikkerhed`**, **`+15 % Compliance`** og registrerer `spor_4g_dongle`.
3. **Krav 2 — X.509 PKI Truststore (`godkend scada certifikat`):** Flytter WinCC SCADA-klientens X.509 certifikat til `Trusted` (og spærrer evt. stjålet certifikat i CRL). Giver **`+10 % Compliance`** og **`+5 % Tillid`**.
4. **Krav 3 — Aktivér OPC UA Kryptografi (`aktiver opc kryptering`):** Sætter SecurityPolicy til `Basic256Sha256` og MessageSecurityMode til `SignAndEncrypt` jf. **NIS2 Art. 21.2.h**. Giver **`+15 % Sikkerhed`**.
5. **Krav 4 — Fjern Anonym Adgang & Håndhæv RBAC/MFA (`deaktiver anonymous opc`):** Deaktiverer `Anonymous` UserToken på port 4840. Giver **`+10 % Sikkerhed`** og **`+10 % Tillid`**.

#### ❌ Fejlvalg & Faldgruber i Kontrolrummet

| Fejlvalg / Handling | 🎓 Hvad gør Hans i Teach Mode? | 📝 Konsekvens i Eksamens-Mode & Udbedring |
| :--- | :--- | :--- |
| **Blokér al TCP Port 4840 trafik i IDMZ-firewallen (`bloker port 4840 totalt`)** | Hans stopper dig ved firewallen: Forklarer at port 4840 bruges til lovpligtig miljø- og drikkevandsrapportering til Miljøstyrelsen, og at porten skal **krypteres og autentificeres** frem for at lukkes (**NIS2 Art. 21.2.h**). | **Miljølogning afbrudt (`scada_log_interrupted = True`)!** Udløser en kritisk compliance-fejl hos Tilsynet. **Udbedring:** Vælg `🔧 Genåbn Port 4840 og skift til selektiv X.509 certifikat-validering` (`aktiver opc certifikater`). |

---

## 🕵️ 7. Efterforskningen, Sagstavlen & De 4 Dynamiske Syndere

Mange studerende bliver så optagede af at slukke tekniske brande, at de glemmer at undersøge, **hvem der står bag angrebet**. Derfor har spillet en dedikeret, interaktiv **Sagstavle (`🕵️ Sagstavle`)** og et fast **Efterforsknings-Checkpoint** efter hver sikret zone.

### Sådan fungerer 2-Trins Bevisanalysen på Sagstavlen
1. **Opdagelse af spor (`discovered = True`, `analyzed = False`):**
   - Når du undersøger et hotspot, spørger Hans eller kører `tshark`, tilføjes sporet på Sagstavlen som **`⚠️ NYT SPOR — KLIK FOR ANALYSE!`**, og knappen `🕵️ Sagstavle` i topbaren lyser **orangerødt**.
   - På dette tidspunkt kan du **endnu ikke se**, hvilke mistænkte sporet peger på (`Peger mod: [Ukendt indtil sporet analyseres]`).
2. **Teknisk Dybdeanalyse (`analyzed = True`):**
   - Når du **klikker direkte på sporet på Sagstavlen** (eller skriver `analyser spor <spor_id>`), udføres den kriminaltekniske analyse:
   - Sporet skifter til **`✅ ANALYSERET`**, afslører sin tekniske vurdering og opdaterer mistanke-scoren (`+5 %`) samt beviskæden (`🔗 Analyserede beviser`) for de mistænkte, sporet peger på!
3. **Udpegning af Hovedmistænkt (`prime_suspect_id`):**
   - Klik direkte på en mistænkt i venstre kolonne på Sagstavlen (eller skriv `anklag <id>`) for at markere vedkommende som din **`⭐ HOVEDMISTÆNKT`**.

---

### De 4 Mulige Bagmænd (+ 1 Teknisk Vildspor)

Ved start af et nyt spil udpeger [`InvestigationManager.configure_dynamic_case()`](./core/investigation.py) én af de 4 første profiler herunder som gennemspilningens sande gerningsmand (`true_culprit_id`):

| Mistænkt ID | Navn & Titel | Motiv & Modus Operandi når vedkommende er gennemspilningens Synder |
| :--- | :--- | :--- |
| **`lars_ex_tekniker`** | **Lars Kofoed** *(Tidligere OT-Automationstekniker, fyret for 2 mdr. siden)* | **Hævnaktion efter fyring:** Lars mente sig snydt for 200 timers overarbejde. Han beholdt en gammel nøglebrik, plantede det sorte hardware-implantat på Ventil-øen, udnyttede Kims 4G-router/fjernadgang til at angribe udefra og brugte sit indgående kendskab til TIA Portal-projektet (`LARS - TIA V16 BACKUP` / bruger `LKO_ENG`) til at ramme `DB1` og VFD'en lige før Tilsynets besøg. |
| **`morten_pumper`** | **Morten Vestergaard** *(Ekstern Servicepartner, Hydropump Nordic A/S)* | **Supply Chain Sabotage & Økonomisk Afpresning (NIS2 Art. 21.2.d):** Morten lånte hovednøglen under sit servicebesøg tirsdag og besøgte uovervåget både Pumpehus, Ventil-ø og El-tavle. Han efterlod en rød leverandør-USB (`HYDROPUMP NORDIC - SERVICE DIAG V4`) med scriptet `pump_stress_induce.py` (signeret `mve@hydropump.dk`) samt et implantat fra `Hydropump Field Test Lab #04` — og dagen efter sendte Hydropump Nordic et tilbud på en "Akut 24/7 Total-Servicekontrakt" til **1,8 mio. kr.**! |
| **`apt_shadowh2o`** | **ShadowH2O / DarkVolt Syndikatet** *(Ekstern Cyberkriminel APT-gruppe)* | **Målrettet Kritisk Infrastruktur Ransomware & Sabotage:** APT-gruppen brød ind via den usikrede fjernadgang og åbne OPC UA-server i Kontrolrummet og pivoterede direkte ned til Level 1/2. `tshark` og netværksspor afslører krypterede C2-beacons hvert 30. sekund til en ekstern Tor-relay samt en droppet ransomware-staging fil (`SHADOWH2O_README.TXT`) i El-tavlen, som matcher Europol-advarsler. |
| **`kim_operatoer`** | **Kim Dahl** *(Intern Procesoperatør på Natholdet)* | **Insider-sabotage for at skjule egen fejlbetjening:** Kim satte ikke blot ulovlig fjernadgang op i Kontrolrummet for at slippe for natkørsel; da han torsdag nat lavede en alvorlig fejlbetjening, gik han i panik og kørte hjemmelavede Python/bash bypass-scripts (`override_all_zones.sh` kl. `03:14`) fra sit personlige USB-stik (`KIM D. - NATTEVAGT AUTO-BYPASS SCRIPTS`) for at undertrykke alarmerne! |
| **`systemisk_fejl`** *(Altid vildspor)* | **Systemisk Konfigurationskollaps & Teknisk Gæld** *(Ingen fjendtlig aktør)* | **Fagligt vildspor:** Tester om den studerende kan skelne mellem almindelig teknisk gæld (fladt netværk, manglende VLANs) og aktiv, forsætlig sabotage (optapet hardware under kabelbakken og målrettede pakke-loops). |

---

### Komplet Tabel over Alle 11 Forensiske Spor

| Spor ID | Kategori | Zone | Hvordan opdages sporet? | Hvad viser sporet (tilpasses dynamisk efter Variant A/B/C og aktiv Synder)? |
| :--- | :--- | :--- | :--- | :--- |
| `spor_morten_rapport` | Vidneudsagn | `indgangen` / `pumpehuset` | Kør `tshark` i Tutorialen, `tal med hans` eller `spørg hans om morten`. | Dokumenterer Mortens servicebesøg tirsdag (og hvis Morten er synderen: adgangslog fra alle 4 zoner + det mistænkelige 1,8 mio. kr. servicetilbud!). |
| `spor_manometer_rystelser` | Fysisk | `pumpehuset` | `undersøg pumpe 2` | Fysiske trykstød på 14.8 Bar mens SCADA viser normalværdi (klassisk Stuxnet-stil telemetri-manipulering). |
| `spor_modbus_flood` | Netværk | `pumpehuset` | Kør `tshark` i Pumpehuset eller løs Pumpehusets firewall. | **Variant A:** Modbus FC06 flood. **Variant B:** SNMPv1 `'private'` SetRequest & ARP-spoof. **Variant C:** HTTP Web-API Override (`admin/admin`). |
| `spor_sort_boks` | Fysisk | `ventil-oen` | `undersøg kabelbakke` eller `sikr pi i faraday-pose` | **Variant A:** Rogue Raspberry Pi 4. **Variant B:** Aktiv LAN-tap i klemkassen. **Variant C:** ESP32/MQTT-bro. *(Har Hydropump-inventarmærke hvis Morten er synderen).* |
| `spor_dcp_storm` | Netværk | `ventil-oen` | Kør `tshark` på Ventil-øen, `undersøg ventiler` eller løs Ventil-øen. | **Variant A:** PROFINET DCP broadcast-storm. **Variant B:** IEEE 802.1Q Priority-stripping & LLDP-spoof. **Variant C:** Ukrypteret MQTT kommandostorm på port 1883. |
| `spor_mac_oui` | Netværk | `ventil-oen` | Kør `tshark` på Ventil-øen eller løs Ventil-øen. | Fremmed MAC-adresse `b8:27:eb:d4:11:22` på feltbussen *(eller C2-beacons til Tor-relay, hvis `apt_shadowh2o` er synderen)*. |
| `spor_plc_stop_buffer` | Systemlog | `el-tavlen` | Kør `tshark` i El-tavlen, `undersøg s7-1500` eller løs El-tavlen. | **Variant A:** S7comm PUT/GET DB1-fejl (`0x8104`). **Variant B:** F-Safety OB35 Watchdog Timeout (`0x75E1`). **Variant C:** NTP Time-Jump til 1970 & TLS-fejl. |
| `spor_usb_backup` | Konfiguration | `el-tavlen` | `undersøg usb` eller `spørg hans om lars` | **Nøglebevis i El-tavlen!** Skifter indhold efter den sande synder: *Lars' TIA V16 USB* (`LKO_ENG`), *Hydropump Service Diag V4 USB* (`mve@hydropump.dk`), *ShadowH2O Ransomware Staging Note* eller *Kims Auto-Bypass Scripts USB*! |
| `spor_4g_dongle` | Fysisk | `kontrolrummet` | `undersøg 4g-router` eller `frakobl 4g-router` | **Variant A:** Teltonika 4G-router bag SCADA-rack. **Variant B:** Skjult Wi-Fi AP under gulvet. **Variant C:** Uautoriseret RDP/VPN hardware-tunnelboks ved patchpanelet. |
| `spor_opc_leak` | Konfiguration | `kontrolrummet` | Kør `tshark` i Kontrolrummet, `undersøg opc` eller hærd OPC UA. | Dokumenterer åben OPC UA (`SecurityPolicy: None` & `Anonymous`) og evt. stjålet leverandørcertifikat på port 4840. |
| `spor_kim_nattevagt` | Vidneudsagn | `kontrolrummet` | `undersøg scada pc` eller `spørg hans om kim` | SCADA-sessionslog fra kl. `03:14` *(viser enten uautoriseret login over 4G-routeren eller — hvis Kim er synderen — at bruger `KIM_D` selv afviklede `override_all_zones.sh`!)*. |

---

## ⚖️ 8. Kapitel 5: Konfrontation, NIS2-Revision & Bedømmelsesmatrix

Når alle 4 proceszoner er sikret, skifter spillet til **Kapitel 5**, og spilleren kaldes ud til **Hovedindgangen**, hvor **Revisor Kirsten** og **Hans McDonald** venter.

### De 3 Faser i Kapitel 5 ved Hovedindgangen
1. **Fase 1 (Før fremlæggelse):**
   - `[1] 🕵️ Åbn Sagstavlen (Analyser sidste spor og vælg ⭐ Hovedmistænkt)`
   - `[2] ⚖️ Fremlæg efterforskningen og udpeg gerningsmanden for Tilsynet` (`fremlæg sagstavle`)
   - `[3] 🛡️ Gennemse forensisk evidensjournal (Chain of Custody)` (`vis evidens`)
   - `[4] ☕ Tal med driftstekniker Hans McDonald` (`tal med hans`)
2. **Fase 2 (Efter fremlæggelse — klar til dom):**
   - `[1] 📋 Gennemfør afsluttende NIS2-revision og modtag Tilsynets dom` (`revisor`)
   - `[2] 🕵️ Åbn Sagstavlen (Skift hovedmistænkt hvis nødvendigt)`
   - `[3] 📑 Eksporter officiel NIS2 revisionsrapport (Markdown)` (`eksporter rapport`)
   - `[4] 🏠 Afslut til Hovedmenuen` (`hovedmenu`)
3. **Fase 3 (Efter afsagt dom):**
   - Eksportér portfoliorapporten (`NIS2_Audit_Rapport_NordicH2O.md`) og vend tilbage til Hovedmenuen.

### Revisor Kirstens NIS2 Point- & Compliance-Matrix (`IncidentManager.evaluate_compliance`)
For at **bestå NIS2-auditten** kræves en samlet score på **mindst 80 ud af 100 point** samt **0 aktive kritiske driftsfejl** (`flaws`):

| Revisionspunkt (NIS2 & IEC 62443) | Krav / Handling i Spillet | Point-bidrag / Straf |
| :--- | :--- | :--- |
| **Zone 1 Conduit & VFD Sikring (Art. 21.2.e)** | `chapter-1-done` (Pumpehuset sikret med SCALANCE S615) | **+15 point** |
| **Zone 2 Layer 2 MRP & Port Security (Art. 21.2.e)** | `chapter-2-done` (Ventil-øen sikret med SCALANCE XB-200) | **+15 point** |
| **Zone 3 S7-1500 PLC Hardening (Art. 21.2.e)** | `chapter-3-done` (El-tavlen sikret med Protection Level 3) | **+15 point** |
| **Backup Management (Art. 21.2.c)** | `backup-taken` (Krypteret offline USB-backup af PLC) | **+10 point** |
| **Zone 4 IDMZ & OPC UA Kryptografi (Art. 21.2.h/i)** | `opc-hardened` (Trusted X.509, `Basic256Sha256`, ingen `Anonymous`, bagdør fjernet) | **+15 point** |
| **24-Timers Early Warning (Art. 23.2)** | `indberet hændelse` indsendt inden 24 simulerede arbejdstimer (Dag 1–3) | **+15 point** *(Kun +5 point hvis indsendt for sent efter 24 timer)* |
| **Retsmedicinsk Beviskæde (Art. 21.2.b & ISO 27037)** | `pi_handling_state == "secured"` (Faraday-pose + SHA-256 hash) | **+15 point** *(Hvis smidt ud: **-25 point**; hvis genbrugt/SD-kort i PC: **-30 point**)* |
| **Aktive Driftsfejl ved Audit (`flaws`)** | Hvis K1 er udløst, SCADA er blind, PLC er i Defective Stop, eller port 4840 er blokeret | **-15 point pr. uløst fejl** (og auditten kan ikke bestås før fejlen er rettet) |

---

## 💻 9. Komplet Liste over Terminalkommandoer & `tshark`-Syntaks

Spillet kan gennemføres 100 % med musen via knapperne, 100 % via tastaturet i terminalen, eller som en kombination:

```text
# ── NAVIGATION & INTERAKTION ──────────────────────────────────────────────────
1 .. 8                                       # Udfør handling nr. [1]-[8] fra handlingspanelet
gå til <zone>                                # Skift rum (indgangen, pumpehuset, ventil-oen, el-tavlen, kontrolrummet)
undersøg <emne>                              # Inspicér komponent (pumpe 2, kabelbakke, usb, scada pc, skilt m.fl.)
tal med hans / tal med kirsten               # Tal med driftstekniker Hans eller Revisor Kirsten
spørg hans om <emne>                         # Afhør Hans om: morten, lars, kim, 4g, pi, modbus, nis2, stuxnet
ring til kirsten                             # Få en foreløbig NIS2-status fra Tilsynet undervejs i ugen
techsupport                                  # Ring til TechSupport for et hint (maks. 3 gange pr. spil)

# ── AUTENTISK TSHARK NETVÆRKSANALYSE ──────────────────────────────────────────
tshark                                       # Fang alle pakker på den aktuelle zones VLAN
tshark -Y "modbus"                           # Filtrer Modbus TCP trafik
tshark -Y "modbus.func_code == 6"            # Find uautoriserede Modbus Write Single Register pakker
tshark -Y "modbus.func_code == 3"            # Find legitim SCADA Read Holding Registers trafik
tshark -Y "pn_dcp"                           # Filtrer PROFINET DCP navne-spoofing
tshark -Y "b8:27:eb"                         # Filtrer på Raspberry Pi / implantat MAC-præfiks
tshark -Y "s7comm"                           # Filtrer Siemens S7comm trafik på TCP port 102
tshark -Y "opcua"                            # Filtrer OPC UA trafik på TCP port 4840
tshark -V                                    # Fuld OSI-lags protokol-dissekering af alle felter
tshark -c 2                                  # Stop capture efter 2 pakker
tshark -T fields -e ip.src -e ip.dst         # Udtræk specifikke kilde- og destinationsfelter
man tshark / cheat tshark                    # Vis indbygget OT tshark-manual og filter-oversigt

# ── TEKNISK HÆRDNING & WORKBENCH-KOMMANDOER ───────────────────────────────────
firewall workbench                           # Åbn TS35 DIN-skinne arbejdsbænken i Pumpehuset
monter scalance på din-skinne                # Trin 1/3: Fastgør SCALANCE S615 på DIN-skinnen
kobl kabler til scalance                     # Trin 2/3: Kobl VFD til LAN P1 og anlæg til WAN P5
firewall rule add --allow-fc 3 --drop-fc 6   # Trin 3/3: Aktivér DPI-regel (tillad FC 03, drop FC 06)
firewall status                              # Vis SCALANCE S615 regeltabel og status
sikr pi i faraday-pose                       # Isolér fundet implantat forensisk med SHA-256 hash
udskift switch med scalance                  # Monter SCALANCE XB-200 med PROFINET MRP-ring
tag offline backup                           # Gem krypteret offline USB-backup af S7-1500 PLC
konfigurer tia portal                        # Hærd S7-1500 PLC (Protection Level 3 & luk sårbarhed)
frakobl 4g-router                            # Fjern uautoriseret fjernadgang i Kontrolrummet / IDMZ
godkend scada certifikat                     # Flyt WinCC SCADA X.509 certifikat til Trusted
aktiver opc kryptering                       # Aktivér Basic256Sha256 & SignAndEncrypt på port 4840
deaktiver anonymous opc                      # Slå Anonymous login fra og håndhæv RBAC/MFA

# ── EFTERFORSKNING, COMPLIANCE & SYSTEM ───────────────────────────────────────
sagstavle                                    # Åbn Efterforskningens Sagstavle
spor                                         # Vis liste over alle opdagede spor
analyser spor <spor_id>                      # Analysér et spor og kobl det til mistænkte på Sagstavlen
mistænkte                                    # Vis alle 5 mistænkte-profiler og mistanke-score
anklag <mistænkt_id>                         # Vælg din ⭐ Hovedmistænkt på Sagstavlen
fremlæg sagstavle                            # Fremlæg sagen for Tilsynet i Kapitel 5
indberet hændelse                            # Indsend lovpligtig NIS2 24-timers Early Warning (Art. 23)
vis evidens                                  # Vis Chain of Custody logbog med SHA-256 hashes
revisor                                      # Gennemfør den afsluttende NIS2-audit i Kapitel 5
eksporter rapport                            # Eksportér 'NIS2_Audit_Rapport_NordicH2O.md'
tilstand                                     # Skift mellem Teach Mode og Eksamens-Mode
gem / gem <navn>                             # Gem aktuel spiltilstand i 'saves/'
hent / gemte spil                            # Indlæs gemt spil eller vis liste over gemte spil
hovedmenu                                    # Vend tilbage til startskærmen
```

---

## 🧪 10. Kodearkitektur & Automatiserede Test-Suiter

Projektet er opdelt i modulære pakker uden eksterne afhængigheder:
- [`core/engine.py`](./core/engine.py) — Central `GameEngine` med kampagne-randomisering, tilstandsstyring, timere, JSON-persistens og rapporteksport.
- [`core/investigation.py`](./core/investigation.py) — `InvestigationManager` med dynamisk synder-konfiguration (`configure_dynamic_case`), 2-trins spor-analyse og Sagstavle-formatering.
- [`core/terminal_engine.py`](./core/terminal_engine.py) — `TSharkEngine` med dynamisk pakkegenerering for alle rum-varianter (`A`, `B`, `C`).
- [`core/forensics.py`](./core/forensics.py) & [`core/incident.py`](./core/incident.py) — Chain of Custody, SHA-256 hashing og NIS2 Artikel 21/23 audit-evaluering.
- [`rooms/`](./rooms/) — [`indgangen.py`](./rooms/indgangen.py), [`pumpehuset.py`](./rooms/pumpehuset.py), [`ventil_oen.py`](./rooms/ventil_oen.py), [`el_tavlen.py`](./rooms/el_tavlen.py), [`kontrolrummet.py`](./rooms/kontrolrummet.py).
- [`dialogues/`](./dialogues/) — [`hans.py`](./dialogues/hans.py) og [`kirsten.py`](./dialogues/kirsten.py).
- [`gui/`](./gui/) — [`app.py`](./gui/app.py), [`canvas.py`](./gui/canvas.py) og [`terminal.py`](./gui/terminal.py).

### Kør de 3 automatiserede test-suiter

```powershell
# 1. Kompilerings-validering af alle 34 Python-filer
python test_compilation.py

# 2. 16 dybdegående mekanik-tests (tester alle rum, A/B/C varianter, alle 4 syndere, Teach/Exam mode, Tutorial og Save/Load)
python test_game_mechanics.py

# 3. Automatiseret GUI-integrationstest (tester startskærm, 3-trins workbench, Sagstavle-klik, HUD og terminal)
python test_gui_app.py
```
