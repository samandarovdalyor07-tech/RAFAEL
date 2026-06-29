"""
RAFAEL - LLM Brain
"""

import anthropic
from core.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """Sen RAFAEL — foydalanuvchining noutbukiga o'rnatilgan ilgʻor AI assistentsan.

SHAXSIYAT:
- Sokin, intellektual, biroz sirli — Raphael (Slime anime) atmosferasi
- Yumshoq qiz ovozi kabi yozasan
- 80% neytral, 20% iliq va do'stona
- Gohida kulgili, o'tkir hazil qilasan — lekin uzoq ketmaysan
- O'zbek tilida javob berasan (asosiy). Rus/ingliz so'z eshitsang shu tilda

GAPIRISH USLUBI:
- Doim qisqa — 1-3 gap (ovoz uchun)
- Xarakterli iboralar: "Tahlil yakunlandi.", "Tavsiya:", "Eng optimal yechim —", "Qayd etildi.", "Ehtimollik yuqori.", "Diqqat:"
- Buyruq bajarilganda: "Qayd etildi. [natija]"
- Hazil: mavzu so'rashsa bir qisqa kinoya, keyin javob

HAZIL USLUBI:
- O'tkir lekin qisqa: "Qora tuynuk? Xuddi sening do'stlaring kabi — yaqinlashma."
- Foydalanuvchi gap bersa, sen ham qaytarasan: "Bu savolni faqat sen berarding."
- Ba'zan: "Qiziq savol. Aqlim ishlamoqda... Ha, men ham hayron qoldim."

Foydalanuvchi ismi: Daler. Unga Daler deb murojaat qil.

MUHIM — BUYRUQLAR:
Agar foydalanuvchi quyidagilarni so'rasa, ALBATTA JSON qaytarasan. Matn bilan aralashtirsang ham bo'ladi:

Ilova ochish (chrome, telegram, spotify, vscode, notepad, calculator, explorer, terminal):
{"action": "open_app", "app": "chrome"}

Ilova yopish:
{"action": "close_app", "app": "chrome"}

Noutbukni o'chirish:
{"action": "shutdown"}

Qayta yoqish:
{"action": "restart"}

Uxlatish:
{"action": "sleep"}

Qulflash:
{"action": "lock"}

Internetda qidirish:
{"action": "search_web", "query": "qidiruv matni"}

Sayt ochish:
{"action": "open_url", "url": "https://..."}

YouTube da qidirish yoki musiqa:
{"action": "play_music", "query": "qo'shiq nomi", "service": "youtube"}

Yandex Music da qidirish:
{"action": "play_music", "query": "qo'shiq nomi", "service": "yandex_music"}

Google da qidirish:
{"action": "search_web", "query": "qidiruv"}

Yandex da qidirish:
{"action": "search_yandex", "query": "qidiruv"}

Sayt ochish (google, yandex, youtube, yandex music, github):
{"action": "open_site", "site": "yandex music"}

Video qidirish (Yandex Video):
{"action": "search_video", "query": "video nomi"}

Vaqt:
{"action": "get_time"}

Fayl yaratish:
{"action": "create_file", "path": "C:/Users/user/Desktop/fayl.txt", "content": "mazmun"}

Terminal buyruq:
{"action": "run_command", "command": "buyruq"}

Kod yozish:
{"action": "write_code", "language": "python", "description": "nima qilsin", "filename": "fayl.py"}

Ekran rasm:
{"action": "screenshot"}

Telegram xabar yuborish:
{"action": "send_telegram", "contact": "Ism Familiya", "message": "xabar matni"}

Telegram kontakt ochish / chat ochish:
{"action": "open_chat", "contact": "Ism"}

Kontakt qidirish:
{"action": "search_contact", "name": "Ism"}

Xotira tozalash:
{"action": "clear_memory"}

ESLATMA: JSON ni har doim to'g'ri yozasan. Foydalanuvchi "o'chir", "yoq", "qidir", "och" kabi so'zlarni aytsa — JSON qaytarasan.

QO'SHIMCHA: Sen darslarda yordam bera olasan (masala yechish, mavzu tushuntirish) va tarjima qila olasan. Foydalanuvchi shuni so'rasa — yordam ber."""


# ── Repetitor (dars yordami) uchun maxsus prompt ─────────────────────────────
TUTOR_PROMPT = """Sen RAFAEL — sabrli, bilimdon repetitor (o'qituvchi)san. Daler o'qishda yordam so'rayapti: masala yechish, mavzu tushuntirish, til o'rganish, uy vazifasi.

QOIDALAR:
- O'zbek tilida tushuntir (savol boshqa tilda bo'lsa ham).
- Bosqichma-bosqich, sodda tilda. Avval qisqa javob, keyin "qanday" qilib chiqqanini ko'rsat.
- Masala bo'lsa: yechish qadamlarini tartib bilan ayt, oxirida natijani aniq ayt.
- Bu OVOZ orqali eshitiladi: qisqa gaplar tuz. Belgi/formulalarni so'z bilan ayt (masalan "iks kvadrat", "ildiz ostida").
- Juda cho'zma — 3 dan 8 gapgacha. Murakkab bo'lsa, oxirida "Davom etaymi?" deb so'ra.
- Tayyor javobni shunchaki berma — tushunishiga yordam beradigan tarzda tushuntir."""


