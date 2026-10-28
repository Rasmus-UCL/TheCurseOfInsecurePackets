"""NIS2 (EU 2022/2555) Incident Reporting & Compliance Evaluation Engine."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class IncidentReport:
    timestamp: float = field(default_factory=time.time)
    submitted_day: int = 1
    submitted_hour: int = 1
    incident_type: str = ""
    affected_zone: str = ""
    severity: str = "HØJ"
    initial_actions: str = ""
    is_early_warning_submitted: bool = False
    early_warning_deadline_hours: int = 24


class IncidentManager:
    """Manages NIS2 Artikel 23 early warnings and generates Artikel 21 compliance audits."""

    def __init__(self) -> None:
        self.reports: list[IncidentReport] = []
        self.early_warning_sent: bool = False
        self.early_warning_on_time: bool = True
        self.wrong_reports: list[str] = []
        self.incident_detected_at: float = 0.0

    def trigger_incident(self) -> None:
        if self.incident_detected_at == 0.0:
            self.incident_detected_at = time.monotonic()

    def record_wrong_report(self, player_name: str, reason: str) -> str:
        """Record a wrongful/inappropriate NIS2 Artikel 23 report and return Kirsten's angry response."""
        name = player_name or "Konsulent"
        self.wrong_reports.append(reason)
        return (
            f"😠 [REVISOR KIRSTEN ER UTILFREDS — FEJLAGTIG NIS2 ARTIKEL 23 INDBERETNING]:\n"
            f"Kirsten afbryder skarpt i telefonen:\n"
            f"\"Hvad tænker du på, {name}?! {reason}\n"
            f"Efter NIS2 Artikel 23 skal CSIRT kun modtage en kvalificeret 24-timers Early Warning for bekræftede, "
            f"væsentlige cyberhændelser — ikke uverificerede alarmer, interne rutineafvigelser eller dublet-spam! "
            f"Denne fejlagtige indberetning er noteret og trækker ned i jeres afsluttende NIS2-revisionsrapport!\""
        )

    def submit_early_warning(
        self,
        day: int,
        hour: int,
        incident_desc: str,
        player_name: str = "Konsulent",
    ) -> tuple[bool, str]:
        """Submit the statutory 24-hour Early Warning to the CSIRT / supervisory authority."""
        name = player_name or "Konsulent"
        self.early_warning_sent = True
        rep = IncidentReport(
            submitted_day=day,
            submitted_hour=hour,
            incident_type="Industriel Netværkssabotage (OT / SCADA)",
            affected_zone="Kritisk Vandforsynings-zone (Purdue Level 1-3.5)",
            severity="KRITISK",
            initial_actions=incident_desc or "Zonering, conduit-isolering og frakobling af mistænkeligt udstyr.",
            is_early_warning_submitted=True,
        )
        self.reports.append(rep)

        # Check 24-hour compliance: Day 1 or Day 2 before hour 8
        is_compliant = (day == 1) or (day == 2 and hour <= 8)
        self.early_warning_on_time = is_compliant
        if is_compliant:
            return True, (
                "✅ [NIS2 ARTIKEL 23.2 OVERHOLDT - REVISOR KIRSTEN ER TILFREDS]:\n"
                f"Modtaget hos Miljø- og Cybersikkerhedstilsynet / CSIRT på Dag {day}, kl. {hour + 7:02d}:00.\n"
                "Rapport-ID: #NIS2-DK-2026-H2O-0994.\n"
                f"Kirsten nikker anerkendende i telefonen: \"Fremragende og rettidig indberetning, {name}! "
                "Du har først isoleret og verificeret den væsentlige OT-hændelse og derefter indsendt jeres 24-timers "
                "Early Warning inden for tidsfristen. Det tæller positivt i den afsluttende NIS2-rapport!\""
            )
        else:
            return False, (
                "⚠️ [NIS2 ARTIKEL 23.2 OVERSKRIDELSE - REVISOR KIRSTEN ER UTILFREDS]:\n"
                f"Hændelsesadvarslen blev først indsendt på Dag {day}, time {hour}.\n"
                f"Kirsten siger skarpt: \"Det er for sent, {name}! Fristen på 24 timer fra detektering er overskredet! "
                "Tilsynet noterer manglende rettidig hændelsesindberetning i den afsluttende rapport!\""
            )

    def evaluate_compliance(
        self,
        player_name: str,
        flags: set[str],
        flaws: list[str],
        forensics_state: str,
    ) -> tuple[bool, int, list[str], str]:
        """Evaluate compliance against NIS2 Artikel 21 requirements and return (passed, score, remarks, report_text)."""
        score = 100
        remarks: list[str] = []

        # 1. Hændelseshåndtering (Artikel 21.2.b & Artikel 23)
        if not self.early_warning_sent:
            score -= 15
            remarks.append("Artikel 23: Manglende 24-timers 'Tidlig Advarsel' til Cybersikkerhedstilsynet.")
        elif not self.early_warning_on_time:
            score -= 10
            remarks.append("Artikel 23: 24-timers 'Tidlig Advarsel' blev indsendt for sent (efter 24-timers fristen).")
        else:
            remarks.append("Artikel 23: Rettidig 24-timers hændelsesindberetning godkendt af Tilsynet.")

        if self.wrong_reports or "art23-wrong-report" in flags:
            score -= 10
            remarks.append(
                f"Artikel 23: FEJL - Fejlagtig eller ukvalificeret indberetning til CSIRT ({len(self.wrong_reports) or 1} påtale(r) fra Kirsten)."
            )

        # 2. Forensic Chain of Custody (Artikel 21.2.b)
        if forensics_state == "secured":
            remarks.append("Artikel 21.2.b: Teknisk bevissikring af beslaglagt hardware i antistatisk Faraday-pose godkendt.")
        elif forensics_state == "trashed":
            score -= 20
            remarks.append("Artikel 21.2.b: KRITISK FEJL - Rogue hardware destrueret i skraldespand (Tab af teknisk bevis).")
        elif forensics_state in {"reused", "infected"}:
            score -= 20
            remarks.append("Artikel 21.2.b: KRITISK FEJL - Kompromitteret hardware genbrugt eller tilsluttet privat PC.")
        else:
            score -= 10
            remarks.append("Artikel 21.2.b: Rogue hardware mangler formel plombering og bevissikring.")

        # 3. Driftskontinuitet og backup (Artikel 21.2.c)
        if "breaker-tripped" in flags:
            score -= 15
            remarks.append("Artikel 21.2.c: Sikkerhedsrelæ K1 er udløst; Pumpe 2 står uden spænding.")
        if "plc-defect-stop" in flags or "backup-taken" not in flags:
            score -= 15
            remarks.append("Artikel 21.2.c: S7-1500 mangler autoriseret offline backup eller står i STOP.")
        else:
            remarks.append("Artikel 21.2.c: Offline gylden backup og redundant driftsberedskab verificeret.")

        # 4. Netværkssikkerhed & Zonering (Artikel 21.2.d / IEC 62443-3-2)
        if "scada-blind" in flags:
            score -= 15
            remarks.append("Artikel 21.2.d: SCADA er blindet af grov Layer 3 portblokering i stedet for Deep Packet Inspection.")
        if "chapter-1-done" in flags and "chapter-2-done" in flags:
            remarks.append("Artikel 21.2.d: Mikrosegmentering (VLAN 10/20) og SCALANCE conduits opfylder IEC 62443 SL-2.")
        else:
            score -= 20
            remarks.append("Artikel 21.2.d: Zonedeling eller feldbus-kryptering er ufuldstændig.")

        # 5. Kryptografi og certifikater (Artikel 21.2.h)
        if "chapter-4-done" in flags:
            remarks.append("Artikel 21.2.h: OPC UA kryptering (Basic256Sha256) og X.509 certifikatvalidering godkendt.")
        else:
            score -= 15
            remarks.append("Artikel 21.2.h: OPC UA kører fortsat ukrypteret (SecurityPolicy: None) eller med Anonymous token.")

        # 6. IDMZ og bagdøre (Purdue 3.5 / Artikel 21.2.i)
        if "router-disconnected" not in flags:
            score -= 20
            remarks.append("Artikel 21.2.i: Uautoriseret cellulær 4G-router fundet aktiv i kontrolrummet.")
        else:
            remarks.append("Artikel 21.2.i: Fysisk og logisk adgangskontrol håndhævet; uautoriseret uplink elimineret.")

        for fl in flaws:
            score -= 10
            remarks.append(f"Driftsfejl: {fl}")

        score = max(0, min(100, score))
        passed = (score >= 80)

        # Generate markdown report text
        report = [
            f"# NIS2 REVISIONSRAPPORT (EU 2022/2555 & IEC 62443)",
            f"**Virksomhed:** Nordic H2O Utility A/S (Drikkevandsforsyning - Væsentlig Enhed)",
            f"**Lead Sikkerhedskonsulent:** {player_name}",
            f"**Auditørdato:** Afsluttende Tilsynsbesøg (Uge 1)",
            f"**Overordnet Resultat:** {'BESTÅET (Fuld driftstilladelse)' if passed else 'DUMPET (Driftstilladelse inddraget)'}",
            f"**Samlet Compliance Score:** {score} / 100 point (Krav: min. 80 point)",
            "",
            "## Gennemgang af NIS2 Artikel 21 Risikostyringsforanstaltninger:",
        ]
        for r in remarks:
            icon = "✅" if not any(w in r for w in {"Mangler", "Manglende", "KRITISK", "FEJL", "fejl", "står", "blindet"}) else "❌"
            report.append(f"- {icon} {r}")

        report_text = "\n".join(report)
        return passed, score, remarks, report_text
