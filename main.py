import asyncio
from contextlib import suppress
import logging

from bot.utils.launcher import process

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting the application...")
    try:
        await process()
    except Exception as e:
        logger.exception(f"An error occurred: {e}")

if __name__ == '__main__':
    logger.info("Entering main block")
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
    logger.info("Application finished")
