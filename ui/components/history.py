"""
RAFAEL v2.0 — Command History Panel
Scrollable, rang-barang, timestamp bilan.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui import theme


class HistoryPanel(tk.Frame):
    """Buyruqlar tarixi paneli."""

    def __init__(self, master, max_lines: int = 200, **kwargs):
        super().__init__(master, bg=theme.BG_PANEL, **kwargs)
        self.max_lines = max_lines
        self._line_count = 0

        self._build()

    def _build(self):
        # Sarlavha
        header = tk.Frame(self, bg=theme.BG_PANEL)
        header.pack(fill=tk.X, padx=theme.PANEL_PAD, pady=(8, 4))

        tk.Label(
            header,
            text="◈  TARIX",
            font=theme.FONT_SMALL,
            bg=theme.BG_PANEL,
            fg=theme.TEXT_SECONDARY,
            anchor="w",
        ).pack(side=tk.LEFT)

        self._clear_btn = tk.Label(
            header,
            text="✕ tozala",
            font=theme.FONT_TINY,
            bg=theme.BG_PANEL,
            fg=theme.TEXT_MUTED,
            cursor="hand2",
        )
        self._clear_btn.pack(side=tk.RIGHT)
        self._clear_btn.bind("<Button-1>", lambda e: self.clear())
        self._clear_btn.bind("<Enter>",
                             lambda e: self._clear_btn.config(fg=theme.TEXT_ERROR))
        self._clear_btn.bind("<Leave>",
                             lambda e: self._clear_btn.config(fg=theme.TEXT_MUTED))

        # Ajratuvchi chiziq
        sep = tk.Frame(self, bg=theme.BORDER, height=1)
        sep.pack(fill=tk.X, padx=0)

        # Scrollable text
        container = tk.Frame(self, bg=theme.BG_PANEL)
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self._text = tk.Text(
            container,
            bg=theme.BG_PANEL,
            fg=theme.TEXT_PRIMARY,
            font=theme.FONT_BODY,
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD,
            state=tk.DISABLED,
            cursor="arrow",
            selectbackground=theme.BG_HOVER,
            insertbackground=theme.TEXT_PRIMARY,
            pady=4,
        )
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        sb = ttk.Scrollbar(container, orient=tk.VERTICAL,
                           command=self._text.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._text.configure(yscrollcommand=sb.set)

        # Matn teglari (rang uchun)
        self._text.tag_configure("time",    foreground=theme.TEXT_MUTED,
                                 font=theme.FONT_TINY)
        self._text.tag_configure("user",    foreground=theme.TEXT_ACCENT,
                                 font=(theme.FONT_FAMILY, 10, "bold"))
        self._text.tag_configure("rafael",  foreground=theme.TEXT_SUCCESS,
                                 font=theme.FONT_BODY)
        self._text.tag_configure("system",  foreground=theme.TEXT_WARN,
                                 font=theme.FONT_SMALL)
        self._text.tag_configure("error",   foreground=theme.TEXT_ERROR,
                                 font=theme.FONT_SMALL)
        self._text.tag_configure("cmd",     foreground=theme.ORB_GLOW,
                                 font=theme.FONT_CODE)
        self._text.tag_configure("divider", foreground=theme.BORDER,
                                 font=theme.FONT_TINY)

    # ─── Public API ──────────────────────────────────────────────────────────

    def add_user(self, text: str):
        """Foydalanuvchi buyrug'ini qo'shing."""
        self._append_line(
            f"  ▷ {text}",
            tag="user",
            prefix_tag="time",
        )

    def add_rafael(self, text: str):
        """RAFAEL javobini qo'shing."""
        self._append_line(
            f"  ◈ {text}",
            tag="rafael",
            prefix_tag="time",
        )

    def add_command(self, action: str, detail: str = ""):
        """Bajarilgan buyruqni qo'shing."""
        msg = f"  ⚡ [{action}]"
        if detail:
            msg += f"  {detail}"
        self._append_line(msg, tag="cmd")

    def add_system(self, text: str):
        """Tizim xabarini qo'shing."""
        self._append_line(f"  ⊕ {text}", tag="system")

    def add_error(self, text: str):
        """Xato xabarini qo'shing."""
        self._append_line(f"  ✕ {text}", tag="error")

    def clear(self):
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.configure(state=tk.DISABLED)
        self._line_count = 0

    # ─── Internal ────────────────────────────────────────────────────────────

    def _append_line(self, text: str, tag: str, prefix_tag: str = None):
        now = datetime.now().strftime("%H:%M:%S")

        self._text.configure(state=tk.NORMAL)

        # Eski qatorlarni chiqarib tashlash
        if self._line_count >= self.max_lines:
            self._text.delete("1.0", "2.0")
            self._line_count -= 1

        if prefix_tag:
            self._text.insert(tk.END, f" {now}  ", prefix_tag)
        self._text.insert(tk.END, text + "\n", tag)
        self._line_count += 1

        self._text.configure(state=tk.DISABLED)
        self._text.see(tk.END)  # Eng pastga scroll
