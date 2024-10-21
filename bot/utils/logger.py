import sys
from rich.console import Console
from rich.panel import Panel
import logging
from rich.emoji import Emoji
from rich.text import Text
from collections import deque
import asyncio

console = Console()

log_buffer = deque(maxlen=100) 
log_update_event = asyncio.Event()

class BufferedHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        emoji_map = {
            "DEBUG": "🐛",
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🚨",
        }
        level_colors = {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold red",
        }
        emoji = emoji_map.get(record.levelname, "")
        color = level_colors.get(record.levelname, "white")
        time_str = record.asctime.split()[1].split(',')[0] 
        formatted_entry = f"{emoji} {time_str} | [{color}]{record.message}[/]"
        log_buffer.appendleft(formatted_entry)
        log_update_event.set()

logger = logging.getLogger("rich")
logger.setLevel(logging.INFO)

buffered_handler = BufferedHandler()
formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
buffered_handler.setFormatter(formatter)
logger.addHandler(buffered_handler)

# Отключаем логи Pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session.auth").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session.session").setLevel(logging.WARNING)

def add_log(message):
    log_buffer.appendleft(message)
    log_update_event.set()

def get_log_panel():
    log_text = Text("\n".join(list(log_buffer)))
    return Panel(log_text, title="Logs", border_style="yellow")

async def wait_for_log_update():
    await log_update_event.wait()
    log_update_event.clear()
