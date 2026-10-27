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
        ch = getattr(engine, "chapter", 1)

        if getattr(engine, "scada_log_interrupted", False):
            return (
                "I kontrolrummet blinker en skarp orange advarsel på operatørskærmen: 'MILJØLOGGING AFBRUDT - PORT 4840 TIMEOUT'. "
                "Lovpligtige miljødata overføres ikke til Miljøstyrelsen, fordi port 4840 blev blokeret groft i firewallen!"
            )
        if "chapter-4-done" in flags:
            return (
                "Kontrolrummet ånder lettet op. WinCC SCADA-arbejdsstationen viser en ren, grøn procesoversigt med "
                "krypteret OPC UA SignAndEncrypt (Basic256Sha256) og gensidig X.509 certifikat-validering. "
                "Hullet i IDMZ-perimeteren er forseglet, og den konfiskerede 4G-router ligger slukket i bevisskuffen."
            )
        if ch == 4:
            return (
                "SCADA-arbejdsstationens store skærme flimrer med procesalarmer og afbrudte telemetri-grafer. "
                "I hjørnet bag 19\" server-racket i IDMZ'en pulserer et svagt blåt diodelys: En uautoriseret Teltonika "
                "RUT950 4G-router sidder i vægstikket med et patchkabel direkte i anlæggets backbone! "
                "Samtidig afslører netværksovervågningen, at anlæggets OPC UA server på port 4840 lækker rå procestags "
                "og kemikaliedoseringer ud til enhver anonym klient uden certifikat."
            )
        return self.description

    def get_choices(self, engine: Any) -> list[tuple[str, str, str, str]]:
        flags = getattr(engine, "flags", set())
        ch = getattr(engine, "chapter", 1)
        choices: list[tuple[str, str, str, str]] = []

        if getattr(engine, "scada_log_interrupted", False):
            choices.append(("1", "🔧 Genåbn Port 4840 og skift til selektiv X.509 certifikat-validering", "aktiver opc certifikater", "success"))
            choices.append(("2", "🔍 Inspicér SCADA-fejllog for afbrudt miljørapportering", "undersøg scada pc", "normal"))
            return choices

        if ch == 4:
            choices.append(("1", "🔍 Inspicér WinCC SCADA PC og operatør-sessionslog fra nattevagten", "undersøg scada pc", "normal"))
            choices.append(("2", "📊 Kør tshark og inspicér OPC.TCP sessioner på port 4840", "åbn wireshark", "normal"))
            if "router-disconnected" not in flags:
                choices.append(("3", "🔌 Frakobl Teltonika RUT950 4G-routeren bag server-racket", "frakobl 4g-router", "normal"))
            if "cert-trusted" not in flags:
                choices.append(("4", "📜 Flyt WinCC SCADA klientens X.509 certifikat til 'Trusted' i truststoren", "godkend scada certifikat", "normal"))
            if "opc-crypto-active" not in flags:
                choices.append(("5", "🔒 Konfigurer OPC UA til Basic256Sha256 og SignAndEncrypt", "aktiver opc kryptering", "normal"))
            if "anon-disabled" not in flags:
                choices.append(("6", "🚫 Deaktivér Anonymous UserToken på port 4840 og håndhæv RBAC", "deaktiver anonymous opc", "normal"))
            choices.append(("7", "🛡️ Bloker al TCP port 4840 trafik i IDMZ-firewallen", "bloker port 4840 totalt", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg WinCC SCADA PC (alle parametre grønne)", "undersøg scada pc", "normal"))
        choices.append(("2", "📊 Kør tshark og bekræft krypteret OPC.TCP session", "åbn wireshark", "normal"))
        choices.append(("3", "🚪 Gå til Hovedindgangen (Fremlæg sagen for Tilsynet)", "gå til indgangen", "primary"))
        return choices
