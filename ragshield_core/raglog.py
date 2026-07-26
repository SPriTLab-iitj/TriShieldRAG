"""
ragshield_core.raglog
Lightweight real-time logger. Writes to logs/ragshield.log AND streams to a
ring buffer the Streamlit UI can display live. Use log() anywhere in the engine.
"""
from __future__ import annotations
import logging, os, time
from collections import deque
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)
_LOG_FILE = _LOG_DIR / "ragshield.log"

# in-memory ring buffer (last 500 lines) for the live UI panel
_BUFFER: deque[str] = deque(maxlen=500)

_logger = logging.getLogger("ragshield")
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(message)s", "%H:%M:%S"))
    _logger.addHandler(fh)


def log(msg: str) -> None:
    """Log one line: to file, console, and the in-memory buffer."""
    line = f"{time.strftime('%H:%M:%S')} | {msg}"
    _BUFFER.append(line)
    _logger.info(msg)
    print(line, flush=True)


def recent(n: int = 200) -> list[str]:
    """Last n log lines (newest last) for the UI."""
    return list(_BUFFER)[-n:]


def clear() -> None:
    _BUFFER.clear()


def logfile_path() -> str:
    return str(_LOG_FILE)
