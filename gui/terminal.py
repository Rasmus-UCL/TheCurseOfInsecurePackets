"""Authentic Green-on-Black CRT Terminal Widget with integrated prompt, history & Tab auto-complete."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Any

from core.terminal_engine import AutocompleteHelper


class TerminalWidget(tk.Frame):
    """Integrated Green-on-Black industrial terminal with embedded command prompt and shell history."""

    def __init__(
        self,
        master: Any,
        on_command: Callable[[str], None],
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg="#050a08", bd=1, relief="ridge", **kwargs)
        self.on_command = on_command

        # Terminal History Buffer
        self.history: list[str] = []
        self.history_index: int = -1

        # Output Text Area
        self.output_frame = tk.Frame(self, bg="#050a08")
        self.output_frame.pack(fill="both", expand=True, padx=6, pady=(6, 2))

        self.scroll = tk.Scrollbar(self.output_frame, bg="#0d1f14", troughcolor="#050a08", relief="flat")
        self.scroll.pack(side="right", fill="y")

        self.text = tk.Text(
            self.output_frame,
            bg="#050a08",
            fg="#4ade80",
            insertbackground="#22c55e",
            font=("Consolas", 10),
            wrap="word",
            padx=10,
            pady=6,
            state="disabled",
            bd=0,
            highlightthickness=0,
            yscrollcommand=self.scroll.set,
        )
        self.text.pack(side="left", fill="both", expand=True)
        self.scroll.config(command=self.text.yview)

        # Color Tags (Green CRT Palette)
        self.text.tag_configure("green_bright", foreground="#86efac", font=("Consolas", 10, "bold"))
        self.text.tag_configure("green_normal", foreground="#4ade80")
        self.text.tag_configure("green_dim", foreground="#166534")
        self.text.tag_configure("alarm", foreground="#f87171", font=("Consolas", 10, "bold"))
        self.text.tag_configure("warning", foreground="#fde047")
        self.text.tag_configure("cyan", foreground="#67e8f9")
        self.text.tag_configure("purple", foreground="#c084fc")
        self.text.tag_configure("menu_hdr", foreground="#fde047", font=("Consolas", 10, "bold"))
        self.text.tag_configure("choice", foreground="#86efac", font=("Consolas", 10))

        # Integrated Command Prompt Line (Directly at the bottom of the terminal)
        self.prompt_bar = tk.Frame(self, bg="#0b1710", padx=8, pady=4, relief="groove", bd=1)
        self.prompt_bar.pack(fill="x", padx=6, pady=(0, 6))

        self.prompt_label = tk.Label(
            self.prompt_bar,
            text="NordicH2O@OT-Consol:~$ ",
            bg="#0b1710",
            fg="#22c55e",
            font=("Consolas", 10, "bold"),
        )
        self.prompt_label.pack(side="left")

        self.entry = tk.Entry(
            self.prompt_bar,
            bg="#050a08",
            fg="#86efac",
            insertbackground="#4ade80",
            font=("Consolas", 10),
            bd=0,
            highlightthickness=1,
            highlightbackground="#166534",
            highlightcolor="#22c55e",
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(4, 6))
        self.entry.focus_set()

        # Keyboard Bindings
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Up>", self._on_history_up)
        self.entry.bind("<Down>", self._on_history_down)
        self.entry.bind("<Tab>", self._on_tab_complete)

        self.exec_btn = tk.Button(
            self.prompt_bar,
            text="UDFØR [⏎]",
            bg="#166534",
            fg="#f0fdf4",
            activebackground="#22c55e",
            activeforeground="#050a08",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            padx=10,
            command=self._execute_from_entry,
        )
        self.exec_btn.pack(side="right")

    def set_prompt_prefix(self, location: str) -> None:
        clean_loc = location.lower().replace("-", "_")
        self.prompt_label.configure(text=f"OT-Consol:\\{clean_loc}> ")

    def write_line(self, message: str, tag: str | None = None) -> None:
        self.text.configure(state="normal")
        if not tag:
            tag = "green_normal"
        self.text.insert("end", message + "\n", tag)
        self.text.see("end")
        self.text.configure(state="disabled")

    def write_block(self, text: str) -> None:
        lines = text.splitlines()
        for line in lines:
            tag = "green_normal"
            s = line.strip()
            if any(w in line for w in {"[ALARM]", "[KRITISK", "💥", "KATASTROFE", "🚨"}):
                tag = "alarm"
            elif any(w in line for w in {"[LØSNING", "[OK]", "✅", "RESULTAT:", "BESTÅR", "🏆"}):
                tag = "green_bright"
            elif "TILGÆNGELIGE HANDLINGER" in line or "TILGAENGELIGE" in line:
                tag = "menu_hdr"
            elif line.startswith("  [") or line.startswith("[") and "]" in line:
                tag = "choice"
            elif any(w in line for w in {"Jens:", "Hans:", "Jens Majer:", "Hans McDonald:", "Revisor", "Kirsten:"}):
                tag = "warning"
            elif any(w in line for w in {"[WIRESHARK", "[SIEMENS", "[NMAP", "[PURDUE", "[NIS2", "Modbus", "PROFINET"}):
                tag = "cyan"
            self.write_line(line, tag)

    def _execute_from_entry(self) -> None:
        cmd = self.entry.get().strip()
        self.entry.delete(0, "end")
        if not cmd:
            return

        self.history.append(cmd)
        self.history_index = len(self.history)

        # Echo command in terminal
        self.write_line(f"> {cmd}", "green_bright")
        self.on_command(cmd)

    def _on_enter(self, _event: tk.Event[tk.Misc]) -> str:
        self._execute_from_entry()
        return "break"

    def _on_history_up(self, _event: tk.Event[tk.Misc]) -> str:
        if not self.history:
            return "break"
        if self.history_index > 0:
            self.history_index -= 1
            self.entry.delete(0, "end")
            self.entry.insert(0, self.history[self.history_index])
        return "break"

    def _on_history_down(self, _event: tk.Event[tk.Misc]) -> str:
        if not self.history:
            return "break"
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.entry.delete(0, "end")
            self.entry.insert(0, self.history[self.history_index])
        else:
            self.history_index = len(self.history)
            self.entry.delete(0, "end")
        return "break"

    def _on_tab_complete(self, _event: tk.Event[tk.Misc]) -> str:
        curr = self.entry.get()
        matches = AutocompleteHelper.get_matches(curr)
        if len(matches) == 1:
            self.entry.delete(0, "end")
            self.entry.insert(0, matches[0])
        elif len(matches) > 1:
            self.write_line(f"[TAB-FORSLAG]: {', '.join(matches[:6])}", "green_dim")
        return "break"
