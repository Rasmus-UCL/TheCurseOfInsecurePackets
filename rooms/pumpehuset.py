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
        variant = getattr(engine, "room_variants", {}).get("pumpehuset", "A")
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
                "dybde-inspektionen effektivt beskytter frekvensomformeren mod uautoriserede skrivekald."
            )
        if variant == "B":
            return (
                "Pumpehuset ryster under fødderne på dig! Tre gigantiske centrifugalpumper brummer i dybe basfrekvenser, "
                "men Pumpe 2 skriger med en skærende metallisk lyd. Manometeret på afgangsrøret hamrer febrilsk frem og "
                "tilbage i den røde zone ved 14.8 bar. Hans McDonald holder sig for ørerne og råber over larmen:\n"
                "'Kavitationen er ved at pulverisere pumpehjulet! Nogen misbruger åben SNMPv1 (community: private) og ARP-spoofing til at tvinge VFD'en op på 120 Hz!'"
            )
        if variant == "C":
            return (
                "Pumpehuset ryster under fødderne på dig! Tre gigantiske centrifugalpumper brummer i dybe basfrekvenser, "
                "men Pumpe 2 skriger med en skærende metallisk lyd. Manometeret på afgangsrøret hamrer febrilsk frem og "
                "tilbage i den røde zone ved 14.8 bar. Hans McDonald holder sig for ørerne og råber over larmen:\n"
                "'Kavitationen er ved at pulverisere pumpehjulet! Nogen er logget ind på VFD'ens ubeskyttede HTTP-webserver (admin/admin) og har låst setpunktet på 120 Hz!'"
            )
        return (
            "Pumpehuset ryster under fødderne på dig! Tre gigantiske centrifugalpumper brummer i dybe basfrekvenser, "
            "men Pumpe 2 skriger med en skærende metallisk lyd. Manometeret på afgangsrøret hamrer febrilsk frem og "
            "tilbage i den røde zone ved 14.8 bar. Hans McDonald holder sig for ørerne og råber over larmen:\n"
            "'Kavitationen er ved at pulverisere pumpehjulet! Nogen oversvømmer vores frekvensomformer med Modbus-skrivninger!'"
        )

    def get_choices(self, engine: Any) -> list[tuple[str, str, str, str]]:
        flags = getattr(engine, "flags", set())
        variant = getattr(engine, "room_variants", {}).get("pumpehuset", "A")
        choices: list[tuple[str, str, str, str]] = []

        if getattr(engine, "breaker_tripped", False):
            choices.append(("1", "⚡ Gå til Hoved-el-tavlen for at inspicere og nulstille K1-sikringsrelæet", "gå til el-tavlen", "danger"))
            choices.append(("2", "🔍 Inspicér den spændingsløse frekvensomformer", "undersøg frekvensomformer", "normal"))
            choices.append(("3", "🔍 Aflæs Pumpe 2 manometer og differenstryk", "undersøg pumpe 2", "normal"))
            return choices

        # If user is currently focused on the DIN-rail montage workbench (Sequential 3-step workflow)
        if getattr(engine, "active_workbench", None) == "vfd_workbench" and "chapter-1-done" not in flags:
            if not getattr(engine, "vfd_mounted", False):
                choices.append(("1", "🔌 [Trin 1/3] Fastgør SCALANCE S615 sikkerhedsrouteren på TS35 DIN-skinnen", "monter scalance på din-skinne", "primary"))
                choices.append(("2", "🚪 Luk arbejdsbænken og vend tilbage til Pumpehuset", "vis rum", "normal"))
                return choices
            if not getattr(engine, "vfd_cabled", False) or getattr(engine, "wrong_cabling", False):
                choices.append(("1", "🔀 [Trin 2/3] Forbind VFD til LAN-port (P1) og anlægsnetværk til WAN-port (P5)", "kobl kabler til scalance", "primary"))
                choices.append(("2", "🔀 [Trin 2/3] Forbind VFD til WAN-port (P5) og anlægsnetværk til LAN-port (P1)", "byt om på lan og wan", "normal"))
                choices.append(("3", "🚪 Luk arbejdsbænken og vend tilbage til Pumpehuset", "vis rum", "normal"))
                return choices
            if variant == "B":
                choices.append(("1", "🛡️ [Trin 3/3] Spær SNMPv1 Write ('private'), aktivér ARP Inspection (DAI) og tillad SCADA FC 03", "firewall rule add --allow-fc 3 --drop-fc 6", "primary"))
                choices.append(("2", "🛡️ [Trin 3/3] Blokér al trafik på SCALANCE uden whitelist til SCADA-telemetri", "firewall rule add --drop-fc 6", "normal"))
            elif variant == "C":
                choices.append(("1", "🛡️ [Trin 3/3] Spær ukrypteret HTTP Port 80, lås VFD-setpunkt til PLC og tillad SCADA FC 03", "firewall rule add --allow-fc 3 --drop-fc 6", "primary"))
                choices.append(("2", "🛡️ [Trin 3/3] Blokér al trafik på SCALANCE uden whitelist til SCADA-telemetri", "firewall rule add --drop-fc 6", "normal"))
            else:
                choices.append(("1", "🛡️ [Trin 3/3] Opret regel: 'firewall rule add --allow-fc 3 --drop-fc 6'", "firewall rule add --allow-fc 3 --drop-fc 6", "primary"))
                choices.append(("2", "🛡️ [Trin 3/3] Opret regel: 'firewall rule add --drop-fc 6'", "firewall rule add --drop-fc 6", "normal"))
            choices.append(("3", "🔀 Ændr kabling: Forbind VFD til WAN-port (P5) og anlægsnetværk til LAN-port (P1)", "byt om på lan og wan", "normal"))
            choices.append(("4", "🚪 Luk arbejdsbænken og vend tilbage til Pumpehuset", "vis rum", "normal"))
            return choices

        if "chapter-1-done" not in flags:
            choices.append(("1", "🔍 Inspicér Pumpe 2 manometer og mekaniske vibrationer", "undersøg pumpe 2", "normal"))
            if variant == "B":
                choices.append(("2", "📊 Kør tshark og overvåg SNMPv1 (UDP 161) og ARP-trafik i Pumpehuset", "tshark", "normal"))
            elif variant == "C":
                choices.append(("2", "📊 Kør tshark og overvåg HTTP-override (Port 80) og Modbus-trafik", "tshark", "normal"))
            else:
                choices.append(("2", "📊 Kør tshark og overvåg Modbus TCP-trafik på port 502", "tshark -Y \"modbus\"", "normal"))
            choices.append(("3", "☕ Spørg Hans om nylige servicebesøg på pumperne", "spørg hans om morten", "normal"))
            choices.append(("4", "🔧 Åbn arbejdsbænk for TS35 DIN-skinne & SCALANCE S615 firewall", "firewall workbench", "primary"))
            choices.append(("5", "🛡️ Blokér al TCP port 502 trafik i netværket med en generel regel", "bloker port 502", "normal"))
            choices.append(("6", "⚡ Afbryd forsyningen til frekvensomformeren på hovedafbryderen", "hård nødnedlukning af vfd", "normal"))
            return choices

        # Zone already stabilized -> offer navigation to next active mission room
        next_room = getattr(engine, "get_current_target_room", lambda: "ventil-oen")()
        choices.append(("1", "🔍 Undersøg Pumpe 2 (stabil drift på 42.0 Bar)", "undersøg pumpe 2", "normal"))
        choices.append(("2", "📊 Kør tshark og inspicér VLAN 10 telemetri", "åbn wireshark", "normal"))
        choices.append(("3", f"➡️ Gå videre til næste aktive zone ({next_room})", f"gå til {next_room}", "primary"))
        return choices
