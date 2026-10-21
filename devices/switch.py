"""Industrial Switches: D-Link Unmanaged vs. Siemens SCALANCE XB-200 (MRP)."""

from __future__ import annotations

from typing import Any
from devices.base import BaseDevice


class SwitchDevice(BaseDevice):
    def __init__(self) -> None:
        super().__init__(
            name="switch",
            title="Netværksswitch (Feldbus)",
            purdue_level="Purdue Level 1 (Infrastruktur)",
            zone="Zone 2: Feldbus & I/O",
            description="Switch der forbinder Festo ventil-øen og ET 200SP I/O stationen med procesnettet.",
        )

    def get_telemetry(self, engine: Any) -> str:
        flags = getattr(engine, "flags", set())
        if "chapter-2-done" in flags:
            return "SIEMENS SCALANCE XB-200: MRP Ring Manager Aktiv | Port Security: Låst | 24V Redundant: OK"
        return "D-LINK DES-1008D: Unmanaged kontor-switch. Broadcast-storm aktiv (98% pakketab)!"

    def get_available_actions(self, engine: Any) -> list[tuple[str, str, str]]:
        flags = getattr(engine, "flags", set())
        actions = []
        if "chapter-2-done" in flags:
            actions.append(("switch_status", "Inspicér MRP Ring", "undersøg switch"))
            return actions

        actions.append(("switch_workbench", "Åbn Switch Montage-arbejdsbænk", "switch workbench"))
        actions.append(("switch_unplug_risky", "Pille switch fra uden varsel (Risiko: Kavitation)", "pille switch fra"))
        actions.append(("switch_reboot_io", "Genstart ET 200SP I/O (Risiko)", "genstart et200sp"))
        return actions
