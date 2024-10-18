import random
import asyncio
from time import time
from datetime import datetime, timezone, timedelta
from random import randint
from urllib.parse import unquote

import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw import types
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.logging import RichHandler
from rich.emoji import Emoji
from rich.columns import Columns
import logging

from bot.config import settings
from bot.utils.logger import logger, get_log_panel, add_log, wait_for_log_update
from bot.exceptions import InvalidSession
from bot.core.headers import headers

console = Console()

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session.auth").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session.session").setLevel(logging.WARNING)

def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.username = None
        self.first_name = None
        self.last_name = None
        self.fullname = None
        self.start_param = None
        self.peer = None
        self.first_run = None
        self.user_data = {}
        self.tg_web_data = None
        self.client_lock = asyncio.Lock()
        self.upgrades = {}
        self.current_coins = 0
        self.current_energy = 0
        self.max_energy = 0
        self.mine_per_sec = 0
        self.energy_per_sec = 0
        self.current_coins_per_tap = 5
        self.restore_energy_usage_today = 0
        self.last_restore_energy_reset_date = None
        self.restore_energy_daily_limit = 6
        self.restore_energy_cooldown = timedelta(hours=1)
        self.last_restore_energy_purchase_time = {}
        self.onboarding = 0
        self.upgrade_delay = {}
        self.friends_count = 0
        self.raffle_id = None
        self.raffle_tickets = 0
        self.raffle_total_tickets = 0
        self.raffle_prizes_count = 0

    async def get_tg_web_data(self, proxy: str | None) -> str:
        async with self.client_lock:
            if proxy:
                proxy = Proxy.from_str(proxy)
                proxy_dict = dict(
                    scheme=proxy.protocol,
                    hostname=proxy.host,
                    port=proxy.port,
                    username=proxy.login,
                    password=proxy.password
                )
            else:
                proxy_dict = None

            self.tg_client.proxy = proxy_dict

            try:
                with_tg = True

                if not self.tg_client.is_connected:
                    with_tg = False
                    try:
                        await self.tg_client.connect()
                    except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                        raise InvalidSession(self.session_name)

                self.start_param = random.choices([settings.REF_ID, "bro-228618799"], weights=[75, 25], k=1)[0]
                peer = await self.tg_client.resolve_peer('qlyukerbot')
                InputBotApp = types.InputBotAppShortName(bot_id=peer, short_name="start")

                web_view = await self.tg_client.invoke(RequestAppWebView(
                    peer=peer,
                    app=InputBotApp,
                    platform='android',
                    write_allowed=True,
                    start_param=self.start_param
                ))

                auth_url = web_view.url
                tg_web_data = unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

                try:
                    if self.user_id == 0:
                        information = await self.tg_client.get_me()
                        self.user_id = information.id
                        self.first_name = information.first_name or ''
                        self.last_name = information.last_name or ''
                        self.username = information.username or ''
                except Exception as e:
                    pass

                if not with_tg:
                    await self.tg_client.disconnect()

                return tg_web_data

            except InvalidSession as error:
                raise error

            except Exception as error:
                add_log(f"{self.session_name} | Unknown error during Authorization: {error}")
                await asyncio.sleep(3)
                return None

    async def login(self, http_client: aiohttp.ClientSession, tg_web_data: str) -> dict:
        try:
            http_client.headers['Onboarding'] = '0'
            json_data = {"startData": tg_web_data}
            response = await http_client.post(
                url='https://qlyuker.io/api/auth/start',
                json=json_data
            )
            if response.status != 200:
                response_text = await response.text()
                add_log(f"{self.session_name} | login FAILED: Status={response.status}, Response={response_text}")
                response.raise_for_status()
            response_json = await response.json()
            http_client.headers['Onboarding'] = '2'
            await self.process_auth_data(response_json)
            add_log(f"{self.session_name} | Successfully logged in.")
            for cookie in http_client.cookie_jar:
                pass
            return response_json

        except aiohttp.ClientResponseError as error:
            try:
                response_text = await error.response.text()
            except Exception:
                response_text = "No response body"
            add_log(f"{self.session_name} | ClientResponseError during login: Status={error.status}, Message={error.message}, Response={response_text}")
            await asyncio.sleep(3)
            return {}
        except Exception as error:
            add_log(f"{self.session_name} | Unexpected error during login: {error}")
            await asyncio.sleep(3)
            return {}

    async def process_auth_data(self, data: dict):
        user = data.get("user", {})
        upgrades = data.get("upgrades", [])
        shared_config = data.get("sharedConfig", {})
        self.upgrade_delay = shared_config.get("upgradeDelay", {})
        self.onboarding = user.get("onboarding", self.onboarding)
        
        for upgrade in upgrades:
            upgrade_id = upgrade.get('id')
            if not upgrade_id:
                continue
            self.upgrades[upgrade_id] = {
                "id": upgrade_id,
                "kind": upgrade.get('kind', ''),
                "level": upgrade.get('level', 0),
                "amount": upgrade.get('amount', 0),
                "upgradedAt": upgrade.get('upgradedAt'),
                "dayLimitation": upgrade.get('dayLimitation', 0),
                "maxLevel": upgrade.get('maxLevel', False),
                "condition": upgrade.get('condition', {}),
                "next": upgrade.get('next', {})
            }
        
        self.current_coins = user.get("currentCoins", self.current_coins)
        self.current_energy = user.get("currentEnergy", self.current_energy)
        self.mine_per_sec = user.get("minePerSec", self.mine_per_sec)
        self.energy_per_sec = user.get("energyPerSec", self.energy_per_sec)
        self.current_coins_per_tap = user.get("coinsPerTap", self.current_coins_per_tap)
        self.max_energy = user.get("maxEnergy", self.max_energy)
        self.friends_count = user.get("friendsCount", 0)

        for upgrade_id, upgrade in self.upgrades.items():
            if upgrade_id.startswith('restoreEnergy') or upgrade_id.startswith('promo') or upgrade_id.startswith('u'):
                upgraded_at_field = upgrade.get('upgradedAt')
                if upgraded_at_field:
                    upgraded_at = await self.parse_upgraded_at(upgraded_at_field)
                    if upgraded_at:
                        current_date = datetime.utcnow().date()
                        last_upgrade_date = upgraded_at.date()
                        if current_date != self.last_restore_energy_reset_date:
                            self.restore_energy_usage_today = 0
                            self.last_restore_energy_reset_date = current_date
                        self.last_restore_energy_purchase_time[upgrade_id] = upgraded_at

        for upgrade_id, upgrade in self.upgrades.items():
            if not (upgrade_id.startswith('restoreEnergy') or upgrade_id.startswith('promo') or upgrade_id.startswith('u')):
                self.last_restore_energy_purchase_time.setdefault(upgrade_id, None)

        raffles = user.get("raffles", [])
        if raffles:
            self.raffle_id = raffles[0].get("id")
            self.raffle_tickets = raffles[0].get("ticketsCount", 0)  

        raffle_info = data.get("raffles", [])
        if raffle_info:
            self.raffle_total_tickets = raffle_info[0].get("ticketsCount", 0)
            stages = raffle_info[0].get("stages", [])
            self.raffle_prizes_count = sum(sum(prize["count"] for prize in stage["prizes"]) for stage in stages)

    async def parse_upgraded_at(self, upgraded_at):
        try:
            if isinstance(upgraded_at, str):
                if upgraded_at.endswith('Z'):
                    upgraded_at = upgraded_at[:-1] + '+00:00'
                return datetime.fromisoformat(upgraded_at).astimezone(timezone.utc)
            elif isinstance(upgraded_at, int):
                return datetime.fromtimestamp(upgraded_at, tz=timezone.utc)
            else:
                add_log(f"{self.session_name} | Unknown time format: {upgraded_at}")
                return None
        except Exception as e:
            add_log(f"{self.session_name} | Error parsing time '{upgraded_at}': {e}")
            return None

    async def send_taps(self, http_client: aiohttp.ClientSession, taps: int, current_energy: int) -> dict:
        try:
            client_time = int(time())
            json_data = {
                "currentEnergy": current_energy,
                "clientTime": client_time,
                "taps": taps
            }
            response = await http_client.post(
                url='https://qlyuker.io/api/game/sync',
                json=json_data
            )
            if response.status != 200:
                response_text = await response.text()
                add_log(f"{self.session_name} | send_taps FAILED: Status={response.status}, Response={response_text}")
                response.raise_for_status()
            response_json = await response.json()
            add_log(f"{self.session_name} | Sent {taps} taps. Energy used: {taps}.")
            return response_json
        except aiohttp.ClientResponseError as error:
            try:
                response_text = await error.response.text()
            except Exception:
                response_text = "No response body"
            add_log(f"{self.session_name} | ClientResponseError during send_taps: Status={error.status}, Message={error.message}, Response={response_text}")
            await asyncio.sleep(3)
            return {}
        except Exception as error:
            add_log(f"{self.session_name} | Unexpected error during send_taps: {error}")
            await asyncio.sleep(3)
            return {}

    async def buy_upgrade(self, http_client: aiohttp.ClientSession, upgrade_id: str) -> dict:
        try:
            if upgrade_id not in self.upgrades:
                add_log(f"{self.session_name} | Upgrade '{upgrade_id}' not found in upgrades data.")
                return {}
            http_client.headers['Referer'] = 'https://qlyuker.io/upgrades'
            http_client.headers['Onboarding'] = str(self.onboarding)
            json_data = {"upgradeId": upgrade_id}
            response = await http_client.post(
                url='https://qlyuker.io/api/upgrades/buy',
                json=json_data
            )
            if response.status != 200:
                response_text = await response.text()
                if 'Слишком рано для улучшения' in response_text:
                    current_level = self.upgrades[upgrade_id].get('level', 0)
                    delay_seconds = self.upgrade_delay.get(str(current_level), 0)
                    next_available_time = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=delay_seconds)
                    self.last_restore_energy_purchase_time[upgrade_id] = next_available_time
                    add_log(f"{self.session_name} | Cooldown for '{upgrade_id}' set to {delay_seconds} seconds.")
                response.raise_for_status()
            response_json = await response.json()
            await self.update_upgrade_after_purchase(response_json)
            add_log(f"{self.session_name} | Successfully purchased upgrade '{upgrade_id}'.")
            self.last_restore_energy_purchase_time[upgrade_id] = datetime.utcnow().replace(tzinfo=timezone.utc)
            return response_json
        except aiohttp.ClientResponseError as error:
            try:
                response_text = await error.response.text()
            except Exception:
                response_text = "No response body"
            await asyncio.sleep(3)
            return {}
        except Exception as error:
            add_log(f"{self.session_name} | Unexpected error during buy_upgrade '{upgrade_id}': {error}")
            await asyncio.sleep(3)
            return {}

    async def update_upgrade_after_purchase(self, buy_response: dict):
        upgrade = buy_response.get("upgrade")
        if upgrade:
            upgrade_id = upgrade.get('id')
            if upgrade_id in self.upgrades:
                self.upgrades[upgrade_id]['level'] = upgrade.get('level', self.upgrades[upgrade_id]['level'])
                self.upgrades[upgrade_id]['amount'] = upgrade.get('amount', self.upgrades[upgrade_id]['amount'])
                self.upgrades[upgrade_id]['upgradedAt'] = upgrade.get('upgradedAt')
                self.upgrades[upgrade_id]['next'] = buy_response.get('next', {})
            else:
                self.upgrades[upgrade_id] = {
                    "id": upgrade_id,
                    "kind": upgrade.get('kind', ''),
                    "level": upgrade.get('level', 0),
                    "amount": upgrade.get('amount', 0),
                    "upgradedAt": upgrade.get('upgradedAt'),
                    "dayLimitation": upgrade.get('dayLimitation', 0),
                    "maxLevel": upgrade.get('maxLevel', False),
                    "condition": upgrade.get('condition', {}),
                    "next": buy_response.get('next', {})
                }
                add_log(f"{self.session_name} | Upgrade '{upgrade_id}' added after purchase.")
        self.current_coins = buy_response.get('currentCoins', self.current_coins)
        self.current_energy = buy_response.get('currentEnergy', self.current_energy)
        self.max_energy = buy_response.get('maxEnergy', self.max_energy)
        self.mine_per_sec = buy_response.get('minePerSec', self.mine_per_sec)
        self.energy_per_sec = buy_response.get('energyPerSec', self.energy_per_sec)

    async def claim_daily_reward(self, http_client: aiohttp.ClientSession) -> dict:
        try:
            http_client.headers['Referer'] = 'https://qlyuker.io/tasks'
            response = await http_client.post(
                url='https://qlyuker.io/api/tasks/daily'
            )
            if response.status != 200:
                response_text = await response.text()
                add_log(f"{self.session_name} | claim_daily_reward FAILED: Status={response.status}, Response={response_text}")
                response.raise_for_status()
            response_json = await response.json()
            add_log(f"{self.session_name} | Daily reward claimed successfully.")
            return response_json
        except aiohttp.ClientResponseError as error:
            try:
                response_text = await error.response.text()
            except Exception:
                response_text = "No response body"
            add_log(f"{self.session_name} | ClientResponseError during claim_daily_reward: Status={error.status}, Message={error.message}, Response={response_text}")
            return {}
        except Exception as error:
            add_log(f"{self.session_name} | Unexpected error during claim_daily_reward: {error}")
            return {}

    async def collect_daily_reward(self, http_client: aiohttp.ClientSession):
        while settings.ENABLE_CLAIM_REWARDS:
            try:
                daily_reward = self.user_data.get('dailyReward', {})
                day = daily_reward.get('day', 0)
                claimed = daily_reward.get('claimed', None)
                if not claimed:
                    add_log(f"{self.session_name} | Daily reward not claimed yet. Attempting to claim.")
                    reward_response = await self.claim_daily_reward(http_client=http_client)
                    if reward_response:
                        self.user_data.update(reward_response.get('user', {}))
                        self.current_coins = self.user_data.get('currentCoins', self.current_coins)
                        add_log(f"{self.session_name} | Daily reward claimed. Current coins: {self.current_coins}")
                    else:
                        add_log(f"{self.session_name} | Failed to claim daily reward.")
                else:
                    add_log(f"{self.session_name} | Daily reward already received. Will try again in 8 hours.")
                await asyncio.sleep(8 * 3600)
            except Exception as error:
                add_log(f"{self.session_name} | [Daily Bonus Task] Error: {error}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(60)

    async def complete_tasks(self, http_client: aiohttp.ClientSession):
        while settings.ENABLE_TASKS:
            try:
                tasks = self.user_data.get('tasks', [])
                if not tasks:
                    add_log(f"{self.session_name} | No tasks available.")
                else:
                    add_log(f"{self.session_name} | Attempting to complete tasks.")
                for task in tasks:
                    task_id = task.get('id')
                    if task.get('completed'):
                        add_log(f"{self.session_name} | Task '{task_id}' already completed.")
                        continue
                    task_response = await self.check_task(http_client=http_client, task_id=task_id)
                    if task_response.get('success'):
                        reward = task_response.get('reward', 0)
                        add_log(f"{self.session_name} | Task '{task_id}' completed. Reward: {reward} coins.")
                        self.current_coins += reward
                        add_log(f"{self.session_name} | Current coins after reward: {self.current_coins}")
                    else:
                        add_log(f"{self.session_name} | Task '{task_id}' not completed or already claimed.")
                    delay = random.uniform(settings.MIN_DELAY_BETWEEN_TASKS, settings.MAX_DELAY_BETWEEN_TASKS)
                    add_log(f"{self.session_name} | Waiting for {delay:.2f} seconds before next task.")
                    await asyncio.sleep(delay)
                add_log(f"{self.session_name} | Finished attempting tasks. Will try again in 8 hours.")
                await asyncio.sleep(8 * 3600)
            except Exception as error:
                add_log(f"{self.session_name} | [Tasks Collection] Error: {error}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(60)

    async def check_task(self, http_client: aiohttp.ClientSession, task_id: str) -> dict:
        try:
            http_client.headers['Referer'] = 'https://qlyuker.io/tasks'
            json_data = {"taskId": task_id}
            response = await http_client.post(
                url='https://qlyuker.io/api/tasks/check',
                json=json_data
            )
            if response.status != 200:
                response_text = await response.text()
                response.raise_for_status()
            response_json = await response.json()
            return response_json
        except aiohttp.ClientResponseError as error:
            try:
                response_text = await error.response.text()
            except Exception:
                response_text = "No response body"
            add_log(f"{self.session_name} | ClientResponseError during check_task '{task_id}': Status={error.status}, Message={error.message}, Response={response_text}")
            await asyncio.sleep(3)
            return {}
        except Exception as error:
            add_log(f"{self.session_name} | Unexpected error during check_task '{task_id}': {error}")
            await asyncio.sleep(3)
            return {}

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(total=5))
            ip = (await response.json()).get('origin')
            add_log(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            add_log(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def prioritize_upgrades(self, user_data: dict) -> list:
        available_upgrades = [
            u for u in self.upgrades.values()
            if not u.get('maxLevel', False)
        ]

        upgrade_scores = []
        for u in available_upgrades:
            upgrade_id = u['id']
            next_info = u.get('next', {})
            if not next_info:
                continue

            increment = next_info.get('increment', 0)
            price = next_info.get('price', float('inf'))
            if price == 0:
                efficiency = float('inf')
                time_to_accumulate = 0
            else:
                current_income_per_sec = self.mine_per_sec + self.energy_per_sec
                if current_income_per_sec > 0:
                    time_to_accumulate = price / current_income_per_sec
                else:
                    time_to_accumulate = float('inf')

                efficiency = increment / price if price != 0 else float('inf')

            roi = time_to_accumulate / increment if increment != 0 else float('inf')

            condition = u.get('condition', {})
            if not await self.check_condition(u, condition, user_data):
                continue

            if not await self.is_upgrade_available(upgrade_id):
                continue

            upgrade_scores.append({
                "upgrade_id": upgrade_id,
                "efficiency": efficiency,
                "increment": increment,
                "price": price,
                "level": u['level'],
                "kind": u['kind'],
                "time_to_accumulate": time_to_accumulate,
                "roi": roi
            })

        if not upgrade_scores:
            add_log(f"{self.session_name} | No upgrades meet the conditions for purchase.")
            return []

        sorted_upgrades = sorted(
            upgrade_scores,
            key=lambda x: (x['roi'], -x['efficiency'])
        )
        return sorted_upgrades

    async def check_condition(self, upgrade, condition, user_data):
        if not condition:
            day_limitation = upgrade.get('dayLimitation', 0)
            if day_limitation > 0:
                last_upgrade_at = upgrade.get('upgradedAt')
                if last_upgrade_at:
                    last_upgrade_time = await self.parse_upgraded_at(last_upgrade_at)
                    if last_upgrade_time:
                        current_date = datetime.utcnow().date()
                        last_upgrade_date = last_upgrade_time.date()
                        if current_date > last_upgrade_date:
                            self.restore_energy_usage_today = 0
                        if self.restore_energy_usage_today >= self.restore_energy_daily_limit:
                            return False
            return True

        kind = condition.get('kind')
        if kind == 'friends':
            required_friends = condition.get('friends', 0)
            actual_friends = user_data.get('friendsCount', 0)
            result = actual_friends >= required_friends
            return result
        elif kind == 'upgrade':
            required_upgrade_id = condition.get('upgradeId')
            required_level = condition.get('level', 0)
            related_upgrade = self.upgrades.get(required_upgrade_id)
            if related_upgrade:
                result = related_upgrade.get('level', 0) >= required_level
                return result
            else:
                return False
        else:
            return False

    async def is_upgrade_available(self, upgrade_id: str) -> bool:
        upgrade = self.upgrades.get(upgrade_id)
        if not upgrade:
            return False

        if upgrade.get('maxLevel', False):
            add_log(f"{self.session_name} | Upgrade '{upgrade_id}' has reached max level.")
            return False

        if upgrade_id.startswith('restoreEnergy') or upgrade_id.startswith('promo') or upgrade_id.startswith('u'):
            if upgrade.get('dayLimitation', 0) > 0:
                if self.restore_energy_usage_today >= self.restore_energy_daily_limit:
                    add_log(f"{self.session_name} | Daily limit for '{upgrade_id}' reached.")
                    return False
            last_purchase = self.last_restore_energy_purchase_time.get(upgrade_id)
            if last_purchase:
                current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
                current_level = upgrade.get('level', 0)
                delay_seconds = self.upgrade_delay.get(str(current_level), 0)
                elapsed_time = (current_time - last_purchase).total_seconds()
                if elapsed_time < delay_seconds:
                    remaining_time = delay_seconds - elapsed_time
                    add_log(f"{self.session_name} | Upgrade '{upgrade_id}' is on cooldown. Remaining time: {int(remaining_time)} seconds.")
                    return False
            return True
        return True

    async def upgrade_loop(self, http_client: aiohttp.ClientSession):
        while settings.ENABLE_UPGRADES:
            try:
                sorted_upgrades = await self.prioritize_upgrades(self.user_data)
                if sorted_upgrades:
                    target_upgrade = sorted_upgrades[0]
                    upgrade_id = target_upgrade['upgrade_id']
                    price = target_upgrade['price']
                    increment = target_upgrade['increment']
                    efficiency = target_upgrade['efficiency']

                    if price <= self.current_coins:
                        add_log(f"{self.session_name} | Attempting to purchase upgrade '{upgrade_id}' for {price} coins. Expected increment: {increment}.")
                        upgrade_response = await self.buy_upgrade(http_client=http_client, upgrade_id=upgrade_id)
                        if upgrade_response:
                            self.current_coins = upgrade_response.get('currentCoins', self.current_coins)
                            add_log(f"{self.session_name} | Purchased upgrade '{upgrade_id}'. Current coins: {self.current_coins}")
                            add_log(f"{self.session_name} | Sleeping for {settings.SLEEP_AFTER_UPGRADE} seconds after purchase.")
                            await asyncio.sleep(settings.SLEEP_AFTER_UPGRADE)
                            continue
                    else:
                        coins_needed = price - self.current_coins
                        if (self.mine_per_sec + self.energy_per_sec) > 0:
                            time_needed_seconds = coins_needed / (self.mine_per_sec + self.energy_per_sec)
                            time_needed_str = f"{int(time_needed_seconds // 3600)}h {int((time_needed_seconds % 3600) // 60)}m {int(time_needed_seconds % 60)}s"
                        else:
                            time_needed_str = "unknown (mine_per_sec + energy_per_sec = 0)"

                        add_log(
                            f"{self.session_name} | Not enough coins to buy upgrade '{upgrade_id}'. "
                            f"Need: {coins_needed} coins. Time to accumulate: {time_needed_str}."
                        )
                else:
                    add_log(f"{self.session_name} | No upgrades available for purchase at this time.")

                await asyncio.sleep(settings.UPGRADE_CHECK_DELAY)
            except Exception as error:
                add_log(f"{self.session_name} | [Upgrade Loop] Error: {error}")
                import traceback
                add_log(traceback.format_exc())
                await asyncio.sleep(settings.RETRY_DELAY)

    async def tap_loop(self, http_client: aiohttp.ClientSession):
        while settings.ENABLE_TAPS:
            try:
                if self.current_energy <= self.max_energy * settings.ENERGY_THRESHOLD:
                    add_log(f"{self.session_name} | Energy ({self.current_energy}/{self.max_energy}) below threshold ({settings.ENERGY_THRESHOLD * 100}%).")
                    if settings.ENABLE_UPGRADES and await self.is_upgrade_available('restoreEnergy'):
                        add_log(f"{self.session_name} | Attempting to purchase 'restoreEnergy' upgrade.")
                        upgrade_response = await self.buy_upgrade(http_client=http_client, upgrade_id='restoreEnergy')
                        if upgrade_response and upgrade_response.get('currentEnergy', 0) > self.current_energy:
                            self.current_energy = upgrade_response['currentEnergy']
                            self.restore_energy_usage_today += 1
                            add_log(f"{self.session_name} | Energy restored to {self.current_energy}.")
                            add_log(f"{self.session_name} | Sleeping for {settings.SLEEP_AFTER_UPGRADE} seconds after upgrade.")
                            await asyncio.sleep(settings.SLEEP_AFTER_UPGRADE)
                            continue
                        else:
                            add_log(f"{self.session_name} | Unable to restore energy at this time.")
                    else:
                        add_log(f"{self.session_name} | 'restoreEnergy' not available for purchase or upgrades disabled. Sleeping for {settings.SLEEP_ON_LOW_ENERGY} seconds.")
                        await asyncio.sleep(settings.SLEEP_ON_LOW_ENERGY)
                        continue

                taps = min(self.current_energy, randint(settings.MIN_TAPS, settings.MAX_TAPS))
                add_log(f"{self.session_name} | Sending {taps} taps. Energy before tap: {self.current_energy}")
                response = await self.send_taps(http_client=http_client, taps=taps, current_energy=self.current_energy)

                if not response:
                    add_log(f"{self.session_name} | Failed to send taps")
                    await asyncio.sleep(3)
                    continue

                self.current_energy = response.get('currentEnergy', self.current_energy)
                self.current_coins = response.get('currentCoins', self.current_coins)

                add_log(f"{self.session_name} | Taps sent: {taps}. Current coins: {self.current_coins}, Energy: {self.current_energy}/{self.max_energy}")

                sleep_duration = randint(settings.MIN_SLEEP_BETWEEN_TAPS, settings.MAX_SLEEP_BETWEEN_TAPS)
                add_log(f"{self.session_name} | Sleeping for {sleep_duration} seconds before next tap.")
                await asyncio.sleep(sleep_duration)

            except Exception as error:
                add_log(f"{self.session_name} | [Tap Loop] Error: {error}")
                import traceback
                add_log(traceback.format_exc())
                await asyncio.sleep(60)

    async def buy_raffle_tickets(self, http_client: aiohttp.ClientSession):
        if not self.raffle_id:
            add_log(f"{self.session_name} | No active raffle found.")
            return

        tickets_to_buy = self.current_coins // 50000 
        if tickets_to_buy == 0:
            add_log(f"{self.session_name} | Not enough coins to buy raffle tickets.")
            return

        try:
            json_data = {"raffleId": self.raffle_id, "ticketsCount": tickets_to_buy}
            response = await http_client.post(
                url='https://qlyuker.io/api/raffles/buy',
                json=json_data
            )
            if response.status == 200:
                data = await response.json()
                self.current_coins = data.get("currentCoins", self.current_coins)
                self.raffle_tickets = data.get("ticketsCount", self.raffle_tickets)
                self.raffle_total_tickets = data.get("ticketsTotal", self.raffle_total_tickets)
                add_log(f"{self.session_name} | Bought {tickets_to_buy} raffle tickets. Total tickets: {self.raffle_tickets}. Next purchase in {settings.RAFFLE_BUY_INTERVAL} seconds.")
                
                # Обновляем данные в таблице
                await update_left_panel()
            else:
                add_log(f"{self.session_name} | Failed to buy raffle tickets. Status: {response.status}")
        except Exception as e:
            add_log(f"{self.session_name} | Error buying raffle tickets: {e}")

    async def raffle_loop(self, http_client: aiohttp.ClientSession):
        while settings.ENABLE_RAFFLE:
            if not settings.RAFFLE_SESSIONS or self.session_name in settings.RAFFLE_SESSIONS:
                await self.buy_raffle_tickets(http_client)
            
            # Ждем указанный интервал перед следующей покупкой
            await asyncio.sleep(settings.RAFFLE_BUY_INTERVAL)

    async def get_status_panel(self):
        stats_table = Table(show_header=False, box=None)
        stats_table.add_row("Coins", f"{self.current_coins:,}")
        stats_table.add_row("Energy", f"{self.current_energy}/{self.max_energy}")
        stats_table.add_row("Mine per sec", f"{self.mine_per_sec:.2f}")
        stats_table.add_row("Energy per sec", f"{self.energy_per_sec:.2f}")

        activity_log = Text()
        activity_log.append(f"Last login: {datetime.now().strftime('%H:%M:%S')}\n")
        activity_log.append(f"Status: Active\n")
        activity_log.append(f"Friends: {self.friends_count}\n")

        if settings.ENABLE_RAFFLE and self.raffle_id:
            win_chance = (self.raffle_tickets / self.raffle_total_tickets) * self.raffle_prizes_count if self.raffle_total_tickets > 0 else 0
            stats_table.add_row("Raffle Tickets", f"{self.raffle_tickets}")
            stats_table.add_row("Win Chance", f"{win_chance:.4%}")

        panel = Panel(
            Columns([stats_table, activity_log]),
            title=f"[bold]{self.session_name}[/bold]",
            border_style="green",
            expand=False
        )
        return panel

    async def refresh_account_data(self, http_client: aiohttp.ClientSession):
        try:
            self.tg_web_data = await self.get_tg_web_data(proxy=self.proxy)
            if not self.tg_web_data:
                add_log(f"{self.session_name} | Failed to get tg_web_data during refresh")
                return False

            login_data = await self.login(http_client=http_client, tg_web_data=self.tg_web_data)
            if not login_data:
                add_log(f"{self.session_name} | Login failed during refresh")
                return False

            await self.process_auth_data(login_data)
            add_log(f"{self.session_name} | Account data refreshed. Current coins: {self.current_coins}, Energy: {self.current_energy}/{self.max_energy}")
            return True
        except Exception as error:
            add_log(f"{self.session_name} | Error during account refresh: {error}")
            return False

    async def run(self, proxy: str | None) -> None:
        self.proxy = proxy
        proxy_conn = ProxyConnector.from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            add_log(f"{self.session_name} | Starting main bot loop.")

            while True:
                try:
                    add_log(f"{self.session_name} | Main loop iteration started.")

                    if not await self.refresh_account_data(http_client):
                        await asyncio.sleep(60)
                        continue

                    tasks = []
                    if settings.ENABLE_CLAIM_REWARDS:
                        tasks.append(asyncio.create_task(self.collect_daily_reward(http_client=http_client)))
                    if settings.ENABLE_TASKS:
                        tasks.append(asyncio.create_task(self.complete_tasks(http_client=http_client)))
                    if settings.ENABLE_UPGRADES:
                        tasks.append(asyncio.create_task(self.upgrade_loop(http_client=http_client)))
                    if settings.ENABLE_TAPS:
                        tasks.append(asyncio.create_task(self.tap_loop(http_client=http_client)))
                    if settings.ENABLE_RAFFLE:
                        tasks.append(asyncio.create_task(self.raffle_loop(http_client=http_client)))

                    # Добавляем задачу для периодического обновления данных аккаунта
                    tasks.append(asyncio.create_task(self.periodic_refresh(http_client)))

                    await asyncio.gather(*tasks)

                except InvalidSession as error:
                    add_log(f"{self.session_name} | Invalid session: {error}")
                    self.current_energy = -1
                    raise error

                except Exception as error:
                    add_log(f"{self.session_name} | Unknown error: {error}")
                    import traceback
                    add_log(traceback.format_exc())
                    await asyncio.sleep(3)

    async def periodic_refresh(self, http_client: aiohttp.ClientSession):
        while True:
            await asyncio.sleep(300)  # Обновляем каждые 5 минут
            await self.refresh_account_data(http_client)

async def run_tappers(tg_clients: list[Client], proxies: list[str | None]):
    tappers = [Tapper(tg_client) for tg_client in tg_clients]
    
    layout = Layout()

    async def update_left_panel():
        table = Table(show_header=True, header_style="bold cyan", box=None)
        table.add_column("Session", style="cyan")
        table.add_column("Coins", justify="right", style="green")
        table.add_column("Energy", justify="right", style="yellow")
        table.add_column("Mine/h", justify="right", style="magenta")
        table.add_column("Tickets", justify="right", style="blue")
        table.add_column("Win Chance", justify="right", style="purple")
        table.add_column("Status", justify="center", style="red")

        # Сортируем tappers по имени сессии
        sorted_tappers = sorted(tappers, key=lambda x: x.session_name)

        for tapper in sorted_tappers:
            if tapper.current_energy > 0:
                status_emoji = Emoji("green_circle")
                status_color = "green"
            elif tapper.current_energy == 0:
                status_emoji = Emoji("sleeping_face")
                status_color = "yellow"
            elif tapper.current_energy == -1: 
                status_emoji = Emoji("cross_mark")
                status_color = "red"
            else:
                status_emoji = Emoji("red_circle")
                status_color = "red"
            
            win_chance = (tapper.raffle_tickets / tapper.raffle_total_tickets) * tapper.raffle_prizes_count if tapper.raffle_total_tickets > 0 else 0
            table.add_row(
                tapper.session_name,
                format_number(tapper.current_coins),
                f"{max(tapper.current_energy, 0)}/{tapper.max_energy}",
                format_number(tapper.mine_per_sec * 3600),
                str(tapper.raffle_tickets), 
                f"{win_chance:.4%}",
                f"[{status_color}]{status_emoji}[/]"
            )

        return Panel(table, title="Sessions Overview", border_style="green")

    async def update_layout():
        while True:
            console_width = console.width
            if console_width < 120:
                layout.split_column(
                    Layout(name="upper", ratio=1),
                    Layout(name="lower", ratio=1)
                )
                layout["upper"].update(await update_left_panel())
                layout["lower"].update(get_log_panel())
            else:
                layout.split_row(
                    Layout(name="left", ratio=1),
                    Layout(name="right", ratio=1)
                )
                layout["left"].update(await update_left_panel())
                layout["right"].update(get_log_panel())
            
            await asyncio.sleep(1)

    with Live(layout, console=console, refresh_per_second=1, screen=True):
        update_task = asyncio.create_task(update_layout())
        
        try:
            await asyncio.gather(*[tapper.run(proxy) for tapper, proxy in zip(tappers, proxies)])
        except asyncio.CancelledError:
            pass
        finally:
            update_task.cancel()
            try:
                await update_task
            except asyncio.CancelledError:
                pass

async def run_tapper(tg_client: Client, proxy: str | None):
    await run_tappers([tg_client], [proxy])
