import json
from typing import Dict, Any
from utils import time_greeting, get_data_period, get_path_to_file_and_period, get_cards_with_spend, get_top_transactions, get_currency, get_stock
from config import PATH_TO_EXCEL, PATH_TO_JSON

def main_info(datetime_string: str) -> Dict[str, Any]:
  '''
    функций и главную функцию, принимающую на вход строку с датой и временем в формате "2025-04-22 18:16:00"
    и возвращающую JSON
  '''

  # ПОДГОТОВКА: получаем DataFrame из документа operations.xlsx за определенный интервал
  time_period = get_data_period(datetime_string)
  sorded_df = get_path_to_file_and_period(PATH_TO_EXCEL, time_period)

  # ШАГ 1: Приветствие по времени суток
  greeting = time_greeting()

  # ШАГ 2: Получение трат по картам за период
  cards = get_cards_with_spend(sorded_df)

  # ШАГ 3: Вывод ТОП 5 транзакций по сумме платежа за период
  top_pay_transactions = get_top_transactions(sorded_df, 5 )

  # ШАГ 4: Вывод курса валют
  # currensies = get_currency(PATH_TO_JSON)

  # ШАГ 5: Вывод курса валют
  stoks = get_stock(PATH_TO_JSON)

# Пример структуры JSON-ответа
  data = {
    "greeting": greeting,
    "cards": cards,
    "top_transactions": top_pay_transactions,
    #currency_rates": currensies,
    #"stock_prices": stoks
  }

  json_data = json.dumps(data, ensure_ascii=False, indent=4)
  return json_data