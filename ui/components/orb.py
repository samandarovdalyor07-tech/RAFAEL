"""
RAFAEL v2.0 — Voice Orb Widget
4 holat: sleeping | listening | thinking | speaking
Tkinter Canvas asosida animatsiya.
"""

import math
import tkinter as tk
from ui import theme


class VoiceOrb(tk.Canvas):
    """Animatsiyali ovoz orbi."""

    def __init__(self, master, size: int = theme.ORB_SIZE, **kwargs):
        super().__init__(
            master,
            width=size,
            height=size,
            bg=theme.BG_DEEP,
            highlightthickness=0,
            **kwargs,
        )
        self.size    = size
        self.cx      = size // 2
        self.cy      = size // 2
        self.r       = theme.ORB_RADIUS

        self._state  = "sleeping"
        self._phase  = 0.0      # animatsiya fazasi (0..2π)
        self._angle  = 0.0      # aylanish burchagi
        self._after  = None

        self._draw()
        self._tick()

    # ─── Public ──────────────────────────────────────────────────────────────

    def set_state(self, state: str):
        """state ∈ {sleeping, listening, thinking, speaking}"""
        if state not in theme.STATE_COLORS:
            state = "sleeping"
        if self._state != state:
            self._state = state
            self._phase = 0.0

    # ─── Animation loop ──────────────────────────────────────────────────────

    def _tick(self):
        self._phase += theme.PULSE_SPEED
        if self._phase > math.tau:
            self._phase -= math.tau
        self._angle = (self._angle + theme.SPIN_SPEED) % 360

        self._draw()
        self._after = self.after(theme.ANIM_STEP_MS, self._tick)

    def _draw(self):
        self.delete("all")
        s = self._state

        if s == "sleeping":
            self._draw_sleeping()
        elif s == "listening":
            self._draw_listening()
        elif s == "thinking":
            self._draw_thinking()
        elif s == "speaking":
            self._draw_speaking()

    # ─── Sleeping: dim pulsing circle ────────────────────────────────────────

    def _draw_sleeping(self):
        pulse = 0.85 + 0.15 * math.sin(self._phase * 0.5)
        r     = int(self.r * pulse)
        # Outer glow (dim)
        self._oval(self.cx, self.cy, r + 10, theme.ORB_SLEEP, alpha_hex="22")
        self._oval(self.cx, self.cy, r + 5,  theme.ORB_SLEEP, alpha_hex="44")
        # Core
        self._oval(self.cx, self.cy, r, theme.ORB_SLEEP)
        # Inner highlight
        self._oval(self.cx - r//5, self.cy - r//5, r//4, "#2563EB", alpha_hex="88")

    # ─── Listening: breathing pulse + mic waves ───────────────────────────────

    def _draw_listening(self):
        breath = 0.9 + 0.1 * math.sin(self._phase * 1.5)
        r      = int(self.r * breath)
        # Expanding rings
        for i in range(3):
            ph   = (self._phase + i * 0.7) % math.tau
            ring = r + int(15 + 10 * i * math.sin(ph * 2))
            alpha = max(10, int(80 - i * 25))
            self._oval_outline(self.cx, self.cy, ring, theme.ORB_LISTEN,
                               width=2, alpha_hex=f"{alpha:02x}")
        # Core
        self._oval(self.cx, self.cy, r, theme.ORB_LISTEN)
        self._oval(self.cx - r//5, self.cy - r//5, r//3, "#60A5FA", alpha_hex="99")
        # Mic bars (3 vertical bars in centre)
        self._draw_bars()

    def _draw_bars(self):
        """Mikrofon animatsiyasi — 3 ta vertikal chiziq."""
        cx, cy = self.cx, self.cy
        bar_w  = 3
        gap    = 6
        heights= [
            int(10 + 8 * abs(math.sin(self._phase * 2.1))),
            int(14 + 10 * abs(math.sin(self._phase * 1.7 + 0.5))),
            int(10 + 8 * abs(math.sin(self._phase * 2.3 + 1.0))),
        ]
        for i, h in enumerate(heights):
            x = cx + (i - 1) * (bar_w + gap)
            self.create_rectangle(
                x - bar_w//2, cy - h,
                x + bar_w//2, cy + h,
                fill=theme.ORB_RING, outline=""
            )

    # ─── Thinking: rotating arcs ─────────────────────────────────────────────

    def _draw_thinking(self):
        r = self.r
        # Core (dim)
        self._oval(self.cx, self.cy, r, theme.ORB_THINK)
        self._oval(self.cx - r//5, self.cy - r//5, r//3, "#A855F7", alpha_hex="99")
        # 3 rotating arcs
        for i in range(3):
            start = (self._angle + i * 120) % 360
            self._arc(self.cx, self.cy, r + 8 + i * 7,
                      start, 70, theme.ORB_GLOW, width=2 + i)
        # Dots on outer ring
        for i in range(8):
            a  = math.radians(self._angle + i * 45)
            rx = self.cx + int((r + 18) * math.cos(a))
            ry = self.cy + int((r + 18) * math.sin(a))
            dot_r = 2 if i % 2 == 0 else 3
            self._oval(rx, ry, dot_r, theme.ORB_GLOW)

    # ─── Speaking: ripple rings ───────────────────────────────────────────────

    def _draw_speaking(self):
        r = self.r
        # Ripple rings (expanding)
        for i in range(4):
            ph   = (self._phase + i * math.pi / 2) % math.tau
            expand = int(8 + 12 * ((ph / math.tau)))
            alpha  = max(10, int(100 - expand * 3))
            self._oval_outline(self.cx, self.cy, r + expand + i * 8,
                               theme.ORB_SPEAK, width=2, alpha_hex=f"{alpha:02x}")
        # Core
        self._oval(self.cx, self.cy, r, theme.ORB_SPEAK)
        self._oval(self.cx - r//5, self.cy - r//5, r//3, "#22D3EE", alpha_hex="99")
        # Sound wave lines
        self._draw_sound_wave()

    def _draw_sound_wave(self):
        """Ovoz to'lqini animatsiyasi."""
        w = self.r - 8
        steps = 30
        points = []
        for i in range(steps + 1):
            t = i / steps
            x = self.cx - w + int(2 * w * t)
            amp = int(12 * math.sin(self._phase * 3 + t * math.tau * 2.5))
            y   = self.cy + amp
            points.extend([x, y])
        if len(points) >= 4:
            self.create_line(points, fill=theme.ORB_RING, width=2, smooth=True)

    # ─── Drawing primitives ───────────────────────────────────────────────────

    def _oval(self, cx, cy, r, color, alpha_hex=""):
        """Filled circle."""
        fill = color  # tkinter alpha rengini to'g'ridan qo'llab-quvvatlamaydi
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=fill, outline="")

    def _oval_outline(self, cx, cy, r, color, width=1, alpha_hex=""):
        """Outline circle."""
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline=color, width=width, fill="")

    def _arc(self, cx, cy, r, start_deg, extent_deg, color, width=2):
        self.create_arc(cx - r, cy - r, cx + r, cy + r,
                        start=start_deg, extent=extent_deg,
                        style=tk.ARC, outline=color, width=width)

    def destroy(self):
        if self._after:
            self.after_cancel(self._after)
        super().destroy()
