# The Curse of Insecure Packets – Et OT-Cybersecurity Eventyr

En spilbar retro-point-and-click cybersikkerhedssimulation udviklet til studerende og undervisere på UCL Erhvervsakademi og Professionshøjskole (Automationsteknolog, Cybersikkerhed og IT-Teknologi). Spillet er skrevet i 100% ren Python standardbibliotek uden eksterne biblioteker eller pip-afhængigheder.

Spillet simulerer et cyberangreb mod drikkevandsværket **NordicH2O Forsyning**, hvor de studerende skal identificere angrebsvektorer, håndhæve **NIS2-direktivet**, anvende **IEC 62443** zoner og conduits samt sikre industrielle systemer under drift.

---

## 🏗️ Arkitektur & Modulær Pakkestruktur (OOP)

Kildekoden er struktureret som et professionelt objektorienteret system med fuld separation af forretningslogik, hardwaremodeller, netværkssimulering og grafisk præsentation:

- [`core/`](./core/):
  - [`engine.py`](./core/engine.py): Central `GameEngine` orkestrerer tilstande, arbejdsdage, timere, point og overordnede workflows.
  - [`terminal_engine.py`](./core/terminal_engine.py): Autentisk `TSharkEngine` og `WiresharkSniffer` med reel kommandolinje-syntaks (`-Y`, `-V`, `-c`, `-T fields`), protokoldissektering samt dynamisk pakkesimulering baseret på anlæggets aktuelle driftsstatus.
  - [`purdue.py`](./core/purdue.py): PERA Level 0–4 Purdue-modeldefinitioner og IEC 62443 Security Level (SL) validering.
  - [`forensics.py`](./core/forensics.py): `ForensicsManager`, `EvidenceItem`, SHA-256 integritetscheck og retsmedicinsk *Chain of Custody* for beslaglagt hardware.
  - [`incident.py`](./core/incident.py): `IncidentManager`, NIS2 Artikel 23 (24h Early Warning) og Artikel 21 compliance matrix.
- [`devices/`](./devices/): Polymorfe industrielle OT-enheder (`VFDDevice`, `SwitchDevice`, `PLCDevice`, `OpcUaDevice`, `RoguePiDevice`) med hardware-tilstand, registeradresser og I/O.
- [`rooms/`](./rooms/): De fysiske zoner på vandværket:
  - `IndgangenRoom` (Purdue L4)
  - `PumpehusetRoom` (Purdue L1)
  - `VentilOenRoom` (Purdue L1)
  - `ElTavlenRoom` (Purdue L1/L2)
  - `KontrolrummetRoom` (Purdue L3/IDMZ)
- [`dialogues/`](./dialogues/):
  - `hans.py`: Hans McDonald (Senior Driftstekniker) med dynamisk situationshukommelse, anlægsalarmer og industrielle anekdoter.
  - `kirsten.py`: Revisor Kirsten (Cybersikkerhedstilsynet) med formel NIS2 Artikel 21 audit-evaluering.
- [`gui/`](./gui/):
  - `app.py`: `GameApp` cockpit controller, der binder canvas, hændelser og terminal sammen.
  - `canvas.py`: `GameCanvas` 2D-vektorskærm med animerede pumper, trykmålere, DIN-skinne montagebord og switch slots.
  - `terminal.py`: `TerminalWidget` integreret retro CRT-terminal (`#22c55e` på `#050a08`) med direkte kommandoprompt (`>`), historik (`Pil Op`/`Pil Ned`) og `Tab`-autofuldførelse.
- [`models.py`](./models.py): Fælles dataclasser, Purdue-enums og datatyper.
- [`game.py`](./game.py): Hovedprogram der starter spillet.

---

## 🚀 Kør Spillet

### Grafisk Brugerflade (Anbefalet Cockpit)

Fra projektmappen i PowerShell eller terminal:

```powershell
python .\game.py
```

Eller hvis du anvender virtuelt miljø:

```powershell
& ".\.venv\Scripts\python.exe" ".\game.py"
```

### Ren Tekstterminal (Headless / CLI)

```powershell
python .\game.py --cli
```

---

## 🖥️ Brugerflade & Cockpit-Design

Cockpittet er opdelt ergonomisk:

