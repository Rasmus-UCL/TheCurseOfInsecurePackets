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
        choices: list[tuple[str, str, str, str]] = []

        # Breaker reset if tripped from Chapter 1
        if getattr(engine, "breaker_tripped", False):
            choices.append(("1", "⚡ Nulstil sikkerhedsrelæ K1 med den manuelle vippekontakt", "nulstil relæ", "warning"))
            choices.append(("2", "🚰 Gå tilbage til Pumpehuset", "gå til pumpehuset", "primary"))
            return choices

        # Defective STOP recovery if corrupted DB1
        if getattr(engine, "plc_defect_stop", False):
            choices.append(("1", "💾 Indsæt autoriseret USB-stik og gendan fabrikskalibreret DB1", "gendan plc db1", "success"))
            choices.append(("2", "🔍 Inspicér S7-1500 display for fejlkode 0x4542 (DEFECTIVE STOP)", "undersøg s7-1500", "normal"))
            return choices

        if ch == 3:
            choices.append(("1", "🔍 Inspicér S7-1500 display, diagnostic buffer og USB-stikket i tavlens lomme", "undersøg usb", "normal"))
            choices.append(("2", "📊 Kør tshark og analyser S7comm trafik på TCP port 102", "åbn wireshark", "normal"))
            if "backup-taken" not in flags:
                choices.append(("3", "💾 Opret offline sikkerhedskopi af CPU 1516F projekt og DB1 til USB-stik", "tag offline backup", "normal"))
            choices.append(("4", "⚙️ Konfigurer TIA Portal: Deaktivér PUT/GET og aktiver Protection Level 3", "konfigurer tia portal", "normal"))
            choices.append(("5", "🔑 Tving CPU 1516F i RUN-mode via den fysiske nøgleomskifter på fronten", "tving cpu i run", "normal"))
            choices.append(("6", "🛡️ Opret firewall-regel der blokerer al TCP port 102 trafik til tavlen", "bloker port 102", "normal"))
            choices.append(("7", "📦 Overfør ny firmware-opdatering direkte til CPU'en over netværket", "opdater firmware live", "normal"))
            choices.append(("8", "💻 Tilslut tekniker-laptop direkte i CPU PROFINET-port X1 under drift", "kobl laptop i plc port", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg Siemens S7-1500 Sikkerheds-PLC (RUN)", "undersøg s7-1500", "normal"))
        choices.append(("2", "📊 Kør tshark og verificer Port 102 status", "åbn wireshark", "normal"))
        choices.append(("3", "🖥️ Gå til Kontrolrummet (IDMZ)", "gå til kontrolrummet", "primary"))
        return choices
