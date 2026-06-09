"""
RAPHAIL - Logger
"""

import logging
import os
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console

console = Console()
_loggers = {}


def get_logger(name: str) -> logging.Logger:
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Console handler (rich)
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            show_time=True,
            show_level=True,
            show_path=False,
        )
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        # File handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(
            log_dir / "raphail.log", encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger
