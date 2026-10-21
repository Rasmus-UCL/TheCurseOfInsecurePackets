"""Base device abstractions for industrial OT equipment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeviceAction:
    action_id: str
    label: str
    command: str
    risk_level: str = "normal"  # "normal", "warning", "danger", "success"
    description: str = ""


class BaseDevice:
    """Base class for all industrial OT assets in the Purdue hierarchy."""

    def __init__(
        self,
        name: str,
        title: str,
        purdue_level: str,
        zone: str,
        description: str,
    ) -> None:
        self.name = name
        self.title = title
        self.purdue_level = purdue_level
        self.zone = zone
        self.description = description
        self.state: dict[str, Any] = {}
        self.revealed: bool = True  # Hidden devices (like rogue Pi) are revealed upon investigation

    def get_info(self, engine: Any) -> dict[str, Any]:
        """Return structured inspection data for UI rendering."""
        return {
            "name": self.name,
            "title": self.title,
            "purdue": self.purdue_level,
            "zone": self.zone,
            "desc": self.description,
            "telemetry": self.get_telemetry(engine),
            "actions": self.get_available_actions(engine),
            "revealed": self.revealed,
        }

    def get_telemetry(self, engine: Any) -> str:
        return "Status: Normal drift"

    def get_available_actions(self, engine: Any) -> list[tuple[str, str, str]]:
        """Return list of (action_id, button_label, command_to_execute)."""
        return []
