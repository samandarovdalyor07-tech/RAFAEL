"""
RAPHAIL - Wake Word Detector
"Raphail" so'zi bilan aktivatsiya.
"""

import re
from core.utils.logger import get_logger

logger = get_logger(__name__)

WAKE_WORDS = [
    "rafael", "рафаел", "рафаель",
    "hey rafael", "ey rafael",
    "raphael", "raphail", "рафаил",
]


def contains_wake_word(text: str) -> tuple[bool, str]:
    """
    Matnda wake word borligini tekshiradi.
    Returns: (found: bool, cleaned_text: str)
    """
    if not text:
        return False, ""

    lower = text.lower().strip()

    for wake in WAKE_WORDS:
        if wake in lower:
            # Wake wordni olib tashlaymiz
            cleaned = re.sub(re.escape(wake), "", lower, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'^[,\.!\s]+', '', cleaned).strip()
            logger.debug(f"Wake word topildi: '{wake}' → '{cleaned}'")
            return True, cleaned

    return False, text


def is_stop_command(text: str) -> bool:
    """
    RAFAELni uxlatish/to'xtatish buyrug'ini tekshiradi.
    DIQQAT: "kompyuterni o'chir" (shutdown) bilan ARALASHMASLIGI kerak —
    shuning uchun kompyuter/noutbuk konteksti bo'lsa, bu stop EMAS.
    """
    lower = text.lower().strip()

    # Kompyuter o'chirish konteksti — bu stop EMAS, shutdown
    pc_context = ["kompyuter", "kompni", "noutbuk", "noutbukni", "komp ",
                  "компьютер", "ноутбук", "ekran", "monitor"]
    if any(w in lower for w in pc_context):
        return False

    # RAFAELni to'xtatish — aniq iboralar (apostrofli va apostrofsiz)
    stop_words = [
        "to'xta", "toxta", "тўхта", "стоп", "stop",
        "chiqish", "чиқиш", "exit", "quit",
        "o'chib qol", "ochib qol", "uxla", "выключись", "xayr", "пока",
        "seni o'chir", "seni ochir", "o'zingni o'chir", "ozingni ochir",
    ]
    return any(w in lower for w in stop_words)
