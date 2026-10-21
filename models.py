"""Data objects shared by the command-line and graphical clients."""

from __future__ import annotations

from dataclasses import dataclass, field


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
    1: "Find og stop Modbus TCP-sabotagen i pumpehuset (IEC 62443-3-2 Zoner & Conduits).",
    2: "Stands PROFINET DCP-kaosset på ventil-øen (Layer 2 hærdning & Port Security).",
    3: "Bring S7-1500 sikkert tilbage fra STOP-mode (Backup & TIA Security Wizard).",
    4: "Luk den uautoriserede 4G-bagdør og hærd OPC UA i kontrolrummet (IDMZ & Certifikater).",
    5: "Fremlæg dokumentation og bestå NIS2-tilsynets revision (Artikel 21).",
}
