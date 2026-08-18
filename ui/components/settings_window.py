"""
RAFAEL v2.0 — Sozlamalar oynasi
config.yaml'ni qo'lda tahrirlash o'rniga, asosiy sozlamalarni UI orqali
o'zgartirish uchun Toplevel oyna. Saqlangach RAFAEL qayta ishga tushirilishi
kerak (config faqat main.py boshlanishida bir marta o'qiladi).
"""

import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import yaml

from ui import theme


class SettingsWindow(tk.Toplevel):
    """config.yaml'dagi asosiy sozlamalarni tahrirlash oynasi."""

    def __init__(self, master, config_path: Path):
        super().__init__(master)
        self.config_path = config_path
        self._vars: dict[str, tk.Variable] = {}

        self.title("RAFAEL — Sozlamalar")
        self.geometry("420x560")
        self.minsize(380, 480)
        self.configure(bg=theme.BG_DEEP)
        self.transient(master)
        self.grab_set()

        self._config = self._load_config()
        self._build_ui()

    # ─── Config I/O ──────────────────────────────────────────────────────────

    def _load_config(self) -> dict:
        try:
            with open(self.config_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            messagebox.showerror("Xato", f"config.yaml o'qilmadi:\n{e}", parent=self)
            return {}

    def _save_config(self):
        cfg = self._config
        raphail = cfg.setdefault("raphail", {})
        voice   = cfg.setdefault("voice", {})
        ai      = cfg.setdefault("ai", {})
        conv    = cfg.setdefault("conversation", {})
        ui      = cfg.setdefault("ui", {})

        try:
            raphail["user_name"] = self._vars["user_name"].get().strip()
            words = [w.strip() for w in self._vars["wake_words"].get().split(",") if w.strip()]
            if words:
                raphail["wake_words"] = words

            voice["silence_duration"] = float(self._vars["silence_duration"].get())
            voice["tts_voice_uz"]     = self._vars["tts_voice_uz"].get().strip()

            ai["model"]       = self._vars["ai_model"].get().strip()
            ai["temperature"] = float(self._vars["ai_temperature"].get())

            conv["followup"]         = bool(self._vars["followup"].get())
            conv["followup_timeout"] = float(self._vars["followup_timeout"].get())

            ui["show_on_start"] = bool(self._vars["show_on_start"].get())
        except ValueError as e:
            messagebox.showerror("Noto'g'ri qiymat", f"Raqamli maydonni tekshiring:\n{e}", parent=self)
            return

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            messagebox.showerror("Xato", f"config.yaml saqlanmadi:\n{e}", parent=self)
            return

        messagebox.showinfo(
            "Saqlandi",
            "Sozlamalar saqlandi. Kuchga kirishi uchun RAFAEL'ni qayta ishga tushiring.",
            parent=self,
        )
        self.destroy()

    # ─── UI ──────────────────────────────────────────────────────────────────

    def _section(self, parent, title: str):
        tk.Label(
            parent, text=title, font=theme.FONT_SMALL,
            bg=theme.BG_DEEP, fg=theme.TEXT_ACCENT,
        ).pack(fill=tk.X, padx=16, pady=(14, 4))

    def _field(self, parent, label: str, key: str, value, kind="text"):
        row = tk.Frame(parent, bg=theme.BG_DEEP)
        row.pack(fill=tk.X, padx=16, pady=4)

        tk.Label(
            row, text=label, font=theme.FONT_BODY,
            bg=theme.BG_DEEP, fg=theme.TEXT_PRIMARY,
            anchor="w", width=18,
        ).pack(side=tk.LEFT)

        if kind == "bool":
            var = tk.BooleanVar(value=bool(value))
            tk.Checkbutton(
                row, variable=var, bg=theme.BG_DEEP,
                activebackground=theme.BG_DEEP,
                selectcolor=theme.BG_GLASS,
            ).pack(side=tk.LEFT)
        else:
            var = tk.StringVar(value=str(value))
            tk.Entry(
                row, textvariable=var, font=theme.FONT_BODY,
                bg=theme.BG_GLASS, fg=theme.TEXT_PRIMARY,
                insertbackground=theme.TEXT_PRIMARY,
                relief=tk.FLAT,
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)

        self._vars[key] = var

    def _build_ui(self):
        cfg     = self._config
        raphail = cfg.get("raphail", {})
        voice   = cfg.get("voice", {})
        ai      = cfg.get("ai", {})
        conv    = cfg.get("conversation", {})
        ui      = cfg.get("ui", {})

        tk.Label(
            self, text="Sozlamalar", font=theme.FONT_TITLE,
            bg=theme.BG_DEEP, fg=theme.TEXT_PRIMARY,
        ).pack(fill=tk.X, padx=16, pady=(16, 0))

        self._section(self, "Umumiy")
        self._field(self, "Ism", "user_name", raphail.get("user_name", ""))
        self._field(self, "Chaqiruv so'zlari", "wake_words",
                    ", ".join(raphail.get("wake_words", []) or []))

        self._section(self, "Ovoz")
        self._field(self, "Jim turish (sekund)", "silence_duration",
                    voice.get("silence_duration", 2.2))
        self._field(self, "TTS ovozi", "tts_voice_uz",
                    voice.get("tts_voice_uz", "uz-UZ-MadinaNeural"))

        self._section(self, "AI")
        self._field(self, "Model", "ai_model", ai.get("model", "claude-opus-4-8"))
        self._field(self, "Temperature", "ai_temperature", ai.get("temperature", 0.7))

        self._section(self, "Suhbat")
        self._field(self, "Follow-up yoqilgan", "followup",
                    conv.get("followup", True), kind="bool")
        self._field(self, "Follow-up timeout (s)", "followup_timeout",
                    conv.get("followup_timeout", 7))

        self._section(self, "Interfeys")
        self._field(self, "Boshlanishda ko'rsat", "show_on_start",
                    ui.get("show_on_start", True), kind="bool")

        # ── Tugmalar ──────────────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=theme.BG_DEEP)
        btn_row.pack(fill=tk.X, padx=16, pady=20, side=tk.BOTTOM)

        tk.Button(
            btn_row, text="Bekor qilish", font=theme.FONT_BODY,
            bg=theme.BG_GLASS, fg=theme.TEXT_SECONDARY,
            activebackground=theme.BG_HOVER, relief=tk.FLAT,
            padx=12, pady=6, cursor="hand2",
            command=self.destroy,
        ).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(
            btn_row, text="Saqlash", font=theme.FONT_BODY,
            bg=theme.TEXT_ACCENT, fg=theme.BG_DEEP,
            activebackground=theme.ORB_GLOW, relief=tk.FLAT,
            padx=12, pady=6, cursor="hand2",
            command=self._save_config,
        ).pack(side=tk.RIGHT)
