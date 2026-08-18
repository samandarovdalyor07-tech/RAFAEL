"""
RAFAEL v2.0 — Voice Listener
sounddevice amplitude-VAD + Google STT (uz-UZ,ru-RU,en-US bitta chaqiruvda)
Echo suppression: is_speaking flag active bo'lganda yozish to'xtatiladi.
"""

import asyncio
import tempfile
import threading
import time
import os
import wave
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from core.utils.logger import get_logger

logger = get_logger(__name__)

TMP_DIR = os.path.join(tempfile.gettempdir(), "rafael")
os.makedirs(TMP_DIR, exist_ok=True)


class VoiceListener:
    def __init__(self, config: dict):
        v = config.get("voice", config)          # voice sub-key yoki to'g'ridan
        self.sample_rate     = v.get("sample_rate", 16000)
        self.channels        = v.get("channels", 1)
        self.silence_thresh  = v.get("silence_threshold", 500)
        self.silence_dur     = v.get("silence_duration", 2.2)
        self.max_seconds     = v.get("max_record_seconds", 25)

        self._is_speaking = False           # Speaker.speak() tomonidan o'rnatiladi
        self._stop_event  = threading.Event()
        self._calibrated  = False           # mikrofon shovqiniga moslashganmi

        # STT dvigateli: "whisper" (aniq, offline) yoki "google"
        self.stt_engine          = v.get("stt_engine", "whisper")
        self.whisper_model_name  = v.get("whisper_model", "small")
        self.whisper_compute     = v.get("whisper_compute", "int8")
        # Whisper o'zbekchani auto-rejimda ko'pincha arabcha deb xato aniqlaydi,
        # shuning uchun tilni "uz" ga majburlaymiz. "" qilsangiz — avto aniqlash.
        self.whisper_language    = v.get("whisper_language", "uz")
        self._whisper            = None     # lazy yuklanadi

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold        = 300
        self.recognizer.dynamic_energy_threshold = True

        logger.info(f"VoiceListener tayyor (STT: {self.stt_engine}, amplitude-VAD).")

    def _load_whisper(self):
        """Whisper modelini bir marta yuklaydi (birinchi marta internetdan)."""
        if self._whisper is not None:
            return
        try:
            from faster_whisper import WhisperModel
            logger.info(
                f"Whisper modeli yuklanmoqda: '{self.whisper_model_name}' "
                f"(birinchi marta bir necha daqiqa yuklab olinishi mumkin)..."
            )
            self._whisper = WhisperModel(
                self.whisper_model_name, device="cpu",
                compute_type=self.whisper_compute,
            )
            logger.info("Whisper tayyor.")
        except Exception as e:
            logger.error(f"Whisper yuklanmadi, Google STT ga o'tildi: {e}")
            self._whisper = None
            self.stt_engine = "google"

    def _transcribe_whisper(self, path: str) -> str | None:
        """Whisper bilan transkripsiya (uz/ru/en avtomatik aniqlanadi)."""
        self._load_whisper()
        if self._whisper is None:
            return None
        try:
            segments, info = self._whisper.transcribe(
                path, beam_size=5, vad_filter=True,
                language=self.whisper_language or None,
            )
            text = "".join(seg.text for seg in segments).strip()
            if text:
                logger.info(f"STT [whisper/{info.language}]: {text!r}")
            return text or None
        except Exception as e:
            logger.error(f"Whisper transkripsiya xatosi: {e}")
            return None

    def _calibrate(self):
        """Mikrofon shovqin darajasini o'lchab, eshitish bo'sag'asini moslaydi.

        Qattiq belgilangan bo'sag'a (silence_threshold) ko'p mikrofonlar uchun
        juda baland bo'lib, ovoz umuman yozilmasligiga sabab bo'ladi. Bu metod
        atrof shovqinni o'lchab, bo'sag'ani avtomatik to'g'irlaydi.
        """
        try:
            frames = int(self.sample_rate * 0.6)        # 0.6 soniya namuna
            rec = sd.rec(frames, samplerate=self.sample_rate,
                         channels=self.channels, dtype="int16")
            sd.wait()
            noise = float(np.abs(rec).mean())
            # Bo'sag'a = shovqin*2.5 + zaxira; [120..900] oralig'ida cheklaymiz
            self.silence_thresh = max(120.0, min(900.0, noise * 2.5 + 80.0))
            logger.info(
                f"Mikrofon kalibratsiya: shovqin={noise:.0f} "
                f"→ bo'sag'a={self.silence_thresh:.0f}"
            )
        except Exception as e:
            logger.warning(f"Kalibratsiya o'tkazib yuborildi: {e}")
        self._calibrated = True

    # ─── External control ────────────────────────────────────────────────────

    def set_speaking(self, speaking: bool):
        """Speaker bu metodni chaqiradi — echo kesiladi."""
        self._is_speaking = speaking

    def stop(self):
        self._stop_event.set()

    # ─── Internal helpers ────────────────────────────────────────────────────

    def _is_speech(self, frame: np.ndarray) -> bool:
        return float(np.abs(frame).mean()) > self.silence_thresh

    def _record_until_silence(self, idle_timeout: float | None = None) -> np.ndarray | None:
        frame_ms    = 30
        frame_size  = int(self.sample_rate * frame_ms / 1000)
        max_silence = int(self.silence_dur * 1000 / frame_ms)   # frames
        min_speech  = 5                                          # frames

        buf: list          = []
        silence_cnt        = 0
        speech_cnt         = 0
        recording          = False
        started_at: float  = 0.0
        wait_start         = time.time()   # gapirish boshlanishini kutish vaqti

        # Birinchi marta — mikrofonni atrof shovqiniga moslaymiz
        if not self._calibrated and not self._is_speaking:
            self._calibrate()

        logger.debug("Ovoz kutilmoqda...")

        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                blocksize=frame_size,
            ) as stream:
                while not self._stop_event.is_set():
                    # Echo: RAFAEL o'zi gapirsa yozma
                    if self._is_speaking:
                        time.sleep(0.05)
                        buf.clear()
                        silence_cnt = speech_cnt = 0
                        recording = False
                        continue

                    # Follow-up: belgilangan vaqt ichida gapirilmasa — voz kechamiz
                    if (not recording and idle_timeout is not None
                            and (time.time() - wait_start) > idle_timeout):
                        logger.debug("Follow-up: jimlik timeout — kutish to'xtatildi.")
                        return None

                    # Maksimal muddat
                    if recording and (time.time() - started_at) > self.max_seconds:
                        logger.debug("Maksimal yozish muddati tugadi.")
                        break

                    raw, _ = stream.read(frame_size)
                    frame  = np.frombuffer(bytes(raw), dtype=np.int16)

                    if self._is_speech(frame):
                        if not recording:
                            recording   = True
                            started_at  = time.time()
                            logger.debug("Ovoz boshlandi.")
                        speech_cnt += 1
                        silence_cnt = 0
                        buf.append(frame)
                    elif recording:
                        silence_cnt += 1
                        buf.append(frame)
                        if silence_cnt >= max_silence:
                            if speech_cnt >= min_speech:
                                logger.debug("Gapirish tugadi.")
                                break
                            else:
                                # Shovqin edi — buferni tozala
                                buf.clear()
                                silence_cnt = speech_cnt = 0
                                recording = False

        except Exception as e:
            logger.error(f"Yozish xatosi: {e}")
            return None

        if not buf:
            return None
        return np.concatenate(buf, axis=0)

    def _save_wav(self, audio: np.ndarray) -> str:
        path = os.path.join(TMP_DIR, f"rafael_stt_{int(time.time()*1000)}.wav")
        with wave.open(path, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio.tobytes())
        return path

    def _transcribe(self, audio: np.ndarray) -> str | None:
        path = None
        try:
            path = self._save_wav(audio)

            # ── Whisper (aniq, offline) ──────────────────────────────────
            if self.stt_engine == "whisper":
                return self._transcribe_whisper(path)

            # ── Google STT (eski yo'l) ───────────────────────────────────
            with sr.AudioFile(path) as src:
                audio_data = self.recognizer.record(src)

            # Fallback: 3 til ketma-ket (qaysi biri qaytarsa shu)
            for lang in ("uz-UZ", "ru-RU", "en-US"):
                try:
                    text = self.recognizer.recognize_google(audio_data, language=lang)
                    if text:
                        logger.info(f"STT [{lang}]: {text!r}")
                        return text.strip()
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    logger.error(f"Google STT xatosi [{lang}]: {e}")
                    return None

            logger.debug("STT: hech narsa aniqlanmadi.")
            return None

        except Exception as e:
            logger.error(f"Transkriptsiya xatosi: {e}")
            return None
        finally:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except OSError:
                    pass

    # ─── Public async API ────────────────────────────────────────────────────

    async def listen(self, idle_timeout: float | None = None) -> str | None:
        """Ovozni yozib, transkripsiya qilib qaytaradi (async).

        idle_timeout berilsa va shu vaqt ichida hech kim gapirmasa — None
        qaytaradi (follow-up suhbat rejimida ishlatiladi).
        """
        loop = asyncio.get_event_loop()
        audio = await loop.run_in_executor(None, self._record_until_silence, idle_timeout)
        if audio is None or len(audio) == 0:
            return None
        return await loop.run_in_executor(None, self._transcribe, audio)
