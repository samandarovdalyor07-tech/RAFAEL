# rafael.py — Shaxsiy AI Yordamchi RAFAEL (sodda, bitta-faylli versiya)
# =====================================================================
# JARVIS uslubidagi ovozli yordamchi. "Rafael" deb chaqirasiz, buyruq
# berasiz — u eshitadi, tushunadi va ovoz bilan javob qaytaradi.
#
# O'rnatish (terminalda bir marta):
#     pip install SpeechRecognition pyttsx3 pyaudio psutil requests
#
# Ishga tushirish:
#     python rafael.py
#
# Tillar: o'zbek (uz-UZ) va ingliz (en-US) — avtomatik sinab ko'radi.
# Platforma: Windows (ilova ochish/yopish Windows buyruqlariga tayanadi).
# =====================================================================

import os                          # ilovalarni ochish, fayllar bilan ishlash
import sys                         # dasturdan chiqish
import subprocess                  # ilovalarni yopish (taskkill)
import datetime                    # vaqt va sana
import webbrowser                  # internet/brauzer ochish

import speech_recognition as sr    # ovozni matnga aylantirish (STT)
import pyttsx3                     # matnni ovozga aylantirish (TTS)
import psutil                      # tizim holati (batareya, CPU, RAM)
import requests                    # internetdan ma'lumot olish (ob-havo)


# ============================ SOZLAMALAR =============================

WAKE_WORDS = ["rafael", "rafayel", "rafail", "raphael"]  # uyg'otuvchi so'zlar
EXIT_WORDS = ["exit", "chiq", "stop", "to'xta", "toxta", "xayr"]  # to'xtatish
DEFAULT_CITY = "Tashkent"          # ob-havo uchun standart shahar

# Ilova nomi  ->  (ochish buyrug'i, yopish uchun jarayon nomi)
# "och" deganda chap qiymat, "yop" deganda o'ng (taskkill) ishlatiladi.
APPS = {
    "bloknot":     ("notepad",  "notepad.exe"),
    "notepad":     ("notepad",  "notepad.exe"),
    "kalkulyator": ("calc",     "Calculator.exe"),
    "calculator":  ("calc",     "Calculator.exe"),
    "paint":       ("mspaint",  "mspaint.exe"),
    "word":        ("winword",  "winword.exe"),
    "excel":       ("excel",    "excel.exe"),
    "chrome":      ("start chrome", "chrome.exe"),
    "brauzer":     ("start chrome", "chrome.exe"),
    "explorer":    ("explorer", "explorer.exe"),
    "fayllar":     ("explorer", "explorer.exe"),
    "cmd":         ("start cmd", "cmd.exe"),
    "terminal":    ("start cmd", "cmd.exe"),
}


# =========================== OVOZ: GAPIRISH ==========================

engine = pyttsx3.init()
engine.setProperty('rate', 175)   # gapirish tezligi (so'z/min)


def gapir(matn):
    """Rafael ovoz bilan javob beradi (va ekranga ham yozadi)."""
    print(f"🤖 RAFAEL: {matn}")
    engine.say(matn)
    engine.runAndWait()


# =========================== OVOZ: ESHITISH ==========================

