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
            # 5 distinct branching paths
            if mode == "exam":
                choices.append(("1", "Opret en offline sikkerhedskopi af CPU 1516F projektet og DB1 til autoriseret USB-stik", "tag offline backup", "success"))
                choices.append(("2", "Konfigurer TIA Portal: Deaktivér ubeskyttet PUT/GET kommunikation og aktiver Protection Level 3", "konfigurer tia portal", "success"))
                choices.append(("3", "Tving CPU 1516F i RUN-mode via den fysiske nøgleomskifter for at genstarte styringen", "tving cpu i run", "danger"))
                choices.append(("4", "Opret en firewall-regel der blokerer al indgående og udgående TCP port 102 trafik", "bloker port 102", "warning"))
                choices.append(("5", "Overfør ny firmware-opdatering v2.9 direkte til CPU'en over det aktive netværk", "opdater firmware live", "danger"))
                choices.append(("6", "Tilslut tekniker-laptop direkte til CPU 1516F PROFINET-port X1 under aktiv drift", "kobl laptop i plc port", "danger"))
                choices.append(("7", "Åbn Wireshark og analyser rå S7comm frames på TCP port 102", "åbn wireshark", "normal"))
                choices.append(("8", "Gå til Kontrolrummet", "gå til kontrolrummet", "normal"))
            else:
                choices.append(("1", "💾 Spor 1 (Guldstandard): Tag offline USB-backup før ændring jf. NIS2", "tag offline backup", "success"))
                choices.append(("2", "⚙️ Spor 1b: TIA Portal: Deaktivér ubeskyttet PUT/GET & aktiver Protection Level 3", "konfigurer tia portal", "success"))
                choices.append(("3", "🔑 Spor 2 (Forhastet koldstart): Tving CPU i RUN via nøgleomskifter uden backup", "tving cpu i run", "danger"))
                choices.append(("4", "🛡️ Spor 3 (Firewall overkill): Bloker Port 102 totalt i cellens firewall (Risiko: Nødstop)", "bloker port 102", "warning"))
                choices.append(("5", "📦 Spor 4 (Live firmware-patch): Opdater CPU firmware live uden SHA-256 validering", "opdater firmware live", "danger"))
                choices.append(("6", "💻 Spor 5 (Uisoleret laptop): Forbind bærbar direkte i CPU PN-port under angreb", "kobl laptop i plc port", "danger"))
                choices.append(("7", "📊 Wireshark: Analyser rå S7comm frames på Port 102", "åbn wireshark", "normal"))
                choices.append(("8", "🖥️ Gå til Kontrolrummet", "gå til kontrolrummet", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg Siemens S7-1500 Sikkerheds-PLC (RUN)", "undersøg s7-1500", "normal"))
        choices.append(("2", "📊 Wireshark: Verificer Port 102 afviser uautoriserede kommandoer", "åbn wireshark", "normal"))
        choices.append(("3", "🖥️ Gå til Kontrolrummet", "gå til kontrolrummet", "normal"))
        choices.append(("4", "🚰 Gå til Pumpehuset", "gå til pumpehuset", "normal"))
        choices.append(("5", "💨 Gå til Ventil-øen", "gå til ventil-oen", "normal"))
        return choices
