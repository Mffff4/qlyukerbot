import random
import asyncio
from time import time
from datetime import datetime, timezone
from random import randint
from urllib.parse import unquote

import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw import types

from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from bot.core.headers import headers

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
        self.onboarding = 0

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
                    logger.error(f"{self.session_name} | Error fetching user info: {e}")

                if not with_tg:
                    await self.tg_client.disconnect()

                return tg_web_data

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(
                    f"{self.session_name} | Unknown error during Authorization: {error}")
                await asyncio.sleep(3)
                return None

    async def login(self, http_client: aiohttp.ClientSession, tg_web_data: str) -> dict:
        try:
            http_client.headers['Onboarding'] = '0'

            response = await http_client.post(
                url='https://qlyuker.io/api/auth/start',
                json={"startData": tg_web_data}
            )
            response.raise_for_status()
            response_json = await response.json()
            http_client.headers['Onboarding'] = '2'

            await self.process_auth_data(response_json)

            logger.info(f"{self.session_name} | Successfully logged in.")
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Error during login: {error}")
            await asyncio.sleep(3)
            return {}

    async def process_auth_data(self, data: dict):
        user = data.get("user", {})
        upgrades = data.get("upgrades", [])
        self.onboarding = user.get("onboarding", self.onboarding)
        for upgrade in upgrades:
            upgrade_id = upgrade.get('id')
            if not upgrade_id:
                logger.warning("Received upgrade without ID, skipping.")
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

        restore_energy_upgrade = self.upgrades.get('restoreEnergy')
        if restore_energy_upgrade:
            upgraded_at_field = restore_energy_upgrade.get('upgradedAt')
            if upgraded_at_field:
                upgraded_at = await self.parse_upgraded_at(upgraded_at_field)
                if upgraded_at:
                    current_date = datetime.utcnow().date()
                    last_upgrade_date = upgraded_at.date()
                    if current_date != self.last_restore_energy_reset_date:
                        self.restore_energy_usage_today = 0
                        self.last_restore_energy_reset_date = current_date
        else:
            self.restore_energy_usage_today = 0

    async def parse_upgraded_at(self, upgraded_at):
        try:
            if isinstance(upgraded_at, str):
                if upgraded_at.endswith('Z'):
                    upgraded_at = upgraded_at[:-1] + '+00:00'
                return datetime.fromisoformat(upgraded_at).astimezone(timezone.utc)
            elif isinstance(upgraded_at, int):
                return datetime.fromtimestamp(upgraded_at, tz=timezone.utc)
            else:
                logger.error(f"{self.session_name} | Unknown time format: {upgraded_at}")
                return None
        except Exception as e:
            logger.error(f"{self.session_name} | Error parsing time '{upgraded_at}': {e}")
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
            response.raise_for_status()

            response_json = await response.json()
            logger.info(f"{self.session_name} | Sent {taps} taps. Energy used: {taps}.")
            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Error during send_taps: {error}")
            await asyncio.sleep(3)
            return {}

    async def buy_upgrade(self, http_client: aiohttp.ClientSession, upgrade_id: str) -> dict:
        try:
            http_client.headers['Referer'] = 'https://qlyuker.io/upgrades'
            http_client.headers['Onboarding'] = str(self.onboarding)
            json_data = {"upgradeId": upgrade_id}
            response = await http_client.post(
                url='https://qlyuker.io/api/upgrades/buy',
                json=json_data
            )
            response.raise_for_status()

            response_json = await response.json()
            await self.update_upgrade_after_purchase(response_json)
            logger.info(f"{self.session_name} | Successfully purchased upgrade '{upgrade_id}'.")
            return response_json
        except aiohttp.ClientResponseError as error:
            logger.error(f"{self.session_name} | Client response error during buy_upgrade '{upgrade_id}': {error.status} - {error.message}")
            await asyncio.sleep(3)
            return {}
        except Exception as error:
            logger.error(f"{self.session_name} | Error during buy_upgrade '{upgrade_id}': {error}")
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
                logger.info(f"{self.session_name} | Upgrade '{upgrade_id}' added after purchase.")

            self.current_coins = buy_response.get('currentCoins', self.current_coins)
            self.current_energy = buy_response.get('currentEnergy', self.current_energy)
            self.max_energy = buy_response.get('maxEnergy', self.max_energy)
            self.mine_per_sec = buy_response.get('minePerSec', self.mine_per_sec)
            self.energy_per_sec = buy_response.get('energyPerSec', self.energy_per_sec)

            if upgrade_id == 'restoreEnergy':
                self.restore_energy_usage_today += 1

    async def claim_daily_reward(self, http_client: aiohttp.ClientSession) -> dict:
        try:
            http_client.headers['Referer'] = 'https://qlyuker.io/tasks'
            response = await http_client.post(
                url='https://qlyuker.io/api/tasks/daily'
            )
            response.raise_for_status()
            response_json = await response.json()
            logger.info(f"{self.session_name} | Daily reward claimed successfully.")
            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Error during claim_daily_reward: {error}")
            return {}

    async def collect_daily_reward(self, http_client: aiohttp.ClientSession, proxy: str | None):
        while True:
            try:
                if not self.tg_web_data:
                    self.tg_web_data = await self.get_tg_web_data(proxy=proxy)
                if not self.tg_web_data:
                    logger.error(f"{self.session_name} | Failed to get tg_web_data in collect_daily_bonus")
                    await asyncio.sleep(60)
                    continue

                login_data = await self.login(http_client=http_client, tg_web_data=self.tg_web_data)
                if not login_data:
                    logger.error(f"{self.session_name} | Login failed during collect_daily_bonus")
                    await asyncio.sleep(60)
                    continue
                self.user_data = login_data.get('user', {})
                daily_reward = self.user_data.get('dailyReward', {})
                day = daily_reward.get('day', 0)
                claimed = daily_reward.get('claimed', None)

                if not claimed:
                    logger.info(f"{self.session_name} | Daily reward not claimed yet. Attempting to claim.")
                    reward_response = await self.claim_daily_reward(http_client=http_client)
                    if reward_response:
                        self.user_data.update(reward_response.get('user', {}))
                        self.current_coins = self.user_data.get('currentCoins', self.current_coins)
                        logger.info(f"{self.session_name} | Daily reward claimed. Current coins: {self.current_coins}")
                    else:
                        logger.error(f"{self.session_name} | Failed to claim daily reward.")
                else:
                    logger.info(f"{self.session_name} | Daily reward already received. Will try again in 8 hours.")

                await asyncio.sleep(8 * 3600)
            except Exception as error:
                logger.error(f"{self.session_name} | [Daily Bonus Task] Error: {error}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(60)

    async def collect_tasks(self, http_client: aiohttp.ClientSession, proxy: str | None):
        while True:
            try:
                if not self.tg_web_data:
                    self.tg_web_data = await self.get_tg_web_data(proxy=proxy)
                if not self.tg_web_data:
                    logger.error(f"{self.session_name} | Failed to get tg_web_data in collect_tasks")
                    await asyncio.sleep(60)
                    continue

                login_data = await self.login(http_client=http_client, tg_web_data=self.tg_web_data)
                if not login_data:
                    logger.error(f"{self.session_name} | Login failed during collect_tasks")
                    await asyncio.sleep(60)
                    continue

                self.user_data = login_data.get('user', {})
                tasks = login_data.get('tasks', [])
                if not tasks:
                    logger.info(f"{self.session_name} | No tasks available.")
                else:
                    logger.info(f"{self.session_name} | Attempting to complete tasks.")

                for task in tasks:
                    task_id = task.get('id')
                    if task.get('completed'):
                        logger.info(f"{self.session_name} | Task '{task_id}' already completed.")
                        continue

                    task_response = await self.check_task(http_client=http_client, task_id=task_id)
                    if task_response.get('success'):
                        reward = task_response.get('reward', 0)
                        logger.info(f"{self.session_name} | Task '{task_id}' completed. Reward: {reward} coins.")
                        self.current_coins += reward
                        logger.info(f"{self.session_name} | Current coins after reward: {self.current_coins}")
                    else:
                        logger.info(f"{self.session_name} | Task '{task_id}' not completed or already claimed.")

                    delay = random.uniform(settings.MIN_DELAY_BETWEEN_TASKS, settings.MAX_DELAY_BETWEEN_TASKS)
                    logger.info(f"{self.session_name} | Waiting for {delay:.2f} seconds before next task.")
                    await asyncio.sleep(delay)

                logger.info(f"{self.session_name} | Finished attempting tasks. Will try again in 8 hours.")
                await asyncio.sleep(8 * 3600)
            except Exception as error:
                logger.error(f"{self.session_name} | [Tasks Collection] Error: {error}")
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
            response.raise_for_status()
            response_json = await response.json()
            return response_json
        except Exception as error:
            await asyncio.sleep(3)
            return {}

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(total=5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

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
            else:
                efficiency = increment / price

            condition = u.get('condition', {})
            if not await self.check_condition(u, condition, user_data):
                continue

            upgrade_scores.append({
                "upgrade_id": upgrade_id,
                "efficiency": efficiency,
                "increment": increment,
                "price": price,
                "level": u['level'],
                "kind": u['kind']
            })

        if not upgrade_scores:
            logger.info(f"{self.session_name} | No upgrades meet the conditions for purchase.")
            return []

        sorted_upgrades = sorted(upgrade_scores, key=lambda x: (-x['efficiency'], x['price']))

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

    async def is_restore_energy_available(self):
        restore_upgrade = self.upgrades.get('restoreEnergy')
        if not restore_upgrade:
            logger.warning(f"{self.session_name} | Upgrade 'restoreEnergy' not found.")
            return False

        if restore_upgrade.get('maxLevel', False):
            return False

        if self.restore_energy_usage_today >= self.restore_energy_daily_limit:
            return False

        return True

    async def run(self, proxy: str | None) -> None:
        proxy_conn = ProxyConnector.from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            logger.info(f"{self.session_name} | Starting main bot loop.")

            daily_bonus_task = asyncio.create_task(self.collect_daily_reward(http_client=http_client, proxy=proxy))
            tasks_collection_task = asyncio.create_task(self.collect_tasks(http_client=http_client, proxy=proxy))

            while True:
                try:
                    logger.info(f"{self.session_name} | Main loop iteration started.")

                    if not self.tg_web_data:
                        self.tg_web_data = await self.get_tg_web_data(proxy=proxy)
                    if not self.tg_web_data:
                        logger.error(f"{self.session_name} | Failed to get tg_web_data in main loop")
                        await asyncio.sleep(60)
                        continue

                    login_data = await self.login(http_client=http_client, tg_web_data=self.tg_web_data)

                    if not login_data:
                        logger.error(f"{self.session_name} | Login failed")
                        await asyncio.sleep(3)
                        continue

                    self.user_data = login_data.get('user', {})
                    current_energy = self.current_energy
                    current_coins = self.current_coins
                    max_energy = self.max_energy

                    logger.info(f"{self.session_name} | Logged in successfully. Current coins: {current_coins}, Energy: {current_energy}/{max_energy}")

                    user_data = {
                        "friendsCount": self.friends_count
                    }

                    while True:
                        if current_energy <= max_energy * settings.ENERGY_THRESHOLD:
                            logger.info(f"{self.session_name} | Energy ({current_energy}/{max_energy}) below threshold ({settings.ENERGY_THRESHOLD * 100}%).")
                            if await self.is_restore_energy_available():
                                upgrade_response = await self.buy_upgrade(http_client=http_client, upgrade_id='restoreEnergy')
                                if upgrade_response and upgrade_response.get('currentEnergy', 0) > current_energy:
                                    current_energy = upgrade_response['currentEnergy']
                                    logger.info(f"{self.session_name} | Energy restored to {current_energy}.")
                                    logger.info(f"{self.session_name} | Sleeping for {settings.SLEEP_AFTER_UPGRADE} seconds after upgrade.")
                                    await asyncio.sleep(settings.SLEEP_AFTER_UPGRADE)
                                else:
                                    logger.info(f"{self.session_name} | Unable to restore energy at this time.")
                            else:
                                logger.info(f"{self.session_name} | 'restoreEnergy' not available for purchase. Sleeping for {settings.SLEEP_ON_LOW_ENERGY} seconds.")
                                await asyncio.sleep(settings.SLEEP_ON_LOW_ENERGY)
                                break

                        sorted_upgrades = await self.prioritize_upgrades(user_data)
                        if sorted_upgrades:
                            target_upgrade = sorted_upgrades[0]
                            upgrade_id = target_upgrade['upgrade_id']
                            price = target_upgrade['price']
                            increment = target_upgrade['increment']
                            efficiency = target_upgrade['efficiency']

                            if price <= current_coins:
                                logger.info(f"{self.session_name} | Attempting to purchase upgrade '{upgrade_id}' for {price} coins. Expected increment: {increment}.")

                                upgrade_response = await self.buy_upgrade(http_client=http_client, upgrade_id=upgrade_id)
                                if upgrade_response:
                                    current_coins = upgrade_response.get('currentCoins', current_coins)
                                    logger.info(f"{self.session_name} | Purchased upgrade '{upgrade_id}'. Current coins: {current_coins}")
                                    logger.info(f"{self.session_name} | Sleeping for {settings.SLEEP_AFTER_UPGRADE} seconds after purchase.")
                                    await asyncio.sleep(settings.SLEEP_AFTER_UPGRADE)
                                    continue
                            else:
                                coins_needed = price - current_coins
                                if (self.mine_per_sec + self.energy_per_sec) > 0:
                                    time_needed_seconds = coins_needed / (self.mine_per_sec + self.energy_per_sec)
                                    time_needed_str = f"{int(time_needed_seconds // 3600)}h {int((time_needed_seconds % 3600) // 60)}m {int(time_needed_seconds % 60)}s"
                                else:
                                    time_needed_str = "unknown (mine_per_sec + energy_per_sec = 0)"

                                logger.info(
                                    f"{self.session_name} | Not enough coins to buy upgrade '{upgrade_id}'. "
                                    f"Need: {coins_needed} coins. Time to accumulate: {time_needed_str}."
                                )
                        else:
                            logger.info(f"{self.session_name} | No upgrades available for purchase at this time.")

                        taps = min(current_energy, randint(settings.MIN_TAPS, settings.MAX_TAPS))
                        logger.info(f"{self.session_name} | Sending {taps} taps. Energy before tap: {current_energy}")
                        response = await self.send_taps(http_client=http_client, taps=taps, current_energy=current_energy)

                        if not response:
                            logger.error(f"{self.session_name} | Failed to send taps")
                            await asyncio.sleep(3)
                            break

                        self.current_energy = response.get('currentEnergy', current_energy)
                        self.current_coins = response.get('currentCoins', current_coins)
                        current_energy = self.current_energy
                        current_coins = self.current_coins

                        logger.info(f"{self.session_name} | Taps sent: {taps}. Current coins: {current_coins}, Energy: {current_energy}/{max_energy}")

                        sleep_duration = randint(settings.MIN_SLEEP_BETWEEN_TAPS, settings.MAX_SLEEP_BETWEEN_TAPS)
                        logger.info(f"{self.session_name} | Sleeping for {sleep_duration} seconds before next action.")
                        await asyncio.sleep(sleep_duration)

                    self.tg_web_data = None

                except InvalidSession as error:
                    logger.error(f"{self.session_name} | Invalid session: {error}")
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error}")
                    import traceback
                    traceback.print_exc()
                    await asyncio.sleep(3)

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
