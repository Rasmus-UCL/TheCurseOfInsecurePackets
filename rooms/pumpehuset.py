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
                choices.append(("1", "Kør tshark og overvåg Modbus TCP-trafik på port 502", "tshark -Y \"modbus\"", "normal"))
                choices.append(("2", "Vis tshark manual og OT-displayfiltre", "man tshark", "normal"))
                choices.append(("3", "Monter SCALANCE S615 firewall på TS35 DIN-skinnen foran frekvensomformeren", "firewall workbench", "success"))
                choices.append(("4", "Opret firewall-regel: firewall rule add --allow-fc 3 --drop-fc 6", "firewall rule add --allow-fc 3 --drop-fc 6", "success"))
                choices.append(("5", "Opret firewall-regel: firewall rule add --drop-fc 6", "firewall rule add --drop-fc 6", "warning"))
                choices.append(("6", "Inspicér firewall-regler og telemetri-status", "firewall status", "normal"))
                choices.append(("7", "Blokér al TCP port 502 trafik i netværket via en generel regel", "bloker port 502", "warning"))
                choices.append(("8", "Afbryd forsyningen til frekvensomformeren ved at udløse hovedafbryderen manuelt", "hård nødnedlukning af vfd", "danger"))
                choices.append(("9", "Inspicér Pumpe 2 manometer og mekaniske vibrationer", "undersøg pumpe 2", "normal"))
                choices.append(("10", "Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
            else:
                choices.append(("1", "📊 tshark: Analyser de ondsindede Modbus TCP-pakker på Port 502 ('tshark -Y \"modbus\"')", "tshark -Y \"modbus\"", "normal"))
                choices.append(("2", "📖 man tshark: Lær display-filtre til industrielle protokoller", "man tshark", "normal"))
                choices.append(("3", "🔧 TS35 DIN-skinne: Åbn arbejdsbænk og monter SCALANCE S615 firewall foran VFD", "firewall workbench", "success"))
                choices.append(("4", "🔒 'firewall rule add --allow-fc 3 --drop-fc 6': L7 DPI Guldstandard (Tillad FC 03 læsning & drop FC 06)", "firewall rule add --allow-fc 3 --drop-fc 6", "success"))
                choices.append(("5", "⚠️ Faldgrube: 'firewall rule add --drop-fc 6' (Drop FC 06, men glem at allowe FC 03 -> SCADA blindhed!)", "firewall rule add --drop-fc 6", "warning"))
                choices.append(("6", "🔍 firewall status: Se SCALANCE S615 regeltabel og pakketællere", "firewall status", "normal"))
                choices.append(("7", "⚠️ Faldgrube 1 (Grov Layer 3 blokering): Drop al port 502 trafik i netværket (Blind SCADA)", "bloker port 502", "warning"))
                choices.append(("8", "⚡ Faldgrube 2 (Vandslag): Træk nødstrømsafbryderen til VFD under last (Udløser K1)", "hård nødnedlukning af vfd", "danger"))
                choices.append(("9", "🔍 Undersøg Pumpe 2 manometer (vibrerer på 133.7 Bar)", "undersøg pumpe 2", "normal"))
                choices.append(("10", "⚡ Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg Pumpe 2 (stabil drift på 42.0 Bar)", "undersøg pumpe 2", "normal"))
        choices.append(("2", "📊 Wireshark: Inspicér VLAN 10 telemetri", "åbn wireshark", "normal"))
        choices.append(("3", "💨 Gå til Ventil-øen (L1)", "gå til ventil-oen", "normal"))
        choices.append(("4", "⚡ Gå til Hoved-el-tavlen (L1/L2)", "gå til el-tavlen", "normal"))
        choices.append(("5", "🖥️ Gå til Kontrolrummet (IDMZ)", "gå til kontrolrummet", "normal"))
        return choices
