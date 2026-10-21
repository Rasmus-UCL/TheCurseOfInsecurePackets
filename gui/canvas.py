"""Dedicated 2D visual plant floor screen & interactive workbenches (Wireshark moves to Terminal)."""

from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Callable
from typing import Any

from rooms import ALL_ROOMS


class GameCanvas(tk.Canvas):
    """Clickable 2D retro-industrial room map & in-canvas workbenches."""

    def __init__(self, master_app: Any, engine: Any, on_hotspot_click: Any, **kwargs: object) -> None:
        super().__init__(master_app, bg="#0d1821", highlightthickness=1, highlightbackground="#1f364d", **kwargs)
        self.master_app = master_app
        self.engine = engine
        self.on_hotspot_click = on_hotspot_click

        self.view_mode: str = "room"  # "room", "vfd_workbench", "switch_workbench"
        self.selected_hotspot: str | None = None
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
        if self.view_mode == "room" and self.engine.room in {"pumpehuset", "ventil-oen"}:
            self.draw()
        elif self.view_mode in {"vfd_workbench", "switch_workbench"}:
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

        width = max(self.winfo_width(), 760)
        height = max(self.winfo_height(), 350)

        if self.view_mode == "room":
            self.draw_room(width, height)
            if self.selected_hotspot:
                self.draw_equipment_hud(width, height)
        elif self.view_mode == "vfd_workbench":
            self.draw_vfd_workbench(width, height)
        elif self.view_mode == "switch_workbench":
            self.draw_switch_workbench(width, height)

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
        elif r == "el-tavlen":
            rail_y = 200
            self.create_rectangle(15, rail_y - 8, width - 15, rail_y + 8, fill="#52606d", outline="#8295a5", width=2)
            self.create_text(width - 160, rail_y - 18, text="35mm DIN-SKINNE TS35", fill="#8295a5", font=("Consolas", 8))
        elif r == "kontrolrummet":
            self.create_rectangle(20, 70, width - 20, height - 35, fill="", outline="#1f425f", width=1, dash=(4, 4))

    def draw_hotspot_card(self, name: str, x1: int, y1: int, x2: int, y2: int, is_hovered: bool, is_selected: bool) -> None:
        flags = self.engine.flags
        card_bg = "#23415c" if is_selected else ("#1b354b" if is_hovered else "#132535")
        border_color = "#38bdf8" if is_selected else ("#f6d365" if is_hovered else "#2a4d6c")
        border_width = 3 if (is_selected or is_hovered) else 1

        self.create_rectangle(x1, y1, x2, y2, fill=card_bg, outline=border_color, width=border_width)

        badge_text = "NORMAL"
        badge_color = "#4ade80"
        icon_type = "⚙️ KOMPONENT"
        sub_info = ""

        if name == "pumpe 2":
            icon_type = "🚰 CENTRIFUGALPUMPE"
            if "chapter-1-done" in flags:
                badge_text = "42 BAR (OK)"
                badge_color = "#4ade80"
                sub_info = "Stabil drift"
            else:
                pulsing = "#ef4444" if self.anim_tick % 2 == 0 else "#f87171"
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
                badge_text = "OSCILLERER"
                badge_color = "#ef4444"
                sub_info = "Kaos i trykluft!"
        elif name == "s7-1500":
            icon_type = "🛡️ SIKKERHEDS-PLC"
            if getattr(self.engine, "plc_defect_stop", False):
                badge_text = "DEFECTIVE STOP"
                badge_color = "#ef4444"
                sub_info = "Fejlkode 0x4542"
            elif "chapter-3-done" in flags:
                badge_text = "RUN MODE"
                badge_color = "#4ade80"
                sub_info = "PUT/GET blokeret"
            else:
                badge_text = "STOP MODE"
                badge_color = "#f59e0b"
                sub_info = "S7comm port 102"
        elif name == "4g-router":
            icon_type = "📡 ROGUE UPLINK"
            if "router-disconnected" in flags:
                badge_text = "FRAKOBLET"
                badge_color = "#4ade80"
                sub_info = "IDMZ sikret"
            else:
                badge_text = "AKTIV 4G BACKDOOR"
                badge_color = "#ef4444"
                sub_info = "Teltonika RUT950"
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
            self.canvas_buttons["hud_open_vfd"] = (btn_x, btn_y1, btn_x + bw, btn_y2, lambda: self.master_app.command("firewall workbench"))
            btn_x += bw + 12

        # Button 2: Switch Workbench (Ventil-øen)
        if name in {"switch", "d-link switch"} or (self.engine.room == "ventil-oen" and "chapter-2-done" not in self.engine.flags and "pi-removed" in self.engine.flags):
            bw = 240
            self.create_rectangle(btn_x, btn_y1, btn_x + bw, btn_y2, fill="#0284c7", outline="#38bdf8", width=2)
            self.create_text(btn_x + bw // 2, (btn_y1 + btn_y2) // 2, text="🔧 Åbn Switch Montage Bænk", fill="white", font=("Segoe UI", 9, "bold"))
            self.canvas_buttons["hud_open_switch"] = (btn_x, btn_y1, btn_x + bw, btn_y2, lambda: self.master_app.command("switch workbench"))
            btn_x += bw + 12

        # Button 3: Reveal Pi in cable tray
        if name == "kabelbakke" and "pi-revealed" not in self.engine.flags:
            bw = 250
            self.create_rectangle(btn_x, btn_y1, btn_x + bw, btn_y2, fill="#b45309", outline="#f59e0b", width=2)
            self.create_text(btn_x + bw // 2, (btn_y1 + btn_y2) // 2, text="🔦 Undersøg Kabelbakke Nøje", fill="white", font=("Segoe UI", 9, "bold"))
            self.canvas_buttons["hud_kabelbakke"] = (btn_x, btn_y1, btn_x + bw, btn_y2, lambda: self.master_app.command("undersøg kabelbakke"))
            btn_x += bw + 12

        # Button 4: Faraday Bag on Rogue Pi
        if name == "rogue raspberry pi" and "pi-removed" not in self.engine.flags:
            bw = 250
            self.create_rectangle(btn_x, btn_y1, btn_x + bw, btn_y2, fill="#15803d", outline="#4ade80", width=2)
            self.create_text(btn_x + bw // 2, (btn_y1 + btn_y2) // 2, text="🛡️ Sikr Pi i Faraday-pose", fill="white", font=("Segoe UI", 9, "bold"))
            self.canvas_buttons["hud_faraday"] = (btn_x, btn_y1, btn_x + bw, btn_y2, lambda: self.master_app.command("sikr pi i faraday-pose"))
            btn_x += bw + 12

        # Button: Wireshark on all hotspots
        ws_bw = 160
        self.create_rectangle(btn_x, btn_y1, btn_x + ws_bw, btn_y2, fill="#162c3d", outline="#38bdf8", width=1)
        self.create_text(btn_x + ws_bw // 2, (btn_y1 + btn_y2) // 2, text="📊 Kør Wireshark", fill="#e0f2fe", font=("Segoe UI", 9, "bold"))
        self.canvas_buttons["hud_wireshark"] = (btn_x, btn_y1, btn_x + ws_bw, btn_y2, lambda: self.master_app.command("wireshark"))

        self.create_text(hx1 + 14, hy1 + 105, anchor="nw", text="💡 TIP: Klik på knapperne foroven eller tast tal (1-N) i terminalen forneden.", fill="#38bdf8", font=("Segoe UI", 8, "italic"))

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
        if not is_cabled or is_wrong:
            self.create_rectangle(c3_x1, c3_y1, c3_x2, c3_y2, fill="#090e14", outline="#334155", width=1)
            self.create_text(c3_x1 + 15, c3_y1 + 50, anchor="nw", text="TRIN 3: MODBUS DPI\n(Kræver korrekt kabling)", fill="#64748b", font=("Segoe UI", 9))
        elif not is_done:
            self.create_rectangle(c3_x1, c3_y1, c3_x2, c3_y2, fill="#0b2942", outline="#38bdf8", width=2, dash=(6, 3))
            s3_text = "TRIN 3: AKTIVER DPI\n(Guldstandard)\n[ KLIK FOR AT AKTIVERE ]\nTillad FC 03 (Læsning)\nDrop FC 06/16 (Sabotage)" if mode == "teach" else "TRIN 3: AKTIVER MODBUS DPI\n\n[ KLIK FOR AT AKTIVERE ]\nTillad FC 03 (Læsning)\nDrop FC 06/16 (Sabotage)"
            self.create_text(c3_x1 + 15, c3_y1 + 20, anchor="nw", text=s3_text, fill="#38bdf8", font=("Segoe UI", 8, "bold"))
            self.hotspot_rects["vfd_dpi"] = (c3_x1, c3_y1, c3_x2, c3_y2)
        else:
            self.create_rectangle(c3_x1, c3_y1, c3_x2, c3_y2, fill="#063220", outline="#22c55e", width=2)
            self.create_text(c3_x1 + 15, c3_y1 + 15, anchor="nw", text="MODBUS DPI REGELSÆT AKTIVT", fill="#f8fafc", font=("Segoe UI", 9, "bold"))
            self.create_text(c3_x1 + 15, c3_y1 + 50, anchor="nw", text="Filter: Deep Packet Inspection\nFC 03: ACCEPT (SCADA OK)\nFC 06: DROP & LOG\nPumpe 2 Tryk: 42.0 Bar (STABIL)", fill="#4ade80", font=("Consolas", 8))

        # Slot 4: Faldgrube / Test knap
        c4_x1, c4_y1, c4_x2, c4_y2 = 760, 75, 960, 245
        self.create_rectangle(c4_x1, c4_y1, c4_x2, c4_y2, fill="#1c1917", outline="#78716c", width=1)
        s4_header = "FALDGRUBE TEST:" if mode == "teach" else "TEST-SCENARIE:"
        s4_sub = "Test hvad der sker hvis\nkablerne krydses forkert" if mode == "teach" else "Forbind VFD til WAN P5\nog switchen til LAN P1"
        self.create_text(c4_x1 + 12, c4_y1 + 20, anchor="nw", text=f"{s4_header}\n\n[ BYT OM PÅ WAN/LAN ]\n{s4_sub}", fill="#fbbf24", font=("Segoe UI", 8, "bold"))
        self.hotspot_rects["vfd_wrong_cable"] = (c4_x1, c4_y1, c4_x2, c4_y2)

        footer_y = h - 26
        self.create_rectangle(0, footer_y, w, h, fill="#081018", outline="#1c3347", width=1)
        self.create_text(20, footer_y + 4, anchor="nw", text="▶ Klik på trinene foroven, brug tallene 1-6 i terminalen, eller klik 'Tilbage' for at vende tilbage.", fill="#f6d365", font=("Consolas", 9, "bold"))

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
            self.master_app.command("vis rum")
        elif name == "vfd_mount":
            self.master_app.command("monter scalance på din-skinne")
        elif name == "vfd_cable":
            self.master_app.command("kobl kabler til scalance")
        elif name == "vfd_wrong_cable":
            self.master_app.command("byt om på lan og wan")
        elif name == "vfd_dpi":
            self.master_app.command("aktiver modbus dpi")
        self.draw()

    def on_switch_workbench_click(self, name: str) -> None:
        if name == "close_switch_workbench":
            self.master_app.command("vis rum")
        self.draw()
