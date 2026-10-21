"""Core game engine coordinating rooms, devices, forensics, NIS2 incidents & gameplay logic."""

from __future__ import annotations

import json
import os
import random
import re
import time
from collections.abc import Callable
from typing import Any

from core.forensics import ForensicsManager
from core.incident import IncidentManager
from core.investigation import InvestigationManager
from core.purdue import PURDUE_LEVELS
from core.terminal_engine import AutocompleteHelper, WiresharkSniffer
from devices import OpcUaDevice, PLCDevice, RoguePiDevice, SwitchDevice, VFDDevice
from dialogues import HansDialogue, KirstenDialogue
from models import OBJECTIVES, MetricValues, Player
from rooms import ALL_ROOMS, BaseRoom


class GameEngine:
    """Modular, Object-Oriented Game Engine for The Curse of Insecure Packets."""

    def __init__(
        self,
        output: Callable[[str], None] | None = None,
        day_seconds: int = 10 * 60,
        pump_deadline_seconds: int = 3 * 60,
        cavitation_deadline_seconds: int = 90,
    ) -> None:
        self.output = output or print
        self.player = Player()
        self.chapter = 0
        self.room = "indgangen"
        self.flags: set[str] = set()
        self.running = True
        self.max_help_calls = 3
        self.help_calls = 0

        # Simulation Clocks
        self.workdays = 5
        self.work_hours_per_day = 8
        self.day_seconds = day_seconds
        self.timer_seconds = self.workdays * self.day_seconds
        self.pump_deadline_seconds = pump_deadline_seconds
        self.cavitation_deadline_seconds = cavitation_deadline_seconds
        self.timer_started_at = 0.0
        self.pump_deadline_started_at = 0.0
        self.pump_deadline_active = False
        self.cavitation_deadline_started_at = 0.0
        self.cavitation_deadline_active = False

        # Active Workbench & Montage State
        self.active_workbench: str | None = None
        self.vfd_mounted: bool = False
        self.vfd_cabled: bool = False
        self.wrong_cabling: bool = False

        # Pedagogical Mode & Randomized Choices
        self.game_mode: str = "teach"  # "teach" (hints/traps visible) or "exam" (neutral realistic options)
        self.shuffle_choices: bool = True
        self._cached_choices: list[tuple[str, str, str, str]] | None = None
        self._cached_state_key: tuple[Any, ...] | None = None

        # Cascading Systemic Consequence Flags
        self.breaker_tripped: bool = False
        self.scada_blind: bool = False
        self.plc_defect_stop: bool = False
        self.scada_log_interrupted: bool = False

        # Modular Subsystems
        self.sniffer = WiresharkSniffer()
        self.forensics = ForensicsManager()
        self.incident = IncidentManager()
        self.hans = HansDialogue()
        self.kirsten = KirstenDialogue()

        # Narrative 4-Metric System & Case Board (Etape 1 Redesign)
        self.metrics = MetricValues()
        self.investigation = InvestigationManager()

        # Instantiated Devices
        self.vfd = VFDDevice()
        self.switch = SwitchDevice()
        self.plc = PLCDevice()
        self.opcua = OpcUaDevice()
        self.rogue_pi = RoguePiDevice()

    def emit(self, message: str) -> None:
        try:
            self.output(message)
        except UnicodeEncodeError:
            safe = message.encode("ascii", errors="replace").decode("ascii")
            self.output(safe)

    def record_clue(self, clue_id: str) -> None:
        """Discover a forensic clue, update the investigation board and adjust trust."""
        sim_time = f"Dag {self.simulated_day}, time {self.simulated_hour}"
        newly_found, clue = self.investigation.discover_clue(clue_id, sim_time)
        if newly_found and clue:
            self.emit(f"\n🔎 [NYT SPOR TIL SAGSTAVLEN]: {clue.title}")
            self.emit(f"   Kategori: {clue.category} | Skriv 'sagstavle' eller 'analyser spor {clue.id}'")
            self.metrics.adjust_tillid(2, f"Nyt spor opdaget: {clue.id}")

    def show_metrics_status(self) -> None:
        """Display the 4 core plant and security metrics."""
        self.emit("\n📊 [ANLÆGGETS 4 HOVEDMETRIKKER - NORDIC H2O]:")
        self.emit(f"  🔧 Drift:      [{self.investigation._render_bar(self.metrics.drift)}] {self.metrics.drift:3d}% (Uptime, vandforsyning, tryk)")
        self.emit(f"  🛡️ Sikkerhed:  [{self.investigation._render_bar(self.metrics.sikkerhed)}] {self.metrics.sikkerhed:3d}% (Zoner, conduits, firewalls)")
        self.emit(f"  📜 Compliance: [{self.investigation._render_bar(self.metrics.compliance)}] {self.metrics.compliance:3d}% (NIS2 Artikel 21/23, dokumentation)")
        self.emit(f"  🤝 Tillid:     [{self.investigation._render_bar(self.metrics.tillid)}] {self.metrics.tillid:3d}% (Hans' stolthed & ledelsens tillid)")
        self.emit("Skriv 'sagstavle' for at se samtlige spor og mistænkte.")

    # -------------------------------------------------------------------------
    # LIFECYCLE & TIMERS
    # -------------------------------------------------------------------------
    def start(self, name: str, education: str) -> None:
        self.player.name = name or "Lead OT-Konsulent"
        self.player.education = education or "Automation & IT-Teknologi"
        self.chapter = 1

        self.emit(
            f"Jens Majer, direktør: \"Velkommen til Nordic H2O Utility, {self.player.name}. "
            f"Jeg har med glæde noteret mig din baggrund inden for {self.player.education}.\""
        )
        self.emit(
            "Jens: \"Situationen er alvorlig: Om fem arbejdsdage kommer Miljø- og Cybersikkerhedstilsynet "
            "for at kontrollere os efter NIS2-direktivet (EU 2022/2555) og IEC 62443-standarden. "
            "Hvis vi dumper, trækkes vores driftstilladelse tilbage!\""
        )
        self.emit(
            "Jens: \"Værre endnu: En ukendt trusselsaktør har allerede fået foden indenfor og saboterer driften. "
            "Vi har brug for en skarp teknolog, der forstår både PLC'er, netværkssegmentering, industrielle protokoller og dokumentation.\""
        )
        self.emit(
            f"HR-chefen nikker: \"Du er hermed hyret som Lead OT-Sikkerhedskonsulent, {self.player.name}. "
            "Undersøg anlægget, stop angrebene metodisk, og opbyg dokumentationen til revisoren.\""
        )
        self.emit(
            "Ved hovedindgangen tager Hans McDonald, senior driftstekniker, imod dig med sin kaffekop: "
            "\"Velkommen om bord! Du står ved Hovedindgangen. Før du rører ved noget, anbefaler jeg, at du kigger dig omkring "
            "eller tager vores 'Rundtur' for at lære zonerne at kende. Gå mod Pumpehuset i produktionshallen, når du er klar til at gå i gang med anlægget.\""
        )

        self.describe_room()
        self.timer_started_at = time.monotonic()
        self.incident.trigger_incident()

    @property
    def elapsed_seconds(self) -> float:
        if self.timer_started_at == 0.0:
            return 0.0
        return max(0.0, time.monotonic() - self.timer_started_at)

    @property
    def time_remaining(self) -> int:
        return max(0, int(self.timer_seconds - self.elapsed_seconds))

    @property
    def time_display(self) -> str:
        rem = self.time_remaining
        m, s = divmod(rem, 60)
        return f"{m:02d}:{s:02d}"

    @property
    def simulated_day(self) -> int:
        day_idx = int(self.elapsed_seconds // self.day_seconds) + 1
        return min(self.workdays, day_idx)

    @property
    def simulated_hour(self) -> int:
        second_in_day = self.elapsed_seconds % self.day_seconds
        hour_fraction = second_in_day / self.day_seconds
        hour_idx = int(hour_fraction * self.work_hours_per_day) + 1
        return min(self.work_hours_per_day, hour_idx)

    @property
    def pump_time_remaining(self) -> int:
        if not self.pump_deadline_active or self.pump_deadline_started_at == 0.0:
            return self.pump_deadline_seconds
        elapsed = time.monotonic() - self.pump_deadline_started_at
        return max(0, int(self.pump_deadline_seconds - elapsed))

    @property
    def pump_time_display(self) -> str:
        rem = self.pump_time_remaining
        m, s = divmod(rem, 60)
        return f"{m:02d}:{s:02d}"

    @property
    def cavitation_time_remaining(self) -> int:
        if not self.cavitation_deadline_active or self.cavitation_deadline_started_at == 0.0:
            return self.cavitation_deadline_seconds
        elapsed = time.monotonic() - self.cavitation_deadline_started_at
        return max(0, int(self.cavitation_deadline_seconds - elapsed))

    @property
    def cavitation_time_display(self) -> str:
        rem = self.cavitation_time_remaining
        m, s = divmod(rem, 60)
        return f"{m:02d}:{s:02d}"

    def check_timers(self) -> bool:
        if not self.running:
            return False

        if self.timer_started_at and self.time_remaining <= 0:
            self.expire_audit_timer()
            return False

        if self.cavitation_deadline_active and self.cavitation_time_remaining <= 0:
            self.expire_cavitation_timer()
            return False

        if self.pump_deadline_active and self.pump_time_remaining <= 0:
            self.expire_pump_timer()
            return False

        return True

    def expire_audit_timer(self) -> None:
        self.emit("\n⏰ [TIDEN ER UDLØBET! Tilsynets 5-dages frist er overskredet]")
        self.emit("Miljø- og Cybersikkerhedstilsynet ankommer uvarslet, men du nåede ikke at sikre anlægget i tide.")
        self.emit("Driftstilladelsen trækkes tilbage. Missionen er tabt.")
        self.emit("\n💡 Tast 'hovedmenu' eller klik '🏠 Menu' for at vende tilbage til Hovedmenuen.")
        self.running = False

    def expire_pump_timer(self) -> None:
        self.emit("\n💥 [KATASTROFE] PUMPE 2 HAR OVERSKREDET SPRÆNGNINGSGRÆNSEN (150 BAR)!")
        self.emit("Rørene sprang, pumpehuset er oversvømmet, og nødstop er udløst på hele fabrikken.")
        self.emit("Du nåede ikke at afværge hændelsen i tide. Missionen er tabt.")
        self.emit("\n💡 Tast 'hovedmenu' eller klik '🏠 Menu' for at vende tilbage til Hovedmenuen.")
        self.running = False

    def expire_cavitation_timer(self) -> None:
        self.emit("\n💥 [KATASTROFE] PUMPE 2'S PUMPEHJUL ER BLEVET SMADRET AF KAVITATION!")
        self.emit("Da modtrykket forsvandt under det ukontrollerede switch-udfald, opstod der voldsomme dampboble-implosioner.")
        self.emit("Vibrationssensoren udløste total nødnedlukning af vandværket. Tilsynet inddrager driftstilladelsen. Missionen er tabt.")
        self.emit("\n💡 Tast 'hovedmenu' eller klik '🏠 Menu' for at vende tilbage til Hovedmenuen.")
        self.running = False

    # -------------------------------------------------------------------------
    # SAVE & LOAD SYSTEM (JSON PERSISTENCE)
    # -------------------------------------------------------------------------
    def save_state(self, filepath: str | None = None) -> tuple[bool, str]:
        """Save the entire game engine state to a JSON file."""
        if not filepath:
            os.makedirs("saves", exist_ok=True)
            p_name = re.sub(r"[^\w\-]", "_", self.player.name.strip()) or "konsulent"
            filepath = os.path.join("saves", f"save_{p_name}.json")
        else:
            d = os.path.dirname(filepath)
            if d:
                os.makedirs(d, exist_ok=True)

        pump_remaining = max(0.0, self.pump_deadline_seconds - (time.monotonic() - self.pump_deadline_started_at)) if self.pump_deadline_active else 0.0
        cav_remaining = max(0.0, self.cavitation_deadline_seconds - (time.monotonic() - self.cavitation_deadline_started_at)) if self.cavitation_deadline_active else 0.0

        save_dict: dict[str, Any] = {
            "version": "2.0",
            "save_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "player": {
                "name": self.player.name,
                "education": getattr(self.player, "education", ""),
                "inventory": list(self.player.inventory),
            },
            "game_mode": self.game_mode,
            "chapter": self.chapter,
            "room": self.room,
            "flags": list(self.flags),
            "running": self.running,
            "help_calls": self.help_calls,
            "elapsed_seconds": self.elapsed_seconds,
            "deadlines": {
                "pump_deadline_active": self.pump_deadline_active,
                "pump_remaining": pump_remaining,
                "cavitation_deadline_active": self.cavitation_deadline_active,
                "cav_remaining": cav_remaining,
            },
            "workbench": {
                "active_workbench": self.active_workbench,
                "vfd_mounted": self.vfd_mounted,
                "vfd_cabled": self.vfd_cabled,
                "wrong_cabling": self.wrong_cabling,
            },
            "consequences": {
                "breaker_tripped": self.breaker_tripped,
                "scada_blind": self.scada_blind,
                "plc_defect_stop": self.plc_defect_stop,
                "scada_log_interrupted": self.scada_log_interrupted,
            },
            "metrics": {
                "drift": self.metrics.drift,
                "sikkerhed": self.metrics.sikkerhed,
                "compliance": self.metrics.compliance,
                "tillid": self.metrics.tillid,
                "history": self.metrics.history,
            },
            "investigation": {
                "prime_suspect_id": self.investigation.prime_suspect_id,
                "clues": {
                    c_id: {"discovered": c.discovered, "discovered_time": c.discovered_time}
                    for c_id, c in self.investigation.clues.items()
                },
                "suspects": {
                    s_id: {"suspicion_score": s.suspicion_score, "status": s.status, "notes": s.notes}
                    for s_id, s in self.investigation.suspects.items()
                },
            },
            "forensics": {
                "pi_handling_state": self.forensics.pi_handling_state,
                "forensic_violations": self.forensics.forensic_violations,
                "evidence_log": [
                    {
                        "item_id": ev.item_id,
                        "name": ev.name,
                        "description": ev.description,
                        "location": ev.location,
                        "purdue_level": ev.purdue_level,
                        "mac_address": ev.mac_address,
                        "ip_address": ev.ip_address,
                        "sha256": ev.sha256,
                        "timestamp": ev.timestamp,
                        "secured_properly": ev.secured_properly,
                        "handling_notes": ev.handling_notes,
                        "seal_number": ev.seal_number,
                    }
                    for ev in self.forensics.evidence_log
                ],
            },
            "incident": {
                "early_warning_sent": self.incident.early_warning_sent,
                "reports": [
                    {
                        "timestamp": r.timestamp,
                        "submitted_day": r.submitted_day,
                        "submitted_hour": r.submitted_hour,
                        "incident_type": r.incident_type,
                        "affected_zone": r.affected_zone,
                        "severity": r.severity,
                        "initial_actions": r.initial_actions,
                        "is_early_warning_submitted": r.is_early_warning_submitted,
                        "early_warning_deadline_hours": r.early_warning_deadline_hours,
                    }
                    for r in self.incident.reports
                ],
            },
            "devices": {
                "rogue_pi_disconnected": self.rogue_pi.disconnected,
                "rogue_pi_revealed": getattr(self.rogue_pi, "revealed", False),
                "plc_f_passivated": getattr(self.plc, "f_passivated", False),
                "plc_bootloader_locked": getattr(self.plc, "bootloader_locked", False),
            },
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_dict, f, indent=2, ensure_ascii=False)
            quicksave_path = os.path.join("saves", "quicksave.json")
            if os.path.abspath(filepath) != os.path.abspath(quicksave_path):
                with open(quicksave_path, "w", encoding="utf-8") as f:
                    json.dump(save_dict, f, indent=2, ensure_ascii=False)
            return True, f"💾 [SPIL GEMT]: Spiltilstanden er gemt i '{filepath}'."
        except Exception as e:
            return False, f"Fejl under lagring af spil: {e}"

    def load_state(self, filepath: str | None = None) -> tuple[bool, str]:
        """Load and restore the game engine state from a JSON file."""
        if not filepath:
            filepath = os.path.join("saves", "quicksave.json")
            if not os.path.exists(filepath):
                saves = self.list_save_files()
                if saves:
                    filepath = saves[0]["filepath"]
                else:
                    return False, "Ingen gemte spil fundet i 'saves/' mappen."

        if not os.path.exists(filepath):
            return False, f"Gemt spil '{filepath}' blev ikke fundet."

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            p_data = data.get("player", {})
            self.player.name = p_data.get("name", "Konsulent")
            self.player.education = p_data.get("education", "Automation & IT-Sikkerhed")
            if "inventory" in p_data:
                self.player.inventory = set(p_data["inventory"])

            self.game_mode = data.get("game_mode", "teach")
            self.chapter = data.get("chapter", 1)
            self.room = data.get("room", "indgangen")
            self.flags = set(data.get("flags", []))
            self.running = data.get("running", True)
            self.help_calls = data.get("help_calls", 0)

            elapsed = data.get("elapsed_seconds", 0.0)
            self.timer_started_at = time.monotonic() - elapsed

            deadlines = data.get("deadlines", {})
            self.pump_deadline_active = deadlines.get("pump_deadline_active", False)
            if self.pump_deadline_active:
                p_rem = deadlines.get("pump_remaining", self.pump_deadline_seconds)
                self.pump_deadline_started_at = time.monotonic() - (self.pump_deadline_seconds - p_rem)
            else:
                self.pump_deadline_started_at = 0.0

            self.cavitation_deadline_active = deadlines.get("cavitation_deadline_active", False)
            if self.cavitation_deadline_active:
                c_rem = deadlines.get("cav_remaining", self.cavitation_deadline_seconds)
                self.cavitation_deadline_started_at = time.monotonic() - (self.cavitation_deadline_seconds - c_rem)
            else:
                self.cavitation_deadline_started_at = 0.0

            wb = data.get("workbench", {})
            self.active_workbench = wb.get("active_workbench")
            self.vfd_mounted = wb.get("vfd_mounted", False)
            self.vfd_cabled = wb.get("vfd_cabled", False)
            self.wrong_cabling = wb.get("wrong_cabling", False)

            cons = data.get("consequences", {})
            self.breaker_tripped = cons.get("breaker_tripped", False)
            self.scada_blind = cons.get("scada_blind", False)
            self.plc_defect_stop = cons.get("plc_defect_stop", False)
            self.scada_log_interrupted = cons.get("scada_log_interrupted", False)

            m_data = data.get("metrics", {})
            self.metrics.drift = m_data.get("drift", 80)
            self.metrics.sikkerhed = m_data.get("sikkerhed", 25)
            self.metrics.compliance = m_data.get("compliance", 40)
            self.metrics.tillid = m_data.get("tillid", 50)
            self.metrics.history = m_data.get("history", [])

            inv_data = data.get("investigation", {})
            self.investigation.prime_suspect_id = inv_data.get("prime_suspect_id")
            for c_id, c_val in inv_data.get("clues", {}).items():
                if c_id in self.investigation.clues:
                    self.investigation.clues[c_id].discovered = c_val.get("discovered", False)
                    self.investigation.clues[c_id].discovered_time = c_val.get("discovered_time", "")
            for s_id, s_val in inv_data.get("suspects", {}).items():
                if s_id in self.investigation.suspects:
                    self.investigation.suspects[s_id].suspicion_score = s_val.get("suspicion_score", 0)
                    self.investigation.suspects[s_id].status = s_val.get("status", "Aktiv efterforskning")
                    self.investigation.suspects[s_id].notes = s_val.get("notes", [])

            f_data = data.get("forensics", {})
            self.forensics.pi_handling_state = f_data.get("pi_handling_state", "unhandled")
            self.forensics.forensic_violations = f_data.get("forensic_violations", [])
            self.forensics.evidence_log = []
            for ev in f_data.get("evidence_log", []):
                from core.forensics import EvidenceItem
                item = EvidenceItem(
                    item_id=ev.get("item_id", ""),
                    name=ev.get("name", ""),
                    description=ev.get("description", ""),
                    location=ev.get("location", ""),
                    purdue_level=ev.get("purdue_level", ""),
                    mac_address=ev.get("mac_address", ""),
                    ip_address=ev.get("ip_address", ""),
                    sha256=ev.get("sha256", ""),
                    timestamp=ev.get("timestamp", time.time()),
                    secured_properly=ev.get("secured_properly", False),
                    handling_notes=ev.get("handling_notes", ""),
                    seal_number=ev.get("seal_number", ""),
                )
                self.forensics.evidence_log.append(item)

            inc_data = data.get("incident", {})
            self.incident.early_warning_sent = inc_data.get("early_warning_sent", False)
            self.incident.reports = []
            for r_item in inc_data.get("reports", []):
                from core.incident import IncidentReport
                rep = IncidentReport(
                    timestamp=r_item.get("timestamp", time.time()),
                    submitted_day=r_item.get("submitted_day", 1),
                    submitted_hour=r_item.get("submitted_hour", 1),
                    incident_type=r_item.get("incident_type", ""),
                    affected_zone=r_item.get("affected_zone", ""),
                    severity=r_item.get("severity", "HØJ"),
                    initial_actions=r_item.get("initial_actions", ""),
                    is_early_warning_submitted=r_item.get("is_early_warning_submitted", False),
                    early_warning_deadline_hours=r_item.get("early_warning_deadline_hours", 24),
                )
                self.incident.reports.append(rep)

            dev = data.get("devices", {})
            self.rogue_pi.disconnected = dev.get("rogue_pi_disconnected", False)
            if dev.get("rogue_pi_revealed", False):
                self.rogue_pi.reveal()
            self.plc.f_passivated = dev.get("plc_f_passivated", False)
            self.plc.bootloader_locked = dev.get("plc_bootloader_locked", False)

            self._cached_choices = None
            self._cached_state_key = None

            return True, f"📂 [SPIL INDLÆST]: Spillet for '{self.player.name}' (Kapitel {self.chapter}/5, Zone: {self.room}) er genoptaget!"

        except Exception as e:
            return False, f"Fejl under indlæsning af gemt spil '{filepath}': {e}"

    @staticmethod
    def list_save_files() -> list[dict[str, Any]]:
        """List all available save games in the saves/ directory with summary metadata."""
        saves_dir = "saves"
        if not os.path.exists(saves_dir):
            return []
        results = []
        for fname in os.listdir(saves_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(saves_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                results.append({
                    "filename": fname,
                    "filepath": fpath,
                    "save_time": data.get("save_time", "Ukendt tid"),
                    "player_name": data.get("player", {}).get("name", "Konsulent"),
                    "player_education": data.get("player", {}).get("education", ""),
                    "chapter": data.get("chapter", 1),
                    "room": data.get("room", "indgangen"),
                    "game_mode": data.get("game_mode", "teach"),
                    "metrics": data.get("metrics", {}),
                    "mtime": os.path.getmtime(fpath),
                })
            except Exception:
                continue
        results.sort(key=lambda x: x["mtime"], reverse=True)
        return results

    # -------------------------------------------------------------------------
    # ROOMS, CHOICES & NAVIGATION
    # -------------------------------------------------------------------------
    def get_current_room(self) -> BaseRoom:
        return ALL_ROOMS.get(self.room, ALL_ROOMS["indgangen"])

    def describe_room(self) -> None:
        r = self.get_current_room()
        self.emit(f"[{r.title.upper()} - {r.purdue_level}]")
        self.emit(r.get_description(self))
        choices_text = self.format_choices_text()
        if choices_text:
            self.emit(choices_text)

    def get_state_key(self) -> tuple[Any, ...]:
        return (
            self.room,
            self.chapter,
            self.active_workbench,
            self.game_mode,
            tuple(sorted(self.flags)),
            self.breaker_tripped,
            self.scada_blind,
            self.plc_defect_stop,
            self.scada_log_interrupted,
            self.vfd_mounted,
            self.vfd_cabled,
            self.wrong_cabling,
        )

    def get_current_choices(self) -> list[tuple[str, str, str, str]]:
        state_key = self.get_state_key()
        if self._cached_state_key == state_key and self._cached_choices is not None:
            return self._cached_choices

        r = self.get_current_room()
        raw_choices = r.get_choices(self)
        if not raw_choices:
            self._cached_choices = []
            self._cached_state_key = state_key
            return []

        actions: list[tuple[str, str, str]] = []
        navs: list[tuple[str, str, str]] = []

        for item in raw_choices:
            _old_k, label, cmd, cat = item
            if cmd.startswith("gå til ") or cmd in {"vis rum", "luk workbench"}:
                navs.append((label, cmd, cat))
            else:
                actions.append((label, cmd, cat))

        if self.shuffle_choices and len(actions) > 1:
            random.shuffle(actions)

        combined = actions + navs
        indexed_choices = [
            (str(idx + 1), label, cmd, cat)
            for idx, (label, cmd, cat) in enumerate(combined)
        ]

        self._cached_choices = indexed_choices
        self._cached_state_key = state_key
        return indexed_choices

    def format_choices_text(self) -> str:
        choices = self.get_current_choices()
        if not choices:
            return ""
        mode_badge = "🎓 TEACH MODE (Hjælp & Faldgruber)" if self.game_mode == "teach" else "📝 EKSAMENS-MODE (Realistiske Valg)"
        lines = [
            f"\n┌── TILGÆNGELIGE VALG [{mode_badge}] ───────────────────────────────",
        ]
        for key, label, _cmd, _cat in choices:
            lines.append(f"│ [{key}] {label}")
        lines.append("└── Tast tal (1-N) eller skriv handling ───────────────────────────────────────────────")
        return "\n".join(lines)

    def toggle_game_mode(self, target_mode: str | None = None) -> None:
        if target_mode in {"teach", "exam"}:
            self.game_mode = target_mode
        else:
            self.game_mode = "exam" if self.game_mode == "teach" else "teach"
        self._cached_choices = None
        self._cached_state_key = None
        if self.game_mode == "teach":
            self.emit("\n🎓 [TILSTAND: TEACH MODE AKTIVERET]:")
            self.emit("Faglige råd, trusselsadvarsler og faldgrube-tags er nu synlige i menuen.")
        else:
            self.emit("\n📝 [TILSTAND: EKSAMENS-MODE AKTIVERET]:")
            self.emit("Ingen spoilers eller faldgrube-tags! Alle valgmuligheder fremstår som realistiske ingeniørbeslutninger.")
            self.emit("Valgmulighederne er blandet tilfældigt, så du skal vurdere den tekniske handling nøje.")

    def execute_choice(self, key: str) -> bool:
        norm_key = key.lower().strip()
        choices = self.get_current_choices()
        for k, label, cmd, _cat in choices:
            if norm_key == k.lower().strip():
                self.emit(f"\n👉 [VALG {k}]: {label}")
                self.handle_command(cmd)
                return True
        return False

    def go_to(self, destination: str) -> None:
        aliases = {
            "pumperne": "pumpehuset", "pumpehus": "pumpehuset", "pumpehuset": "pumpehuset",
            "ventil-øen": "ventil-oen", "ventiløen": "ventil-oen", "ventil": "ventil-oen",
            "ventiler": "ventil-oen", "ventil-oen": "ventil-oen", "ventiloen": "ventil-oen",
            "el-tavlen": "el-tavlen", "hoved-el-tavlen": "el-tavlen", "tavlen": "el-tavlen",
            "kontrolrummet": "kontrolrummet", "kontrolrum": "kontrolrummet", "idmz": "kontrolrummet",
            "indgangen": "indgangen", "indgang": "indgangen", "hovedindgang": "indgangen",
        }
        dest_norm = destination.lower().strip()
        clean = dest_norm.replace("ø", "oe").replace("å", "aa").replace("æ", "ae")
        target_room = aliases.get(dest_norm) or aliases.get(clean) or (dest_norm if dest_norm in ALL_ROOMS else None)

        if not target_room:
            self.emit("Ukendt destination. Gyldige zoner: INDGANGEN, PUMPEHUSET, VENTIL-ØEN, EL-TAVLEN, KONTROLRUMMET.")
            return

        if target_room == self.room:
            self.emit(f"Du befinder dig allerede i {ALL_ROOMS[self.room].title}.")
            return

        self.room = target_room
        self.active_workbench = None
        self.describe_room()

        # Trigger acute pump deadline ONLY upon entering Pumpehuset
        if self.room == "pumpehuset" and "chapter-1-done" not in self.flags and not self.pump_deadline_active:
            self.pump_deadline_started_at = time.monotonic()
            self.pump_deadline_active = True
            self.emit("\n🚨 [AKUT HÆNDELSE AKTIVERET!]: Idet du træder ind ad døren til Pumpehuset, gjalder sirenen!")
            self.emit("Pumpe 2 hyler voldsomt som en overophedet kedel! Manometeret vibrerer på 133.7 Bar og nærmer sig sprængningsgrænsen (150 Bar)!")
            self.emit("Du har 3 minutter til at afværge sprængningen! Brug Wireshark i terminalen for at fange angriberens pakker.")

    # -------------------------------------------------------------------------
    # COMMAND PROCESSING
    # -------------------------------------------------------------------------
    def handle_command(self, command: str) -> None:
        raw = command.strip()
        if not raw:
            if self.chapter > 0 and self.running:
                self.emit(self.format_choices_text())
            return
        normalized = re.sub(r"\s+", " ", raw.lower())

        # Menu and start screen transitions (always available, even when finished or stopped)
        if normalized in {
            "hovedmenu", "hovemenu", "menu", "hjem", "home",
            "startskærm", "startskaerm", "afslut til menu", "hoved menu", "main menu"
        }:
            self.flags.add("return-to-menu")
            self.emit("\n🏠 [HOVEDMENU]: Vender tilbage til startskærmen...")
            return

        # Save and Load commands (always available)
        if normalized in {"gem", "gem spil", "save", "savegame"}:
            ok, msg = self.save_state()
            self.emit(msg)
            return
        if normalized.startswith("gem "):
            save_name = normalized.removeprefix("gem ").strip()
            filepath = os.path.join("saves", f"{save_name}.json" if not save_name.endswith(".json") else save_name)
            ok, msg = self.save_state(filepath)
            self.emit(msg)
            return
        if normalized in {"hent", "hent spil", "indlæs", "indlaes", "load"}:
            ok, msg = self.load_state()
            self.emit(msg)
            if ok:
                self.describe_room()
            return
        if normalized.startswith("hent ") or normalized.startswith("load ") or normalized.startswith("indlæs ") or normalized.startswith("indlaes "):
            save_name = normalized.replace("hent ", "").replace("load ", "").replace("indlæs ", "").replace("indlaes ", "").strip()
            filepath = os.path.join("saves", f"{save_name}.json" if not save_name.endswith(".json") else save_name)
            ok, msg = self.load_state(filepath)
            self.emit(msg)
            if ok:
                self.describe_room()
            return
        if normalized in {"gemte spil", "saves", "vis saves", "list saves"}:
            saves = self.list_save_files()
            if not saves:
                self.emit("Ingen gemte spil fundet i 'saves/' mappen.")
            else:
                self.emit("\n💾 [GEMTE SPIL I 'saves/']:")
                for s in saves:
                    self.emit(f"  • {s['filename']} ({s['save_time']}) - {s['player_name']} (Kapitel {s['chapter']}/5, {s['game_mode'].upper()})")
            return

        # If game is stopped or completed, notify user how to return to menu
        if not self.running:
            self.emit(
                "\n💡 [MISSIONEN ER AFSLUTTET]\n"
                "Tast 'hovedmenu' eller klik på '🏠 HOVEDMENU' øverst for at vende tilbage til startskærmen,\n"
                "hvor du kan starte en ny mission eller indlæse et tidligere spil."
            )
            return

        # Check timers for active simulation
        if not self.check_timers():
            return

        # Mode toggles
        if normalized in {"tilstand", "mode", "skift tilstand", "toggle mode"}:
            self.toggle_game_mode()
            self.emit(self.format_choices_text())
            return
        if normalized in {"tilstand teach", "mode teach", "teach", "teach mode", "undervisning"}:
            self.toggle_game_mode("teach")
            self.emit(self.format_choices_text())
            return
        if normalized in {"tilstand eksamen", "mode exam", "eksamen", "exam", "exam mode"}:
            self.toggle_game_mode("exam")
            self.emit(self.format_choices_text())
            return
        if normalized in {"valg", "menu", "muligheder", "handlinger"}:
            self.emit(self.format_choices_text())
            return

        # Direct number choice
        if normalized in {str(i) for i in range(1, 20)}:
            if self.execute_choice(normalized):
                return

        # General game commands
        if normalized in {"hjælp", "help", "?"}:
            self.help()
        elif normalized in {"status", "mål", "mission"}:
            self.status()
        elif normalized in {"rundtur", "tour"}:
            self.tour()
        elif normalized in {"techsupport", "support", "ring support"}:
            self.call_tech_support()
        elif normalized in {"inventory", "inventar", "rygsæk", "taske"}:
            self.emit("[RYGSÆK] Din rygsæk indeholder: " + ", ".join(sorted(self.player.inventory)))
        elif normalized in {"vis evidens", "evidens", "logbog", "forensik"}:
            self.emit(self.forensics.get_summary())
        elif normalized in {"sagstavle", "tavle", "board", "case board", "clueboard", "investigation", "efterforskning"}:
            self.emit(self.investigation.format_clue_board(self.metrics))
        elif normalized in {"spor", "clues", "evidensliste"}:
            self.emit(self.investigation.format_clues_list())
        elif normalized.startswith("analyser spor ") or normalized.startswith("analyser "):
            s_id = normalized.replace("analyser spor ", "").replace("analyser ", "").strip()
            self.emit(self.investigation.format_clue_analysis(s_id))
        elif normalized in {"mistænkte", "mistaenkte", "suspects", "hypoteser"}:
            self.emit(self.investigation.format_suspects_list())
        elif normalized.startswith("anklag ") or normalized.startswith("hypotese "):
            susp_id = normalized.replace("anklag ", "").replace("hypotese ", "").strip()
            ok, msg = self.investigation.set_prime_suspect(susp_id)
            self.emit(msg)
            if ok:
                self.metrics.adjust_tillid(5, f"Arbejdshypotese fastsat: {susp_id}")
        elif normalized in {"metrikker", "metrics", "score", "konsekvenser"}:
            self.show_metrics_status()
        elif normalized in {"indberet hændelse", "early warning", "indberet", "anmeld hændelse"}:
            self.submit_early_warning()
        elif normalized in {"eksporter rapport", "eksport rapport", "gem rapport"}:
            self.export_audit_report()
        elif normalized in {"fremlæg sagstavle", "fremlaeg sagstavle", "fremlæg sag", "fremlaeg sag", "fremlæg", "fremlaeg", "afslut efterforskning", "fremlæg beviser", "fremlaeg beviser"}:
            self.present_case_investigation()
        elif normalized.startswith("tshark") or normalized in {"man tshark", "cheat tshark", "tshark cheatsheet", "tshark help"}:
            self.flags.add("wireshark-open")
            if self.room == "pumpehuset":
                self.record_clue("spor_modbus_flood")
            elif self.room == "ventil-oen":
                self.record_clue("spor_dcp_storm")
                self.record_clue("spor_mac_oui")
            elif self.room == "el-tavlen":
                self.record_clue("spor_plc_stop_buffer")
            elif self.room == "kontrolrummet":
                self.record_clue("spor_opc_leak")
            self.emit(self.sniffer.execute_tshark_command(raw, self.room, engine=self))
        elif normalized.startswith("wireshark filter "):
            filt = normalized.removeprefix("wireshark filter ").strip()
            self.flags.add("wireshark-open")
            if self.room == "pumpehuset":
                self.record_clue("spor_modbus_flood")
            elif self.room == "ventil-oen":
                self.record_clue("spor_dcp_storm")
                self.record_clue("spor_mac_oui")
            elif self.room == "el-tavlen":
                self.record_clue("spor_plc_stop_buffer")
            elif self.room == "kontrolrummet":
                self.record_clue("spor_opc_leak")
            self.emit(f"💡 [TSHARK INFO]: I terminalen anvendes 'tshark -Y \"{filt}\"'. Kører filter for dig:")
            self.emit(self.sniffer.execute_tshark_command(f"tshark -Y \"{filt}\"", self.room, engine=self))
        elif normalized.startswith("wireshark detaljer "):
            pkt = normalized.removeprefix("wireshark detaljer ").strip()
            self.flags.add("wireshark-open")
            self.emit("💡 [TSHARK INFO]: I terminalen anvendes 'tshark -V'. Kører protokol-dissekering:")
            self.emit(self.sniffer.execute_tshark_command("tshark -V", self.room, engine=self))
        elif normalized in {"åbn wireshark", "wireshark", "start wireshark", "sniffer"}:
            self.flags.add("wireshark-open")
            if self.room == "pumpehuset":
                self.record_clue("spor_modbus_flood")
            elif self.room == "ventil-oen":
                self.record_clue("spor_dcp_storm")
                self.record_clue("spor_mac_oui")
            elif self.room == "el-tavlen":
                self.record_clue("spor_plc_stop_buffer")
            elif self.room == "kontrolrummet":
                self.record_clue("spor_opc_leak")
            self.emit(f"💡 [TSHARK INFO]: Kører tshark på '{self.room}_vlan'... (Skriv 'man tshark' for filtre som f.eks. -Y \"modbus\")")
            self.emit(self.sniffer.execute_tshark_command("tshark", self.room, engine=self))
        elif normalized.startswith("spørg hans om ") or normalized.startswith("afhør hans om ") or normalized.startswith("spoerg hans om "):
            topic = normalized.replace("spørg hans om ", "").replace("afhør hans om ", "").replace("spoerg hans om ", "").strip()
            self.emit(self.hans.interrogate(self, topic))
        elif normalized.startswith("spørg kirsten om ") or normalized.startswith("afhør kirsten om ") or normalized.startswith("spoerg kirsten om "):
            topic = normalized.replace("spørg kirsten om ", "").replace("afhør kirsten om ", "").replace("spoerg kirsten om ", "").strip()
            self.emit(self.kirsten.interrogate(self, topic))
        elif normalized in {"ring til kirsten", "ring kirsten", "kontakt tilsynet", "interim audit", "ring tilsynet"}:
            self.emit(self.kirsten.get_interim_audit(self))
        elif normalized.startswith("gå til ") or normalized.startswith("gaa til "):
            dest = normalized.replace("gå til ", "").replace("gaa til ", "")
            self.go_to(dest)
            return
        elif normalized.startswith("undersøg ") or normalized.startswith("undersoeg "):
            item = normalized.replace("undersøg ", "").replace("undersoeg ", "")
            self.inspect(item)
        elif normalized.startswith("tal med "):
            target = normalized.replace("tal med ", "")
            self.talk_to(target)
        elif normalized in {"revisor", "audit"} and self.chapter == 5:
            self.complete_audit()
            return
        elif self.handle_domain_actions(normalized):
            pass
        else:
            self.emit(f"Kommandoen '{command}' blev ikke genkendt. Prøv et tal fra menuen eller skriv 'hjælp'.")

        # Always reprint choices after an action so options are never lost!
        if self.running and self.chapter > 0:
            choices_text = self.format_choices_text()
            if choices_text:
                self.emit(choices_text)

    # -------------------------------------------------------------------------
    # DOMAIN SPECIFIC ACTIONS & CASCADING BRANCHES
    # -------------------------------------------------------------------------
    def handle_domain_actions(self, cmd: str) -> bool:
        # Chapter 1: Modbus Sabotage, DIN-rail Workbench & Firewall CLI
        if "firewall rule" in cmd or "firewall add" in cmd or cmd.startswith("firewall --") or cmd.startswith("scalance rule"):
            self.apply_firewall_rule(cmd)
            return True
        if cmd in {"firewall status", "firewall rules", "scalance status", "vis firewall"}:
            self.show_firewall_status()
            return True
        if any(k in cmd for k in {"firewall workbench", "vfd workbench", "åbn workbench", "din-skinne", "din skinne", "arbejdsbænk"}):
            self.open_vfd_workbench()
            return True
        if any(k in cmd for k in {"switch workbench", "montage workbench"}):
            self.open_switch_workbench()
            return True
        if any(k in cmd for k in {"monter scalance", "monter firewall", "fastgør scalance"}):
            self.mount_scalance_on_rail()
            return True
        if any(k in cmd for k in {"kobl kabler", "forbind kabler", "patchkabler", "kabling"}):
            self.cable_scalance_correctly()
            return True
        if any(k in cmd for k in {"byt om på lan", "forkert kabling", "wan i vfd"}):
            self.cable_scalance_wrong()
            return True
        if any(k in cmd for k in {"vis rum", "luk workbench", "tilbage til rum", "forlad workbench", "tilbage"}):
            self.close_workbench()
            return True
        if any(k in cmd for k in {"hård nødnedlukning", "træk afbryder", "sluk vfd"}):
            self.hard_shutdown_vfd()
            return True
        if any(k in cmd for k in {"juster setpunkt", "drej potentiometer", "manuel justering"}):
            self.manual_vfd_adjustment_fails()
            return True
        if any(k in cmd for k in {"bloker port 502", "drop port 502"}):
            self.block_port_502_blindly()
            return True
        if any(k in cmd for k in {"nulstil relæ", "nulstil k1", "k1 reset"}):
            self.reset_safety_breaker()
            return True
        if any(k in cmd for k in {"aktiver modbus dpi", "fix scada filter", "skift til dpi", "modbus dpi", "tillad fc03", "konfigurer firewall"}):
            self.solve_chapter_1()
            return True

        # Chapter 2: PROFINET & Rogue Pi Dilemmas
        if any(k in cmd for k in {"sikr pi i faraday", "faraday-pose", "forensisk sikring"}):
            self.handle_pi_removal("faraday")
            return True
        if any(k in cmd for k in {"smid pi i skraldespand", "skraldespand", "smid ud"}):
            self.handle_pi_removal("skraldespand")
            return True
        if any(k in cmd for k in {"gem pi til genbrug", "tag med hjem", "iot"}):
            self.handle_pi_removal("genbrug")
            return True
        if any(k in cmd for k in {"indsæt sd-kort", "sd-kort i bærbar", "undersøg sd"}):
            self.handle_pi_removal("sd-kort i laptop")
            return True
        if any(k in cmd for k in {"pille switch fra", "træk kabler ud af switch"}):
            self.unplug_switch_abruptly()
            return True
        if any(k in cmd for k in {"genstart et200sp", "genstart io"}):
            self.reboot_et200sp_fails()
            return True
        if any(k in cmd for k in {"udskift switch med scalance", "installer scalance", "mrp ring"}):
            self.solve_chapter_2()
            return True

        # Chapter 3: S7-1500 5-Way Branching
        if any(k in cmd for k in {"tag offline backup", "usb-backup", "offline backup"}):
            self.take_plc_backup()
            return True
        if any(k in cmd for k in {"konfigurer tia portal", "deaktiver put/get", "tia portal"}):
            self.configure_tia_portal()
            return True
        if any(k in cmd for k in {"tving cpu i run", "tving i run", "nøglekontakt"}):
            self.force_cpu_run_fails()
            return True
        if any(k in cmd for k in {"bloker port 102", "drop port 102", "firewall 102"}):
            self.block_port_102_passivates_safety()
            return True
        if any(k in cmd for k in {"opdater firmware live", "firmware live", "live patch"}):
            self.live_firmware_patch_corrupts()
            return True
        if any(k in cmd for k in {"kobl laptop i plc", "laptop i plc port", "uisoleret laptop"}):
            self.direct_laptop_arp_poisoned()
            return True
        if any(k in cmd for k in {"gendan plc db1", "gendan db1", "restore db1"}):
            self.restore_plc_db1()
            return True

        # Chapter 4: Real-World OPC UA & IDMZ
        if any(k in cmd for k in {"godkend scada certifikat", "flyt certifikat", "trust cert"}):
            self.trust_scada_certificate()
            return True
        if any(k in cmd for k in {"aktiver opc kryptering", "basic256sha256", "signandencrypt"}):
            self.enable_opc_crypto()
            return True
        if any(k in cmd for k in {"deaktiver anonymous", "fjern anonymous", "håndhæv rbac"}):
            self.disable_opc_anonymous()
            return True
        if any(k in cmd for k in {"frakobl 4g-router", "fjern 4g", "konfisker 4g"}):
            self.disconnect_4g_router()
            return True
        if any(k in cmd for k in {"bloker port 4840", "drop port 4840"}):
            self.block_port_4840_blindly()
            return True
        if any(k in cmd for k in {"aktiver opc certifikater", "genåbn 4840"}):
            self.restore_scada_logging()
            return True

        return False

    # -------------------------------------------------------------------------
    # CHAPTER 1 ACTIONS
    # -------------------------------------------------------------------------
    def manual_vfd_adjustment_fails(self) -> None:
        self.emit("\n⚠️ [MANUEL DRIFTSFEJL - SIKKERHEDS-OVERSTYRING]:")
        self.emit("Du forsøger febrilsk at dreje potentiometeret på frekvensomformerens frontpanel ned på 50 Hz...")
        self.emit("Men inden for 20 millisekunder overskriver angriberens Modbus-loop værdien tilbage til 1337!")
        self.emit("Pumpe 2 hyler i smerte, og du taber 20 sekunder på pumpe-timeren!")
        self.emit("IEC 62443 læresætning: Du kan IKKE overstyre et netværksangreb med manuelle knapper på komponenten. "
                  "Du er nødt til at etablere en netværksfirewall (conduit) med Deep Packet Inspection!")
        if self.pump_deadline_active:
            self.pump_deadline_started_at -= 20

    def hard_shutdown_vfd(self) -> None:
        self.emit("\n🚨 [HYDRAULISK VANDSLAG - DRIFTSAFBRYDELSE]:")
        self.emit("Du flår hovedafbryderen til frekvensomformeren ud under fuld last (146 Bar)!")
        self.emit("Motoren dør brat. Den pludselige kinetiske standsning af 12 tons vand i DN150-røret skaber et voldsomt trykstød (vandslag).")
        self.emit("Overspændingsbølgen forplanter sig bagud, og med et højt knald slår sikkerhedsrelæ K1 i Hoved-el-tavlen fra!")
        self.emit("Frekvensomformeren er nu fuldstændig strømløs. Du kan ikke konfigurere den, før du har været i El-tavlen og nulstillet K1!")
        self.breaker_tripped = True
        self.flags.add("breaker-tripped")

    def block_port_502_blindly(self) -> None:
        self.emit("\n⚠️ [GROV NETVÆRKSBLOKERING - SCADA BLINDHED]:")
        self.emit("Du aktiverer en simpel Layer 3 firewall-regel: 'DROP ALL TCP 502'.")
        self.emit("Angriberen er stoppet, men SCADA-operatøren i kontrolrummet råber i radioen:")
        self.emit("'Skærmen er frosset! Vi har mistet overvågningen af hele vandværket!'")
        self.emit("Læresætning: I procesnetværk må du ikke bare blokere porten – du skal implementere Deep Packet Inspection (DPI) "
                  "der tillader lovlig læsning (FC 03), men blokerer uautoriserede skrivninger (FC 06/16)!")
        self.scada_blind = True
        self.flags.add("scada-blind")

    def reset_safety_breaker(self) -> None:
        if not self.breaker_tripped:
            self.emit("Sikkerhedsrelæ K1 er allerede i normal position.")
            return
        self.emit("\n✅ [SIKKERHEDSRELÆ K1 NULSTILLET]:")
        self.emit("Du åbner el-tavlen og flipper K1-hovedafbryderen tilbage til ON. Frekvensomformeren i Pumpehuset tænder igen!")
        self.breaker_tripped = False
        self.flags.discard("breaker-tripped")

    def open_vfd_workbench(self) -> None:
        self.active_workbench = "vfd_workbench"
        self.emit("\n🔧 [TS35 DIN-SKINNE ARBEJDSBÆNK ÅBNET]:")
        self.emit("Du træder hen til 35mm DIN-skinnen ved siden af Pumpe 2.")
        self.emit("Her skal der etableres et sikkert conduit jf. IEC 62443-3-2 foran frekvensomformeren.")
        self.emit("Du har en fabriksny Siemens SCALANCE S615 sikkerhedsrouter i kassen.")
        self.emit("\nFremgangsmåde på arbejdsbænken:")
        self.emit("  1. Fastgør SCALANCE S615 på DIN-skinnen ('monter scalance på din-skinne')")
        self.emit("  2. Kobl patchkabler: VFD til LAN (P1) og anlæg til WAN (P5) ('kobl kabler til scalance')")
        self.emit("  3. Aktivér Modbus DPI regelsæt: Tillad FC 03 Læs, Drop FC 06 Skriv ('aktiver modbus dpi')")
        self.emit("  4. Eller klik direkte på DIN-skinnen på skærmen foroven!")

    def open_switch_workbench(self) -> None:
        self.active_workbench = "switch_workbench"
        self.emit("\n🛠️ [SWITCH MONTAGE-ARBEJDSBÆNK ÅBNET]:")
        self.emit("Du træder hen til tavlen på Ventil-øen med SCALANCE XB-200 managed switch og redundant MRP-ring.")

    def mount_scalance_on_rail(self) -> None:
        self.vfd_mounted = True
        self.active_workbench = "vfd_workbench"
        self.emit("\n🔌 [SCALANCE S615 MONTERET PÅ DIN-SKINNE]:")
        self.emit("Du klikker Siemens SCALANCE S615 routeren fast på 35mm TS35 DIN-skinnen.")
        self.emit("Routeren sidder solidt med jordforbindelse via fjederbeslaget.")
        self.emit("Næste skridt: Kobl netværkskablerne ('kobl kabler til scalance' eller valg 2).")

    def cable_scalance_correctly(self) -> None:
        if not self.vfd_mounted:
            self.vfd_mounted = True
            self.emit("\n(Du fastgør først SCALANCE S615 på DIN-skinnen)")
        self.vfd_cabled = True
        self.wrong_cabling = False
        self.active_workbench = "vfd_workbench"
        self.emit("\n🔀 [KABLER FORBUNDET KORREKT - PURDUE LEVEL 1 CONDUIT]:")
        self.emit("  • Grønt kabel fra SINAMICS VFD tilsluttes beskyttet LAN Port P1.")
        self.emit("  • Gult anlægskabel fra SCADA/switch tilsluttes WAN Port P5.")
        self.emit("Link-dioderne blinker grønt! Routeren adskiller nu VFD-cellen fra det øvrige netværk.")
        self.emit("Næste skridt: Aktivér Modbus DPI regelsættet ('aktiver modbus dpi' eller valg 3).")

    def cable_scalance_wrong(self) -> None:
        self.wrong_cabling = True
        self.active_workbench = "vfd_workbench"
        self.emit("\n⚠️ [FALDGRUBE: FORKERT KABLING - INGEN BESKYTTELSE]:")
        self.emit("Du forbyttede portene og satte kablet fra frekvensomformeren i WAN i stedet for LAN!")
        self.emit("Konsekvens:")
        self.emit("  1. Frekvensomformeren er stadig direkte eksponeret mod angriberens net uden firewall-filtrering.")
        self.emit("  2. WAN-firewallen blokerer legitim telemetri til WinCC SCADA.")
        self.emit("Læresætning: I industrielle firewalls skal den sårbare enhed altid placeres i den beskyttede interne LAN-zone!")
        self.emit("Byt om på kablerne ('kobl kabler til scalance' eller valg 2) for at rette fejlen.")

    def close_workbench(self) -> None:
        self.active_workbench = None
        self.emit("\n🚪 Du træder tilbage fra arbejdsbænken og ser ud over rummet.")

    def apply_firewall_rule(self, cmd: str) -> None:
        if self.breaker_tripped:
            self.emit("⚠️ Frekvensomformeren er strømløs på grund af udløst K1-relæ! Nulstil K1 i El-tavlen først.")
            return

        if not self.vfd_mounted or not self.vfd_cabled:
            self.vfd_mounted = True
            self.vfd_cabled = True
            self.wrong_cabling = False
            self.emit("\n(SCALANCE S615 monteres på TS35 DIN-skinnen og patchkabler forbindes til LAN P1 og WAN P5)")

        if self.wrong_cabling:
            self.emit("⚠️ Kan ikke anvende firewall-regler: Kablerne er krydset forkert! VFD sidder i WAN-porten i stedet for LAN.")
            self.emit("Byt om på kablerne ('kobl kabler til scalance'), så frekvensomformeren sidder i beskyttet LAN P1!")
            return

        norm_cmd = cmd.lower()
        has_allow_fc3 = any(k in norm_cmd for k in {"allow-fc 3", "allow-fc3", "allow fc 3", "allow fc03", "allow fc 03", "allow-fc 03", "tillad fc 03", "tillad fc03", "tillad fc 3"})
        has_drop_fc6 = any(k in norm_cmd for k in {"drop-fc 6", "drop-fc6", "drop fc 6", "drop fc06", "drop fc 06", "drop-fc 06", "drop-fc 6,16", "drop-fc 6, 16", "afvis fc 06", "afvis fc 6", "afvis fc06"})

        # Case A: Correct rule (Allow FC 03 AND Drop FC 06/16)
        if has_allow_fc3 and (has_drop_fc6 or "drop" in norm_cmd):
            self.scada_blind = False
            self.flags.discard("scada-blind")
            self.flags.add("chapter-1-done")
            self.pump_deadline_active = False
            self.active_workbench = None
            self.chapter = 2
            self.metrics.adjust_drift(10, "Pumpe 2 normaliseret til 3.2 Bar")
            self.metrics.adjust_sikkerhed(25, "Modbus FC06 spærret med DPI-firewall")
            self.metrics.adjust_tillid(15, "Hans roser rolig motorgang")
            self.metrics.adjust_compliance(15, "IEC 62443 zone 1 conduit etableret")
            self.record_clue("spor_modbus_flood")
            self.emit("\n✅ [SCALANCE S615 DPI REGEL AKTIVERET - GULDSTANDARD]:")
            self.emit("Regel oprettet: PERMIT Modbus TCP FC 03 (WinCC SCADA Telemetri)")
            self.emit("Regel oprettet: DROP & LOG Modbus TCP FC 06/16 (Sabotage Register-skrivning)")
            self.emit("Default Policy: DROP (Conduit IEC 62443-3-2)")
            self.emit("\n🎉 RESULTAT:")
            self.emit("  • WinCC SCADA modtager ubrudt telemetri via FC 03.")
            self.emit("  • Angriberens uautoriserede Modbus FC 06-pakker droppes ved indgangen til cellen.")
            self.emit("  • Pumpe 2's omdrejningstal falder til 450 RPM. Manometeret stabiliserer sig på 42.0 Bar!")
            self.emit("\n[MÅL] NYT MÅL: Kapitel 2 aktiveret! Hans kalder over radioen:")
            self.emit("'Skynd dig til VENTIL-ØEN! Ventilerne danser rundt i et PROFINET kaos!'")
            return

        # Case B: The critical mistake: Forgetting allow FC 03 (only drop FC 06)
        if has_drop_fc6 and not has_allow_fc3:
            self.scada_blind = True
            self.flags.add("scada-blind")
            self.metrics.adjust_drift(-25, "SCADA blindet - telemetritab")
            self.metrics.adjust_tillid(-15, "Hans i panik over blinde transmittere")
            self.metrics.adjust_compliance(-10, "Mangler driftsobservation")
            self.emit("\n⚠️ [FIREWALL-REGEL AKTIVERET - MEN SCADA GIK I FEJL!]:")
            self.emit("Regel oprettet: DROP & LOG Modbus TCP FC 06/16.")
            self.emit("Hov! SCALANCE S615 kører med industriel default-deny policy, og du har IKKE oprettet en ALLOW-regel for FC 03!")
            self.emit("\n🚨 SCADA-ALARM HYLER I KONTROLRUMMET:")
            self.emit("\"ALARM: TAB AF PROCESOVERVÅGNING PÅ PUMPE 2! (WinCC Modbus Timeout Port 502)\"")
            self.emit("\nHans McDonald kalder febrilsk over radioen:")
            self.emit("\"Hov, makker! Hvad skete der lige?! Pumpe 2 trykket på driftsskærmen viser '??? BAR' og blinker rødt!")
            self.emit("Du har nok afvist angriberens FC 06 sabotage, men du GLEMTE at tillade WinCC SCADA's FC 03 (Read Holding Registers)!")
            self.emit("Firewallen blokerer alt der ikke er eksplicit tilladt, så vi kan slet ikke se om anlægget kører!\"")
            self.emit("\nLæresætning (IEC 62443 / NIS2 Artikel 21):")
            self.emit("I OT-sikkerhed er Oppetid & Observability (Availability) lige så vigtigt som integritet!")
            self.emit("En firewall-regel i et industrielt conduit skal altid eksplicit tillade legitim procesovervågning (FC 03).")
            self.emit("\n💡 Prøv at køre 'tshark -Y \"modbus\"' for at se de blokerede SCADA-pakker.")
            self.emit("Ret fejlen ved at tilføje allow-reglen: 'firewall rule add --allow-fc 3 --drop-fc 6'")
            return

        # Case C: Blocking all port 502
        if any(k in norm_cmd for k in {"drop port 502", "bloker port 502", "drop modbus", "drop all"}):
            self.block_port_502_blindly()
            return

        # Case D: Allow all
        if "allow all" in norm_cmd or "allow modbus" in norm_cmd:
            self.emit("\n⚠️ [FIREWALL-REGEL FOR ÅBEN - SABOTAGE FORTSÆTTER]:")
            self.emit("Du oprettede en regel der tillader al Modbus TCP-trafik uden inspektion.")
            self.emit("Angriberen overskriver fortsat register 0x0000 med 1337! Pumpe 2 skriger videre!")
            return

        self.emit("Ukendt firewall-kommando. Eksempel: 'firewall rule add --allow-fc 3 --drop-fc 6' eller 'firewall status'")

    def show_firewall_status(self) -> None:
        self.emit("\n┌── SCALANCE S615 FIREWALL STATUS & REGELTABEL ───────────────────────")
        self.emit(f"│ Fysisk montage: {'OK (TS35 DIN-skinne)' if self.vfd_mounted else 'IKKE MONTERET'}")
        self.emit(f"│ Kabling:        {'OK (VFD: LAN P1, Uplink: WAN P5)' if (self.vfd_cabled and not self.wrong_cabling) else 'FORKERT ELLER MANGLER'}")
        self.emit("│")
        if "chapter-1-done" in self.flags:
            self.emit("│ Regel #1: Modbus TCP FC 03 (Read)      -> ACTION: PERMIT (SCADA OK)")
            self.emit("│ Regel #2: Modbus TCP FC 06/16 (Write)  -> ACTION: DROP & LOG (Sabotage blokeret)")
            self.emit("│ Default Policy: DROP (Conduit IEC 62443-3-2)")
            self.emit("│ Status: ✅ OPTIMAL DRIFT & SIKKERHED (Pumpe 2: 42.0 Bar)")
        elif self.scada_blind:
            self.emit("│ Regel #1: Modbus TCP FC 06/16 (Write)  -> ACTION: DROP & LOG")
            self.emit("│ Regel #2: Modbus TCP FC 03 (Read)      -> ACTION: [MANGLER!]")
            self.emit("│ Default Policy: DROP")
            self.emit("│ Status: 🚨 FEJL - SCADA BLIND! Mangler 'allow-fc 3'!")
        else:
            self.emit("│ Regel #1: [INGEN REGLER AKTIVE - ANLÆG UBESKYTTET]")
            self.emit("│ Status: ⚠️ SÅRBAR OVER FOR SABOTAGE")
        self.emit("└─────────────────────────────────────────────────────────────────────")

    def solve_chapter_1(self) -> None:
        self.apply_firewall_rule("firewall rule add --allow-fc 3 --drop-fc 6")

    # -------------------------------------------------------------------------
    # CHAPTER 2 ACTIONS
    # -------------------------------------------------------------------------
    def handle_pi_removal(self, method: str) -> None:
        success, message = self.forensics.secure_rogue_pi(method)
        self.emit(f"\n{message}")
        self.flags.add("pi-removed")
        self.rogue_pi.disconnected = True
        self.rogue_pi.disposition = self.forensics.pi_handling_state
        if method in {"faraday", "sikr", "pose"}:
            self.metrics.adjust_sikkerhed(20, "Rogue hardware isoleret")
            self.metrics.adjust_compliance(25, "Forensisk chain of custody overholdt")
            self.metrics.adjust_tillid(10, "Professionel håndtering af bevismateriale")
        elif method in {"trash", "skraldespand"}:
            self.metrics.adjust_compliance(-30, "Destruktion af retsmedicinsk bevis")
            self.metrics.adjust_tillid(-10, "Hans utilfreds med sjusk")
        elif method in {"reuse", "genbrug", "infected", "sd-kort"}:
            self.metrics.adjust_sikkerhed(-25, "Kompromitteret udstyr genanvendt")
            self.metrics.adjust_compliance(-25, "Sikkerhedsbrud på privat hardware")
        self.record_clue("spor_sort_boks")
        self.emit("\nDu kan nu udskifte den gamle D-Link switch med den industrielle SCALANCE XB-200 med MRP-ring!")

    def unplug_switch_abruptly(self) -> None:
        if "chapter-2-done" in self.flags:
            self.emit("SCALANCE switchen er allerede monteret og kører med MRP-ring.")
            return
        if not self.cavitation_deadline_active:
            self.cavitation_deadline_started_at = time.monotonic()
            self.cavitation_deadline_active = True
            self.metrics.adjust_drift(-20, "Kaotisk nedlukning af ventiler - kavitation truende")
            self.metrics.adjust_tillid(-10, "Hans bange for ødelagt rørnetværk")
            self.emit("\n🚨 [AKUT KAVITATION-ALARM - 90 SEKUNDER TIL DESTRUKTION!]:")
            self.emit("Du flår kablerne ud af D-Link switchen uden forudgående forberedelse!")
            self.emit("Ventilerne låser øjeblikkeligt i uheldig position, modtrykket i hovedrøret forsvinder, og Pumpe 2 begynder at KAVITERE voldsomt!")
            self.emit("DU HAR 90 SEKUNDER TIL AT FÅ SCALANCE SWITCHEN MONTERET OG PROFINET MRP-RINGEN GENOPRETTET!")
        else:
            self.emit("Kavitations-alarmen er allerede i gang! Monter SCALANCE switchen hurtigst muligt!")

    def reboot_et200sp_fails(self) -> None:
        self.emit("\n⚠️ [GENSTART FEJLEDE - PROFINET DCP IDENTITETSKAPRET]:")
        self.emit("Du genstarter ET 200SP I/O stationen...")
        self.emit("Men i samme sekund I/O-modulet booter, sender den rogue Raspberry Pi en DCP Set-ramme, der omdøber stationen til 'rogue-io'!")
        self.emit("Hans McDonald råber: 'En genstart løser intet, så længe der sidder en rogue enhed på kablet! Kobl den fra kabelbakken!'")

    def solve_chapter_2(self) -> None:
        if "pi-removed" not in self.flags:
            self.emit("\n⚠️ [PORT SECURITY VIOLATION]:")
            self.emit("Du monterer SCALANCE switchen, men den rogue Raspberry Pi sidder stadig på kabelbakken!")
            self.emit("Switchen detekterer spoofing på Port 4 og lukker porten. Frakobl den rogue Raspberry Pi for at genoprette determinismen!")
            return

        self.cavitation_deadline_active = False
        self.flags.add("chapter-2-done")
        self.chapter = 3
        self.metrics.adjust_sikkerhed(20, "Layer 2 MRP og Port Security aktiveret")
        self.metrics.adjust_compliance(15, "NIS2 netværkssegmentering zone 2")
        self.metrics.adjust_tillid(10, "Hans lettet over Profinet-stabilitet")
        self.record_clue("spor_dcp_storm")
        self.record_clue("spor_mac_oui")
        self.emit("\n🏆 [LØSNING GENNEMFØRT - IEC 62443-3-3 & IEC 62439-2]:")
        self.emit("Siemens SCALANCE XB-200 managed switch monteret på DIN-skinnen med redundant 24V forsyning.")
        self.emit("PROFINET Media Redundancy Protocol (MRP) aktiv! Ventilerne synkroniserer, og Pumpe 2 trykket er stabilt!")
        self.emit("\n[MÅL] NYT MÅL: Kapitel 3 aktiveret! Hans kalder over radioen:")
        self.emit("'Hoved-el-tavlen har fået et chok - S7-1500 PLC'en er gået i STOP-mode!'")

    # -------------------------------------------------------------------------
    # CHAPTER 3 ACTIONS (5-WAY BRANCHING)
    # -------------------------------------------------------------------------
    def take_plc_backup(self) -> None:
        self.flags.add("backup-taken")
        self.forensics.log_usb_backup("S7-1500_CPU_1516F", "9e8a7c2b5d4f1092837465abcdeffedc")
        self.metrics.adjust_compliance(10, "Offline gylden backup sikret")
        self.metrics.adjust_tillid(5, "Hans tilfreds med teknisk forsigtighed")
        self.emit("\n💾 [OFFLINE GYLDEN BACKUP SIKRET - NIS2 ARTIKEL 21.2.c]:")
        self.emit("Du indsætter det krypterede USB-stik og gemmer en fuld offline kopi af:")
        self.emit("  • Hardwarekonfiguration (Protection Level, I/O-adresser)")
        self.emit("  • Sikkerhedsprogram (F-Call OB35) & DB1 fabrikskalibrering")
        self.emit("Hans McDonald klapper i hænderne: 'Fremragende! En god automationsteknolog rører aldrig en PLC uden en frisk backup!'")

    def configure_tia_portal(self) -> None:
        if "backup-taken" not in self.flags:
            self.plc_defect_stop = True
            self.flags.add("plc-defect-stop")
            self.metrics.adjust_drift(-25, "PLC i DEFECTIVE STOP ved mislykket download")
            self.metrics.adjust_tillid(-15, "Hans skuffet over manglende backup")
            self.record_clue("spor_plc_stop_buffer")
            self.emit("\n🚨 [KORRUPT OVERFØRSEL - PLC GÅET I DEFECTIVE STOP]:")
            self.emit("Du forsøgte at overføre TIA-konfigurationen uden en forudgående offline backup!")
            self.emit("Et netværksudfald under overførslen medførte en CRC-fejl, der korrumperede datablok DB1.")
            self.emit("S7-1500 CPU'en blinker gult/rødt med fejlkode 0x4542 (DEFECTIVE STOP).")
            self.emit("Du må genskabe DB1 fra USB-backup ('gendan plc db1') før CPU'en kan køre!")
            return

        self.flags.add("chapter-3-done")
        self.chapter = 4
        self.metrics.adjust_drift(15, "S7-1500 i stabil RUN")
        self.metrics.adjust_sikkerhed(20, "Protection Level 3 og PUT/GET deaktiveret")
        self.metrics.adjust_compliance(15, "TIA Portal sikkerhedskonfiguration opdateret")
        self.metrics.adjust_tillid(10, "Hans stolt over grøn RUN diode")
        self.record_clue("spor_plc_stop_buffer")
        self.emit("\n🏆 [LØSNING GENNEMFØRT - TIA SECURITY HARDENING]:")
        self.emit("  • Adgangsniveau sat til: 'Læse-/skriveadgang beskyttet med adgangskode' (Level 3)")
        self.emit("  • 'Permit access with PUT/GET communication from remote partner' er DEAKTIVERET.")
        self.emit("  • S7comm port 102 afviser nu alle uautoriserede blokskrivninger.")
        self.emit("S7-1500 CPU 1516F skifter til grøn RUN-diode. Sikkerhedsdeterminismen er genoprettet!")
        self.emit("\n[MÅL] NYT MÅL: Kapitel 4 aktiveret! Hans kalder over radioen:")
        self.emit("'Skynd dig til KONTROLRUMMET! Vores SCADA-server lækker data, og der sidder en mistænkelig 4G-router!'")

    def force_cpu_run_fails(self) -> None:
        self.metrics.adjust_drift(-25, "Koldstart fejlede - CPU i DEFECTIVE STOP")
        self.metrics.adjust_tillid(-15, "Hans ryster på hovedet over koldstartsforsøg")
        self.record_clue("spor_plc_stop_buffer")
        self.emit("\n⚠️ [KOLDSTART FEJLEDE - ANGREBSLOOP AKTIVERET]:")
        self.emit("Du drejer nøgleomskifteren på CPU'en fra STOP til RUN uden at have sikret netværket...")
        self.emit("Angriberens loop fanger opstarten og overskriver øjeblikkeligt DB1 med en byte-bomb på port 102!")
        self.emit("CPU'en kastes tilbage i DEFECTIVE STOP! Du kan ikke tvinge en PLC i RUN, hvis netværkssårbarheden ikke er lukket!")

    def block_port_102_passivates_safety(self) -> None:
        self.plc.f_passivated = True
        self.metrics.adjust_drift(-35, "Port 102 blokering kappede PROFIsafe - anlæg nødbremset")
        self.metrics.adjust_tillid(-20, "Hans chokeret over passiveret F-I/O")
        self.emit("\n🚨 [ALARM: F-I/O PASSIVERING & NØDSTOP - EN ISO 13849 / IEC 62061]:")
        self.emit("Du blokerede port 102 totalt i cellens firewall!")
        self.emit("Det stoppede angriberen, men kappede samtidig safety-kommunikationen mellem CPU 1516F og de decentrale ET 200SP I/O-moduler.")
        self.emit("Safety-systemet reagerer som designet: Udløser øjeblikkelig F-I/O passivering og nødstop af hele fabrikken!")
        self.emit("Læresætning: Sikkerheds-I/O kan ikke bare isoleres blindt – safety-conduits skal tillade autoriseret PROFIsafe-trafik!")

    def live_firmware_patch_corrupts(self) -> None:
        self.plc.bootloader_locked = True
        self.metrics.adjust_drift(-30, "Bootloader låst efter MitM firmware corrupt")
        self.metrics.adjust_compliance(-20, "Overtrædelse af supply chain krav")
        self.emit("\n🚨 [SUPPLY CHAIN OVERTRÆDELSE - BOOTLOADER LÅST]:")
        self.emit("Du downloadede en ny firmware-pakke over det inficerede netværk uden at verificere SHA-256 hash-værdien!")
        self.emit("Angriberen udførte et Man-in-the-Middle angreb og injicerede en korrupt bootloader-blok.")
        self.emit("CPU'en nægter at boote og kræver en fabriksnulstilling (NIS2 Artikel 21.2.e overtrædelse).")

    def direct_laptop_arp_poisoned(self) -> None:
        self.metrics.adjust_sikkerhed(-15, "Laptop kompromitteret af ARP-spoofing")
        self.metrics.adjust_drift(-15, "Sikkerhedsrelæ koblede fra")
        self.emit("\n⚠️ [ARP-SPOOFING KAPRET TIA-SESSION]:")
        self.emit("Du tilsluttede din bærbare direkte i CPU'ens port uden at isolere din egen IP.")
        self.emit("Angriberens ARP-spoofing opsnappede din ingeniørsession og forsøgte at injicere et uautoriseret OB-kald.")
        self.emit("Sikkerhedsrelæet koblede fra for at beskytte maskinen!")

    def restore_plc_db1(self) -> None:
        self.plc_defect_stop = False
        self.flags.discard("plc-defect-stop")
        self.flags.add("backup-taken")
        self.metrics.adjust_drift(15, "DB1 genskabt fra autoriseret backup")
        self.metrics.adjust_tillid(10, "Hans lettet over genskabt database")
        self.emit("\n✅ [DB1 GENDANNET FRA SIKKERHEDSKOPI]:")
        self.emit("Du overfører den sunde DB1-blok fra det autoriserede USB-stik. STOP-koden 0x4542 forsvinder!")

    # -------------------------------------------------------------------------
    # CHAPTER 4 ACTIONS (REAL-WORLD OPC UA & IDMZ)
    # -------------------------------------------------------------------------
    def trust_scada_certificate(self) -> None:
        self.flags.add("cert-trusted")
        self.metrics.adjust_compliance(10, "X.509 certifikat flyttet til Trusted")
        self.metrics.adjust_tillid(5, "SCADA forbinder sikkert")
        self.emit("\n📜 [X.509 CERTIFIKAT GODKENDT]:")
        self.emit("I OPC UA certifikat-truststoren flytter du 'WinCC_SCADA_Client_Cert_2026.der' fra mappen 'Rejected' til 'Trusted'.")
        self.emit("Serveren accepterer nu SCADA-klientens kryptografiske identitet!")
        self.check_chapter_4_completion()

    def enable_opc_crypto(self) -> None:
        self.flags.add("opc-crypto-active")
        self.metrics.adjust_sikkerhed(15, "Basic256Sha256 kryptering aktiveret")
        self.record_clue("spor_opc_leak")
        self.emit("\n🔒 [OPC UA KRYPTERING AKTIVERET]:")
        self.emit("SecurityPolicy sat til 'Basic256Sha256' og MessageSecurityMode sat til 'SignAndEncrypt'.")
        self.emit("Al kommunikation på port 4840 er nu beskyttet mod aflytning og manipulation jf. NIS2 Artikel 21.2.h!")
        self.check_chapter_4_completion()

    def disable_opc_anonymous(self) -> None:
        self.flags.add("anon-disabled")
        self.metrics.adjust_sikkerhed(10, "Anonymous token deaktiveret i OPC UA")
        self.record_clue("spor_opc_leak")
        self.emit("\n🚫 [ANONYM ADGANG DEAKTIVERET]:")
        self.emit("Anonymous UserTokenType er fjernet fra endpointet. Al adgang kræver nu X.509 certifikat eller stærke RBAC-brugeroplysninger.")
        self.check_chapter_4_completion()

    def disconnect_4g_router(self) -> None:
        self.flags.add("router-disconnected")
        self.metrics.adjust_sikkerhed(20, "Uautoriseret 4G router afbrudt")
        self.metrics.adjust_compliance(15, "Fysisk adgangskontrol og IDMZ genoprettet")
        self.record_clue("spor_4g_dongle")
        self.emit("\n🔌 [UAUTORISERET 4G-ROUTER FRAKOBLET & KONFISKERET]:")
        self.emit("Du trækker strømstikket til Teltonika RUT950 4G-routeren bag SCADA-racket og fjerner WAN-kablet.")
        self.emit("Den uautoriserede cellulære bagdør til internettet er lukket! IDMZ (Purdue Level 3.5) er genetableret.")
        self.check_chapter_4_completion()

    def check_chapter_4_completion(self) -> None:
        reqs = {"cert-trusted", "opc-crypto-active", "anon-disabled", "router-disconnected"}
        if reqs.issubset(self.flags):
            self.flags.add("chapter-4-done")
            self.flags.add("opc-hardened")
            self.chapter = 5
            self.metrics.adjust_tillid(10, "Hans melder anlæg klar til revision")
            self.emit("\n🏆 [LØSNING GENNEMFØRT - NIS2 ARTIKEL 21 & IEC 62443-3-2 IDMZ]:")
            self.emit("OPC UA serveren kører nu med fuld kryptografisk signering, kryptering og certifikatgodkendelse.")
            self.emit("Alle bagdøre er lukkede, og anlæggets zoner er isolerede og deterministiske!")
            self.emit("\n🎉 [SEJR] SAMTLIGE ANGREB ER AFVÆRGET! Kirsten fra Cybersikkerhedstilsynet er ankommet ved Hovedindgangen.")
            self.emit("Gå til Hovedindgangen og fremlæg dokumentationen for at bestå den officielle NIS2-audit!")

    def block_port_4840_blindly(self) -> None:
        self.scada_log_interrupted = True
        self.emit("\n⚠️ [MILJØLOGNING AFBRUDT]:")
        self.emit("Du blokerede port 4840 blindt i firewallen. Lovpligtig miljørapportering til Miljøstyrelsen fejler!")

    def restore_scada_logging(self) -> None:
        self.scada_log_interrupted = False
        self.emit("\n✅ [PORT 4840 GENÅBNET MED CERTIFIKATKONTROL]: Lovpligtig miljølogning genoptaget.")

    # -------------------------------------------------------------------------
    # INSPECTIONS & INTERACTIONS
    # -------------------------------------------------------------------------
    def inspect(self, target: str) -> None:
        norm = target.lower().strip()

        # Secret cable tray reveal in Ventil-øen
        if "kabelbakke" in norm or "sort boks" in norm or "sort kasse" in norm or "bakke" in norm:
            if self.room == "ventil-oen":
                r_obj = ALL_ROOMS["ventil-oen"]
                if hasattr(r_obj, "reveal_pi"):
                    r_obj.reveal_pi(self)
                self.rogue_pi.reveal()
                self.flags.add("pi-revealed")
                self.record_clue("spor_sort_boks")
                self.emit("\n🔍 [FYSISK EFTERFORSKNING - ROGUE HARDWARE FUNDET!]:")
                self.emit("Du lyser op under kabelbakken bag Festo-ventilerne med din lommelygte...")
                self.emit("Der sidder en sort boks tapet fast med gaffa-tape! Et blåt Cat6-kabel er ført direkte ind i D-Link switchen.")
                self.emit("Det er en ROGUE RASPBERRY PI 4 med en aktiv PoE-strømforsyning! Den blinker hektisk med grønne netværksdioder.")
                self.emit("Du har fundet angriberens fysiske implantat!")
                return

        if "skinne" in norm or "din-skinne" in norm or "ts35" in norm:
            if self.room == "pumpehuset":
                self.open_vfd_workbench()
                return
            elif self.room == "ventil-oen":
                self.open_switch_workbench()
                return
            self.emit("En standard 35mm DIN-skinne (EN 60715 TS35) i industrielt stål til montering af automationsudstyr.")
            return

        if "pumpe" in norm or "manometer" in norm:
            self.record_clue("spor_manometer_rystelser")
            self.emit(self.vfd.get_telemetry(self))
            return
        if "frekvens" in norm or "vfd" in norm:
            self.emit(self.vfd.description)
            self.emit(self.vfd.get_telemetry(self))
            if "chapter-1-done" not in self.flags:
                self.emit("\n💡 På DIN-skinnen foran frekvensomformeren kan der monteres en SCALANCE S615 DPI-firewall ('firewall workbench' eller klik på DIN-skinnen på skærmen).")
            return
        if "switch" in norm:
            self.emit(self.switch.description)
            self.emit(self.switch.get_telemetry(self))
            return
        if "s7" in norm or "plc" in norm:
            self.record_clue("spor_plc_stop_buffer")
            self.emit(self.plc.description)
            self.emit(self.plc.get_telemetry(self))
            return
        if "usb" in norm or "backup" in norm:
            self.record_clue("spor_usb_backup")
            self.emit("Du undersøger USB-stikket: 'NordicH2O_Rev12_LARS.zap16'. Indeholder Siemens TIA V16 projekt.")
            return
        if "opc" in norm:
            self.record_clue("spor_opc_leak")
            self.emit(self.opcua.description)
            self.emit(self.opcua.get_telemetry(self))
            return
        if "router" in norm or "4g" in norm:
            self.record_clue("spor_4g_dongle")
            self.emit("Teltonika RUT950 4G-router. Den er tilsluttet en ekstern mobilmast og har en aktiv VPN-tunnel til udlandet.")
            return
        if "scada" in norm or "wincc" in norm or "arbejdsstation" in norm:
            self.record_clue("spor_kim_nattevagt")
            self.emit(
                "WinCC SCADA PC: Hændelsesloggen viser, at operatørkonto 'kdahl' (Kim Dahl) "
                "loggede ind kl. 03:14 natten til onsdag fra en intern subnet-IP (10.144.20.1). "
                "I sessionsloggen ses en routing-kommando, der peger mod Teltonika 4G-routerens IP!"
            )
            return
        if "ventil" in norm or "festo" in norm:
            self.record_clue("spor_dcp_storm")
            self.emit(
                "Festo ventil-ø og Siemens ET 200SP I/O moduler: Ventilerne cykler kaotisk. "
                "En statusdiode blinker 'BF' (Bus Fault), fordi PROFINET DCP pakker overskriver enhedens stationsnavn."
            )
            return

        self.emit(f"Du undersøger {target}. Alt virker som forventet for denne komponent.")

    def talk_to(self, character: str) -> None:
        norm = character.lower().strip()
        if "hans" in norm:
            self.record_clue("spor_morten_rapport")
            greeting = self.hans.get_greeting(self)
            self.emit(f"\n{greeting}")
            if random.random() < 0.4:
                self.emit(f"\n{self.hans.get_anecdote()}")
        elif "kirsten" in norm or "revisor" in norm or "tilsyn" in norm:
            self.record_clue("spor_kim_nattevagt")
            if self.chapter == 5:
                self.complete_audit()
            else:
                self.emit(self.kirsten.get_interim_audit(self))
        else:
            self.emit(f"Der er ingen ved navn '{character}' her.")

    def submit_early_warning(self) -> None:
        success, msg = self.incident.submit_early_warning(self.simulated_day, self.simulated_hour, "Sabotage af procespumper og feldbus.")
        if success:
            self.flags.add("early-warning-reported")
            self.metrics.adjust_compliance(20, "NIS2 24-timers Early Warning indsendt rettidigt")
            self.metrics.adjust_tillid(10, "Ledelsen anerkender rettidig indberetning")
        else:
            self.metrics.adjust_compliance(-10, "Frist for 24-timers Early Warning overskredet")
        self.emit(f"\n{msg}")

    def present_case_investigation(self) -> None:
        if self.chapter < 5:
            self.emit(
                f"\n⚠️ [EFTERFORSKNING UNDERVEJS - KAPITEL {self.chapter}/5]:\n"
                "Du kan ikke afslutte og fremlægge efterforskningen endnu. "
                "Du skal først afværge de akutte angreb og sikre alle anlægszoner!"
            )
            return

        prime_id = self.investigation.prime_suspect_id
        if not prime_id:
            self.emit(
                "\n⚠️ [SAGSTAVLE MANGLER HOVEDMISTÆNKT]:\n"
                "Kirsten og Hans ser på dig: 'Hvem mener du står bag denne sabotage mod drikkevandsforsyningen?'\n"
                "Du skal fastsætte din hovedmistænkte før Tilsynet kan vurdere sagen.\n"
                "Brug 'anklag <id>' med en af kandidaterne fra sagstavlen:\n"
                "  • 'anklag lars_ex_tekniker'  (Lars Kofoed - Fratrådt automationstekniker)\n"
                "  • 'anklag kim_operatoer'     (Kim Dahl - Intern procesoperatør på natholdet)\n"
                "  • 'anklag morten_pumper'     (Morten Vestergaard - Ekstern pumpe-ingeniør)\n"
                "  • 'anklag apt_shadowh2o'     (ShadowH2O - Cyberkriminelt APT-syndikat)\n"
                "  • 'anklag systemisk_fejl'    (Systemisk fejl & akkumuleret teknisk gæld)\n"
                "Skriv derefter 'fremlæg sagstavle' igen for at konfrontere Tilsynet!"
            )
            return

        suspect = self.investigation.get_suspect(prime_id)
        discovered_count = len(self.investigation.get_discovered_clues())
        self.flags.add("case-presented")

        self.emit("\n" + "=" * 80)
        self.emit("   🕵️  DEN STORE KONFRONTATION – FREMLÆGGELSE FORAN TILSYNET & DRIFTEN    ")
        self.emit("=" * 80)
        self.emit(f"Du træder frem foran Kirsten fra Cybersikkerhedstilsynet og driftstekniker Hans McDonald.")
        self.emit(f"På sagstavlen er der dokumenteret {discovered_count} ud af 11 mulige tekniske og fysiske spor.")
        self.emit(f"\nDu peger på din hovedmistænkte: {suspect.name if suspect else prime_id}!")
        if suspect:
            self.emit(f"Rolle: {suspect.role}")
            self.emit(f"Arbejdshypotese: \"{suspect.theory}\"")

        if prime_id == "lars_ex_tekniker":
            self.flags.add("case-solved-lars")
            self.metrics.adjust_compliance(15, "Korrekt identifikation af gerningsmand")
            self.metrics.adjust_tillid(10, "Hans lettet over sagens opklaring")
            self.emit("\nHans spærrer øjnene op og tager sig til hovedet:")
            self.emit("\"Lars... Vor herre bevares. Det giver jo fuldkommen mening!")
            self.emit("Lars vidste præcis hvordan datablok DB1 var bygget op i S7-1500 PLC'en, for det var ham selv, der lavede den i TIA Portal!")
            self.emit("Og det efterladte USB-stik mærket 'LARS - TIA V16 BACKUP'... Han efterlod sine ubeskyttede projekter uden kodeord!")
            self.emit("Og den Raspberry Pi i kabelbakken... Lars snakkede altid om, at 'Siemens switches er spild af penge, en Pi kan det samme'.")
            self.emit("Han har haft en gammel nøglebrik og sneg sig ind i produktionshallen efter fyringen!\"")

            self.emit("\nKirsten nikker med et sjældent, anerkendende smil og retter på sine briller:")
            self.emit("\"Vores telemetri-analyse af Teltonika 4G-routerens VPN-tunnel bekræfter din konklusion.")
            self.emit("IP-adressen i tunnelens endepunkt peger direkte på en lejet cloud-VPS registreret til 'Lars Kofoed Automationsservice'.")
            self.emit("Lars udnyttede operatøren Kims naivitet – han overtalte Kim til at sætte 4G-routeren op under påskud af,")
            self.emit("at det var en uskyldig 'Wi-Fi forstærker', så Kim kunne streame fodbold om natten.")
            self.emit("Lars forsøgte bevidst at fremprovokere et kavitetskollaps og et PLC-nedbrud lige op til vores ankomst for at hævne sin fyring.")
            self.emit("Sagen er hermed overdraget til Rigspolitiets Nationale Cyber Crime Center (NC3) under Straffelovens § 193.")
            self.emit("Fremragende opklaringsarbejde, konsulent!\"")

        elif prime_id == "kim_operatoer":
            self.emit("\nHans ryster på hovedet:")
            self.emit("\"Kim?! Jamen Kim er jo bare en doven operatør på natholdet! Ja, han satte 4G-modemet i stikket bag racket,")
            self.emit("fordi han ville se Champions League fra sofaen. Men Kim kan knap nok stave til Python!")
            self.emit("Han var slet ikke i stand til at konstruere Scapy Modbus exploits eller DCP spoofing.\"")
            self.emit("\nKirsten tilføjer: 'Korrekt. Kim handlede i grov strid med anlæggets fysiske sikkerhedspolitik (NIS2 Art. 21.2.i),")
            self.emit("men han var blot en uvidende døråbner for den virkelige bagmand (den fyrede tekniker Lars Kofoed).")
            self.emit("Kim modtager en disciplinær advarsel, men han er ikke hovedmanden bag angrebet.'")

        elif prime_id == "morten_pumper":
            self.emit("\nHans udbryder forfærdet:")
            self.emit("\"Morten?! Nej hør nu, Mortens firma Hydropump har serviceret vores pumper i 15 år!")
            self.emit("Netværksloggen viste ganske rigtigt Modbus-pakker fra 192.168.1.50, men det var spoofet fra den rogue Raspberry Pi")
            self.emit("for at kaste mistanken over på en uskyldig ekstern leverandør!\"")
            self.emit("\nKirsten: 'Vi har kontrolleret Mortens alibi. Han sad i et kundemøde i Kolding på gerningstidspunktet.")
            self.emit("Du hoppede i gerningsmandens vildspor, konsulent.'")

        elif prime_id == "apt_shadowh2o":
            self.emit("\nKirsten trækker på smilebåndet med en tør latter:")
            self.emit("\"ShadowH2O? Et geopolitisk cybersyndikat? Du har set for mange actionfilm, konsulent.")
            self.emit("Dette angreb indeholdt ingen 'Zero-days' eller avancerede statsstøttede cybervåben.")
            self.emit("Det krævede blot standardkodeord, ubeskyttede PUT/GET indstillinger og en billig Raspberry Pi tapet med gaffa.")
            self.emit("Dette var en forsmået tidligere medarbejder – ikke en fremmed magt.\"")

        elif prime_id == "systemisk_fejl":
            self.emit("\nHans sukker:")
            self.emit("\"Vores tekniske gæld var enorm, ja. Men gaffatape i en kabelbakke og en hemmelig 4G-router i et server-rack")
            self.emit("opstår ikke af sig selv ved et uheld! Dette var overlagt, målrettet sabotage.\"")
            self.emit("\nKirsten: 'Bekvem forklaring, men de fysiske beviser dokumenterer en overlagt forbrydelse.'")

        self.emit("\n" + "-" * 80)
        self.emit("📋 Sagstavlen er nu fremlagt! Kirsten er klar til at udstede Tilsynets officielle revision.")
        self.emit("Tast '2' eller skriv 'revisor' for at modtage det endelige NIS2 audit-dekret!")
        self.emit("-" * 80)

    def export_audit_report(self) -> None:
        flaws = self.collect_flaws()
        passed, score, remarks, base_report = self.incident.evaluate_compliance(
            self.player.name, self.flags, flaws, self.forensics.pi_handling_state
        )
        prime_id = self.investigation.prime_suspect_id
        prime_name = self.investigation.get_suspect(prime_id).name if prime_id and self.investigation.get_suspect(prime_id) else "Ingen anklaget"

        # Build extensive Markdown audit report
        discovered_clues = self.investigation.get_discovered_clues()
        evidence_entries = self.forensics.evidence_log

        lines = [
            f"# NIS2 & IEC 62443 REVISIONSRAPPORT",
            f"**Virksomhed:** Nordic H2O Utility A/S (Drikkevandsforsyning - Væsentlig Enhed)",
            f"**Lead Cybersikkerhedskonsulent:** {self.player.name} ({getattr(self.player, 'education', 'Automation & IT-Sikkerhed')})",
            f"**Revisionsorgan:** Miljø- og Cybersikkerhedstilsynet (Auditor Kirsten)",
            f"**Tilsynsdato:** Dag 5 (Afsluttende hændelsesrevision)",
            f"**Overordnet Resultat:** {'BESTÅET (Fuld 3-årig driftstilladelse)' if passed else 'DUMPET (Driftstilladelse inddraget)'}",
            f"**Samlet Compliance Score:** {score} / 100 point (Krav: min. 80 point)",
            "",
            "## 1. Hovedmetrikker for Anlæg og Drift",
            f"- **🔧 Drift:** [{self.investigation._render_bar(self.metrics.drift)}] {self.metrics.drift}% (Uptime & hydraulisk stabilitet)",
            f"- **🛡️ Sikkerhed:** [{self.investigation._render_bar(self.metrics.sikkerhed)}] {self.metrics.sikkerhed}% (IEC 62443 zoner & conduits)",
            f"- **📜 Compliance:** [{self.investigation._render_bar(self.metrics.compliance)}] {self.metrics.compliance}% (NIS2 Artikel 21 & 23)",
            f"- **🤝 Tillid:** [{self.investigation._render_bar(self.metrics.tillid)}] {self.metrics.tillid}% (Samarbejde med driftspersonale)",
            "",
            "## 2. Efterforskning & Sagstavle (Trusselsvurdering)",
            f"- **Udpeget gerningsmand:** {prime_name}",
            f"- **Gerningsmandskonklusion:** {'KORREKT (Lars Kofoed - Sag overdraget til Rigspolitiet NC3)' if prime_id == 'lars_ex_tekniker' else 'Uafklaret eller vildledt'}",
            f"- **Dokumenterede spor:** {len(discovered_clues)} af 11 spor opdaget",
            "",
            "### Opdagede tekniske og fysiske spor:",
        ]

        for c in discovered_clues:
            lines.append(f"- **[{c.id}]** *{c.title}* ({c.category} - {c.discovery_room}): {c.analysis}")

        lines.extend([
            "",
            "## 3. Forensisk Evidens & Chain of Custody (NIS2 Artikel 21.2.b)",
            f"- **Rogue Pi Tilstand:** {self.forensics.pi_handling_state.upper()}",
        ])

        for ev in evidence_entries:
            lines.append(f"- **Bevis #{ev.item_id}:** {ev.description} | SHA-256: `{ev.sha256}` | Plomberingsnr: `{ev.seal_number}`")

        lines.extend([
            "",
            "## 4. Gennemgang af NIS2 Artikel 21 Risikostyringsforanstaltninger",
        ])
        for r in remarks:
            icon = "✅" if not any(w in r for w in {"Mangler", "Manglende", "KRITISK", "FEJL", "fejl", "står", "blindet"}) else "❌"
            lines.append(f"- {icon} {r}")

        lines.extend([
            "",
            "## 5. UCL Faglige Læringsmål og Studiekonklusion",
            "Denne rapport dokumenterer kompetencer inden for:",
            "- **Purdue Modellen & IEC 62443:** Etablering af zoner og conduits mellem Level 1 (Feltbus) og Level 3.5 (IDMZ).",
            "- **Modbus TCP Sikkerhed:** L7 Deep Packet Inspection (DPI) på SCALANCE S615 (Tillad FC 03 læsning, afvis FC 06/16 skrivning).",
            "- **PROFINET Determinisme & MRP:** Eliminering af rogue hardware og redundans med SCALANCE XB-200.",
            "- **Siemens S7-1500 Sikkerhedshærdning:** Frakobling af ubeskyttet PUT/GET og etablering af Protection Level 3.",
            "- **OPC UA PKI & Kryptografi:** X.509 certifikatvalidering, Basic256Sha256 SignAndEncrypt og eliminering af anonym adgang.",
            "- **NIS2 Compliance:** 24-timers Early Warning (Art. 23) og retsmedicinsk beviskæde i Faraday-pose (Art. 21.2.b).",
            "",
            "---",
            "*Genereret automatisk af The Curse of Insecure Packets - UCL Erhvervsakademi og Professionshøjskole.*"
        ])

        full_report_text = "\n".join(lines)
        try:
            with open("NIS2_Audit_Rapport_NordicH2O.md", "w", encoding="utf-8") as f:
                f.write(full_report_text)
            self.emit("\n📄 [NIS2 REVISIONSRAPPORT EKSPORTERET]:")
            self.emit("Rapporten er gemt i projektmappen som 'NIS2_Audit_Rapport_NordicH2O.md'.")
            self.emit("De studerende kan benytte denne rapport som bilag til deres UCL-studieportfolio!")
        except Exception as e:
            self.emit(f"Fejl under eksport af rapport: {e}")

    def collect_flaws(self) -> list[str]:
        flaws = []
        if self.breaker_tripped:
            flaws.append("Sikkerhedsrelæ K1 er udløst; Pumpe 2 står uden spænding.")
        if self.scada_blind:
            flaws.append("SCADA er blindet af grov Layer 3 portblokering frem for Deep Packet Inspection.")
        if self.plc_defect_stop:
            flaws.append("S7-1500 PLC står i DEFECTIVE STOP med korrumperet DB1.")
        if self.scada_log_interrupted:
            flaws.append("Lovpligtig miljørapportering på port 4840 er afbrudt.")
        if "router-disconnected" not in self.flags:
            flaws.append("Uautoriseret 4G-router efterladt aktiv i IDMZ.")
        return flaws

    def complete_audit(self) -> None:
        self.emit(f"\n{self.kirsten.get_audit_intro(self.player.name)}")
        flaws = self.collect_flaws()
        passed, score, remarks, _report = self.incident.evaluate_compliance(
            self.player.name, self.flags, flaws, self.forensics.pi_handling_state
        )
        prime_id = self.investigation.prime_suspect_id

        # Kirsten's four-dimensional decree
        verdict = self.kirsten.format_final_verdict(
            passed, score, self.metrics, remarks, prime_id
        )
        self.emit(verdict)

        # Hans debriefing
        hans_reaction = self.hans.get_final_verdict_reaction(self.metrics, prime_id)
        self.emit(hans_reaction)

        # Export full official report
        self.export_audit_report()

        if passed:
            self.emit("\n🎉 [SPILLET ER GENNEMFØRT!] Tillykke! Du har reddet Nordic H2O Utility og bestået NIS2-auditten!")
            self.emit("En fuld revisionsrapport 'NIS2_Audit_Rapport_NordicH2O.md' er genereret til din UCL-studieportfolio.")
            self.emit("\n💡 Tast 'hovedmenu' eller klik '🏠 Menu' for at vende tilbage til Hovedmenuen og starte et nyt spil.")
            self.running = False
        else:
            self.emit("\n⚠️ [AUDIT IKKE BESTÅET] Ret fejlene og genforsøg auditten med 'revisor'.")

    def help(self) -> None:
        self.emit("\n=== TILGÆNGELIGE KOMMANDOER ===")
        self.emit("  Tast et tal [1-6] fra valgmenuen for at udføre en handling direkte.")
        self.emit("  GÅ TIL <zone>             Skift rum (indgangen, pumpehuset, ventil-øen, el-tavlen, kontrolrummet)")
        self.emit("  UNDERSØG <komponent>      Inspicér maskine, kabelbakke eller enhed")
        self.emit("  TAL MED HANS              Få praktisk vejledning og erfaringer fra driftsteknikeren")
        self.emit("  SPØRG HANS OM <emne>      Forhør Hans om mistænkte (morten, lars, kim, 4g, stuxnet, modbus)")
        self.emit("  RING TIL KIRSTEN          Få Tilsynets foreløbige NIS2 risikovurdering undervejs i ugen")
        self.emit("  SPØRG KIRSTEN OM <emne>   Spørg Tilsynet om lovkrav (artikel 21, artikel 23, beviser, bøder)")
        self.emit("  SAGSTAVLE                 Vis efterforskningstavle, mistænkte og de 4 anlægsmetrikker")
        self.emit("  SPOR                      Vis opdagede tekniske og fysiske spor")
        self.emit("  ANALYSER SPOR <id>        Udfør retsmedicinsk/teknisk dybdeanalyse af et fundet spor")
        self.emit("  MISTÆNKTE                 Vis liste over mistænkte personer og arbejdshypoteser")
        self.emit("  ANKLAG <id>               Udnævn din primære mistænkte på sagstavlen")
        self.emit("  METRIKKER                 Vis anlæggets status for Drift, Sikkerhed, Compliance og Tillid")
        self.emit("  TSHARK                    Start netværksanalyse (f.eks. 'tshark -Y \"modbus\"' eller 'man tshark')")
        self.emit("  INDBERET HÆNDELSE         Indsend lovpligtig NIS2 24-timers Early Warning")
        self.emit("  VIS EVIDENS               Gennemse digital Chain of Custody journal")
        self.emit("  STATUS                    Vis aktuel arbejdsdag, tidsfrist og kapitelmål")
        self.emit("  RYGSÆK                    Vis inventar og værktøjer")
        self.emit("  GEM SPIL                  Gem din aktuelle spiltilstand til disk (saves/quicksave.json)")
        self.emit("  HENT SPIL                 Hent og genoptag et gemt spil")
        self.emit("  HOVEDMENU                 Gå tilbage til startskærmen / hovedmenuen")

    def tour(self) -> None:
        self.emit("\nHans McDonald tager dig med på en teknisk rundtur gennem anlæggets Purdue-zoner:")
        for lvl, p in sorted(PURDUE_LEVELS.items()):
            self.emit(f"  • [{p.name}]: {p.description} (Krav: {p.iec_sl_target})")

    def status(self) -> None:
        r = self.get_current_room()
        self.emit(f"\n[STATUS] KAPITEL {self.chapter}/5 | Zone: {r.title} ({r.purdue_level})")
        self.emit(f"Mål: {OBJECTIVES.get(self.chapter, 'Gennemfør audit')}")
        self.emit(f"Arbejdsdag {self.simulated_day}/5, time {self.simulated_hour}/8 | Tid til audit: {self.time_display}")
        self.emit(f"Anlægstilstand: 🔧 Drift: {self.metrics.drift}% | 🛡️ Sikkerhed: {self.metrics.sikkerhed}% | 📜 Compliance: {self.metrics.compliance}% | 🤝 Tillid: {self.metrics.tillid}%")
        if self.cavitation_deadline_active:
            self.emit(f"🚨 AKUT KAVITATION-ALARM: {self.cavitation_time_display} tilbage før pumperne ødelægges!")
        elif self.pump_deadline_active:
            self.emit(f"⚠️ AKUT PUMPE 2 ALARM: {self.pump_time_display} tilbage før sprængning!")
        else:
            self.emit("✅ Ingen overhængende akutte procesalarmer.")

    def call_tech_support(self) -> None:
        if self.help_calls >= self.max_help_calls:
            self.emit("Tech Support svarer ikke. Telefonsvareren siger: 'Brug din faglige viden og NIS2 vejledningen!'")
            return
        self.help_calls += 1
        hints = {
            1: "Tech Support: 'I Pumpehuset skal du isolere frekvensomformeren med en SCALANCE S615 router og aktivere Modbus Deep Packet Inspection (DPI)!'",
            2: "Tech Support: 'På Ventil-øen skal du undersøge kabelbakken for fremmed hardware og montere en SCALANCE switch med MRP-ringstyring!'",
            3: "Tech Support: 'I Hoved-el-tavlen må du aldrig røre en PLC uden offline backup! Deaktivér PUT/GET i TIA Portal for at sikre mod S7comm overstyring.'",
            4: "Tech Support: 'I Kontrolrummet skal du flytte WinCC klientens certifikat fra Rejected til Trusted, slå Anonymous fra og koble 4G-routeren fra!'",
            5: "Tech Support: 'Gå ud til Revisor Kirsten ved Hovedindgangen og fremlæg dokumentationen!'",
        }
        self.emit(f"\n[TECH SUPPORT ({self.help_calls}/{self.max_help_calls})]:\n{hints.get(self.chapter, 'Følg NIS2 retningslinjerne!')}")
