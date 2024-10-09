# Qlyuker Bot
🔗 Автоматизированный бот для Telegram.

[![Static Badge](https://img.shields.io/badge/Телеграм-Ссылка_на_бота-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/qlyukerbot/start?startapp=bro-228618799)
[![Static Badge](https://img.shields.io/badge/Телеграм-Ссылка_на_канал-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+ap1Yd23CiuVkOTEy)

## Содержание
- [Рекомендация перед использованием](#рекомендация-перед-использованием)
- [Функционал](#функционал)
- [Настройки](#настройки)
- [Быстрый старт](#быстрый-старт)
- [Получение API ключей](#получение-api-ключей)
- [Установка](#установка)
- [Отблагодарить](#отблагодарить)

## Рекомендация перед использованием
# 🔥🔥 Используйте PYTHON версии 3.10 🔥🔥

> 🇪🇳 README in English available [here](README-EN.md)

## Функционал  
|                   **Функционал**                   | **Поддерживается** |
|:---------------------------------------------------:|:------------------:|
|                     **Многопоточность**              |        ✅          | 
|                **Привязка прокси к сессии**         |        ✅          | 
|       **Авто-регистрация аккаунта по вашей реф. ссылке** |        ✅          |
|             **Автоматическое улучшение бустеров**   |        ✅          |
|                  **Сбор ежедневных бонусов**        |        ✅          |
|                  **Создание сессий через QR код**    |        ✅          |
|                  **Поддержка pyrogram .session**     |        ✅          |

## Настройки
| Настройки                     | Описание                                                                                       |
|-------------------------------|------------------------------------------------------------------------------------------------|
| **API_ID**                    | Уникальный идентификатор приложения, необходимый для подключения к Telegram API. Тип: `int`.   |
| **API_HASH**                  | Хэш приложения, используемый для аутентификации и безопасности при подключении к API. Тип: `str`. |
| **USE_PROXY_FROM_FILE**       | Флаг, указывающий, использовать ли прокси из файла `bot/config/proxies.txt`. Тип: `bool`. Значения: `True` или `False`. |
| **REF_ID**                    | Реферальный аргумент, используемый в ссылках для отслеживания рефералов. Тип: `str`. Пример: `"bro-228618799"`. |
| **TAPS**                      | Список значений, определяющий количество кликов за один цикл. Тип: `list`. Значения по умолчанию: `[10, 100]`. |
| **SLEEP_BETWEEN_TAPS**       | Список значений, определяющий задержку между кликами. Тип: `list`. Значения по умолчанию: `[1, 3]`. |
| **ENERGY_THRESHOLD**          | Порог энергии, при котором начинаются действия. Тип: `float`. Значение по умолчанию: `0.05`.     |
| **SLEEP_ON_LOW_ENERGY**       | Время ожидания при низком уровне энергии. Тип: `int`. Значение по умолчанию: `60` (в секундах). |
| **SLEEP_AFTER_UPGRADE**      | Время задержки после выполнения апгрейда. Тип: `int`. Значение по умолчанию: `1` (в секунду).   |
| **DELAY_BETWEEN_TASKS**      | Список значений, определяющий задержку между выполнением заданий. Тип: `list`. Значения по умолчанию: `[3, 15]`. |
| **UPGRADE_CHECK_DELAY**      | Задержка между проверками доступности апгрейдов. Тип: `int`. Значение по умолчанию: `5` (в секундах). |
| **RETRY_DELAY**               | Время ожидания перед повторной попыткой в случае ошибки. Тип: `int`. Значение по умолчанию: `3` (в секундах). |
| **MAX_RETRIES**               | Максимальное количество попыток выполнить задачу в случае ошибки. Тип: `int`. Значение по умолчанию: `5`. |

## Быстрый старт 📚
Для быстрой установки и последующего запуска - запустите файл `run.bat` на Windows или `run.sh` на Линукс.

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) **версии 3.10**

## Получение API ключей
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/Mffff4/qlyukerbot.git) клонированием на вашу систему и установкой необходимых зависимостей:

```shell
git clone https://github.com/Mffff4/qlyukerbot.git
cd qlyukerbot
```

Затем для автоматической установки введите:

### Windows
```shell
run.bat
```

### Linux
```shell
run.sh
```

## Linux ручная установка
```shell
sudo sh install.sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH, остальное берется по умолчанию
python3 main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/qlyukerbot >>> python3 main.py --action (1/2/3/4)
# Or
~/qlyukerbot >>> python3 main.py -a (1/2/3/4)

#1. Создать сессию
#2. Создать сессию через QR
#3. Запустить бота
#4. Запустить бота через Telegram (Beta)
```

## Windows ручная установка
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/qlyukerbot >>> python main.py --action (1/2/3/4)
# Или
~/qlyukerbot >>> python main.py -a (1/2/3/4)

#1. Создать сессию
#2. Создать сессию через QR
#3. Запустить бота
#4. Запустить бота через Telegram (Beta)
```

## Отблагодарить  
|                   Токен                   | Адрес кошелька |
|:----------------------------------------------:|:--------------:|
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
