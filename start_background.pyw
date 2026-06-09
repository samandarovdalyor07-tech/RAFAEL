"""
RAFAEL - Fon rejimida ishga tushirish
Terminal oynasiz ishlaydi. start_background.pyw
"""
import asyncio
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import yaml
from core.assistant import RaphailAssistant

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

async def main():
    config = load_config()
    assistant = RaphailAssistant(config["raphail"] | {
        "voice": config["voice"],
        "ai": config["ai"],
        "system": config["system"],
    })
    await assistant.start()

if __name__ == "__main__":
    asyncio.run(main())
