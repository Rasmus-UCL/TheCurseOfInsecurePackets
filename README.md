# The Curse of Insecure Packets – Et Interaktivt OT-Cybersecurity & Forensisk Efterforskningsspil

En spilbar, atmosfærisk point-and-click cybersikkerheds- og efterforskningssimulation udviklet til studerende og undervisere på **UCL Erhvervsakademi og Professionshøjskole** (Automationsteknolog, IT-Teknologi og PBA i Cybersikkerhed). Spillet er skrevet i **100 % ren Python standardbibliotek** (`tkinter`, `json`, `hashlib`, `shlex`, `dataclasses`) uden eksterne pakker eller `pip`-afhængigheder.

Spillet kombinerer **praktisk industriel netværkssikkerhed (OT/ICS)** med **aktiv kriminologisk efterforskning**: Som tilkaldt Lead OT-Cybersikkerhedskonsulent på drikkevandsværket **Nordic H2O Utility** har du 5 simulerede arbejdsdage til at afværge fysiske nedbrud i anlæggets fire proceszoner, sikre digital og fysisk evidens efter **NIS2-direktivet (EU 2022/2555)** og **IEC 62443**, analysere tekniske spor på **Sagstavlen** og udpege den sande gerningsmand over for **Miljø- og Cybersikkerhedstilsynet**.

---

## 🌟 Nye Hovedfunktioner (Etape 1 & Etape 2 Redesign)

1. **🎬 Startskærm, Hovedmenu & Fuld Gem/Hent-funktionalitet (`saves/`):**
   - Dedikeret startskærm før spillet går i gang med 4 faner: **🚀 Nyt Spil**, **📂 Indlæs Gemt Spil**, **📖 Om Spillet & Lore** og **❌ Afslut**.
   - Vælg spillerprofil, uddannelse, **Teach Mode vs. Eksamens-Mode** samt om spillet skal starte med **Intro-Tutorial**.
   - Gem når som helst undervejs via knappen `💾 Gem` eller terminalkommandoen `gem` / `gem <filnavn>`, og vend altid tilbage til hovedmenuen via `🏠 Menu` eller kommandoen `hovedmenu`.
2. **🎓 Interaktiv 5-trins Intro-Tutorial (Kapitel 0 — Sikkerhedsgodkendelse hos Hans):**
   - Inden nedtællingsuret starter, guider senior driftstekniker **Hans McDonald** nye spillere gennem et 60-sekunders udstyrstjek ved Hovedindgangen (med timeren sat på pause):
     1. *Inspektion af rum & klikbare 2D-hotspots* (`undersøg skilt`).
     2. *Netværkssniffing i terminalen* (`tshark` eller `🦈 Kør tshark CLI`-knappen).
     3. *Åbning af Efterforskningens Sagstavle* (`🕵️ Sagstavle`).
     4. *2-trins bevisanalyse* (`analyser spor <id>`) og *udpegning af foreløbig hovedmistænkt* (`anklag <id>`).
     5. *Gennemgang af de 4 nøglemetrikker* og overgang til Kapitel 1.
3. **🔀 Automatisk Tilfældig Missionsrækkefølge (Høj Genspilningsværdi):**
   - Spilleren vælger **ikke** selv rækkefølgen af missionerne. Ved start af et nyt spil blander [`GameEngine.randomize_campaign()`](./core/engine.py) automatisk rækkefølgen af de 4 proceszoner (`Pumpehuset`, `Ventil-øen`, `Hoved-el-tavlen`, `Kontrolrummet`), mens **Kapitel 5-finalen med Revisor Kirsten ved `Hovedindgangen` altid ligger til sidst**, når alle 4 zoner er sikret.
   - Hans McDonald kalder automatisk over radioen og dirigerer spilleren til den næste akutte zone, som samtidig fremhæves med `📍` i top-navigationen.
