"""
RAFAEL - Voice Speaker
Yumshoq, aniq AI ovozi.
"""

import asyncio, tempfile, os, re
import edge_tts
import sounddevice as sd
import soundfile as sf
from core.utils.logger import get_logger

logger = get_logger(__name__)

TMP_DIR = os.path.join(tempfile.gettempdir(), "rafael")
os.makedirs(TMP_DIR, exist_ok=True)


# TTS ayrim so'zlarni noto'g'ri o'qiydi. Ikki muammo bor:
#   1. Bosh harfli so'z ("RAFAEL") — harfma-harf "R-A-F-A-E-L" deb o'qiladi
#   2. "ae" kabi harf birikmalari o'zbekcha noto'g'ri talaffuz qilinadi
# Yechim: so'zni TTS to'g'ri o'qiydigan yozuvga almashtiramiz.
# config.yaml → voice.pronunciation orqali kengaytirish/o'zgartirish mumkin.
DEFAULT_PRONOUNCE = {
    "rafael": "Rafayel",
}


def normalize_uz(text: str) -> str:
    """O'zbek TTS talaffuzini yaxshilaydi"""
    # Apostrof bilan harflar — TTS ko'pincha noto'g'ri o'qiydi
    replacements = {
        "o'": "o", "O'": "O", "oʻ": "o", "Oʻ": "O",
        "g'": "g", "G'": "G", "gʻ": "g", "Gʻ": "G",
        "ʻ": "", "ʼ": "", "‘": "", "’": "",
        # Raqamlar
        "0": "nol", "1": "bir", "2": "ikki", "3": "uch",
        "4": "tort", "5": "besh", "6": "olti", "7": "yetti",
        "8": "sakkiz", "9": "toqqiz",
    }
    # Avval raqamlarni kontekstda almashtirmaymiz (odatiy matnda qolsin)
    # Faqat apostrof muammolarini tuzatamiz
    for old, new in list(replacements.items())[:8]:
        text = text.replace(old, new)
    return text


class VoiceSpeaker:
    def __init__(self, config: dict, on_speaking_start=None, on_speaking_end=None):
        self.voice_uz = config.get("tts_voice_uz", config.get("tts_voice", "uz-UZ-MadinaNeural"))
        self.voice_ru = config.get("tts_voice_ru", "ru-RU-SvetlanaNeural")
        self.voice_en = config.get("tts_voice_en", "en-US-JennyNeural")
        self.rate     = config.get("tts_rate",   "+0%")
        self.volume   = config.get("tts_volume", "+15%")
        self.on_speaking_start = on_speaking_start
        self.on_speaking_end   = on_speaking_end
        self._speaking = False

        # Talaffuz lug'ati: standart + config.yaml dagi qo'shimchalar
        self.pronounce = dict(DEFAULT_PRONOUNCE)
        self.pronounce.update(config.get("pronunciation", {}) or {})

    def _fix_pronunciation(self, text: str) -> str:
        """Noto'g'ri o'qiladigan so'zlarni to'g'ri yozuvga almashtiradi.

        Katta-kichik harfga qaramaydi, shuning uchun "RAFAEL", "Rafael" va
        "rafael" ning uchalasi ham to'g'irlanadi (bosh harfli yozuv TTS
        tomonidan harfma-harf o'qib yuborilishining oldini oladi).

        O'zbekcha qo'shimchalar saqlanadi: "Rafaelning" → "Rafayelning".
        Shu sababli lug'atga qisqa so'z qo'shmang — u boshqa so'zlarning
        boshiga ham tushib qolishi mumkin.
        """
        for word, spoken in self.pronounce.items():
            text = re.sub(
                rf"\b{re.escape(word)}(\w*)",
                lambda m, s=spoken: s + m.group(1),
                text, flags=re.IGNORECASE,
            )
        return text

    def _detect_lang(self, text: str) -> str:
        ru = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
        ratio = sum(1 for c in text if c in ru) / max(len(text.strip()), 1)
        if ratio > 0.25:
            return self.voice_ru
        en = ["the ", "is ", "are ", "you ", "have ", "will "]
        if sum(1 for w in en if w in text.lower()) >= 2:
            return self.voice_en
        return self.voice_uz

    async def speak(self, text: str):
        if not text or not text.strip():
            return
        clean = self._clean(text)
        if not clean:
            return

        clean = self._fix_pronunciation(clean)
        voice = self._detect_lang(clean)

        # O'zbek ovozi uchun talaffuz normallashtirish
        if voice == self.voice_uz:
            clean = normalize_uz(clean)

        logger.info(f"TTS: '{clean[:65]}'")
        tmp_path = None
        try:
            if self.on_speaking_start:
                self.on_speaking_start()
            self._speaking = True

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, dir=TMP_DIR) as f:
                tmp_path = f.name

            await edge_tts.Communicate(
                text=clean, voice=voice,
                rate=self.rate, volume=self.volume,
            ).save(tmp_path)

            await asyncio.get_event_loop().run_in_executor(None, self._play, tmp_path)

        except Exception as e:
            logger.error(f"TTS xatosi: {e}")
        finally:
            self._speaking = False
            if self.on_speaking_end:
                self.on_speaking_end()
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                pass

    def _play(self, path: str):
        try:
            data, sr = sf.read(path)
            sd.play(data, sr); sd.wait()
        except Exception as e:
            logger.error(f"Audio xatosi: {e}")

    def _clean(self, text: str) -> str:
        text = re.sub(r'#{1,6}\s+', '', text)
        text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
        text = re.sub(r'_{1,2}(.*?)_{1,2}', r'\1', text)
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'^\s*[-*+•]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @property
    def is_speaking(self) -> bool:
        return self._speaking
