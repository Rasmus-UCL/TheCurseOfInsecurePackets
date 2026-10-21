"""Main Tkinter Application Cockpit with Dedicated 2D Screen & Integrated Green Terminal."""

from __future__ import annotations

import tkinter as tk
from typing import Any

from core.engine import GameEngine
from gui.canvas import GameCanvas
from gui.terminal import TerminalWidget
from models import OBJECTIVES


class GameApp(tk.Tk):
    """Cockpit GUI combining 2D plant screen with integrated Green CRT Terminal."""

    def __init__(self) -> None:
        super().__init__()
        self.title("The Curse of Insecure Packets - OT Cybersikkerhed Cockpit (NIS2 / IEC 62443)")
        self.geometry("1160x860")
        self.minsize(1000, 740)
        self.configure(bg="#081018")

        self.intro_step = 0
        self.intro_answers: list[str] = []

        # Setup Game Engine
        self.engine = GameEngine(output=self.write_to_terminal)

        self.setup_ui()
        self.after(100, self.introduce)
        self.after(1000, self.update_timer)

    def setup_ui(self) -> None:
        # 1. Top Header Bar: Simulation Status, Timers & Workweek
        header = tk.Frame(self, bg="#0d1822", padx=16, pady=6, relief="ridge", bd=1)
        header.pack(fill="x")

        tk.Label(
            header, text="THE CURSE OF INSECURE PACKETS",
            bg="#0d1822", fg="#f6d365", font=("Consolas", 12, "bold"),
        ).pack(side="left")

        self.timer_label = tk.Label(
            header, text="Dag 1/5 | Audit: --:--",
            bg="#0d1822", fg="#f6d365", font=("Consolas", 11, "bold"),
        )
        self.timer_label.pack(side="right")

        self.acute_label = tk.Label(
            header, text="ℹ️ Pumpe 2: Stand-by",
            bg="#0d1822", fg="#94a3b8", font=("Consolas", 11, "bold"), padx=12,
        )
        self.acute_label.pack(side="right", padx=10)

        # 2. Purdue Zone Navigation Bar
        zone_bar = tk.Frame(self, bg="#101c27", padx=12, pady=4, relief="groove", bd=1)
        zone_bar.pack(fill="x")

        tk.Label(
            zone_bar, text="PURDUE ZONER:", bg="#101c27", fg="#9cbcd4",
            font=("Segoe UI", 9, "bold"), padx=4,
        ).pack(side="left")

        self.room_buttons: dict[str, tk.Button] = {}
        for title, key in (
            ("🚪 Indgangen (L4)", "indgangen"),
            ("🚰 Pumpehuset (L1)", "pumpehuset"),
            ("💨 Ventil-øen (L1)", "ventil-oen"),
            ("⚡ El-tavlen (L1/L2)", "el-tavlen"),
            ("🖥️ Kontrolrummet (IDMZ)", "kontrolrummet"),
        ):
            b = tk.Button(
                zone_bar, text=title, bg="#16293a", fg="#d8e6ed", activebackground="#274a68",
                relief="groove", font=("Segoe UI", 9),
                command=lambda k=key: self.navigate_to(k),
            )
            b.pack(side="left", padx=3)
            self.room_buttons[key] = b

        # Quick Tool Buttons in Navigation Bar
        self.mode_btn = tk.Button(
            zone_bar, text="🎓 Tilstand: TEACH", bg="#065f46", fg="#a7f3d0", activebackground="#047857",
            font=("Segoe UI", 8, "bold"), relief="raised", padx=8, command=self.toggle_mode,
        )
        self.mode_btn.pack(side="right", padx=4)

        tk.Button(
            zone_bar, text="🎯 NIS2 Guide", bg="#1e40af", fg="white",
            font=("Segoe UI", 8, "bold"), relief="raised", padx=6, command=self.show_guidance_window,
        ).pack(side="right", padx=3)

        tk.Button(
            zone_bar, text="📋 Tilsynet", bg="#4c1d95", fg="#e9d5ff",
            font=("Segoe UI", 8, "bold"), relief="groove", padx=6, command=lambda: self.command("ring til kirsten"),
        ).pack(side="right", padx=3)

        tk.Button(
            zone_bar, text="☕ Hans", bg="#1e293b", fg="#fde047",
            font=("Segoe UI", 8, "bold"), relief="groove", padx=6, command=lambda: self.command("tal med hans"),
        ).pack(side="right", padx=3)

        self.support_btn = tk.Button(
            zone_bar, text="📞 Support (3/3)", bg="#162b3d", fg="#dceaf4",
            font=("Segoe UI", 8, "bold"), relief="groove", padx=6, command=lambda: self.command("techsupport"),
        )
        self.support_btn.pack(side="right", padx=3)

        tk.Button(
            zone_bar, text="🎒 Rygsæk", bg="#162b3d", fg="#dceaf4",
            font=("Segoe UI", 8, "bold"), relief="groove", padx=6, command=lambda: self.command("inventory"),
        ).pack(side="right", padx=3)

        # 3. Objective Banner
        self.objective_banner = tk.Label(
            self, text="Aktuelt mål: Start ansættelsessamtale",
            bg="#172e42", fg="#dceaf4", font=("Segoe UI", 9, "bold"),
            padx=16, pady=3, anchor="w",
        )
        self.objective_banner.pack(fill="x")

        # 3.5. Four Core Metrics & Investigation Bar (Etape 2 Redesign)
        self.metrics_bar = tk.Frame(self, bg="#0c1622", padx=12, pady=4, relief="ridge", bd=1)
        self.metrics_bar.pack(fill="x")

        self.metric_drift_label = tk.Label(
            self.metrics_bar, text="🔧 Drift: 80%", bg="#0c1622", fg="#4ade80",
            font=("Segoe UI", 9, "bold"), padx=6,
        )
        self.metric_drift_label.pack(side="left")

        self.metric_sikkerhed_label = tk.Label(
            self.metrics_bar, text="🛡️ Sikkerhed: 25%", bg="#0c1622", fg="#38bdf8",
            font=("Segoe UI", 9, "bold"), padx=6,
        )
        self.metric_sikkerhed_label.pack(side="left")

        self.metric_compliance_label = tk.Label(
            self.metrics_bar, text="📜 Compliance: 40%", bg="#0c1622", fg="#fbbf24",
            font=("Segoe UI", 9, "bold"), padx=6,
        )
        self.metric_compliance_label.pack(side="left")

        self.metric_tillid_label = tk.Label(
            self.metrics_bar, text="🤝 Tillid: 50%", bg="#0c1622", fg="#a78bfa",
            font=("Segoe UI", 9, "bold"), padx=6,
        )
        self.metric_tillid_label.pack(side="left")

        self.sagstavle_btn = tk.Button(
            self.metrics_bar, text="🕵️ Sagstavle (0 spor)", bg="#7c2d12", fg="#fed7aa",
            activebackground="#9a3412", font=("Segoe UI", 8, "bold"), relief="raised", padx=8,
            command=self.toggle_sagstavle,
        )
        self.sagstavle_btn.pack(side="right", padx=4)

        # 4. Dedicated 2D Visual Plant Floor Screen (Height = 330 px)
        self.map = GameCanvas(self, self.engine, on_hotspot_click=self.on_canvas_click, height=330)
        self.map.pack(fill="x", expand=False, padx=12, pady=(4, 2))

        # 5. Integrated Green-on-Black CRT Terminal (Takes full remaining space)
        self.terminal = TerminalWidget(self, on_command=self.command)
        self.terminal.pack(fill="both", expand=True, padx=12, pady=(2, 6))

        self.update_nav_highlight()

    # -------------------------------------------------------------------------
    # TERMINAL OUTPUT & PROMPT SYNCHRONIZATION
    # -------------------------------------------------------------------------
    def write_to_terminal(self, message: str) -> None:
        self.terminal.write_block(message)
        self.terminal.set_prompt_prefix(self.engine.room)
        self.update_timer_display()
        self.map.draw()

    def command(self, cmd: str) -> None:
        normalized = cmd.strip()
        if not normalized:
            return

        if self.intro_step:
            self.submit_intro(normalized)
            return

        # Special command window triggers
        if normalized.lower() in {"hjælp", "help", "?"}:
            self.show_help_window()
            return
        if normalized.lower() in {"guide", "guidance", "nis2 guide"}:
            self.show_guidance_window()
            return

        # Execute on engine
        self.engine.handle_command(normalized)

        # Synchronize view mode with active workbench or clue board
        if normalized.lower() in {"sagstavle", "tavle", "board", "case board", "clueboard", "investigation", "efterforskning"}:
            self.map.view_mode = "clue_board"
            self.sagstavle_btn.configure(text="🚪 Luk Sagstavle", relief="sunken")
        elif self.engine.active_workbench:
            self.map.view_mode = self.engine.active_workbench
        elif normalized.lower() in {"vis rum", "luk workbench", "tilbage", "rum", "forlad workbench", "luk sagstavle"}:
            self.map.view_mode = "room"
            self.sagstavle_btn.configure(relief="raised")
        elif "chapter-1-done" in self.engine.flags and self.map.view_mode == "vfd_workbench":
            self.map.view_mode = "room"
        elif "chapter-2-done" in self.engine.flags and self.map.view_mode == "switch_workbench":
            self.map.view_mode = "room"

        self.terminal.set_prompt_prefix(self.engine.room)
        self.update_mode_button()
        self.update_nav_highlight()
        self.update_objective()
        self.update_metrics_display()
        self.map.draw()

    def toggle_sagstavle(self) -> None:
        if self.map.view_mode == "clue_board":
            self.map.view_mode = "room"
            self.sagstavle_btn.configure(relief="raised")
        else:
            self.map.view_mode = "clue_board"
            self.sagstavle_btn.configure(text="🚪 Luk Sagstavle", relief="sunken")
            self.command("sagstavle")
        self.update_metrics_display()
        self.map.draw()

    def update_metrics_display(self) -> None:
        if not hasattr(self.engine, "metrics"):
            return
        m = self.engine.metrics
        drift_color = "#4ade80" if m.drift >= 70 else ("#f59e0b" if m.drift >= 40 else "#ef4444")
        sec_color = "#38bdf8" if m.sikkerhed >= 70 else ("#f59e0b" if m.sikkerhed >= 40 else "#ef4444")
        comp_color = "#fbbf24" if m.compliance >= 70 else ("#f59e0b" if m.compliance >= 40 else "#ef4444")
        tillid_color = "#a78bfa" if m.tillid >= 60 else ("#f59e0b" if m.tillid >= 35 else "#ef4444")

        self.metric_drift_label.configure(text=f"🔧 Drift: {m.drift}%", fg=drift_color)
        self.metric_sikkerhed_label.configure(text=f"🛡️ Sikkerhed: {m.sikkerhed}%", fg=sec_color)
        self.metric_compliance_label.configure(text=f"📜 Compliance: {m.compliance}%", fg=comp_color)
        self.metric_tillid_label.configure(text=f"🤝 Tillid: {m.tillid}%", fg=tillid_color)

        num_clues = len(self.engine.investigation.get_discovered_clues())
        if self.map.view_mode != "clue_board":
            self.sagstavle_btn.configure(text=f"🕵️ Sagstavle ({num_clues} spor)")

    def toggle_mode(self) -> None:
        self.engine.toggle_game_mode()
        self.update_mode_button()
        self.terminal.set_prompt_prefix(self.engine.room)
        self.map.draw()

    def update_mode_button(self) -> None:
        if self.engine.game_mode == "teach":
            self.mode_btn.configure(
                text="🎓 Tilstand: TEACH",
                bg="#065f46",
                fg="#a7f3d0",
                activebackground="#047857",
            )
        else:
            self.mode_btn.configure(
                text="📝 Tilstand: EKSAMEN",
                bg="#854d0e",
                fg="#fef08a",
                activebackground="#a16207",
            )

    def navigate_to(self, room_key: str) -> None:
        if self.map.view_mode != "room":
            self.map.view_mode = "room"
        self.command(f"gå til {room_key}")

    def on_canvas_click(self, hotspot_name: str) -> None:
        if hotspot_name in {"ts35 din-skinne", "din-skinne", "din skinne"}:
            self.command("firewall workbench")
            return
        self.command(f"undersøg {hotspot_name}")

    def update_nav_highlight(self) -> None:
        for r_key, btn in self.room_buttons.items():
            if r_key == self.engine.room:
                btn.configure(bg="#0284c7", fg="white", relief="sunken")
            else:
                btn.configure(bg="#16293a", fg="#d8e6ed", relief="groove")

    def update_objective(self) -> None:
        if self.engine.chapter == 0:
            self.objective_banner.configure(text="Ansættelsessamtale i gang")
            return
        obj_text = OBJECTIVES.get(self.engine.chapter, "Gennemfør audit")
        self.objective_banner.configure(
            text=f"Aktuelt mål (Kapitel {self.engine.chapter}/5): {obj_text}"
        )

    def introduce(self) -> None:
        self.write_to_terminal("=== THE CURSE OF INSECURE PACKETS - ET OT-CYBERSECURITY EVENTYR ===")
        self.write_to_terminal(
            "Jens Majer, direktør: Velkommen til ansættelsessamtalen her hos Nordic H2O Utility.\n"
            "Før vi gennemgår anlæggets udfordringer: Hvad hedder du?"
        )
        self.intro_step = 1
        self.objective_banner.configure(text="Ansættelsessamtale: Skriv dit navn i terminalen forneden og tryk Enter.")

    def submit_intro(self, answer: str) -> None:
        self.intro_answers.append(answer)
        if len(self.intro_answers) == 1:
            self.intro_step = 2
            self.write_to_terminal(
                f"Jens: Godt at have dig med om bord, {answer}. "
                "Hvilken uddannelse eller baggrund bringer du med dig? (f.eks. Automationsteknolog, IT-Teknologi, Elektriker)"
            )
            self.objective_banner.configure(text="Ansættelsessamtale: Hvilken uddannelse har du?")
            return

        self.intro_step = 0
        edu = self.intro_answers[1] if len(self.intro_answers) > 1 else "Automation & IT-Sikkerhed"
        self.engine.start(self.intro_answers[0], edu)
        self.update_objective()
        self.update_nav_highlight()

    def update_timer_display(self) -> None:
        self.update_metrics_display()
        audit = self.engine.time_display
        color = "#ef4444" if self.engine.time_remaining <= 60 else "#f6d365"
        self.timer_label.configure(
            text=f"Dag {self.engine.simulated_day}/5 (Time {self.engine.simulated_hour}/8) | Audit: {audit}",
            fg=color,
        )

        if self.engine.cavitation_deadline_active:
            cav_time = self.engine.cavitation_time_display
            c_color = "#ef4444" if self.engine.cavitation_time_remaining <= 25 else "#f87171"
            self.acute_label.configure(text=f"🚨 KAVITATION: {cav_time}", fg=c_color)
        elif self.engine.pump_deadline_active:
            pump_time = self.engine.pump_time_display
            p_color = "#ef4444" if self.engine.pump_time_remaining <= 30 else "#f87171"
            self.acute_label.configure(text=f"⚠️ PUMPE 2 ALARM: {pump_time}", fg=p_color)
        elif "chapter-2-done" in self.engine.flags:
            self.acute_label.configure(text="✅ PROFINET & Ventiler sikret (MRP aktiv)", fg="#4ade80")
        elif "chapter-1-done" in self.engine.flags:
            self.acute_label.configure(text="✅ Pumpe 2 tryk stabiliseret (42 Bar)", fg="#4ade80")
        else:
            self.acute_label.configure(text="ℹ️ Pumpe 2: Stand-by (Alarm aktiveres i pumpehuset)", fg="#64748b")

        self.support_btn.configure(text=f"📞 Support ({self.engine.max_help_calls - self.engine.help_calls}/{self.engine.max_help_calls})")

    def update_timer(self) -> None:
        if self.engine.running and self.engine.timer_started_at:
            self.engine.check_timers()
            self.update_timer_display()
        if self.winfo_exists():
            self.after(1000, self.update_timer)

    def show_guidance_window(self) -> None:
        window = tk.Toplevel(self)
        window.title("Faglig Læringsguide (NIS2 / IEC 62443)")
        window.geometry("640x480")
        window.configure(bg="#0f1923")
        window.transient(self)

        tk.Label(
            window, text=f"KAPITEL {self.engine.chapter}/5 GUIDANCE",
            bg="#0f1923", fg="#f6d365", font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        txt = tk.Text(window, bg="#080d12", fg="#dceaf4", font=("Consolas", 10), wrap="word", padx=12, pady=12)
        txt.pack(fill="both", expand=True, padx=16, pady=8)

        guidance_text = (
            f"AKTUELT MÅL: {OBJECTIVES.get(self.engine.chapter, 'Gennemfør audit')}\n\n"
            f"FAGLIG VEJLEDNING:\n"
            f"- Følg IEC 62443-3-2 Zoner & Conduits.\n"
            f"- Indberet hændelser rettidigt jf. NIS2 Artikel 23 ('indberet hændelse').\n"
            f"- Sørg for at sikre beviser i Faraday-pose ('sikr pi i faraday-pose').\n"
            f"- Tag altid offline backup før ændringer i TIA Portal.\n"
            f"- Hærd OPC UA med Basic256Sha256 og godkend certifikater i truststoren.\n"
        )
        txt.insert("1.0", guidance_text)
        txt.configure(state="disabled")

        tk.Button(window, text="Luk guide", bg="#1b3348", fg="white", command=window.destroy).pack(pady=(0, 12))

    def show_help_window(self) -> None:
        self.engine.help()
        self.terminal.set_prompt_prefix(self.engine.room)
