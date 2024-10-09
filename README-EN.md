

# Telegram Bot

[![Static Badge](https://img.shields.io/badge/Telegram-Link_to_bot-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/qlyukerbot/start?startapp=bro-228618799)
[![Static Badge](https://img.shields.io/badge/Telegram-Link_to_my_channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+ap1Yd23CiuVkOTEy)
> README на русском языке доступно [здесь](README.md)

## Recommendation Before Using

# 🔥🔥 Use PYTHON version 3.10 🔥🔥

## Features
|                   **Functionality**                   | **Supported** |
|:-----------------------------------------------------:|:-------------:|
|                     **Multithreading**                 |      ✅       | 
|                **Proxy Binding to Session**           |      ✅       | 
|       **Auto-registration of Accounts via Referral Link** |      ✅       |
|             **Automatic Booster Upgrades**            |      ✅       |
|                **Daily Bonus Collection**             |      ✅       |
|                  **Session Creation via QR Code**     |      ✅       |
|                  **Support for pyrogram .session**    |      ✅       |


## [Settings](https://github.com/Mffff4/qlyukerbot/blob/main/.env-example/)
| Settings                     | Description                                                                                   |
|------------------------------|-----------------------------------------------------------------------------------------------|
| **API_ID**                   | Unique identifier for the application required to connect to the Telegram API. Type: `int`.  |
| **API_HASH**                 | Hash of the application used for authentication and security when connecting to the API. Type: `str`. |
| **USE_PROXY_FROM_FILE**      | Flag indicating whether to use a proxy from the file `bot/config/proxies.txt`. Type: `bool`. Values: `True` or `False`. |
| **REF_ID**                   | Referral argument used in links for tracking referrals. Type: `str`. Example: `"bro-228618799"`. |
| **TAPS**                     | List of values determining the number of taps to perform in one cycle. Type: `list`. Default values: `[10, 100]`. |
| **SLEEP_BETWEEN_TAPS**      | List of values determining the delay between taps. Type: `list`. Default values: `[1, 3]`.    |
| **ENERGY_THRESHOLD**         | Energy threshold at which actions begin. Type: `float`. Default value: `0.05`.               |
| **SLEEP_ON_LOW_ENERGY**      | Waiting time when energy is low. Type: `int`. Default value: `60` (in seconds).              |
| **SLEEP_AFTER_UPGRADE**     | Delay time after performing an upgrade. Type: `int`. Default value: `1` (in seconds).       |
| **DELAY_BETWEEN_TASKS**     | List of values determining the delay between task executions. Type: `list`. Default values: `[3, 15]`. |
| **UPGRADE_CHECK_DELAY**     | Delay between checks for upgrade availability. Type: `int`. Default value: `5` (in seconds). |
| **RETRY_DELAY**              | Waiting time before retrying in case of an error. Type: `int`. Default value: `3` (in seconds). |
| **MAX_RETRIES**              | Maximum number of attempts to perform a task in case of an error. Type: `int`. Default value: `5`. |


## Quick Start 📚

For quick installation and launch - run the file run.bat on Windows or run.sh on Linux

## Prerequisites
Before starting, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10**

## Getting API Keys
1. Go to [my.telegram.org](https://my.telegram.org) and log in using your phone number.
2. Select **"API development tools"** and fill out the form to register a new application.
3. Write down the `API_ID` and `API_HASH` in the `.env` file provided after registering your app.

## Installation
You can download the [**Repository**](https://github.com/Mffff4/qlyukerbot.git) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/Mffff4/qlyukerbot.git
cd qlyukerbot
```

Then for automatic installation enter:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

### Manual Installation on Linux
```shell
sudo sh install.sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must enter your API_ID and API_HASH, the rest is taken as default
python3 main.py
```

You can also quickly start using the following arguments, for example:
```shell
~/qlyukerbot >>> python3 main.py --action (1/2/3/4)
# Or
~/qlyukerbot >>> python3 main.py -a (1/2/3/4)

#1. Create a session
#2. Create a session via QR
#3. Run the bot
#4. Run the bot via Telegram (Beta)
```

### Manual Installation on Windows
```shell
python -m venv venv
venv\Scriptsctivate
pip install -r requirements.txt
copy .env-example .env
# Enter your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also quickly start using the following arguments, for example:
```shell
~/qlyukerbot >>> python main.py --action (1/2/3/4)
# Or
~/qlyukerbot >>> python main.py -a (1/2/3/4)

#1. Create a session
#2. Create a session via QR
#3. Run the bot
#4. Run the bot via Telegram (Beta)
```
## Thank you  
| Token | Wallet Address |
|:----------------------------------------------:|:--------------:|
| Bitcoin (BTC)|bc1qt84nyhuzcnkh2qpva93jdqa20hp49edcl94nf6| 
|Ethereum (ETH)|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
|Binance Coin (BNB)|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
|Solana (SOL)|3vVxkGKasJWCgoamdJiRPy6is4di72xR98CDj2UdS1BE| 
|Ripple (XRP)|rPJzfBcU6B8SYU5M8h36zuPcLCgRcpKNB4| 
|Dogecoin (DOGE)|DST5W1c4FFzHVhruVsa2zE6jh5dznLDkmW| 
|Polka dot (DOT)|1US84xhUghAhrMtw2bcZh9CXN3i7T1VJB2Gdjy9hNjR3K71| 
|Litecoin (LTC)|ltc1qcg8qesg8j4wvk9m7e74pm7aanl34y7q9rutvwu| 
|Matic|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
|Tron (TRX)|TQkDWCjchCLhNsGwr4YocUHEeezsB4jVo5| 
|TON|UQAjFg_VSG6lpV1WCXVt3_aBzC7TQZ_kU8D70cTv1KeiVq4_|