1. **Top Header & Purdue Zone Navigator:**
   - Viser virtuel arbejdsdag (Dag 1–5, time 1–8), audit-nedtælling, anlægsstatus og akutte driftsalarmer.
   - Direkte skift mellem zoner: `🚪 Indgangen`, `🚰 Pumpehuset`, `💨 Ventil-øen`, `⚡ El-tavlen`, `🖥️ Kontrolrummet`.
2. **2D Visuel Procesflade (Canvas):**
   - Viser procesrør, trykmålere, VFD frekvens, SCADA telemetristatus og klikbare DIN-skinne/switch montageborde.
3. **Integreret CRT Terminal (Grøn på sort):**
   - Alt output og input samles i terminalvinduet.
   - Understøtter både hurtige talvalg (`1`, `2`, `3`...) og frie tekstkommandoer.
   - **Tast `Enter`** på en tom linje for øjeblikkeligt at genudskrive de aktuelle valgmuligheder uden at miste overblikket.

---

## 🦈 Autentisk Netværksanalyse med `tshark`

Spillet træner studerende i virkelige netværksværktøjer ved at understøtte autentiske **`tshark`** kommandolinjeargumenter direkte i terminalen:

```text
tshark                                 # Kør standard capture (10 seneste pakker)
tshark -c 5                            # Vis præcis 5 pakker
tshark -Y "modbus"                     # Filtrer på Modbus TCP pakker
tshark -Y "modbus.func_code == 6"      # Find uautoriserede Modbus Write Single Register angreb
tshark -Y "dcp"                        # Find PROFINET DCP pakker
tshark -Y "eth.addr contains b8:27:eb" # Opspor Raspberry Pi OUI MAC-adresser
tshark -Y "s7comm"                     # Filtrer Siemens S7 communication pakker
tshark -Y "opcua"                      # Filtrer OPC UA binære protokolpakker
tshark -V -c 1                         # Udførlig OSI-lags dissektion af pakken
tshark -T fields -e ip.src -e ip.dst   # Vis specifikke header-felter
man tshark                             # Manual og oversigt over syntaks
cheat tshark                           # Hurtig snydeseddel med eksempler tilpasset anlægget
```

Pakkerne genereres dynamisk i realtid afhængigt af anlæggets fysiske tilstand (f.eks. angrebsfrekvens, firewall-blokeringer og SCADA-timeouts).

---

## 🎓 Pædagogiske Tilstande: Teach Mode vs. Exam Mode

For at differentiere mellem introducerende undervisning og individuel eksamination/test tilbyder spillet to driftstilstande:

- **Skift tilstand:** Skriv `skift tilstand`, `mode teach` eller `mode exam`.
- **Teach Mode:**
  - Svarmuligheder vises med tydelige pædagogiske markeringer: `[FALDGRUPE - ...]`, forklaringer og ledetråde.
  - Hjælper den studerende med at forstå årsagssammenhænge og konsekvenser i et trygt læringsrum.
- **Exam Mode:**
  - Ingen advarsler eller markeringer.
  - **Svarmulighederne blandes tilfældigt hver gang**, så studerende ikke kan bestå ved blot at huske svarnumre eller faste positioner.

---

## ⚙️ Faglige Udfordringer & Angrebsscenarier

### 1. Pumpehuset: Modbus TCP Firewall & "Glem Allow FC 03" Dilemmaet
Spilleren skal montere en industriel DIN-skinne DPI-firewall foran VFD-frekvensomformeren.
- **Angrebet:** En uautoriseret enhed (`192.168.1.99`) oversvømmer VFD'en med Modbus Function Code 06 (Write Single Register) til register `40001` med `120 Hz`, hvilket presser pumpehovedet til 14.8 bar og truer med at sprænge rørledningerne.
- **Faldgruppen (Drop uden Allow):**
  - Hvis man blot konfigurerer firewallen til at blokere FC 06 (`firewall rule add --drop-fc 6`), glemmer man at give eksplicit tilladelse til læsning af telemetri (FC 03 Read Holding Registers).
  - **Konsekvens:** SCADA mister kontakten (`SCADA BLIND / TIMEOUT`), overvågningen blinker lilla alarm på canvas, og Hans McDonald slår alarm over manglende driftsovervågning.
- **Korrekt løsning:**
  ```text
  firewall rule add --allow-fc 3 --drop-fc 6
  ```
  Eller via arbejdsbordets talvalg med både læse-tilladelse og skrive-blokering.

