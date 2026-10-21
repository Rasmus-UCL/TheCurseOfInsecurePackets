"""Rogue Raspberry Pi 4 Device (Hidden in Cable Tray) with Forensic Dilemma Actions."""

from __future__ import annotations

from typing import Any
from devices.base import BaseDevice


class RoguePiDevice(BaseDevice):
    def __init__(self) -> None:
        super().__init__(
            name="rogue raspberry pi",
            title="Kabelbakke bag ventilstativerne",
            purdue_level="Purdue Level 1 (Fremmed udstyr)",
            zone="Zone 2: Feldbus & I/O",
            description="En kabelbakke bag Festo-ventilerne. Et sort bundt kabler forsvinder bag en metalkonstruktion.",
        )
        self.revealed = False
        self.disconnected = False
        self.disposition = "unhandled"

    def reveal(self) -> None:
        self.revealed = True
        self.name = "rogue raspberry pi"
        self.title = "Rogue Raspberry Pi 4 (Optapet boks)"
        self.description = (
            "En Raspberry Pi 4 i sort kabinet tapet fast med gaffa på kabelbakken. "
            "Den er forsynet via en PoE-splitter og sender tusindvis af falske PROFINET DCP-pakker pr. sekund!"
        )

    def get_telemetry(self, engine: Any) -> str:
        flags = getattr(engine, "flags", set())
        if self.disconnected:
            return f"FRAKOBLET: Sikret i evidens-tilstand [{self.disposition.upper()}]."
        if not self.revealed:
            return "KABELBAKKE: Mistænkeligt kabeltræk fører mod en sort boks tapet fast under stålskinnen."
        return "AKTIV LAYER 2 ANGREBSVEKTOR: MAC b8:27:eb:d4:11:22 | Sender DCP Set (Station: rogue-io) | ARP-spoofing aktiv!"

    def get_available_actions(self, engine: Any) -> list[tuple[str, str, str]]:
        actions = []
        if not self.revealed:
            actions.append(("investigate_tray", "Undersøg kabelbakken nøje med lommelygte", "undersøg kabelbakke"))
            return actions

        if not self.disconnected:
            actions.append(("pi_remove_proper", "1. Forensisk sikring i Faraday-pose (NIS2 Best Practice)", "sikr pi i faraday-pose"))
            actions.append(("pi_remove_trash", "2. Smid den ud i værkstedets skraldespand (Fælde)", "smid pi i skraldespand"))
            actions.append(("pi_remove_reuse", "3. Gem den i lommen til privat IoT-projekt (Fælde)", "gem pi til genbrug"))
            actions.append(("pi_inspect_sd", "4. Træk SD-kortet ud og sæt i din egen laptop (Fælde)", "indsæt sd-kort i bærbar"))
        else:
            actions.append(("pi_status", "Aflæs evidensjournal", "vis evidens"))

        return actions
