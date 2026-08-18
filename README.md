<div align="center">

# 🤖 RAFAEL v2.0

### Ovozli boshqariladigan shaxsiy AI assistent (Windows)

*O'zbek · Русский · English · Jarvis-style voice control*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://www.microsoft.com/windows)
[![Tests](https://img.shields.io/badge/Tests-25%20passed-success.svg)](#test)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 📖 RAFAEL nima qiladi?

RAFAEL — bu noutbukingizni **ovoz** orqali boshqaradigan AI assistent. "Rafael" deb chaqirasiz, buyruq berasiz — u bajaradi.

- 🎙️ **Ovozli boshqaruv** — wake-word "Rafael", keyin buyruq
- 🌐 **3 til** — O'zbek (asosiy), Rus, Ingliz (avtomatik aniqlanadi)
- 💻 **Ilova boshqaruvi** — Chrome, VS Code, Telegram, kalkulyator va h.k.
- 🔍 **Qidiruv** — Google, Yandex, YouTube, Yandex Music
- 💬 **Telegram** — ovoz bilan xabar yuborish
- 🔊 **Tizim** — ovoz balandligi, Bluetooth, o'chirish, qulflash
- ⏰ **Eslatmalar** — "soat 15 da eslat"
- 🧠 **AI suhbat** — Claude (Anthropic) bilan aqlli javoblar
- ✨ **Futuristik UI** — jonli voice orb, buyruqlar tarixi, dark mode

---

## 🎬 Tez boshlash

### 1. Talablar
- Windows 10/11
- Python 3.11+ ([python.org](https://www.python.org/downloads/))
- Mikrofon + internet
- OpenAI API kalit ([platform.openai.com](https://platform.openai.com))

### 2. O'rnatish
```bash
git clone https://github.com/<username>/RAFAEL.git
cd RAFAEL
pip install -r requirements.txt
```

### 3. API kalit
`.env` fayl yarating (`.env.example` dan nusxa oling):
```
OPENAI_API_KEY=sk-...
```

### 4. Ishga tushirish
```bash
python main.py
```

RAFAEL salomlashadi va "Rafael" so'zini kutadi. Sinab ko'ring:
> *"Rafael, chrome och"* · *"Rafael, youtube och"* · *"Rafael, soat 15 da dars borligini eslat"*

---

## 🗣️ Buyruqlar

| Toifa | Misol | Amal |
|-------|-------|------|
| **Ilova** | "Rafael, vscode och" | VS Code ochiladi |
| **Yopish** | "Rafael, telegramni yop" | Telegram yopiladi |
| **Veb** | "Rafael, youtube och" | Brauzerda YouTube |
| **Qidiruv** | "Rafael, google da python qidir" | Google qidiruv |
| **Musiqa** | "Rafael, youtube da [qo'shiq] qo'y" | YouTube'da ijro |
| **Ko'p buyruq** | "Rafael, chrome och **va** vscode ham och" | Ikkalasi ham |
| **Ovoz** | "Rafael, ovozni oshir" | Volume +5 |
| **Bluetooth** | "Rafael, bluetooth och" | BT sozlamalari |
| **Eslatma** | "Rafael, 30 minutdan keyin eslat" | Eslatma qo'yiladi |
| **Tarjima** | "Rafael, will you come ni tarjima qil" | Tarjima qilib aytadi |
| **Dars** | "Rafael, bu masalani yech" / "fotosintezni tushuntir" | Repetitor kabi tushuntiradi |
| **Ko'z (Vision)** | "Rafael, ekrandagi masalani o'qib yech" / "ekrandagi xatoni tushuntir" | Ekranni ko'rib javob beradi |
| **Ob-havo** | "Rafael, Toshkentda ob-havo qanday" | wttr.in dan ob-havo |
| **Valyuta** | "Rafael, dollar kursi qancha" | CBU dan so'm kursi |
| **Ro'yxat** | "Rafael, ro'yxatga non qo'sh" / "ro'yxatni o'qi" | Todo ro'yxati |
| **Xotira** | "Rafael, eslab qol — ertaga imtihonim bor" / "nimani eslaysan" | Uzoq muddatli xotira |
| **Tizim** | "Rafael, kompyuterni o'chir" | Shutdown (3s) |
| **To'xtatish** | "Rafael, to'xta" | Uxlash rejimi |

---

## 🏗️ Arxitektura

```
                    ┌─────────────────────────┐
                    │      main.py            │
                    │  (Supervisor + 2 ip)    │
                    └───────────┬─────────────┘
                ┌───────────────┴───────────────┐
                ▼                               ▼
   ┌────────────────────┐          ┌────────────────────┐
   │  ASOSIY IP          │  queue   │   FON IP            │
   │  Tkinter UI         │◄─────────│   asyncio           │
   │  (orb, tarix)       │  Queue   │   RaphailAssistant  │
   └────────────────────┘          └─────────┬──────────┘
                                              ▼
              ┌──────────────┬────────────────┼──────────────┐
              ▼              ▼                 ▼              ▼
        🎙️ Listener    🔊 Speaker      🧠 Parser/LLM   💻 Controllers
        (Google STT)   (Edge TTS)     (keyword+Claude)  (system/browser/...)
```

**Ikki qatlamli buyruq tizimi:**
1. **Parser** (millisekund) — kalit so'z bo'yicha, LLM kutmaydi
2. **LLM** (Claude) — parser tushunmasa, aqlli javob

**Texnologiyalar:**
| Qatlam | Texnologiya |
|--------|-------------|
| UI | tkinter (Canvas animatsiya, glassmorphism) |
| Backend | asyncio + threading |
| STT (ovoz→matn) | faster-whisper (offline, `uz`) + Google (zaxira) |
| TTS (matn→ovoz) | edge-tts (uz-UZ-MadinaNeural) |
| AI | OpenAI (`gpt-4o-mini`) |
| Xotira | JSON (suhbat tarixi) |
| Tizim | pywin32, ctypes, subprocess, pyautogui |

---

## 📂 Loyiha tuzilishi

```
RAFAEL/
├── main.py                  # Kirish: supervisor + UI/asyncio iplar
├── config.yaml              # Barcha sozlamalar
├── .env                     # API kalit (commit qilinmaydi)
├── requirements.txt
│
├── core/
│   ├── assistant.py         # Asosiy miya: listen→parse→execute→speak
│   ├── voice/
│   │   ├── listener.py      # Mikrofon + Google STT + echo o'chirish
│   │   ├── speaker.py       # Edge TTS + til aniqlash
│   │   └── wake_word.py     # "Rafael" aniqlash + stop buyruq
│   ├── brain/
│   │   ├── parser.py        # Kalit so'z parser (multi-command)
│   │   ├── llm.py           # Claude API
│   │   ├── memory.py        # Suhbat xotirasi (JSON)
│   │   └── reminder.py      # Eslatmalar (asyncio)
│   ├── control/
│   │   ├── system.py        # Ilova/fayl/o'chirish boshqaruvi
│   │   ├── browser.py       # Google/Yandex/YouTube
│   │   ├── messenger.py     # Telegram avtomatlashtirish
│   │   ├── bluetooth.py     # Bluetooth (PowerShell/WinRT)
│   │   └── code_writer.py   # AI kod yozish
│   └── utils/
│       ├── logger.py        # Rich + fayl loglari
│       └── lang_detect.py   # Til aniqlash (uz/ru/en)
│
├── ui/
│   ├── app.py               # Tkinter oyna + queue ko'prik
│   ├── theme.py             # Ranglar, shriftlar, o'lchamlar
│   └── components/
│       ├── orb.py           # Jonli voice orb (4 holat)
│       ├── history.py       # Buyruqlar tarixi paneli
│       └── status_bar.py    # Holat ko'rsatgich
│
└── tests/
    ├── test_parser.py       # 20 test
    └── test_lang_detect.py  # 5 test
```

---

## ⚙️ Sozlash (`config.yaml`)

```yaml
raphail:
  user_name: "Daler"              # Sizning ismingiz
  wake_words: ["rafael", ...]     # Chaqiruv so'zlari

voice:
  silence_duration: 2.2           # Jim turish (sekund) → gap tugadi
  tts_voice_uz: "uz-UZ-MadinaNeural"

ai:
  model: "gpt-4o-mini"
  context_window: 20              # Eslab qoladigan xabarlar soni

ui:
  show_on_start: true             # UI oynani ko'rsatish
```

---

## 🧪 Test

```bash
pip install pytest
python -m pytest tests/ -v
```

**Natija:** `25 passed` ✓ — parser, ko'p-buyruq, til aniqlash, veb-saytlar.

---

## 📊 Ishlash ko'rsatkichlari

| Ko'rsatkich | Qiymat |
|-------------|--------|
| RAM (idle) | ~140 MB |
| CPU (idle) | ~0.3% |
| Orb animatsiya | 30 FPS |
| Parser tezligi | <1 ms |
| STT javob | ~1-2 s |

---

## 🔧 Muammolarni hal qilish

| Muammo | Yechim |
|--------|--------|
| Oyna chiqmaydi | `python main.py` ni terminalda ishga tushiring, xatoni ko'ring |
| "API kalit topilmadi" | `.env` faylda `OPENAI_API_KEY=sk-...` borligini tekshiring |
| Ovoz eshitilmaydi | Mikrofon ulanganini, `silence_threshold` ni tekshiring |
| Buyruq bajarilmaydi | `logs/raphail.log` ni o'qing — parser nima topganini ko'ring |

---

## 🗺️ Keyingi reja

- [ ] Picovoice/Vosk bilan offline wake-word (internetga bog'liq emas)
- [ ] Spotify API bilan to'g'ridan ijro
- [ ] Tizim tray ikonkasi (minimize to tray)
- [ ] Sozlamalar oynasi (UI orqali config tahrirlash)
- [ ] Ko'proq til (qozoq, turk)

---

## 📜 Litsenziya

MIT License — erkin foydalaning.

<div align="center">

**RAFAEL** — *"Tahlil yakunlandi. Hop bo'ladi, janob."*

</div>
