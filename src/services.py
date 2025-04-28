import json
import logging
import os
from typing import Any

import pandas as pd

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     filename="../logs/services.log",
#     filemode="w",
#     encoding="utf-8",
# )

# Создаем логеры для различных компонентов программы
# logger_services = logging.getLogger("services")

# Получаем путь к текущему скрипту
script_dir = os.path.dirname(os.path.abspath(__file__))

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # Создаем папку logs, если её нет

# Настройка обработчиков
file_handler = logging.FileHandler("logs/services.log", "w", "utf-8")
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


def analyze_cashback(file_path: str, year: int, month: int) -> dict[Any, Any] | str:
    """
    Функция Анализирует выгодность категорий повышенного кешбэка и возвращает JSON-файл с суммами кешбэка по категориям
    """
    logger.info(
        f"Запуск функции spending_by_category с файлом: {file_path}, годом: {year}, месяцем: {month}"
    )

    if not os.path.exists(file_path):
        logger.error(f"Файл {file_path} не найден")
        return {}

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        return {}

    # Преобразование даты в формат datetime
    try:
        df["Дата операции"] = pd.to_datetime(
            df["Дата операции"], format="%d.%m.%Y %H:%M:%S"
        )
        logger.info("Преобразование даты в формат datetime")
    except Exception as e:
        logger.error(f"Ошибка при преобразовании даты: {e}")
        return {}

    # Фильтрация данных по году и месяцу
    filtered_data = df[
        (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)
    ]
    logger.info("Фильтрация данных по году и месяцу")

    if filtered_data.empty:
        logger.warning(f"Нет данных за {month}.{year}")
        return {}

    # Фильтрация расходов (отрицательные значения в "Сумма операции")
    filtered_data = filtered_data[filtered_data["Сумма платежа"] < 0]
    logger.info("Фильтрация расходов")

    # Группировка по категориям и расчёт суммы расходов
    expenses_by_category = filtered_data.groupby("Категория")["Сумма платежа"].sum()

    # Расчёт кешбэка: сумма расходов // 100
    cashback_by_category = (abs(expenses_by_category) // 100).astype(int)
    logger.info("Расчет кэшбэка")

    # Преобразование в словарь
    result = cashback_by_category.to_dict()

    logger.info(f"Анализ завершён. Найдено {len(result)} категорий:")
    return json.dumps(result, ensure_ascii=False, indent=4)
