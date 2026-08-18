"""
RAFAEL v2.0 — Tkinter UI
Asyncio backend thread ↔ Tkinter main thread (queue.Queue orqali).
Oyna: 520×720, dark futuristik, orb + tarix + status.
"""

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont

from ui import theme
from ui.components.orb import VoiceOrb
from ui.components.history import HistoryPanel
from ui.components.status_bar import StatusBar
from ui.components.settings_window import SettingsWindow
from core.utils.logger import get_logger

logger = get_logger(__name__)

# UI Events (assistant tomonidan yuboriladi)
EVT_STATE   = "state"     # {"type":"state",  "value":"listening"}
EVT_USER    = "user"      # {"type":"user",   "text":"..."}
EVT_RAFAEL  = "rafael"    # {"type":"rafael", "text":"..."}
EVT_CMD     = "cmd"       # {"type":"cmd",    "action":"...", "detail":"..."}
EVT_SYSTEM  = "system"    # {"type":"system", "text":"..."}
EVT_ERROR   = "error"     # {"type":"error",  "text":"..."}
EVT_QUIT    = "quit"      # {"type":"quit"}


class RafaelApp:
    """Tkinter asosiy oynasi."""

    def __init__(self, ui_queue: queue.Queue, stop_event: threading.Event,
                 config: dict = None):
        self._q         = ui_queue
        self._stop      = stop_event
        self._config    = config or {}

        self.root = tk.Tk()
        self._setup_window()
        self._build_ui()
        self._poll()     # queue tekshiruv loopi boshlanadi

    # ─── Window setup ────────────────────────────────────────────────────────

    def _setup_window(self):
        self.root.title("RAFAEL")
        self.root.geometry(f"{theme.WINDOW_W}x{theme.WINDOW_H}")
        self.root.minsize(400, 600)
        self.root.configure(bg=theme.BG_DEEP)
        self.root.resizable(True, True)

        # Markazga joylashtirish
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - theme.WINDOW_W) // 2
        y  = (sh - theme.WINDOW_H) // 2
        self.root.geometry(f"{theme.WINDOW_W}x{theme.WINDOW_H}+{x}+{y}")

        # Yopish tugmasi
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Shrift mavjudligini tekshirish
        try:
            tkfont.Font(family=theme.FONT_FAMILY, size=10)
        except Exception:
            pass

    # ─── UI Layout ───────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Sarlavha ──────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=theme.BG_DEEP)
        header.pack(fill=tk.X, padx=16, pady=(16, 0))

        tk.Label(
            header,
            text="R A F A E L",
            font=(theme.FONT_FAMILY, 16, "bold"),
            bg=theme.BG_DEEP,
            fg=theme.TEXT_ACCENT,
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text="Shaxsiy AI",
            font=theme.FONT_TINY,
            bg=theme.BG_DEEP,
            fg=theme.TEXT_SECONDARY,
        ).pack(side=tk.LEFT, padx=(8, 0), pady=(6, 0))

        # Minimize / Hide tugmasi
        tk.Button(
            header,
            text="—",
            font=theme.FONT_SMALL,
            bg=theme.BG_GLASS,
            fg=theme.TEXT_SECONDARY,
            activebackground=theme.BG_HOVER,
            activeforeground=theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            cursor="hand2",
            command=self.root.iconify,
        ).pack(side=tk.RIGHT)

        # Sozlamalar tugmasi
        tk.Button(
            header,
            text="⚙",
            font=theme.FONT_SMALL,
            bg=theme.BG_GLASS,
            fg=theme.TEXT_SECONDARY,
            activebackground=theme.BG_HOVER,
            activeforeground=theme.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            cursor="hand2",
            command=self._open_settings,
        ).pack(side=tk.RIGHT, padx=(0, 6))

        # ── Ajratgich ─────────────────────────────────────────────────────
        tk.Frame(self.root, bg=theme.BORDER, height=1).pack(fill=tk.X, pady=(8, 0))

        # ── Orb ───────────────────────────────────────────────────────────
        orb_frame = tk.Frame(self.root, bg=theme.BG_DEEP)
        orb_frame.pack(pady=20)

        self.orb = VoiceOrb(orb_frame, size=theme.ORB_SIZE)
        self.orb.pack()

        # Holat matni orb ostida
        self._orb_label = tk.Label(
            orb_frame,
            text=theme.STATE_LABELS["sleeping"],
            font=theme.FONT_SUBTITLE,
            bg=theme.BG_DEEP,
            fg=theme.TEXT_SECONDARY,
        )
        self._orb_label.pack(pady=(6, 0))

        # ── Oxirgi buyruq / javob ─────────────────────────────────────────
        last_frame = tk.Frame(self.root, bg=theme.BG_GLASS,
                              highlightthickness=1,
                              highlightbackground=theme.BORDER)
        last_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

        self._last_label = tk.Label(
            last_frame,
            text="Salom, Daler. Men RAFAELman.",
            font=theme.FONT_BODY,
            bg=theme.BG_GLASS,
            fg=theme.TEXT_PRIMARY,
            wraplength=theme.WINDOW_W - 60,
            justify=tk.LEFT,
            anchor="w",
            padx=12,
            pady=8,
        )
        self._last_label.pack(fill=tk.X)

        # ── Tarix paneli ──────────────────────────────────────────────────
        history_outer = tk.Frame(self.root, bg=theme.BG_PANEL,
                                 highlightthickness=1,
                                 highlightbackground=theme.BORDER)
        history_outer.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 0))

        self.history = HistoryPanel(
            history_outer,
            max_lines=self._config.get("ui", {}).get("history_max_lines", 200),
        )
        self.history.pack(fill=tk.BOTH, expand=True)

        # ── Status bar ────────────────────────────────────────────────────
        self.status = StatusBar(self.root)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    # ─── Event queue polling ─────────────────────────────────────────────────

    def _poll(self):
        """Har 50ms queue tekshiriladi — UI thread xavfsiz."""
        try:
            while True:
                evt = self._q.get_nowait()
                self._handle(evt)
        except queue.Empty:
            pass
        finally:
            self.root.after(50, self._poll)

    def _handle(self, evt: dict):
        t = evt.get("type", "")

        if t == EVT_STATE:
            state = evt.get("value", "sleeping")
            self.orb.set_state(state)
            self.status.set_state(state)
            label = theme.STATE_LABELS.get(state, state)
            self._orb_label.configure(
                text=label,
                fg=theme.STATE_COLORS.get(state, theme.TEXT_SECONDARY),
            )

        elif t == EVT_USER:
            text = evt.get("text", "")
            self._last_label.configure(
                text=f"▷  {text}",
                fg=theme.TEXT_ACCENT,
            )
            self.history.add_user(text)

        elif t == EVT_RAFAEL:
            text = evt.get("text", "")
            self._last_label.configure(
                text=f"◈  {text}",
                fg=theme.TEXT_SUCCESS,
            )
            self.history.add_rafael(text)

        elif t == EVT_CMD:
            action = evt.get("action", "")
            detail = evt.get("detail", "")
            self.history.add_command(action, detail)

        elif t == EVT_SYSTEM:
            self.history.add_system(evt.get("text", ""))

        elif t == EVT_ERROR:
            self.history.add_error(evt.get("text", ""))
            self.status.set_state("error")

        elif t == EVT_QUIT:
            self._on_close()

    # ─── Sozlamalar ──────────────────────────────────────────────────────────

    def _open_settings(self):
        config_path = Path(__file__).resolve().parent.parent / "config.yaml"
        SettingsWindow(self.root, config_path)

    # ─── Close ───────────────────────────────────────────────────────────────

    def _on_close(self):
        logger.info("UI yopilmoqda...")
        self._stop.set()
        self.root.after(300, self.root.destroy)

    def run(self):
        """Tkinter main loopini ishga tushiradi (bloklaydi)."""
        self.root.mainloop()
