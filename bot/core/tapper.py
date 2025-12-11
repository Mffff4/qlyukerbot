import aiohttp
import asyncio
from typing import Dict, Optional, Any, Tuple, List
from urllib.parse import urlencode, unquote
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from random import uniform, randint
from time import time
from datetime import datetime, timezone
import json
import os

from bot.utils.universal_telegram_client import UniversalTelegramClient
from bot.utils.proxy_utils import check_proxy, get_working_proxy
from bot.utils.first_run import check_is_first_run, append_recurring_session
from bot.config import settings
from bot.utils import logger, config_utils, CONFIG_PATH
from bot.exceptions import InvalidSession

class BaseBot:
    API_BASE_URL = "https://qlyuker.sp.yandex.ru/api"
    AUTH_START_URL = f"{API_BASE_URL}/auth/start"
    GAME_ONBOARDING_URL = f"{API_BASE_URL}/game/onboarding"
    GAME_SYNC_URL = f"{API_BASE_URL}/game/sync"
    UPGRADE_BUY_URL = f"{API_BASE_URL}/upgrades/buy"
    TASKS_CHECK_URL = f"{API_BASE_URL}/tasks/check"
    TICKETS_BUY_URL = f"{API_BASE_URL}/game/tickets/buy"
    
    DEFAULT_HEADERS = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Klyuk': '0110101101101100011110010111010101101011',
        'Locale': 'ru',
        'Origin': 'https://qlyuker.sp.yandex.ru',
        'Referer': 'https://qlyuker.sp.yandex.ru/front/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'TGPlatform': 'ios',
        'content-type': 'application/json'
    }
    
    UPGRADE_COOLDOWN = {
        "maxEnergy": 10,
        "coinsPerTap": 10,
        "promo1": 60*5,
        "promo2": 60*10,
        "promo3": 60*20,
        "restoreEnergy": 3600
    }
    
    def __init__(self, tg_client: UniversalTelegramClient):
        self.tg_client = tg_client
        if hasattr(self.tg_client, 'client'):
            self.tg_client.client.no_updates = True
            
        self.session_name = tg_client.session_name
        self._http_client: Optional[CloudflareScraper] = None
        self._current_proxy: Optional[str] = None
        self._access_token: Optional[str] = None
        self._is_first_run: Optional[bool] = None
        self._init_data: Optional[str] = None
        self._current_ref_id: Optional[str] = None
        self._game_data: Optional[Dict] = None
        self._cookies: Optional[str] = None
        self._onboarding_completed: bool = False
        self._team_joined: bool = False
        self._team_id: Optional[int] = None
        self._user_agent: Optional[str] = None
        
        self._accumulated_taps: int = 0
        self._current_energy: int = 500
        self._max_energy: int = 500
        self._last_sync_time: int = int(time())
        self._current_distance: int = 0
        self._distance_per_tap: int = 1
        self._distance_per_hour: int = 0
        self._distance_per_sec: int = 0
        self._current_candies: int = 0
        self._current_tickets: int = 0
        self._next_checkpoint_position: int = 0
        
        self._energy_restores_used: int = 0
        self._energy_restores_max: int = 6
        self._last_restore_date: Optional[str] = None
        self._restore_energy_attempts: int = 0
        
        self._available_upgrades: Dict[str, Dict] = {}
        self._upgrade_last_buy_time: Dict[str, float] = {}
        self._pending_upgrade_check: bool = True

        self._available_tasks: Dict[str, Dict] = {}
        
        session_config = config_utils.get_session_config(self.session_name, CONFIG_PATH)
        if not all(key in session_config for key in ('api', 'user_agent')):
            logger.critical(f"CHECK accounts_config.json as it might be corrupted")
            exit(-1)
            
        self.proxy = session_config.get('proxy')
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            self.tg_client.set_proxy(proxy)
            self._current_proxy = self.proxy
            
        self._user_agent = session_config.get('user_agent', 
            'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36')

    def get_ref_id(self) -> str:
        if self._current_ref_id is None:
            session_hash = sum(ord(c) for c in self.session_name)
            remainder = session_hash % 10
            if remainder < 6:
                self._current_ref_id = settings.REF_ID
            elif remainder < 9:
                self._current_ref_id = 'bro-228618799'
            else:
                self._current_ref_id = 'bro-228618799'
        return self._current_ref_id
    
    async def get_tg_web_data(self, app_name: str = "qlyukerbot", path: str = "start") -> str:
        try:
            webview_url = await self.tg_client.get_app_webview_url(
                app_name,
                path,
                self.get_ref_id()
            )
            
            if not webview_url:
                raise InvalidSession("Failed to get webview URL")
                
            tg_web_data = unquote(
                string=webview_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
            )
            
            self._init_data = tg_web_data
            return tg_web_data
            
        except Exception as e:
            logger.error(f"{self.session_name} | Error getting TG Web Data: {str(e)}")
            raise InvalidSession("Failed to get TG Web Data")

    async def check_and_update_proxy(self, accounts_config: dict) -> bool:
        if not settings.USE_PROXY:
            return True

        if not self._current_proxy or not await check_proxy(self._current_proxy):
            new_proxy = await get_working_proxy(accounts_config, self._current_proxy)
            if not new_proxy:
                return False

            self._current_proxy = new_proxy
            if self._http_client and not self._http_client.closed:
                await self._http_client.close()

            proxy_conn = {'connector': ProxyConnector.from_url(new_proxy)}
            self._http_client = CloudflareScraper(timeout=aiohttp.ClientTimeout(60), **proxy_conn)
            logger.info(f"{self.session_name} | Switched to new proxy: {new_proxy}")

        return True

    async def initialize_session(self) -> bool:
        try:
            self._is_first_run = await check_is_first_run(self.session_name)
            if self._is_first_run:
                logger.info(f"{self.session_name} | First run detected for session {self.session_name}")
                await append_recurring_session(self.session_name)
            return True
        except Exception as e:
            logger.error(f"{self.session_name} | Session initialization error: {str(e)}")
            return False

    async def make_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        if not self._http_client:
            raise InvalidSession("HTTP client not initialized")

        try:
            async with getattr(self._http_client, method.lower())(url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    if response.status != 400:
                        response_text = ""
                        try:
                            response_text = await response.text()
                        except Exception as e_text:
                            logger.error(f"{self.session_name} | Error reading response text: {e_text}")
                        
                        logger.error(f"{self.session_name} | Request failed with status {response.status}. URL: {url}. Response: {response_text}")
                    return None
        except Exception as e:
            logger.error(f"{self.session_name} | Request error: {str(e)}. URL: {url}")
            return None
            
    async def auth_start(self) -> bool:
        logger.info(f"{self.session_name} | 🔑 Attempting authorization...")
        try:
            tg_web_data = await self.get_tg_web_data()
            
            headers = self.DEFAULT_HEADERS.copy()
            headers['User-Agent'] = self._user_agent
            headers['Onboarding'] = 'null'
            
            payload = {
                "startData": tg_web_data
            }
            
            response = await self.make_request(
                'post',
                self.AUTH_START_URL,
                headers=headers,
                json=payload
            )
            
            if not response:
                logger.error("ኃ Auth request failed or returned no data")
                return False
                
            self._game_data = response
            
            if 'game' in response:
                game_data = response['game']
                self._current_energy = game_data.get('currentEnergy', self._current_energy)
                self._max_energy = game_data.get('maxEnergy', self._max_energy)
                self._current_distance = game_data.get('currentCoins', self._current_distance)
                self._distance_per_tap = game_data.get('coinsPerTap', self._distance_per_tap)
                self._distance_per_hour = game_data.get('minePerHour', self._distance_per_hour)
                self._distance_per_sec = game_data.get('minePerSec', self._distance_per_sec)
                self._current_candies = game_data.get('currentCandies', self._current_candies)
                self._current_tickets = game_data.get('currentTickets', self._current_tickets)
                self._next_checkpoint_position = game_data.get('nextCheckpointPosition', self._next_checkpoint_position)
            
            if 'sharedConfig' in response and 'upgradeDelay' in response['sharedConfig']:
                self.UPGRADE_COOLDOWN = {}
                for level, delay in response['sharedConfig']['upgradeDelay'].items():
                    self.UPGRADE_COOLDOWN[int(level)] = int(delay)
                    
                day_limitation_delay = response['sharedConfig'].get('dayLimitationUpgradeDelay', 3600)
                self.UPGRADE_COOLDOWN['restoreEnergy'] = day_limitation_delay
            
            self._update_available_upgrades()
            self._update_available_tasks()
            
            if hasattr(self._http_client, '_session') and hasattr(self._http_client._session, 'cookie_jar'):
                cookies = self._http_client._session.cookie_jar.filter_cookies(self.AUTH_START_URL)
                cookie_strings = [f"{key}={cookie.value}" for key, cookie in cookies.items()]
                self._cookies = "; ".join(cookie_strings)
                
            user_id = self._game_data.get('user', {}).get('uid')
            distance_to_checkpoint = self._next_checkpoint_position - self._current_distance
            logger.info(
                f"{self.session_name} | ✅ Auth successful! User ID: {user_id}, "
                f"📏 Distance: {self._current_distance} (to checkpoint: {distance_to_checkpoint}), "
                f"🍬 Candies: {self._current_candies}, 🎫 Tickets: {self._current_tickets}, "
                f"⚡ Energy: {self._current_energy}/{self._max_energy}"
            )
            return True
            
        except Exception as e:
            logger.error(f"{self.session_name} | ኃ Error during auth start: {str(e)}")
            return False

    def _update_available_upgrades(self) -> None:
        if not self._game_data or 'upgrades' not in self._game_data or 'list' not in self._game_data['upgrades']:
            return
            
        upgrades_list = self._game_data['upgrades']['list']
        self._available_upgrades = {}
        
        for upgrade in upgrades_list:
            upgrade_id = upgrade.get('id')
            if not upgrade_id:
                continue
                
            if upgrade_id == 'restoreEnergy':
                day_limitation = upgrade.get('dayLimitation', 6)
                current_level = upgrade.get('level', 0)
                self._energy_restores_max = day_limitation
                self._energy_restores_used = current_level
                
            self._available_upgrades[upgrade_id] = upgrade

    def _update_available_tasks(self) -> None:
        if not self._game_data or 'tasks' not in self._game_data:
            logger.info("🧾 No tasks data found in game_data.")
            self._available_tasks = {}
            return

        tasks_list = self._game_data.get('tasks', [])
        temp_tasks = {}
        for task_data in tasks_list:
            task_id = task_data.get('id')
            if task_id:
                temp_tasks[task_id] = task_data
        
        self._available_tasks = temp_tasks
        logger.info(f"{self.session_name} | 🧾 Updated available tasks: {len(self._available_tasks)} tasks loaded.")

    async def game_onboarding(self) -> bool:
        try:
            headers = self.DEFAULT_HEADERS.copy()
            headers['User-Agent'] = self._user_agent
            headers['Onboarding'] = '0'
            
            if self._cookies:
                headers['Cookie'] = self._cookies
                
            payload = {"tier": 2}
            
            response = await self.make_request(
                'post',
                self.GAME_ONBOARDING_URL,
                headers=headers,
                json=payload
            )
            
            if not response or response.get('result') != 2:
                logger.error(f"{self.session_name} | Failed to complete onboarding: {response}")
                return False
                
            logger.info(f"{self.session_name} | ✅ Onboarding completed (tier 2)")
            self._onboarding_completed = True
            return True
            
        except Exception as e:
            logger.error(f"{self.session_name} | Error during game onboarding: {str(e)}")
            return False
            

    async def sync_game(self, taps: int = 0) -> Optional[Dict]:
        try:
            headers = self.DEFAULT_HEADERS.copy()
            headers['User-Agent'] = self._user_agent
            headers['Onboarding'] = '2'
            
            if self._cookies:
                headers['Cookie'] = self._cookies
                
            current_time = int(time())
            
            payload = {
                "currentEnergy": self._current_energy,
                "clientTime": current_time,
                "taps": taps
            }
            
            response = await self.make_request(
                'post',
                self.GAME_SYNC_URL,
                headers=headers,
                json=payload
            )
            
            if not response:
                logger.error(f"{self.session_name} | Failed to sync game data")
                
                logger.info("Trying to re-authenticate due to sync failure")
                if await self.auth_start():
                    logger.info("Re-authentication successful, retrying sync")
                    
                    if self._cookies:
                        headers['Cookie'] = self._cookies
                        
                    response = await self.make_request(
                        'post',
                        self.GAME_SYNC_URL,
                        headers=headers,
                        json=payload
                    )
                    
                    if not response:
                        logger.error(f"{self.session_name} | Failed to sync game data after re-authentication")
                        return None
                else:
                    logger.error("Re-authentication failed")
                    return None
            
            self._current_distance = response.get('currentCoins', self._current_distance)
            self._current_candies = response.get('currentCandies', self._current_candies)
            self._current_tickets = response.get('currentTickets', self._current_tickets)
            self._current_energy = response.get('currentEnergy', self._current_energy)
            self._last_sync_time = response.get('lastSync', current_time)
            
            checkpoint_reward = response.get('reward')
            if checkpoint_reward:
                reward_candies = checkpoint_reward.get('candies', 0)
                reward_upgrade = checkpoint_reward.get('upgrade')
                reward_skin = checkpoint_reward.get('skin')
                
                reward_parts = [f"{reward_candies} 🍬"]
                if reward_upgrade:
                    reward_parts.append(f"upgrade: {reward_upgrade}")
                if reward_skin:
                    reward_parts.append(f"skin: {reward_skin}")
                    
                logger.info(
                    f"{self.session_name} | 🎁 Checkpoint reached! "
                    f"Reward: {', '.join(reward_parts)}"
                )
            
            next_checkpoint = response.get('nextCheckpoint')
            if next_checkpoint:
                if isinstance(next_checkpoint, dict) and 'position' in next_checkpoint:
                    self._next_checkpoint_position = next_checkpoint['position']
                elif isinstance(next_checkpoint, (int, float)):
                    self._next_checkpoint_position = int(next_checkpoint)
            
            self._pending_upgrade_check = True
            
            distance_to_checkpoint = self._next_checkpoint_position - self._current_distance if self._next_checkpoint_position > 0 else 0
            logger.info(
                f"{self.session_name} | Sync: {taps} taps, "
                f"📏 {self._current_distance} (to checkpoint: {distance_to_checkpoint}), "
                f"🍬 {self._current_candies}, ⚡ {self._current_energy}/{self._max_energy}"
            )
            return response
            
        except Exception as e:
            logger.error(f"{self.session_name} | Error during game sync: {str(e)}")
            return None

    async def buy_upgrade(self, upgrade_id: str) -> Optional[Dict]:
        try:
            if not await self._is_upgrade_available(upgrade_id):
                logger.info(f"{self.session_name} | Upgrade {upgrade_id} is not available now")
                return None
                
            headers = self.DEFAULT_HEADERS.copy()
            headers['User-Agent'] = self._user_agent
            headers['Onboarding'] = '2'
            headers['Referer'] = 'https://qlyuker.io/upgrades'
            
            if self._cookies:
                headers['Cookie'] = self._cookies
                
            payload = {
                "upgradeId": upgrade_id
            }
            
            response = await self.make_request(
                'post',
                self.UPGRADE_BUY_URL,
                headers=headers,
                json=payload
            )
            
            if not response:
                logger.warning(
                    f"{self.session_name} | Failed to buy upgrade {upgrade_id} "
                    f"(may be locked or on cooldown)"
                )
                
                current_level = 0
                if upgrade_id in self._available_upgrades:
                    current_level = self._available_upgrades[upgrade_id].get('level', 0)
                
                cooldown = 10
                if current_level + 1 in self.UPGRADE_COOLDOWN:
                    cooldown = self.UPGRADE_COOLDOWN[current_level + 1]
                elif isinstance(self.UPGRADE_COOLDOWN, dict) and len(self.UPGRADE_COOLDOWN) > 0:
                    cooldown = max(self.UPGRADE_COOLDOWN.values())
                
                self._upgrade_last_buy_time[upgrade_id] = time()
                
                if upgrade_id == 'restoreEnergy':
                    self._restore_energy_attempts += 1
                    if self._restore_energy_attempts >= 2:
                        self._energy_restores_used = self._energy_restores_max
                        
                return None
                
            await self._update_upgrade_after_purchase(response, upgrade_id)
                
            logger.info(
                f"{self.session_name} | 🛒 Successfully bought upgrade {upgrade_id}, "
                f"⚡ {self._current_energy}/{self._max_energy}, 🍬 {self._current_candies}"
            )
            return response
            
        except Exception as e:
            logger.error(f"{self.session_name} | Error buying upgrade: {str(e)}")
            return None
            
    async def _update_upgrade_after_purchase(self, buy_response: Dict, upgrade_id: str) -> None:
        if 'currentEnergy' in buy_response:
            self._current_energy = buy_response.get('currentEnergy', self._current_energy)
            self._max_energy = buy_response.get('maxEnergy', self._max_energy)
            self._current_distance = buy_response.get('currentCoins', self._current_distance)
            self._current_candies = buy_response.get('currentCandies', self._current_candies)
            self._current_tickets = buy_response.get('currentTickets', self._current_tickets)
            self._distance_per_tap = buy_response.get('coinsPerTap', self._distance_per_tap)
            self._distance_per_hour = buy_response.get('minePerHour', self._distance_per_hour)
            self._distance_per_sec = buy_response.get('minePerSec', self._distance_per_sec)
                
        if upgrade_id == 'restoreEnergy' and 'upgrade' in buy_response:
            self._energy_restores_used = buy_response['upgrade'].get('level', 0)
            self._last_restore_date = datetime.now().strftime("%Y-%m-%d")
            self._restore_energy_attempts = 0
        
        if 'upgrade' in buy_response:
            upgrade = buy_response['upgrade']
            upgrade_id = upgrade.get('id')
            if upgrade_id in self._available_upgrades:
                self._available_upgrades[upgrade_id]['level'] = upgrade.get('level', self._available_upgrades[upgrade_id].get('level', 0))
                self._available_upgrades[upgrade_id]['amount'] = upgrade.get('amount', self._available_upgrades[upgrade_id].get('amount', 0))
                self._available_upgrades[upgrade_id]['upgradedAt'] = upgrade.get('upgradedAt')
                
                if 'next' in buy_response:
                    self._available_upgrades[upgrade_id]['next'] = buy_response['next']
            else:
                self._available_upgrades[upgrade_id] = {
                    "id": upgrade_id,
                    "level": upgrade.get('level', 0),
                    "amount": upgrade.get('amount', 0),
                    "upgradedAt": upgrade.get('upgradedAt'),
                    "next": buy_response.get('next', {})
                }
                logger.info(f"{self.session_name} | Upgrade {upgrade_id} added after purchase")
                
        self._upgrade_last_buy_time[upgrade_id] = time()
            
    async def _is_upgrade_available(self, upgrade_id: str) -> bool:
        if upgrade_id != 'restoreEnergy' and upgrade_id not in self._available_upgrades:
            return False
            
        if upgrade_id == 'restoreEnergy':
            if self._restore_energy_attempts >= 2:
                logger.warning(f"{self.session_name} | ⚠️ Too many restore energy attempts, skipping")
                return False
                
            if self._energy_restores_used >= self._energy_restores_max:
                logger.warning(
                    f"{self.session_name} | 🔋 Daily energy restore limit reached "
                    f"({self._energy_restores_used}/{self._energy_restores_max})"
                )
                return False
                
        if upgrade_id in self._upgrade_last_buy_time:
            current_time = time()
            
            if upgrade_id == 'restoreEnergy':
                cooldown = self.UPGRADE_COOLDOWN.get('restoreEnergy', 3600)
            else:
                current_level = 0
                if upgrade_id in self._available_upgrades:
                    current_level = self._available_upgrades[upgrade_id].get('level', 0)
                
                cooldown = 10
                if current_level + 1 in self.UPGRADE_COOLDOWN:
                    cooldown = self.UPGRADE_COOLDOWN[current_level + 1]
                elif isinstance(self.UPGRADE_COOLDOWN, dict) and len(self.UPGRADE_COOLDOWN) > 0:
                    cooldown = max(self.UPGRADE_COOLDOWN.values())
                
            last_buy_time = self._upgrade_last_buy_time[upgrade_id]
            elapsed_time = current_time - last_buy_time
            
            if elapsed_time < cooldown:
                remaining_time = cooldown - elapsed_time
                remaining_minutes = int(remaining_time // 60)
                remaining_seconds = int(remaining_time % 60)
                
                if remaining_minutes > 0:
                    time_str = f"{remaining_minutes}m {remaining_seconds}s"
                else:
                    time_str = f"{remaining_seconds}s"
                    
                logger.info(
                    f"{self.session_name} | 🕒 Upgrade {upgrade_id} on cooldown, "
                    f"remaining: {time_str}"
                )
                return False
                
        if upgrade_id != 'restoreEnergy':
            upgrade_price = self._available_upgrades[upgrade_id].get('next', {}).get('price', 0)
            if upgrade_price > self._current_candies:
                logger.info(
                    f"{self.session_name} | 🍬 Not enough candies for upgrade {upgrade_id}, "
                    f"need {upgrade_price}, have {self._current_candies}"
                )
                return False
                
        return True
            
    async def _prioritize_upgrades(self) -> List[Dict]:
        self._update_available_upgrades()
        
        if self._current_candies < 3:
            return []
            
        upgrade_scores = []
        current_speed_per_sec = self._distance_per_sec
        
        excluded_upgrades = {'restoreEnergy', 'coinsPerTap'}
        
        for upgrade_id, upgrade_data in self._available_upgrades.items():
            if upgrade_id in excluded_upgrades:
                continue
                
            if 'next' not in upgrade_data:
                continue
                
            if not await self._is_upgrade_available(upgrade_id):
                continue
                
            next_level = upgrade_data.get('next', {})
            price = next_level.get('price', 0)
            current_level = upgrade_data.get('level', 0)
            increment = next_level.get('increment', 0)
            
            if price == 0 or increment == 0:
                continue

            efficiency = increment / price if price > 0 else 0
            
            payback_time_hours = (price / increment) if increment > 0 else float('inf')
            
            urgency = 1.0
            if current_speed_per_sec > 0:
                time_to_expensive = price / current_speed_per_sec
                if time_to_expensive < 3600:
                    urgency = 0.7
            
            final_score = (efficiency * urgency) / (payback_time_hours + 1)
            
            upgrade_scores.append({
                "upgrade_id": upgrade_id,
                "efficiency": efficiency,
                "payback_time": payback_time_hours,
                "final_score": final_score,
                "price": price,
                "increment": increment,
                "level": current_level
            })
            
        sorted_upgrades = sorted(
            upgrade_scores,
            key=lambda x: (-x['final_score'], x['payback_time'])
        )
        
        if sorted_upgrades:
            best_upgrade = sorted_upgrades[0]
            logger.info(
                f"{self.session_name} | 💡 Best upgrade: {best_upgrade['upgrade_id']}, "
                f"lvl: {best_upgrade['level']}, "
                f"price: {best_upgrade['price']} 🍬, "
                f"speed: +{best_upgrade['increment']}/sec"
            )
        else:
            logger.info(f"{self.session_name} | 📦 No upgrades available (may need to unlock boxes first)")
            
        return sorted_upgrades
        
    async def check_and_buy_upgrades(self) -> None:
        logger.info(f"{self.session_name} | ▶️ Starting upgrade phase with 🍬 {self._current_candies}")
        prioritized_upgrades = await self._prioritize_upgrades()
        
        if not prioritized_upgrades:
            logger.info(f"{self.session_name} | ⏹️ No upgrades to buy or not enough candies")
            return
            
        upgrades_bought_count = 0
        for upgrade_info in prioritized_upgrades:
            upgrade_id = upgrade_info['upgrade_id']
            price = upgrade_info['price']
            
            if price > self._current_candies:
                continue
                
            logger.info(f"{self.session_name} | 🛒 Trying to buy {upgrade_id} (Price: {price} 🍬)")
            result = await self.buy_upgrade(upgrade_id)
            
            if result:
                upgrades_bought_count += 1
                await asyncio.sleep(2)
                
        logger.info(
            f"{self.session_name} | ⏹️ Upgrade phase completed. Bought: {upgrades_bought_count} upgrades. "
            f"Remaining 🍬 {self._current_candies}"
        )

    async def _check_task(self, task_id: str) -> bool:
        task_data = self._available_tasks.get(task_id)
        if not task_data:
            logger.error(f"{self.session_name} | 🚫 Task {task_id} not found in available tasks.")
            return False

        try:
            headers = self.DEFAULT_HEADERS.copy()
            headers['User-Agent'] = self._user_agent
            headers['Onboarding'] = '2'
            if self._cookies:
                headers['Cookie'] = self._cookies

            payload = {"taskId": task_id}
            response = await self.make_request(
                'post',
                self.TASKS_CHECK_URL,
                headers=headers,
                json=payload
            )

            if not response:
                logger.error(f"{self.session_name} | 🚫 Failed to check task {task_id}, no response.")
                if task_id in self._available_tasks:
                     self._available_tasks[task_id]['time'] = int(time())
                return False

            if response.get('task'):
                 self._available_tasks[task_id] = response['task']

            if response.get("success") is True:
                reward = task_data.get('meta', {}).get('reward', 0)
                reward_type = task_data.get('meta', {}).get('rewardType', 'range')
                
                if 'currentCoins' in response:
                    self._current_distance = response.get('currentCoins', self._current_distance)
                    
                if 'currentCandies' in response:
                    self._current_candies = response.get('currentCandies', self._current_candies)

                reward_emoji = '🍬' if reward_type == 'candy' else '📏'
                logger.info(
                    f"{self.session_name} | ✅ Task {task_id} completed! "
                    f"Reward: {reward} {reward_emoji}"
                )
                return True
            else:
                logger.info(f"{self.session_name} | ⏳ Task {task_id} not yet completed or failed. Server time: {response.get('time')}")
                return False

        except Exception as e:
            logger.error(f"{self.session_name} | 🚫 Error checking task {task_id}: {str(e)}")
            return False

    async def _process_tasks(self) -> None:
        logger.info(f"{self.session_name} | ▶️ Starting task processing phase.")
        if not self._available_tasks:
            logger.info("🧾 No tasks available to process.")
            return

        tasks_processed_count = 0
        tasks_completed_count = 0
        supported_task_kinds = ["actionCheck", "checkPlusBenefits", "subscribeChannel"]

        for task_id, task_data in list(self._available_tasks.items()):
            task_kind = task_data.get('kind')
            task_title = task_data.get('title', task_id)

            if task_kind not in supported_task_kinds:
                continue
            
            last_check_time = task_data.get('time', 0)
            check_delay = task_data.get('meta', {}).get('checkDelay', 0)
            current_timestamp = int(time())

            if last_check_time > 0 and current_timestamp < last_check_time + check_delay:
                remaining = last_check_time + check_delay - current_timestamp
                logger.info(
                    f"{self.session_name} | ⏳ Task {task_id} on cooldown, "
                    f"remaining: {remaining}s"
                )
                continue
            
            if task_kind == "subscribeChannel":
                pass
            
            if task_kind in ["actionCheck", "checkPlusBenefits"]:
                completed = await self._check_task(task_id)
                if completed:
                    tasks_completed_count += 1
                tasks_processed_count +=1
                await asyncio.sleep(randint(3, 7))
        
        logger.info(f"{self.session_name} | ⏹️ Task processing phase completed. Checked: {tasks_processed_count}, Completed now: {tasks_completed_count}.")

    async def buy_tickets(self) -> None:
        if not self._game_data or 'user' not in self._game_data or 'yandex' not in self._game_data['user']:
            return

        logger.info(f"{self.session_name} | Yandex account detected. Starting to buy tickets with candies.")
        
        while self._current_candies >= 10:
            logger.info(f"{self.session_name} | Have {self._current_candies} candies. Trying to buy 1 ticket.")
            
            headers = self.DEFAULT_HEADERS.copy()
            headers['User-Agent'] = self._user_agent
            headers['Onboarding'] = '2'
            if self._cookies:
                headers['Cookie'] = self._cookies

            payload = {"count": 1}

            response = await self.make_request(
                'post',
                self.TICKETS_BUY_URL,
                headers=headers,
                json=payload
            )

            if response and 'result' in response:
                result = response['result']
                old_tickets = self._current_tickets
                self._current_tickets = result.get('currentTickets', self._current_tickets)
                self._current_candies = result.get('currentCandies', self._current_candies)
                logger.info(f"{self.session_name} | Successfully bought {self._current_tickets - old_tickets} ticket(s). "
                            f"Tickets: {self._current_tickets}, Candies: {self._current_candies}")
                await asyncio.sleep(uniform(1, 2))
            else:
                logger.error(f"{self.session_name} | Failed to buy ticket. Stopping ticket purchase for this cycle.")
                break
        
        logger.info(f"{self.session_name} | Finished buying tickets. Current candies: {self._current_candies}")

    async def game_loop(self) -> None:
        if self._game_data and 'game' in self._game_data:
            game_data = self._game_data['game']
            self._current_energy = game_data.get('currentEnergy', self._current_energy)
            self._max_energy = game_data.get('maxEnergy', self._max_energy)
            self._current_distance = game_data.get('currentCoins', self._current_distance)
            self._current_candies = game_data.get('currentCandies', self._current_candies)
            self._current_tickets = game_data.get('currentTickets', self._current_tickets)
            self._distance_per_tap = game_data.get('coinsPerTap', self._distance_per_tap)
            self._distance_per_hour = game_data.get('minePerHour', self._distance_per_hour)
            self._distance_per_sec = game_data.get('minePerSec', self._distance_per_sec)
            self._next_checkpoint_position = game_data.get('nextCheckpointPosition', self._next_checkpoint_position)
            
        sync_result = await self.sync_game(0)
        if not sync_result:
            logger.error("Initial sync failed, retrying in 30 seconds")
            await asyncio.sleep(30)
            return
        
        self._update_available_upgrades()
        
        while True:
            try:
                logger.info(f"{self.session_name} | ▶️ Starting active phase with ⚡ {self._current_energy}/{self._max_energy}")
                await self._active_phase()
                
                logger.info(f"{self.session_name} | ▶️ Starting task processing phase")
                await self._process_tasks()

                await self.buy_tickets()

                logger.info(
                    f"{self.session_name} | ⏭️ Skipping upgrade phase (testing auto-upgrades on checkpoints). "
                    f"Current 🍬 {self._current_candies}"
                )
                
                logger.info(f"{self.session_name} | ▶️ Starting sleep phase with ⚡ {self._current_energy}/{self._max_energy}")
                await self._sleep_phase()
                
                logger.info("🔑 Re-authenticating after sleep phase")
                auth_result = await self.auth_start()
                if not auth_result:
                    logger.error("🔑 Re-authentication failed, retrying in 30 seconds")
                    await asyncio.sleep(30)
                    continue
            except Exception as e:
                logger.error(f"{self.session_name} | 🔥 Error in game loop: {str(e)}")
                await asyncio.sleep(30)

    async def _sleep_phase(self) -> None:
        if self._current_energy >= self._max_energy * 0.8:
            logger.info(f"{self.session_name} | ✅ Energy already high, skipping sleep.")
            return
            
        energy_to_restore = int(self._max_energy * 0.8) - self._current_energy
        energy_per_sec = self._game_data.get('game', {}).get('energyPerSec', 3)
        if energy_per_sec <= 0: energy_per_sec = 3
            
        sleep_time = energy_to_restore / energy_per_sec
        max_sleep_time = 60 * 30
        sleep_time = min(sleep_time, max_sleep_time)
        sleep_time = max(sleep_time, 60)
        
        logger.info(f"{self.session_name} | 😴 Entering sleep for {int(sleep_time)}s to restore {energy_to_restore} ⚡")
        
        sleep_interval = 60
        total_slept = 0
        
        while total_slept < sleep_time:
            await asyncio.sleep(sleep_interval)
            total_slept += sleep_interval
            
            if total_slept % 300 == 0 or total_slept >= sleep_time:
                sync_result = await self.sync_game(0)
                if not sync_result:
                    logger.error("🔥 Sync failed during sleep phase")
                    continue
                    
                if self._current_energy >= self._max_energy * 0.8:
                    logger.info(f"{self.session_name} | ☀️ Energy recovered to {self._current_energy}/{self._max_energy}, ending sleep.")
                    break
                
                logger.info(
                    f"{self.session_name} | 💤 Sleep check: {total_slept}s passed, "
                    f"⚡ {self._current_energy}/{self._max_energy}, "
                    f"📏 {self._current_distance}, 🍬 {self._current_candies}"
                )
        
        logger.info(f"{self.session_name} | ⏹️ Sleep phase completed. Current ⚡ {self._current_energy}/{self._max_energy}")

    async def run(self) -> None:
        if not await self.initialize_session():
            raise InvalidSession("Failed to initialize session")

        random_delay = uniform(1, settings.SESSION_START_DELAY)
        logger.info(f"{self.session_name} | Bot will start in {int(random_delay)}s")
        await asyncio.sleep(random_delay)

        proxy_conn = {'connector': ProxyConnector.from_url(self._current_proxy)} if self._current_proxy else {}
        async with CloudflareScraper(timeout=aiohttp.ClientTimeout(60), **proxy_conn) as http_client:
            self._http_client = http_client

            while True:
                try:
                    session_config = config_utils.get_session_config(self.session_name, CONFIG_PATH)
                    if not await self.check_and_update_proxy(session_config):
                        logger.warning('Failed to find working proxy. Sleep 5 minutes.')
                        await asyncio.sleep(300)
                        continue

                    await self.process_bot_logic()
                    
                except InvalidSession:
                    raise
                except Exception as error:
                    sleep_duration = uniform(60, 120)
                    logger.error(f"{self.session_name} | Unknown error: {error}. Sleeping for {int(sleep_duration)}")
                    await asyncio.sleep(sleep_duration)

    async def process_bot_logic(self) -> None:
        if not self._game_data:
            if not await self.auth_start():
                logger.error("Failed to authenticate")
                await asyncio.sleep(60)
                return
                
        onboarding_level = self._game_data.get('app', {}).get('onboarding', 0)
        logger.info(f"{self.session_name} | Current onboarding level: {onboarding_level}")
        
        if onboarding_level == 0:
            if not await self.game_onboarding():
                logger.error(f"{self.session_name} | Failed to complete onboarding")
                await asyncio.sleep(60)
                return
        
        await self.game_loop()

    async def _active_phase(self) -> None:
        total_taps_sent_in_phase = 0
        initial_energy_in_phase = self._current_energy
        energy_restores_used_in_phase = 0
        

        while True:
            if self._current_energy <= 50:
                energy_restored = await self.restore_energy_if_needed()
                if energy_restored:
                    energy_restores_used_in_phase += 1
                else:
                    break
                
            if self._current_energy > 200:
                taps_to_accumulate = randint(35, 45)
            elif self._current_energy > 100:
                taps_to_accumulate = randint(25, 35)
            else:
                taps_to_accumulate = randint(15, 25)
            
            taps_to_accumulate = min(taps_to_accumulate, max(0, self._current_energy - 5))

            if taps_to_accumulate == 0:
                break

            sync_result = await self.sync_game(taps_to_accumulate)
            if not sync_result:
                logger.error(f"{self.session_name} | Sync failed during active phase, retrying...")
                await asyncio.sleep(10)
                continue
                
            total_taps_sent_in_phase += taps_to_accumulate
            await asyncio.sleep(uniform(1.5, 2.5))
        
        distance_traveled = total_taps_sent_in_phase * self._distance_per_tap
        logger.info(
            f"{self.session_name} | ⏹️ Active phase completed. Taps: {total_taps_sent_in_phase}, "
            f"📏 Distance traveled: {distance_traveled}, "
            f"⚡ Used: {initial_energy_in_phase - self._current_energy + energy_restores_used_in_phase * self._max_energy}, "
            f"Restored: {energy_restores_used_in_phase}x. Current 📏 {self._current_distance}, 🍬 {self._current_candies}"
        )

    async def restore_energy_if_needed(self) -> bool:
        current_date = datetime.now().strftime("%Y-%m-%d")
        if self._last_restore_date and self._last_restore_date != current_date:
            logger.info(f"{self.session_name} | ☀️ New day detected, resetting energy restores counter")
            self._energy_restores_used = 0
            self._restore_energy_attempts = 0
            
        if self._energy_restores_used >= self._energy_restores_max:
            logger.info(
                f"{self.session_name} | 🔋 Daily energy restore limit reached "
                f"({self._energy_restores_used}/{self._energy_restores_max})"
            )
            return False
            
        if self._restore_energy_attempts >= 2:
            logger.warning(f"{self.session_name} | ⚠️ Too many restore energy attempts, skipping")
            return False
            
        if self._pending_upgrade_check:
            self._update_available_upgrades()
            self._pending_upgrade_check = False
            
        energy_restore_data = self._available_upgrades.get('restoreEnergy')
        if energy_restore_data:
            day_limitation = energy_restore_data.get('dayLimitation', 6)
            current_level = energy_restore_data.get('level', 0)
            
            self._energy_restores_max = day_limitation
            self._energy_restores_used = current_level
            
            if current_level < day_limitation:
                logger.info(
                    f"{self.session_name} | ⚡ Energy low ({self._current_energy}/{self._max_energy}), "
                    f"using restore ({current_level}/{day_limitation} used)"
                )
                result = await self.buy_upgrade('restoreEnergy')
                if result:
                    logger.info(f"{self.session_name} | ✅ Energy restored: {self._current_energy}/{self._max_energy}")
                    return True
                    
        return False

async def run_tapper(tg_client: UniversalTelegramClient):
    bot = BaseBot(tg_client=tg_client)
    try:
        await bot.run()
    except InvalidSession as e:
        logger.error(f"{self.session_name} | Invalid Session: {e}")
        raise