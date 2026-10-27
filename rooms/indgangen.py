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
        if getattr(engine, "tutorial_active", False):
            step = getattr(engine, "tutorial_step", 1)
            if step == 1:
                return (
                    "🎓 [INTRO-TUTORIAL — TRIN 1/5: INSPEKTION AF RUM & HOTSPOTS]\n"
                    "Senior driftstekniker Hans McDonald rækker dig en gul sikkerhedshjelm og peger på 2D-skærmen foroven:\n"
                    "\"Velkommen til Nordic H2O Utility! Inden vi låser dig ind i selve produktionshallen, tager vi et hurtigt 60-sekunders udstyrstjek "
                    "(timeren er sat på pause under tutorialen).\n\n"
                    "I hvert rum kan du undersøge fysiske komponenter ved at KLIKKE DIREKTE på de stiplede hotspots på 2D-skærmen foroven, "
                    "eller ved at vælge [1] i menuen herunder.\n"
                    "👉 PRØV NU: Klik på 'EMALJESKILT (Zoner)' på skærmen foroven, eller tast '1' (eller skriv 'undersøg skilt').\""
                )
            if step == 2:
                return (
                    "🎓 [INTRO-TUTORIAL — TRIN 2/5: NETVÆRKSSNIFFING MED TSHARK]\n"
                    "Hans klapper anerkendende og peger på din bærbare konsulent-PC:\n"
                    "\"Sådan! Når du undersøger komponenter eller netværkstrafik, opsamler du vigtige tekniske spor.\n"
                    "Dit vigtigste cyber-værktøj i terminalen er 'tshark' (kommandolinje-Wireshark).\n\n"
                    "Jeg har koblet din PC på vores trænings-port her ved indgangen. Lad os fange de seneste pakker fra loggen!\n"
                    "👉 PRØV NU: Tast '1' eller skriv 'tshark' i terminalen for at sniffe netværkstrafikken.\""
                )
            if step == 3:
                return (
                    "🎓 [INTRO-TUTORIAL — TRIN 3/5: ÅBN EFTERFORSKNINGENS SAGSTAVLE]\n"
                    "Hans peger op på bjælken lige over 2D-skærmen, hvor knappen '🕵️ Sagstavle' nu lyser ORANGERØDT:\n"
                    "\"Så du det?! Da du kørte tshark, fandt vi et forensisk spor ('spor_morten_rapport' fra gårsdagens servicebesøg)!\n"
                    "Mange konsulenter glemmer at lede efter selve gerningsmanden ('synderen'), fordi de har travlt med at slukke brande.\n\n"
                    "Derfor har du en interaktiv SAGSTAVLE, der samler alle mistænkte og beviser!\n"
                    "👉 PRØV NU: Klik på den orange knap '🕵️ Sagstavle' over skærmen, eller tast '1' (eller skriv 'sagstavle').\""
                )
            if step == 4:
                return (
                    "🎓 [INTRO-TUTORIAL — TRIN 4/5: ANALYSÉR BEVIS & VÆLG EN FORELØBIG HOVEDMISTÆNKT]\n"
                    "Hans stiller sig ved siden af Sagstavlen:\n"
                    "\"Her på Sagstavlen gælder en vigtig 3-trins regel:\n"
                    "  1. Nye spor starter som '⚠️ NYT SPOR (Uanalyseret)' — du ved endnu ikke, hvem sporet peger på!\n"
                    "  2. Når du KLIKKER på sporet (eller skriver 'analyser spor <id>'), afsløres den tekniske sammenhæng, og mistanke-scoren opdateres.\n"
                    "  3. Til venstre kan du derefter klikke på en mistænkt for at udpege vedkommende som din foreløbige '⭐ Hovedmistænkt'.\n\n"
                    "👉 PRØV NU: Analyser sporet ('analyser spor spor_morten_rapport' / klik på sporet på tavlen) OG vælg en foreløbig mistænkt ('anklag morten_pumper' / klik på en mistænkt)!\""
                )
            return (
                "🎓 [INTRO-TUTORIAL — TRIN 5/5: DE 4 METRIKKER & KLAR TIL INDSATS!]\n"
                "Hans nikker tilfreds:\n"
                "\"Fremragende! Du har nu styr på hotspots, tshark og Sagstavlen. Som det sidste skal du kende de 4 metrikker over skærmen:\n"
                "  • 🔧 Drift:      Vandværkets oppetid og tryk (pas på panik-nedlukninger og blind blokering af porte!).\n"
                "  • 🛡️ Sikkerhed:  IEC 62443 segmentering, firewalls, PLC-hærdning og kryptering.\n"
                "  • 📜 Compliance: NIS2 Artikel 21/23 lovkrav, 24-timers Early Warning og Faraday-bevissikring.\n"
                "  • 🤝 Tillid:     Mit og ledelsens samarbejde med dig.\n\n"
                "Når du træder ind i Pumpehuset om lidt, starter Kapitel 1 og uret! Husk at tjekke Sagstavlen efter hvert kapitel.\n"
                "👉 PRØV NU: Tast '1' ('afslut tutorial') for at starte den rigtige mission!\""
            )

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
        if getattr(engine, "tutorial_active", False):
            step = getattr(engine, "tutorial_step", 1)
            if step == 1:
                return [
                    ("1", "🎓 [Tutorial Trin 1/5]: Undersøg emaljeskiltet med Purdue-zonerne ('undersøg skilt')", "undersøg skilt", "primary"),
                    ("2", "⏭️ Spring intro-tutorialen over og start Kapitel 1 direkte", "spring tutorial over", "normal"),
                ]
            if step == 2:
                return [
                    ("1", "🎓 [Tutorial Trin 2/5]: Kør 'tshark' for at opsnappe træningspakker og finde dit første spor", "tshark", "primary"),
                    ("2", "⏭️ Spring intro-tutorialen over og start Kapitel 1 direkte", "spring tutorial over", "normal"),
                ]
            if step == 3:
                return [
                    ("1", "🎓 [Tutorial Trin 3/5]: Åbn Efterforskningens Sagstavle ('sagstavle')", "sagstavle", "primary"),
                    ("2", "⏭️ Spring intro-tutorialen over og start Kapitel 1 direkte", "spring tutorial over", "normal"),
                ]
            if step == 4:
                c = engine.investigation.clues.get("spor_morten_rapport")
                choices_step4: list[tuple[str, str, str, str]] = []
                if not (c and c.analyzed):
                    choices_step4.append(("1", "🔬 [Tutorial Trin 4A]: Analyser det nye spor på Sagstavlen ('analyser spor spor_morten_rapport')", "analyser spor spor_morten_rapport", "primary"))
                if not engine.investigation.prime_suspect_id:
                    choices_step4.append(("2", "⭐ [Tutorial Trin 4B]: Udpeg en foreløbig hovedmistænkt ('anklag morten_pumper')", "anklag morten_pumper", "primary"))
                if not choices_step4:
                    choices_step4.append(("1", "✅ Gå videre til sidste trin af tutorialen", "analyser spor spor_morten_rapport", "success"))
                choices_step4.append(("3", "⏭️ Spring intro-tutorialen over og start Kapitel 1 direkte", "spring tutorial over", "normal"))
                return choices_step4
            return [
                ("1", "🚀 [Tutorial Trin 5/5]: Afslut tutorial og start Kapitel 1 (Gå i krig med missionen!)", "afslut tutorial", "success"),
                ("2", "👉 Gå direkte ind i Pumpehuset (Starter Kapitel 1 & akut pumpe-alarm)", "gå til pumpehuset", "primary"),
            ]

        ch = getattr(engine, "chapter", 1)
        mode = getattr(engine, "game_mode", "teach")
        choices: list[tuple[str, str, str, str]] = []

        if ch == 5:
            # Streamlined 3-phase finale so the player only sees 3-4 clear actions at a time
            flags = getattr(engine, "flags", set())
            case_presented = "case-presented" in flags
            if not case_presented:
                choices.append(("1", "🕵️ Åbn Sagstavlen (Analyser sidste spor og vælg ⭐ Hovedmistænkt)", "sagstavle", "primary"))
                choices.append(("2", "⚖️ Fremlæg efterforskningen og udpeg gerningsmanden for Tilsynet", "fremlæg sagstavle", "success"))
                choices.append(("3", "🛡️ Gennemse forensisk evidensjournal (Chain of Custody)", "vis evidens", "normal"))
                choices.append(("4", "☕ Tal med driftstekniker Hans McDonald", "tal med hans", "normal"))
            elif getattr(engine, "running", True):
                choices.append(("1", "📋 Gennemfør afsluttende NIS2-revision og modtag Tilsynets dom", "revisor", "success"))
                choices.append(("2", "🕵️ Åbn Sagstavlen (Skift hovedmistænkt hvis nødvendigt)", "sagstavle", "normal"))
                choices.append(("3", "📑 Eksporter officiel NIS2 revisionsrapport (Markdown)", "eksporter rapport", "normal"))
                choices.append(("4", "🏠 Afslut til Hovedmenuen", "hovedmenu", "normal"))
            else:
                choices.append(("1", "📑 Eksporter officiel NIS2 revisionsrapport (Markdown)", "eksporter rapport", "success"))
                choices.append(("2", "🏠 Afslut missionen og vend tilbage til Hovedmenuen", "hovedmenu", "primary"))
            return choices

        choices.append(("1", "🚰 Gå til Pumpehuset i produktionshallen (Start indsats)", "gå til pumpehuset", "primary"))
        choices.append(("2", "📜 Undersøg emaljeskiltet med Purdue-zonemodellen", "undersøg skilt", "normal"))
        choices.append(("3", "🚶 Tag en teknisk rundtur med Hans McDonald", "rundtur", "normal"))
        choices.append(("4", "☕ Tal med Hans McDonald om anlæggets tilstand", "tal med hans", "normal"))
        return choices
