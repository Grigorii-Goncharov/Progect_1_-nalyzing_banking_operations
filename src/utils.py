import json
import logging
import os
from datetime import datetime
import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     filename="../logs/utils.log",
#     filemode="w",
#     encoding="utf-8",
# )
#
# # Создаем логеры для различных компонентов программы
# logger = logging.getLogger("utils")

# Получаем путь к текущему скрипту
script_dir = os.path.dirname(os.path.abspath(__file__))

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # Создаем папку logs, если её нет

# Настройка обработчиков
file_handler = logging.FileHandler("logs/utils.log", "w", "utf-8")
file_handler.setLevel(logging.DEBUG)  # Убедимся, что обработчик принимает все уровни

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)

console_formatter = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)

# Добавляем обработчики к логгеру
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


URL = "https://api.apilayer.com/exchangerates_data/convert"
URL_2 = "https://api.twelvedata.com/price"

# Загрузка переменных из .env-файла
load_dotenv()

# Получаем API-ключ из переменных окружения
API_KEY = os.getenv("API_KEY")  # В .env есть строка API_KEY=ваш_ключ
headers = {"apikey": API_KEY}

API_KEY_2 = os.getenv("API_KEY_2")  # В .env есть строка API_KEY_2=ваш_ключ


def time_greeting():
    """
    1. Функция для страницы «Главная» принимает на вход строку с датой и временем в формате  YYYY-MM-DD HH:MM:SS
    и возвращает в зависимости от времени суток приветствие: Доброе утро / Добрый день / Добрый вечер / Доброй ночи
    """

    user_time = datetime.now().hour

    if 5 <= user_time < 12:
        greet = "Доброе утро"
    elif 12 <= user_time < 18:
        greet = "Добрый день"
    elif 18 <= user_time < 23:
        greet = "Добрый вечер"
    else:
        greet = "Доброй ночи"

    logger.info(
        "Работа функции time_greeting: Вывод приветствия в зависимости от времени суток... ОК"
    )
    return greet


def get_data_period(datetime_string: str, data_format="%Y-%m-%d %H:%M:%S") -> list[str]:
    """
    2. Функция получения периода даты. Если дата на вход подана дата: 20.05.2020,то данные для анализа
    будут в диапазоне 01.05.2020 - 20.05.2020.
    Дополнительно: преобразование даты из "%Y-%m-%d %H:%M:%S" в "%d.%m.%Y %H:%M:%S" (согласно формату даты в Excel)
    """

    today_day_by_period = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
    first_day_by_period = today_day_by_period.replace(day=1)

    logger.info(
        "Работа функции get_data_period: Расчет периода по дате от сегодняшней даты... ОК"
    )
    return [
        first_day_by_period.strftime("%d.%m.%Y %H:%M:%S"),
        today_day_by_period.strftime("%d.%m.%Y %H:%M:%S"),
    ]


