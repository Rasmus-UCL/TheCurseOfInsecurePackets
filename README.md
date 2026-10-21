# The Curse of Insecure Packets – Et OT-Cybersecurity Eventyr

En spilbar retro-point-and-click cybersikkerhedssimulation udviklet til studerende og undervisere på UCL (Automationsteknolog, Cybersikkerhed og IT-Teknologi). Spillet er skrevet i 100% ren Python uden eksterne afhængigheder eller pip-pakker.

Spillet er opbygget efter stringente objektorienterede principper (OOP) i en modulær pakkestruktur, der gør det nemt at udvide med nye zoner, industrielle enheder og scenarier:

- [`core/`](./core/):
  - `engine.py`: Central `GameEngine` koordinerende tilstandsmaskine, timere og hændelsesafvikling.
  - `purdue.py`: PERA Level 0-4 arkitektur og IEC 62443 Security Level (SL) definitioner.
  - `forensics.py`: `ForensicsManager`, `EvidenceItem`, SHA-256 integritetscheck og retsmedicinske procedurer for beslaglagt hardware.
  - `incident.py`: `IncidentManager`, NIS2 Artikel 23 (24h Early Warning) og Artikel 21 compliance matrix.
  - `terminal_engine.py`: `WiresharkSniffer` (terminal-baseret pakkefangst, display-filtre og OSI-lags dissektion) samt `AutocompleteHelper`.
- [`devices/`](./devices/): Polymorfe industrielle enheder med tilstand, Purdue-niveau, telemetri og faglige handlinger (`VFDDevice`, `SwitchDevice`, `PLCDevice`, `OpcUaDevice`, `RoguePiDevice`).
- [`rooms/`](./rooms/): Fysiske zoner og Purdue-rum (`IndgangenRoom`, `PumpehusetRoom`, `VentilOenRoom`, `ElTavlenRoom`, `KontrolrummetRoom`).
- [`dialogues/`](./dialogues/):
  - `hans.py`: Hans McDonald (Senior Driftstekniker) med dynamisk situationshukommelse og OT-anekdoter.
  - `kirsten.py`: Revisor Kirsten (Cybersikkerhedstilsynet) med formel NIS2 Artikel 21 audit-evaluering.
- [`gui/`](./gui/):
  - `app.py`: `GameApp` cockpit der samler header, Purdue-zonebar, 2D fabriksgulv og integreret terminal.
  - `canvas.py`: `GameCanvas` 2D-vektorskærm med animerede pumper, manometre, DIN-skinne og switch workbenches.
  - `terminal.py`: `TerminalWidget` integreret Green-on-Black (`#22c55e` på `#050a08`) CRT-terminal med integreret promptlinje, Up/Down kommandohukommelse og Tab-autofuldførelse.
- [`engine.py`](./engine.py): Bagudkompatibel bridge til den modulære kerne.
- [`game.py`](./game.py): Hovedprogram (starter Cockpit GUI som standard, eller CLI med flaget `--cli`).

---

## 🚀 Kør spillet

### Grafisk tilstand (standard)

Fra denne mappe i PowerShell:

```powershell
python .\game.py
```

Eller med virtuelt miljø:

```powershell
& ".\.venv\Scripts\python.exe" ".\game.py"
```

### Tekstbaseret terminalversion (CLI)

```powershell
python .\game.py --cli
```

---

## 🖥️ Brugerflade & Nyt Cockpit-Design

Spillet kombinerer et dedikeret 2D fabriksgulv med en autentisk integreret grøn terminal:

1. **Top Header & Purdue Zoner:**
   - Viser virtuel arbejdsdag (Dag 1-5, time 1-8), audit-nedtælling og akutte alarmer (Kavitation, Pumpe 2 trykalarm).
   - Hurtig navigation mellem zoner: *🚪 Indgangen (L4)*, *🚰 Pumpehuset (L1)*, *💨 Ventil-øen (L1)*, *⚡ El-tavlen (L1/L2)*, *🖥️ Kontrolrummet (IDMZ)*.
2. **Dedikeret 2D Visuel Skærm (Top):**
   - Interaktivt 2D-vektorkort med animerede rørledninger, vibrationsalarmer og hotspots.
   - Indeholder interaktive montageskærme (DIN-skinne montage i Pumpehuset og switch-ombytning i Ventil-øen).
3. **Integreret CRT Terminal (Bund - Grøn på sort):**
   - Autentisk retro-terminal (`#22c55e` tekst på `#050a08` baggrund).
   - Terminalen fungerer som både output-vindue og aktiv kommandolinje via en integreret prompt (`>`).
   - Fuld understøttelse af **både naturlige kommandoer og hurtige talvalg (1-6)**.
   - **Historik:** Bladr i tidligere kørte kommandoer med `Pil Op` og `Pil Ned`.
   - **Autofuldførelse:** Tryk `Tab` for at få vist eller fuldføre faglige OT-kommandoer.

---

## 🦈 Wireshark i Terminalen

Wireshark er flyttet fra den øverste skærm direkte ned i terminalvinduet for en mere autentisk og professionel teknikeroplevelse:

