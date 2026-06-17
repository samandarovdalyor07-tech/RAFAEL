"""
RAFAEL v2.0 — Command Parser
Keyword-based, millisecond speed. Runs BEFORE LLM.
Multi-command split: "chrome och va vscode ham och"
Returns: list[dict] | None
"""

import re
from typing import Optional

# ══════════════════════════════════════════════════════════════
#  ILOVALAR
# ══════════════════════════════════════════════════════════════
APP_WORDS: dict = {
    "chrome":     ["chrome","xrom","xrome","google chrome","brauzer","браузер","хром",
                   "chromeni","xromni","google","googl","gugl","кром","googlechrome",
                   "googlochrome","googloch"],
    "telegram":   ["telegram","telegam","telegaram","telegramm","telega","телеграм",
                   "telegramda","telegramni","telegramga"],
    "spotify":    ["spotify","spotifay","спотифай","spotifi"],
    "vscode":     ["vs code","vscode","vs kod","visual studio","visual studio code",
                   "viskod","viskot","viskodum","viskoda","viskotda","vscodum","vscodda",
                   "vizual studio","vizual","visual kode","visualstudio","vistudio",
                   "vistudyo","vistudioni","kod muharriri","редактор кода","code editor",
                   "vscodeni","vskodini","visualstudiocode"],
    "notepad":    ["notepad","bloknot","matn muharriri","блокнот","notpad","notepadni"],
    "calculator": ["calculator","kalkulyator","hisob","hisoblagich","калькулятор","kalkulator","calc"],
    "explorer":   ["explorer","fayl menejeri","papkalar","проводник","mening kompyuterim",
                   "file explorer","papka","fayl","files","windows explorer"],
    "terminal":   ["terminal","konsol","cmd","buyruq satri","терминал","командная строка",
                   "command prompt","komandnaya stroka"],
    "powershell": ["powershell","пауэршелл","пауэр шелл","power shell"],
    "task_manager":["task manager","vazifa menejeri","диспетчер задач","диспетчер",
                    "task menejeri","taskmgr","jarayonlar","ctrl alt del"],
    "firefox":    ["firefox","файерфокс","fire fox"],
    "edge":       ["edge","microsoft edge","эдж"],
    "word":       ["word","microsoft word","ворд","wordni","wordda","hujjat","dokument"],
    "excel":      ["excel","microsoft excel","эксел","excelni","jadval"],
    "vlc":        ["vlc","vlc player","видео плеер","mediaplayer"],
    "settings":   ["sozlamalar","settings","параметры","nastroyki","nastroykalar",
                   "windows settings","sozlamani","parametrlar"],
    "camera":     ["camera","kamera","фотоаппарат","webcam","veb kamera","фотик"],
}

# ══════════════════════════════════════════════════════════════
#  VEB-SAYTLAR (ilova emas — brauzerda ochiladi)
# ══════════════════════════════════════════════════════════════
WEBSITES: dict = {
    "youtube":      ["youtube","yutub","you tube","ютуб","youtubeni","yutubni"],
    "yandex music": ["yandex muzika","yandex music","яндекс музыка","yandeks muzika",
                     "yandex musiqa"],
    "yandex":       ["yandexni","yandex ni","яндекс","yandeksni"],
    "github":       ["github","гитхаб","git hub"],
    "gmail":        ["gmail","джимейл","pochta","почта","jimeyl"],
    "chatgpt":      ["chatgpt","chat gpt","чатгпт","chat dji pi ti"],
    "wikipedia":    ["wikipedia","vikipediya","википедия","wiki"],
}

# ══════════════════════════════════════════════════════════════
#  QIDIRUV TIZIMLARI
# ══════════════════════════════════════════════════════════════
SEARCH_ENGINES = {
    "yandex_music": ["yandex music","yandex muzika","яндекс музыка","yandex musiqada",
                     "yandex musiqa","яндекс музыке","yandeks muzika"],
    "youtube":      ["youtubeda","youtube da","ютубе","ютуб","youtube","youtubedan",
                     "yutube","yutubedan","ютубда"],
    "yandex":       ["yandexda","yandex da","яндексе","яндекс","yandex","yandeks"],
    "google":       ["googleda","google da","гугл","гугле","google"],
}

