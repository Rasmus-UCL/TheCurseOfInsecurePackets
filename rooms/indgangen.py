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

    def get_description(self, engine: Any) -> str:
        ch = getattr(engine, "chapter", 1)
        if ch == 5:
            return (
                "Du træder ind i Hovedindgangen. Udenfor siler en kold efterårsregn ned over anlæggets rørbroer. "
                "Ved skranken står Tilsynets chefinspektør Kirsten med sit digitale audit-tablet og en tæt mappe med NIS2-bilag. "
                "Ved siden af står driftstekniker Hans McDonald i sin kedeldragt med termokanden i hånden. Han kigger spændt på dig.\n\n"
                "Kirsten tjekker sit ur og retter blikket mod dig:\n"
                "\"Tidsfristen er udløbet, konsulent. Nordic H2O Utility er klassificeret som en 'Væsentlig Enhed' under NIS2. "
                "Vi har modtaget jeres tekniske logbøger, men nu vil Tilsynet se jeres samlede efterforskning: "
                "Hvem stod bag angrebet, hvilke beviser understøtter det, og hvordan er anlæggets 4 metrikker endt? "
                "Fremlæg jeres sagstavle, så Tilsynet kan afsige den endelige dom!\""
            )
        return self.description

    def get_choices(self, engine: Any) -> list[tuple[str, str, str, str]]:
        ch = getattr(engine, "chapter", 1)
        mode = getattr(engine, "game_mode", "teach")
        choices: list[tuple[str, str, str, str]] = []

        if ch == 5:
            if mode == "exam":
                choices.append(("1", "Fremlæg efterforskningens sagstavle og udpeg gerningsmand", "fremlæg sagstavle", "success"))
                choices.append(("2", "Gennemfør afsluttende revision med Tilsynets auditor Kirsten", "revisor", "success"))
                choices.append(("3", "Åbn efterforskningens sagstavle og verificer fundne spor", "sagstavle", "normal"))
                choices.append(("4", "Vis forensisk evidensjournal og Chain of Custody", "vis evidens", "normal"))
                choices.append(("5", "Eksporter officiel NIS2 compliance-revisionsrapport", "eksporter rapport", "success"))
                choices.append(("6", "Tal med driftstekniker Hans McDonald om anlæggets drift", "tal med hans", "normal"))
                choices.append(("7", "Spørg auditor Kirsten om compliance-krav og sanktioner", "spørg kirsten om artikel 21", "normal"))
                choices.append(("8", "Gå til Kontrolrummet (IDMZ)", "gå til kontrolrummet", "normal"))
                choices.append(("9", "Afslut til Hovedmenuen", "hovedmenu", "normal"))
            else:
                choices.append(("1", "🕵️ Trin 1 (Konfrontation): Fremlæg sagstavle & udpeg gerningsmand ('fremlæg sagstavle')", "fremlæg sagstavle", "success"))
                choices.append(("2", "📋 Trin 2 (Audit): Gennemfør officiel NIS2 revision med Revisor Kirsten ('revisor')", "revisor", "success"))
                choices.append(("3", "🔍 Trin 3 (Sagstavle): Gennemse alle 11 spor og mistænkte ('sagstavle')", "sagstavle", "normal"))
                choices.append(("4", "🛡️ Trin 4 (Forensics): Vis forensisk evidensjournal & Chain of Custody ('vis evidens')", "vis evidens", "normal"))
                choices.append(("5", "📑 Trin 5 (Dokumentation): Eksporter officiel NIS2 Revisionsrapport ('eksporter rapport')", "eksporter rapport", "success"))
                choices.append(("6", "☕ Trin 6 (Debrief): Tal med Hans McDonald om forløbet ('tal med hans')", "tal med hans", "normal"))
                choices.append(("7", "⚖️ Trin 7 (Tilsyn): Spørg Kirsten om sanktioner og NIS2 Artikel 21/23", "spørg kirsten om artikel 21", "normal"))
                choices.append(("8", "🖥️ Navigation: Gå til Kontrolrummet (IDMZ)", "gå til kontrolrummet", "normal"))
                choices.append(("9", "🏠 Afslutning: Vend tilbage til Hovedmenuen ('hovedmenu')", "hovedmenu", "normal"))
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