4. **⚡ 3 Forskellige Tekniske Angrebs-Variationer (`A`, `B`, `C`) i Hver Zone:**
   - Hver af de 4 zoner trækker tilfældigt ét af **3 forskellige tekniske angrebsscenarier** (i alt $3^4 = 81$ mulige tekniske kombinationer). Det er f.eks. ikke altid et Modbus-angreb i Pumpehuset!
   - Både rum-beskrivelser, `tshark`-pakker, arbejdsbænke og forensiske spor tilpasser sig automatisk den aktive variant.
5. **🕵️ Dynamisk Synder & 2-Trins Bevisanalyse på Sagstavlen:**
   - Bagmanden bag angrebet udvælges dynamisk ved spilstart blandt **4 mulige hovedmistænkte** (`lars_ex_tekniker`, `morten_pumper`, `apt_shadowh2o`, `kim_operatoer`).
   - Nye spor starter som **`⚠️ NYT SPOR (Uanalyseret)`** og afslører først deres sammenhæng med de mistænkte, når den studerende aktivt klikker på sporet på Sagstavlen (eller skriver `analyser spor <id>`).
6. **🛑 Nul Spoilers i Valgmuligheder & Autentisk Hans-Mentor i Teach Mode:**
   - Alle tekster som `(Faldgrube)` og `(Fælde)` er fjernet fra valgknapperne i både Teach Mode og Eksamens-Mode, så den studerende altid skal tænke selv.
   - **I Teach Mode:** Hvis spilleren vælger en farlig eller forkert handling, griber Hans McDonald ind, **stopper handlingen før skaden sker**, og forklarer pædagogisk *hvorfor* det er farligt med direkte henvisning til **NIS2 Artikel 21/23** og **IEC 62443**.
   - **I Eksamens-Mode:** Hans griber **ikke** ind — han nøjes med en tør bemærkning (*"Det dér havde jeg nok ikke gjort, konsulent..."*), hvorefter den fulde fysiske og driftstekniske konsekvens udløses.

---

## 🚀 Sådan Starter Du Spillet

### Grafisk Cockpit (Anbefalet)

Kør fra projektmappen i PowerShell eller kommandoprompt:

```powershell
python .\game.py
```

### Ren Tekstterminal (Headless / CLI)

```powershell
python .\game.py --cli
```

---

## 🖥️ Gennemgang af Brugerfladen (Fast 1180×840 Cockpit)

Vinduet er låst i en stabil `1180x840` arkitektur med faste panelhøjder, så terminalen og kommandoprompten **aldrig** forsvinder eller skubbes ud af billedet:

1. **Top Header & Purdue Zone-Navigator:**
   - Viser aktuel arbejdsdag (`Dag 1–5, time 1–8`), nedtælling til Tilsynets audit samt eventuelle akutte sprængnings- eller kavitationsalarmer.
   - Hurtigknapper til alle 5 zoner (`🚪 Indgangen`, `🚰 Pumpehuset`, `💨 Ventil-øen`, `⚡ El-tavlen`, `🖥️ Kontrolrummet`), hvor den aktuelle missionszone er markeret med `📍`.
   - Indeholder desuden knapper til tilstandsskift (`🎓 Tilstand: TEACH / EKSAMEN`), `💾 Gem` og `🏠 Menu`.
2. **4-Metrik HUD & Værktøjslinje:**
   - Realtidsvisning af de 4 modstridende anlægsmetrikker:
     - **🔧 Drift (0–100 %):** Vandværkets oppetid, vandtryk og fysiske integritet.
     - **🛡️ Sikkerhed (0–100 %):** IEC 62443 segmentering, conduits, PLC-hærdning og OPC UA PKI.
     - **📜 Compliance (0–100 %):** Overholdelse af NIS2 Artikel 21 & 23, 24-timers Early Warning og retsmedicinsk beviskæde.
     - **🤝 Tillid (0–100 %):** Samarbejdet med senior driftstekniker Hans McDonald og ledelsen.
   - Knapper til **`🕵️ Sagstavle`** (lyser orange ved nye uanalyserede spor!), **`🦈 Kør tshark CLI`** og en tydelig blå **`📞 TechSupport (3/3)`**-knap.