# ══════════════════════════════════════════════════════════════
#  KALIT SO'ZLAR
# ══════════════════════════════════════════════════════════════
OPEN_WORDS  = [
    "och","ochib ber","ochvorchi","ishga tushir","yoq","start","chiqar","ko'rsat",
    "открой","запусти","включи","открыть","open","launch","run",
]
CLOSE_WORDS = [
    "yop","yopib","yopvorchi","o'chir","закрой","close","stop","выключи",
    "завершить","kill","exit","quit","yopqil",
]
SEARCH_WORDS = [
    "qidir","topib ber","topvorchi","izla","найди","поищи","search","find",
    "qidirish","najdi","поискать","izlab ber","izlavorchi","googla",
]
PLAY_WORDS = [
    "ijro et","qo'y","chalvorchi","tinglatib ber","play","поставь",
    "включи музыку","qo'shiq qo'y","musiqa qo'y","включи","listen",
    "tingla","chalvorchi","eshit","ijro","kuy","ashula","qushiq",
    "qo'shiq","yangrat","radio",
]
# Kompyuter konteksti — "o'chir" so'zini shutdown deb hisoblash uchun SHART.
# Aks holda "telegramni o'chir" (ilovani yop) butun noutbukni o'chirib yuboradi!
PC_CONTEXT = [
    "kompyuter","kompyuterni","komp","kompni","noutbuk","noutbukni","notebook",
    "pc","tizim","tizimni","sistema","компьютер","ноутбук","систему","системы",
]
# Kontekstsiz ham aniq shutdown bo'ladigan iboralar
SHUTDOWN_EXPLICIT = [
    "shutdown","poweroff","power off","turn off","выключи компьютер",
    "выключить","kompyuterni o'chir","noutbukni o'chir","kompni o'chir",
    "kompyuter o'chir","o'chirib yubor",
]
# "o'chir" tipidagi fe'llar — faqat PC_CONTEXT bilan birga shutdown bo'ladi.
# Yolg'iz (ilova nomi bilan) kelsa — bu close_app (ilovani yopish).
SHUTDOWN_VERBS = ["o'chir","uchir","uchirgin","выключи"]
RESTART_WORDS = [
    "qayta yoq","qayta ishga tushir","restart","перезагрузи","reboot",
    "перезагрузить","qayta ishga tushirish",
]
SLEEP_WORDS = [
    "uxlat","uyquga","sleep","спящий режим","uxlash","splyat","засыпай","hibernate",
    "uxlatib qo'y","uxlash rejimi",
]
LOCK_WORDS = [
    "qulfla","block","lock","заблокируй","экран заблокировать","ekranni qulflash",
    "qulflash","qulflab qo'y",
]
TIME_WORDS = [
    "soat necha","soatnecha","vaqt","время","сколько времени",
    "qancha vaqt","sana","bugun necha","what time","current time","hozir soat",
    "bugun sana","necha san","nechanchi",
]
SCREENSHOT_WORDS = [
    "ekran rasm","skrinsshot","screenshot","скриншот","screen shot","skrinsot",
    "ekranni suratga","ekranni olish",
]
BLUETOOTH_WORDS = [
    "bluetoothga ula","bluetooth ga ula","bluetooth ula","ulanganga ula",
    "bluetooth orqali ula","bluetooth","блютуз","bluetoothni och",
    "bluetooth sozlama","bluetooth qurulma","наушники подключи","bluetooth qurilma",
    "blutus","blutuz","bt",
]
VOLUME_UP_WORDS   = ["ovozni oshir","громкость увеличь","volume up","ovozni ko'tar",
                     "louder","balandroq","ovoz oshir","gromche","gromko","громче"]
VOLUME_DOWN_WORDS = ["ovozni kamayt","громкость уменьши","volume down","ovozni past",
                     "quieter","pastroq","ovoz past","tishe","тише","ovozni tushir"]
MUTE_WORDS        = ["ovozni o'chir","mute","заглуши","тишина","jim","ovoz o'chir",
                     "ovozsiz","sesiz"]
SEND_WORDS        = [
    "yoz","yuborvorchi","yubor","jo'nat","отправь","напиши","send","write to",
    "xabar yoz","xabar yubor","yozib yubor","yozib ber","yuborgin",
]
REMINDER_WORDS    = [
    "eslatma","eslatib ber","remind me","reminder","eslat","напомни","напоминание",
    "eslatib qo'y","eslatma qo'y","soatda eslatib ber","da eslatib ber",
]
BRIGHTNESS_WORDS  = ["yorqinlik","яркость","brightness","ekran yorqinligi"]

