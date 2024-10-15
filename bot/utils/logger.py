import sys
from rich.console import Console
from rich.panel import Panel
import logging
from rich.emoji import Emoji
from rich.text import Text

console = Console()

log_buffer = []

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
        log_buffer.append(formatted_entry)
        if len(log_buffer) > 100:
            log_buffer.pop(0)

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

def get_logs(n=30):
    return Text.from_markup("\n".join(log_buffer[-n:]))

def get_log_panel():
    return Panel(get_logs(), title="Logs", border_style="yellow")
