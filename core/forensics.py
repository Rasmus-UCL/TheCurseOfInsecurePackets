"""Digital Forensics & Chain of Custody Management (NIS2 Artikel 21.2.b & NIST SP 800-61)."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class EvidenceItem:
    item_id: str
    name: str
    description: str
    location: str
    purdue_level: str
    mac_address: str = ""
    ip_address: str = ""
    sha256: str = ""
    timestamp: float = field(default_factory=time.time)
    secured_properly: bool = False
    handling_notes: str = ""
    seal_number: str = ""

    def calculate_hash(self, raw_data: str) -> str:
        h = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()
        self.sha256 = h
        return h


class ForensicsManager:
    """Manages legal chain of custody, evidence preservation, and forensic traps."""

    def __init__(self) -> None:
        self.evidence_log: list[EvidenceItem] = []
        self.forensic_violations: list[str] = []
        self.pi_handling_state: str = "unhandled"  # "secured", "trashed", "reused", "infected"

    def secure_rogue_pi(self, method: str) -> tuple[bool, str]:
        """Handle the seized Rogue Raspberry Pi from Ventil-øen."""
        norm = method.lower().strip()

        if "skrald" in norm or "smid ud" in norm or "trash" in norm:
            self.pi_handling_state = "trashed"
            violation = "Fysisk bevisdestruktion: Rogue Pi kasseret i skraldespand. Tab af retsmedicinsk C2-evidens (NIS2 Art. 21.2.b)."
            self.forensic_violations.append(violation)
            return False, (
                "⚠️ [FORENSISK FEJL - TAB AF EVIDENS]: Du smed enheden i skraldespanden!\n"
                "Uden den fysiske enhed kan Cybersikkerhedstilsynet og NC3 ikke rekonstruere angrebsvektoren, "
                "C2-serverens IP'er eller etablere gerningsmandens profil. Dette er en direkte overtrædelse af NIS2 Artikel 21.2.b!"
            )

        if "genbrug" in norm or "hjem" in norm or "iot" in norm or "skuffe" in norm:
            self.pi_handling_state = "reused"
            violation = "Uautoriseret genbrug af kompromitteret hardware: Rogue Pi gemt til privat IoT (Supply Chain risiko)."
            self.forensic_violations.append(violation)
            return False, (
                "⚠️ [SIKKERHEDSRISIKO - PERSISTENT TRUSSEL]: Du lægger enheden i skuffen til privat genbrug!\n"
                "Enheden indeholder ondsindet firmware, et persistent reverse-shell og en skjult Bluetooth-beacon. "
                "Ved genstart på dit hjemmenetværk eller skolens netværk aktiveres bagdøren på ny!"
            )

        if "sd-kort i laptop" in norm or "snag" in norm or "undersøg sd" in norm or "egen laptop" in norm:
            self.pi_handling_state = "infected"
            violation = "Brud på bevisintegritet & infektionsrisiko: SD-kort tilsluttet ingeniørlaptop uden write-blocker."
            self.forensic_violations.append(violation)
            return False, (
                "⚠️ [FORENSISK FEJL & MALWARE INFEKTION]: Du satte MicroSD-kortet direkte i din egen bærbar!\n"
                "1. Kortet manglede hardware-skrivebeskyttelse (Write-Blocker), så styresystemet overskrev adgangstidsstemplerne (MACB), hvilket gør beviset juridisk ugyldigt.\n"
                "2. En ondsindet USB/SD autorun-loader inficerede din felt-laptop med tastatur-logger!"
            )

        # Correct procedure: Forensic bagging & evidence tagging
        self.pi_handling_state = "secured"
        item = EvidenceItem(
            item_id="EVIDENS-001",
            name="Rogue Raspberry Pi 4 Model B (Rev 1.4)",
            description="Uautoriseret enhed tapet til kabelbakke i Ventil-øen. Udførte L2 DCP-spoofing.",
            location="Ventil-øen (Kabelbakke K-04)",
            purdue_level="Purdue Level 1 (Feldbus)",
            mac_address="b8:27:eb:d4:11:22",
            ip_address="10.20.2.199",
            secured_properly=True,
            handling_notes="Sikret i afskærmet Faraday-antistatisk pose. Forseglet med plombering #NC3-8821.",
            seal_number="NC3-8821",
        )
        item.calculate_hash("RASPBERRY_PI_4_IMAGE_B8:27:EB:D4:11:22_DCP_SPOOF_PAYLOAD")
        self.evidence_log.append(item)
        return True, (
            "✅ [FORENSISK EVIDENS SIKRET - NIST SP 800-61 / NIS2 ART. 21.2.b]:\n"
            "Du ifører dig ESD-handsker, afbryder spændingen, og pakker den rogue Raspberry Pi "
            "ned i en antistatisk Faraday-pose. Beviset plomberes med nummer NC3-8821, og SHA-256 hash "
            f"({item.sha256[:16]}...) registreres i hændelsesloggen til Tilsynet!"
        )

    def log_usb_backup(self, plc_name: str, checksum: str) -> None:
        """Record offline golden safety backup in chain of custody."""
        item = EvidenceItem(
            item_id="BACKUP-001",
            name=f"Offline Sikkerhedskopi ({plc_name})",
            description="Uforfalsket fabrikskopi af hardwarekonfiguration, DB1 kalibrering og safety-program.",
            location="Hoved-el-tavlen (Sikkerhedsskab TS-01)",
            purdue_level="Purdue Level 1/2",
            sha256=checksum,
            secured_properly=True,
            handling_notes="Krypteret SanDisk Industrial USB-stik. Opbevares i brandsikkert nøgleskab.",
            seal_number="ISO-27001-BKP",
        )
        self.evidence_log.append(item)

    def get_summary(self) -> str:
        """Render format-ready evidence summary for Revisor Kirsten and player."""
        if not self.evidence_log and not self.forensic_violations:
            return "Ingen registrerede forensiske evidensposter endnu."

        lines = ["=== DIGITAL CHAIN OF CUSTODY (HÆNDELSESLOG) ==="]
        for item in self.evidence_log:
            lines.append(f"[{item.item_id}] {item.name}")
            lines.append(f"  Placering:    {item.location} ({item.purdue_level})")
            if item.mac_address:
                lines.append(f"  Hardware MAC: {item.mac_address} | IP: {item.ip_address}")
            lines.append(f"  SHA-256:      {item.sha256}")
            lines.append(f"  Plombe/Status: {item.seal_number} ({item.handling_notes})")
            lines.append("")

        if self.forensic_violations:
            lines.append("⚠️ REGISTREREDE PROCEDUREFEJL VED HÆNDELSESHÅNDTERING:")
            for v in self.forensic_violations:
                lines.append(f"  - {v}")
            lines.append("")

        return "\n".join(lines)