# Multi-command split tokens
SPLIT_RE = re.compile(
    r"\bva\b|\bkeyin\b|\bso'ng\b|\bsong\b|\bthen\b|\bи\b|\bafter\b|[,،]",
    re.IGNORECASE
)

# ══════════════════════════════════════════════════════════════
#  HELPER FUNKSIYALAR
# ══════════════════════════════════════════════════════════════
def _l(t: str) -> str:
    return t.lower().strip()

def _has(text: str, words: list) -> bool:
    t = _l(text)
    t_nospace = t.replace(" ", "")
    return any(w in t or w in t_nospace for w in words)

def _detect_app(text: str) -> Optional[str]:
    t = _l(text)
    t_ns = t.replace(" ", "")
    for key, aliases in APP_WORDS.items():
        for a in aliases:
            if a in t or (len(a) >= 3 and a in t_ns):
                return key
    return None

def _detect_engine(text: str) -> str:
    t = _l(text)
    for engine, aliases in SEARCH_ENGINES.items():
        for a in aliases:
            if a in t:
                return engine
    return "google"

def _detect_website(text: str) -> Optional[str]:
    t = _l(text)
    t_ns = t.replace(" ", "")
    for site, aliases in WEBSITES.items():
        for a in aliases:
            if a in t or (len(a) >= 4 and a.replace(" ", "") in t_ns):
                return site
    return None

_PARTICLES = [" da ", " ga ", " ni ", " uchun ", " bilan ", " orqali ",
              " de ", " deb ", " ham ", " va ", " yoki "]

def _clean_query(text: str, *word_lists) -> str:
    t = " " + _l(text) + " "
    for aliases in SEARCH_ENGINES.values():
        for a in sorted(aliases, key=len, reverse=True):
            t = t.replace(a, " ")
    for wlist in word_lists:
        for w in sorted(wlist, key=len, reverse=True):
            t = t.replace(w, " ")
    for aliases in APP_WORDS.values():
        for a in sorted(aliases, key=len, reverse=True):
            t = t.replace(a, " ")
    for p in _PARTICLES:
        t = t.replace(p, " ")
    return re.sub(r'\s+', ' ', t).strip(" ,.-")

def _extract_contact_and_msg(text: str) -> tuple:
    t = _l(text)
    patterns = [
        r"(\w+)\s*ga\s+(.+?)\s*(?:deb\s+)?(?:yoz|yubor|jo'nat|отправь|напиши).*",
        r"(\w+)\s*ga\s+(?:yoz|yubor|xabar):\s*(.+)",
        r"(?:yoz|yubor|напиши|отправь)\s+(\w+)\s*ga\s+(.+)",
    ]
    for p in patterns:
        m = re.search(p, t)
        if m:
            contact = m.group(1).strip()
            message = m.group(2).strip()
            for w in sorted(SEND_WORDS, key=len, reverse=True):
                message = message.replace(w, "").strip()
            return contact, message
    return None, None

def _extract_bt_device(text: str) -> Optional[str]:
    t = " " + _l(text) + " "
    for w in sorted(BLUETOOTH_WORDS, key=len, reverse=True):
        t = t.replace(w, " ")
    for p in [" ga ", " ni ", " da ", " orqali ", " ula ", " ulan "]:
        t = t.replace(p, " ")
    name = re.sub(r'\s+', ' ', t).strip(" ,.-")
    return name if len(name) > 1 else None


