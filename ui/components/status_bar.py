"""
RAFAEL v2.0 — Status Bar
Holat ko'rsatgichi: uxlayapti / tinglayapti / fikrlayapti / gapirmoqda
"""

import tkinter as tk
from ui import theme


class StatusBar(tk.Frame):
    """Pastki status paneli."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            bg=theme.BG_PANEL,
            height=theme.STATUS_H,
            **kwargs,
        )
        self.pack_propagate(False)
        self._state = "sleeping"
        self._build()

    def _build(self):
        # Yuqori chegara chizig'i
        line = tk.Frame(self, bg=theme.BORDER, height=1)
        line.pack(fill=tk.X, side=tk.TOP)

        inner = tk.Frame(self, bg=theme.BG_PANEL)
        inner.pack(fill=tk.BOTH, expand=True, padx=theme.PANEL_PAD, pady=2)

        # Holat nuqtasi (rang rangi)
        self._dot = tk.Label(
            inner,
            text="●",
            font=(theme.FONT_FAMILY, 10),
            bg=theme.BG_PANEL,
            fg=theme.TEXT_MUTED,
        )
        self._dot.pack(side=tk.LEFT, padx=(0, 5))

        # Holat matni
        self._label = tk.Label(
            inner,
            text=theme.STATE_LABELS.get("sleeping", ""),
            font=theme.FONT_SMALL,
            bg=theme.BG_PANEL,
            fg=theme.TEXT_MUTED,
            anchor="w",
        )
        self._label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # RAFAEL nomi o'ngda
        tk.Label(
            inner,
            text="RAFAEL v2.0",
            font=theme.FONT_TINY,
            bg=theme.BG_PANEL,
            fg=theme.TEXT_MUTED,
        ).pack(side=tk.RIGHT)

    def set_state(self, state: str):
        """state ∈ {sleeping, listening, thinking, speaking, error}"""
        if state not in theme.STATE_COLORS:
            state = "error"
        self._state = state
        color = theme.STATE_COLORS[state]
        label = theme.STATE_LABELS.get(state, state)

        self._dot.configure(fg=color)
        self._label.configure(text=label, fg=color)

    def set_text(self, text: str):
        """Ixtiyoriy qo'shimcha matn ko'rsatish."""
        self._label.configure(text=text)
