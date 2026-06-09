"""
RAFAEL v2.0 — lang_detect.py testlari
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.utils.lang_detect import detect, tts_voice


def test_uzbek():
    assert detect("Salom, bugun nima qilamiz?") == "uz"
    assert detect("Chrome ni och") == "uz"
    assert detect("qo'shiq ijro et") == "uz"
    assert detect("Noutbookni o'chirib qo'y") == "uz"

def test_russian():
    assert detect("Привет, как дела?") == "ru"
    assert detect("открой браузер") == "ru"
    assert detect("выключи компьютер") == "ru"

def test_english():
    assert detect("open chrome browser") == "en"
    assert detect("search for python tutorials") == "en"
    assert detect("close the terminal") == "en"

def test_empty():
    assert detect("") == "uz"
    assert detect("   ") == "uz"

def test_tts_voice():
    cfg = {
        "voice": {
            "tts_voice_uz": "uz-UZ-MadinaNeural",
            "tts_voice_ru": "ru-RU-SvetlanaNeural",
            "tts_voice_en": "en-US-JennyNeural",
        }
    }
    assert tts_voice("uz", cfg) == "uz-UZ-MadinaNeural"
    assert tts_voice("ru", cfg) == "ru-RU-SvetlanaNeural"
    assert tts_voice("en", cfg) == "en-US-JennyNeural"
    assert tts_voice("xx", cfg) == "uz-UZ-MadinaNeural"  # default
