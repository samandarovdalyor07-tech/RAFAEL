"""
RAFAEL v2.0 — Voice Listener
sounddevice amplitude-VAD + Google STT (uz-UZ,ru-RU,en-US bitta chaqiruvda)
Echo suppression: is_speaking flag active bo'lganda yozish to'xtatiladi.
"""

import asyncio
import threading
import time
import os
import wave
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from core.utils.logger import get_logger

logger = get_logger(__name__)

TMP_DIR = "D:\\tmp"
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

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold        = 300
        self.recognizer.dynamic_energy_threshold = True

        logger.info("VoiceListener tayyor (Google STT, amplitude-VAD).")

    # ─── External control ────────────────────────────────────────────────────

    def set_speaking(self, speaking: bool):
        """Speaker bu metodni chaqiradi — echo kesiladi."""
        self._is_speaking = speaking

    def stop(self):
        self._stop_event.set()

    # ─── Internal helpers ────────────────────────────────────────────────────

    def _is_speech(self, frame: np.ndarray) -> bool:
        return float(np.abs(frame).mean()) > self.silence_thresh

    def _record_until_silence(self) -> np.ndarray | None:
        frame_ms    = 30
        frame_size  = int(self.sample_rate * frame_ms / 1000)
        max_silence = int(self.silence_dur * 1000 / frame_ms)   # frames
        min_speech  = 5                                          # frames

        buf: list          = []
        silence_cnt        = 0
        speech_cnt         = 0
        recording          = False
        started_at: float  = 0.0

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
            with sr.AudioFile(path) as src:
                audio_data = self.recognizer.record(src)

            # Bitta chaqiruv — Google o'zi tanlaydi (eng tez)
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

    async def listen(self) -> str | None:
        """Ovozni yozib, transkripsiya qilib qaytaradi (async)."""
        loop = asyncio.get_event_loop()
        audio = await loop.run_in_executor(None, self._record_until_silence)
        if audio is None or len(audio) == 0:
            return None
        return await loop.run_in_executor(None, self._transcribe, audio)
