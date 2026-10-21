"""Revisor Kirsten (Miljø- og Cybersikkerhedstilsynet) - Audit Dialogue & NIS2 Evaluation."""

from __future__ import annotations

from typing import Any


class KirstenDialogue:
    def get_audit_intro(self, player_name: str) -> str:
        return (
            f"Kirsten tager sine læsebriller på og slår op i sit clipboard:\n"
            f"\"Goddag, {player_name}. Jeg er Kirsten fra Miljø- og Cybersikkerhedstilsynet.\n"
            f"Nordic H2O Utility er klassificeret som en 'Væsentlig Enhed' under NIS2-direktivet (EU 2022/2555).\n"
            f"I dag skal jeg kontrollere, om anlægget opfylder de 10 obligatoriske risikostyringskrav i Artikel 21 "
            f"samt de tekniske krav i IEC 62443 standarden.\n"
            f"Lad mig se din dokumentation og gennemgå anlæggets zoner punkt for punkt.\""
        )

    def format_verdict(self, passed: bool, score: int, remarks: list[str]) -> str:
        lines = []
        if passed:
            lines.append(f"\n🏆 [AUDIT BESTÅET! CERTIFICERING TILDELT - SCORE: {score}/100 POINT]:")
            lines.append("Kirsten nikker anerkendende og sætter sit officielle stempel:")
            lines.append(
                f"\"Fremragende arbejde, konsulent! Du har demonstreret dyb teknisk forståelse for "
                f"både OT-netværkssikkerhed, IEC 62443 zoner og conduits, samt NIS2 Artikel 21.\n"
                f"Driftstilladelsen til Nordic H2O Utility er hermed forlænget for de næste tre år!\""
            )
        else:
            lines.append(f"\n❌ [AUDIT DUMPET - DRIFTSTILLADELSE INDDRAGET - SCORE: {score}/100 POINT]:")
            lines.append("Kirsten ryster alvorligt på hovedet og trækker den røde pen frem:")
            lines.append(
                f"\"Det her er ikke acceptabelt. Der er konstateret kritiske afvigelser fra NIS2 Artikel 21.\n"
                f"Et vandværk i kritisk infrastruktur kan ikke drives med disse sikkerhedsmæssige huller.\n"
                f"Følgende mangler skal udbedres omgående f.s.v. anlægget ikke skal påbydes standsning:\""
            )

        lines.append("\nKIRSTENS AUDIT-BEMÆRKNINGER:")
        for r in remarks:
            lines.append(f"  • {r}")

        return "\n".join(lines)