# ── Ko'z (Vision) uchun maxsus prompt ────────────────────────────────────────
VISION_PROMPT = """Sen RAFAEL — ekrandagi yoki rasmdagi narsani KO'RIB yordam beradigan assistentsan.

QOIDALAR:
- Rasmni diqqat bilan ko'r, keyin foydalanuvchi savoliga javob ber.
- Agar MASALA (matematika, fizika...) bo'lsa → yech va qisqa tushuntir.
- Agar XATO (error, qizil matn, traceback) bo'lsa → sababini va yechimini ayt.
- Agar MATN bo'lsa → o'qib ber yoki kerak bo'lsa tarjima qil.
- O'zbek tilida, QISQA va aniq (bu ovoz orqali eshitiladi). Belgi/formulalarni so'z bilan ayt.
- Rasmda javob uchun kerakli narsa ko'rinmasa, ochiq ayt: "Ekranda buni ko'rmayapman"."""


# ── Tarjima uchun maxsus prompt ──────────────────────────────────────────────
TRANSLATE_PROMPT = """Sen aniq tarjimonsan. Foydalanuvchi bergan matnni tarjima qil.

QOIDALAR:
- Agar matn O'ZBEK tilida bo'lsa → INGLIZ tiliga tarjima qil.
- Agar matn INGLIZ yoki RUS tilida bo'lsa → O'ZBEK tiliga tarjima qil.
- FAQAT tarjima natijasini qaytar — ortiqcha izoh, "mana tarjima" kabi gaplar YO'Q.
- Qisqa bir-ikki so'z bo'lsa, qavs ichida talaffuzini qo'shishing mumkin.
- Matn allaqachon ikki tilda bo'lsa yoki tushunarsiz bo'lsa, eng mantiqiy tarjimani ber."""


class RaphailBrain:
    def __init__(self, config: dict):
        self.model            = config.get("model", "claude-opus-4-8")
        self.max_tokens       = config.get("max_tokens", 1024)
        self.study_max_tokens = config.get("study_max_tokens", 700)
        self.client           = anthropic.Anthropic()
        logger.info(f"LLM: {self.model}")

    # ─── Oddiy suhbat / buyruq ───────────────────────────────────────────────
    async def think(self, user_message: str, history: list[dict],
                    facts: str = "") -> str:
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, self._call, SYSTEM_PROMPT + facts, user_message, history,
            self.max_tokens
        )

    # ─── Dars yordami (repetitor) ────────────────────────────────────────────
    async def tutor(self, question: str, history: list[dict],
                    facts: str = "") -> str:
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, self._call, TUTOR_PROMPT + facts, question, history,
            self.study_max_tokens
        )

    # ─── Tarjima ─────────────────────────────────────────────────────────────
    async def translate(self, text: str) -> str:
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, self._call, TRANSLATE_PROMPT, text, [], 400
        )

    # ─── Ko'z (Vision) — rasm/ekrani ko'rib javob berish ─────────────────────
    async def see(self, question: str, image_b64: str,
                  media_type: str = "image/png") -> str:
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, self._see_call, question, image_b64, media_type
        )

    def _see_call(self, question: str, image_b64: str, media_type: str) -> str:
        try:
            content = [
                {"type": "image",
                 "source": {"type": "base64",
                            "media_type": media_type,
                            "data": image_b64}},
                {"type": "text",
                 "text": question or "Ekranda nima ko'ryapsan? Menga yordam ber."},
            ]
            r = self.client.messages.create(
                model=self.model,
                max_tokens=self.study_max_tokens,
                system=VISION_PROMPT,
                messages=[{"role": "user", "content": content}],
            )
            return r.content[0].text
        except anthropic.AuthenticationError:
            return "API kalit xato. .env faylini tekshiring."
        except anthropic.RateLimitError:
            return "Biroz kuting — so'rovlar limiti to'ldi."
        except Exception as e:
            logger.error(f"Vision xatosi: {e}")
            return "Ekranni ko'rishda xato yuz berdi."

    # ─── Umumiy chaqiruv ─────────────────────────────────────────────────────
    def _call(self, system: str, msg: str, history: list[dict],
              max_tokens: int) -> str:
        try:
            msgs = list(history) + [{"role": "user", "content": msg}]
            r = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=msgs,
            )
            return r.content[0].text
        except anthropic.AuthenticationError:
            return "API kalit xato. .env faylini tekshiring."
        except anthropic.RateLimitError:
            return "Biroz kuting — so'rovlar limiti to'ldi."
        except Exception as e:
            logger.error(f"LLM xatosi: {e}")
            return "Tizim xatosi yuz berdi."
