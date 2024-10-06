[![Static Badge](https://img.shields.io/badge/Телеграм-Ссылка_на_бота-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/qlyukerbot/start?startapp=bro-228618799)

## Рекомендация перед использованием

# 🔥🔥 Используйте PYTHON версии 3.10 🔥🔥

> 🇪🇳 README in english available [here](README-EN.md)

## Функционал  
|                   Функционал                   | Поддерживается |
|:----------------------------------------------:|:--------------:|
|                Многопоточность                 |       ✅        | 
|            Привязка прокси к сессии            |       ✅        | 
| Авто-регистрация аккаунта по вашей реф. ссылке |       ✅        |
|     Автоматическое улучшение бустеров          |       ✅        |
|          Поддержка pyrogram .session           |       ✅        |
|          Создание сессий через QR код          |       ✅        |


## [Настройки](https://github.com/Mffff4/qlyukerbot/blob/main/.env-example/)
|          Настройки          |                                      Описание                                       |
|:---------------------------:|:-----------------------------------------------------------------------------------:|
|    **API_ID / API_HASH**    | Данные платформы, с которой будет запущена сессия Telegram (по умолчанию - android) |
|       **MIN_TAPS / MAX_TAPS**        |            Количество кликов за один цикл (по умолчанию от 10 до 100)            |
|         **MIN_SLEEP_BETWEEN_TAPS**          |      Минимальная задержка между кликами (по умолчанию - 1 секунда)       |
| **MAX_SLEEP_BETWEEN_TAPS** |                                 Максимальная задержка между кликами (по умолчанию - 3 секунды)                                 |
|   **ENERGY_THRESHOLD**   |            Порог энергии для выполнения действий (по умолчанию - 0.05)            |
|         **REF_ID**          |       Ваш реферальный аргумент (идет после app/startapp? в вашей реф. ссылке)       |
|         **SLEEP_ON_LOW_ENERGY**          |       Время ожидания при низком уровне энергии (по умолчанию - 15 минут)       |
|         **SLEEP_AFTER_UPGRADE**          |       Время задержки после апгрейда (по умолчанию - 1 секунда)       |
|         **SLEEP_AFTER_TAPS**          |       Время задержки после выполнения всех кликов (по умолчанию - 0 секунд)       |
|   **USE_PROXY_FROM_FILE**   |       Использовать ли прокси из файла `bot/config/proxies.txt` (True / False)       |

## Быстрый старт 📚

Для быстрой установки и последующего запуска - запустите файл run.bat на Windows или run.sh на Линукс

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

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux ручная установка
```shell
sudo sh install.sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
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


# Windows ручная установка
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

