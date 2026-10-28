"""Dedicated 2D visual plant floor screen & interactive workbenches (Wireshark moves to Terminal)."""

from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Callable
from typing import Any

from rooms import ALL_ROOMS


class GameCanvas(tk.Canvas):
    """Clickable 2D retro-industrial room map & in-canvas workbenches."""

    def __init__(self, master_app: Any, engine: Any, on_hotspot_click: Any, app: Any = None, **kwargs: object) -> None:
        super().__init__(master_app, bg="#0d1821", highlightthickness=1, highlightbackground="#1f364d", **kwargs)
        self.master_app = app if app is not None else master_app
        self.engine = engine
        self.on_hotspot_click = on_hotspot_click

        self.view_mode: str = "room"  # "room", "vfd_workbench", "switch_workbench", "clue_board"
        self.selected_hotspot: str | None = None
        self.selected_clue_id: str | None = None
        self.hovered_hotspot: str | None = None
        self.hotspot_rects: dict[str, tuple[int, int, int, int]] = {}
        self.canvas_buttons: dict[str, tuple[int, int, int, int, Callable[[], None]]] = {}

        # Workbench state
        self.vfd_step: int = 0
        self.switch_step: int = 0
        self.anim_tick: int = 0

        self.bind("<Button-1>", self.on_click)
        self.bind("<Motion>", self.on_motion)
        self.bind("<Leave>", lambda _e: self.clear_hover())
        self.start_animation()

    def start_animation(self) -> None:
        self.anim_tick = (self.anim_tick + 1) % 100
        if self.view_mode == "room" and self.engine.room in {"pumpehuset", "ventil-oen", "el-tavlen", "kontrolrummet"}:
            self.draw()
        elif self.view_mode in {"vfd_workbench", "switch_workbench", "clue_board"}:
            self.draw()
        if self.winfo_exists():
            self.after(350, self.start_animation)

    def on_click(self, event: tk.Event[tk.Misc]) -> None:
        x, y = event.x, event.y
        for _btn_id, (bx1, by1, bx2, by2, callback) in self.canvas_buttons.items():
            if bx1 <= x <= bx2 and by1 <= y <= by2:
                callback()
                return

        for name, (rx1, ry1, rx2, ry2) in self.hotspot_rects.items():
            if rx1 <= x <= rx2 and ry1 <= y <= ry2:
                if self.view_mode == "room":
                    self.select_hotspot(name)
                    return
                elif self.view_mode == "vfd_workbench":
                    self.on_vfd_workbench_click(name)
                    return
                elif self.view_mode == "switch_workbench":
                    self.on_switch_workbench_click(name)
                    return

    def on_motion(self, event: tk.Event[tk.Misc]) -> None:
        x, y = event.x, event.y
        new_hover: str | None = None
        for name, (rx1, ry1, rx2, ry2) in self.hotspot_rects.items():
            if rx1 <= x <= rx2 and ry1 <= y <= ry2:
                new_hover = name
                break

        if new_hover != self.hovered_hotspot:
            self.hovered_hotspot = new_hover
            self.draw()

    def clear_hover(self) -> None:
        if self.hovered_hotspot is not None:
            self.hovered_hotspot = None
            self.draw()

    def select_hotspot(self, name: str) -> None:
        self.selected_hotspot = name
        self.draw()
        if self.on_hotspot_click:
            self.on_hotspot_click(name)

    def close_hud(self) -> None:
        self.selected_hotspot = None
        self.draw()

    def _trigger_command(self, cmd: str) -> None:
        """Safely dispatch a command through GameApp (or fallback to GameEngine)."""
        self.selected_hotspot = None
        if hasattr(self.master_app, "command"):
            self.master_app.command(cmd)
        else:
            self.engine.handle_command(cmd)
            self.draw()

    def _on_clue_card_click(self, cid: str) -> None:
        """Analyze a clicked clue card on the Sagstavle and show its details immediately."""
        self.selected_clue_id = cid
        self._trigger_command(f"analyser spor {cid}")

    def draw(self) -> None:
        self.delete("all")
        self.hotspot_rects.clear()
        self.canvas_buttons.clear()

        # Synchronize workbench steps with engine flags
        if "chapter-1-done" in self.engine.flags:
            self.vfd_step = 3
        if "chapter-2-done" in self.engine.flags:
            self.switch_step = 3
        elif "pi-removed" in self.engine.flags and self.switch_step == 0:
            self.switch_step = 1

        w_actual = self.winfo_width()
        h_actual = self.winfo_height()
        width = w_actual if w_actual > 100 else 840
        height = h_actual if h_actual > 100 else 310

        if self.view_mode == "room":
            self.draw_room(width, height)
            if self.selected_hotspot:
                self.draw_equipment_hud(width, height)
        elif self.view_mode == "vfd_workbench":
            self.draw_vfd_workbench(width, height)
        elif self.view_mode == "switch_workbench":
            self.draw_switch_workbench(width, height)
        elif self.view_mode == "clue_board":
            self.draw_clue_board(width, height)

    # -------------------------------------------------------------------------
    # 1. PLANT FLOOR ROOM VIEW RENDERING
    # -------------------------------------------------------------------------
    def draw_room(self, width: int, height: int) -> None:
        current_room = ALL_ROOMS.get(self.engine.room, ALL_ROOMS["indgangen"])

        # Industrial Grating Backdrop
        self.create_rectangle(0, 0, width, height, fill="#0d1821", outline="")
        for gy in range(65, height, 40):
            self.create_line(0, gy, width, gy, fill="#122332", width=1)
        for gx in range(0, width, 45):
            self.create_line(gx, 65, gx, height, fill="#122332", width=1)

        # Overhead Cable Tray & Header
        self.create_rectangle(0, 0, width, 58, fill="#162736", outline="#25425c", width=1)
        for hx in range(0, width, 28):
            self.create_polygon(hx, 0, hx + 12, 0, hx + 4, 10, hx - 8, 10, fill="#f6d365", outline="")
            self.create_polygon(hx + 12, 0, hx + 24, 0, hx + 16, 10, hx + 4, 10, fill="#162736", outline="")

        self.create_text(
            20, 16, anchor="nw",
            text=f"ZONE: {current_room.title.upper()} | {current_room.purdue_level.upper()}",
            fill="#f6d365", font=("Consolas", 13, "bold"),
        )
        self.create_text(
            20, 36, anchor="nw",
            text=f"Topologi: {current_room.zone}  |  Krav: IEC 62443 SL-2  |  Klik en komponent for inspektion",
            fill="#9cbcd4", font=("Segoe UI", 9),
        )

        # Quick Workbench Action Button on Canvas
        if self.engine.room == "pumpehuset" and "chapter-1-done" not in self.engine.flags:
            btn_w = 230
            btn_x1 = width - btn_w - 20
            btn_y1 = 12
            btn_x2 = width - 20
            btn_y2 = 44
            self.create_rectangle(btn_x1, btn_y1, btn_x2, btn_y2, fill="#0284c7", outline="#38bdf8", width=2)
            self.create_text((btn_x1 + btn_x2) // 2, (btn_y1 + btn_y2) // 2, text="🔧 Åbn DIN-Skinne Montage", fill="white", font=("Segoe UI", 9, "bold"))
            self.canvas_buttons["pumpe_top_wb"] = (btn_x1, btn_y1, btn_x2, btn_y2, lambda: self.master_app.command("firewall workbench"))
        elif self.engine.room == "ventil-oen" and "chapter-2-done" not in self.engine.flags and "pi-removed" in self.engine.flags:
            btn_w = 230
            btn_x1 = width - btn_w - 20
            btn_y1 = 12
            btn_x2 = width - 20
            btn_y2 = 44
            self.create_rectangle(btn_x1, btn_y1, btn_x2, btn_y2, fill="#0284c7", outline="#38bdf8", width=2)
            self.create_text((btn_x1 + btn_x2) // 2, (btn_y1 + btn_y2) // 2, text="🔧 Åbn Switch Montage", fill="white", font=("Segoe UI", 9, "bold"))
            self.canvas_buttons["switch_top_wb"] = (btn_x1, btn_y1, btn_x2, btn_y2, lambda: self.master_app.command("switch workbench"))

        self.draw_room_background(width, height)

        # Visible hotspots (Filtered so Rogue Pi is hidden until found)
        hotspots = current_room.get_visible_hotspots(self.engine)
        count = len(hotspots)
        if count == 0:
            return

        cols = min(4, count)
        card_w = min(220, (width - 50 - (cols - 1) * 16) // cols)
        card_h = 125 if not self.selected_hotspot else 110
        start_y = 75

        for idx, name in enumerate(hotspots):
            col = idx % cols
            row = idx // cols
            x1 = 25 + col * (card_w + 16)
            y1 = start_y + row * (card_h + 16)
            x2 = x1 + card_w
            y2 = y1 + card_h
            self.hotspot_rects[name] = (x1, y1, x2, y2)
            self.draw_hotspot_card(name, x1, y1, x2, y2, is_hovered=(name == self.hovered_hotspot), is_selected=(name == self.selected_hotspot))

        if not self.selected_hotspot:
            footer_y = height - 24
            self.create_rectangle(0, footer_y, width, height, fill="#0a1219", outline="#1c3347", width=1)
            hover_info = f"▶ PEGER PÅ: [{self.hovered_hotspot.upper()}] - Klik for detaljer" if self.hovered_hotspot else "▶ RUM-STATUS: Vælg en komponent ovenfor eller skriv kommandoer i terminalen"
            self.create_text(20, footer_y + 4, anchor="nw", text=hover_info, fill="#64d8cb", font=("Consolas", 9, "bold"))

    def draw_room_background(self, width: int, height: int) -> None:
        r = self.engine.room
        if r == "pumpehuset":
            pipe_y = 205
            c1_done = "chapter-1-done" in self.engine.flags
            pipe_color = "#2b5c73" if c1_done else "#852b2b"
            self.create_rectangle(10, pipe_y - 10, width - 10, pipe_y + 10, fill=pipe_color, outline="#1b3a4a", width=2)
            self.create_text(width - 150, pipe_y - 18, text="HOVED-RØR 16 BAR / DN150", fill="#a1c4d9", font=("Consolas", 8))

            # Dynamic water hammer shockwaves in pipe under Modbus sabotage
            if not c1_done:
                wave_offset = (self.anim_tick * 14) % 80
                for wx in range(15 + wave_offset, width - 20, 80):
                    self.create_line(wx, pipe_y - 7, wx + 12, pipe_y + 7, fill="#ef4444", width=3)

            # Steel TS35 DIN-rail in Pumpehuset (Clickable directly on screen!)
            rail_y = 135
            self.create_rectangle(15, rail_y - 8, width - 15, rail_y + 8, fill="#334155", outline="#64748b", width=1)
            for sx in range(25, width - 25, 30):
                self.create_line(sx, rail_y - 4, sx, rail_y + 4, fill="#475569", width=2)
            self.create_text(25, rail_y - 18, anchor="nw", text="TS35 DIN-SKINNE FELT (KLIK FOR AT ÅBNE ARBEJDSBÆNK)", fill="#f6d365", font=("Consolas", 8, "bold"))
            self.canvas_buttons["pumpe_din_rail"] = (15, rail_y - 18, width - 15, rail_y + 12, lambda: self.master_app.command("firewall workbench"))
        elif r == "ventil-oen":
            tube_y = 210
            self.create_line(15, tube_y, width - 15, tube_y, fill="#3b7a99", width=4, dash=(6, 3))
            self.create_line(15, tube_y + 14, width - 15, tube_y + 14, fill="#2b5c73", width=3)
            # Animated DCP packet pulses along PROFINET bus when not done
            if "chapter-2-done" not in self.engine.flags:
                pulse_x = 25 + (self.anim_tick * 25) % (width - 50)
                self.create_oval(pulse_x - 6, tube_y - 4, pulse_x + 6, tube_y + 8, fill="#38bdf8", outline="white")
        elif r == "el-tavlen":
            rail_y = 200
            self.create_rectangle(15, rail_y - 8, width - 15, rail_y + 8, fill="#52606d", outline="#8295a5", width=2)
            self.create_text(width - 160, rail_y - 18, text="35mm DIN-SKINNE TS35", fill="#8295a5", font=("Consolas", 8))
        elif r == "kontrolrummet":
            self.create_rectangle(20, 70, width - 20, height - 35, fill="", outline="#1f425f", width=1, dash=(4, 4))
            if "router-disconnected" not in self.engine.flags:
                # Cellular wave arcs from 4G router towards top right
                rx = width - 120
                ry = 120
                arc_r = 15 + (self.anim_tick % 4) * 8
                self.create_arc(rx - arc_r, ry - arc_r, rx + arc_r, ry + arc_r, start=30, extent=120, outline="#38bdf8", width=2, style="arc")

    def draw_hotspot_card(self, name: str, x1: int, y1: int, x2: int, y2: int, is_hovered: bool, is_selected: bool) -> None:
        flags = self.engine.flags

        # Show Don't Tell: Physical hydraulic vibration on Pumpe 2 under sabotage
        if name == "pumpe 2" and "chapter-1-done" not in flags and not getattr(self.engine, "scada_blind", False):
            jx = int(2.5 * math.sin(self.anim_tick * 1.8))
            jy = int(1.5 * math.cos(self.anim_tick * 2.2))
            x1 += jx
            x2 += jx
            y1 += jy
            y2 += jy
            self.hotspot_rects[name] = (x1, y1, x2, y2)

        card_bg = "#23415c" if is_selected else ("#1b354b" if is_hovered else "#132535")
        border_color = "#38bdf8" if is_selected else ("#f6d365" if is_hovered else "#2a4d6c")
        border_width = 3 if (is_selected or is_hovered) else 1

        if getattr(self.engine, "scada_blind", False) and name in {"pumpe 2", "scada"}:
            card_bg = "#26132b" if self.anim_tick % 2 == 0 else "#1c0d20"
            border_color = "#c084fc"
            border_width = 3

        self.create_rectangle(x1, y1, x2, y2, fill=card_bg, outline=border_color, width=border_width)

        badge_text = "NORMAL"
        badge_color = "#4ade80"
        icon_type = "⚙️ KOMPONENT"
        sub_info = ""

        if name == "pumpe 2":
            icon_type = "🚰 CENTRIFUGALPUMPE"
            if getattr(self.engine, "scada_blind", False):
                badge_text = "TRYK UKENDT (TIMEOUT)"
                badge_color = "#ef4444"
                sub_info = "Mangler FC 03 allow!"
            elif "chapter-1-done" in flags:
                badge_text = "42 BAR (OK)"
                badge_color = "#4ade80"
                sub_info = "Stabil drift"
            else:
                pulsing = "#ef4444" if self.anim_tick % 2 == 0 else "#f87171"
                badge_text = "146.5 BAR (VIBRATION!)"
                badge_color = pulsing
                sub_info = "Modbus sabotage aktiv!"
                badge_text = "146.5 BAR (ALARM)"
                badge_color = pulsing
                sub_info = "Modbus sabotage aktiv!"
        elif name in {"ts35 din-skinne", "din-skinne"}:
            icon_type = "🔧 MONTAGEFELT"
            if "chapter-1-done" in flags:
                badge_text = "FIREWALL MONTERET"
                badge_color = "#4ade80"
                sub_info = "SCALANCE S615 aktiv"
            elif getattr(self.engine, "vfd_cabled", False):
                badge_text = "KABLET (MANGLER DPI)"
                badge_color = "#f59e0b"
                sub_info = "DPI mangler"
            elif getattr(self.engine, "vfd_mounted", False):
                badge_text = "MONTERET PÅ TS35"
                badge_color = "#38bdf8"
                sub_info = "Mangler RJ45 kabling"
            else:
                badge_text = "KLAR TIL MONTAGE"
                badge_color = "#38bdf8"
                sub_info = "Klik for at åbne"
        elif name == "scada":
            icon_type = "🖥️ WINCC SCADA HMI"
            if getattr(self.engine, "scada_blind", False):
                badge_text = "TIMEOUT / COMM ERROR"
                badge_color = "#ef4444"
                sub_info = "FC 03 mangler allow-regel!"
            elif "chapter-1-done" in flags:
                badge_text = "OVERVÅGNING OK"
                badge_color = "#4ade80"
                sub_info = "Pumpe 2 telemetri OK"
            else:
                badge_text = "ALARM INDIKATION"
                badge_color = "#f59e0b"
                sub_info = "Overvåger Port 502"
        elif name == "frekvensomformer":
            icon_type = "⚡ VFD DRIVER"
            if getattr(self.engine, "breaker_tripped", False):
                badge_text = "STRØMLØS (K1)"
                badge_color = "#ef4444"
                sub_info = "Relæ K1 udløst!"
            elif "chapter-1-done" in flags:
                badge_text = "DPI FIREWALL (OK)"
                badge_color = "#4ade80"
                sub_info = "VLAN 10 isoleret"
            else:
                badge_text = "REG 0x0000=1337"
                badge_color = "#f59e0b"
                sub_info = "Port 502 ubeskyttet"
        elif name == "kabelbakke":
            icon_type = "📦 KABELTRÆK"
            badge_text = "MISTÆNKELIG"
            badge_color = "#f59e0b"
            sub_info = "Optapet sort boks fundet!"
        elif name == "rogue raspberry pi":
            icon_type = "⚠️ ROGUE HARDWARE"
            if "pi-removed" in flags:
                badge_text = "KONFISKERET"
                badge_color = "#38bdf8"
                sub_info = "Sikret i Faraday-pose"
            else:
                badge_text = "MAC: B8:27:EB"
                badge_color = "#ef4444"
                sub_info = "DCP spoofing aktiv!"
        elif name == "ventiler":
            icon_type = "💨 FESTO VENTIL-Ø"
            if "chapter-2-done" in flags:
                badge_text = "DETERMINISTISK"
                badge_color = "#4ade80"
                sub_info = "PROFINET RT synkron"
            else:
                pulsing_state = "OPEN (KAOS)" if self.anim_tick % 2 == 0 else "CLOSE (OSCILLERER)"
                badge_text = pulsing_state
                badge_color = "#ef4444" if self.anim_tick % 2 == 0 else "#f87171"
                sub_info = "DCP broadcast storm!"
        elif name in {"s7-1500", "s7", "plc"}:
            icon_type = "🛡️ SIKKERHEDS-PLC"
            if getattr(self.engine, "plc_defect_stop", False):
                badge_text = "DEFECTIVE STOP"
                badge_color = "#ef4444" if self.anim_tick % 2 == 0 else "#fbbf24"
                sub_info = "Fejlkode 0x4542 - DB1 korrupt"
            elif "chapter-3-done" in flags:
                badge_text = "RUN MODE"
                badge_color = "#4ade80"
                sub_info = "Protection Level 3 aktiv"
            else:
                blinking_stop = "#ef4444" if self.anim_tick % 2 == 0 else "#7f1d1d"
                badge_text = "STOP DIODE BLINKER"
                badge_color = blinking_stop
                sub_info = "S7comm port 102"
        elif name in {"4g-router", "router", "4g"}:
            icon_type = "📡 ROGUE UPLINK"
            if "router-disconnected" in flags:
                badge_text = "FRAKOBLET"
                badge_color = "#4ade80"
                sub_info = "IDMZ sikret"
            else:
                pulse_4g = "#38bdf8" if self.anim_tick % 2 == 0 else "#f59e0b"
                badge_text = "((( AKTIV TUNNEL )))"
                badge_color = pulse_4g
                sub_info = "Teltonika RUT950 lækker"
        elif name == "opc ua server":
            icon_type = "🔒 OPC UA GATEWAY"
            if "chapter-4-done" in flags:
                badge_text = "BASIC256SHA256"
                badge_color = "#4ade80"
                sub_info = "Certifikater betroet"
            else:
                badge_text = "SECURITY: NONE"
                badge_color = "#f59e0b"
                sub_info = "Lækker opskriftdata"

        self.create_text(x1 + 8, y1 + 10, anchor="nw", text=icon_type, fill="#7ea2be", font=("Consolas", 8, "bold"))
        self.create_text(x1 + 8, y1 + 25, anchor="nw", text=name.title(), fill="white", font=("Segoe UI", 11, "bold"))

        pill_w = len(badge_text) * 7 + 10
        pill_x1 = x1 + 8
        pill_y1 = y1 + 50
        pill_x2 = min(x2 - 8, pill_x1 + pill_w)
        pill_y2 = pill_y1 + 18
        self.create_rectangle(pill_x1, pill_y1, pill_x2, pill_y2, fill="#0a1520", outline=badge_color, width=1)
        self.create_text(pill_x1 + 4, pill_y1 + 2, anchor="nw", text=badge_text, fill=badge_color, font=("Consolas", 8, "bold"))

        if sub_info:
            self.create_text(x1 + 8, y1 + 75, anchor="nw", text=sub_info, fill="#a5c4d8", font=("Segoe UI", 8))

        hint_action = "▶ Valgt" if is_selected else "Klik for handling"
        self.create_text(x2 - 8, y2 - 8, anchor="se", text=hint_action, fill="#38bdf8" if is_selected else "#507899", font=("Segoe UI", 7))

    # -------------------------------------------------------------------------
    # 2. EQUIPMENT INSPECTION HUD OVERLAY
    # -------------------------------------------------------------------------
    def draw_equipment_hud(self, width: int, height: int) -> None:
        if not self.selected_hotspot:
            return

        name = self.selected_hotspot
        hud_h = 135
        hx1 = 16
        hy1 = height - hud_h - 10
        hx2 = width - 16
        hy2 = height - 10

        self.create_rectangle(hx1, hy1, hx2, hy2, fill="#0f1f2e", outline="#38bdf8", width=2)
        self.create_rectangle(hx1, hy1, hx2, hy1 + 24, fill="#162e45", outline="")

        self.create_text(
            hx1 + 12, hy1 + 5, anchor="nw",
            text=f"🔍 INSPEKTION: {name.upper()}",
            fill="#f6d365", font=("Consolas", 10, "bold"),
        )

        close_x1, close_x2 = hx2 - 32, hx2 - 8
        self.create_rectangle(close_x1, hy1 + 2, close_x2, hy1 + 22, fill="#7f1d1d", outline="#ef4444", width=1)
        self.create_text(close_x1 + 7, hy1 + 4, anchor="nw", text="✕", fill="white", font=("Segoe UI", 9, "bold"))
        self.canvas_buttons["hud_close"] = (close_x1, hy1 + 2, close_x2, hy1 + 22, self.close_hud)

        desc = f"Undersøger komponenten '{name}'. Brug terminalen eller knapperne herunder."
        if name == "pumpe 2":
            desc = "Centrifugalpumpe med kavitetsfare. Manometeret vibrerer voldsomt og kavitetsgrænsen truer!"
        elif name == "kabelbakke":
            desc = "Sort optapet boks fundet under kabelbakken. Mistænkeligt Cat6-kabel fører ind i switchen."
        elif name in {"frekvensomformer", "ts35 din-skinne", "din-skinne"}:
            desc = "SINAMICS G120 & TS35 DIN-skinne. Modtager Modbus TCP på port 502. Skal isoleres med SCALANCE S615 DPI."
        elif name in {"switch", "d-link switch"}:
            desc = "D-Link DES-1008D unmanaged switch. Mangler VLAN-segmentering og MRP redundant ring."
        elif name == "rogue raspberry pi":
            desc = "Rogue Raspberry Pi fundet tapet under kabelbakken! Udsender uautoriserede PROFINET DCP-pakker."

        self.create_text(hx1 + 14, hy1 + 30, anchor="nw", text=desc, fill="#e2e8f0", font=("Segoe UI", 9))

        # Interactive Action Buttons inside HUD
        btn_y1 = hy1 + 58
        btn_y2 = hy1 + 88
        btn_x = hx1 + 14

        # Button 1: TS35 DIN-Skinne Workbench (Pumpehuset)
        if name in {"frekvensomformer", "ts35 din-skinne", "din-skinne"} or (self.engine.room == "pumpehuset" and "chapter-1-done" not in self.engine.flags):
            bw = 250
            self.create_rectangle(btn_x, btn_y1, btn_x + bw, btn_y2, fill="#0284c7", outline="#38bdf8", width=2)
            self.create_text(btn_x + bw // 2, (btn_y1 + btn_y2) // 2, text="🔧 Åbn DIN-Skinne Montage", fill="white", font=("Segoe UI", 9, "bold"))
            self.canvas_buttons["hud_open_vfd"] = (btn_x, btn_y1, btn_x + bw, btn_y2, lambda: self._trigger_command("firewall workbench"))
            btn_x += bw + 12

        # Button 2: Switch Workbench (Ventil-øen)
        if name in {"switch", "d-link switch"} or (self.engine.room == "ventil-oen" and "chapter-2-done" not in self.engine.flags and "pi-removed" in self.engine.flags):
            bw = 240
            self.create_rectangle(btn_x, btn_y1, btn_x + bw, btn_y2, fill="#0284c7", outline="#38bdf8", width=2)
            self.create_text(btn_x + bw // 2, (btn_y1 + btn_y2) // 2, text="🔧 Åbn Switch Montage Bænk", fill="white", font=("Segoe UI", 9, "bold"))
            self.canvas_buttons["hud_open_switch"] = (btn_x, btn_y1, btn_x + bw, btn_y2, lambda: self._trigger_command("switch workbench"))
            btn_x += bw + 12

        # Button 3: Reveal Pi in cable tray
        if name == "kabelbakke" and "pi-revealed" not in self.engine.flags:
            bw = 250
            self.create_rectangle(btn_x, btn_y1, btn_x + bw, btn_y2, fill="#b45309", outline="#f59e0b", width=2)
            self.create_text(btn_x + bw // 2, (btn_y1 + btn_y2) // 2, text="🔦 Undersøg Kabelbakke Nøje", fill="white", font=("Segoe UI", 9, "bold"))
            self.canvas_buttons["hud_kabelbakke"] = (btn_x, btn_y1, btn_x + bw, btn_y2, lambda: self._trigger_command("undersøg kabelbakke"))
            btn_x += bw + 12

        # Button 4: Faraday Bag on Rogue Pi
        if name == "rogue raspberry pi" and "pi-removed" not in self.engine.flags:
            bw = 250
            self.create_rectangle(btn_x, btn_y1, btn_x + bw, btn_y2, fill="#15803d", outline="#4ade80", width=2)
            self.create_text(btn_x + bw // 2, (btn_y1 + btn_y2) // 2, text="🛡️ Sikr Pi i Faraday-pose", fill="white", font=("Segoe UI", 9, "bold"))
            self.canvas_buttons["hud_faraday"] = (btn_x, btn_y1, btn_x + bw, btn_y2, lambda: self._trigger_command("sikr pi i faraday-pose"))
            btn_x += bw + 12

        # Button: tshark on all hotspots
        ws_bw = 180
        self.create_rectangle(btn_x, btn_y1, btn_x + ws_bw, btn_y2, fill="#162c3d", outline="#38bdf8", width=1)
        self.create_text(btn_x + ws_bw // 2, (btn_y1 + btn_y2) // 2, text="📊 Kør tshark CLI", fill="#e0f2fe", font=("Segoe UI", 9, "bold"))
        self.canvas_buttons["hud_wireshark"] = (btn_x, btn_y1, btn_x + ws_bw, btn_y2, lambda: self._trigger_command("tshark -Y \"modbus\"" if self.engine.room == "pumpehuset" else "tshark"))

        self.create_text(hx1 + 14, hy1 + 105, anchor="nw", text="💡 TIP: Klik på handlingsknapperne under kortet eller brug kommandolinjen.", fill="#38bdf8", font=("Segoe UI", 8, "italic"))

    # -------------------------------------------------------------------------
    # 3. WORKBENCHES (CHAPTER 1 & 2)
    # -------------------------------------------------------------------------
    def draw_vfd_workbench(self, w: int, h: int) -> None:
        self.create_rectangle(0, 0, w, h, fill="#0b141e", outline="")
        self.create_text(20, 16, anchor="nw", text="TS35 DIN-SKINNE ARBEJDSBÆNK: SCALANCE S615 FIREWALL MONTAGE", fill="#f6d365", font=("Consolas", 11, "bold"))

        # Close / Return button
        btn_w = 200
        self.create_rectangle(w - btn_w - 20, 10, w - 20, 38, fill="#162c3d", outline="#38bdf8", width=1)
        self.create_text(w - btn_w // 2 - 20, 24, text="⬅️ Tilbage til Pumpehuset", fill="#e0f2fe", font=("Segoe UI", 9, "bold"))
        self.hotspot_rects["close_vfd_workbench"] = (w - btn_w - 20, 10, w - 20, 38)

        # Steel DIN rail TS35
        rail_y = 150
        self.create_rectangle(15, rail_y - 12, w - 15, rail_y + 12, fill="#334155", outline="#94a3b8", width=2)
        for sx in range(25, w - 25, 40):
            self.create_line(sx, rail_y - 6, sx, rail_y + 6, fill="#64748b", width=3)
        self.create_text(30, rail_y - 24, anchor="nw", text="35mm STÅL DIN-SKINNE (EN 60715 TS35)", fill="#94a3b8", font=("Consolas", 8, "bold"))

        is_mounted = getattr(self.engine, "vfd_mounted", False) or self.vfd_step >= 1
        is_cabled = getattr(self.engine, "vfd_cabled", False)
        is_wrong = getattr(self.engine, "wrong_cabling", False)
        is_done = "chapter-1-done" in self.engine.flags

        # Slot 1: Montage
        c1_x1, c1_y1, c1_x2, c1_y2 = 40, 75, 260, 245
        if not is_mounted:
            self.create_rectangle(c1_x1, c1_y1, c1_x2, c1_y2, fill="#0f1f2e", outline="#38bdf8", width=2, dash=(6, 3))
            self.create_text(c1_x1 + 15, c1_y1 + 25, anchor="nw", text="TRIN 1: FYSISK MONTAGE\n\n[ KLIK FOR AT MONTERE ]\nFastgør SCALANCE S615\npå TS35 DIN-skinnen", fill="#38bdf8", font=("Segoe UI", 9, "bold"))
            self.hotspot_rects["vfd_mount"] = (c1_x1, c1_y1, c1_x2, c1_y2)
        else:
            self.create_rectangle(c1_x1, c1_y1, c1_x2, c1_y2, fill="#092233", outline="#22c55e", width=2)
            self.create_text(c1_x1 + 15, c1_y1 + 15, anchor="nw", text="SIEMENS SCALANCE S615\nINDUSTRIEL ROUTER", fill="#f8fafc", font=("Segoe UI", 9, "bold"))
            self.create_text(c1_x1 + 15, c1_y1 + 60, anchor="nw", text="Status: Monteret på TS35\nJordforbindelse: OK (PE)\n24V DC forsyning: Aktiv", fill="#4ade80", font=("Consolas", 8))

        # Slot 2: RJ45 Kabling
        c2_x1, c2_y1, c2_x2, c2_y2 = 280, 75, 500, 245
        if not is_mounted:
            self.create_rectangle(c2_x1, c2_y1, c2_x2, c2_y2, fill="#090e14", outline="#334155", width=1)
            self.create_text(c2_x1 + 15, c2_y1 + 50, anchor="nw", text="TRIN 2: RJ45 KABLING\n(Kræver montage først)", fill="#64748b", font=("Segoe UI", 9))
        elif is_wrong:
            self.create_rectangle(c2_x1, c2_y1, c2_x2, c2_y2, fill="#2b1414", outline="#ef4444", width=2)
            self.create_text(c2_x1 + 10, c2_y1 + 15, anchor="nw", text="⚠️ FORKERT KABLING!\nVFD i WAN i stedet for LAN!\n\n[ KLIK FOR AT RETTE ]\nByt om på portene", fill="#f87171", font=("Segoe UI", 9, "bold"))
            self.hotspot_rects["vfd_cable"] = (c2_x1, c2_y1, c2_x2, c2_y2)
        elif not is_cabled:
            self.create_rectangle(c2_x1, c2_y1, c2_x2, c2_y2, fill="#0f1f2e", outline="#38bdf8", width=2, dash=(6, 3))
            self.create_text(c2_x1 + 15, c2_y1 + 25, anchor="nw", text="TRIN 2: RJ45 KABLING\n\n[ KLIK FOR AT KOBLE ]\nVFD -> LAN P1\nAnlæg -> WAN P5", fill="#38bdf8", font=("Segoe UI", 9, "bold"))
            self.hotspot_rects["vfd_cable"] = (c2_x1, c2_y1, c2_x2, c2_y2)
        else:
            self.create_rectangle(c2_x1, c2_y1, c2_x2, c2_y2, fill="#092233", outline="#22c55e", width=2)
            self.create_text(c2_x1 + 15, c2_y1 + 15, anchor="nw", text="RJ45 PORT STATUS (OK)", fill="#f8fafc", font=("Segoe UI", 9, "bold"))
            self.create_text(c2_x1 + 15, c2_y1 + 50, anchor="nw", text="LAN P1 (VFD): 10.20.1.20\nWAN P5 (SCADA): 10.20.1.5\nLink: 100 Mbps Full Duplex\nIsolering: Level 1 Conduit OK", fill="#4ade80", font=("Consolas", 8))

        # Slot 3: Modbus DPI
        c3_x1, c3_y1, c3_x2, c3_y2 = 520, 75, 740, 245
        mode = getattr(self.engine, "game_mode", "teach")
        is_scada_blind = getattr(self.engine, "scada_blind", False)

        if not is_cabled or is_wrong:
            self.create_rectangle(c3_x1, c3_y1, c3_x2, c3_y2, fill="#090e14", outline="#334155", width=1)
            self.create_text(c3_x1 + 15, c3_y1 + 50, anchor="nw", text="TRIN 3: MODBUS DPI\n(Kræver korrekt kabling)", fill="#64748b", font=("Segoe UI", 9))
        elif is_scada_blind:
            self.create_rectangle(c3_x1, c3_y1, c3_x2, c3_y2, fill="#2b1414", outline="#ef4444", width=2)
            self.create_text(c3_x1 + 10, c3_y1 + 15, anchor="nw", text="🚨 SCADA BLIND (TIMEOUT)!\nFC 06 er blokeret, men du mangler\nat tillade FC 03 (Læsning)!\n\n[ KLIK FOR AT TILLADE FC 03 ]", fill="#f87171", font=("Segoe UI", 8, "bold"))
            self.hotspot_rects["vfd_dpi"] = (c3_x1, c3_y1, c3_x2, c3_y2)
        elif not is_done:
            self.create_rectangle(c3_x1, c3_y1, c3_x2, c3_y2, fill="#0b2942", outline="#38bdf8", width=2, dash=(6, 3))
            s3_text = "TRIN 3: MODBUS DPI REGEL\n\n[ KLIK FOR AT AKTIVERE ]\nTillad FC 03 (Læsning)\nDrop FC 06/16 (Skrivning)"
            self.create_text(c3_x1 + 15, c3_y1 + 20, anchor="nw", text=s3_text, fill="#38bdf8", font=("Segoe UI", 8, "bold"))
            self.hotspot_rects["vfd_dpi"] = (c3_x1, c3_y1, c3_x2, c3_y2)
        else:
            self.create_rectangle(c3_x1, c3_y1, c3_x2, c3_y2, fill="#063220", outline="#22c55e", width=2)
            self.create_text(c3_x1 + 15, c3_y1 + 15, anchor="nw", text="MODBUS DPI REGELSÆT AKTIVT", fill="#f8fafc", font=("Segoe UI", 9, "bold"))
            self.create_text(c3_x1 + 15, c3_y1 + 50, anchor="nw", text="Filter: Deep Packet Inspection\nFC 03: ACCEPT (SCADA OK)\nFC 06: DROP & LOG\nPumpe 2 Tryk: 42.0 Bar (STABIL)", fill="#4ade80", font=("Consolas", 8))

        # Slot 4: Alternativ konfiguration
        c4_x1, c4_y1, c4_x2, c4_y2 = 760, 75, 960, 245
        self.create_rectangle(c4_x1, c4_y1, c4_x2, c4_y2, fill="#1c1917", outline="#78716c", width=1)
        if not is_done and not is_scada_blind and is_cabled:
            self.create_text(c4_x1 + 12, c4_y1 + 20, anchor="nw", text="ALTERNATIV REGEL:\n\n[ KUN DROP FC 06 ]\nOpret blokering af FC 06\nuden FC 03 undtagelse", fill="#fbbf24", font=("Segoe UI", 8, "bold"))
            self.hotspot_rects["vfd_test_forget_fc3"] = (c4_x1, c4_y1, c4_x2, c4_y2)
        else:
            self.create_text(c4_x1 + 12, c4_y1 + 20, anchor="nw", text="ALTERNATIV KABLING:\n\n[ BYT OM PÅ WAN/LAN ]\nForbind VFD til WAN P5\nog switchen til LAN P1", fill="#fbbf24", font=("Segoe UI", 8, "bold"))
            self.hotspot_rects["vfd_wrong_cable"] = (c4_x1, c4_y1, c4_x2, c4_y2)

        footer_y = h - 26
        self.create_rectangle(0, footer_y, w, h, fill="#081018", outline="#1c3347", width=1)
        self.create_text(20, footer_y + 4, anchor="nw", text="▶ Klik på trinene foroven, brug tshark/firewall CLI i terminalen, eller klik 'Tilbage' for at vende tilbage.", fill="#f6d365", font=("Consolas", 9, "bold"))

    def draw_switch_workbench(self, w: int, h: int) -> None:
        self.create_rectangle(0, 0, w, h, fill="#0b141e", outline="")
        self.create_text(20, 16, anchor="nw", text="FELTBUS ARBEJDSBÆNK: SCALANCE XB-200 MANAGED SWITCH & MRP-RING", fill="#f6d365", font=("Consolas", 11, "bold"))

        # Close / Return button
        btn_w = 200
        self.create_rectangle(w - btn_w - 20, 10, w - 20, 38, fill="#162c3d", outline="#38bdf8", width=1)
        self.create_text(w - btn_w // 2 - 20, 24, text="⬅️ Tilbage til Ventil-øen", fill="#e0f2fe", font=("Segoe UI", 9, "bold"))
        self.hotspot_rects["close_switch_workbench"] = (w - btn_w - 20, 10, w - 20, 38)

        rail_y = 150
        self.create_rectangle(15, rail_y - 12, w - 15, rail_y + 12, fill="#475569", outline="#94a3b8", width=2)

        s_x1, s_y1 = 60, 80
        s_x2, s_y2 = 360, 240
        if "chapter-2-done" in self.engine.flags:
            self.create_rectangle(s_x1, s_y1, s_x2, s_y2, fill="#0f2b3c", outline="#22c55e", width=2)
            self.create_text(s_x1 + 15, s_y1 + 15, anchor="nw", text="SCALANCE XB-200 (MANAGED)\nMRP RING: AKTIV (DETERMINISTISK)", fill="#4ade80", font=("Segoe UI", 9, "bold"))
            self.create_text(s_x1 + 15, s_y1 + 65, anchor="nw", text="Port 1-2: MRP Redundant Ring\nPort 3-8: Sikrede feldbus-porte\nPort Security: MAC Sticky aktiv", fill="#f8fafc", font=("Consolas", 8))
        else:
            self.create_rectangle(s_x1, s_y1, s_x2, s_y2, fill="#2b1414", outline="#ef4444", width=2)
            self.create_text(s_x1 + 15, s_y1 + 15, anchor="nw", text="D-LINK DES-1008D (UNMANAGED)\nBROADCAST-STORM AKTIV!", fill="#f87171", font=("Segoe UI", 9, "bold"))
            self.create_text(s_x1 + 15, s_y1 + 65, anchor="nw", text="Ingen VLAN-segmentering\nIngen MRP-ring redundancy\nUbeskyttet mod rogue DCP-spoofing", fill="#cbd5e1", font=("Consolas", 8))

        footer_y = h - 26
        self.create_rectangle(0, footer_y, w, h, fill="#081018", outline="#1c3347", width=1)
        self.create_text(20, footer_y + 4, anchor="nw", text="▶ Frakobl rogue enheden i kabelbakken for at fuldføre sikringen.", fill="#f6d365", font=("Consolas", 9, "bold"))

    def on_vfd_workbench_click(self, name: str) -> None:
        if name == "close_vfd_workbench":
            self._trigger_command("vis rum")
        elif name == "vfd_mount":
            self._trigger_command("monter scalance på din-skinne")
        elif name == "vfd_cable":
            self._trigger_command("kobl kabler til scalance")
        elif name == "vfd_wrong_cable":
            self._trigger_command("byt om på lan og wan")
        elif name == "vfd_test_forget_fc3":
            self._trigger_command("firewall rule add --drop-fc 6")
        elif name == "vfd_dpi":
            self._trigger_command("firewall rule add --allow-fc 3 --drop-fc 6")
        self.draw()

    def on_switch_workbench_click(self, name: str) -> None:
        if name == "close_switch_workbench":
            self._trigger_command("vis rum")
        self.draw()

    # -------------------------------------------------------------------------
    # 4. INVESTIGATION CASE BOARD VIEW (SAGSTAVLE)
    # -------------------------------------------------------------------------
    def draw_clue_board(self, w: int, h: int) -> None:
        # Corkboard / slate detective background
        self.create_rectangle(0, 0, w, h, fill="#121820", outline="")

        # Compact Top Header Bar (34px)
        self.create_rectangle(0, 0, w, 34, fill="#1c2430", outline="#2e3b4e", width=1)
        self.create_text(
            12, 8, anchor="nw",
            text="🕵️ SAGSTAVLE – KLIK PÅ ET SPOR TIL HØJRE FOR AT ANALYSERE DET & KLIK PÅ EN MISTÆNKT TIL VENSTRE",
            fill="#f6d365", font=("Consolas", 10, "bold"),
        )

        # Header Buttons: [ 🏠 Hovedmenu ] and [ ⬅️ Tilbage til Anlægget ]
        btn_w = 165
        btn_x2 = w - 10
        btn_x1 = btn_x2 - btn_w
        self.create_rectangle(btn_x1, 4, btn_x2, 30, fill="#1e293b", outline="#38bdf8", width=1)
        self.create_text((btn_x1 + btn_x2) // 2, 17, text="⬅️ Tilbage til Anlægget", fill="#e0f2fe", font=("Segoe UI", 8, "bold"))
        self.canvas_buttons["close_clue_board"] = (
            btn_x1, 4, btn_x2, 30,
            lambda: self.master_app.toggle_sagstavle() if hasattr(self.master_app, "toggle_sagstavle") else self._trigger_command("vis rum"),
        )

        home_w = 115
        home_x2 = btn_x1 - 8
        home_x1 = home_x2 - home_w
        self.create_rectangle(home_x1, 4, home_x2, 30, fill="#0284c7", outline="#38bdf8", width=1)
        self.create_text((home_x1 + home_x2) // 2, 17, text="🏠 Hovedmenu", fill="#ffffff", font=("Segoe UI", 8, "bold"))
        self.canvas_buttons["menu_from_clue_board"] = (
            home_x1, 4, home_x2, 30,
            lambda: self.master_app.prompt_return_to_menu() if hasattr(self.master_app, "prompt_return_to_menu") else None,
        )

        content_top_y = 38
        detail_box_h = 42
        footer_y = h - detail_box_h
        bottom_y = footer_y - 4

        # Column 1: Mistænkte & Hypoteser (Left ~37%)
        col1_w = int(w * 0.37)
        self.create_rectangle(10, content_top_y, col1_w, bottom_y, fill="#0d131a", outline="#1f2937", width=1)
        self.create_text(
            16, content_top_y + 3, anchor="nw",
            text="👥 MISTÆNKTE (Klik for ⭐ Hovedmistænkt):",
            fill="#f6d365", font=("Segoe UI", 8, "bold"),
        )

        is_exam = getattr(self.engine, "game_mode", "teach") == "exam"
        suspects = (
            list(self.engine.investigation.suspects.values())
            if is_exam
            else sorted(self.engine.investigation.suspects.values(), key=lambda x: x.suspicion_score, reverse=True)
        )
        s_start_y = content_top_y + 21
        s_avail_h = max(140, bottom_y - s_start_y - 2)
        s_gap = 3
        s_card_h = max(28, int((s_avail_h - 4 * s_gap) / 5))

        for idx, s in enumerate(suspects):
            is_prime = s.status == "Hovedmistænkt"
            s_bg = "#2b1e16" if is_prime else "#141c24"
            border_c = "#f59e0b" if is_prime else "#253342"
            border_w = 2 if is_prime else 1

            cy1 = s_start_y + idx * (s_card_h + s_gap)
            cy2 = cy1 + s_card_h
            cx1 = 14
            cx2 = col1_w - 5

            self.create_rectangle(cx1, cy1, cx2, cy2, fill=s_bg, outline=border_c, width=border_w)
            star = "⭐ " if is_prime else ""
            name_col = "#fde047" if is_prime else "#f8fafc"
            self.create_text(cx1 + 5, cy1 + 2, anchor="nw", text=f"{star}{s.name}", fill=name_col, font=("Segoe UI", 8, "bold"))

            if is_exam:
                link_txt = f"{s.role[:42]}"
                link_col = "#94a3b8"
                self.create_text(cx1 + 5, cy1 + 15, anchor="nw", text=link_txt, fill=link_col, font=("Segoe UI", 7))
            else:
                linked = self.engine.investigation.get_analyzed_clues_for_suspect(s.id)
                if linked:
                    link_txt = f"🔗 {len(linked)} bevis(er) peger her"
                    link_col = "#34d399"
                else:
                    link_txt = f"{s.role[:32]}"
                    link_col = "#94a3b8"
                self.create_text(cx1 + 5, cy1 + 15, anchor="nw", text=link_txt, fill=link_col, font=("Segoe UI", 7))

                # Suspicion meter (Only shown in Teach Mode)
                meter_w = 50
                meter_x1 = cx2 - meter_w - 6
                meter_x2 = cx2 - 6
                meter_y1 = cy1 + 5
                meter_y2 = cy1 + 18
                self.create_rectangle(meter_x1, meter_y1, meter_x2, meter_y2, fill="#0f172a", outline="#334155")
                filled_w = int((s.suspicion_score / 100) * meter_w)
                meter_col = "#ef4444" if s.suspicion_score >= 50 else ("#f59e0b" if s.suspicion_score >= 30 else "#38bdf8")
                if filled_w > 0:
                    self.create_rectangle(meter_x1, meter_y1, meter_x1 + filled_w, meter_y2, fill=meter_col, outline="")
                self.create_text(meter_x1 + meter_w // 2, meter_y1 + 6, text=f"{s.suspicion_score}%", fill="white", font=("Segoe UI", 7, "bold"))

            btn_id = f"susp_{s.id}"
            self.canvas_buttons[btn_id] = (cx1, cy1, cx2, cy2, lambda sid=s.id: self._trigger_command(f"anklag {sid}"))

        # Column 2: Opdagede Spor (Right ~63% - 2-Column Grid of all 11 clues)
        col2_x1 = col1_w + 8
        col2_x2 = w - 10
        self.create_rectangle(col2_x1, content_top_y, col2_x2, bottom_y, fill="#0d131a", outline="#1f2937", width=1)

        discovered = self.engine.investigation.get_discovered_clues()
        unanalyzed = self.engine.investigation.get_unanalyzed_clues()
        total_clues = len(self.engine.investigation.clues)
        unanalyzed_badge = f"  |  ⚠️ {len(unanalyzed)} MANGLER ANALYSE (KLIK PÅ DEM!)" if unanalyzed else "  |  ✅ Alle fundne analyseret"
        self.create_text(
            col2_x1 + 8, content_top_y + 3, anchor="nw",
            text=f"🔍 SPOR & BEVISER ({len(discovered)}/{total_clues} fundet{unanalyzed_badge}):",
            fill="#fbbf24" if unanalyzed else "#f6d365", font=("Segoe UI", 8, "bold"),
        )

        c_start_y = content_top_y + 21
        c_avail_h = max(140, bottom_y - c_start_y - 2)
        num_rows = 6
        c_gap = 3
        c_card_h = max(24, int((c_avail_h - (num_rows - 1) * c_gap) / num_rows))
        sub_col_w = int((col2_x2 - col2_x1 - 18) / 2)

        cat_colors = {
            "Netværk": "#0284c7",
            "Fysisk": "#b45309",
            "Systemlog": "#7c3aed",
            "Vidneudsagn": "#15803d",
            "Konfiguration": "#475569",
        }

        for idx in range(total_clues):
            row = idx % num_rows
            col = idx // num_rows
            cx1 = (col2_x1 + 6) if col == 0 else (col2_x1 + 12 + sub_col_w)
            cx2 = cx1 + sub_col_w
            cy1 = c_start_y + row * (c_card_h + c_gap)
            cy2 = cy1 + c_card_h

            if idx < len(discovered):
                c = discovered[idx]
                cat_col = cat_colors.get(c.category, "#334155")
                is_analyzed = getattr(c, "analyzed", False)
                is_sel = self.selected_clue_id == c.id
                card_bg = "#1e3a5f" if is_sel else ("#142228" if is_analyzed else "#291d12")
                card_border = "#38bdf8" if is_sel else ("#10b981" if is_analyzed else "#f59e0b")
                border_w = 2 if (is_sel or not is_analyzed) else 1
                self.create_rectangle(cx1, cy1, cx2, cy2, fill=card_bg, outline=card_border, width=border_w)

                # Category badge
                self.create_rectangle(cx1 + 3, cy1 + 3, cx1 + 55, cy1 + 16, fill=cat_col, outline="")
                self.create_text(cx1 + 29, cy1 + 9, text=c.category[:7].upper(), fill="white", font=("Segoe UI", 6, "bold"))

                status_prefix = "✅ " if is_analyzed else "⚠️ NYT: "
                title_col = "#f8fafc" if is_analyzed else "#fde047"
                self.create_text(cx1 + 59, cy1 + 2, anchor="nw", text=f"{status_prefix}{c.title[:24]}", fill=title_col, font=("Segoe UI", 7, "bold"))

                if is_analyzed:
                    if is_exam:
                        sub_txt = f"{c.discovery_room} • Teknisk analyse klar"
                    else:
                        s_names = []
                        for sid in c.associated_suspects:
                            s_obj = self.engine.investigation.suspects.get(sid)
                            s_names.append(s_obj.name.split()[0] if s_obj else sid)
                        sub_txt = f"➔ Peger på: {', '.join(s_names)}" if s_names else f"{c.discovery_room} • Analyseret"
                    sub_col = "#6ee7b7"
                else:
                    sub_txt = "👉 KLIK HER FOR ANALYSE!"
                    sub_col = "#fb923c"
                self.create_text(cx1 + 59, cy1 + 13, anchor="nw", text=sub_txt[:34], fill=sub_col, font=("Segoe UI", 7, "bold" if not is_analyzed else "normal"))

                btn_id = f"clue_{c.id}"
                self.canvas_buttons[btn_id] = (cx1, cy1, cx2, cy2, lambda cid=c.id: self._on_clue_card_click(cid))
            else:
                self.create_rectangle(cx1, cy1, cx2, cy2, fill="#0a1016", outline="#1c2836", width=1, dash=(3, 3))
                self.create_text(cx1 + 6, cy1 + 5, anchor="nw", text=f"🔒 Spor #{idx + 1}: Ikke fundet endnu", fill="#64748b", font=("Segoe UI", 7))

        # Bottom Active Clue Detail Banner (always visible inside the 310px Sagstavle!)
        self.create_rectangle(0, footer_y, w, h, fill="#0b1929", outline="#0284c7", width=1)
        sel_clue = self.engine.investigation.clues.get(self.selected_clue_id) if self.selected_clue_id else (discovered[-1] if discovered else None)
        if sel_clue:
            if getattr(sel_clue, "analyzed", False):
                if is_exam:
                    suspect_info = "✅ Analyseret (Vurdér selv sammenhængen ud fra analysen i terminalen)"
                else:
                    s_names = [self.engine.investigation.suspects[sid].name for sid in sel_clue.associated_suspects if sid in self.engine.investigation.suspects]
                    suspect_info = f"Peger på: {', '.join(s_names)}"
            else:
                suspect_info = "⚠️ KLIK PÅ KORTET OVENFOR FOR AT ANALYSERE DETTE SPOR!"
            self.create_text(
                14, footer_y + 4, anchor="nw",
                text=f"🔬 VALGT BEVIS: [{sel_clue.id}] {sel_clue.title}  —  {suspect_info}",
                fill="#fde047", font=("Segoe UI", 8, "bold"),
            )
            self.create_text(
                14, footer_y + 21, anchor="nw",
                text=f"   Detaljer: {sel_clue.description[:118]}",
                fill="#bae6fd", font=("Segoe UI", 8),
            )
        else:
            self.create_text(
                14, footer_y + 12, anchor="nw",
                text="💡 Ingen spor fundet endnu. Undersøg komponenter og kør tshark i zonerne for at samle spor!",
                fill="#f6d365", font=("Segoe UI", 8, "bold"),
            )
