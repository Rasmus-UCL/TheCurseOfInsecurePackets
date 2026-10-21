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
            if "router-disconnected" not in flags:
                if mode == "exam":
                    choices.append(("1", "Frakobl Teltonika RUT950 4G-routeren og afbryd den eksterne cellulære uplink", "frakobl 4g-router", "success"))
                    choices.append(("2", "Inspicér 4G-routerens IP-konfiguration og aktive VPN-tunneler", "undersøg 4g-router", "normal"))
                else:
                    choices.append(("1", "🔌 Frakobl & konfisker den uautoriserede Teltonika 4G-router fra racket", "frakobl 4g-router", "success"))
                    choices.append(("2", "🔍 Undersøg 4G-routerens SIM-kort og aktive VPN-tunneler", "undersøg 4g-router", "normal"))

            # OPC UA PKI multi-step workflow
            if "cert-trusted" not in flags:
                if mode == "exam":
                    choices.append(("3", "Godkend WinCC SCADA klientens X.509 certifikat i OPC UA serverens truststore", "godkend scada certifikat", "success"))
                else:
                    choices.append(("3", "📜 Certifikat-håndtering: Flyt WinCC SCADA certifikat fra 'Rejected' til 'Trusted'", "godkend scada certifikat", "success"))
            if "opc-crypto-active" not in flags:
                if mode == "exam":
                    choices.append(("4", "Konfigurer OPC UA endpoint til Basic256Sha256 og MessageSecurityMode SignAndEncrypt", "aktiver opc kryptering", "success"))
                else:
                    choices.append(("4", "🔒 Kryptering: Skift SecurityPolicy fra 'None' til Basic256Sha256 / SignAndEncrypt", "aktiver opc kryptering", "success"))
            if "anon-disabled" not in flags:
                if mode == "exam":
                    choices.append(("5", "Deaktivér Anonymous UserTokenType på port 4840 og håndhæv rollebaseret adgangskontrol", "deaktiver anonymous opc", "success"))
                else:
                    choices.append(("5", "🚫 Adgangskontrol: Deaktivér Anonymous User Token & håndhæv RBAC", "deaktiver anonymous opc", "success"))

            if mode == "exam":
                choices.append(("6", "Bloker al TCP port 4840 trafik i IDMZ-firewallen for at stoppe datalækage", "bloker port 4840 totalt", "warning"))
                choices.append(("7", "Åbn Wireshark og inspicér ukrypterede OPC.TCP sessioner på port 4840", "åbn wireshark", "normal"))
                choices.append(("8", "Tal med Hans McDonald i kontrolrummet", "tal med hans", "normal"))
                choices.append(("9", "Gå til Hovedindgangen", "gå til indgangen", "normal"))
            else:
                choices.append(("6", "🛡️ Bloker Port 4840 totalt i IDMZ-firewallen (Grov blokering: Risiko)", "bloker port 4840 totalt", "warning"))
                choices.append(("7", "📊 Wireshark: Inspicér rå ukrypterede OPC.TCP pakker på Port 4840", "åbn wireshark", "normal"))
                choices.append(("8", "☕ Hæld en kop frisk kaffe op hos Hans", "tal med hans", "normal"))
                choices.append(("9", "🚪 Gå til Hovedindgangen", "gå til indgangen", "normal"))
            return choices

        # Later chapters
        choices.append(("1", "🔍 Undersøg WinCC SCADA PC (alle parametre grønne)", "undersøg scada pc", "normal"))
        choices.append(("2", "📊 Wireshark: Bekræft krypteret OPC.TCP session", "åbn wireshark", "normal"))
        choices.append(("3", "🚪 Gå til Hovedindgangen", "gå til indgangen", "normal"))
        choices.append(("4", "🚰 Gå til Pumpehuset", "gå til pumpehuset", "normal"))
        choices.append(("5", "⚡ Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
        return choices