3. **2D Interaktiv Visuel Skærm (`GameCanvas` — fast 310px højde):**
   - **Rum-visning:** Viser animerede pumper, manometre, rørføringer og **stiplede hotspots**, som kan klikkes direkte med musen.
   - **DIN-Skinne Arbejdsbænk (`vfd_workbench`):** Trin-for-trin montering og kabling af SCALANCE S615 sikkerhedsrouteren.
   - **Sagstavle (`clue_board`):** Interaktivt kriminalteknisk overblik, hvor du kan klikke direkte på **Mistænkte** til venstre (for at vælge `⭐ Hovedmistænkt`) og **Spor-kort** til højre (for at køre dybdeanalyse).
4. **Klikbart Handlingspanel (`⚡ HANDLINGER I ZONEN`):**
   - Viser op til 8 kontekstafhængige handlinger som tydelige knapper i 2 kolonner lige over terminalen.
   - Hver gang du vælger en handling, ryddes terminalvisningen for gammel tekst, så du kun læser det aktuelle respons-afsnit fra toppen.
5. **Integreret CRT-Terminal (`TerminalWidget`) med Fastlåst Bund-Prompt:**
   - Understøtter både klik, tal-genveje (`1`–`8`) og autentiske CLI-kommandoer (`tshark`, `firewall rule add ...`, `analyser spor ...`, `anklag ...`) med `Tab`-autofuldførelse og kommandohistorik (`Pil Op`/`Pil Ned`).

---

## 🗺️ Grundig Gennemgang af Spillets Zoner & De 3 Angrebs-Variationer pr. Rum

Efter **Kapitel 0 (Intro-Tutorial)** ved Hovedindgangen gennemspilles de **4 proceszoner i en tilfældigt genereret rækkefølge** (Kapitel 1–4). I hver zone møder den studerende én af **3 mulige tekniske udfordringer**:

---

### 🚰 Zone: Pumpehuset (Purdue Level 1 — VFD & Procespumper)
Pumpe 2 kører med livsfarligt overtryk (14.8 Bar på vej mod 150 Bar i hovedledningen) og voldsom kavitation. Foran SINAMICS G120 frekvensomformeren sidder en 35mm TS35 DIN-skinne, hvor spilleren skal gennemføre en **sekventiel 3-trins arbejdsbænk**:
- **Trin 1/3:** Fastgør `SCALANCE S615` sikkerhedsrouteren fysisk på DIN-skinnen.
- **Trin 2/3:** Kobl kablerne efter **IEC 62443 Zone & Conduit-princippet** (VFD på beskyttet intern **LAN Port P1** og anlægs-uplink på ekstern **WAN Port P5**).
- **Trin 3/3:** Konfigurér pakkefilteret efter den aktive angrebsvariant (husk altid at tillade SCADA-telemetri `FC 03`, så kontrolrummet ikke bliver blindt!):

| Variant | Angrebsvektor & Protokol | Hvad viser `tshark`? | Korrekt Teknisk Løsning |
| :--- | :--- | :--- | :--- |
| **Variant A** | **Modbus TCP Register Flood (TCP Port 502)** | Uautoriseret vært sender `FC 06 Write Single Register (0x0000 = 1337)` hvert 20. ms. | Aktivér L7 Modbus Deep Packet Inspection: `firewall rule add --allow-fc 3 --drop-fc 6` |
| **Variant B** | **SNMPv1 Default Community (`private`) & ARP-Poisoning (UDP Port 161)** | *Ikke et Modbus-angreb!* Angriberen bruger ARP-spoofing og `SNMPv1 SetRequest (community='private')` til at tvinge VFD'ens interne maks-frekvens op på 120 Hz. | Spær SNMPv1 Write (`private`), aktivér Dynamic ARP Inspection (DAI) på SCALANCE S615 og tillad SCADA `FC 03`. |
| **Variant C** | **Ubeskyttet VFD HTTP-Webserver (`admin/admin` på TCP Port 80)** | *Ikke et Modbus-angreb!* `HTTP POST /api/vfd/override` med Basic Auth `admin:admin` låser VFD'en i 120 Hz manuel tvangsdrift. | Spær ukrypteret HTTP Port 80 i SCALANCE S615, lås setpunkt-kilden tilbage til PLC-feltbussen og tillad SCADA `FC 03`. |

