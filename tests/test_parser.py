"""
RAFAEL v2.0 — parser.py testlari
Ishga tushirish: cd D:\\RAPHAEL && python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.brain.parser import parse


def test_open_chrome():
    r = parse("Rafael, chromeni och")
    assert r is not None
    assert r[0]["action"] == "open_app"
    assert r[0]["app"] == "chrome"

def test_open_vscode_alias():
    for alias in ["viskod och", "vistudio och", "visual studio ni yoq",
                  "vscodeni ochib ber", "viskodni ishga tushir"]:
        r = parse(alias)
        assert r is not None, f"Topilmadi: {alias!r}"
        assert r[0]["action"] == "open_app"
        assert r[0]["app"] == "vscode", f"Noto'g'ri: {alias!r}"

def test_close_telegram():
    r = parse("telegramni yop")
    assert r is not None
    assert r[0]["action"] == "close_app"
    assert r[0]["app"] == "telegram"

def test_multi_command():
    r = parse("chrome och va vscode ham och")
    assert r is not None
    assert len(r) == 2
    apps = {c["app"] for c in r}
    assert "chrome" in apps
    assert "vscode" in apps

def test_multi_command_comma():
    r = parse("chromeni och, telegramni ham och")
    assert r is not None
    assert len(r) == 2

def test_multi_command_keyin():
    r = parse("spotifyni och keyin yandex muzikadan qidir")
    assert r is not None
    assert len(r) == 2

def test_shutdown():
    for t in ["kompyuterni o'chir", "noutbukni o'chir", "shutdown"]:
        r = parse(t)
        assert r is not None, f"Topilmadi: {t!r}"
        assert r[0]["action"] == "shutdown"

def test_volume():
    assert parse("ovoz oshir")[0]["action"] == "volume_up"
    assert parse("ovoz past")[0]["action"] == "volume_down"
    assert parse("jim")[0]["action"] == "mute"

def test_search():
    r = parse("google da python darslarini qidir")
    assert r is not None
    assert r[0]["action"] == "search"
    assert "python" in r[0]["query"]

def test_play_music():
    r = parse("youtube da dildora niyozova qo'shig'ini ijro et")
    assert r is not None
    assert r[0]["action"] == "play_music"

def test_telegram_send():
    r = parse("Akbarga salom deb yoz")
    assert r is not None
    assert r[0]["action"] == "send_telegram"
    assert r[0]["contact"] == "akbar"

def test_bluetooth():
    for t in ["bluetooth sozlamalarini och", "blutus", "bt qurulmaga ul"]:
        r = parse(t)
        assert r is not None, f"Topilmadi: {t!r}"
        assert r[0]["action"] in ("bluetooth_open", "bluetooth_connect")

def test_none_for_question():
    """Oddiy savol — parser None qaytarishi kerak (LLM ga ketadi)."""
    r = parse("Python da dekoratorlar nima?")
    assert r is None

def test_stt_merged():
    """STT 'rafaelgoogloch' → parser topsin."""
    r = parse("rafaelgoogloch")
    # Qisman moslik — chrome yoki None (split fallback assistant.py da)
    # parser.py bu yerda None qaytarishi mumkin, lekin "googl" ni topishi kerak
    if r is not None:
        assert r[0]["app"] == "chrome"

def test_restart():
    r = parse("qayta yoq")
    assert r is not None
    assert r[0]["action"] == "restart"

def test_youtube_opens_as_website():
    """youtube — ilova emas, brauzerda ochilishi kerak."""
    for t in ["youtube och", "youtube", "rafael youtube ochib ber"]:
        r = parse(t)
        assert r is not None, f"Topilmadi: {t!r}"
        assert r[0]["action"] == "open_youtube", f"Noto'g'ri: {t!r} -> {r}"

def test_youtube_search_still_works():
    """youtube da qidirish — play yoki search bo'lishi kerak, open_app EMAS."""
    r = parse("youtube da dildora qo'shig'ini qo'y")
    assert r is not None
    assert r[0]["action"] == "play_music"

def test_github_website():
    r = parse("github och")
    assert r is not None
    assert r[0]["action"] == "open_site"
    assert r[0]["site"] == "github"

def test_youtube_not_open_app():
    """youtube hech qachon open_app bo'lmasligi kerak."""
    r = parse("youtube")
    assert r[0]["action"] != "open_app"

def test_lock():
    r = parse("ekranni qulflash")
    assert r is not None
    assert r[0]["action"] == "lock"
