"""Siemens SIMATIC S7-1500 (CPU 1516F-3 PN/DP) - Purdue Level 1/2 with 5-Way Branching."""

from __future__ import annotations

from typing import Any
from devices.base import BaseDevice


class PLCDevice(BaseDevice):
    def __init__(self) -> None:
        super().__init__(
            name="s7-1500",
            title="Siemens SIMATIC S7-1500 (CPU 1516F-3 PN/DP)",
            purdue_level="Purdue Level 1/2: PLC & Safety Controller",
            zone="Zone 3: Hoved-el-tavle (VLAN 30)",
            description=(
                "Fejlsikker modular sikkerheds-PLC. Styrer anlæggets pumper, kemikaliedosering og nødstop. "
                "Den er under aktivt S7comm-angreb på Port 102 og er gået i STOP."
            ),
        )
        self.mode = "STOP"
        self.db1_corrupted = False
        self.f_passivated = False
        self.bootloader_locked = False
        self.put_get_permitted = True
        self.protection_level = 1  # 1 = No protection, 2 = Read only, 3 = Read/Write password

    def get_telemetry(self, engine: Any) -> str:
        flags = getattr(engine, "flags", set())
        if getattr(engine, "plc_defect_stop", False):
            return "KRITISK STOP: Fejlkode 0x4542 (DEFECTIVE STOP - CRC Mismatch i Safety DB1)!"
        if self.f_passivated:
            return "ALARM: F-I/O PASSIVERING (EN ISO 13849-1 / IEC 62061) - Nødstop udløst pga. manglende I/O sync!"
        if self.bootloader_locked:
            return "KRITISK HARDWARE-FEJL: Bootloader låst pga. korrupt firmware-image (Supply Chain overtrædelse)!"
        if "chapter-3-done" in flags:
            return "RUN TILSTAND: CPU 1516F OK | PUT/GET Blokeret | DB1 Verificeret | Safety Determinisme: OK"
        return "STOP TILSTAND: Rød STOP-LED blinker (1 Hz) | S7comm Port 102 angreb detekteret!"

    def get_available_actions(self, engine: Any) -> list[tuple[str, str, str]]:
        flags = getattr(engine, "flags", set())
        actions = []
        if "chapter-3-done" in flags:
            actions.append(("plc_diag", "Aflæs TIA Diagnostics Buffer", "undersøg s7-1500"))
            return actions

        # 5 distinct branching paths
        actions.append(("plc_backup_gold", "1. Tag offline USB-backup (Guldstandard)", "tag offline backup"))
        actions.append(("plc_tia_harden", "2. TIA Portal: Deaktivér PUT/GET & Protection Level 3", "konfigurer tia portal"))
        actions.append(("plc_force_run", "3. Tving CPU i RUN via nøglekontakt (Risiko: Koldstart)", "tving cpu i run"))
        actions.append(("plc_drop_port102", "4. Bloker Port 102 i cellens firewall (Risiko: F-I/O)", "bloker port 102"))
        actions.append(("plc_live_patch", "5. Kør live firmware-opdatering uden hash (Risiko: Supply Chain)", "opdater firmware live"))
        actions.append(("plc_direct_laptop", "6. Kobl felt-laptop uisoleret i CPU PN-port (Risiko: ARP)", "kobl laptop i plc port"))
        return actions
