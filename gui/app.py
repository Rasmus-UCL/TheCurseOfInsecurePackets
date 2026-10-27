"""Main Tkinter Application Cockpit with Start Screen, 2D Visual Map & Integrated Green CRT Terminal."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk
from typing import Any

from core.engine import GameEngine
from gui.canvas import GameCanvas
from gui.terminal import TerminalWidget
from models import OBJECTIVES


class GameApp(tk.Tk):
    """Cockpit GUI combining Start Menu with 2D plant screen & integrated Green CRT Terminal."""

    def __init__(self) -> None:
        super().__init__()
        self.title("The Curse of Insecure Packets - OT Cybersikkerhed Cockpit (NIS2 / IEC 62443)")
        self.geometry("1180x840")
        self.minsize(1180, 840)
        self.maxsize(1180, 840)
        self.resizable(False, False)
        self.configure(bg="#081018")

        self.intro_step = 0
        self.intro_answers: list[str] = []
        self.save_files_meta: list[dict[str, Any]] = []
        self.action_buttons: list[tk.Button] = []

        # Setup Game Engine with terminal callback
        self.engine = GameEngine(output=self.write_to_terminal)
        self.engine.auto_print_choices = False

        # Build UI Containers: Main Menu & Active Gameplay
        self.setup_ui()

        # Start on Main Menu by default
        self.show_main_menu("new_game")
        self.after(1000, self.update_timer)

    # -------------------------------------------------------------------------
    # UI SETUP (DUAL CONTAINER ARCHITECTURE)
    # -------------------------------------------------------------------------
    def setup_ui(self) -> None:
        """Create menu container and gameplay container."""
        self.menu_container = tk.Frame(self, bg="#081018")
        self.gameplay_container = tk.Frame(self, bg="#081018")

        self.setup_menu_ui()
        self.setup_gameplay_ui()

    def setup_gameplay_ui(self) -> None:
        """Create all widgets for the live gameplay screen."""
        # 1. Top Header Bar: Simulation Status, Timers & Workweek
        header = tk.Frame(self.gameplay_container, bg="#0d1822", padx=14, pady=6, relief="ridge", bd=1)
        header.pack(fill="x")

        # Pinned Prominent Home and Save buttons at top-left
        self.btn_hovedmenu = tk.Button(
            header, text="🏠 HOVEDMENU", bg="#0284c7", fg="#ffffff", activebackground="#0369a1",
            activeforeground="#ffffff", font=("Segoe UI", 9, "bold"), relief="raised", padx=10, pady=2,
            command=self.prompt_return_to_menu,
        )
        self.btn_hovedmenu.pack(side="left", padx=(0, 6))

        self.btn_quick_save = tk.Button(
            header, text="💾 GEM", bg="#059669", fg="#ffffff", activebackground="#047857",
            activeforeground="#ffffff", font=("Segoe UI", 9, "bold"), relief="raised", padx=10, pady=2,
            command=self.quick_save,
        )
        self.btn_quick_save.pack(side="left", padx=(0, 14))

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
        zone_bar = tk.Frame(self.gameplay_container, bg="#101c27", padx=12, pady=4, relief="groove", bd=1)
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

        # Controls on the right side of Navigation Bar
        self.mode_btn = tk.Button(
            zone_bar, text="🎓 Tilstand: TEACH", bg="#065f46", fg="#a7f3d0", activebackground="#047857",
            font=("Segoe UI", 8, "bold"), relief="raised", padx=8, command=self.toggle_mode,
        )
        self.mode_btn.pack(side="right", padx=3)

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
            self.gameplay_container, text="Aktuelt mål: Start ansættelsessamtale",
            bg="#172e42", fg="#dceaf4", font=("Segoe UI", 9, "bold"),
            padx=16, pady=3, anchor="w",
        )
        self.objective_banner.pack(fill="x")

        # 3.5. Four Core Metrics & Investigation Bar (Etape 2 Redesign)
        self.metrics_bar = tk.Frame(self.gameplay_container, bg="#0c1622", padx=12, pady=4, relief="ridge", bd=1)
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

        # 4. Dedicated 2D Visual Plant Floor Screen (Static Height = 310 px in all modes)
        self.map = GameCanvas(
            self.gameplay_container,
            self.engine,
            on_hotspot_click=self.on_canvas_click,
            app=self,
            height=310,
        )
        self.map.pack(fill="x", expand=False, padx=12, pady=(4, 2))

        # 4.5. Dedicated Interactive Action Panel (Clickable Choice Buttons so terminal isn't flooded)
        self.action_panel = tk.Frame(self.gameplay_container, bg="#0b1520", padx=10, pady=5, relief="groove", bd=1)
        self.action_panel.pack(fill="x", expand=False, padx=12, pady=(2, 2))

        self.action_header_label = tk.Label(
            self.action_panel,
            text="⚡ HANDLINGER I ZONEN (Klik på en knap herunder, klik på 2D-kortet foroven, eller skriv i terminalen):",
            bg="#0b1520", fg="#f6d365", font=("Segoe UI", 8, "bold"), anchor="w",
        )
        self.action_header_label.pack(fill="x", pady=(0, 3))

        self.action_grid = tk.Frame(self.action_panel, bg="#0b1520")
        self.action_grid.pack(fill="x")
        self.action_grid.columnconfigure(0, weight=1, uniform="act_col")
        self.action_grid.columnconfigure(1, weight=1, uniform="act_col")

        # 5. Integrated Green-on-Black CRT Terminal (Takes remaining space; prompt pinned at bottom)
        self.terminal = TerminalWidget(self.gameplay_container, on_command=self.command)
        self.terminal.pack(fill="both", expand=True, padx=12, pady=(2, 6))

    # -------------------------------------------------------------------------
    # START SCREEN & MAIN MENU UI SETUP
    # -------------------------------------------------------------------------
    def setup_menu_ui(self) -> None:
        """Construct the atmospheric start screen with tabs and game options."""
        # Top Brand & Title Banner
        header = tk.Frame(self.menu_container, bg="#0a121a", pady=18, padx=24, relief="ridge", bd=1)
        header.pack(fill="x")

        tk.Label(
            header, text="🏭 NORDIC H2O UTILITY — INCIDENT COMMAND",
            bg="#0a121a", fg="#38bdf8", font=("Consolas", 10, "bold"),
        ).pack(anchor="center")

        tk.Label(
            header, text="THE CURSE OF INSECURE PACKETS",
            bg="#0a121a", fg="#f6d365", font=("Consolas", 22, "bold"), pady=4,
        ).pack(anchor="center")

        tk.Label(
            header,
            text="OT Cybersikkerhed, IEC 62443 Zoner & NIS2 Incident Response Træningssimulator",
            bg="#0a121a", fg="#94a3b8", font=("Segoe UI", 10),
        ).pack(anchor="center")

        # Tab Navigation Bar
        tab_bar = tk.Frame(self.menu_container, bg="#0d1822", padx=20, pady=8, relief="groove", bd=1)
        tab_bar.pack(fill="x")

        self.tab_buttons: dict[str, tk.Button] = {}
        for tab_id, tab_label in (
            ("new_game", "🎮 START NYT SPIL"),
            ("load_game", "💾 INDLÆS GEMT SPIL"),
            ("lore", "📖 OM SPILLET & LORE"),
            ("exit", "❌ AFSLUT"),
        ):
            btn = tk.Button(
                tab_bar, text=tab_label, bg="#16293a", fg="#d8e6ed", activebackground="#0284c7",
                font=("Segoe UI", 10, "bold"), relief="raised", padx=16, pady=5,
                command=lambda tid=tab_id: self.switch_menu_tab(tid),
            )
            btn.pack(side="left", padx=6)
            self.tab_buttons[tab_id] = btn

        # Content Cards Container
        self.menu_content_frame = tk.Frame(self.menu_container, bg="#081018")
        self.menu_content_frame.pack(fill="both", expand=True)

        self.cards: dict[str, tk.Frame] = {}
        self.setup_card_new_game()
        self.setup_card_load_game()
        self.setup_card_lore()
        self.setup_card_exit()

    def setup_card_new_game(self) -> None:
        """Card: Player configuration and Mode selection (Teach vs Exam)."""
        card = tk.Frame(self.menu_content_frame, bg="#0d1822", padx=28, pady=20, relief="ridge", bd=1)
        self.cards["new_game"] = card

        tk.Label(
            card, text="START NY MISSION",
            bg="#0d1822", fg="#f6d365", font=("Consolas", 14, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            card, text="Konfigurer din profil som tilkaldt OT-cybersikkerhedskonsulent og vælg den ønskede tilstand.",
            bg="#0d1822", fg="#94a3b8", font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 16))

        # Main Split Frame: Left = Profile, Right = Mode Selection
        split = tk.Frame(card, bg="#0d1822")
        split.pack(fill="both", expand=True)

        # --- LEFT: Profile Form ---
        left_col = tk.Frame(split, bg="#101c27", padx=16, pady=16, relief="groove", bd=1)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 12))

        tk.Label(
            left_col, text="👤 KONSULENT PROFIL",
            bg="#101c27", fg="#38bdf8", font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            left_col, text="Dit Navn / Kaldenavn:",
            bg="#101c27", fg="#dceaf4", font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(4, 2))

        self.entry_player_name = tk.Entry(
            left_col, bg="#080d12", fg="#86efac", insertbackground="#4ade80",
            font=("Consolas", 11), relief="sunken", bd=1,
        )
        self.entry_player_name.pack(fill="x", pady=(0, 14), ipady=4)
        self.entry_player_name.insert(0, "Konsulent")

        tk.Label(
            left_col, text="Uddannelsesretning / Faglig Baggrund:",
            bg="#101c27", fg="#dceaf4", font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(4, 2))

        self.combo_edu_var = tk.StringVar(value="Automationsteknolog")
        self.entry_player_edu = ttk.Combobox(
            left_col, textvariable=self.combo_edu_var,
            values=[
                "Automationsteknolog",
                "IT-Teknologi",
                "Elektriker / Installatør",
                "Datamatiker / Softwareudvikler",
                "Maskinmester / Driftsingeniør",
                "Anden teknisk baggrund",
            ],
            font=("Segoe UI", 10),
        )
        self.entry_player_edu.pack(fill="x", pady=(0, 14), ipady=2)

        info_box = tk.Label(
            left_col,
            text="ℹ️ Du ankommer til Nordic H2O Utility i en akut krisesituation.\n"
                 "Pumpe 2 er i alarm, SCADA-loggen er manipuleret, og Revisor Kirsten "
                 "har indledt et uanmeldt NIS2-tilsyn med trussel om 10 mio. EUR i bøde.",
            bg="#0a121a", fg="#cbd5e1", font=("Segoe UI", 8),
            justify="left", padx=10, pady=10, relief="sunken", bd=1,
        )
        info_box.pack(fill="x", pady=(10, 0))

        # --- RIGHT: Mode Selection (Teach vs Exam) ---
        right_col = tk.Frame(split, bg="#101c27", padx=16, pady=16, relief="groove", bd=1)
        right_col.pack(side="right", fill="both", expand=True, padx=(12, 0))

        tk.Label(
            right_col, text="🎯 VÆLG TRÆNINGSTILSTAND",
            bg="#101c27", fg="#f6d365", font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        self.menu_mode_var = tk.StringVar(value="teach")

        # Teach Mode Card
        teach_frame = tk.Frame(right_col, bg="#0a1a14", padx=12, pady=10, relief="ridge", bd=1)
        teach_frame.pack(fill="x", pady=(0, 10))

        rb_teach = tk.Radiobutton(
            teach_frame, text="🎓 Teach Mode (Undervisningstilstand) — [ANBEFALET]",
            variable=self.menu_mode_var, value="teach",
            bg="#0a1a14", fg="#34d399", selectcolor="#064e3b",
            activebackground="#0a1a14", activeforeground="#6ee7b7",
            font=("Segoe UI", 10, "bold"),
        )
        rb_teach.pack(anchor="w")

        tk.Label(
            teach_frame,
            text="• Ingen spoilers i svarmulighederne — alle valg fremstår som realistiske handlinger.\n"
                 "• Hvis du vælger en farlig procedure, griber Hans McDonald ind og stopper dig.\n"
                 "• Hans forklarer hvorfor det er forkert og henviser til rette procedure jf. NIS2 & IEC 62443.\n"
                 "• Ideel til studerende på UCL, workshops og øvelsestimer.",
            bg="#0a1a14", fg="#a7f3d0", font=("Segoe UI", 8),
            justify="left", padx=8, pady=4,
        ).pack(anchor="w")

        # Exam Mode Card
        exam_frame = tk.Frame(right_col, bg="#1a140a", padx=12, pady=10, relief="ridge", bd=1)
        exam_frame.pack(fill="x", pady=(0, 10))

        rb_exam = tk.Radiobutton(
            exam_frame, text="📝 Exam Mode (Eksamenstilstand) — [REALISTISK TEST]",
            variable=self.menu_mode_var, value="exam",
            bg="#1a140a", fg="#fbbf24", selectcolor="#78350f",
            activebackground="#1a140a", activeforeground="#fde68a",
            font=("Segoe UI", 10, "bold"),
        )
        rb_exam.pack(anchor="w")

        tk.Label(
            exam_frame,
            text="• Hans stopper dig IKKE ved fejlvalg — han kommer kun med en tør bemærkning bagefter.\n"
                 "• Forkerte valg udføres og udløser realistiske driftskonsekvenser og NIS2-bøder.\n"
                 "• Svarmulighederne blandes i tilfældig rækkefølge ved hvert træk.\n"
                 "• Ideel til eksamensprojekter, certificeringer og selvtest.",
            bg="#1a140a", fg="#fde68a", font=("Segoe UI", 8),
            justify="left", padx=8, pady=4,
        ).pack(anchor="w")

        # Bottom Launch & Tutorial Options
        bottom_bar = tk.Frame(card, bg="#0d1822", pady=12)
        bottom_bar.pack(fill="x")

        self.tutorial_var = tk.BooleanVar(value=True)
        chk_tut = tk.Checkbutton(
            bottom_bar,
            text="🎓 Start med 60-sekunders Intro-Tutorial (Kapitel 0: Lær hotspots, tshark & Sagstavlen med Hans)",
            variable=self.tutorial_var,
            bg="#0d1822", fg="#38bdf8", selectcolor="#081018",
            activebackground="#0d1822", activeforeground="#7dd3fc",
            font=("Segoe UI", 9, "bold"),
        )
        chk_tut.pack(side="left", padx=4)

        tk.Button(
            bottom_bar, text="🚀 START DIREKTE (KAP. 1)",
            bg="#1e293b", fg="#cbd5e1", activebackground="#334155", activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), relief="groove", padx=12, pady=7,
            command=lambda: self.start_new_game(tutorial=False),
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            bottom_bar, text="🕹️ START SPIL (MED VALGTE INDSTILLINGER)",
            bg="#059669", fg="#ffffff", activebackground="#10b981", activeforeground="#000000",
            font=("Segoe UI", 10, "bold"), relief="raised", padx=18, pady=7,
            command=self.start_new_game,
        ).pack(side="right")

    def setup_card_load_game(self) -> None:
        """Card: View and load saved games from saves/*.json."""
        card = tk.Frame(self.menu_content_frame, bg="#0d1822", padx=28, pady=20, relief="ridge", bd=1)
        self.cards["load_game"] = card

        tk.Label(
            card, text="INDLÆS GEMT SPIL",
            bg="#0d1822", fg="#f6d365", font=("Consolas", 14, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            card, text="Vælg et tidligere gemt spil fra 'saves/' mappen for at genoptage din efterforskning.",
            bg="#0d1822", fg="#94a3b8", font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 16))

        # Split: Listbox on left, detailed summary on right
        split = tk.Frame(card, bg="#0d1822")
        split.pack(fill="both", expand=True)

        left_frame = tk.Frame(split, bg="#101c27", padx=12, pady=12, relief="groove", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(
            left_frame, text="TILGÆNGELIGE GEMTE SPIL:",
            bg="#101c27", fg="#38bdf8", font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        list_container = tk.Frame(left_frame, bg="#101c27")
        list_container.pack(fill="both", expand=True)

        list_scroll = tk.Scrollbar(list_container, bg="#0d1822")
        list_scroll.pack(side="right", fill="y")

        self.save_listbox = tk.Listbox(
            list_container, bg="#080d12", fg="#86efac", selectbackground="#0284c7",
            selectforeground="#ffffff", font=("Consolas", 10), relief="sunken", bd=1,
            yscrollcommand=list_scroll.set,
        )
        self.save_listbox.pack(side="left", fill="both", expand=True)
        list_scroll.config(command=self.save_listbox.yview)
        self.save_listbox.bind("<<ListboxSelect>>", self.on_save_selected)

        right_frame = tk.Frame(split, bg="#101c27", padx=16, pady=12, relief="groove", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(
            right_frame, text="DETALJER OM VALGTE SPIL:",
            bg="#101c27", fg="#f6d365", font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.save_details_label = tk.Label(
            right_frame, text="Vælg et spil fra listen til venstre...",
            bg="#080d12", fg="#dceaf4", font=("Consolas", 10), justify="left", anchor="nw",
            padx=12, pady=12, relief="sunken", bd=1,
        )
        self.save_details_label.pack(fill="both", expand=True)

        # Action Buttons
        btn_bar = tk.Frame(card, bg="#0d1822", pady=14)
        btn_bar.pack(fill="x")

        tk.Button(
            btn_bar, text="📂 Indlæs Valgte Spil", bg="#0284c7", fg="#ffffff",
            font=("Segoe UI", 10, "bold"), relief="raised", padx=16, pady=6,
            command=self.load_selected_save,
        ).pack(side="left", padx=4)

        tk.Button(
            btn_bar, text="🔄 Opdater Liste", bg="#16293a", fg="#d8e6ed",
            font=("Segoe UI", 9), relief="groove", padx=12, pady=6,
            command=self.refresh_save_list,
        ).pack(side="left", padx=4)

        tk.Button(
            btn_bar, text="🗑️ Slet Gemt Spil", bg="#7f1d1d", fg="#fca5a5",
            font=("Segoe UI", 9, "bold"), relief="groove", padx=12, pady=6,
            command=self.delete_selected_save,
        ).pack(side="right", padx=4)

    def setup_card_lore(self) -> None:
        """Card: Lore, Purdue architecture, NIS2, and gameplay mechanics."""
        card = tk.Frame(self.menu_content_frame, bg="#0d1822", padx=28, pady=20, relief="ridge", bd=1)
        self.cards["lore"] = card

        tk.Label(
            card, text="OM SPILLET & LORE",
            bg="#0d1822", fg="#f6d365", font=("Consolas", 14, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            card, text="Baggrundshistorie, Purdue Model, NIS2 Direktivet og gameplay-instruktioner.",
            bg="#0d1822", fg="#94a3b8", font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 10))

        text_container = tk.Frame(card, bg="#080d12")
        text_container.pack(fill="both", expand=True)

        lore_scroll = tk.Scrollbar(text_container, bg="#0d1822")
        lore_scroll.pack(side="right", fill="y")

        lore_text = tk.Text(
            text_container, bg="#080d12", fg="#dceaf4", font=("Consolas", 10),
            wrap="word", padx=14, pady=12, relief="sunken", bd=1,
            yscrollcommand=lore_scroll.set,
        )
        lore_text.pack(side="left", fill="both", expand=True)
        lore_scroll.config(command=lore_text.yview)

        lore_content = (
            "========================================================================================\n"
            "         THE CURSE OF INSECURE PACKETS — NORDIC H2O UTILITY INCIDENT\n"
            "========================================================================================\n\n"
            "1. BAGGRUND: VANDVÆRKET UNDER PRES\n"
            "Nordic H2O Utility er et moderne, men sårbart vandværk, som forsyner 85.000 borgere med\n"
            "rent drikkevand. De seneste uger har SCADA-systemet oplevet uforklarlige trykfald, uautoriseret\n"
            "fjernadgang og mystisk netværkstrafik.\n\n"
            "Nu er Pumpe 2 i akut alarmtilstand (trykket nærmer sig 150 Bar sprængningsgrænsen!), og\n"
            "Miljø- og Cybersikkerhedstilsynet ved Revisor Kirsten har varslet et uanmeldt NIS2-tilsyn.\n"
            "Som nyansat OT-cybersikkerhedskonsulent skal du forhindre fysisk rørbrud, afdække angrebet,\n"
            "og bringe forsyningen i fuld compliance med EU's NIS2-direktiv og standarden IEC 62443.\n\n"
            "----------------------------------------------------------------------------------------\n"
            "2. PURDUE MODELLEN & IEC 62443-3-2 ZONER & CONDUITS\n"
            "Anlæggets OT-arkitektur er opbygget jf. Purdue Enterprise Reference Architecture (PERA):\n"
            "  • Level 0 (Fysisk proces):   Pumper, ventiler, tryktransmittere og flowmålere.\n"
            "  • Level 1 (Styring):         Siemens S7-1200 PLC'er, Danfoss VFD, Festo Ventil-ø.\n"
            "  • Level 2 (Områdestyring):   Lokale HMI touchskærme, SCALANCE managed switches.\n"
            "  • Level 3 (Driftsledelse):   SCADA WinCC servere, historikere, ingeniør-stationer.\n"
            "  • Level 3.5 (IDMZ):          Industriel DMZ med firewalls, jump hosts og PKI Truststore.\n"
            "  • Level 4 (Enterprise):      Kontor-IT, ERP og eksterne leverandør-forbindelser.\n\n"
            "----------------------------------------------------------------------------------------\n"
            "3. NIS2-DIREKTIVET (ARTIKEL 21 & 23)\n"
            "Som væsentlig samfundskritisk forsyning skal Nordic H2O Utility overholde:\n"
            "  • Artikel 21 (Risikostyring): Hærdning, segmentering, kryptering og leverandørstyring.\n"
            "  • Artikel 23 (Hændelsesrapportering):\n"
            "      - 24-timers Early Warning (indberet hændelse til Kirsten før tidsfristen).\n"
            "      - 72-timers detaljeret hændelsesrapport og Chain of Custody bevisintegritet.\n"
            "  • Sanktioner: Bøder på op til 10 mio. EUR eller 2% af den globale koncernomsætning.\n\n"
            "----------------------------------------------------------------------------------------\n"
            "4. DE 4 NØGLEMETRIKKER\n"
            "Dine handlinger har direkte indflydelse på 4 modstridende hensyn:\n"
            "  • 🔧 DRIFT (0-100%):      Vandværkets oppetid. Forkert kabling eller unødige reboots koster drift!\n"
            "  • 🛡️ SIKKERHED (0-100%):  Netværkets modstandsdygtighed (firewalls, OPC UA PKI, segmentering).\n"
            "  • 📜 COMPLIANCE (0-100%): NIS2-dokumentation, bevisintegritet og revisionsoverholdelse.\n"
            "  • 🤝 TILLID (0-100%):     Samarbejdet med driftstekniker Hans McDonald og ledelsen.\n\n"
            "----------------------------------------------------------------------------------------\n"
            "5. EFTERFORSKNING & SAGSTAVLE\n"
            "Undervejs finder du fysiske og digitale spor (f.eks. Rogue Raspberry Pi, 4G dongle, uautoriserede\n"
            "Modbus-skrivninger). Gennemse 'sagstavle', analyser spor med 'analyser spor <id>', beregn SHA256\n"
            "hashes, forsegl beviser i Faraday-poser, og konfronter den sande gerningsmand i Kapitel 5!\n\n"
            "----------------------------------------------------------------------------------------\n"
            "6. GEM, INDLÆS & BETJENING\n"
            "  • Gem undervejs: Klik på '💾 Gem' knappen eller tast 'gem' i terminalen.\n"
            "  • Gå til Hovedmenu: Klik på '🏠 Menu' knappen eller tast 'hovedmenu'.\n"
            "  • Hotspots: Klik direkte på maskiner og DIN-skinner på 2D-skærmen for at inspicere dem.\n"
            "  • Tast valg: Tast [1-9] for at vælge handlinger fra den aktive valgmenu.\n"
        )
        lore_text.insert("1.0", lore_content)
        lore_text.configure(state="disabled")

    def setup_card_exit(self) -> None:
        """Card: Confirmation before quitting the application."""
        card = tk.Frame(self.menu_content_frame, bg="#0d1822", padx=28, pady=30, relief="ridge", bd=1)
        self.cards["exit"] = card

        box = tk.Frame(card, bg="#101c27", padx=24, pady=24, relief="groove", bd=1)
        box.pack(anchor="center", pady=40)

        tk.Label(
            box, text="AFSLUT THE CURSE OF INSECURE PACKETS?",
            bg="#101c27", fg="#f87171", font=("Consolas", 14, "bold"),
        ).pack(pady=(0, 10))

        tk.Label(
            box,
            text="Er du sikker på, at du vil forlade Nordic H2O Utility?\n"
                 "Hvis du har gemt dit spil via '💾 Gem', kan du genoptage din mission når som helst.",
            bg="#101c27", fg="#dceaf4", font=("Segoe UI", 10), justify="center",
        ).pack(pady=(0, 20))

        btn_row = tk.Frame(box, bg="#101c27")
        btn_row.pack()

        tk.Button(
            btn_row, text="❌ Ja, Luk Spillet", bg="#991b1b", fg="#fee2e2",
            font=("Segoe UI", 10, "bold"), relief="raised", padx=16, pady=6,
            command=self.destroy,
        ).pack(side="left", padx=10)

        tk.Button(
            btn_row, text="↩️ Tilbage til Hovedmenu", bg="#16293a", fg="#d8e6ed",
            font=("Segoe UI", 10), relief="groove", padx=16, pady=6,
            command=lambda: self.switch_menu_tab("new_game"),
        ).pack(side="left", padx=10)

    # -------------------------------------------------------------------------
    # MENU NAVIGATION & STATE SWITCHING
    # -------------------------------------------------------------------------
    def show_main_menu(self, tab: str = "new_game") -> None:
        """Switch from gameplay to the atmospheric start screen/main menu."""
        self.gameplay_container.pack_forget()
        self.menu_container.pack(fill="both", expand=True)
        self.switch_menu_tab(tab)
        self.refresh_save_list()

    def show_gameplay(self) -> None:
        """Switch from start screen to the active gameplay cockpit."""
        self.menu_container.pack_forget()
        self.gameplay_container.pack(fill="both", expand=True)

    def switch_menu_tab(self, tab_key: str) -> None:
        """Show the selected card and highlight its tab button."""
        for key, frame in self.cards.items():
            if key == tab_key:
                frame.pack(fill="both", expand=True, padx=20, pady=12)
            else:
                frame.pack_forget()

        for key, btn in self.tab_buttons.items():
            if key == tab_key:
                btn.configure(bg="#0284c7", fg="#ffffff", relief="sunken")
            else:
                btn.configure(bg="#16293a", fg="#94a3b8", relief="raised")

        if tab_key == "load_game":
            self.refresh_save_list()

    # -------------------------------------------------------------------------
    # GAME LAUNCH & PERSISTENCE (SAVE / LOAD)
    # -------------------------------------------------------------------------
    def start_new_game(self, tutorial: bool | None = None) -> None:
        """Start a brand new game session configured from the start screen."""
        name = self.entry_player_name.get().strip() or "Konsulent"
        edu = self.combo_edu_var.get().strip() or "Automationsteknolog"
        mode = self.menu_mode_var.get() or "teach"
        use_tutorial = self.tutorial_var.get() if tutorial is None else tutorial

        self.engine = GameEngine(output=self.write_to_terminal)
        self.engine.auto_print_choices = False
        self.map.engine = self.engine
        self.engine.game_mode = mode

        self.show_gameplay()
        self.terminal.clear()
        self.engine.start(name, edu, tutorial=use_tutorial)
        self.terminal.scroll_to_top()

        self.update_objective()
        self.update_nav_highlight()
        self.update_mode_button()
        self.update_metrics_display()
        self.update_action_buttons()
        self.map.draw()

    def quick_save(self) -> None:
        """Perform in-game quicksave to saves/ directory."""
        ok, msg = self.engine.save_state()
        self.write_to_terminal(msg)

    def prompt_return_to_menu(self) -> None:
        """Autosave current game and return to the start screen/main menu."""
        ok, msg = self.engine.save_state()
        self.write_to_terminal(msg)
        self.write_to_terminal("\n🏠 [HOVEDMENU]: Vender tilbage til startskærmen...")
        self.show_main_menu("new_game")

    def refresh_save_list(self) -> None:
        """Scan saves/ directory and populate the listbox with metadata."""
        self.save_listbox.delete(0, "end")
        self.save_files_meta = self.engine.list_save_files()

        if not self.save_files_meta:
            self.save_details_label.configure(
                text="Ingen gemte spil fundet i 'saves/' mappen.\n\n"
                     "Du kan gemme dit spil undervejs ved at trykke på knappen '💾 Gem' i zonenavigationen "
                     "eller ved at skrive 'gem' i terminalen.",
                fg="#94a3b8",
            )
            return

        for s in self.save_files_meta:
            display_str = f"📁 {s['filename']} — {s['player_name']} (Kap. {s['chapter']}/5, {s['game_mode'].upper()}) [{s['save_time']}]"
            self.save_listbox.insert("end", display_str)

        self.save_listbox.select_set(0)
        self.on_save_selected(None)

    def on_save_selected(self, _event: Any = None) -> None:
        """Display detailed inspection of the selected save file."""
        sel = self.save_listbox.curselection()
        if not sel or sel[0] >= len(self.save_files_meta):
            return
        meta = self.save_files_meta[sel[0]]
        m = meta.get("metrics", {})
        det = (
            f"📄 FILNAVN: {meta['filename']}\n"
            f"⏰ GEMT: {meta['save_time']}\n"
            f"👤 SPILLER: {meta['player_name']} ({meta.get('education', 'Ikke angivet')})\n"
            f"📍 PLACERING: Kapitel {meta['chapter']}/5 — Rum: {meta['room']}\n"
            f"🎓 TILSTAND: {meta['game_mode'].upper()}\n\n"
            f"📊 HOVEDMETRIKKER:\n"
            f"   • 🔧 Drift:       {m.get('drift', '--')}%\n"
            f"   • 🛡️ Sikkerhed:   {m.get('sikkerhed', '--')}%\n"
            f"   • 📜 Compliance:  {m.get('compliance', '--')}%\n"
            f"   • 🤝 Tillid:      {m.get('tillid', '--')}%\n\n"
            f"💾 Gemt i: {meta['filepath']}"
        )
        self.save_details_label.configure(text=det, fg="#dceaf4")

    def load_selected_save(self) -> None:
        """Load the game chosen in the load game listbox."""
        sel = self.save_listbox.curselection()
        if not sel or sel[0] >= len(self.save_files_meta):
            return
        meta = self.save_files_meta[sel[0]]
        self.load_game_file(meta["filepath"])

    def load_game_file(self, filepath: str) -> bool:
        """Load state from a specific JSON file and enter live gameplay."""
        self.engine = GameEngine(output=self.write_to_terminal)
        self.engine.auto_print_choices = False
        self.map.engine = self.engine
        ok, msg = self.engine.load_state(filepath)
        if ok:
            self.show_gameplay()
            self.terminal.clear()
            self.write_to_terminal(msg)
            self.engine.describe_room()
            self.terminal.scroll_to_top()
            self.update_objective()
            self.update_nav_highlight()
            self.update_mode_button()
            self.update_metrics_display()
            self.update_action_buttons()
            self.map.draw()
            return True
        else:
            self.write_to_terminal(f"❌ Fejl ved indlæsning af spil: {msg}")
            return False

    def delete_selected_save(self) -> None:
        """Delete chosen save file from saves/ directory."""
        sel = self.save_listbox.curselection()
        if not sel or sel[0] >= len(self.save_files_meta):
            return
        meta = self.save_files_meta[sel[0]]
        try:
            if os.path.exists(meta["filepath"]):
                os.remove(meta["filepath"])
        except Exception as e:
            print(f"Error deleting save file: {e}")
        self.refresh_save_list()

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

        # Direct menu commands (always available: during gameplay, upon completion, or on game over)
        if normalized.lower() in {
            "hovedmenu", "hovemenu", "menu", "hjem", "home",
            "startskærm", "startskaerm", "afslut til menu", "hoved menu", "main menu"
        }:
            self.show_main_menu()
            return

        # Special command window triggers
        if normalized.lower() in {"hjælp", "help", "?"}:
            self.show_help_window()
            return
        if normalized.lower() in {"guide", "guidance", "nis2 guide"}:
            self.show_guidance_window()
            return

        # Clear terminal before executing the new action so the user never faces a scrolling wall of text
        self.terminal.clear()
        self.terminal.write_line(f"▶ {normalized}", "green_bright")

        # Execute on engine
        self.engine.handle_command(normalized)
        self.terminal.scroll_to_top()

        # Check for menu return signal
        if "return-to-menu" in self.engine.flags:
            self.engine.flags.remove("return-to-menu")
            self.after(500, self.show_main_menu)
            return

        # Synchronize view mode with active workbench or clue board (Keep static 310px height!)
        if normalized.lower() in {"sagstavle", "tavle", "board", "case board", "clueboard", "investigation", "efterforskning"}:
            self.map.view_mode = "clue_board"
            self.sagstavle_btn.configure(text="🚪 Luk Sagstavle", relief="sunken")
        elif self.engine.active_workbench:
            self.map.view_mode = self.engine.active_workbench
        elif normalized.lower() in {"vis rum", "luk workbench", "tilbage", "rum", "forlad workbench", "luk sagstavle"}:
            self.map.view_mode = "room"
            self.sagstavle_btn.configure(relief="raised", text=f"🕵️ Sagstavle ({len(self.engine.investigation.get_discovered_clues())} spor)")
        elif "chapter-1-done" in self.engine.flags and self.map.view_mode == "vfd_workbench":
            self.map.view_mode = "room"
        elif "chapter-2-done" in self.engine.flags and self.map.view_mode == "switch_workbench":
            self.map.view_mode = "room"

        self.terminal.set_prompt_prefix(self.engine.room)
        self.update_mode_button()
        self.update_nav_highlight()
        self.update_objective()
        self.update_metrics_display()
        self.update_action_buttons()
        self.map.draw()

    def toggle_sagstavle(self) -> None:
        if self.map.view_mode == "clue_board":
            self.map.view_mode = "room"
            self.sagstavle_btn.configure(relief="raised", text=f"🕵️ Sagstavle ({len(self.engine.investigation.get_discovered_clues())} spor)")
            self.update_action_buttons()
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
        unanalyzed = len(self.engine.investigation.get_unanalyzed_clues())
        if self.map.view_mode != "clue_board":
            if unanalyzed > 0:
                self.sagstavle_btn.configure(
                    text=f"🕵️ Sagstavle ({num_clues} spor — ⚠️ {unanalyzed} NYE!)",
                    bg="#d97706", fg="#ffffff",
                )
            else:
                self.sagstavle_btn.configure(
                    text=f"🕵️ Sagstavle ({num_clues} spor)",
                    bg="#7c2d12", fg="#fed7aa",
                )

    def toggle_mode(self) -> None:
        self.engine.toggle_game_mode()
        self.update_mode_button()
        self.update_action_buttons()
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
            self.sagstavle_btn.configure(relief="raised", text=f"🕵️ Sagstavle ({len(self.engine.investigation.get_discovered_clues())} spor)")
        self.command(f"gå til {room_key}")

    def on_canvas_click(self, hotspot_name: str) -> None:
        if hotspot_name in {"ts35 din-skinne", "din-skinne", "din skinne"}:
            self.command("firewall workbench")
            return
        self.command(f"undersøg {hotspot_name}")

    def update_action_buttons(self) -> None:
        """Render the current room/state choices as clickable buttons in the Action Panel."""
        for b in self.action_buttons:
            b.destroy()
        self.action_buttons.clear()

        if not self.engine.running:
            btn = tk.Button(
                self.action_grid,
                text="🏠 Vend tilbage til Hovedmenuen",
                bg="#0284c7", fg="white", activebackground="#0369a1",
                font=("Segoe UI", 9, "bold"), anchor="w", padx=10, pady=3,
                command=self.show_main_menu,
            )
            btn.grid(row=0, column=0, columnspan=2, sticky="ew", padx=3, pady=2)
            self.action_buttons.append(btn)
            return

        choices = self.engine.get_current_choices()
        mode_str = "🎓 TEACH MODE (Hans vejleder ved fejl)" if self.engine.game_mode == "teach" else "📝 EKSAMENS-MODE (Ingen hjælp fra Hans)"
        self.action_header_label.configure(
            text=f"⚡ HANDLINGER I ZONEN [{mode_str}] — Klik på en knap herunder eller skriv i terminalen:"
        )

        for idx, (key, label, cmd, _cat) in enumerate(choices[:8]):
            row = idx // 2
            col = idx % 2
            is_nav = cmd.startswith("gå til ") or cmd in {"vis rum", "luk workbench", "spring tutorial over", "sagstavle"}
            btn_bg = "#1e293b" if is_nav else "#132a3e"
            btn_fg = "#bae6fd" if is_nav else "#f8fafc"
            display_lbl = f"[{key}] {label}" if len(label) <= 64 else f"[{key}] {label[:61]}..."
            btn = tk.Button(
                self.action_grid,
                text=display_lbl,
                bg=btn_bg, fg=btn_fg,
                activebackground="#0284c7", activeforeground="white",
                font=("Segoe UI", 8, "bold" if not is_nav else "normal"),
                relief="raised", anchor="w", padx=8, pady=2,
                command=lambda k=key: self.command(k),
            )
            btn.grid(row=row, column=col, sticky="ew", padx=3, pady=2)
            self.action_buttons.append(btn)

    def update_nav_highlight(self) -> None:
        base_labels = {
            "indgangen": "🚪 Indgangen (L4)",
            "pumpehuset": "🚰 Pumpehuset (L1)",
            "ventil-oen": "💨 Ventil-øen (L1)",
            "el-tavlen": "⚡ El-tavlen (L1/L2)",
            "kontrolrummet": "🖥️ Kontrolrummet (IDMZ)",
        }
        chapter_target_room = {
            0: "indgangen",
            1: "pumpehuset",
            2: "ventil-oen",
            3: "el-tavlen",
            4: "kontrolrummet",
            5: "indgangen",
        }.get(self.engine.chapter, "indgangen")
        if getattr(self.engine, "breaker_tripped", False):
            chapter_target_room = "el-tavlen"

        for r_key, btn in self.room_buttons.items():
            lbl = base_labels.get(r_key, r_key)
            is_target = (r_key == chapter_target_room) and self.engine.running
            prefix = "📍 " if is_target else ""
            if r_key == self.engine.room:
                btn.configure(text=f"{prefix}{lbl}", bg="#0284c7", fg="white", relief="sunken")
            elif is_target:
                btn.configure(text=f"{prefix}{lbl}", bg="#1e3a5f", fg="#fde047", relief="raised")
            else:
                btn.configure(text=lbl, bg="#16293a", fg="#d8e6ed", relief="groove")

    def update_objective(self) -> None:
        if not self.engine.running:
            if "case-solved-lars" in self.engine.flags or self.engine.chapter == 5:
                self.objective_banner.configure(
                    text="🎉 MISSION GENNEMFØRT! Rapport er eksporteret. Klik på '🏠 HOVEDMENU' øverst for at vende tilbage.",
                    bg="#065f46", fg="#f0fdf4",
                )
            else:
                self.objective_banner.configure(
                    text="⚠️ MISSIONEN ER AFSLUTTET. Klik på '🏠 HOVEDMENU' øverst for at starte forfra eller hente et gemt spil.",
                    bg="#7f1d1d", fg="#fee2e2",
                )
            return

        if getattr(self.engine, "tutorial_active", False):
            t_step = getattr(self.engine, "tutorial_step", 1)
            step_goals = {
                1: "Trin 1/5: Klik på 'EMALJESKILT' på 2D-skærmen eller tast [1] ('undersøg skilt')",
                2: "Trin 2/5: Sniff netværkstrafik i terminalen ved at taste [1] eller skrive 'tshark'",
                3: "Trin 3/5: Åbn Sagstavlen ved at klikke på '🕵️ Sagstavle' eller taste [1] ('sagstavle')",
                4: "Trin 4/5: Klik på det ⚠️ NYE SPOR på tavlen for at analysere det, og vælg en ⭐ Hovedmistænkt!",
                5: "Trin 5/5: Du er klar! Tast [1] ('afslut tutorial') eller klik på '🚰 Pumpehuset' for at starte missionen!",
            }
            self.objective_banner.configure(
                text=f"🎓 INTRO-TUTORIAL ({step_goals.get(t_step, 'Følg Hans McDonalds instruktioner')}) — [Timer på pause]",
                bg="#0f3d3e", fg="#a7f3d0",
            )
            return

        if self.engine.chapter == 0:
            self.objective_banner.configure(
                text="Ansættelsessamtale i gang",
                bg="#172e42", fg="#dceaf4",
            )
            return
        obj_text = OBJECTIVES.get(self.engine.chapter, "Gennemfør audit")
        self.objective_banner.configure(
            text=f"Aktuelt mål (Kapitel {self.engine.chapter}/5): {obj_text}",
            bg="#172e42", fg="#dceaf4",
        )

    def introduce(self) -> None:
        """Direct introduction sequence (transitions straight into gameplay)."""
        self.show_gameplay()
        self.terminal.clear()
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
        self.update_mode_button()
        self.update_metrics_display()
        self.map.draw()

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