- **Kør live capture:** `åbn wireshark` eller `wireshark`
- **Interaktiv filtrering på protokoller og feltværdier:**
  - `wireshark filter modbus`
  - `wireshark filter modbus.func_code == 6`
  - `wireshark filter dcp`
  - `wireshark filter b8:27:eb` (Rogue Raspberry Pi OUI)
  - `wireshark filter s7` eller `wireshark filter 102`
  - `wireshark filter opc`
- **Dybdegående OSI-lags inspektion:**
  - `wireshark detaljer 1` (Viser Ethernet II, IP, TCP/UDP og applikationslag med forklaring på angrebsvektorer).

---

## 🔍 Skjult Angrebsvektor i Ventil-øen & Forensiske Dilemmaer

- **Skjult boks:** I Ventil-øen er den uautoriserede Raspberry Pi skjult som en ukendt, optapet sort kasse i kabelbakken. Den opdages først, når spilleren undersøger kabelbakken (`undersøg kabelbakke`) eller kører Wireshark med DCP-detektion.
- **Forensiske dilemmaer ved frakobling:**
  - **Option A (Korrekt):** Sikring i antistatisk Faraday-pose (`sikr pi i faraday-pose`). Genererer SHA-256 checksum og opretter journal i Digital Chain of Custody.
  - **Option B (Fælde):** Smid i skraldespanden (`smid pi i skraldespand`). Medfører tab af retsmedicinsk bevis (NIS2 Artikel 21.2.b overtrædelse).
  - **Option C (Fælde):** Gem til privat IoT-projekt (`gem pi til genbrug`). Bagdøren genaktiveres persistent.
  - **Option D (Fælde):** Sæt MicroSD-kort direkte i egen felt-laptop (`sd-kort i laptop`). Ødelægger tidsstempler og inficerer computeren via ubeskyttet autorun.

---

## ⚡ El-tavlen: 5 Forgrenede Ingeniørveje & Systemiske Konsekvenser

I Hoved-el-tavlen (Kapitel 3) skal S7-1500 PLC'en bringes sikkert tilbage fra STOP-mode med fem mulige faglige veje:

1. **Guldstandard (Korrekt):** Tag offline USB-backup (`tag offline backup`), kør TIA Portal Security Wizard for at deaktivere ubeskyttet PUT/GET og aktiver Protection Level 3 (`konfigurer tia portal`).
2. **Forhastet koldstart (Fælde):** Tving CPU i RUN via nøglekontakt uden at lukke sårbarheden (`tving cpu i run`). Angriberens loop fanger opstarten og korrumperer DB1 på port 102 -> kastes i *DEFECTIVE STOP*.
3. **Firewall Overkill (Fælde):** Total blokering af port 102 i cellens firewall (`bloker port 102`). Kapper PROFIsafe-kommunikationen til ET 200SP I/O og udløser øjeblikkelig **F-I/O passivering og nødstop** (IEC 62061 / EN ISO 13849).
4. **Live Firmware-Patch (Fælde):** Opdatering af CPU-firmware live uden SHA-256 validering (`opdater firmware live`). Angriberen udfører MitM og låser bootloaderen (NIS2 Artikel 21.2.e overtrædelse).
5. **Uisoleret Laptop (Fælde):** Tilslutning af bærbar direkte i CPU'ens port under aktivt angreb (`kobl laptop i plc port`). ARP-spoofing kaprer ingeniørsessionen.

---

## 🖥️ Kontrolrummet: Autentisk OPC UA PKI Hardening

I Kontrolrummet (Kapitel 4) konfigureres industriel DMZ (Purdue 3.5) efter IEC 62541 standarden:

- **Fjernelse af Shadow-IT:** Frakobl og konfiskér den uautoriserede Teltonika 4G-router (`frakobl 4g-router`).
- **Certifikat-håndtering (PKI Truststore):** Flyt WinCC SCADA klientens certifikat fra mappen *Rejected* til *Trusted* (`godkend scada certifikat`).
- **Kryptografisk sikkerhed:** Skift SecurityPolicy til `Basic256Sha256` og MessageSecurityMode til `SignAndEncrypt` (`aktiver opc kryptering`).
- **Adgangskontrol:** Deaktivér Anonymous UserTokenType og håndhæv rollebaseret adgangskontrol (RBAC) (`deaktiver anonymous opc`).

---

## 📋 NIS2 Værktøjer & Læringselementer

- **24-timers Early Warning (`indberet hændelse`):** Indsend lovpligtig tidlig advarsel om en væsentlig hændelse til CSIRT / Tilsynet jf. NIS2 Artikel 23.
- **Digital Chain of Custody (`vis evidens`):** Inspicér den elektroniske logbog over beslaglagt udstyr med SHA-256 hashes og plomberingsnumre (NIST SP 800-61).
- **Eksportér NIS2 Audit Rapport (`eksporter rapport`):** Genererer automatisk en formel revisionsrapport i Markdown (`NIS2_Audit_Rapport_NordicH2O.md`) indeholdende Artikel 21 compliance matrix, hændelseslog og auditor-anmærkninger.
- **Hans McDonald Situationsdialog:** Hans reagerer dynamisk på anlæggets tilstande (udløst relæ, blindet SCADA, DEFECTIVE STOP, kavitationsalarm) og fortæller lærerige historier fra sine 30 år i industrien (Stuxnet, SCADA-kælderoversvømmelse, Zoner & Conduits).