### 2. Ventil-øen: Skjult Rogue Pi & Retsmedicinske Dilemmaer (Chain of Custody)
- **Skjult boks:** En uautoriseret boks er tapet fast i kabelbakken bag Profinet-ventilerne. Den fremgår ikke umiddelbart på skærmen, men skal opspores via omhyggelig inspektion (`undersøg kabelbakke`) eller via `tshark -Y "dcp"`.
- **Forensisk håndtering:**
  - **Korrekt:** Sikr enheden i en antistatisk Faraday-pose (`sikr pi i faraday-pose`). Der udregnes automatisk en SHA-256 hash af enhedens hukommelse, og der oprettes et plomberingsnummer i den digitale logbog.
  - **Faldgrupper:** At smide den i skraldespanden (tab af bevis jf. NIS2 Art. 21.2.b), gemme den til eget hobbyprojekt (genaktiverer bagdøren) eller indsætte SD-kortet direkte i egen bærbar (korrumperer tidsstempler og risikerer malwareinfektion).

### 3. El-tavlen: 5 Forgrenede Ingeniørveje
S7-1500 PLC'en er gået i STOP. Spilleren har fem mulige tilgange med vidt forskellige konsekvenser:
1. **Guldstandard:** Tag offline USB-backup, kør TIA Portal Security Wizard for at deaktivere ubeskyttet PUT/GET og aktiver Protection Level 3 (`konfigurer tia portal`).
2. **Forhastet koldstart (Fælde):** Tving CPU i RUN via nøglekontakt uden at lappe hullet. Angriberen korrumperer DB1 på port 102 -> PLC låser i *DEFECTIVE STOP*.
3. **Firewall Overkill (Fælde):** Total blokering af TCP port 102 i cellens firewall. Kapper PROFIsafe-kommunikationen til ET 200SP I/O -> øjeblikkelig **F-I/O passivering og anlægsstop**.
4. **Live Firmware-Patch (Fælde):** Firmware-opdatering live uden SHA-256 validering -> angriberen udfører MitM og bricker bootloaderen.
5. **Uisoleret Laptop (Fælde):** Bærbar kobles direkte i CPU-porten under aktivt angreb -> ARP-spoofing kaprer ingeniørsessionen.

### 4. Kontrolrummet: Autentisk OPC UA PKI Hardening
Industriel DMZ (Purdue 3.5) skal sikres mod uautoriseret adgang:
- **Sanering af Shadow-IT:** Afmontér uautoriseret 4G-router monteret bag SCADA-skabet (`frakobl 4g-router`).
- **PKI Truststore:** Flyt SCADA-klientens certifikat fra mappen *Rejected* til mappen *Trusted* (`godkend scada certifikat`).
- **Kryptografi:** Skift SecurityPolicy til `Basic256Sha256` og MessageSecurityMode til `SignAndEncrypt` (`aktiver opc kryptering`).
- **Adgangskontrol:** Deaktivér `Anonymous` UserTokenType og gennemtving rollebaseret adgangskontrol (`deaktiver anonymous opc`).

---

## 📜 NIS2 Rapportering & Revisionsværktøjer

- **24-timers Early Warning (`indberet hændelse`):** Lovpligtig tidlig advarsel til det nationale CSIRT / Cybersikkerhedstilsynet jf. NIS2 Artikel 23 vedrørende væsentlige hændelser.
- **Evidenslog (`vis evidens`):** Retsmedicinsk oversigt over beslaglagt udstyr med SHA-256 hashes og opbevaringskæde (NIST SP 800-61).
- **Eksportér NIS2 Revisionsrapport (`eksporter rapport`):** Opretter en officiel revisionsrapport i Markdown (`NIS2_Audit_Rapport_NordicH2O.md`), indeholdende Artikel 21 compliance matrix, hændelseslog og revisor Kirstens bedømmelse.

---

## 🧪 Tests & Kvalitetssikring

Projektet indeholder automatiserede testsuiter til validering af kodebase og spilmekanikker:

```powershell
# 1. Kontroller at alle 33 Python-filer kompilerer fejlfrit
python test_compilation.py

# 2. Afprøv alle 11 spilmekanikker, fail-states, Purdue-mapping og tshark-engine
python test_game_mechanics.py

# 3. Kør automatiseret GUI integrationstest (Tkinter terminal, canvas og dialoger)
python test_gui_app.py
```

Alle tests kører hurtigt og uafhængigt uden behov for eksterne test-frameworks som pytest.
