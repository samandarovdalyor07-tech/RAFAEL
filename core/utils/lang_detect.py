"""
RAFAEL - Language Detector
O'zbek | Rus | Ingliz tilini avtomatik aniqlaydi.
"""

import re

RU_CHARS = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
EN_WORDS = {"the","is","are","was","were","have","has","will","can","you",
            "i","my","your","open","close","play","search","find","stop",
            "browser","chrome","windows","computer","laptop","start","exit",
            "volume","settings","bluetooth","connect","download","update","run",
            "please","hello","hey","what","how","when","where","who","why",
            "for","to","of","in","on","at","with","about","and","or","not",
            "me","it","this","that","get","set","show","list","go","do",
            "python","code","file","folder","music","video","tutorial","app"}
UZ_PATTERNS = ["sh","ch","ng","ni","ga","da","bilan","uchun","qil","och","yop"]


def detect(text: str) -> str:
    """'uz' | 'ru' | 'en' qaytaradi"""
    if not text:
        return "uz"
    t = text.strip()
    total = max(len([c for c in t if c.isalpha()]), 1)

    # Kirill harflari → Rus
    ru_count = sum(1 for c in t if c in RU_CHARS)
    if ru_count / total > 0.3:
        return "ru"

    # Ingliz so'zlari → Ingliz
    words = set(re.findall(r'\b\w+\b', t.lower()))
    en_hits = len(words & EN_WORDS)
    if en_hits >= 2:
        return "en"

    # O'zbek patternlari
    tl = t.lower()
    uz_hits = sum(1 for p in UZ_PATTERNS if p in tl)
    if uz_hits >= 1:
        return "uz"

    # Ko'p lotin harfi — ingliz yoki o'zbek
    if en_hits >= 1:
        return "en"

    return "uz"  # default


def tts_voice(lang: str, config: dict) -> str:
    """Tilga qarab TTS voice qaytaradi"""
    voice_cfg = config.get("voice", {})
    if lang == "ru":
        return voice_cfg.get("tts_voice_ru", "ru-RU-SvetlanaNeural")
    if lang == "en":
        return voice_cfg.get("tts_voice_en", "en-US-JennyNeural")
    return voice_cfg.get("tts_voice_uz", "uz-UZ-MadinaNeural")
