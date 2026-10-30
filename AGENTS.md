# Projektorganisation & Agent-Team: The Curse of Insecure Packets

Dette dokument beskriver det specialiserede agent-team oprettet til videreudviklingen af *The Curse of Insecure Packets* (Valgfag i OT-Sikkerhed & Industrielle Netværk, UCL).

---

## 🏛️ Overordnet Mål & PoC-Strategi

Spillet udvikles aktuelt som et **Proof of Concept (PoC)** i Python.
For at fremtidssikre spillet til en potentiel migrering til et andet programmeringssprog eller motor (f.eks. C#, Unity, Godot eller Web/TypeScript), håndhæver teamet:
1. **Streng Separation of Concerns:** Spillogik, state machines og datamodeller holdes fuldstændigt afkoblet fra GUI og platformspecifik kode.
2. **Serialiserbare data:** Missioner, dialoger, mistænkte og beviser defineres i deklarative strukturer (JSON/dataclasses).
3. **Didaktisk og faglig integritet:** Spillet skal fungere optimalt både som undervisningsværktøj (*Teach Mode*) og eksamensværktøj (*Exam Mode*).

---

## 👥 Agent-Roller & Ansvarsområder

### 🎮 Spiludviklingsteamet

| Agent | Rolle | Primære ansvarsområder |
| :--- | :--- | :--- |
| **`senior-dev-lead`** | **Teamansvarlig & Senior Udvikler** | Overordnet spilarkitektur, håndhævelse af PoC-portabilitet (afkobling af logik fra GUI), code review og koordinering med fagkonsulenterne (`ot-nis2-expert` og `ucl-didactic`). |
| **`senior-narrative-designer`** | **Senior Fortælling & Dialog** | Lore, dynamiske dialogtræer (herunder Revisor Kirsten uden akavede gentagelser), tone-of-voice og præcis cybersikkerhedsterminologi (f.eks. "netværksforensiske spor" i stedet for "retsmedicinske beviser"). |
| **`game-programmer`** | **Core Spilprogrammør** | Implementering af mekanikker i Python, Teach vs. Exam mode (kun valgbar fra start), dags-timer justering, NIS2 art. 23 (24-timers indberetningsregel) og nulstilling af sagstavle. |
| **`ui-visual-designer`** | **UI & Visuel Designer** | Grafisk layout og styling af brugerfladen, sagstavle-visning (skjulning af procenter/beviser i Exam mode), UCL-branding samt design af separat vindue til eksport/gemning af revisionsrapporten. |
| **`game-tester-qa`** | **QA & Game Tester** | Testautomatisering (`test_game_mechanics.py`, `test_gui_app.py`), verifikation af spilflow, regressionstests og validering af, at data ikke lækkes i Exam Mode. |

---

### 🎓 Faglige & Didaktiske Konsulenter

| Agent | Rolle | Primære ansvarsområder |
| :--- | :--- | :--- |
| **`ot-nis2-expert`** | **OT/ICS- & NIS2-Fagkonsulent** | Realistisk OT-sikkerhed (Purdue-model, IDMZ, Modbus/PLC, Wireshark/tshark) samt juridisk og praktisk implementering af NIS2 artikel 23 (24-timers varsling vs. 72-timers rapport, væsentlighedskriterier). |
| **`ucl-didactic`** | **UCL Læring & Didaktik** | Forankring i UCL's læringsmål, studieaktivitetsmodellen, differentiering mellem formativ læring (*Teach Mode*) og summativ evaluering (*Exam Mode*) samt rapportens værdi som eksamensbilag. |

---

## 🚀 Samspilsmodel

```
                      ┌──────────────────────┐
                      │    Bruger / Ejer     │
                      └──────────┬───────────┘
                                 │
                     ┌───────────▼───────────┐
                     │    senior-dev-lead    │
                     └─────┬───────┬───────┬─┘
         ┌─────────────────┘       │       └─────────────────┐
         │ (Faglig sparring)       │ (Arkitektur/opgaver)    │ (Didaktisk sparring)
┌────────▼────────┐                │                ┌────────▼────────┐
│ ot-nis2-expert  │                │                │  ucl-didactic   │
└─────────────────┘                │                └─────────────────┘
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
┌────────▼────────┐       ┌────────▼────────┐       ┌────────▼────────┐
│ senior-narrative│       │ game-programmer │       │ ui-visual-      │
│    designer     │       │                 │       │    designer     │
└────────┬────────┘       └────────┬────────┘       └────────┬────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │ (Validering & regression)
                          ┌────────▼────────┐
                          │ game-tester-qa  │
                          └─────────────────┘
```
