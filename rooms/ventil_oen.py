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
        mode = getattr(engine, "game_mode", "teach")
        choices: list[tuple[str, str, str, str]] = []

        is_revealed = "pi-revealed" in flags
        pi_removed = "pi-removed" in flags

        if ch == 2:
            if not is_revealed:
                if mode == "exam":
                    choices.append(("1", "Inspicér Festo ventil-øen og ET 200SP decentrale I/O moduler", "undersøg ventiler", "normal"))
                    choices.append(("2", "Åbn Wireshark og overvåg Layer 2 PROFINET DCP-broadcasts", "åbn wireshark", "normal"))
                    choices.append(("3", "Undersøg kabelbakke K-04 bag ventilstativerne for uautoriseret kabling", "undersøg kabelbakke", "primary"))
                    choices.append(("4", "Spørg driftstekniker Hans om tidligere netværksændringer", "spørg hans om lars", "normal"))
                    choices.append(("5", "Åbn efterforskningens sagstavle og opdater hypoteser", "sagstavle", "normal"))
                    choices.append(("6", "Afbryd den eksisterende D-Link switch ved at trække alle patchkabler ud", "pille switch fra", "danger"))
                else:
                    choices.append(("1", "👁️ Trin 1 (Observation): Undersøg Festo ventil-øen og ET 200SP I/O", "undersøg ventiler", "normal"))
                    choices.append(("2", "📊 Trin 2 (Dataindsamling): Wireshark / tshark (Analyser Layer 2 DCP-storm)", "åbn wireshark", "normal"))
                    choices.append(("3", "🔍 Trin 3 (Fysisk efterforskning): Undersøg kabelbakke K-04 bag ventilstativerne", "undersøg kabelbakke", "primary"))
                    choices.append(("4", "☕ Trin 4 (Afhøring): Spørg Hans om tidligere teknikere og kabling ('spørg hans om lars')", "spørg hans om lars", "normal"))
                    choices.append(("5", "🕵️ Trin 5 (Sagstavle): Gennemse spor og mistænkte ('sagstavle')", "sagstavle", "normal"))
                    choices.append(("6", "⚠️ Faldgrube: Pille switch fra (Træk kabler ud -> Risiko: Kavitation)", "pille switch fra", "danger"))
                return choices

            if not pi_removed:
                if mode == "exam":
                    choices.append(("1", "Inspicér DCP Identify pakker fra kilde-MAC b8:27:eb:d4:11:22", "åbn wireshark", "normal"))
                    choices.append(("2", "Spørg driftstekniker Hans om hvem der installerede Raspberry Pi udstyr", "spørg hans om lars", "normal"))
                    choices.append(("3", "Frakobl enheden, forsegl i antistatisk Faraday-pose og registrer i hændelsesloggen", "sikr pi i faraday-pose", "success"))
                    choices.append(("4", "Frakobl enheden og kasser den som defekt elektronikaffald i værkstedets skraldespand", "smid pi i skraldespand", "warning"))
                    choices.append(("5", "Frakobl enheden og gem den til genanvendelse i et lokalt testmiljø", "gem pi til genbrug", "danger"))
                    choices.append(("6", "Tag MicroSD-kortet ud og tilslut direkte til din felt-laptop for filanalyse", "indsæt sd-kort i bærbar", "danger"))
                    choices.append(("7", "Frakobl netværkskablerne fra D-Link switchen uden at fjerne den tilkoblede hardware", "pille switch fra", "danger"))
                else:
                    choices.append(("1", "📊 Dataindsamling: Inspicér de falske DCP-pakker fra MAC b8:27:eb:d4:11:22", "åbn wireshark", "normal"))
                    choices.append(("2", "☕ Afhøring: Spørg Hans om hvem der brugte Raspberry Pi i driften ('spørg hans om lars')", "spørg hans om lars", "normal"))
                    choices.append(("3", "🛡️ Forensisk sikring (Guldstandard): Kobl Pi fra & forsegl i antistatisk Faraday-pose (NIS2)", "sikr pi i faraday-pose", "success"))
                    choices.append(("4", "🗑️ Faldgrube 1: Frakobl Pi og smid ud i værkstedets skraldespand (Tab af bevis)", "smid pi i skraldespand", "warning"))
                    choices.append(("5", "🏠 Faldgrube 2: Tag Pi med hjem i lommen til privat genbrug (Fælde)", "gem pi til genbrug", "danger"))
                    choices.append(("6", "💻 Faldgrube 3: Tag MicroSD-kortet ud og sæt i din egen bærbare (Fælde)", "indsæt sd-kort i bærbar", "danger"))
                    choices.append(("7", "⚠️ Faldgrube 4: Pille switch fra uden at fjerne Pi (Risiko: Kavitation)", "pille switch fra", "danger"))
                return choices

            # Pi removed, now fix the switch
            if mode == "exam":
                choices.append(("1", "Monter SCALANCE XB-200 managed switch og etabler redundant PROFINET MRP-ring", "udskift switch med scalance", "success"))
                choices.append(("2", "Åbn montage-arbejdsbænken for SCALANCE XB-200 og MRP-konfiguration", "switch workbench", "normal"))
                choices.append(("3", "Verificer netværkets determinisme med Wireshark", "åbn wireshark", "normal"))
                choices.append(("4", "Åbn efterforskningens sagstavle og opdater hypoteser", "sagstavle", "normal"))
                choices.append(("5", "Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
            else:
                choices.append(("1", "🔄 Modtræk (Guldstandard): Monter SCALANCE XB-200 & forbind PROFINET MRP-ring", "udskift switch med scalance", "success"))
                choices.append(("2", "🛠️ Montage: Åbn Switch Montage-arbejdsbænk for manuel montage", "switch workbench", "normal"))
                choices.append(("3", "📊 Verifikation: Wireshark - Verificer om DCP-stormen er stoppet", "åbn wireshark", "normal"))
                choices.append(("4", "🕵️ Sagstavle: Gennemse opdateret sagstavle ('sagstavle')", "sagstavle", "normal"))
                choices.append(("5", "⚡ Navigation: Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg Festo ventil-øen (deterministisk PROFINET RT)", "undersøg ventiler", "normal"))
        choices.append(("2", "📊 Wireshark: Inspicér PROFINET RT rammer", "åbn wireshark", "normal"))
        choices.append(("3", "⚡ Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
        choices.append(("4", "🖥️ Gå til Kontrolrummet", "gå til kontrolrummet", "normal"))
        choices.append(("5", "🚰 Gå til Pumpehuset", "gå til pumpehuset", "normal"))
        return choices