def get_path_to_file_and_period(path_to_file: str, time_period: list) -> DataFrame:
    """
    3. Функция принимает путь к Excel файлу и полученный период из ф-ии get_data_period
    и осуществляет возврат таблицы в заданном периоде
    """
    # Читаем данные построчно
    df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям")

    # Преобразуем строки колонки "Дата операции" в формат даты
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

    # Задаём начальный день периода (индекс 0 из списка периода и приводим к формату "%d.%m.%Y %H:%M:%S)
    start_date = datetime.strptime(time_period[0], "%d.%m.%Y %H:%M:%S")
    # Задаём конечный день периода  (индекс 1 из списка периода и приводим к формату "%d.%m.%Y %H:%M:%S)
    end_date = datetime.strptime(time_period[1], "%d.%m.%Y %H:%M:%S")

    # фильтруем ип получаем данные в filtered_df по колонке "Дата операции" с 1-ого по крайний день
    filtered_df = df[
        (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    ]
    # Сортируем полученные данные из filtered_df по возрастанию
    sorted_df = filtered_df.sort_values(by="Дата операции", ascending=True)

    logger.info(
        "Работа функции get_path_to_file_and_period: "
        "Сортируем полученные данные из filtered_df по возрастанию... ОК"
    )
    return sorted_df


def get_cards_with_spend(sorded_df: DataFrame) -> list[dict]:
    """
    4. Функция принимает DataFrame и возвращает список карт с расходами
    """
    card_expenses_transactions = [] # type: ignore

    # Проверка на пустой DataFrame
    if sorded_df.empty:
        logger.info("Получен пустой DataFrame, возвращаю пустой список")
        return card_expenses_transactions

    try:
        card_sorted = sorded_df[
            [
                "Номер карты",
                "Сумма операции",
                "Кэшбэк",
                "Сумма операции с округлением",
            ]
        ]
    except KeyError as e:
        logger.error(f"Отсутствуют необходимые колонки: {e}")
        return card_expenses_transactions

    for index, row in card_sorted.iterrows():
        if row["Сумма операции"] < 0:
            last_digits = str(row["Номер карты"]).replace("*", "")
            total_spent = row["Сумма операции с округлением"]
            cashback = float(total_spent) // 100
            row = {
                "last_digits": last_digits,
                "total_spent": total_spent,
                "cashback": cashback,
            }
            card_expenses_transactions.append(row)

    logger.info(
        "Работа функции get_cards_with_spend: Подготавливаю список карт с расходами... ОК"
    )
    return card_expenses_transactions


def get_top_transactions(sorted_df: DataFrame, get_top: int) -> DataFrame:
    """
    5. Функция принимает DataFrame и возвращает get_top топ-транзакций по сумме платежа
    """
    top_pay_transactions = []
    sorted_pay_df = sorted_df.sort_values(by="Сумма операции", ascending=False)
    top_transactions = sorted_pay_df.head(get_top)
    top_transactions_sorted = top_transactions[
        ["Дата платежа", "Сумма операции", "Категория", "Описание"]
    ]

    for i, row in top_transactions_sorted.iterrows():
        transaction = {
            "date": f'{row["Дата платежа"]}',
            "amount": f'{row["Сумма операции"]}',
            "category": f'{row["Категория"]}',
            "description": f'{row["Описание"]}',
        }
        top_pay_transactions.append(transaction)

    logger.info(
        "Работа функции get_top_transactions: Осуществляю вывод топ-транзакций по сумме платежа... ОК"
    )
    return top_pay_transactions


def get_currency(path_to_json: str) -> list[dict]:
    """
    7. Функция принимает на вход path_to_json и вjзвращает курс валют
    """
    logger.debug(
        f"Вызвана функция get_currency с параметром: path_to_json={path_to_json}"
    )

    currency_rates = []

    try:
        # Чтение JSON-файла
        with open(path_to_json, "r", encoding="utf-8") as file:
            data = json.load(file)
        logger.debug(f"Файл {path_to_json} успешно прочитан")

        # Проверка наличия ключа "user_currencies"
        if "user_currencies" not in data:
            logger.warning("Ключ 'user_currencies' отсутствует в JSON")
            raise KeyError("Ключ 'user_currencies' отсутствует в JSON")

        # Обработка валют
        for currency in data["user_currencies"]:
            try:
                logger.debug(f"Обработка валюты: {currency}")
                # Сетевой запрос
                params = {"amount": 1, "from": currency, "to": "RUB"}
                headers = {"apikey": API_KEY}
                # отправляем по HTTP GET-запрос к указанному URL с заданными параметрами -params и заголовками headers
                response = requests.get(URL, headers=headers, params=params, timeout=10)

                # Проверка статуса ответа. Выбросит HTTPError при статусе 4xx/5xx
                response.raise_for_status()

                result = response.json()
                logger.debug(f"Результат запроса API: {result}")

                # Проверка структуры ответа
                if "query" not in result or "result" not in result:
                    logger.warning("Некорректная структура ответа API")
                    raise ValueError("Некорректная структура ответа API")

                currency_code = result["query"]["from"]
                currency_amount = round(result["result"], 2)
                currency_rates.append(
                    {"currency": currency_code, "rate": currency_amount}
                )
                logger.debug(f"Курс валюты {currency_code}: {currency_amount}")

            except requests.exceptions.RequestException as e:
                logger.exception(f"Ошибка при обработке валюты {currency}: {e}")
                continue

    except FileNotFoundError:
        logger.error(f"Файл {path_to_json} не найден")
        return []
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле {path_to_json}")
        return []
    except KeyError as e:
        logger.error(f"Ошибка в структуре JSON: {e}")
        return []
    except Exception as e:
        logger.exception(f"Неизвестная ошибка: {e}")
        return []
    logger.debug(f"Возвращаемые курсы валют: {currency_rates} ... OK")
    return currency_rates


def get_stock(path_to_json: str) -> list[dict]:
    """7. Функция принимает на вход path_to_json и возвращает курс Акций"""
    logger.debug(f"Вызвана функция get_stock с параметром: path_to_json={path_to_json}")
    stock_rates = []

    try:
        # Чтение файла
        with open(path_to_json, "r", encoding="utf-8") as file:
            data = json.load(file)
            logger.debug(f"Файл {path_to_json} успешно прочитан")

        # Проверка наличия ключа
        if "user_stocks" not in data:
            logger.warning("Ключ 'user_stocks' отсутствует в JSON")
            return []

        # Обработка акций
        for symbol in data["user_stocks"]:
            try:
                logger.debug(f"Обработка акции: {symbol}")
                params = {"symbol": symbol, "apikey": API_KEY_2}
                # отправляем по HTTP GET-запрос к указанному URL с заданными параметрами params и заголовками headers
                response = requests.get(URL_2, params=params, timeout=10)
                response.raise_for_status()
                stock_data = response.json()
                logger.debug(f"Результат запроса API: {stock_data}")

                if "price" not in stock_data:
                    logger.warning(
                        f"Ключ 'price' отсутствует в ответе API для акции {symbol}"
                    )
                    continue

                try:
                    price = float(stock_data["price"])
                    stock_rates.append({"stock": symbol, "price": price})
                    logger.debug(f"Цена акции {symbol}: {price}")
                except ValueError as e:
                    logger.warning(
                        f"Невозможно преобразовать цену для акции {symbol}: {e}"
                    )
                    continue

            except requests.exceptions.RequestException as e:
                logger.warning(f"Ошибка при обработке акции {symbol}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Неизвестная ошибка при обработке акции {symbol}: {e}")
                continue

    except FileNotFoundError:
        logger.error(f"Файл {path_to_json} не найден")
        return []
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле {path_to_json}")
        return []
    except Exception as e:
        logger.exception(f"Неизвестная ошибка: {e}")
        return []

    logger.debug(f"Возвращаемые данные об акциях: {stock_rates}")
    return stock_rates
