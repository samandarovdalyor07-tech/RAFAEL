"""
RAFAEL v2.0 — UI Theme
Futuristik dark/glassmorphism palette.
"""

# ─── Asosiy ranglar ──────────────────────────────────────────────────────────
BG_DEEP     = "#070B14"   # Eng qoʻngʻir qora fon
BG_PANEL    = "#0D1320"   # Panel foni
BG_GLASS    = "#111827"   # Glassmorphism karta
BG_HOVER    = "#1A2035"   # Hover holati
BORDER      = "#1E293B"   # Chegara
BORDER_GLOW = "#3B82F6"   # Faol chegara (ko'k glow)

# ─── Matn ranglari ───────────────────────────────────────────────────────────
TEXT_PRIMARY   = "#E2E8F0"  # Asosiy matn (oq-kulrang)
TEXT_SECONDARY = "#64748B"  # Ikkinchi darajali
TEXT_MUTED     = "#334155"  # Soʻngan matn
TEXT_ACCENT    = "#38BDF8"  # Ko'k aksent
TEXT_SUCCESS   = "#34D399"  # Yashil muvaffaqiyat
TEXT_WARN      = "#FBBF24"  # Sariq ogohlantirish
TEXT_ERROR     = "#F87171"  # Qizil xato

# ─── Orb ranglari ────────────────────────────────────────────────────────────
ORB_SLEEP     = "#1E3A5F"   # Uxlayapti — koʻk-qoʻngʻir
ORB_LISTEN    = "#1D4ED8"   # Tinglayapti — yorqin ko'k
ORB_THINK     = "#7C3AED"   # Fikrlayapti — binafsha
ORB_SPEAK     = "#0891B2"   # Gapirmoqda — cyan
ORB_GLOW      = "#60A5FA"   # Glow effekti
ORB_RING      = "#93C5FD"   # Tashqi halqa

# ─── Gradient uchun ─────────────────────────────────────────────────────────
GRAD_START    = "#1E3A5F"
GRAD_END      = "#0F172A"

# ─── Shriftlar ───────────────────────────────────────────────────────────────
FONT_FAMILY   = "Segoe UI"
FONT_MONO     = "Consolas"

FONT_TITLE    = (FONT_FAMILY, 13, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 10, "normal")
FONT_BODY     = (FONT_FAMILY, 10, "normal")
FONT_SMALL    = (FONT_FAMILY, 9,  "normal")
FONT_TINY     = (FONT_FAMILY, 8,  "normal")
FONT_CODE     = (FONT_MONO,   10, "normal")

# ─── O'lchamlar ──────────────────────────────────────────────────────────────
WINDOW_W      = 520
WINDOW_H      = 720
PANEL_PAD     = 12
CORNER_R      = 8
ORB_SIZE      = 120     # px (canvas width & height)
ORB_RADIUS    = 45      # orb circle radius
STATUS_H      = 28
HISTORY_H     = 320     # scrollable history panel height

# ─── Animatsiya ──────────────────────────────────────────────────────────────
ANIM_FPS      = 30      # kadr/soniya
ANIM_STEP_MS  = 1000 // ANIM_FPS   # ~33ms
PULSE_SPEED   = 0.05    # nafas olish tezligi
SPIN_SPEED    = 4       # aylanish daraja/kadr

# ─── Holat ranglari (status bar) ─────────────────────────────────────────────
STATE_COLORS = {
    "sleeping":  TEXT_MUTED,
    "listening": ORB_LISTEN,
    "thinking":  ORB_THINK,
    "speaking":  ORB_SPEAK,
    "error":     TEXT_ERROR,
}
STATE_LABELS = {
    "sleeping":  "Kutmoqda...",
    "listening": "Tinglayapman",
    "thinking":  "Tahlil qilmoqda...",
    "speaking":  "Gapirmoqda",
    "error":     "Xato yuz berdi",
}
