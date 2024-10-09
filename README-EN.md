# Qlyuker Bot
🔗 Automated Telegram bot.

[![Static Badge](https://img.shields.io/badge/Telegram-Bot_Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/qlyukerbot/start?startapp=bro-228618799)
[![Static Badge](https://img.shields.io/badge/Telegram-Channel_Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+ap1Yd23CiuVkOTEy)

## Table of Contents
- [Recommendation before Use](#recommendation-before-use)
- [Functionality](#functionality)
- [Settings](#settings)
- [Quick Start](#quick-start)
- [Getting API Keys](#getting-api-keys)
- [Installation](#installation)
- [Acknowledgments](#acknowledgments)

## Recommendation before Use
# 🔥🔥 Use PYTHON version 3.10 🔥🔥

> README на русском языке доступно [здесь](README.md)

## Functionality  
|                   **Functionality**                   | **Supported** |
|:-----------------------------------------------------:|:-------------:|
|                     **Multithreading**                |        ✅     | 
|                **Proxy Binding to Session**           |        ✅     | 
|       **Auto Registration of Account via Your Ref Link** |        ✅     |
|             **Automatic Booster Upgrades**            |        ✅     |
|                  **Daily Bonus Collection**           |        ✅     |
|                  **Session Creation via QR Code**     |        ✅     |
|                  **Support for pyrogram .session**    |        ✅     |

## Settings
| Settings                     | Description                                                                                       |
|-------------------------------|------------------------------------------------------------------------------------------------|
| **API_ID**                    | Unique application identifier needed to connect to the Telegram API. Type: `int`.           |
| **API_HASH**                  | Application hash used for authentication and security when connecting to the API. Type: `str`. |
| **USE_PROXY_FROM_FILE**       | Flag indicating whether to use proxies from the file `bot/config/proxies.txt`. Type: `bool`. Values: `True` or `False`. |
| **REF_ID**                    | Referral argument used in links to track referrals. Type: `str`. Example: `"bro-228618799"`. |
| **TAPS**                      | List of values determining the number of clicks per cycle. Type: `list`. Default values: `[10, 100]`. |
| **SLEEP_BETWEEN_TAPS**       | List of values determining the delay between clicks. Type: `list`. Default values: `[1, 3]`. |
| **ENERGY_THRESHOLD**          | Energy threshold at which actions begin. Type: `float`. Default value: `0.05`.                 |
| **SLEEP_ON_LOW_ENERGY**       | Waiting time when energy level is low. Type: `int`. Default value: `60` (in seconds).        |
| **SLEEP_AFTER_UPGRADE**      | Delay time after performing an upgrade. Type: `int`. Default value: `1` (in seconds).         |
| **DELAY_BETWEEN_TASKS**      | List of values determining the delay between task executions. Type: `list`. Default values: `[3, 15]`. |
| **UPGRADE_CHECK_DELAY**      | Delay between checks for available upgrades. Type: `int`. Default value: `5` (in seconds).    |
| **RETRY_DELAY**               | Waiting time before retrying in case of an error. Type: `int`. Default value: `3` (in seconds). |
| **MAX_RETRIES**               | Maximum number of attempts to execute a task in case of an error. Type: `int`. Default value: `5`. |

## Quick Start 📚
For quick installation and subsequent launch, run the `run.bat` file on Windows or `run.sh` on Linux.

## Prerequisites
Before you start, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10**

## Getting API Keys
1. Go to [my.telegram.org](https://my.telegram.org) and log in using your phone number.
2. Select **"API development tools"** and fill out the form to register a new application.
3. Write down `API_ID` and `API_HASH` in the `.env` file provided after registering your application.

## Installation
You can download the [**Repository**](https://github.com/Mffff4/qlyukerbot.git) by cloning it to your system and installing the required dependencies:

```shell
git clone https://github.com/Mffff4/qlyukerbot.git
cd qlyukerbot
```

Then for automatic installation enter:

### Windows
```shell
run.bat
```

### Linux
```shell
run.sh
```

## Manual Installation on Linux
```shell
sudo sh install.sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

Also, for quick launching you can use arguments, for example:
```shell
~/qlyukerbot >>> python3 main.py --action (1/2/3/4)
# Or
~/qlyukerbot >>> python3 main.py -a (1/2/3/4)

#1. Create a session
#2. Create a session via QR
#3. Start the bot
#4. Start the bot via Telegram (Beta)
```

## Manual Installation on Windows
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

Also, for quick launching you can use arguments, for example:
```shell
~/qlyukerbot >>> python main.py --action (1/2/3/4)
# Or
~/qlyukerbot >>> python main.py -a (1/2/3/4)

#1. Create a session
#2. Create a session via QR
#3. Start the bot
#4. Start the bot via Telegram (Beta)
```

## Acknowledgments  
|                   Token                   | Wallet Address |
|:-------------------------------------------:|:--------------:|
| Bitcoin (BTC)|bc1qt84nyhuzcnkh2qpva93jdqa20hp49edcl94nf6| 
| Ethereum (ETH)|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Binance Coin (BNB)|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Solana (SOL)|3vVxkGKasJWCgoamdJiRPy6is4di72xR98CDj2UdS1BE| 
| Ripple (XRP)|rPJzfBcU6B8SYU5M8h36zuPcLCgRcpKNB4| 
| Dogecoin (DOGE)|DST5W1c4FFzHVhruVsa2zE6jh5dznLDkmW| 
| Polkadot (DOT)|1US84xhUghAhrMtw2bcZh9CXN3i7T1VJB2Gdjy9hNjR3K71| 
| Litecoin (LTC)|ltc1qcg8qesg8j4wvk9m7e74pm7aanl34y7q9rutvwu| 
| Matic|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Tron (TRX)|TQkDWCjchCLhNsGwr4YocUHEeezsB4jVo5| 
