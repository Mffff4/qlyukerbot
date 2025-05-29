# BOT Bot

[🇷🇺 Русский](README-RU.md) | [🇬🇧 English](README.md)

[<img src="https://res.cloudinary.com/dkgz59pmw/image/upload/v1736756459/knpk224-28px-market_ksivis.svg" alt="Market Link" width="200">](https://t.me/MaineMarketBot?start=8HVF7S9K)
[<img src="https://res.cloudinary.com/dkgz59pmw/image/upload/v1736756459/knpk224-28px-channel_psjoqn.svg" alt="Channel Link" width="200">](https://t.me/+vpXdTJ_S3mo0ZjIy)
[<img src="https://res.cloudinary.com/dkgz59pmw/image/upload/v1736756459/knpk224-28px-chat_ixoikd.svg" alt="Chat Link" width="200">](https://t.me/+wWQuct9bljQ0ZDA6)

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
   git clone https://bitbucket.org:mffff4/qlyukerbot.git
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
   python3 main.py --a 1  # Запустить бота
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
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env-example .env
   python main.py
   ```

---


## ⚙️ Настройки

| Параметр                  | Значение по умолчанию | Описание                                                 |
|---------------------------|----------------------|---------------------------------------------------------|
| **API_ID**                |                      | Идентификатор приложения Telegram API                   |
| **API_HASH**              |                      | Хэш приложения Telegram API                              |
| **GLOBAL_CONFIG_PATH**    |                      | Путь к файлам конфигурации. По умолчанию используется переменная окружения TG_FARM |
| **FIX_CERT**              | False                | Исправить ошибки сертификата SSL                        |
| **SESSION_START_DELAY**   | 360                  | Задержка перед началом сессии (в секундах)             |
| **REF_ID**                |                      | Идентификатор реферала для новых аккаунтов             |
| **USE_PROXY**             | True                 | Использовать прокси                                     |
| **SESSIONS_PER_PROXY**    | 1                    | Количество сессий на один прокси                        |
| **DISABLE_PROXY_REPLACE** | False                | Отключить замену прокси при ошибках                     |
| **BLACKLISTED_SESSIONS**  | ""                   | Сессии, которые не будут использоваться (через запятую)|
| **DEBUG_LOGGING**         | False                | Включить подробный логгинг                              |
| **DEVICE_PARAMS**         | False                | Использовать пользовательские параметры устройства        |
| **AUTO_UPDATE**           | True                 | Автоматические обновления                               |
| **CHECK_UPDATE_INTERVAL** | 300                  | Интервал проверки обновлений (в секундах)              |

---

## 💰 Поддержка и донаты

Поддержите разработку с помощью криптовалют или платформ:

| Валюта               | Адрес кошелька                                                                       |
|----------------------|-------------------------------------------------------------------------------------|
| Bitcoin (BTC)        |bc1qt84nyhuzcnkh2qpva93jdqa20hp49edcl94nf6| 
| Ethereum (ETH)       |0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| TON                  |UQBlvCgM84ijBQn0-PVP3On0fFVWds5SOHilxbe33EDQgryz|
| Binance Coin         |0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Solana (SOL)         |3vVxkGKasJWCgoamdJiRPy6is4di72xR98CDj2UdS1BE| 
| Ripple (XRP)         |rPJzfBcU6B8SYU5M8h36zuPcLCgRcpKNB4| 
| Dogecoin (DOGE)      |DST5W1c4FFzHVhruVsa2zE6jh5dznLDkmW| 
| Polkadot (DOT)       |1US84xhUghAhrMtw2bcZh9CXN3i7T1VJB2Gdjy9hNjR3K71| 
| Litecoin (LTC)       |ltc1qcg8qesg8j4wvk9m7e74pm7aanl34y7q9rutvwu| 
| Matic                |0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Tron (TRX)           |TQkDWCjchCLhNsGwr4YocUHEeezsB4jVo5| 

---

## 📞 Контакты

Если у вас возникли вопросы или предложения:
- **Telegram**: [Присоединяйтесь к нашему каналу](https://t.me/+vpXdTJ_S3mo0ZjIy)

---
## ⚠️ Дисклеймер

Данное программное обеспечение предоставляется "как есть", без каких-либо гарантий. Используя этот бот, вы принимаете на себя полную ответственность за его использование и любые последствия, которые могут возникнуть.

Автор не несет ответственности за:
- Любой прямой или косвенный ущерб, связанный с использованием бота
- Возможные нарушения условий использования сторонних сервисов
- Блокировку или ограничение доступа к аккаунтам

Используйте бота на свой страх и риск и в соответствии с применимым законодательством и условиями использования сторонних сервисов.
