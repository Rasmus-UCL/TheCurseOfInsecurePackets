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
        mode = getattr(engine, "game_mode", "teach")
        choices: list[tuple[str, str, str, str]] = []

        if getattr(engine, "scada_log_interrupted", False):
            if mode == "exam":
                choices.append(("1", "Genåbn Port 4840 og skift til selektiv X.509 certifikat-validering", "aktiver opc certifikater", "success"))
                choices.append(("2", "Inspicér SCADA-fejllog for afbrudt miljørapportering", "undersøg scada pc", "normal"))
                choices.append(("3", "Gå til Hovedindgangen", "gå til indgangen", "normal"))
            else:
                choices.append(("1", "🔧 Genåbn Port 4840 & skift til selektiv X.509 certifikat-validering", "aktiver opc certifikater", "success"))
                choices.append(("2", "🔍 Undersøg SCADA-fejllog for afbrudt miljørapportering", "undersøg scada pc", "normal"))
                choices.append(("3", "🚪 Gå til Hovedindgangen", "gå til indgangen", "normal"))
            return choices

        if ch == 4:
            if mode == "exam":
                choices.append(("1", "Inspicér WinCC SCADA PC og operatør-sessionslog", "undersøg scada pc", "normal"))
                choices.append(("2", "Inspicér 4G-routerens IP-konfiguration og aktive VPN-tunneler", "undersøg 4g-router", "normal"))
                choices.append(("3", "Åbn Wireshark og inspicér ukrypterede OPC.TCP sessioner på port 4840", "åbn wireshark", "normal"))
                choices.append(("4", "Spørg driftstekniker Hans om operatørvagter og eksterne forbindelser", "spørg hans om kim", "normal"))
                choices.append(("5", "Åbn efterforskningens sagstavle og opdater hypoteser", "sagstavle", "normal"))
                if "router-disconnected" not in flags:
                    choices.append(("6", "Frakobl Teltonika RUT950 4G-routeren og afbryd den eksterne cellulære uplink", "frakobl 4g-router", "success"))
                if "cert-trusted" not in flags:
                    choices.append(("7", "Godkend WinCC SCADA klientens X.509 certifikat i OPC UA serverens truststore", "godkend scada certifikat", "success"))
                if "opc-crypto-active" not in flags:
                    choices.append(("8", "Konfigurer OPC UA endpoint til Basic256Sha256 og MessageSecurityMode SignAndEncrypt", "aktiver opc kryptering", "success"))
                if "anon-disabled" not in flags:
                    choices.append(("9", "Deaktivér Anonymous UserTokenType på port 4840 og håndhæv rollebaseret adgangskontrol", "deaktiver anonymous opc", "success"))
                choices.append(("10", "Bloker al TCP port 4840 trafik i IDMZ-firewallen for at stoppe datalækage", "bloker port 4840 totalt", "warning"))
                choices.append(("11", "Gå til Hovedindgangen", "gå til indgangen", "normal"))
            else:
                choices.append(("1", "👁️ Trin 1 (Observation): Undersøg WinCC SCADA PC & nattens hændelseslog", "undersøg scada pc", "normal"))
                choices.append(("2", "🔍 Trin 2 (Dataindsamling): Undersøg 4G-routeren bag racket (SIM & VPN-tunnel)", "undersøg 4g-router", "normal"))
                choices.append(("3", "📊 Trin 3 (Dataindsamling): Wireshark / tshark (Analyser rå OPC.TCP på Port 4840)", "åbn wireshark", "normal"))
                choices.append(("4", "☕ Trin 4 (Afhøring): Spørg Hans om Kims nattevagt og 4G-modemet ('spørg hans om kim')", "spørg hans om kim", "normal"))
                choices.append(("5", "🕵️ Trin 5 (Sagstavle): Gennemse spor og opdater hovedmistænkte ('sagstavle')", "sagstavle", "normal"))
                if "router-disconnected" not in flags:
                    choices.append(("6", "🔌 Modtræk 1 (Perimeter): Frakobl & konfisker den uautoriserede 4G-router", "frakobl 4g-router", "success"))
                if "cert-trusted" not in flags:
                    choices.append(("7", "📜 Modtræk 2 (PKI): Flyt WinCC SCADA certifikat fra 'Rejected' til 'Trusted'", "godkend scada certifikat", "success"))
                if "opc-crypto-active" not in flags:
                    choices.append(("8", "🔒 Modtræk 3 (Kryptering): Skift SecurityPolicy til Basic256Sha256 / SignAndEncrypt", "aktiver opc kryptering", "success"))
                if "anon-disabled" not in flags:
                    choices.append(("9", "🚫 Modtræk 4 (Adgangskontrol): Deaktivér Anonymous User Token & håndhæv RBAC", "deaktiver anonymous opc", "success"))
                choices.append(("10", "🛡️ Faldgrube: Bloker Port 4840 totalt i firewallen (Afbryder miljølogning!)", "bloker port 4840 totalt", "warning"))
                choices.append(("11", "🚪 Navigation: Gå til Hovedindgangen", "gå til indgangen", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg WinCC SCADA PC (alle parametre grønne)", "undersøg scada pc", "normal"))
        choices.append(("2", "📊 Wireshark: Bekræft krypteret OPC.TCP session", "åbn wireshark", "normal"))
        choices.append(("3", "🚪 Gå til Hovedindgangen", "gå til indgangen", "normal"))
        choices.append(("4", "🚰 Gå til Pumpehuset", "gå til pumpehuset", "normal"))
        choices.append(("5", "⚡ Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
        return choices
