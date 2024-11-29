import asyncio
from contextlib import suppress
import logging
import signal
from bot.utils.logger import add_log
from bot.utils.launcher import process

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def handle_shutdown(signum, frame):
    add_log("Received shutdown signal. Cleaning up...")
    for task in asyncio.all_tasks():
        task.cancel()

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

async def main():
    logger.info("Starting the application...")
    try:
        await process()
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
    finally:
        logger.info("Application finished")

if __name__ == '__main__':
    logger.info("Entering main block")
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
