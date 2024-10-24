# Qlyuker Bot

[![Bot Link](https://img.shields.io/badge/Telegram-Bot_Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/qlyukerbot/start?startapp=bro-228618799)
[![Channel Link](https://img.shields.io/badge/Telegram-Channel_Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+dhoKHLCh5Bk3MWU6)

---

## 📑 Table of Contents
1. [Description](#description)
2. [Key Features](#key-features)
3. [Installation](#installation)
   - [Quick Start](#quick-start)
   - [Manual Installation](#manual-installation)
4. [Settings](#settings)
5. [Support and Donations](#support-and-donations)
6. [Contact](#contact)

---

## 📜 Description
**Qlyuker Bot** is a powerful bot for Telegram that helps automate interaction with the bot. It supports multithreading, proxy integration, and session creation via QR codes.

---

## 🌟 Key Features
- 🔄 **Multithreading** — supports parallel processes to increase work speed.
- 🔐 **Proxy binding to session** — allows secure work through proxy servers.
- 📲 **Auto-account registration** — quick account registration via referral links.
- 🎁 **Bonus automation** — automatic collection of daily bonuses without manual actions.
- 📸 **Session creation via QR code** — fast and convenient session generation through a mobile app.
- 📄 **Support for pyrogram session format (.session)** — easy integration with the Telegram API for session storage.

---

## 🛠️ Installation

### Quick Start
1. **Download the project:**
   ```bash
   git clone https://github.com/Mffff4/qlyukerbot.git
   cd qlyukerbot
   ```

2. **Install dependencies:**
   - **Windows**:
     ```bash
     run.bat
     ```
   - **Linux**:
     ```bash
     run.sh
     ```

3. **Obtain API keys:**
   - Go to [my.telegram.org](https://my.telegram.org) and get your `API_ID` and `API_HASH`.
   - Add this information to the `.env` file.

4. **Run the bot:**
   ```bash
   python3 main.py --action 3  # Run the bot
   ```

### Manual Installation
1. **Linux:**
   ```bash
   sudo sh install.sh
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   cp .env-example .env
   nano .env  # Add your API_ID and API_HASH
   python3 main.py
   ```

2. **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env-example .env
   python main.py
   ```

---

## ⚙️ Settings

| Setting               | Default Value            | Description                                                                                                                                 |
|-----------------------|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| **API_ID**            |                          | Unique application ID required for connecting to the Telegram API.                                                                          |
| **API_HASH**          |                          | Application hash used for authentication and security when connecting to the API.                                                            |
| **USE_PROXY_FROM_FILE**| False                    | Flag indicating whether to use proxy from bot/config/proxies.txt file.                                                                       |
| **REF_ID**            | "bro-228618799"          | Referral argument used in links to track referrals.                                                                                          |
| **TAPS**              | [10, 100]                | List of values determining the number of taps per cycle.                                                                                     |
| **SLEEP_BETWEEN_TAPS** | [1, 3]                   | List of values determining the delay between taps.                                                                                           |
| **ENERGY_THRESHOLD**   | 0.05                     | Energy threshold at which actions start.                                                                                                     |
| **SLEEP_ON_LOW_ENERGY**| 900                      | Waiting time at low energy level. Value in seconds.                                                                                          |
| **SLEEP_AFTER_UPGRADE**| 1                        | Delay time after an upgrade. Value in seconds.                                                                                               |
| **DELAY_BETWEEN_TASKS**| [3, 15]                  | List of values determining the delay between tasks.                                                                                          |
| **UPGRADE_CHECK_DELAY**| 60                       | Delay between upgrade checks. Value in seconds.                                                                                              |
| **RETRY_DELAY**        | 3                        | Waiting time before retrying after an error. Value in seconds.                                                                                |
| **MAX_RETRIES**        | 5                        | Maximum number of attempts to complete a task in case of failure.                                                                             |
| **ENABLE_TAPS**        | True                     | Flag to enable/disable the tap function.                                                                                                     |
| **ENABLE_CLAIM_REWARDS**| True                    | Flag to enable/disable reward claiming.                                                                                                      |
| **ENABLE_UPGRADES**    | True                     | Flag to enable/disable upgrades.                                                                                                             |
| **ENABLE_TASKS**       | True                     | Flag to enable/disable task execution.                                                                                                       |
| **ENABLE_RAFFLE**      | True                    | Flag to enable/disable participation in the raffle.                                                                                        |
| **RAFFLE_BUY_INTERVAL**| 600                     | Interval between ticket purchases for the raffle (in seconds).                                                                             |
| **RAFFLE_SESSIONS**    | []                      | List of sessions to participate in the raffle. An empty list means all sessions participate. Example: ["session1", "session2"]            |
| **SLEEP_HOURS**       | []                       | List of two strings representing the start and end of the sleep period in "HH:MM" format. If the list is empty, the bot works 24/7.        |

---

## 💰 Support and Donations

Support the development using cryptocurrencies or platforms:

| Currency               | Wallet Address                                                                     |
|------------------------|------------------------------------------------------------------------------------|
| Bitcoin (BTC)|bc1qt84nyhuzcnkh2qpva93jdqa20hp49edcl94nf6| 
| Ethereum (ETH)|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
|TON|UQBlvCgM84ijBQn0-PVP3On0fFVWds5SOHilxbe33EDQgryz|
| Binance Coin (BNB)|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Solana (SOL)|3vVxkGKasJWCgoamdJiRPy6is4di72xR98CDj2UdS1BE| 
| Ripple (XRP)|rPJzfBcU6B8SYU5M8h36zuPcLCgRcpKNB4| 
| Dogecoin (DOGE)|DST5W1c4FFzHVhruVsa2zE6jh5dznLDkmW| 
| Polkadot (DOT)|1US84xhUghAhrMtw2bcZh9CXN3i7T1VJB2Gdjy9hNjR3K71| 
| Litecoin (LTC)|ltc1qcg8qesg8j4wvk9m7e74pm7aanl34y7q9rutvwu| 
| Matic|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Tron (TRX)|TQkDWCjchCLhNsGwr4YocUHEeezsB4jVo5| 


---

## 📞 Contact

If you have any questions or suggestions:
- **Telegram**: [Join our channel](https://t.me/+ap1Yd23CiuVkOTEy)