> **Typiske fejl (som Hans stopper i Teach Mode, men som udløser ulykker i Eksamens-Mode):**
> - *Hård nødnedlukning af VFD under fuld last:* Skaber et destruktivt hydraulisk vandslag, der sprænger sikkerhedsrelæ **K1** i Hoved-el-tavlen!
> - *Rå blokering af Port 502 eller Drop uden `--allow-fc 3`:* Gør WinCC SCADA i Kontrolrummet totalt blind (`SCADA BLIND / TIMEOUT`).

---

### 💨 Zone: Ventil-øen (Purdue Level 1 — Decentralt I/O & Layer 2 Feltbus)
De pneumatiske Festo-ventiler og Siemens ET 200SP I/O-moduler klaprer kaotisk, mens en billig, uadministreret D-Link plast-switch blinker hysterisk. Bag stålrammen løber **kabelbakke K-04**.
- **Trin 1:** Undersøg kabelbakken (`undersøg kabelbakke`) og kør `tshark` for at afsløre det skjulte hardware-implantat.
- **Trin 2 (Retsmedicinsk Dilemma — NIS2 Art. 21.2.b & ISO/IEC 27037):** Isolér det fremmede hardware i en **antistatisk Faraday-pose** og log SHA-256 hash + plomberingsnummer (`sikr pi i faraday-pose`). *(At smide det i skraldespanden destruerer beviser; at sætte SD-kortet i egen laptop inficerer konsulent-PC'en!).*
- **Trin 3:** Udskift D-Link switchen med en industriel **Siemens SCALANCE XB-200 managed switch** med Port Security og **PROFINET MRP-ring** (`udskift switch med scalance`).

| Variant | Fysisk Implantat & Layer 2/IIoT Sabotage | Hvad viser `tshark`? |
| :--- | :--- | :--- |
| **Variant A** | **Rogue Raspberry Pi 4 med PROFINET DCP Name-Spoofing** | `PN-DCP Set NameOfStation='rogue-io'` og ARP-poisoning fra MAC OUI `b8:27:eb:d4:11:22`. |
| **Variant B** | **Skjult Aktiv LAN-Tap i ventil-klemkassen med IEEE 802.1Q Priority-Stripping** | Stripper `802.1Q Priority 6` QoS-tags fra PROFINET RT-pakker og udsender falske `LLDP`-nabopakker. |
| **Variant C** | **Uautoriseret ESP32/MQTT-Bro med ukrypteret MQTT-storm (TCP Port 1883)** | Oversvømmer smart-ventilerne med uautentificerede `MQTT PUBLISH nordic/valves/all/set = OSCILLATE_MAX`. |

---

### ⚡ Zone: Hoved-el-tavlen (Purdue Level 1/2 — Sikkerheds-PLC & TIA Portal)
Vandværkets centrale **Siemens S7-1500 Fail-Safe PLC (CPU 1516F)** står med blinkende rød `STOP`-diode, og i tavlens dokumentlomme ligger et efterladt USB-stik med vigtige spor.
- **Trin 1 (NIS2 Art. 21.2.c Backup-krav):** Tag altid en **krypteret offline USB-backup** af CPU 1516F og kalibreringsblok `DB1` (`tag offline backup`), *før* du skriver ændringer til PLC'en!
- **Trin 2:** Gennemfør sikkerhedshærdningen i **TIA Portal** (`konfigurer tia portal`):

| Variant | Angrebsvektor mod S7-1500 PLC | Hvad viser `tshark` & Diagnostic Buffer? | Hærdning i TIA Portal |
| :--- | :--- | :--- | :--- |
| **Variant A** | **Uautoriseret S7comm PUT/GET Blok-overskrivning (TCP Port 102)** | `S7comm Write Variable (PUT til DB1.DBX0.0)` korrumperer sikkerheds-checksummen (`0x8104`). | Deaktivér *Permit access with PUT/GET* og aktivér **Protection Level 3** (kodeordsbeskyttet). |
| **Variant B** | **Manipuleret F-Safety Watchdog i OB35 (`0x75E1`)** | Cyklustiden i `OB35` er ændret til `500 ms` (maks. grænse `100 ms`) uden Safety-adgangskode. | Gendan `OB35` (100 ms), kompilér F-Safety signatur og aktivér **Protection Level 3**. |
| **Variant C** | **NTP Time-Spoofing (UDP Port 123) & TLS Certifikat-svigt** | Falske NTP-pakker stiller PLC-uret tilbage til `1970-01-01`, så CPU'ens X.509/TLS-certifikater fejler. | Lås NTP-synkronisering til autentificeret GPS-tidsserver (`SHA-256`) og aktivér **Protection Level 3**. |

> **De 4 klassiske ingeniør-fælder i El-tavlen:**
> 1. *Konfigurér TIA Portal uden forudgående offline backup:* Et netværksudfald under overførslen korrumperer `DB1` og låser PLC'en i `0x4542 DEFECTIVE STOP`.
> 2. *Tving CPU i RUN med nøglekontakten:* Angriberens loop overskriver straks PLC'en igen.
> 3. *Blokér hele TCP Port 102 i celle-firewallen:* Kapper den vitale **PROFIsafe**-kommunikation til nødstop-modulerne og udløser total **F-I/O passivering (EN ISO 13849)**.
> 4. *Live uverificeret firmware-opdatering over kompromitteret netværk:* Udløser Supply Chain / MitM-fejl og låser CPU'ens bootloader.

---

### 🖥️ Zone: Kontrolrummet / IDMZ (Purdue Level 3.5 — SCADA & OPC UA PKI)
I Kontrolrummet og Industrial DMZ (IDMZ) er der både etableret en **ulovlig fysisk bagdør** uden om perimeter-firewallen, og **OPC UA-serveren på TCP port 4840** lækker procesdata i klartekst. For at sikre zonen skal spilleren gennemføre **4 hærdningstrin** (uden at blokere port 4840 råt, da det afbryder lovpligtig miljølogning til Miljøstyrelsen):
1. **Fjern den fysiske bagdør** (`frakobl 4g-router`).
2. **PKI Truststore:** Flyt WinCC SCADA-klientens X.509-certifikat fra `Rejected` til `Trusted` (`godkend scada certifikat`).
3. **Kryptografi (NIS2 Art. 21.2.h):** Sæt OPC UA SecurityPolicy til `Basic256Sha256` og tilstand til `SignAndEncrypt` (`aktiver opc kryptering`).
4. **Adgangskontrol & MFA (NIS2 Art. 21.2.i/j):** Deaktivér `Anonymous` UserTokenType og håndhæv RBAC/MFA (`deaktiver anonymous opc`).

| Variant | Fysisk IDMZ-Bagdør & OPC UA Sårbarhed | Hvad viser `tshark`? |
| :--- | :--- | :--- |
| **Variant A** | **Teltonika RUT950 4G-Router bag SCADA-racket + Åben OPC UA** | Indgående VPN-trafik fra 4G-routeren samt `OpenSecureChannel: SecurityPolicy='None'` & `Anonymous`. |
| **Variant B** | **Skjult Wi-Fi Access Point under gulvet ved patchpanelet + Stjålet Leverandør-Certifikat** | Trådløs trafik fra parkeringspladsen med kompromitteret leverandør-certifikat og `SecurityPolicy='None'`. |
| **Variant C** | **Uautoriseret RDP/VPN Hardware-Tunnelboks (TCP Port 3389 uden MFA) + Åben OPC UA** | Direkte Remote Desktop (`TCP 3389`) uden Multi-Factor Authentication kombineret med ukrypteret OPC UA. |

---

## 🕵️ Efterforskningen, Sagstavlen & De 4 Dynamiske Syndere

Sideløbende med den tekniske brandslukning skal spilleren finde ud af, **hvem der står bag angrebet**. Ved start af et nyt spil udpeger [`InvestigationManager.configure_dynamic_case()`](./core/investigation.py) én af følgende **4 mistænkte** som gennemspilningens sande bagmand og tilpasser de forensiske spor (USB-stik, kommandologs, netværkssignaturer og vidneudsagn):

| Mistænkt ID | Navn & Rolle | Motiv & Typiske Forensiske Spor når vedkommende er Synderen |
| :--- | :--- | :--- |
| `lars_ex_tekniker` | **Lars Kofoed** — Tidligere OT-Automationstekniker (fyret for 2 mdr. siden) | **Hævnaktion efter fyring:** Efterladt USB-stik mærket `'LARS - TIA V16 BACKUP'`, bruger-ID `LKO_ENG` i kompilerede scripts, eksakt kendskab til `DB1` og udnyttelse af gammel nøglebrik. |
| `morten_pumper` | **Morten Vestergaard** — Ekstern Pumpe-ingeniør (*Hydropump Nordic A/S*) | **Supply Chain Sabotage:** Besøgte alle 4 zoner alene tirsdag; rød leverandør-USB (`HYDROPUMP NORDIC - SERVICE DIAG V4`) med `pump_stress_induce.py`; inventarmærke under kabelbakken og et mistænkeligt tilbud på 1,8 mio. kr. for en akut 24/7-servicekontrakt dagen efter! |
| `apt_shadowh2o` | **ShadowH2O / DarkVolt Syndikatet** — Ekstern Cyberkriminel APT-gruppe | **Ransomware & Afpresning mod Kritisk Infrastruktur:** Krypterede C2-beacons til ekstern Tor-relay gennem den uautoriserede fjernadgang i Kontrolrummet samt droppet staging-note (`SHADOWH2O_README.TXT`) i El-tavlen, der matcher Europol-signaturer. |
| `kim_operatoer` | **Kim Dahl** — Intern Procesoperatør (Natholdet) | **Panisk Dækmanøvre efter Fejlbetjening:** Satte ulovlig fjernadgang op af magelighed, men kørte kl. `03:14` hjemmelavede bypass-scripts (`override_all_zones.sh`) fra sin personlige USB-nøgle for at skjule en farlig driftsfejl fra torsdag nat! |

### Sådan gennemføres Kapitel 5 (Den Store Konfrontation ved Hovedindgangen)
Når alle 4 proceszoner er sikret, ankommer **Chefinspektør Kirsten** fra Miljø- og Cybersikkerhedstilsynet ved `Hovedindgangen`. Finalen er opdelt i **3 overskuelige trin**:
1. **Åbn Sagstavlen (`sagstavle`):** Klik på alle fundne spor til højre for at analysere dem (`✅ ANALYSERET`), se hvem der har den højeste mistanke-score og flest knyttede beviser, og klik på vedkommende til venstre for at udpege din **`⭐ Hovedmistænkt`**.
2. **Fremlæg efterforskningen (`fremlæg sagstavle`):** Konfrontér Tilsynet og Hans med din anklage og dine tekniske beviser.
3. **Modtag NIS2 Audit-Dommen & Eksportér Rapport (`revisor` / `eksporter rapport`):** Kirsten evaluerer anlæggets 4 metrikker, 24-timers Early Warning (`indberet hændelse`) og Chain of Custody (`vis evidens`), og spillet genererer en komplet **Markdown-revisionsrapport** (`NIS2_Audit_Rapport_NordicH2O.md`) lige til den studerendes UCL-studieportfolio!

---

## 🦈 Oversigt over `tshark` & Terminalkommandoer

```text
# Netværkssniffing & Protokol-dissekering
tshark                                       # Fang pakker på den aktuelle zones VLAN
tshark -Y "modbus"                           # Filtrer Modbus TCP trafik
tshark -Y "modbus.func_code == 6"            # Find uautoriserede Modbus Write-kald
tshark -Y "pn_dcp"                           # Find PROFINET DCP navne-spoofing
tshark -Y "s7comm"                           # Filtrer Siemens S7comm trafik på port 102
tshark -Y "opcua"                            # Filtrer OPC UA trafik på port 4840
tshark -V                                    # Vis fuld OSI-lags pakkedissekering
man tshark                                   # Vis indbygget OT tshark-manual

# Efterforskning & Sagstavle
sagstavle                                    # Åbn den visuelle og tekstbaserede Sagstavle
spor                                         # Vis liste over fundne spor
analyser spor <spor_id>                      # Udfør dybdeanalyse og kobl sporet til mistænkte
mistænkte                                    # Vis profiler på alle mistænkte
anklag <mistænkt_id>                         # Udpeg din ⭐ Hovedmistænkt på Sagstavlen
fremlæg sagstavle                            # Fremlæg sagen for Tilsynet i Kapitel 5

# NIS2 Compliance, System & Spilstyring
indberet hændelse                            # Indsend lovpligtig 24-timers NIS2 Early Warning (Art. 23)
vis evidens                                  # Vis forensisk Chain of Custody logbog (SHA-256)
eksporter rapport                            # Eksportér NIS2_Audit_Rapport_NordicH2O.md
tilstand                                     # Skift mellem Teach Mode og Eksamens-Mode
gem / hent                                   # Hurtig-gem eller indlæs spil fra saves/
hovedmenu                                    # Vend tilbage til startskærmen
```

---

## 🏗️ Modulær Kodearkitektur

- [`game.py`](./game.py) — Entrypoint til både grafisk Tkinter-cockpit og `--cli` tilstand.
- [`models.py`](./models.py) — Datamodeller for `Player`, `MetricValues`, `Clue`, `Suspect` og `OBJECTIVES`.
- [`core/`](./core/)
  - [`engine.py`](./core/engine.py) — `GameEngine`: Orkestrerer tilfældig missionsrækkefølge, rum-varianter (`A/B/C`), Teach/Exam mentor-logik, timere, JSON save/load og NIS2-rapporteksport.
  - [`investigation.py`](./core/investigation.py) — `InvestigationManager`: Styrer Sagstavlen, 2-trins bevisanalyse og dynamisk konfiguration af spor og gerningsmand (`configure_dynamic_case`).
  - [`terminal_engine.py`](./core/terminal_engine.py) — `TSharkEngine` & `AutocompleteHelper`: Realistisk netværkssniffer med pakker tilpasset rum-variant `A`, `B` og `C`.
  - [`forensics.py`](./core/forensics.py) — `ForensicsManager`: Faraday-pose håndtering, SHA-256 hashing og plomberingslog.
  - [`incident.py`](./core/incident.py) — `IncidentManager`: NIS2 Artikel 21 & 23 evaluering.
  - [`purdue.py`](./core/purdue.py) — Purdue Level 0–4 arkitektur og IEC 62443 Security Levels.
- [`rooms/`](./rooms/) — [`indgangen.py`](./rooms/indgangen.py), [`pumpehuset.py`](./rooms/pumpehuset.py), [`ventil_oen.py`](./rooms/ventil_oen.py), [`el_tavlen.py`](./rooms/el_tavlen.py), [`kontrolrummet.py`](./rooms/kontrolrummet.py).
- [`dialogues/`](./dialogues/) — [`hans.py`](./dialogues/hans.py) (Hans McDonald) og [`kirsten.py`](./dialogues/kirsten.py) (Revisor Kirsten).
- [`gui/`](./gui/) — [`app.py`](./gui/app.py) (`GameApp` med startskærm, fast 1180×840 layout og klikbart handlingspanel), [`canvas.py`](./gui/canvas.py) (`GameCanvas` med interaktive hotspots, DIN-skinne arbejdsbænk og klikbar Sagstavle) og [`terminal.py`](./gui/terminal.py) (`TerminalWidget`).

---

## 🧪 Automatiserede Tests & Kvalitetssikring

Projektet indeholder tre komplette test-suiter, som kan køres direkte med standard Python:

```powershell
# 1. Kompilerings-tjek af samtlige 34 Python-filer
python test_compilation.py

# 2. 16 dybdegående mekanik-tests (Teach/Exam mode, Tutorial, Sagstavle, Save/Load, A/B/C varianter & alle 4 syndere)
python test_game_mechanics.py

# 3. Automatiseret GUI-integrationstest (Startskærm, Workbench, Sagstavle-klik, HUD & Terminal)
python test_gui_app.py
```
