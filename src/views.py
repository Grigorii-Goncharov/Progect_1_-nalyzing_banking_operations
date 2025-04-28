import json
import logging
import os
from typing import Any, Dict

from config import PATH_TO_EXCEL, PATH_TO_JSON
from src.utils import (get_cards_with_spend, get_currency, get_data_period, get_path_to_file_and_period, get_stock,
                       get_top_transactions, time_greeting)

script_dir = os.path.dirname(os.path.abspath(__file__))

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # Создаем папку logs, если её нет

# Настройка обработчиков
file_handler = logging.FileHandler("logs/views.log", "w", "utf-8")
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


def main_info(datetime_string: str) -> Dict[str, Any]:
    """
    функций и главную функцию, принимающую на вход строку с датой и временем в формате "2025-04-22 18:16:00"
    и возвращающую JSON
    """

    # ПОДГОТОВКА: получаем DataFrame из документа operations.xlsx за определенный интервал
    time_period = get_data_period(datetime_string)
    sorded_df = get_path_to_file_and_period(PATH_TO_EXCEL, time_period)

    # ШАГ 1: Приветствие по времени суток
    logger.info("Начало Работы программы")
    greeting = time_greeting()

    # ШАГ 2: Получение трат по картам за период
    cards = get_cards_with_spend(sorded_df)

    # ШАГ 3: Вывод ТОП 5 транзакций по сумме платежа за период
    top_pay_transactions = get_top_transactions(sorded_df, 5)

    # ШАГ 4: Вывод курса валют
    currensies = get_currency(PATH_TO_JSON)

    # ШАГ 5: Вывод стоимости акций
    stoks = get_stock(PATH_TO_JSON)

    # Пример структуры JSON-ответа
    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_pay_transactions,
        "currency_rates": currensies,
        "stock_prices": stoks,
    }
    logger.info("Выводим json ответ")
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data
