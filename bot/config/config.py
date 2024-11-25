from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator, field_validator
from typing import Dict
import re


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

    API_ID: int
    API_HASH: str

    USE_PROXY_FROM_FILE: bool = False
    REF_ID: str = "bro-228618799"

    TAPS: list = [10, 100] 
    SLEEP_BETWEEN_TAPS: list = [1, 3] 
    ENERGY_THRESHOLD: float = 0.05
    SLEEP_ON_LOW_ENERGY: int = 60 * 15
    SLEEP_AFTER_UPGRADE: int = 1
    DELAY_BETWEEN_TASKS: list = [3, 15]

    UPGRADE_CHECK_DELAY: int = 60
    RETRY_DELAY: int = 3
    MAX_RETRIES: int = 5

    ENABLE_TAPS: bool = True
    ENABLE_CLAIM_REWARDS: bool = True
    ENABLE_UPGRADES: bool = True
    ENABLE_TASKS: bool = True

    ENABLE_RAFFLE: bool = False
    RAFFLE_BUY_INTERVAL: int = 600
    RAFFLE_SESSIONS: list[str] = []

    MAX_INCOME_PER_HOUR: float = 0

    RESERVED_BALANCE: str = ""

    @field_validator('RESERVED_BALANCE')
    @classmethod
    def parse_reserved_balance(cls, v: str) -> Dict[str, float]:
        if not v:
            return {}
        
        try:
            balance_dict = {}
            matches = re.findall(r'\[(.*?):(.*?)\]', v)
            for session, amount in matches:
                balance_dict[session.strip()] = float(amount.strip())
            return balance_dict
        except Exception as e:
            print(f"Error parsing RESERVED_BALANCE: {e}")
            return {}

    @property
    def MIN_TAPS(self):
        return self.TAPS[0]

    @property
    def MAX_TAPS(self):
        return self.TAPS[1]

    @property
    def MIN_SLEEP_BETWEEN_TAPS(self):
        return self.SLEEP_BETWEEN_TAPS[0]

    @property
    def MAX_SLEEP_BETWEEN_TAPS(self):
        return self.SLEEP_BETWEEN_TAPS[1]

    @property
    def MIN_DELAY_BETWEEN_TASKS(self):
        return self.DELAY_BETWEEN_TASKS[0]

    @property
    def MAX_DELAY_BETWEEN_TASKS(self):
        return self.DELAY_BETWEEN_TASKS[1]

settings = Settings()
