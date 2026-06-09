"""
RAPHAIL - Ovoz testi
Mikrofon va TTS ni tekshirish uchun.
Ishga tushirish: python test_voice.py
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()


async def test_tts():
    print("\n[1] TTS (Matn → Ovoz) testi...")
    try:
        from core.voice.speaker import VoiceSpeaker
        config = {
            "tts_voice": "uz-UZ-SardorNeural",
            "tts_voice_ru": "ru-RU-DmitryNeural",
            "tts_voice_en": "en-US-GuyNeural",
            "tts_rate": "+0%",
            "tts_volume": "+0%",
        }
        speaker = VoiceSpeaker(config)
        print("  O'zbek tilida gap aytilmoqda...")
        await speaker.speak("Salom! Men RAPHAIL. Ovozim ishlayapti.")
        print("  [OK] TTS ishladi!")
    except Exception as e:
        print(f"  [XATO] TTS: {e}")


async def test_stt():
    print("\n[2] STT (Ovoz → Matn) testi...")
    print("  3 soniya gapirib ko'ring...")
    try:
        from core.voice.listener import VoiceListener
        config = {
            "stt_model": "tiny",  # test uchun tiny
            "sample_rate": 16000,
            "channels": 1,
            "chunk_size": 1024,
            "silence_duration": 1.5,
            "max_record_seconds": 10,
            "vad_aggressiveness": 2,
        }
        listener = VoiceListener(config)
        text = await listener.listen()
        if text:
            print(f"  [OK] Eshitildi: '{text}'")
        else:
            print("  [OGOHLANTIRISH] Hech narsa eshitilmadi.")
    except Exception as e:
        print(f"  [XATO] STT: {e}")


async def test_api():
    print("\n[3] Anthropic API testi...")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("  [XATO] ANTHROPIC_API_KEY yo'q!")
        return

    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=50,
            messages=[{"role": "user", "content": "Salom, qisqa javob ber."}],
        )
        print(f"  [OK] API ishlayapti. Javob: '{response.content[0].text[:60]}'")
    except Exception as e:
        print(f"  [XATO] API: {e}")


async def main():
    print("=" * 50)
    print("RAPHAIL - Diagnostika testi")
    print("=" * 50)

    await test_tts()
    await test_api()

    run_stt = input("\nMikrofon testini o'tkazish? (y/n): ").strip().lower()
    if run_stt == "y":
        await test_stt()

    print("\n" + "=" * 50)
    print("Test tugadi.")
    print("=" * 50)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