def eshit(prompt_matn="Tinglayapman..."):
    """Mikrofondan bitta gapni eshitadi va matnga aylantiradi.

    Avval o'zbekcha (uz-UZ), tushunmasa inglizcha (en-US) sinab ko'radi.
    Hech narsa eshitilmasa bo'sh satr qaytaradi.
    """
    r = sr.Recognizer()
    r.pause_threshold = 1          # 1 soniya jimlik = gap tugadi
    with sr.Microphone() as source:
        print(f"🎙️  {prompt_matn}")
        r.adjust_for_ambient_noise(source, duration=0.4)  # shovqinga moslash
        try:
            audio = r.listen(source, timeout=6, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""

    # Ikki tilda navbat bilan urinib ko'ramiz
    for til in ("uz-UZ", "en-US"):
        try:
            buyruq = r.recognize_google(audio, language=til)
            print(f"🧑 SIZ ({til}): {buyruq}")
            return buyruq.lower()
        except sr.UnknownValueError:
            continue               # bu tilda tushunmadi — keyingisini sinaymiz
        except sr.RequestError:
            gapir("Internet bilan bog'lanishda muammo bor")
            return ""
    return ""                       # ikkala tilda ham tushunmadi


# =========================== BUYRUQ AMALLARI =========================

def vaqtni_ayt():
    """Hozirgi soatni aytadi."""
    vaqt = datetime.datetime.now().strftime("%H:%M")
    gapir(f"Hozir soat {vaqt}")


def sanani_ayt():
    """Bugungi sanani aytadi."""
    bugun = datetime.datetime.now().strftime("%d-%m-%Y")
    gapir(f"Bugun {bugun}")


def batareya_holati():
    """Batareya foizini aytadi."""
    bat = psutil.sensors_battery()
    if bat:
        holat = "quvvatlanmoqda" if bat.power_plugged else "quvvatlanmayapti"
        gapir(f"Batareya {int(bat.percent)} foiz, {holat}")
    else:
        gapir("Batareya ma'lumoti topilmadi")


def tizim_holati():
    """CPU va xotira yuklamasini aytadi."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    gapir(f"Protsessor {cpu} foiz, xotira {ram} foiz band")


def ob_havo(shahar=DEFAULT_CITY):
    """Internetdan ob-havoni oladi (wttr.in — API kalit kerak emas)."""
    try:
        url = f"https://wttr.in/{shahar}?format=%t+%C&lang=ru"
        javob = requests.get(url, timeout=8)
        if javob.ok and javob.text.strip():
            gapir(f"{shahar} da hozir: {javob.text.strip()}")
        else:
            gapir("Ob-havo ma'lumotini olib bo'lmadi")
    except requests.RequestException:
        gapir("Ob-havoni olishda internet xatosi yuz berdi")


def internetda_qidir(buyruq):
    """Buyruqdan qidiruv so'zini ajratib, Google'da qidiradi."""
    so_rov = buyruq
    for kalit in ["qidir", "search", "google da", "google", "izla", "qidirib ber"]:
        so_rov = so_rov.replace(kalit, "")
    so_rov = so_rov.strip()
    if so_rov:
        gapir(f"{so_rov} bo'yicha qidiryapman")
        webbrowser.open(f"https://www.google.com/search?q={so_rov}")
    else:
        gapir("Nimani qidiray?")


def youtube_da(buyruq):
    """YouTube ochadi yoki so'rovni YouTube'da qidiradi."""
    so_rov = buyruq
    for kalit in ["youtube", "da", "qo'y", "qoy", "och", "qidir", "play"]:
        so_rov = so_rov.replace(kalit, "")
    so_rov = so_rov.strip()
    if so_rov:
        gapir(f"YouTube da {so_rov} ni qidiryapman")
        webbrowser.open(f"https://www.youtube.com/results?search_query={so_rov}")
    else:
        gapir("YouTube ni ochyapman")
        webbrowser.open("https://youtube.com")


def ilova_och(buyruq):
    """Buyruqda nomi aytilgan ilovani ochadi."""
    for nom, (ochish, _) in APPS.items():
        if nom in buyruq:
            gapir(f"{nom.capitalize()} ni ochyapman")
            os.system(ochish)
            return True
    gapir("Qaysi ilovani ochishni tushunmadim")
    return False


def ilova_yop(buyruq):
    """Buyruqda nomi aytilgan ilovani yopadi (taskkill)."""
    for nom, (_, jarayon) in APPS.items():
        if nom in buyruq:
            natija = subprocess.run(
                ["taskkill", "/IM", jarayon, "/F"],
                capture_output=True, text=True
            )
            if natija.returncode == 0:
                gapir(f"{nom.capitalize()} yopildi")
            else:
                gapir(f"{nom.capitalize()} ochiq emas edi")
            return True
    gapir("Qaysi ilovani yopishni tushunmadim")
    return False


def fayl_qidir(buyruq):
    """Foydalanuvchi papkalaridan fayl nomini qidiradi (birinchi 5 ta)."""
    so_rov = buyruq
    for kalit in ["fayl", "qidir", "topib ber", "top", "izla", "file", "find"]:
        so_rov = so_rov.replace(kalit, "")
    so_rov = so_rov.strip()
    if not so_rov:
        gapir("Qaysi faylni qidiray?")
        return

    gapir(f"{so_rov} nomli faylni qidiryapman, bir oz kuting")
    topildi = []
    bosh_papka = os.path.expanduser("~")     # foydalanuvchi papkasi
    for ildiz, _, fayllar in os.walk(bosh_papka):
        for f in fayllar:
            if so_rov in f.lower():
                topildi.append(os.path.join(ildiz, f))
                if len(topildi) >= 5:
                    break
        if len(topildi) >= 5:
            break

    if topildi:
        gapir(f"{len(topildi)} ta fayl topdim, birinchisini ochyapman")
        print("📂 Topilgan fayllar:")
        for yo_l in topildi:
            print("   ", yo_l)
        os.startfile(topildi[0])             # birinchisini ochib beradi
    else:
        gapir("Bunday fayl topilmadi")


# ========================= BUYRUQNI YO'NALTIRISH =====================

def buyruqni_bajar(buyruq):
    """Eshitilgan buyruqni tahlil qilib, mos amalni bajaradi.

    True qaytarsa — Rafael ishlashda davom etadi.
    False qaytarsa — dastur to'xtaydi.
    """
    if not buyruq:
        return True

    # --- To'xtatish ---
    if any(s in buyruq for s in EXIT_WORDS):
        gapir("Xayr! Rafael o'chmoqda")
        return False

    # --- Vaqt / sana ---
    if "vaqt" in buyruq or "soat" in buyruq or "time" in buyruq:
        vaqtni_ayt()
    elif "sana" in buyruq or "kun" in buyruq or "date" in buyruq:
        sanani_ayt()

    # --- Tizim holati ---
    elif "batareya" in buyruq or "battery" in buyruq or "quvvat" in buyruq:
        batareya_holati()
    elif "tizim" in buyruq or "protsessor" in buyruq or "xotira" in buyruq or "system" in buyruq:
        tizim_holati()

    # --- Ob-havo ---
    elif "ob-havo" in buyruq or "obhavo" in buyruq or "ob havo" in buyruq or "weather" in buyruq:
        ob_havo()

    # --- Internet / qidiruv ---
    elif "youtube" in buyruq:
        youtube_da(buyruq)
    elif "qidir" in buyruq or "search" in buyruq or "izla" in buyruq:
        if "fayl" in buyruq or "file" in buyruq:
            fayl_qidir(buyruq)
        else:
            internetda_qidir(buyruq)
    elif "fayl" in buyruq or "file" in buyruq:
        fayl_qidir(buyruq)

    # --- Ilova boshqaruvi (yopish "och"dan oldin tekshiriladi) ---
    elif "yop" in buyruq or "close" in buyruq:
        ilova_yop(buyruq)
    elif "och" in buyruq or "ishga tushir" in buyruq or "open" in buyruq:
        ilova_och(buyruq)

    # --- Salomlashish ---
    elif "salom" in buyruq or "hello" in buyruq or "hi" in buyruq:
        gapir("Salom! Sizga qanday yordam bera olaman?")

    # --- Tushunmadi ---
    else:
        gapir("Kechirasiz, bu buyruqni tushunmadim")

    return True


# ============================= ASOSIY TSIKL ==========================

def main():
    """Wake-word tsikli: 'Rafael' kutadi -> buyruq oladi -> bajaradi."""
    gapir("Salom! Men Rafael. Meni chaqirish uchun 'Rafael' deng")

    while True:
        # 1-bosqich: uyg'otuvchi so'zni kutamiz
        gap = eshit("'Rafael' degancha kutyapman...")
        if not gap:
            continue

        if any(w in gap for w in WAKE_WORDS):
            # Ba'zan wake-word bilan buyruq bir gapda keladi:
            # "rafael chrome och" — wake-word'dan keyingi qismni olamiz.
            qoldiq = gap
            for w in WAKE_WORDS:
                qoldiq = qoldiq.replace(w, "")
            qoldiq = qoldiq.strip()

            if qoldiq:
                # Buyruq allaqachon aytilgan
                if not buyruqni_bajar(qoldiq):
                    break
            else:
                # Faqat chaqirdi — endi buyruqni alohida olamiz
                gapir("Labbay?")
                buyruq = eshit("Buyrug'ingizni ayting...")
                if not buyruqni_bajar(buyruq):
                    break

        # Wake-word bo'lmasa — jim turamiz (e'tibor bermaymiz)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🤖 RAFAEL to'xtatildi (Ctrl+C).")
        sys.exit(0)
