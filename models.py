"""Data objects shared by the command-line and graphical clients."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricValues:
    """The 4 core operational and security dimensions of Nordic H2O Utility."""

    drift: int = 80          # 0-100%: Uptime, vandforsyning, trykstabilitet, pumpetilstand
    sikkerhed: int = 25      # 0-100%: Firewall, segmentering, hardening, lukkede sårbarheder
    compliance: int = 40     # 0-100%: NIS2 Artikel 21/23, dokumentation, chain of custody
    tillid: int = 50         # 0-100%: Hans' partnerskab og moral, ledelsens tiltro

    history: list[dict[str, Any]] = field(default_factory=list)

    def adjust_drift(self, delta: int, reason: str = "") -> None:
        old = self.drift
        self.drift = max(0, min(100, self.drift + delta))
        self.history.append({"metric": "drift", "old": old, "new": self.drift, "delta": delta, "reason": reason})

    def adjust_sikkerhed(self, delta: int, reason: str = "") -> None:
        old = self.sikkerhed
        self.sikkerhed = max(0, min(100, self.sikkerhed + delta))
        self.history.append({"metric": "sikkerhed", "old": old, "new": self.sikkerhed, "delta": delta, "reason": reason})

    def adjust_compliance(self, delta: int, reason: str = "") -> None:
        old = self.compliance
        self.compliance = max(0, min(100, self.compliance + delta))
        self.history.append({"metric": "compliance", "old": old, "new": self.compliance, "delta": delta, "reason": reason})

    def adjust_tillid(self, delta: int, reason: str = "") -> None:
        old = self.tillid
        self.tillid = max(0, min(100, self.tillid + delta))
        self.history.append({"metric": "tillid", "old": old, "new": self.tillid, "delta": delta, "reason": reason})

    def get_summary(self) -> dict[str, int]:
        return {
            "drift": self.drift,
            "sikkerhed": self.sikkerhed,
            "compliance": self.compliance,
            "tillid": self.tillid,
        }


@dataclass
class Clue:
    """An individual piece of forensic or investigative evidence found at the plant."""

    id: str
    title: str
    category: str            # "Netværk", "Fysisk", "Systemlog", "Vidneudsagn", "Konfiguration"
    discovery_room: str
    description: str
    analysis: str
    associated_suspects: list[str] = field(default_factory=list)
    discovered: bool = False
    discovered_time: str = ""
    analyzed: bool = False


@dataclass
class Suspect:
    """A person of interest or hypothesis regarding the incident at Nordic H2O Utility."""

    id: str
    name: str
    role: str
    theory: str
    opportunity: str
    motive: str
    suspicion_score: int = 0  # 0-100%
    status: str = "Aktiv efterforskning"  # "Aktiv efterforskning", "Hovedmistænkt", "Udelukket", "Bekræftet"
    notes: list[str] = field(default_factory=list)


@dataclass
class Player:
    name: str = ""
    education: str = ""
    inventory: set[str] = field(
        default_factory=lambda: {
            "laptop",
            "rj45 patchkabel",
            "konsolkabel",
            "usb-stik med backup",
            "skruetrækker",
            "kaffe",
            "scalance xb-200 managed switch",
        }
    )


@dataclass(frozen=True)
class Room:
    key: str
    title: str
    description: str
    hotspots: tuple[str, ...]
    purdue_level: str = "Purdue Level 1: Basic Control"
    zone: str = "Zone 1"


ROOMS = {
    "indgangen": Room(
        "indgangen",
        "Hovedindgangen",
        "Du står foran hovedindgangen til Nordic H2O Utility. Kontrolrummet ligger mod nord, "
        "og en håndskrevet pil peger mod pumpehuset i produktionshallen.",
        ("hoveddør", "skilt"),
        purdue_level="Purdue Level 4: Enterprise & Adgangszone",
        zone="Zone 0: Perimeter",
    ),
    "pumpehuset": Room(
        "pumpehuset",
        "Pumpehuset",
        "Tre massive centrifugalpumper brummer. Pumpe 2 lyder som en overkogt elkedel, "
        "mens SCADA-panelet viser 'ALT NORMALT'. Manometeret på pumpen er faretruende tæt på rød zone.",
        ("pumpe 2", "scada", "frekvensomformer"),
        purdue_level="Purdue Level 1: Basic Process Control",
        zone="Zone 1: Pumpe-celle (VLAN 10)",
    ),
    "ventil-oen": Room(
        "ventil-oen",
        "Ventil-øen",
        "PROFINET-kablerne snor sig mod den decentrale ventil-ø. Ventilerne åbner og lukker "
        "i et hektisk kaos, og trykluften hvisler. Pumperne risikerer kavitation!",
        ("ventiler", "unmanaged switch", "rogue raspberry pi"),
        purdue_level="Purdue Level 1: Distributed I/O Zone",
        zone="Zone 2: Feldbus & I/O (VLAN 20)",
    ),
    "el-tavlen": Room(
        "el-tavlen",
        "Hoved-el-tavlen",
        "Hoved-el-tavlen summer dybt. En Siemens S7-1500 står med blinkende rød STOP-diode. "
        "Ved siden af ligger en ældre unmanaged switch og en fabriksny SCALANCE S615 i sin papkasse.",
        ("s7-1500", "d-link switch", "scalance s615"),
        purdue_level="Purdue Level 1/2: PLC & Netværkscenter",
        zone="Zone 3: Hovedtavle & Sikkerheds-PLC",
    ),
    "kontrolrummet": Room(
        "kontrolrummet",
        "Kontrolrummet / DMZ",
        "SCADA-arbejdsstationen viser log-alarmer, historikserveren blinker, og en mistænkelig "
        "4G-router sidder i vægkontakten bag racket. En åben OPC UA server lækker opskriftsdata, "
        "mens kaffemaskinen brygger trofast.",
        ("scada pc", "4g-router", "opc ua server", "kaffemaskine"),
        purdue_level="Purdue Level 3.5: Industrial DMZ (IDMZ)",
        zone="Zone 4: Kontrol & Driftsovervågning",
    ),
}


OBJECTIVES = {
    0: "Intro-Tutorial: Gennemfør Hans' sikkerheds- og udstyrstjek i Indgangen (eller vælg 'Spring over').",
    1: "Find og stop Modbus TCP-sabotagen i pumpehuset (IEC 62443-3-2 Zoner & Conduits).",
    2: "Stands PROFINET DCP-kaosset på ventil-øen (Layer 2 hærdning & Port Security).",
    3: "Bring S7-1500 sikkert tilbage fra STOP-mode (Backup & TIA Security Wizard).",
    4: "Luk den uautoriserede 4G-bagdør og hærd OPC UA i kontrolrummet (IDMZ & Certifikater).",
    5: "Fremlæg dokumentation og bestå NIS2-tilsynets revision (Artikel 21).",
}
