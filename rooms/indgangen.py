"""Hovedindgangen - Purdue Level 4: Enterprise & Perimeter."""

from __future__ import annotations

from typing import Any
from rooms.base import BaseRoom


class IndgangenRoom(BaseRoom):
    def __init__(self) -> None:
        super().__init__(
            key="indgangen",
            title="Hovedindgangen",
            purdue_level="Purdue Level 4: Enterprise & Adgangszone",
            zone="Zone 0: Perimeter & Administration",
            description=(
                "Du står foran hovedindgangen til Nordic H2O Utility. Kontrolrummet ligger mod nord, "
                "og en håndskrevet pil peger mod pumpehuset i produktionshallen."
            ),
            hotspots=["hoveddør", "skilt", "kaffebar"],
        )

    def get_choices(self, engine: Any) -> list[tuple[str, str, str, str]]:
        ch = getattr(engine, "chapter", 1)
        mode = getattr(engine, "game_mode", "teach")
        choices: list[tuple[str, str, str, str]] = []

        if ch == 5:
            if mode == "exam":
                choices.append(("1", "Gennemfør afsluttende audit med Tilsynets revisor Kirsten", "revisor", "success"))
                choices.append(("2", "Tal med driftstekniker Hans McDonald om driftsjournalen", "tal med hans", "normal"))
                choices.append(("3", "Vis forensisk evidensjournal og Chain of Custody", "vis evidens", "normal"))
                choices.append(("4", "Eksporter officiel NIS2 compliance-revisionsrapport", "eksporter rapport", "success"))
                choices.append(("5", "Gå til Kontrolrummet (IDMZ)", "gå til kontrolrummet", "normal"))
            else:
                choices.append(("1", "📋 Gennemfør afsluttende audit med Revisor Kirsten", "revisor", "success"))
                choices.append(("2", "☕ Tal med Hans McDonald ved kaffebaren", "tal med hans", "normal"))
                choices.append(("3", "🔍 Vis forensisk evidensjournal & Chain of Custody", "vis evidens", "normal"))
                choices.append(("4", "📑 Eksporter officiel NIS2 Revisionsrapport", "eksporter rapport", "success"))
                choices.append(("5", "🖥️ Gå til Kontrolrummet (IDMZ)", "gå til kontrolrummet", "normal"))
            return choices

        if mode == "exam":
            choices.append(("1", "Gå til Pumpehuset i produktionshallen", "gå til pumpehuset", "primary"))
            choices.append(("2", "Gå til Kontrolrummet (IDMZ)", "gå til kontrolrummet", "normal"))
            choices.append(("3", "Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
            choices.append(("4", "Undersøg skiltet med anlæggets Purdue-zonemodel", "undersøg skilt", "normal"))
            choices.append(("5", "Gennemfør teknisk orientering med driftstekniker Hans McDonald", "rundtur", "normal"))
            choices.append(("6", "Tal med Hans McDonald om anlæggets driftshistorik", "tal med hans", "normal"))
        else:
            choices.append(("1", "👉 Gå til Pumpehuset i produktionshallen (Start indsats)", "gå til pumpehuset", "primary"))
            choices.append(("2", "🖥️ Gå til Kontrolrummet (IDMZ)", "gå til kontrolrummet", "normal"))
            choices.append(("3", "⚡ Gå til Hoved-el-tavlen", "gå til el-tavlen", "normal"))
            choices.append(("4", "📜 Undersøg emaljeskiltet med zonemodellen", "undersøg skilt", "normal"))
            choices.append(("5", "🚶 Tag en teknisk rundtur med Hans McDonald", "rundtur", "normal"))
            choices.append(("6", "☕ Tal med Hans McDonald om anlæggets tilstand", "tal med hans", "normal"))
        return choices