# ══════════════════════════════════════════════════════════════
#  BITTA SEGMENT UCHUN PARSE
# ══════════════════════════════════════════════════════════════
def _parse_one(text: str) -> Optional[dict]:
    t = _l(text)
    if len(t) < 2:
        return None

    # 1. SHUTDOWN — faqat ANIQ buyruq, YOKI "o'chir" + kompyuter konteksti.
    #    "telegramni o'chir" → bu yerda SHUTDOWN bo'lmaydi, pastda close_app bo'ladi.
    if _has(t, SHUTDOWN_EXPLICIT) or (_has(t, SHUTDOWN_VERBS) and _has(t, PC_CONTEXT)):
        return {"action": "shutdown"}

    # 2. RESTART
    if _has(t, RESTART_WORDS):
        return {"action": "restart"}

    # 3. SLEEP
    if _has(t, SLEEP_WORDS):
        return {"action": "sleep"}

    # 4. LOCK
    if _has(t, LOCK_WORDS):
        return {"action": "lock"}

    # 5. VAQT
    if _has(t, TIME_WORDS):
        return {"action": "get_time"}

    # 6. SCREENSHOT
    if _has(t, SCREENSHOT_WORDS):
        return {"action": "screenshot"}

    # 7. BLUETOOTH
    if _has(t, BLUETOOTH_WORDS):
        device = _extract_bt_device(t)
        if device and len(device) > 1:
            return {"action": "bluetooth_connect", "device": device}
        return {"action": "bluetooth_open"}

    # 8. OVOZ
    if _has(t, VOLUME_UP_WORDS):
        return {"action": "volume_up"}
    if _has(t, VOLUME_DOWN_WORDS):
        return {"action": "volume_down"}
    if _has(t, MUTE_WORDS):
        return {"action": "mute"}

    # 9. ESLATMA
    if _has(t, REMINDER_WORDS):
        return {"action": "reminder", "text": t}

    # 10. MUSIQA
    if _has(t, PLAY_WORDS):
        engine = _detect_engine(t)
        query  = _clean_query(t, PLAY_WORDS)
        return {"action": "play_music", "query": query or "musiqa", "service": engine}

    # 11. ILOVA YOPISH
    if _has(t, CLOSE_WORDS):
        app = _detect_app(t)
        if app:
            return {"action": "close_app", "app": app}

    # 12. QIDIRUV — open_app dan oldin (muhim!)
    #     "google da python qidir" → search, nafaqat chrome
    if _has(t, SEARCH_WORDS):
        engine = _detect_engine(t)
        query  = _clean_query(t, SEARCH_WORDS)
        return {"action": "search", "query": query or text, "engine": engine}

    # 12.5 VEB-SAYT OCHISH (youtube, yandex music, github...) — ilova emas
    #      "youtube och" / "youtube" → brauzerda ochiladi
    site = _detect_website(t)
    if site and not _has(t, CLOSE_WORDS):
        if site == "youtube":
            return {"action": "open_youtube"}
        if site in ("yandex music", "yandex_music"):
            return {"action": "search", "query": "", "engine": "yandex_music"}
        return {"action": "open_site", "site": site}

    # 13. ILOVA OCHISH — faqat ochish so'zi bor bo'lsa
    if _has(t, OPEN_WORDS):
        app = _detect_app(t)
        if app:
            return {"action": "open_app", "app": app}
        after = _clean_query(t, OPEN_WORDS)
        if after and ("." in after or "http" in after):
            return {"action": "open_url", "url": after}
    # Faqat app nomi aytilsa (open so'zisiz) ham ochish
    if not _has(t, SEARCH_WORDS + CLOSE_WORDS):
        app = _detect_app(t)
        # Qisqa matn: 1-3 so'z va ilova nomi — ochish deb hisoblash
        words_count = len(t.split())
        if app and words_count <= 4:
            return {"action": "open_app", "app": app}

    # 14. TELEGRAM XABAR
    if _has(t, SEND_WORDS):
        contact, message = _extract_contact_and_msg(t)
        if contact and message:
            return {"action": "send_telegram", "contact": contact, "message": message}

    return None


# ══════════════════════════════════════════════════════════════
#  OMMAVIY API
# ══════════════════════════════════════════════════════════════
def parse(text: str) -> Optional[list]:
    """
    Matnni parse qiladi.
    Qaytaradi: list[dict] yoki None (LLMga yuborish kerak)

    Misol:
      parse("chrome och va vscode ham och")
      → [{"action":"open_app","app":"chrome"},
         {"action":"open_app","app":"vscode"}]
    """
    if not text:
        return None

    # Ko'p buyruqga ajrat
    segments = SPLIT_RE.split(text)
    results: list = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        cmd = _parse_one(seg)
        if cmd:
            results.append(cmd)

    if results:
        return results

    # Fallback: butun matnni sinab ko'r
    cmd = _parse_one(text)
    if cmd:
        return [cmd]

    return None
