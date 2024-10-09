
# Qlyuker Bot

[![Bot Link](https://img.shields.io/badge/Telegram-Бот_Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/qlyukerbot/start?startapp=bro-228618799)
[![Channel Link](https://img.shields.io/badge/Telegram-Канал_Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+ap1Yd23CiuVkOTEy)

---

## 📑 Оглавление
1. [Описание](#описание)
2. [Ключевые особенности](#ключевые-особенности)
3. [Установка](#установка)
   - [Быстрый старт](#быстрый-старт)
   - [Ручная установка](#ручная-установка)
4. [Настройки](#настройки)
5. [Поддержка и донаты](#поддержка-и-донаты)
6. [Контакты](#контакты)

---

## 📜 Описание
**Qlyuker Bot** — это мощный бот для Telegram, который помогает автоматизировать взаимодействие с ботом. Поддерживает многопоточность, работу с прокси и создание сессий через QR-коды.

---

## 🌟 Ключевые особенности
- 🔄 **Многопоточность** — поддержка параллельных процессов для повышения скорости работы.
- 🔐 **Привязка прокси к сессии** — возможность безопасной работы через прокси-сервера.
- 📲 **Авто-регистрация аккаунтов** — быстрая регистрация аккаунтов по реферальным ссылкам.
- 🎁 **Автоматизация бонусов** — сбор ежедневных бонусов без необходимости ручных действий.
- 📸 **Создание сессий через QR-код** — быстрая и удобная генерация сессий через мобильное приложение.
- 📄 **Поддержка формата сессий pyrogram (.session)** — простая интеграция с API Telegram для хранения сессий.

---

## 🛠️ Установка

### Быстрый старт
1. **Скачайте проект:**
   ```bash
   git clone https://github.com/Mffff4/qlyukerbot.git
   cd qlyukerbot
   ```

2. **Установите зависимости:**
   - **Windows**:
     ```bash
     run.bat
     ```
   - **Linux**:
     ```bash
     run.sh
     ```

3. **Получите API ключи:**
   - Перейдите на [my.telegram.org](https://my.telegram.org) и получите `API_ID` и `API_HASH`.
   - Добавьте эти данные в файл `.env`.

4. **Запустите бота:**
   ```bash
   python3 main.py --action 3  # Запустить бота
   ```

### Ручная установка
1. **Linux:**
   ```bash
   sudo sh install.sh
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   cp .env-example .env
   nano .env  # Укажите свои API_ID и API_HASH
   python3 main.py
   ```

2. **Windows:**
   ```bash
   python -m venv venv
   venv\Scriptsctivate
   pip install -r requirements.txt
   copy .env-example .env
   python main.py
   ```

---

## ⚙️ Настройки

Пример конфигурации `.env` файла:

```plaintext
API_ID = "Ваш уникальный ID"
API_HASH = "Ваш хэш"
USE_PROXY_FROM_FILE = True
REF_ID = "bro-228618799"
TAPS = [10, 100]
SLEEP_BETWEEN_TAPS = [1, 3]
ENERGY_THRESHOLD = 0.05
SLEEP_ON_LOW_ENERGY = 60
SLEEP_AFTER_UPGRADE = 1
DELAY_BETWEEN_TASKS = [3, 15]
UPGRADE_CHECK_DELAY = 5
RETRY_DELAY = 3
MAX_RETRIES = 5
```

---

## 💰 Поддержка и донаты

Поддержите разработку с помощью криптовалют или платформ:

| Валюта               | Адрес кошелька                                                                       |
|----------------------|-------------------------------------------------------------------------------------|
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

## 📞 Контакты

Если у вас возникли вопросы или предложения:
- **Telegram**: [Присоединяйтесь к нашему каналу](https://t.me/+ap1Yd23CiuVkOTEy)

