"""Hoved-el-tavlen - Purdue Level 1/2: PLC & Safety Control Center with 5-Way Branching."""

from __future__ import annotations

from typing import Any
from rooms.base import BaseRoom


class ElTavlenRoom(BaseRoom):
    def __init__(self) -> None:
        super().__init__(
            key="el-tavlen",
            title="Hoved-el-tavlen",
            purdue_level="Purdue Level 1/2: PLC & Netværkscenter",
            zone="Zone 3: Hovedtavle & Sikkerheds-PLC (VLAN 30)",
            description=(
                "Hoved-el-tavlen summer dybt. En Siemens S7-1500 (CPU 1516F) står med blinkende rød STOP-diode. "
                "Ved siden af sidder sikkerhedsrelæ K1 på 35mm DIN-skinnen og en fordelingsswitch for cellen."
            ),
            hotspots=["s7-1500", "sikkerhedsrelæ k1", "d-link switch"],
        )

    def get_description(self, engine: Any) -> str:
        flags = getattr(engine, "flags", set())
        ch = getattr(engine, "chapter", 1)

        if getattr(engine, "breaker_tripped", False):
            return (
                "Hoved-el-tavlen er præget af en rød advarselslampe. Sikkerhedsrelæ K1 er udløst af det hydrauliske "
                "tilbageslag fra Pumpehuset! Hovedkontaktoren står åben med en sort indikator. Pumpe 2 er uden spænding. "
                "Du kan nulstille K1 med den manuelle vippekontakt."
            )
        if getattr(engine, "plc_defect_stop", False):
            return (
                "Hoved-el-tavlen er oplyst af en hektisk gul/rød advarselslampe. Siemens S7-1500 Sikkerheds-PLC'en "
                "(CPU 1516F) er låst i DEFECTIVE STOP (fejlkode 0x4542). Datablok DB1 er korrupt som følge af "
                "en overførsel uden forudgående backup. Hele processtyringen er lammet. Du må gendanne DB1 fra backup."
            )
        if "chapter-3-done" in flags:
            return (
                "Hoved-el-tavlen summer med en stabil, beroligende 50 Hz brummen. CPU 1516F lyser med en fast, "
                "grøn RUN-diode. TIA Portal konfigurationen er hærdet med Password Protection Level 3, og "
                "uautoriserede PUT/GET kald fra S7comm port 102 afvises konsekvent ved porten."
            )
        if ch == 3:
            return (
                "Hoved-el-tavlens låge står på klem, og duften af varm elektronik og ozon møder dig. "
                "Siemens S7-1500 (CPU 1516F) Failsafe PLC'en står med en blinkende rød STOP-diode! Al automatisk "
                "processtyring er slået fra, og vandværkets buffertanke tømmes gradvist. Hans McDonald tørrer "
                "sved af panden:\n'Nogen har sendt rå S7comm blokskrivninger direkte ind i vores kalibreringsblok!'"
            )
        return self.description

    def get_choices(self, engine: Any) -> list[tuple[str, str, str, str]]:
        flags = getattr(engine, "flags", set())
        ch = getattr(engine, "chapter", 1)
        mode = getattr(engine, "game_mode", "teach")
        choices: list[tuple[str, str, str, str]] = []

        # Breaker reset if tripped from Chapter 1
        if getattr(engine, "breaker_tripped", False):
            if mode == "exam":
                choices.append(("1", "Nulstil K1-sikringsrelæet med den manuelle vippekontakt", "nulstil relæ", "warning"))
            else:
                choices.append(("1", "⚡ Nulstil sikkerhedsrelæ K1 med den manuelle flip-kontakt", "nulstil relæ", "warning"))

        # Defective STOP recovery if corrupted DB1
        if getattr(engine, "plc_defect_stop", False):
            if mode == "exam":
                choices.append(("1", "Indsæt autoriseret USB-stik og gendan fabrikskalibreret DB1", "gendan plc db1", "success"))
                choices.append(("2", "Inspicér S7-1500 display for fejlkode 0x4542 (DEFECTIVE STOP)", "undersøg s7-1500", "normal"))
                choices.append(("3", "Gå til Kontrolrummet", "gå til kontrolrummet", "normal"))
            else:
                choices.append(("1", "💾 Indsæt autoriseret USB-stik og gendan fabrikskalibreret DB1", "gendan plc db1", "success"))
                choices.append(("2", "🔍 Inspicér S7-1500 display for fejlkode 0x4542 (DEFECTIVE STOP)", "undersøg s7-1500", "normal"))
                choices.append(("3", "🖥️ Gå til Kontrolrummet", "gå til kontrolrummet", "normal"))
            return choices

        if ch == 3:
            # 5 distinct branching paths & investigative steps
            if mode == "exam":
                choices.append(("1", "Inspicér S7-1500 display og diagnostic buffer log", "undersøg s7-1500", "normal"))
                choices.append(("2", "Undersøg USB-stik fundet i el-tavlens dokumentlomme", "undersøg usb", "normal"))
                choices.append(("3", "Åbn Wireshark og analyser rå S7comm frames på TCP port 102", "åbn wireshark", "normal"))
                choices.append(("4", "Spørg driftstekniker Hans om PLC-backup og tidligere teknikere", "spørg hans om lars", "normal"))
                choices.append(("5", "Åbn efterforskningens sagstavle og opdater hypoteser", "sagstavle", "normal"))
                choices.append(("6", "Opret en offline sikkerhedskopi af CPU 1516F projektet og DB1 til autoriseret USB-stik", "tag offline backup", "success"))
                choices.append(("7", "Konfigurer TIA Portal: Deaktivér ubeskyttet PUT/GET kommunikation og aktiver Protection Level 3", "konfigurer tia portal", "success"))
                choices.append(("8", "Tving CPU 1516F i RUN-mode via den fysiske nøgleomskifter for at genstarte styringen", "tving cpu i run", "danger"))
                choices.append(("9", "Opret en firewall-regel der blokerer al indgående og udgående TCP port 102 trafik", "bloker port 102", "warning"))
                choices.append(("10", "Overfør ny firmware-opdatering v2.9 direkte til CPU'en over det aktive netværk", "opdater firmware live", "danger"))
                choices.append(("11", "Tilslut tekniker-laptop direkte til CPU 1516F PROFINET-port X1 under aktiv drift", "kobl laptop i plc port", "danger"))
                choices.append(("12", "Gå til Kontrolrummet", "gå til kontrolrummet", "normal"))
            else:
                choices.append(("1", "👁️ Trin 1 (Observation): Undersøg S7-1500 display & diagnostic buffer", "undersøg s7-1500", "normal"))
                choices.append(("2", "🔍 Trin 2 (Efterforskning): Undersøg efterladt USB-stik i tavlens dokumentlomme", "undersøg usb", "normal"))
                choices.append(("3", "📊 Trin 3 (Dataindsamling): tshark -Y \"s7comm\" (Analyser blokskrivninger på Port 102)", "åbn wireshark", "normal"))
                choices.append(("4", "☕ Trin 4 (Afhøring): Spørg Hans om PLC-projektet og adgangskoder ('spørg hans om lars')", "spørg hans om lars", "normal"))
                choices.append(("5", "🕵️ Trin 5 (Sagstavle): Opdater sagstavlen med spor ('sagstavle')", "sagstavle", "normal"))
                choices.append(("6", "💾 Modtræk Spor 1 (Guldstandard): Tag offline USB-backup før ændring jf. NIS2", "tag offline backup", "success"))
                choices.append(("7", "⚙️ Modtræk Spor 1b: TIA Portal: Deaktivér ubeskyttet PUT/GET & aktiver Protection Level 3", "konfigurer tia portal", "success"))
                choices.append(("8", "🔑 Faldgrube 1 (Koldstart): Tving CPU i RUN via nøgleomskifter uden backup", "tving cpu i run", "danger"))
                choices.append(("9", "🛡️ Faldgrube 2 (Firewall overkill): Bloker Port 102 totalt (Passiverer PROFIsafe!)", "bloker port 102", "warning"))
                choices.append(("10", "📦 Faldgrube 3 (Live patch): Opdater CPU firmware live uden SHA-256 validering", "opdater firmware live", "danger"))
                choices.append(("11", "💻 Faldgrube 4 (Uisoleret laptop): Forbind bærbar direkte i CPU PN-port under angreb", "kobl laptop i plc port", "danger"))
                choices.append(("12", "🖥️ Navigation: Gå til Kontrolrummet", "gå til kontrolrummet", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg Siemens S7-1500 Sikkerheds-PLC (RUN)", "undersøg s7-1500", "normal"))
        choices.append(("2", "📊 Wireshark: Verificer Port 102 afviser uautoriserede kommandoer", "åbn wireshark", "normal"))
        choices.append(("3", "🖥️ Gå til Kontrolrummet", "gå til kontrolrummet", "normal"))
        choices.append(("4", "🚰 Gå til Pumpehuset", "gå til pumpehuset", "normal"))
        choices.append(("5", "💨 Gå til Ventil-øen", "gå til ventil-oen", "normal"))
        return choices
