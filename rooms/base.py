"""Base class for all physical zones/rooms in the facility."""

from __future__ import annotations

from typing import Any


class BaseRoom:
    def __init__(
        self,
        key: str,
        title: str,
        purdue_level: str,
        zone: str,
        description: str,
        hotspots: list[str],
    ) -> None:
        self.key = key
        self.title = title
        self.purdue_level = purdue_level
        self.zone = zone
        self.description = description
        self.hotspots = hotspots

    def get_description(self, engine: Any) -> str:
        return self.description

    def get_visible_hotspots(self, engine: Any) -> list[str]:
        return self.hotspots.copy()

    def get_choices(self, engine: Any) -> list[tuple[str, str, str, str]]:
        """Return list of (key, label, command, category) choices for this room."""
        return []
