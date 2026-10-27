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

    def get_description(self, engine: Any) -> str:
        flags = getattr(engine, "flags", set())
        ch = getattr(engine, "chapter", 1)
        is_revealed = "pi-revealed" in flags
        pi_removed = "pi-removed" in flags

        if "chapter-2-done" in flags:
            return (
                "Ventil-øen arbejder med millimeterpræcis, tysk determinisme. Festo magnetventilerne "
                "klikker blidt og synkront i en stabil takt. Den nye SCALANCE XB-200 switch danner en "
                "robust PROFINET MRP-ring med 200ms redundansgaranti, og port-sikkerheden afviser spoofing."
            )
        if ch == 2:
            if not is_revealed:
                return (
                    "Trykluften hvæser som en såret slange! De decentrale Festo-ventiler smælder op og i "
                    "med voldsomme, kaotiske ryk hvert 100. millisekund. Rørledningerne spændes op af farlige "
                    "hydrauliske trykstød. På DIN-skinnen blinker en billig, uadministreret D-Link plast-switch "
                    "i et hysterisk grønt diodelys. Bag stålrammen løber kabelbakke K-04 med et mistænkeligt blåt patchkabel..."
                )
            if not pi_removed:
                return (
                    "Ventilerne hamrer fortsat uregelmæssigt. Lommelygtens kegle oplyser den sorte plastikboks under "
                    "kabelbakke K-04: En Rogue Raspberry Pi 4 tapet fast med gaffa-tape og kablet direkte ind i switchport 4. "
                    "Enheden blinker aggressivt, mens den sender falske PROFINET DCP pakker ud i det flade netværk!"
                )
            return (
                "Den rogue Raspberry Pi er fjernet og isoleret i bevissikringen! Men den gamle D-Link switch "
                "kæmper stadig med at genskabe netværksstabiliteten. Ventilerne mangler en managed switch med "
                "Media Redundancy Protocol (MRP) for at genvinde determinismen."
            )
        return self.description

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
        choices: list[tuple[str, str, str, str]] = []

        is_revealed = "pi-revealed" in flags
        pi_removed = "pi-removed" in flags

        if ch == 2:
            if not is_revealed:
                choices.append(("1", "🔍 Inspicér Festo ventil-øen og ET 200SP decentrale I/O moduler", "undersøg ventiler", "normal"))
                choices.append(("2", "📊 Kør tshark og overvåg Layer 2 PROFINET DCP-broadcasts", "åbn wireshark", "normal"))
                choices.append(("3", "🔦 Undersøg kabelbakke K-04 bag ventilstativerne for skjult kabling", "undersøg kabelbakke", "primary"))
                choices.append(("4", "☕ Spørg Hans om tidligere netværksændringer på ventil-øen", "spørg hans om lars", "normal"))
                choices.append(("5", "🔌 Afbryd D-Link switchen ved at trække alle patchkabler ud med det samme", "pille switch fra", "normal"))
                return choices

            if not pi_removed:
                choices.append(("1", "📊 Inspicér DCP-pakkerne fra kilde-MAC b8:27:eb:d4:11:22 i tshark", "åbn wireshark", "normal"))
                choices.append(("2", "☕ Spørg Hans om hvem der har brugt Raspberry Pi udstyr i driften", "spørg hans om lars", "normal"))
                choices.append(("3", "🛡️ Frakobl enheden, forsegl den i antistatisk Faraday-pose og log SHA-256", "sikr pi i faraday-pose", "normal"))
                choices.append(("4", "🗑️ Frakobl enheden og smid den ud i værkstedets elektronik-skraldespand", "smid pi i skraldespand", "normal"))
                choices.append(("5", "📦 Frakobl enheden og gem den på hylden til genbrug i et lokalt testmiljø", "gem pi til genbrug", "normal"))
                choices.append(("6", "💻 Tag MicroSD-kortet ud og sæt det direkte i din egen bærbare PC for filanalyse", "indsæt sd-kort i bærbar", "normal"))
                return choices

            # Pi removed, now fix the switch
            choices.append(("1", "🔄 Monter SCALANCE XB-200 managed switch og etabler redundant PROFINET MRP-ring", "udskift switch med scalance", "primary"))
            choices.append(("2", "📊 Verificer med tshark om DCP-broadcast-stormen er ophørt", "åbn wireshark", "normal"))
            choices.append(("3", "🕵️ Åbn Sagstavlen og analyser de nye spor", "sagstavle", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg Festo ventil-øen (deterministisk PROFINET RT)", "undersøg ventiler", "normal"))
        choices.append(("2", "📊 Kør tshark og inspicér PROFINET RT rammer", "åbn wireshark", "normal"))
        choices.append(("3", "⚡ Gå til Hoved-el-tavlen", "gå til el-tavlen", "primary"))
        return choices
