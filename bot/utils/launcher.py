import os
import glob
import asyncio
import argparse
from itertools import cycle
import subprocess
import signal

from pyrogram import Client, compose
from better_proxy import Proxy

from bot.config import settings
from bot.utils import logger
from bot.utils.web import run_web_and_tunnel, stop_web_and_tunnel
from bot.core.tapper import run_tappers
from bot.core.registrator import register_sessions  

start_text = """
 ██████╗ ██╗  ██╗   ██╗██╗   ██╗██╗  ██╗███████╗██████╗ ██████╗  ██████╗ ████████╗
██╔═══██╗██║  ╚██╗ ██╔╝██║   ██║██║ ██╔╝██╔════╝██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝
██║   ██║██║   ╚████╔╝ ██║   ██║█████╔╝ █████╗  ██████╔╝██████╔╝██║   ██║   ██║   
██║▄▄ ██║██║    ╚██╔╝  ██║   ██║██╔═██╗ ██╔══╝  ██╔══██╗██╔══██╗██║   ██║   ██║   
╚██████╔╝███████╗██║   ╚██████╔╝██║  ██╗███████╗██║  ██║██████╔╝╚██████╔╝   ██║   
 ╚══▀▀═╝ ╚═════╝╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝   

Select an action:

    1. Create session
    2. Create session via QR
    3. Run clicker
    4. Run via Telegram (Beta)
    5. Upload sessions via web (BETA)
"""

global tg_clients

shutdown_event = asyncio.Event()

def get_session_names() -> list[str]:
    session_names = glob.glob("sessions/*.session")
    session_names = [
        os.path.splitext(os.path.basename(file))[0] for file in session_names
    ]
    return session_names

def get_proxies() -> list[Proxy]:
    if settings.USE_PROXY_FROM_FILE:
        with open(file="bot/config/proxies.txt", encoding="utf-8-sig") as file:
            proxies = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    return proxies

async def get_tg_clients() -> list[Client]:
    global tg_clients

    session_names = get_session_names()

    if not session_names:
        logger.warning("No session files found. Please create a session.")
        return []

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    tg_clients = [
        Client(
            name=session_name,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            workdir="sessions/",
            plugins=dict(root="bot/plugins"),
        )
        for session_name in session_names
    ]

    return tg_clients

async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")

    logger.info(f"Detected {len(get_session_names())} sessions | {len(get_proxies())} proxies")

    action = parser.parse_args().action

    if not action:
        print(start_text)

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Action must be a number")
            elif action not in ["1", "2", "3", "4", "5"]:
                logger.warning("Action must be 1, 2, 3, 4, or 5")
            else:
                action = int(action)
                break

    if action == 1:
        await register_sessions()
    elif action == 2:
        session_name = input("Enter the session name for QR code authentication: ")
        print("Initializing QR code authentication...")
        subprocess.run(["python", "-m", "bot.utils.loginQR", "-s", session_name])
        print("QR code authentication was successful!")
    elif action == 3:
        tg_clients = await get_tg_clients()
        if not tg_clients:
            print("No sessions found. You can create sessions using the following methods:")
            print("1. By phone number: python main.py -a 1")
            print("2. By QR code: python main.py -a 2")
            print("3. Upload via web interface (BETA): python main.py -a 5")
            print("\nIf you're using Docker, use these commands:")
            print("1. By phone number: docker compose run bot python3 main.py -a 1")
            print("2. By QR code: docker compose run bot python3 main.py -a 2")
            print("3. Upload via web interface (BETA): docker compose run bot python3 main.py -a 5")
            return
        await run_tasks(tg_clients=tg_clients)
    elif action == 4:
        tg_clients = await get_tg_clients()
        if not tg_clients:
            print("No sessions found. You can create sessions using the following methods:")
            print("1. By phone number: python main.py -a 1")
            print("2. By QR code: python main.py -a 2")
            print("3. Upload via web interface (BETA): python main.py -a 5")
            print("\nIf you're using Docker, use these commands:")
            print("1. By phone number: docker compose run bot python3 main.py -a 1")
            print("2. By QR code: docker compose run bot python3 main.py -a 2")
            print("3. Upload via web interface (BETA): docker compose run bot python3 main.py -a 5")
            return
        logger.info("Send /help command in Saved Messages\n")
        await compose(tg_clients)
    elif action == 5:
        logger.info("Starting web interface for uploading sessions...")
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            web_task = asyncio.create_task(run_web_and_tunnel())
            await shutdown_event.wait()
        finally:
            web_task.cancel()
            await stop_web_and_tunnel()
            print("Program terminated.")

async def run_tasks(tg_clients: list[Client]):
    proxies = get_proxies()
    proxies_cycle = cycle(proxies) if proxies else None
    proxies_list = [next(proxies_cycle) if proxies_cycle else None for _ in tg_clients]
    
    await run_tappers(tg_clients, proxies_list)

def signal_handler(signum, frame):
    print("\nShutting down...")
    shutdown_event.set()

if __name__ == "__main__":
    try:
        asyncio.run(process())
    except KeyboardInterrupt:
        pass
