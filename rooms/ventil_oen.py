"""Ventil-øen - Purdue Level 1: Distributed I/O Zone & Hidden Rogue Pi."""

from __future__ import annotations

from typing import Any
from rooms.base import BaseRoom


class VentilOenRoom(BaseRoom):
    def __init__(self) -> None:
        super().__init__(
            key="ventil-oen",
            title="Ventil-øen",
            purdue_level="Purdue Level 1: Distributed I/O Zone",
            zone="Zone 2: Feldbus & I/O (VLAN 20)",
            description=(
                "PROFINET-kablerne snor sig mod den decentrale Festo ventil-ø. Ventilerne åbner og lukker "
                "i et hektisk kaos, og trykluften hvisler. En kabelbakke bag stålrammen gemmer på et mistænkeligt kabeltræk."
            ),
            hotspots=["ventiler", "switch", "kabelbakke"],
        )
        self.pi_revealed: bool = False

    def get_visible_hotspots(self, engine: Any) -> list[str]:
        flags = getattr(engine, "flags", set())
        if self.pi_revealed or "pi-revealed" in flags:
            return ["ventiler", "switch", "rogue raspberry pi"]
        return ["ventiler", "switch", "kabelbakke"]

    def reveal_pi(self, engine: Any) -> None:
        self.pi_revealed = True
        flags = getattr(engine, "flags", set())
        flags.add("pi-revealed")

    def get_choices(self, engine: Any) -> list[tuple[str, str, str, str]]:
        flags = getattr(engine, "flags", set())
        ch = getattr(engine, "chapter", 1)
        mode = getattr(engine, "game_mode", "teach")
        choices: list[tuple[str, str, str, str]] = []

        is_revealed = self.pi_revealed or "pi-revealed" in flags
        pi_removed = "pi-removed" in flags

        if ch == 2:
            if not is_revealed:
                if mode == "exam":
                    choices.append(("1", "Åbn Wireshark og overvåg Layer 2 PROFINET DCP-broadcasts", "åbn wireshark", "normal"))
                    choices.append(("2", "Undersøg kabelbakke K-04 bag ventilstativerne for uautoriseret kabling", "undersøg kabelbakke", "primary"))
                    choices.append(("3", "Inspicér Festo ventil-øen og ET 200SP decentrale I/O moduler", "undersøg ventiler", "normal"))
                    choices.append(("4", "Afbryd den eksisterende D-Link switch ved at trække alle patchkabler ud", "pille switch fra", "danger"))
                else:
                    choices.append(("1", "📊 Wireshark: Analyser Layer 2 PROFINET DCP & find ukendt MAC", "åbn wireshark", "normal"))
                    choices.append(("2", "🔍 Undersøg den mistænkelige kabelbakke bag ventilstativerne", "undersøg kabelbakke", "primary"))
                    choices.append(("3", "🔍 Undersøg Festo ventil-øen og ET 200SP I/O", "undersøg ventiler", "normal"))
                    choices.append(("4", "⚠️ Pille switch fra: Træk kablerne ud af D-Link switchen (Risiko: Kavitation)", "pille switch fra", "danger"))
                return choices

            if not pi_removed:
                if mode == "exam":
                    choices.append(("1", "Inspicér DCP Identify pakker fra kilde-MAC b8:27:eb:d4:11:22", "åbn wireshark", "normal"))
                    choices.append(("2", "Frakobl enheden, forsegl i antistatisk Faraday-pose og registrer i hændelsesloggen", "sikr pi i faraday-pose", "success"))
                    choices.append(("3", "Frakobl enheden og kasser den som defekt elektronikaffald i værkstedets skraldespand", "smid pi i skraldespand", "warning"))
                    choices.append(("4", "Frakobl enheden og gem den til genanvendelse i et lokalt testmiljø", "gem pi til genbrug", "danger"))
                    choices.append(("5", "Tag MicroSD-kortet ud og tilslut direkte til din felt-laptop for filanalyse", "indsæt sd-kort i bærbar", "danger"))
                    choices.append(("6", "Frakobl netværkskablerne fra D-Link switchen uden at fjerne den tilkoblede hardware", "pille switch fra", "danger"))
                else:
                    choices.append(("1", "📊 Wireshark: Inspicér de falske DCP-pakker fra MAC b8:27:eb:d4:11:22", "åbn wireshark", "normal"))
                    choices.append(("2", "🛡️ Forensisk sikring: Kobl Pi fra & forsegl i antistatisk Faraday-pose (NIS2 Guldstandard)", "sikr pi i faraday-pose", "success"))
                    choices.append(("3", "🗑️ Frakobl Pi og smid den ud i værkstedets skraldespand (Fælde)", "smid pi i skraldespand", "warning"))
                    choices.append(("4", "🏠 Tag Pi med hjem i lommen til privat genbrug (Fælde)", "gem pi til genbrug", "danger"))
                    choices.append(("5", "💻 Tag MicroSD-kortet ud og sæt i din egen bærbare (Fælde)", "indsæt sd-kort i bærbar", "danger"))
                    choices.append(("6", "⚠️ Pille switch fra uden at fjerne Pi (Risiko: Kavitation)", "pille switch fra", "danger"))
                return choices

            # Pi removed, now fix the switch
            if mode == "exam":
                choices.append(("1", "Monter SCALANCE XB-200 managed switch og etabler redundant PROFINET MRP-ring", "udskift switch med scalance", "success"))
                choices.append(("2", "Åbn montage-arbejdsbænken for SCALANCE XB-200 og MRP-konfiguration", "switch workbench", "normal"))
                choices.append(("3", "Verificer netværkets determinisme med Wireshark", "åbn wireshark", "normal"))
                choices.append(("4", "Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
            else:
                choices.append(("1", "🔄 Monter SCALANCE XB-200 managed switch & forbind PROFINET MRP-ring (Guldstandard)", "udskift switch med scalance", "success"))
                choices.append(("2", "🛠️ Åbn Switch Montage-arbejdsbænk for manuel montage", "switch workbench", "normal"))
                choices.append(("3", "📊 Wireshark: Verificer om DCP-stormen er stoppet", "åbn wireshark", "normal"))
                choices.append(("4", "⚡ Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg Festo ventil-øen (deterministisk PROFINET RT)", "undersøg ventiler", "normal"))
        choices.append(("2", "📊 Wireshark: Inspicér PROFINET RT rammer", "åbn wireshark", "normal"))
        choices.append(("3", "⚡ Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
        choices.append(("4", "🖥️ Gå til Kontrolrummet", "gå til kontrolrummet", "normal"))
        choices.append(("5", "🚰 Gå til Pumpehuset", "gå til pumpehuset", "normal"))
        return choices
