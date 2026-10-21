import tkinter as tk
from plc_3d_engine import Engine3D
from plc_network_client import PLCNetworkClient, KNOWN_GOOD_CRC
from plc_3d_scene import SceneManager
import asyncio
import threading
from datetime import datetime

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🛡️ Advanced Industrial Cybersecurity Twin 4.0")
        self.geometry("1200x800")
        self.configure(bg="#0f172a")
        
        # Initialisering af de eksterne moduler
        self.engine = Engine3D()
        self.net = PLCNetworkClient()
        self.scene = SceneManager(self.engine)
        
        self.plc_color = "#1e3a8a"
        self.ar_color = "#22c55e"
        self.pulse = 0
        self.robot_active = True
        self.last_known_status = "UNKNOWN"

        # --- TOP BAR ---
        top = tk.Frame(self, bg="#1e293b", height=70)
        top.pack(fill=tk.X, side=tk.TOP)
        tk.Label(top, text="🛡️ CYBERSECURITY INDUSTRIAL DIGITAL TWIN 4.0", font=("Arial", 14, "bold"), fg="#38bdf8", bg="#1e293b").pack(side=tk.LEFT, padx=20, pady=15)
        self.lbl_status = tk.Label(top, text="OFFLINE", font=("Arial", 10, "bold"), fg="#64748b", bg="#0f172a", padx=10, pady=5)
        self.lbl_status.pack(side=tk.RIGHT, padx=20)

        # --- BUND PANEL: EVENT LOG ---
        bottom_panel = tk.Frame(self, bg="#1e293b", height=150)
        bottom_panel.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_panel.pack_propagate(False)
        
        tk.Label(bottom_panel, text="📋 CYBERSECURITY INCIDENT LOG (REAL-TIME)", font=("Arial", 9, "bold"), fg="#94a3b8", bg="#1e293b").pack(anchor="w", padx=15, pady=5)
        self.log_text = tk.Text(bottom_panel, bg="#0f172a", fg="#38bdf8", font=("Courier", 9), bd=0, padx=10, pady=5)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        self.add_log("System initialiseret. Afventer scanning...")

        # Main Workspace Split
        main = tk.Frame(self, bg="#0f172a")
        main.pack(fill=tk.BOTH, expand=True)

        # --- LEFT PANEL: CONTROL & AR ---
        left = tk.Frame(main, bg="#1e293b", width=350, padx=15, pady=15)
        left.pack(fill=tk.Y, side=tk.LEFT)
        left.pack_propagate(False)

        tk.Label(left, text="📡 LIVE PLC STATUS", font=("Arial", 10, "bold"), fg="#94a3b8", bg="#1e293b").pack(anchor="w")
        dbox = tk.Frame(left, bg="#0f172a", padx=10, pady=10, bd=1, relief="solid")
        dbox.pack(fill=tk.X, pady=5)
        
        self.lbl_key = tk.Label(dbox, text="Keyswitch: OFFLINE", font=("Courier", 10), fg="#64748b", bg="#0f172a")
        self.lbl_key.pack(anchor="w")
        self.lbl_crc = tk.Label(dbox, text="Program CRC: OFFLINE", font=("Courier", 10), fg="#64748b", bg="#0f172a")
        self.lbl_crc.pack(anchor="w", pady=(5,0))

        tk.Label(left, text="🕶️ AR OPERATØR-INSTRUKTION", font=("Arial", 10, "bold"), fg="#94a3b8", bg="#1e293b").pack(anchor="w", pady=(15, 5))
        self.ar_card = tk.Frame(left, bg="#0f172a", padx=15, pady=15, bd=2, relief="solid", highlightbackground="#475569")
        self.ar_card.pack(fill=tk.X, pady=5)
        self.ar_title = tk.Label(self.ar_card, text="🔌 Offline", font=("Arial", 11, "bold"), fg="#94a3b8", bg="#0f172a")
        self.ar_title.pack(anchor="w")
        self.ar_desc = tk.Label(self.ar_card, text="Forbind til simulator.", font=("Arial", 9), fg="#64748b", bg="#0f172a", wraplength=300, justify="left")
        self.ar_desc.pack(anchor="w", pady=5)

        tk.Label(left, text="⚡ INCIDENT RESPONSE ACTION", font=("Arial", 10, "bold"), fg="#94a3b8", bg="#1e293b").pack(anchor="w", pady=(15, 5))
        self.btn_recover = tk.Button(left, text="💾 GENDAN PLC & LÅS HUKOMMELSE", font=("Arial", 10, "bold"), bg="#2563eb", fg="white", activebackground="#1d4ed8", command=self.trigger_recovery, state=tk.DISABLED)
        self.btn_recover.pack(fill=tk.X, pady=5)

        # --- RIGHT PANEL: 3D VIEWPORT ---
        self.canvas = tk.Canvas(main, bg="#0f172a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        self.canvas.bind("<B1-Motion>", self.mouse_move)
        self.canvas.bind("<Button-1>", self.mouse_down)
        self.canvas.bind("<MouseWheel>", self.mouse_zoom)

        # Håndtering af ren lukning, når vinduet lukkes på krydset
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start netværks-loopet i en baggrundstråd via den nye klient
        threading.Thread(target=lambda: asyncio.run(self.net.poll_loop()), daemon=True).start()
        self.update_gui_loop()

    def add_log(self, msg):
        tstamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{tstamp}] {msg}\n")
        self.log_text.see(tk.END)

    def trigger_recovery(self):
        def async_task():
            success = asyncio.run(self.net.send_recovery())
            if success:
                self.add_log("SUCCESS: Gendannelsessignal modtaget af PLC. Firmware overskrevet med baseline hash.")
            else:
                self.add_log("ERROR: Kunne ikke sende gendannelsessignal til simulatoren.")
        threading.Thread(target=async_task, daemon=True).start()

    def mouse_down(self, event):
        self.last_x, self.last_y = event.x, event.y

    def mouse_move(self, event):
        self.engine.angle_y += (event.x - self.last_x) * 0.01
        self.engine.angle_x -= (event.y - self.last_y) * 0.01
        self.last_x, self.last_y = event.x, event.y
        self.draw_scene()

    def mouse_zoom(self, event):
        self.engine.zoom += 15 if event.delta > 0 else -15
        self.draw_scene()

    def draw_scene(self):
        # Kalder den eksterne scenemanager til at håndtere tegningen
        self.scene.draw(self.canvas, self.plc_color, self.ar_color, self.robot_active)

    def update_gui_loop(self):
        key, crc = self.net.live_key, self.net.live_crc

        self.lbl_key.config(text=f"Keyswitch: {key}", fg="#f8fafc" if key != "OFFLINE" else "#64748b")
        self.lbl_crc.config(text=f"Program CRC: {crc}", fg="#f8fafc" if crc != "OFFLINE" else "#64748b")

        if key == "OFFLINE":
            if self.last_known_status != "OFFLINE":
                self.add_log("CRITICAL: Forbindelse til maskinen tabt (PLC Nedbrud eller DoS).")
                self.last_known_status = "OFFLINE"
            self.lbl_status.config(text="OFFLINE", fg="#64748b")
            self.ar_card.config(highlightbackground="#475569")
            self.ar_title.config(text="🔌 Ingen Forbindelse", fg="#94a3b8")
            self.ar_desc.config(text="Tænd for plc_simulator.py.")
            self.plc_color, self.ar_color = "#1e40af", "#475569"
            self.robot_active, self.btn_recover['state'] = False, tk.DISABLED

        elif crc != KNOWN_GOOD_CRC:
            if self.last_known_status != "MALWARE":
                self.add_log(f"🚨 INTEGRITETS ALARM: Uautoriseret kode ændret! CRC Hash detekteret: {crc}")
                self.add_log("SIKKERHEDSAKTION: Nødstop udløst automatisk. Robotarm frosset.")
                self.last_known_status = "MALWARE"
            self.lbl_status.config(text="LIVE: CYBERANGREB DETEKTERET", fg="#ef4444")
            self.ar_card.config(highlightbackground="#ef4444")
            self.ar_title.config(text="🚨 MALWARE INTRUSION!", fg="#f87171")
            self.ar_desc.config(text=f"Kritisk: PLC programmets hash er manipuleret.\n\nAR-Instruks: Klik på 'GENDAN PLC' eller isoler fysisk.")
            self.plc_color = "#b91c1c"
            self.pulse += 1
            self.ar_color = "#ef4444" if self.pulse % 2 == 0 else "#7f1d1d"
            self.robot_active, self.btn_recover['state'] = False, tk.NORMAL

        elif key == "PROGRAM":
            if self.last_known_status != "VULN":
                self.add_log("⚠️ ADVARSEL: PLC omskifter sat i 'PROGRAM' tilstand trådløst. Angrebsflade åben!")
                self.last_known_status = "VULN"
            self.lbl_status.config(text="LIVE: SÅRBAR KONFIGURATION", fg="#f59e0b")
            self.ar_card.config(highlightbackground="#f59e0b")
            self.ar_title.config(text="⚠️ SÅRBAR KONFIGURATION", fg="#fbbf24")
            self.ar_desc.config(text="Nøglen står i PROGRAM-mode trådløst.\n\nAR-Instruks: Lås hukommelsen ved at klikke 'Gendan PLC' for at tvinge RUN mode.")
            self.plc_color, self.ar_color = "#d97706", "#f59e0b"
            self.robot_active, self.btn_recover['state'] = True, tk.NORMAL

        else:
            if self.last_known_status != "SAFE":
                self.add_log("🟢 SYSTEM STATUS: Sikker normal drift herunder baseline godkendt. Robotproduktion genstartet.")
                self.last_known_status = "SAFE"
            self.lbl_status.config(text="LIVE: SIKKER DRIFT", fg="#22c55e")
            self.ar_card.config(highlightbackground="#16a34a")
            self.ar_title.config(text="🟢 SIKKER DRIFT", fg="#4ade80")
            self.ar_desc.config(text="Integritet godkendt mod baseline. Ingen trusler fundet.")
            self.plc_color, self.ar_color = "#047857", "#22c55e"
            self.robot_active, self.btn_recover['state'] = True, tk.DISABLED

        self.draw_scene()
        self.after(200, self.update_gui_loop)

    def on_closing(self):
        """Lukker programmet og alle baggrundstråde øjeblikkeligt"""
        self.destroy()
        import os
        os._exit(0)

if __name__ == "__main__":

    # TILFØJ DENNE LINJE FOR AT FJERNE SESSION-TIMEOUT PRINT FRA TERMINALEN:
    import logging
    logging.getLogger("asyncua").setLevel(logging.CRITICAL)

    app = App()
    app.mainloop()
