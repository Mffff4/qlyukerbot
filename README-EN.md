

# Telegram Bot

[![Static Badge](https://img.shields.io/badge/Telegram-Link_to_bot-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/qlyukerbot/start?startapp=bro-228618799)

> README на русском языке доступно [здесь](README.md)

## Recommendation Before Using

# 🔥🔥 Use PYTHON version 3.10 🔥🔥

## Features
|                    Feature                     |   Supported    |
|:----------------------------------------------:|:--------------:|
|                 Multithreading                 |       ✅        |
|        Proxy binding to the session            |       ✅        |
| Auto-registration of the account via ref link  |       ✅        |
|      Automatic booster upgrades                |       ✅        |
|      Pyrogram .session file support            |       ✅        |
|     Session creation via QR code               |       ✅        |


## [Settings](https://github.com/Mffff4/qlyukerbot/blob/main/.env-example/)
|        Setting           |                                     Description                                      |
|:------------------------:|:------------------------------------------------------------------------------------:|
|    **API_ID / API_HASH**  | Data from the platform where the Telegram session will be launched (default - android) |
|  **MIN_TAPS / MAX_TAPS**  |        Number of taps per cycle (default from 10 to 100)                              |
| **MIN_SLEEP_BETWEEN_TAPS**|     Minimum delay between taps (default - 1 second)                                  |
| **MAX_SLEEP_BETWEEN_TAPS**|     Maximum delay between taps (default - 3 seconds)                                 |
|   **ENERGY_THRESHOLD**    |        Energy threshold for actions (default - 0.05)                                 |
|   **SLEEP_ON_LOW_ENERGY** |     Waiting time with low energy (default - 15 minutes)                              |
|   **SLEEP_AFTER_UPGRADE** |     Delay after upgrading (default - 1 second)                                       |
|   **SLEEP_AFTER_TAPS**    |     Delay after all taps are done (default - 0 seconds)                              |
| **USE_PROXY_FROM_FILE**   |     Use proxy from `bot/config/proxies.txt` (True / False)                           |


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
