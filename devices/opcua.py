"""IEC 62541 OPC UA Server & PKI Certificate Management - Purdue Level 3/IDMZ."""

from __future__ import annotations

from typing import Any
from devices.base import BaseDevice


class OpcUaDevice(BaseDevice):
    def __init__(self) -> None:
        super().__init__(
            name="opc ua server",
            title="IEC 62541 OPC UA Server (WinCC SCADA Gateway)",
            purdue_level="Purdue Level 3.5: Industrial DMZ (IDMZ)",
            zone="Zone 4: Kontrol & Driftsovervågning",
            description=(
                "Industriel interoperabilitets-server. Leverer telemetri og doseringsopskrifter til SCADA. "
                "Lytter på port 4840. Kører aktuelt med SecurityPolicy: None og tillader Anonymous adgang."
            ),
        )
        self.endpoint_url = "opc.tcp://10.20.2.10:4840"
        self.security_policy = "None"  # "None", "Basic256Sha256"
        self.message_mode = "None"     # "None", "SignAndEncrypt"
        self.allow_anonymous = True
        self.trusted_certificates: list[str] = []
        self.rejected_certificates: list[str] = ["WinCC_SCADA_Client_Cert_2026.der"]

    def get_telemetry(self, engine: Any) -> str:
        flags = getattr(engine, "flags", set())
        if getattr(engine, "scada_log_interrupted", False):
            return "ALARM: Port 4840 blokeret! Lovpligtig miljølogning til Miljøstyrelsen er afbrudt (NIS2 overtrædelse)!"
        if "opc-hardened" in flags:
            return "SIKRET DRIFT: Basic256Sha256 / SignAndEncrypt | WinCC Certifikat: Betroet | Anonymous: Deaktiveret"
        return "SÅRBAR SIKKERHEDSTILSTAND: SecurityPolicy: None | Anonymous: Tilladt | WinCC Klientcertifikat: Rejected!"

    def get_available_actions(self, engine: Any) -> list[tuple[str, str, str]]:
        flags = getattr(engine, "flags", set())
        actions = []
        if "chapter-4-done" in flags:
            actions.append(("opc_diag", "Aflæs OPC UA Sikkerhedslog", "undersøg opc ua server"))
            return actions

        actions.append(("opc_inspect_ep", "1. Inspicér Endpoint & Security Policies", "undersøg opc ua server"))
        actions.append(("opc_trust_cert", "2. Flyt WinCC SCADA Certifikat fra Rejected til Trusted", "godkend scada certifikat"))
        actions.append(("opc_set_policy", "3. Aktivér Basic256Sha256 & SignAndEncrypt", "aktiver opc kryptering"))
        actions.append(("opc_disable_anon", "4. Deaktivér Anonymous User Token (Håndhæv RBAC)", "deaktiver anonymous opc"))
        actions.append(("opc_block_port", "5. Bloker Port 4840 totalt i firewall (Grov blokering)", "bloker port 4840 totalt"))
        return actions
