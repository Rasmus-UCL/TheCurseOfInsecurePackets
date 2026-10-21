"""Siemens SINAMICS G120 Variable Frequency Drive (VFD) - Purdue Level 1."""

from __future__ import annotations

from typing import Any
from devices.base import BaseDevice


class VFDDevice(BaseDevice):
    def __init__(self) -> None:
        super().__init__(
            name="frekvensomformer",
            title="SINAMICS G120 Frekvensomformer",
            purdue_level="Purdue Level 1 (Feltudstyr)",
            zone="Zone 1: Pumpe-celle (VLAN 10)",
            description=(
                "Industriel frekvensomformer koblet til Pumpe 2 via Modbus TCP (Port 502). "
                "Den modtager hastigheds-setpunkter i Register 0x0000. Ubeskyttet mod netværksmanipulation."
            ),
        )
        self.rpm = 1337
        self.pressure_bar = 146.5
        self.dpi_firewall_active = False

    def get_telemetry(self, engine: Any) -> str:
        flags = getattr(engine, "flags", set())
        if getattr(engine, "breaker_tripped", False):
            return "STRØMLØS: Sikkerhedsrelæ K1 i Hoved-el-tavlen er udløst (Vandslag)!"
        if "chapter-1-done" in flags:
            return "NORMAL DRIFT: 42.0 Bar | 450 RPM | SCALANCE S615 DPI Aktiv (VLAN 10 isoleret)"
        return f"ALARM OVERTRYK: {self.pressure_bar:.1f} Bar (Grænse: 150 Bar) | RPM: {self.rpm} | Sabotage aktiv!"

    def get_available_actions(self, engine: Any) -> list[tuple[str, str, str]]:
        flags = getattr(engine, "flags", set())
        actions = []
        if "chapter-1-done" in flags:
            actions.append(("vfd_status", "Aflæs telemetri", "undersøg frekvensomformer"))
            return actions

        actions.append(("vfd_workbench", "Monter SCALANCE S615 & Kabling", "firewall workbench"))
        actions.append(("vfd_tune_risky", "Drej potentiometer manuelt (Risiko)", "juster setpunkt"))
        actions.append(("vfd_trip_breaker", "Træk hovedafbryder under last (Risiko)", "hård nødnedlukning af vfd"))
        actions.append(("vfd_block_port", "Bloker Port 502 totalt (Blind blokering)", "bloker port 502 totalt"))
        return actions
