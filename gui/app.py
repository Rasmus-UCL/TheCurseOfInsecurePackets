"""Main Tkinter Application Cockpit with Start Screen, 2D Visual Map & Integrated Green CRT Terminal."""

from __future__ import annotations

import os
import shutil
import tkinter as tk
from tkinter import filedialog, ttk
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
        """Create a streamlined, professional industrial workstation layout."""
        # 1. Top Header Bar: Station Branding, Mode, Timers & Controls (Clean Slate #081018)
        header = tk.Frame(self.gameplay_container, bg="#081018", padx=10, pady=5, relief="flat", highlightthickness=1, highlightbackground="#172635")
        header.pack(fill="x")

        # Pinned controls at left
        self.btn_hovedmenu = tk.Button(
            header, text="🏠 MENU", bg="#0f2233", fg="#38bdf8", activebackground="#1e3a53",
            activeforeground="#ffffff", font=("Segoe UI", 8, "bold"), relief="groove", bd=1, padx=8, pady=2,
            command=self.prompt_return_to_menu,
        )
        self.btn_hovedmenu.pack(side="left", padx=(0, 4))

        self.btn_quick_save = tk.Button(
            header, text="💾 GEM", bg="#06382b", fg="#34d399", activebackground="#0b5340",
            activeforeground="#ffffff", font=("Segoe UI", 8, "bold"), relief="groove", bd=1, padx=8, pady=2,
            command=self.quick_save,
        )
        self.btn_quick_save.pack(side="left", padx=(0, 10))

        tk.Label(
            header, text="UCL • NORDIC H2O FIELD WORKSTATION",
            bg="#081018", fg="#f1f5f9", font=("Consolas", 11, "bold"),
        ).pack(side="left")

        # Right side status indicators
        self.mode_btn = tk.Label(
            header, text="🔒 Tilstand: TEACH", bg="#064e3b", fg="#6ee7b7",
            font=("Segoe UI", 8, "bold"), relief="ridge", bd=1, padx=8, pady=2,
        )
        self.mode_btn.pack(side="right", padx=4)

        self.support_btn = tk.Button(
            header, text="📞 Support (3/3)", bg="#0e2336", fg="#7dd3fc",
            font=("Segoe UI", 8, "bold"), relief="groove", bd=1, padx=8, pady=1,
            command=lambda: self.command("techsupport"),
        )
        self.support_btn.pack(side="right", padx=4)

        tk.Button(
            header, text="🎯 Guide", bg="#1e293b", fg="#94a3b8",
            font=("Segoe UI", 8, "bold"), relief="groove", bd=1, padx=8, pady=1,
            command=self.show_guidance_window,
        ).pack(side="right", padx=4)

        self.timer_label = tk.Label(
            header, text="Dag 1/5 | 08:00",
            bg="#081018", fg="#f6d365", font=("Consolas", 10, "bold"), padx=6,
        )
        self.timer_label.pack(side="right", padx=4)

        self.acute_label = tk.Label(
            header, text="ℹ️ Anlæg: Aktiv overvågning",
            bg="#081018", fg="#94a3b8", font=("Consolas", 10, "bold"), padx=8,
        )
        self.acute_label.pack(side="right", padx=4)

        # 2. Purdue Navigation & 4-Metrics Control Strip (Collapsed into one high-density strip)
        control_strip = tk.Frame(self.gameplay_container, bg="#0d1622", padx=10, pady=3, relief="flat", highlightthickness=1, highlightbackground="#172635")
        control_strip.pack(fill="x")

        # Purdue Zone buttons
        self.room_buttons: dict[str, tk.Button] = {}
        for title, key in (
            ("🚪 Indgangen (L4)", "indgangen"),
            ("🚰 Pumpehuset (L1)", "pumpehuset"),
            ("💨 Ventil-øen (L1)", "ventil-oen"),
            ("⚡ El-tavlen (L1/L2)", "el-tavlen"),
            ("🖥️ Kontrolrummet (IDMZ)", "kontrolrummet"),
        ):
            b = tk.Button(
                control_strip, text=title, bg="#132130", fg="#cbd5e1", activebackground="#1e344d",
                activeforeground="#ffffff", relief="groove", bd=1, font=("Segoe UI", 8, "bold"), padx=6, pady=2,
                command=lambda k=key: self.navigate_to(k),
            )
            b.pack(side="left", padx=2)
            self.room_buttons[key] = b

        # Assistant Buttons on Right
        self.sagstavle_btn = tk.Button(
            control_strip, text="🕵️ Sagstavle", bg="#451a03", fg="#fdba74",
            activebackground="#7c2d12", font=("Segoe UI", 8, "bold"), relief="groove", bd=1, padx=8, pady=2,
            command=self.toggle_sagstavle,
        )
        self.sagstavle_btn.pack(side="right", padx=3)

        tk.Button(
            control_strip, text="☕ Hans", bg="#3b1f06", fg="#fde68a",
            font=("Segoe UI", 8, "bold"), relief="groove", bd=1, padx=6, pady=2, command=lambda: self.command("tal med hans"),
        ).pack(side="right", padx=2)

        tk.Button(
            control_strip, text="🎒 Rygsæk", bg="#1e293b", fg="#94a3b8",
            font=("Segoe UI", 8, "bold"), relief="groove", bd=1, padx=6, pady=2, command=lambda: self.command("inventory"),
        ).pack(side="right", padx=2)

        # 4 Core Metrics
        self.metric_tillid_label = tk.Label(
            control_strip, text="🤝 Tillid: 50%", bg="#0d1622", fg="#c084fc",
            font=("Consolas", 9, "bold"), padx=4,
        )
        self.metric_tillid_label.pack(side="right")

        self.metric_compliance_label = tk.Label(
            control_strip, text="📜 Comp: 40%", bg="#0d1622", fg="#fbbf24",
            font=("Consolas", 9, "bold"), padx=4,
        )
        self.metric_compliance_label.pack(side="right")

        self.metric_sikkerhed_label = tk.Label(
            control_strip, text="🛡️ Sikkerhed: 25%", bg="#0d1622", fg="#38bdf8",
            font=("Consolas", 9, "bold"), padx=4,
        )
        self.metric_sikkerhed_label.pack(side="right")

        self.metric_drift_label = tk.Label(
            control_strip, text="🔧 Drift: 80%", bg="#0d1622", fg="#4ade80",
            font=("Consolas", 9, "bold"), padx=4,
        )
        self.metric_drift_label.pack(side="right")

        # 3. Compact Objective Strip (1 sleek line)
        self.objective_banner = tk.Label(
            self.gameplay_container, text="AKTUELT MÅL: Undersøg anlægget og stabilisér zonen",
            bg="#060c13", fg="#38bdf8", font=("Consolas", 9, "bold"),
            padx=12, pady=2, anchor="w",
        )
        self.objective_banner.pack(fill="x")

        # 4. Canvas maintained in memory for background and test compatibility (NOT packed on screen)
        self.map = GameCanvas(
            self.gameplay_container,
            self.engine,
            on_hotspot_click=self.on_canvas_click,
            app=self,
            height=310,
        )
        # Middle screen canvas removed per design directive: terminal now receives full vertical space!

        # 4.5. Dedicated Interactive Action Panel (Sleek Technical Toolbar)
        self.action_panel = tk.Frame(self.gameplay_container, bg="#091017", padx=10, pady=6, relief="flat", highlightthickness=1, highlightbackground="#172635")
        self.action_panel.pack(fill="x", expand=False, padx=10, pady=(4, 4))

        self.action_header_label = tk.Label(
            self.action_panel,
            text="⚡ TEKNISK VÆRKTØJSLINJE & INDGREB:",
            bg="#091017", fg="#38bdf8", font=("Consolas", 9, "bold"), anchor="w",
        )
        self.action_header_label.pack(fill="x", pady=(0, 4))

        self.action_grid = tk.Frame(self.action_panel, bg="#091017")
        self.action_grid.pack(fill="x")
        self.action_grid.columnconfigure(0, weight=1, uniform="act_col")
        self.action_grid.columnconfigure(1, weight=1, uniform="act_col")

        # 5. Integrated Engineer Console (Takes all remaining vertical space)
        self.terminal = TerminalWidget(self.gameplay_container, on_command=self.command)
        self.terminal.pack(fill="both", expand=True, padx=10, pady=(2, 6))

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
            ("lore", "📖 OM SPILLET & BAGGRUND"),
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
            text="ℹ️ Du er tilkaldt som OT-cybersikkerhedskonsulent hos Nordic H2O Utility.\n"
                 "Vandværkets produktionszoner rammes af skiftende tekniske cyberangreb, mens Revisor Kirsten "
                 "fra Miljø- og Cybersikkerhedstilsynet har indledt et uanmeldt NIS2-tilsyn med trussel om 10 mio. EUR i bøde.\n"
                 "Hvert nyt spil sammensætter en ny rækkefølge af zoner, angrebstyper og bagmænd!",
            bg="#0a121a", fg="#cbd5e1", font=("Segoe UI", 8),
            justify="left", padx=10, pady=10, relief="sunken", bd=1, wraplength=460,
        )
        info_box.pack(fill="x", pady=(10, 0))

        # --- RIGHT: Mode Selection (Teach vs Exam — Locked once the game starts) ---
        right_col = tk.Frame(split, bg="#101c27", padx=16, pady=16, relief="groove", bd=1)
        right_col.pack(side="right", fill="both", expand=True, padx=(12, 0))

        tk.Label(
            right_col, text="🎯 VÆLG TRÆNINGSTILSTAND (Låses ved spilstart)",
            bg="#101c27", fg="#f6d365", font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        self.menu_mode_var = tk.StringVar(value="teach")

        # Teach Mode Card (Clearly highlighted when selected)
        self.teach_frame = tk.Frame(right_col, bg="#064e3b", padx=12, pady=10, relief="solid", bd=3, cursor="hand2")
        self.teach_frame.pack(fill="x", pady=(0, 10))

        self.teach_header_btn = tk.Button(
            self.teach_frame,
            text="✅ [VALGT] 🎓 Teach Mode (Undervisningstilstand — Anbefalet)",
            bg="#059669", fg="#ffffff", activebackground="#10b981", activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"), relief="flat", anchor="w", padx=8, pady=4, cursor="hand2",
            command=lambda: self.select_menu_mode("teach"),
        )
        self.teach_header_btn.pack(fill="x")

        self.teach_desc_lbl = tk.Label(
            self.teach_frame,
            text="• Ingen spoilers i svarmulighederne — alle valg fremstår som realistiske handlinger.\n"
                 "• Hvis du vælger en farlig procedure, griber Hans McDonald ind og stopper dig.\n"
                 "• Hans forklarer hvorfor det er forkert og henviser til rette procedure jf. NIS2 & IEC 62443.\n"
                 "• Sagstavlen viser mistanke-procenter og antallet af tekniske beviser mod hver mistænkt.",
            bg="#064e3b", fg="#ecfdf5", font=("Segoe UI", 8),
            justify="left", padx=8, pady=4, cursor="hand2",
        )
        self.teach_desc_lbl.pack(anchor="w")

        # Exam Mode Card (Clearly highlighted when selected)
        self.exam_frame = tk.Frame(right_col, bg="#141820", padx=12, pady=10, relief="ridge", bd=1, cursor="hand2")
        self.exam_frame.pack(fill="x", pady=(0, 10))

        self.exam_header_btn = tk.Button(
            self.exam_frame,
            text="⬜ [KLIK FOR AT VÆLGE] 📝 Exam Mode (Eksamenstilstand — Realistisk Test)",
            bg="#1e293b", fg="#cbd5e1", activebackground="#b45309", activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"), relief="flat", anchor="w", padx=8, pady=4, cursor="hand2",
            command=lambda: self.select_menu_mode("exam"),
        )
        self.exam_header_btn.pack(fill="x")

        self.exam_desc_lbl = tk.Label(
            self.exam_frame,
            text="• Hans stopper dig IKKE ved fejlvalg — han kommer kun med en tør bemærkning bagefter.\n"
                 "• Forkerte valg udføres og udløser realistiske driftskonsekvenser og NIS2-bøder.\n"
                 "• Sagstavlen skjuler procent-barer og bevis-tællere: Du skal selv deducere synderen!\n"
                 "• Ideel til eksamensprojekter, certificeringer og selvtest.",
            bg="#141820", fg="#94a3b8", font=("Segoe UI", 8),
            justify="left", padx=8, pady=4, cursor="hand2",
        )
        self.exam_desc_lbl.pack(anchor="w")

        for w in (self.teach_frame, self.teach_desc_lbl):
            w.bind("<Button-1>", lambda _e: self.select_menu_mode("teach"))
        for w in (self.exam_frame, self.exam_desc_lbl):
            w.bind("<Button-1>", lambda _e: self.select_menu_mode("exam"))

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

    def select_menu_mode(self, mode: str) -> None:
        """Visually highlight the chosen training mode (Teach vs Exam) on the Start Screen."""
        self.menu_mode_var.set(mode)
        if mode == "teach":
            self.teach_frame.configure(bg="#064e3b", relief="solid", bd=3)
            self.teach_header_btn.configure(
                text="✅ [VALGT] 🎓 Teach Mode (Undervisningstilstand — Anbefalet)",
                bg="#059669", fg="#ffffff",
            )
            self.teach_desc_lbl.configure(bg="#064e3b", fg="#ecfdf5")

            self.exam_frame.configure(bg="#141820", relief="ridge", bd=1)
            self.exam_header_btn.configure(
                text="⬜ [KLIK FOR AT VÆLGE] 📝 Exam Mode (Eksamenstilstand — Realistisk Test)",
                bg="#1e293b", fg="#cbd5e1",
            )
            self.exam_desc_lbl.configure(bg="#141820", fg="#94a3b8")
        else:
            self.exam_frame.configure(bg="#78350f", relief="solid", bd=3)
            self.exam_header_btn.configure(
                text="✅ [VALGT] 📝 Exam Mode (Eksamenstilstand — Realistisk Test)",
                bg="#d97706", fg="#ffffff",
            )
            self.exam_desc_lbl.configure(bg="#78350f", fg="#fef3c7")

            self.teach_frame.configure(bg="#141820", relief="ridge", bd=1)
            self.teach_header_btn.configure(
                text="⬜ [KLIK FOR AT VÆLGE] 🎓 Teach Mode (Undervisningstilstand — Anbefalet)",
                bg="#1e293b", fg="#cbd5e1",
            )
            self.teach_desc_lbl.configure(bg="#141820", fg="#94a3b8")

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
        """Card: Game background story, dynamic mission pack, Purdue architecture, and NIS2."""
        card = tk.Frame(self.menu_content_frame, bg="#0d1822", padx=28, pady=20, relief="ridge", bd=1)
        self.cards["lore"] = card

        tk.Label(
            card, text="OM SPILLET & BAGGRUNDSHISTORIE",
            bg="#0d1822", fg="#f6d365", font=("Consolas", 14, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            card, text="Baggrundshistorie, Dynamisk Missionspack, Purdue Model, NIS2 Direktivet og betjening.",
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
            "1. BAGGRUND: VANDVÆRKET UNDER PRES & UANMELDT NIS2-TILSYN\n"
            "Nordic H2O Utility er et kommunalt vandværk, som forsyner 85.000 borgere med rent drikkevand.\n"
            "Anlægget oplever pludselige driftsforstyrrelser, manipulerede styresignaler og uautoriseret\n"
            "netværkstrafik på tværs af produktionszonerne.\n\n"
            "Samtidig har Miljø- og Cybersikkerhedstilsynet ved chefinspektør Revisor Kirsten indledt et\n"
            "NIS2-tilsyn med en stram 5-dages tidsfrist. Som tilkaldt OT-cybersikkerhedskonsulent skal du\n"
            "samarbejde med senior driftstekniker Hans McDonald om at lokalisere og standse angrebene,\n"
            "sikre de tekniske beviser, udpege gerningsmanden og bestå den afsluttende NIS2-revision!\n\n"
            "----------------------------------------------------------------------------------------\n"
            "2. DYNAMISK MISSIONSPACK (NY UDFORDRING HVER GANG DU SPILLER)\n"
            "Spillet genererer automatisk et nyt kampagnescenarie ved hvert nyt spil:\n"
            "  • Tilfældig zonerækkefølge: Rækkefølgen af de 4 produktionszoner udtrækkes dynamisk,\n"
            "    mens Kapitel 5 (fremlæggelse og NIS2-audit hos Revisor Kirsten) altid er finalen.\n"
            "  • 12 forskellige OT-angrebsscenarier (3 varianter A/B/C pr. zone): Du kan møde alt fra\n"
            "    Modbus TCP, SNMPv1/ARP-spoofing, HTTP Web-API overrides, PROFINET DCP, 802.1Q VLAN-tags,\n"
            "    MQTT-broer, S7comm PUT/GET, F-Safety OB35 watchdogs, NTP-spoofing til 4G/Wi-Fi/RDP-bagdøre.\n"
            "  • 4 mulige bagmænd: De tekniske og fysiske spor på Sagstavlen tilpasser sig dynamisk\n"
            "    rundens sande gerningsmand — du kan aldrig gætte synderen uden at analysere sporene!\n\n"
            "----------------------------------------------------------------------------------------\n"
            "3. PURDUE MODELLEN & IEC 62443-3-2 ZONER & CONDUITS\n"
            "Anlæggets OT-arkitektur er opbygget jf. Purdue Enterprise Reference Architecture (PERA):\n"
            "  • Level 0 (Fysisk proces):   Pumper, ventiler, tryktransmittere og flowmålere.\n"
            "  • Level 1 (Styring):         Siemens S7-1500 PLC'er, SINAMICS VFD, Festo Ventil-ø.\n"
            "  • Level 2 (Områdestyring):   Lokale HMI skærme, SCALANCE managed switches & S615 firewalls.\n"
            "  • Level 3 (Driftsledelse):   SCADA WinCC servere, historikere og ingeniør-stationer.\n"
            "  • Level 3.5 (IDMZ):          Industriel DMZ med firewalls, OPC UA og X.509 PKI Truststore.\n"
            "  • Level 4 (Enterprise):      Hovedindgangen, administration og eksterne forbindelser.\n\n"
            "----------------------------------------------------------------------------------------\n"
            "4. NIS2-DIREKTIVET (ARTIKEL 21 & 23 — 24-TIMERS REGLEN)\n"
            "Som væsentlig samfundskritisk forsyning skal Nordic H2O Utility overholde:\n"
            "  • Artikel 21 (Risikostyring): Netværkssegmentering, PLC-backups, kryptering og adgangskontrol.\n"
            "  • Artikel 23 (24-timers Hændelsesindberetning):\n"
            "      - Når du har løst den første væsentlige cyberhændelse, skal du indsende 24-timers Early\n"
            "        Warning til Revisor Kirsten inden fristen udløber (senest Dag 2)!\n"
            "      - Pas på: Efterfølgende del-fund under samme angreb skal logges internt til 72-timers\n"
            "        rapporten — hvis du spammer Kirsten med dublet-alarmer, bliver hun utilfreds!\n\n"
            "----------------------------------------------------------------------------------------\n"
            "5. DE 4 NØGLEMETRIKKER & SAGSTAVLEN\n"
            "  • 🔧 DRIFT (0-100%):      Vandværkets oppetid. Undgå panik-nedlukninger og blind port-blokering!\n"
            "  • 🛡️ SIKKERHED (0-100%):  Netværkets modstandsdygtighed (DPI-firewalls, MRP, OPC UA PKI).\n"
            "  • 📜 COMPLIANCE (0-100%): NIS2-dokumentation, Faraday-bevissikring og Artikel 23-indberetning.\n"
            "  • 🤝 TILLID (0-100%):     Samarbejdet med driftstekniker Hans McDonald og Tilsynet.\n"
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
    def start_new_game(self, tutorial: bool | None = None, randomize: bool = True) -> None:
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
        self.engine.start(name, edu, tutorial=use_tutorial, randomize=randomize)
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

        # Open formatted UCL & NIS2 Report Window when audit completes or report is requested
        if "show-report-window" in self.engine.flags:
            self.engine.flags.remove("show-report-window")
            self.after(200, self.show_audit_report_window)

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
        """Mode is locked during active gameplay (chosen only from the Start Menu)."""
        self.write_to_terminal(
            f"\n🔒 [TILSTAND LÅST]: Spillet kører i {self.engine.game_mode.upper()} mode. "
            "For at sikre en retvisende evaluering kan tilstanden kun vælges fra Startmenuen inden spilstart."
        )

    def set_game_mode(self, mode: str) -> None:
        """Programmatic setter for mode (used by Start Menu and testing)."""
        self.engine.game_mode = mode
        self.update_mode_button()
        self.update_action_buttons()
        self.update_metrics_display()

    def update_mode_button(self) -> None:
        if self.engine.game_mode == "teach":
            self.mode_btn.configure(
                text="🔒 Tilstand: TEACH",
                bg="#065f46",
                fg="#a7f3d0",
            )
        else:
            self.mode_btn.configure(
                text="🔒 Tilstand: EKSAMEN",
                bg="#854d0e",
                fg="#fef08a",
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
        mode_str = "TEACH MODE (Hans vejleder)" if self.engine.game_mode == "teach" else "EKSAMEN (Blind test)"
        self.action_header_label.configure(
            text=f"⚡ TEKNISK VÆRKTØJSLINJE [{mode_str}] — Klik eller tast tal/kommando i terminalen:"
        )

        for idx, (key, label, cmd, _cat) in enumerate(choices[:8]):
            row = idx // 2
            col = idx % 2
            is_nav = cmd.startswith("gå til ") or cmd in {"vis rum", "luk workbench", "spring tutorial over", "sagstavle"}
            btn_bg = "#111c28" if is_nav else "#162536"
            btn_fg = "#93c5fd" if is_nav else "#f1f5f9"
            display_lbl = f"[{key}] {label}" if len(label) <= 66 else f"[{key}] {label[:63]}..."
            btn = tk.Button(
                self.action_grid,
                text=display_lbl,
                bg=btn_bg, fg=btn_fg,
                activebackground="#0284c7", activeforeground="white",
                font=("Segoe UI", 8, "bold" if not is_nav else "normal"),
                relief="groove", bd=1, anchor="w", padx=8, pady=3,
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
        chapter_target_room = self.engine.get_current_target_room()
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
                btn.configure(text=lbl, bg="#132130", fg="#cbd5e1", relief="groove")

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
                1: "Trin 1/5: Vælg [1] 'Undersøg skilt' i værktøjslinjen eller tast '1'",
                2: "Trin 2/5: Sniff netværkstrafik i terminalen ved at taste [1] eller skrive 'tshark'",
                3: "Trin 3/5: Åbn Sagstavlen ved at klikke på '🕵️ Sagstavle' eller taste [1] ('sagstavle')",
                4: "Trin 4/5: Klik på det ⚠️ NYE SPOR på tavlen for at analysere det, og vælg en ⭐ Hovedmistænkt!",
                5: "Trin 5/5: Du er klar! Tast [1] ('afslut tutorial') for at starte missionen!",
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
        obj_text = self.engine.get_current_objective_text()
        self.objective_banner.configure(
            text=f"Aktuelt mål: {obj_text}",
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
        elif self.engine.chapter >= 5:
            self.acute_label.configure(text="✅ Alle 4 produktionszoner er sikret — Fremlæg Sagstavle", fg="#4ade80")
        else:
            nis2_text, nis2_color = self.engine.incident.get_incident_status_line(
                self.engine.simulated_day, self.engine.simulated_hour
            )
            self.acute_label.configure(text=nis2_text, fg=nis2_color)

        remaining_support = self.engine.max_help_calls - self.engine.help_calls
        self.support_btn.configure(
            text=f"📞 TechSupport ({remaining_support}/{self.engine.max_help_calls})",
            bg="#0284c7" if remaining_support > 0 else "#334155",
        )

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

    def _find_ucl_logo_path(self) -> str | None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [
            os.path.join(base_dir, "ucl_logo.png"),
            os.path.join(base_dir, "assets", "ucl_logo.png"),
            os.path.join(base_dir, "logo.png"),
        ]
        for path in candidates:
            if os.path.isfile(path):
                return path
        return None

    def _render_ucl_header_logo(self, container: tk.Frame) -> None:
        for child in container.winfo_children():
            child.destroy()

        logo_path = self._find_ucl_logo_path()
        if logo_path:
            try:
                img = tk.PhotoImage(file=logo_path)
                # Downscale smoothly if the image is very wide/tall
                w, h = img.width(), img.height()
                if h > 72:
                    factor = max(1, int(round(h / 60)))
                    img = img.subsample(factor, factor)
                self._ucl_logo_img_ref = img  # keep reference alive
                lbl = tk.Label(container, image=img, bg="#00454e", bd=0)
                lbl.pack(side="left", padx=(4, 12), pady=4)
                return
            except Exception:
                pass

        # Built-in crisp UCL vector badge if no PNG file is provided yet
        logo_canvas = tk.Canvas(
            container, width=155, height=58, bg="#00454e", highlightthickness=0
        )
        logo_canvas.pack(side="left", padx=(4, 12), pady=4)
        logo_canvas.create_rectangle(2, 2, 153, 56, fill="#00353c", outline="#4fd1c5", width=2)
        logo_canvas.create_text(
            48, 29, text="UCL", fill="#ffffff", font=("Segoe UI", 22, "bold")
        )
        logo_canvas.create_line(86, 10, 86, 48, fill="#4fd1c5", width=1)
        logo_canvas.create_text(
            92, 20, text="Erhvervsakademi", fill="#b2f5ea", font=("Segoe UI", 7, "bold"), anchor="w"
        )
        logo_canvas.create_text(
            92, 31, text="og Professions-", fill="#b2f5ea", font=("Segoe UI", 7), anchor="w"
        )
        logo_canvas.create_text(
            92, 42, text="højskole", fill="#b2f5ea", font=("Segoe UI", 7), anchor="w"
        )

    def _choose_ucl_logo_file(self, logo_container: tk.Frame, parent_win: tk.Toplevel) -> None:
        chosen = filedialog.askopenfilename(
            parent=parent_win,
            title="Vælg UCL-logo (.png eller .gif)",
            filetypes=[("PNG/GIF Billeder", "*.png *.gif"), ("Alle filer", "*.*")],
        )
        if not chosen:
            return
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        target = os.path.join(base_dir, "ucl_logo.png")
        try:
            if os.path.abspath(chosen) != os.path.abspath(target):
                shutil.copyfile(chosen, target)
            self._render_ucl_header_logo(logo_container)
        except Exception as exc:
            self.write_to_terminal(f"⚠️ Kunne ikke indlæse logo-fil: {exc}")

    def _build_html_report(self, report_md: str) -> str:
        import base64
        import html
        import re

        logo_html = (
            '<div style="display:inline-block;padding:8px 16px;background:#00353c;'
            'border:2px solid #4fd1c5;border-radius:6px;color:#fff;font-weight:bold;'
            'font-size:24px;letter-spacing:1px;">UCL '
            '<span style="font-size:11px;font-weight:normal;color:#b2f5ea;display:inline-block;'
            'border-left:1px solid #4fd1c5;padding-left:8px;margin-left:6px;vertical-align:middle;">'
            'Erhvervsakademi og<br>Professionshøjskole</span></div>'
        )
        logo_path = self._find_ucl_logo_path()
        if logo_path and os.path.isfile(logo_path):
            try:
                with open(logo_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                logo_html = f'<img src="data:image/png;base64,{b64}" alt="UCL Logo" style="max-height:64px;" />'
            except Exception:
                pass

        def inline_fmt(text: str) -> str:
            # Inline formatting for bold, italics, backticks
            escaped = html.escape(text)
            escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            escaped = re.sub(r"\*(.+?)\*", r"<em>\1</em>", escaped)
            escaped = re.sub(
                r"`(.+?)`",
                r'<code style="background:#f1f5f9;color:#0f5257;padding:2px 6px;border-radius:4px;font-family:Consolas,monospace;">\1</code>',
                escaped,
            )
            return escaped

        lines_html: list[str] = []
        in_table = False
        table_rows: list[str] = []

        def flush_table() -> None:
            nonlocal in_table, table_rows
            if table_rows:
                lines_html.append('<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:13px;">')
                for idx, r in enumerate(table_rows):
                    cols = [c.strip() for c in r.strip().strip("|").split("|")]
                    if idx == 0:
                        lines_html.append('<tr style="background:#00454e;color:#ffffff;font-weight:bold;">')
                        for c in cols:
                            lines_html.append(f'<th style="border:1px solid #cbd5e1;padding:8px 10px;text-align:left;">{inline_fmt(c)}</th>')
                        lines_html.append('</tr>')
                    elif idx == 1 and all(set(c) <= set("-: ") for c in cols):
                        continue
                    else:
                        bg = "#ffffff" if idx % 2 == 0 else "#f8fafc"
                        lines_html.append(f'<tr style="background:{bg};">')
                        for c in cols:
                            lines_html.append(f'<border style="display:none;"></border><td style="border:1px solid #cbd5e1;padding:7px 10px;">{inline_fmt(c)}</td>')
                        lines_html.append('</tr>')
                lines_html.append('</table>')
                table_rows = []
            in_table = False

        for raw_line in report_md.splitlines():
            line_s = raw_line.strip()
            if line_s.startswith("|") and line_s.endswith("|"):
                in_table = True
                table_rows.append(line_s)
                continue
            elif in_table:
                flush_table()

            if raw_line.startswith("# "):
                lines_html.append(f'<h1 style="color:#00454e;border-bottom:3px solid #00454e;padding-bottom:6px;margin-top:20px;font-size:22px;">{inline_fmt(raw_line[2:])}</h1>')
            elif raw_line.startswith("## "):
                lines_html.append(f'<h2 style="color:#0f5257;border-bottom:1px solid #e2e8f0;padding-bottom:4px;margin-top:18px;margin-bottom:8px;font-size:17px;">{inline_fmt(raw_line[3:])}</h2>')
            elif raw_line.startswith("### "):
                lines_html.append(f'<h3 style="color:#134e4a;margin-top:14px;margin-bottom:6px;font-size:15px;">{inline_fmt(raw_line[4:])}</h3>')
            elif raw_line.startswith("> "):
                lines_html.append(
                    f'<blockquote style="background:#f0fdf4;border-left:4px solid #0d9488;margin:10px 0;padding:10px 16px;border-radius:4px;font-style:italic;color:#134e4a;">'
                    f'{inline_fmt(raw_line[2:])}</blockquote>'
                )
            elif raw_line.startswith("- "):
                content = raw_line[2:]
                if content.startswith("✅"):
                    lines_html.append(f'<li style="margin:5px 0;color:#166534;">{inline_fmt(content)}</li>')
                elif content.startswith("❌"):
                    lines_html.append(f'<li style="margin:5px 0;color:#991b1b;">{inline_fmt(content)}</li>')
                elif content.startswith("⚠️"):
                    lines_html.append(f'<li style="margin:5px 0;color:#854d0e;">{inline_fmt(content)}</li>')
                else:
                    lines_html.append(f'<li style="margin:4px 0;">{inline_fmt(content)}</li>')
            elif not line_s:
                lines_html.append("<br/>")
            else:
                lines_html.append(f"<p style='margin:4px 0;'>{inline_fmt(raw_line)}</p>")

        if in_table:
            flush_table()

        grade_code = getattr(self.engine, "last_audit_grade", "12")
        score = getattr(self.engine, "last_audit_score", 100)
        passed = getattr(self.engine, "last_audit_passed", True)

        badge_color = "#047857" if passed else "#b91c1c"
        badge_title = f"BESTÅET — Karakter {grade_code} ({score}/100 point)" if passed else f"IKKE BESTÅET — Karakter {grade_code} ({score}/100 point)"

        body_content = "\n".join(lines_html)
        return f"""<!DOCTYPE html>
<html lang="da">
<head>
<meta charset="utf-8" />
<title>NIS2 &amp; IEC 62443 Revisionsrapport - {html.escape(self.engine.player.name)}</title>
<style>
  @media print {{
    body {{ background: #ffffff !important; padding: 0 !important; }}
    .page {{ box-shadow: none !important; border: none !important; max-width: 100% !important; }}
    .banner {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .no-print {{ display: none !important; }}
  }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #e2e8f0; margin: 0; padding: 24px; color: #1e293b; }}
  .page {{ max-width: 860px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 6px 24px rgba(0,0,0,0.12); }}
  .banner {{ background: #00454e; color: #ffffff; padding: 20px 28px; display: flex; align-items: center; justify-content: space-between; border-bottom: 4px solid #4fd1c5; }}
  .badge-bar {{ background: {badge_color}; color: #ffffff; padding: 8px 28px; font-weight: bold; font-size: 14px; letter-spacing: 0.5px; text-align: right; }}
  .content {{ padding: 28px 36px; line-height: 1.6; font-size: 14px; }}
  .footer {{ background: #f8fafc; color: #64748b; padding: 14px 36px; font-size: 12px; border-top: 1px solid #cbd5e1; text-align: right; }}
</style>
</head>
<body>
  <div class="page">
    <div class="banner">
      <div>{logo_html}</div>
      <div style="text-align:right;">
        <div style="font-size:16px;font-weight:bold;color:#e6fffa;">OT-SIKKERHED &amp; INDUSTRIELLE NETVÆRK</div>
        <div style="font-size:12px;color:#b2f5ea;">Officiel NIS2 (EU 2022/2555) &amp; IEC 62443 Revisionsrapport &amp; Eksamensbilag</div>
      </div>
    </div>
    <div class="badge-bar">
      🎓 EKSAMENSRESULTAT: {badge_title}
    </div>
    <div class="content">
      {body_content}
    </div>
    <div class="footer">
      Dokument genereret i The Curse of Insecure Packets — Erhvervsakademi og Professionshøjskole UCL
    </div>
  </div>
</body>
</html>
"""

    def show_audit_report_window(self) -> None:
        if not getattr(self.engine, "last_report_markdown", ""):
            self.engine.export_audit_report()
            self.engine.flags.discard("show-report-window")

        report_md = self.engine.last_report_markdown
        window = tk.Toplevel(self)
        window.title("Officiel NIS2 & IEC 62443 Revisionsrapport — UCL")
        window.geometry("880x740")
        window.minsize(800, 640)
        window.configure(bg="#0b1520")
        window.transient(self)

        # Top UCL Header Banner (#00454e)
        banner = tk.Frame(window, bg="#00454e", padx=18, pady=12, highlightthickness=1, highlightbackground="#4fd1c5")
        banner.pack(fill="x", padx=14, pady=(14, 8))

        logo_container = tk.Frame(banner, bg="#00454e")
        logo_container.pack(side="left")
        self._render_ucl_header_logo(logo_container)

        title_box = tk.Frame(banner, bg="#00454e")
        title_box.pack(side="left", fill="x", expand=True, padx=10)
        tk.Label(
            title_box,
            text="OFFICIEL NIS2 & IEC 62443 REVISIONSRAPPORT",
            bg="#00454e", fg="#ffffff", font=("Segoe UI", 14, "bold"), anchor="w",
        ).pack(fill="x")
        tk.Label(
            title_box,
            text=(
                f"Valgfag: OT-Sikkerhed & Industrielle Netværk  |  "
                f"Konsulent: {self.engine.player.name}  |  "
                f"Tilstand: {'EKSAMEN (Blind Test)' if self.engine.game_mode == 'exam' else 'TEACH MODE'}"
            ),
            bg="#00454e", fg="#b2f5ea", font=("Segoe UI", 9, "bold"), anchor="w",
        ).pack(fill="x", pady=(2, 0))

        passed = getattr(self.engine, "last_audit_passed", True)
        score = getattr(self.engine, "last_audit_score", 100)
        grade_code = getattr(self.engine, "last_audit_grade", "12")
        badge_bg = "#065f46" if passed else "#7f1d1d"
        badge_fg = "#6ee7b7" if passed else "#fca5a5"
        badge_txt = f"✅ BESTÅET (Karakter {grade_code} • {score}p)" if passed else f"❌ DUMPET (Karakter {grade_code} • {score}p)"
        tk.Label(
            banner, text=badge_txt, bg=badge_bg, fg=badge_fg,
            font=("Segoe UI", 11, "bold"), padx=12, pady=8, relief="flat",
        ).pack(side="right", padx=4)

        # Document Viewer Frame
        doc_frame = tk.Frame(window, bg="#101e2b", highlightthickness=1, highlightbackground="#294866")
        doc_frame.pack(fill="both", expand=True, padx=14, pady=6)

        scrollbar = tk.Scrollbar(doc_frame)
        scrollbar.pack(side="right", fill="y")

        txt = tk.Text(
            doc_frame,
            bg="#0d1822",
            fg="#e2e8f0",
            font=("Consolas", 10),
            wrap="word",
            padx=22,
            pady=18,
            yscrollcommand=scrollbar.set,
            relief="flat",
            spacing1=2,
            spacing3=2,
        )
        txt.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=txt.yview)

        txt.tag_configure("h1", font=("Segoe UI", 14, "bold"), foreground="#4fd1c5", spacing1=8, spacing3=6)
        txt.tag_configure("h2", font=("Segoe UI", 11, "bold"), foreground="#f6d365", spacing1=10, spacing3=4)
        txt.tag_configure("table", font=("Consolas", 10, "bold"), foreground="#93c5fd")
        txt.tag_configure("good", font=("Consolas", 10), foreground="#4ade80")
        txt.tag_configure("bad", font=("Consolas", 10), foreground="#f87171")
        txt.tag_configure("body", font=("Consolas", 10), foreground="#dceaf4")

        for line in report_md.splitlines():
            if line.startswith("# "):
                txt.insert("end", line[2:] + "\n", "h1")
            elif line.startswith("## "):
                txt.insert("end", line[3:] + "\n", "h2")
            elif line.strip().startswith("|"):
                txt.insert("end", line + "\n", "table")
            elif "✅" in line or "BESTÅET" in line or "Rettidig" in line:
                txt.insert("end", line + "\n", "good")
            elif "❌" in line or "⚠️" in line or "DUMPET" in line or "Kirsten" in line and "sur" in line.lower():
                txt.insert("end", line + "\n", "bad")
            else:
                txt.insert("end", line + "\n", "body")

        txt.configure(state="disabled")

        # Bottom Action Bar
        btn_bar = tk.Frame(window, bg="#0b1520")
        btn_bar.pack(fill="x", padx=14, pady=(6, 14))

        status_var = tk.StringVar(value="💡 Tip: Du kan gemme rapporten som print-klar HTML (med UCL-logo) eller Markdown/Tekst.")
        status_lbl = tk.Label(
            btn_bar, textvariable=status_var, bg="#0b1520", fg="#94a3b8", font=("Segoe UI", 9)
        )
        status_lbl.pack(side="left", padx=4)

        def save_to_computer() -> None:
            safe_name = "".join(
                c if c.isalnum() or c in ("-", "_") else "_" for c in self.engine.player.name
            ).strip("_") or "konsulent"
            default_file = f"NIS2_Revisionsrapport_{safe_name}.html"
            filepath = filedialog.asksaveasfilename(
                parent=window,
                title="Gem NIS2 & IEC 62443 Revisionsrapport på computeren",
                initialfile=default_file,
                defaultextension=".html",
                filetypes=[
                    ("HTML Rapport med UCL-logo (.html)", "*.html"),
                    ("Markdown Dokument (.md)", "*.md"),
                    ("Tekstfil (.txt)", "*.txt"),
                ],
            )
            if not filepath:
                return
            try:
                if filepath.lower().endswith(".html"):
                    content = self._build_html_report(report_md)
                else:
                    content = report_md
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                status_var.set(f"✅ Rapport gemt: {filepath}")
                status_lbl.configure(fg="#4ade80")
            except Exception as exc:
                status_var.set(f"❌ Fejl ved gemning: {exc}")
                status_lbl.configure(fg="#f87171")

        tk.Button(
            btn_bar,
            text="Luk vindue",
            bg="#1e293b",
            fg="#e2e8f0",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=window.destroy,
        ).pack(side="right", padx=4)

        tk.Button(
            btn_bar,
            text="🖼️ Vælg UCL-Logo (.png)",
            bg="#1b3348",
            fg="#7dd3fc",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=lambda: self._choose_ucl_logo_file(logo_container, window),
        ).pack(side="right", padx=6)

        tk.Button(
            btn_bar,
            text="💾 Gem Rapport på Computeren (.html / .md / .txt)",
            bg="#059669",
            fg="#ffffff",
            activebackground="#047857",
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=save_to_computer,
        ).pack(side="right", padx=6)

