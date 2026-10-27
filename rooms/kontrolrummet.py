"""Kontrolrummet / IDMZ - Purdue Level 3.5: SCADA & Real-World OPC UA PKI Hardening."""

from __future__ import annotations

from typing import Any
from rooms.base import BaseRoom


class KontrolrummetRoom(BaseRoom):
    def __init__(self) -> None:
        super().__init__(
            key="kontrolrummet",
            title="Kontrolrummet / IDMZ",
            purdue_level="Purdue Level 3.5: Industrial DMZ (IDMZ)",
            zone="Zone 4: Kontrol & Driftsovervågning",
            description=(
                "SCADA-arbejdsstationen viser procesalarmer, historikserveren blinker, og en mistænkelig "
                "Teltonika 4G-router sidder i vægkontakten bag racket. En åben OPC UA server på port 4840 "
                "lækker procesdata og tillader anonym adgang, mens kaffemaskinen brygger trofast."
            ),
            hotspots=["scada pc", "opc ua server", "4g-router", "kaffemaskine"],
        )

    def get_description(self, engine: Any) -> str:
        flags = getattr(engine, "flags", set())
        variant = getattr(engine, "room_variants", {}).get("kontrolrummet", "A")

        if getattr(engine, "scada_log_interrupted", False):
            return (
                "I kontrolrummet blinker en skarp orange advarsel på operatørskærmen: 'MILJØLOGGING AFBRUDT - PORT 4840 TIMEOUT'. "
                "Lovpligtige miljødata overføres ikke til Miljøstyrelsen, fordi port 4840 blev blokeret groft i firewallen!"
            )
        if "chapter-4-done" in flags:
            return (
                "Kontrolrummet ånder lettet op. WinCC SCADA-arbejdsstationen viser en ren, grøn procesoversigt med "
                "krypteret OPC UA SignAndEncrypt (Basic256Sha256) og gensidig X.509 certifikat-validering. "
                "Hullet i IDMZ-perimeteren er forseglet, og det konfiskerede fjernadgangs-udstyr ligger slukket i bevisskuffen."
            )
        if variant == "B":
            return (
                "SCADA-arbejdsstationens store skærme flimrer med procesalarmer. Under det hævede gulv ved patchpanelet "
                "blinker et skjult, uautoriseret Wi-Fi Access Point koblet direkte i SCADA-switchen! "
                "Samtidig afslører overvågningen, at en klient misbruger et kompromitteret leverandør-certifikat og åben "
                "OPC UA (SecurityPolicy: None & Anonymous) på port 4840 til at tappe procesdata."
            )
        if variant == "C":
            return (
                "SCADA-arbejdsstationens store skærme flimrer med procesalarmer. Bag IDMZ-patchpanelet sidder en "
                "uautoriseret mini-tunnelboks, der eksponerer Remote Desktop (TCP Port 3389) uden MFA! "
                "Samtidig afslører netværksovervågningen, at OPC UA serveren på port 4840 kører ukrypteret "
                "(SecurityPolicy: None) og tillader anonym læse-/skriveadgang."
            )
        return (
            "SCADA-arbejdsstationens store skærme flimrer med procesalarmer og afbrudte telemetri-grafer. "
            "I hjørnet bag 19\" server-racket i IDMZ'en pulserer et svagt blåt diodelys: En uautoriseret Teltonika "
            "RUT950 4G-router sidder i vægstikket med et patchkabel direkte i anlæggets backbone! "
            "Samtidig afslører netværksovervågningen, at anlæggets OPC UA server på port 4840 lækker rå procestags "
            "og kemikaliedoseringer ud til enhver anonym klient uden certifikat."
        )

    def get_choices(self, engine: Any) -> list[tuple[str, str, str, str]]:
        flags = getattr(engine, "flags", set())
        variant = getattr(engine, "room_variants", {}).get("kontrolrummet", "A")
        choices: list[tuple[str, str, str, str]] = []

        if getattr(engine, "scada_log_interrupted", False):
            choices.append(("1", "🔧 Genåbn Port 4840 og skift til selektiv X.509 certifikat-validering", "aktiver opc certifikater", "success"))
            choices.append(("2", "🔍 Inspicér SCADA-fejllog for afbrudt miljørapportering", "undersøg scada pc", "normal"))
            return choices

        if "chapter-4-done" not in flags:
            choices.append(("1", "🔍 Inspicér WinCC SCADA PC og operatør-sessionslog fra nattevagten", "undersøg scada pc", "normal"))
            choices.append(("2", "📊 Kør tshark og inspicér sessioner i Kontrolrummet / IDMZ", "åbn wireshark", "normal"))
            if "router-disconnected" not in flags:
                if variant == "B":
                    choices.append(("3", "🔌 Frakobl det skjulte Wi-Fi Access Point ved patchpanelet", "frakobl 4g-router", "normal"))
                elif variant == "C":
                    choices.append(("3", "🔌 Frakobl den uautoriserede RDP/VPN tunnel-boks bag patchpanelet", "frakobl 4g-router", "normal"))
                else:
                    choices.append(("3", "🔌 Frakobl Teltonika RUT950 4G-routeren bag server-racket", "frakobl 4g-router", "normal"))
            if "cert-trusted" not in flags:
                if variant == "B":
                    choices.append(("4", "📜 Spær det stjålne certifikat (CRL) og godkend WinCC SCADA X.509 certifikatet", "godkend scada certifikat", "normal"))
                else:
                    choices.append(("4", "📜 Flyt WinCC SCADA klientens X.509 certifikat til 'Trusted' i truststoren", "godkend scada certifikat", "normal"))
            if "opc-crypto-active" not in flags:
                choices.append(("5", "🔒 Konfigurer OPC UA til Basic256Sha256 og SignAndEncrypt", "aktiver opc kryptering", "normal"))
            if "anon-disabled" not in flags:
                choices.append(("6", "🚫 Deaktivér Anonymous UserToken på port 4840 og håndhæv RBAC / MFA", "deaktiver anonymous opc", "normal"))
            choices.append(("7", "🛡️ Bloker al TCP port 4840 trafik i IDMZ-firewallen", "bloker port 4840 totalt", "normal"))
            return choices

        # Zone already stabilized -> offer navigation to next active mission room
        next_room = getattr(engine, "get_current_target_room", lambda: "indgangen")()
        choices.append(("1", "🔍 Undersøg WinCC SCADA PC (alle parametre grønne)", "undersøg scada pc", "normal"))
        choices.append(("2", "📊 Kør tshark og bekræft krypteret OPC.TCP session", "åbn wireshark", "normal"))
        choices.append(("3", f"➡️ Gå videre til næste aktive zone ({next_room})", f"gå til {next_room}", "primary"))
        return choices
