"""Pumpehuset - Purdue Level 1: Basic Process Control & Drev."""

from __future__ import annotations

from typing import Any
from rooms.base import BaseRoom


class PumpehusetRoom(BaseRoom):
    def __init__(self) -> None:
        super().__init__(
            key="pumpehuset",
            title="Pumpehuset",
            purdue_level="Purdue Level 1: Basic Process Control & Drev",
            zone="Zone 1: Pumpe-celle (VLAN 10)",
            description=(
                "Pumpehuset danner fundamentet for byens drikkevandsforsyning. "
                "Tre massive centrifugalpumper brummer dybt. Pumpe 2 skriger i lejerne og manometeret vibrerer i rød zone!"
            ),
            hotspots=["pumpe 2", "frekvensomformer", "ts35 din-skinne", "scada"],
        )

    def get_description(self, engine: Any) -> str:
        flags = getattr(engine, "flags", set())
        ch = getattr(engine, "chapter", 1)
        if getattr(engine, "breaker_tripped", False):
            return (
                "Pumpehuset er badet i en trykkende, unormal stilhed. Pumpe 2 er brat stoppet, "
                "og sikkerhedsrelæ K1 i Hoved-el-tavlen er udløst på grund af et voldsomt hydraulisk tilbageslag. "
                "Frekvensomformeren er strømløs, og kondensdryp falder langsomt fra de spændte rør. "
                "Hans McDonald stirrer blegt på tavlen: 'K1 har slået fra! Vi skal ind i el-tavlen og nulstille relæet!'"
            )
        if getattr(engine, "scada_blind", False):
            return (
                "Pumpe 2 brummer monotont, men på SCALANCE S615 firewallens front blinker en advarselsdiode. "
                "SCADA er totalt blindet! Transmitterne kan ikke sende måledata (FC 03) igennem, og kontrolrummet "
                "sejler i blinde uden trykaflæsning. Hans råber over radioen: 'Hvorfor viser WinCC ingen værdier?!'"
            )
        if "chapter-1-done" in flags:
            return (
                "Pumpehuset summer roligt og harmonisk. Pumpe 2 arbejder stabilt ved 42.0 Bar og 50 Hz. "
                "På DIN-skinnen blinker SCALANCE S615 routeren betryggende med grønne dioder, mens "
                "Modbus DPI-inspektionen effektivt filtrerer uautoriserede register-skrivninger fra."
            )
        if ch == 1:
            return (
                "Pumpehuset ryster under fødderne på dig! Tre gigantiske centrifugalpumper brummer i dybe basfrekvenser, "
                "men Pumpe 2 skriger med en skærende metallisk lyd. Manometeret på afgangsrøret hamrer febrilsk frem og "
                "tilbage i den røde zone ved 14.8 bar. Hans McDonald holder sig for ørerne og råber over larmen:\n"
                "'Kavitationen er ved at pulverisere pumpehjulet! Nogen oversvømmer vores frekvensomformer med Modbus-skrivninger!'"
            )
        return self.description

    def get_choices(self, engine: Any) -> list[tuple[str, str, str, str]]:
        flags = getattr(engine, "flags", set())
        ch = getattr(engine, "chapter", 1)
        mode = getattr(engine, "game_mode", "teach")
        choices: list[tuple[str, str, str, str]] = []

        if getattr(engine, "breaker_tripped", False):
            if mode == "exam":
                choices.append(("1", "Gå til Hoved-el-tavlen for at inspicere sikringsgruppen", "gå til el-tavlen", "danger"))
                choices.append(("2", "Inspicér den spændingsløse frekvensomformer", "undersøg frekvensomformer", "normal"))
                choices.append(("3", "Aflæs Pumpe 2 manometer og differenstryk", "undersøg pumpe 2", "normal"))
            else:
                choices.append(("1", "⚡ Gå til Hoved-el-tavlen for at nulstille udløst K1-sikringsrelæ", "gå til el-tavlen", "danger"))
                choices.append(("2", "🔍 Undersøg den strømløse frekvensomformer", "undersøg frekvensomformer", "normal"))
                choices.append(("3", "🔍 Undersøg Pumpe 2 manometer", "undersøg pumpe 2", "normal"))
            return choices

        # If user is currently focused on the DIN-rail montage workbench
        if getattr(engine, "active_workbench", None) == "vfd_workbench" and ch == 1:
            if mode == "exam":
                choices.append(("1", "Fastgør SCALANCE S615 routeren på TS35 DIN-skinnen", "monter scalance på din-skinne", "normal"))
                choices.append(("2", "Forbind patchkabel fra VFD til LAN (Port P1) og uplink til WAN (Port P5)", "kobl kabler til scalance", "normal"))
                choices.append(("3", "Opret L7 DPI regel: firewall rule add --allow-fc 3 --drop-fc 6", "firewall rule add --allow-fc 3 --drop-fc 6", "success"))
                choices.append(("4", "Opret firewall regel: firewall rule add --drop-fc 6", "firewall rule add --drop-fc 6", "warning"))
                choices.append(("5", "Forbind VFD til WAN-port P5 og switchen til LAN-port P1", "byt om på lan og wan", "danger"))
                choices.append(("6", "Luk arbejdsbænken og vend tilbage til Pumpehus-oversigten", "vis rum", "normal"))
            else:
                choices.append(("1", "🔌 Trin 1: Fastgør SCALANCE S615 routeren på TS35 DIN-skinnen", "monter scalance på din-skinne", "normal"))
                choices.append(("2", "🔀 Trin 2: Kobl patchkabler: VFD til LAN (Port P1) og anlægsnet til WAN (Port P5)", "kobl kabler til scalance", "normal"))
                choices.append(("3", "🔒 Trin 3 (Guldstandard): 'firewall rule add --allow-fc 3 --drop-fc 6' (Tillad FC 03 læsning & drop FC 06)", "firewall rule add --allow-fc 3 --drop-fc 6", "success"))
                choices.append(("4", "⚠️ Faldgrube: 'firewall rule add --drop-fc 6' (Glem allow FC 03 -> SCADA blindhed!)", "firewall rule add --drop-fc 6", "warning"))
                choices.append(("5", "⚠️ Faldgrube: Forbind VFD til WAN og netværk til LAN (Forkert kabling)", "byt om på lan og wan", "danger"))
                choices.append(("6", "🚪 Luk arbejdsbænken og vend tilbage til Pumpehus-oversigten", "vis rum", "normal"))
            return choices

        if ch == 1:
            if mode == "exam":
                choices.append(("1", "Inspicér Pumpe 2 manometer og mekaniske vibrationer", "undersøg pumpe 2", "normal"))
                choices.append(("2", "Kør tshark og overvåg Modbus TCP-trafik på port 502", "tshark -Y \"modbus\"", "normal"))
                choices.append(("3", "Spørg driftstekniker Hans om nylige servicebesøg på pumperne", "spørg hans om morten", "normal"))
                choices.append(("4", "Åbn efterforskningens sagstavle og opdater hypoteser", "sagstavle", "normal"))
                choices.append(("5", "Monter SCALANCE S615 firewall på TS35 DIN-skinnen foran frekvensomformeren", "firewall workbench", "success"))
                choices.append(("6", "Opret firewall-regel: firewall rule add --allow-fc 3 --drop-fc 6", "firewall rule add --allow-fc 3 --drop-fc 6", "success"))
                choices.append(("7", "Opret firewall-regel: firewall rule add --drop-fc 6", "firewall rule add --drop-fc 6", "warning"))
                choices.append(("8", "Blokér al TCP port 502 trafik i netværket via en generel regel", "bloker port 502", "warning"))
                choices.append(("9", "Afbryd forsyningen til frekvensomformeren ved at udløse hovedafbryderen manuelt", "hård nødnedlukning af vfd", "danger"))
                choices.append(("10", "Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
            else:
                choices.append(("1", "👁️ Trin 1 (Observation): Undersøg Pumpe 2 manometer og mærk lejevibrationer", "undersøg pumpe 2", "normal"))
                choices.append(("2", "📊 Trin 2 (Dataindsamling): tshark -Y \"modbus\" (Analyser ondsindede FC 06 pakker)", "tshark -Y \"modbus\"", "normal"))
                choices.append(("3", "☕ Trin 3 (Afhøring): Spørg Hans om eksterne serviceteknikere ('spørg hans om morten')", "spørg hans om morten", "normal"))
                choices.append(("4", "🕵️ Trin 4 (Sagstavle): Gennemse fundne spor og mistænkte ('sagstavle')", "sagstavle", "normal"))
                choices.append(("5", "🔧 Trin 5 (Modtræk): Åbn arbejdsbænk for TS35 DIN-skinne & SCALANCE S615", "firewall workbench", "success"))
                choices.append(("6", "🔒 Modtræk (Guldstandard): 'firewall rule add --allow-fc 3 --drop-fc 6' (L7 DPI)", "firewall rule add --allow-fc 3 --drop-fc 6", "success"))
                choices.append(("7", "⚠️ Faldgrube: 'firewall rule add --drop-fc 6' (Drop FC 06, men glem allow FC 03 -> SCADA blindhed!)", "firewall rule add --drop-fc 6", "warning"))
                choices.append(("8", "⚠️ Faldgrube 1 (Grov blokering): Drop al port 502 trafik i netværket (Blind SCADA)", "bloker port 502", "warning"))
                choices.append(("9", "⚡ Faldgrube 2 (Vandslag): Træk nødstrømsafbryderen til VFD under last (Udløser K1)", "hård nødnedlukning af vfd", "danger"))
                choices.append(("10", "⚡ Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg Pumpe 2 (stabil drift på 42.0 Bar)", "undersøg pumpe 2", "normal"))
        choices.append(("2", "📊 Wireshark: Inspicér VLAN 10 telemetri", "åbn wireshark", "normal"))
        choices.append(("3", "💨 Gå til Ventil-øen (L1)", "gå til ventil-oen", "normal"))
        choices.append(("4", "⚡ Gå til Hoved-el-tavlen (L1/L2)", "gå til el-tavlen", "normal"))
        choices.append(("5", "🖥️ Gå til Kontrolrummet (IDMZ)", "gå til kontrolrummet", "normal"))
        return choices
