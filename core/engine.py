"""Core game engine coordinating rooms, devices, forensics, NIS2 incidents & gameplay logic."""

from __future__ import annotations

import random
import re
import time
from collections.abc import Callable
from typing import Any

from core.forensics import ForensicsManager
from core.incident import IncidentManager
from core.purdue import PURDUE_LEVELS
from core.terminal_engine import AutocompleteHelper, WiresharkSniffer
from devices import OpcUaDevice, PLCDevice, RoguePiDevice, SwitchDevice, VFDDevice
from dialogues import HansDialogue, KirstenDialogue
from models import OBJECTIVES, Player
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
        self.running = False

    def expire_pump_timer(self) -> None:
        self.emit("\n💥 [KATASTROFE] PUMPE 2 HAR OVERSKREDET SPRÆNGNINGSGRÆNSEN (150 BAR)!")
        self.emit("Rørene sprang, pumpehuset er oversvømmet, og nødstop er udløst på hele fabrikken.")
        self.emit("Du nåede ikke at afværge hændelsen i tide. Missionen er tabt.")
        self.running = False

    def expire_cavitation_timer(self) -> None:
        self.emit("\n💥 [KATASTROFE] PUMPE 2'S PUMPEHJUL ER BLEVET SMADRET AF KAVITATION!")
        self.emit("Da modtrykket forsvandt under det ukontrollerede switch-udfald, opstod der voldsomme dampboble-implosioner.")
        self.emit("Vibrationssensoren udløste total nødnedlukning af vandværket. Tilsynet inddrager driftstilladelsen. Missionen er tabt.")
        self.running = False

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
        if not self.check_timers():
            return
        raw = command.strip()
        if not raw:
            if self.chapter > 0:
                self.emit(self.format_choices_text())
            return
        normalized = re.sub(r"\s+", " ", raw.lower())

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
        elif normalized in {"indberet hændelse", "early warning", "indberet", "anmeld hændelse"}:
            self.submit_early_warning()
        elif normalized in {"eksporter rapport", "eksport rapport", "gem rapport"}:
            self.export_audit_report()
        elif normalized.startswith("tshark") or normalized in {"man tshark", "cheat tshark", "tshark cheatsheet", "tshark help"}:
            self.flags.add("wireshark-open")
            self.emit(self.sniffer.execute_tshark_command(raw, self.room, engine=self))
        elif normalized.startswith("wireshark filter "):
            filt = normalized.removeprefix("wireshark filter ").strip()
            self.flags.add("wireshark-open")
            self.emit(f"💡 [TSHARK INFO]: I terminalen anvendes 'tshark -Y \"{filt}\"'. Kører filter for dig:")
            self.emit(self.sniffer.execute_tshark_command(f"tshark -Y \"{filt}\"", self.room, engine=self))
        elif normalized.startswith("wireshark detaljer "):
            pkt = normalized.removeprefix("wireshark detaljer ").strip()
            self.flags.add("wireshark-open")
            self.emit("💡 [TSHARK INFO]: I terminalen anvendes 'tshark -V'. Kører protokol-dissekering:")
            self.emit(self.sniffer.execute_tshark_command("tshark -V", self.room, engine=self))
        elif normalized in {"åbn wireshark", "wireshark", "start wireshark", "sniffer"}:
            self.flags.add("wireshark-open")
            self.emit(f"💡 [TSHARK INFO]: Kører tshark på '{self.room}_vlan'... (Skriv 'man tshark' for filtre som f.eks. -Y \"modbus\")")
            self.emit(self.sniffer.execute_tshark_command("tshark", self.room, engine=self))
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

    def solve_chapter_1(self) -> None:
        if self.breaker_tripped:
            self.emit("⚠️ Frekvensomformeren er strømløs på grund af udløst K1-relæ! Nulstil K1 i El-tavlen først.")
            return
        if self.wrong_cabling:
            self.emit("⚠️ Kan ikke aktivere Modbus DPI: Kablerne er krydset forkert! VFD sidder i WAN-porten i stedet for LAN.")
            self.emit("Byt om på kablerne ('kobl kabler til scalance' eller valg 2), så frekvensomformeren sidder i LAN P1!")
            return
        self.vfd_mounted = True
        self.vfd_cabled = True
        self.wrong_cabling = False
        self.active_workbench = None
        self.scada_blind = False
        self.flags.discard("scada-blind")
        self.pump_deadline_active = False
        self.flags.add("chapter-1-done")
        self.chapter = 2
        self.emit("\n🏆 [LØSNING GENNEMFØRT - IEC 62443-3-2 ZONER & CONDUITS]:")
        self.emit("SCALANCE S615 sikkerhedsrouteren er monteret på DIN-skinnen og kablerne er verificeret.")
        self.emit("Modbus DPI-regelsæt aktivt: Tillader FC 03 (Læsning fra SCADA), men dropper FC 06 (Uautoriseret skrivning).")
        self.emit("Pumpe 2's omdrejningstal falder til rolige 450 RPM. Manometeret stabiliserer sig på 42.0 Bar!")
        self.emit("\n[MÅL] NYT MÅL: Kapitel 2 aktiveret! Hans kalder over radioen:")
        self.emit("'Skynd dig til VENTIL-ØEN! Ventilerne danser rundt i et PROFINET kaos!'")

    # -------------------------------------------------------------------------
    # CHAPTER 2 ACTIONS
    # -------------------------------------------------------------------------
    def handle_pi_removal(self, method: str) -> None:
        success, message = self.forensics.secure_rogue_pi(method)
        self.emit(f"\n{message}")
        self.flags.add("pi-removed")
        self.rogue_pi.disconnected = True
        self.rogue_pi.disposition = self.forensics.pi_handling_state
        self.emit("\nDu kan nu udskifte den gamle D-Link switch med den industrielle SCALANCE XB-200 med MRP-ring!")

    def unplug_switch_abruptly(self) -> None:
        if "chapter-2-done" in self.flags:
            self.emit("SCALANCE switchen er allerede monteret og kører med MRP-ring.")
            return
        if not self.cavitation_deadline_active:
            self.cavitation_deadline_started_at = time.monotonic()
            self.cavitation_deadline_active = True
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
        self.emit("\n💾 [OFFLINE GYLDEN BACKUP SIKRET - NIS2 ARTIKEL 21.2.c]:")
        self.emit("Du indsætter det krypterede USB-stik og gemmer en fuld offline kopi af:")
        self.emit("  • Hardwarekonfiguration (Protection Level, I/O-adresser)")
        self.emit("  • Sikkerhedsprogram (F-Call OB35) & DB1 fabrikskalibrering")
        self.emit("Hans McDonald klapper i hænderne: 'Fremragende! En god automationsteknolog rører aldrig en PLC uden en frisk backup!'")

    def configure_tia_portal(self) -> None:
        if "backup-taken" not in self.flags:
            self.plc_defect_stop = True
            self.flags.add("plc-defect-stop")
            self.emit("\n🚨 [KORRUPT OVERFØRSEL - PLC GÅET I DEFECTIVE STOP]:")
            self.emit("Du forsøgte at overføre TIA-konfigurationen uden en forudgående offline backup!")
            self.emit("Et netværksudfald under overførslen medførte en CRC-fejl, der korrumperede datablok DB1.")
            self.emit("S7-1500 CPU'en blinker gult/rødt med fejlkode 0x4542 (DEFECTIVE STOP).")
            self.emit("Du må genskabe DB1 fra USB-backup ('gendan plc db1') før CPU'en kan køre!")
            return

        self.flags.add("chapter-3-done")
        self.chapter = 4
        self.emit("\n🏆 [LØSNING GENNEMFØRT - TIA SECURITY HARDENING]:")
        self.emit("  • Adgangsniveau sat til: 'Læse-/skriveadgang beskyttet med adgangskode' (Level 3)")
        self.emit("  • 'Permit access with PUT/GET communication from remote partner' er DEAKTIVERET.")
        self.emit("  • S7comm port 102 afviser nu alle uautoriserede blokskrivninger.")
        self.emit("S7-1500 CPU 1516F skifter til grøn RUN-diode. Sikkerhedsdeterminismen er genoprettet!")
        self.emit("\n[MÅL] NYT MÅL: Kapitel 4 aktiveret! Hans kalder over radioen:")
        self.emit("'Skynd dig til KONTROLRUMMET! Vores SCADA-server lækker data, og der sidder en mistænkelig 4G-router!'")

    def force_cpu_run_fails(self) -> None:
        self.emit("\n⚠️ [KOLDSTART FEJLEDE - ANGREBSLOOP AKTIVERET]:")
        self.emit("Du drejer nøgleomskifteren på CPU'en fra STOP til RUN uden at have sikret netværket...")
        self.emit("Angriberens loop fanger opstarten og overskriver øjeblikkeligt DB1 med en byte-bomb på port 102!")
        self.emit("CPU'en kastes tilbage i DEFECTIVE STOP! Du kan ikke tvinge en PLC i RUN, hvis netværkssårbarheden ikke er lukket!")

    def block_port_102_passivates_safety(self) -> None:
        self.plc.f_passivated = True
        self.emit("\n🚨 [ALARM: F-I/O PASSIVERING & NØDSTOP - EN ISO 13849 / IEC 62061]:")
        self.emit("Du blokerede port 102 totalt i cellens firewall!")
        self.emit("Det stoppede angriberen, men kappede samtidig safety-kommunikationen mellem CPU 1516F og de decentrale ET 200SP I/O-moduler.")
        self.emit("Safety-systemet reagerer som designet: Udløser øjeblikkelig F-I/O passivering og nødstop af hele fabrikken!")
        self.emit("Læresætning: Sikkerheds-I/O kan ikke bare isoleres blindt – safety-conduits skal tillade autoriseret PROFIsafe-trafik!")

    def live_firmware_patch_corrupts(self) -> None:
        self.plc.bootloader_locked = True
        self.emit("\n🚨 [SUPPLY CHAIN OVERTRÆDELSE - BOOTLOADER LÅST]:")
        self.emit("Du downloadede en ny firmware-pakke over det inficerede netværk uden at verificere SHA-256 hash-værdien!")
        self.emit("Angriberen udførte et Man-in-the-Middle angreb og injicerede en korrupt bootloader-blok.")
        self.emit("CPU'en nægter at boote og kræver en fabriksnulstilling (NIS2 Artikel 21.2.e overtrædelse).")

    def direct_laptop_arp_poisoned(self) -> None:
        self.emit("\n⚠️ [ARP-SPOOFING KAPRET TIA-SESSION]:")
        self.emit("Du tilsluttede din bærbare direkte i CPU'ens port uden at isolere din egen IP.")
        self.emit("Angriberens ARP-spoofing opsnappede din ingeniørsession og forsøgte at injicere et uautoriseret OB-kald.")
        self.emit("Sikkerhedsrelæet koblede fra for at beskytte maskinen!")

    def restore_plc_db1(self) -> None:
        self.plc_defect_stop = False
        self.flags.discard("plc-defect-stop")
        self.flags.add("backup-taken")
        self.emit("\n✅ [DB1 GENDANNET FRA SIKKERHEDSKOPI]:")
        self.emit("Du overfører den sunde DB1-blok fra det autoriserede USB-stik. STOP-koden 0x4542 forsvinder!")

    # -------------------------------------------------------------------------
    # CHAPTER 4 ACTIONS (REAL-WORLD OPC UA & IDMZ)
    # -------------------------------------------------------------------------
    def trust_scada_certificate(self) -> None:
        self.flags.add("cert-trusted")
        self.emit("\n📜 [X.509 CERTIFIKAT GODKENDT]:")
        self.emit("I OPC UA certifikat-truststoren flytter du 'WinCC_SCADA_Client_Cert_2026.der' fra mappen 'Rejected' til 'Trusted'.")
        self.emit("Serveren accepterer nu SCADA-klientens kryptografiske identitet!")
        self.check_chapter_4_completion()

    def enable_opc_crypto(self) -> None:
        self.flags.add("opc-crypto-active")
        self.emit("\n🔒 [OPC UA KRYPTERING AKTIVERET]:")
        self.emit("SecurityPolicy sat til 'Basic256Sha256' og MessageSecurityMode sat til 'SignAndEncrypt'.")
        self.emit("Al kommunikation på port 4840 er nu beskyttet mod aflytning og manipulation jf. NIS2 Artikel 21.2.h!")
        self.check_chapter_4_completion()

    def disable_opc_anonymous(self) -> None:
        self.flags.add("anon-disabled")
        self.emit("\n🚫 [ANONYM ADGANG DEAKTIVERET]:")
        self.emit("Anonymous UserTokenType er fjernet fra endpointet. Al adgang kræver nu X.509 certifikat eller stærke RBAC-brugeroplysninger.")
        self.check_chapter_4_completion()

    def disconnect_4g_router(self) -> None:
        self.flags.add("router-disconnected")
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

        if "pumpe" in norm:
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
            self.emit(self.plc.description)
            self.emit(self.plc.get_telemetry(self))
            return
        if "opc" in norm:
            self.emit(self.opcua.description)
            self.emit(self.opcua.get_telemetry(self))
            return
        if "router" in norm or "4g" in norm:
            self.emit("Teltonika RUT950 4G-router. Den er tilsluttet en ekstern mobilmast og har en aktiv VPN-tunnel til udlandet.")
            return

        self.emit(f"Du undersøger {target}. Alt virker som forventet for denne komponent.")

    def talk_to(self, character: str) -> None:
        norm = character.lower().strip()
        if "hans" in norm:
            greeting = self.hans.get_greeting(self)
            self.emit(f"\n{greeting}")
            if random.random() < 0.4:
                self.emit(f"\n{self.hans.get_anecdote()}")
        elif "kirsten" in norm or "revisor" in norm:
            if self.chapter == 5:
                self.complete_audit()
            else:
                self.emit("Kirsten fra Tilsynet er endnu ikke ankommet. Hun forventes først til den afsluttende revision.")
        else:
            self.emit(f"Der er ingen ved navn '{character}' her.")

    def submit_early_warning(self) -> None:
        success, msg = self.incident.submit_early_warning(self.simulated_day, self.simulated_hour, "Sabotage af procespumper og feldbus.")
        if success:
            self.flags.add("early-warning-reported")
        self.emit(f"\n{msg}")

    def export_audit_report(self) -> None:
        flaws = self.collect_flaws()
        passed, score, remarks, report_text = self.incident.evaluate_compliance(
            self.player.name, self.flags, flaws, self.forensics.pi_handling_state
        )
        try:
            with open("NIS2_Audit_Rapport_NordicH2O.md", "w", encoding="utf-8") as f:
                f.write(report_text)
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
        verdict = self.kirsten.format_verdict(passed, score, remarks)
        self.emit(verdict)
        if passed:
            self.export_audit_report()
            self.running = False

    def help(self) -> None:
        self.emit("\n=== TILGÆNGELIGE KOMMANDOER ===")
        self.emit("  Tast et tal [1-6] fra valgmenuen for at udføre en handling direkte.")
        self.emit("  GÅ TIL <zone>             Skift rum (indgangen, pumpehuset, ventil-øen, el-tavlen, kontrolrummet)")
        self.emit("  UNDERSØG <komponent>      Inspicér maskine, kabelbakke eller enhed")
        self.emit("  TAL MED HANS              Få praktisk vejledning og erfaringer fra driftsteknikeren")
        self.emit("  ÅBN WIRESHARK             Start den integrerede terminal-sniffer")
        self.emit("  WIRESHARK FILTER <tekst>  Filtrer pakker (f.eks. 'modbus.func_code == 6' eller 'b8:27:eb')")
        self.emit("  WIRESHARK DETALJER <nr>   Dybdegående OSI-lags inspektion af en pakke")
        self.emit("  INDBERET HÆNDELSE         Indsend lovpligtig NIS2 24-timers Early Warning")
        self.emit("  VIS EVIDENS               Gennemse digital Chain of Custody journal")
        self.emit("  STATUS                    Vis aktuel arbejdsdag, tidsfrist og kapitelmål")
        self.emit("  RYGSÆK                    Vis inventar og værktøjer")

    def tour(self) -> None:
        self.emit("\nHans McDonald tager dig med på en teknisk rundtur gennem anlæggets Purdue-zoner:")
        for lvl, p in sorted(PURDUE_LEVELS.items()):
            self.emit(f"  • [{p.name}]: {p.description} (Krav: {p.iec_sl_target})")

    def status(self) -> None:
        r = self.get_current_room()
        self.emit(f"\n[STATUS] KAPITEL {self.chapter}/5 | Zone: {r.title} ({r.purdue_level})")
        self.emit(f"Mål: {OBJECTIVES.get(self.chapter, 'Gennemfør audit')}")
        self.emit(f"Arbejdsdag {self.simulated_day}/5, time {self.simulated_hour}/8 | Tid til audit: {self.time_display}")
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
