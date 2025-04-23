import json
from config import PATH_TO_EXCEL

from utils import time_greeting, get_data_period, get_path_to_file_and_period, get_cerds_with_spend
from typing import Dict, Any

def main_info(datetime_string: str) -> Dict[str, Any]:
  '''
    функций и главную функцию, принимающую на вход строку с датой и временем в формате "2025-04-22 18:16:00"
    и возвращающую JSON
  '''

  # ПОДГОТОВКА: получаем DataFrame из документа operations.xlsx за определенный интервал
  time_period = get_data_period(datetime_string)
  sorded_df = get_path_to_file_and_period('../data/operations.xlsx', time_period)

  # ШАГ 1: Приветствие по времени суток
  greeting = time_greeting()

  # ШАГ 2: Получение трат по картам за период
  cards = get_cerds_with_spend(sorded_df)

  # ШАГ 3: Вывод ТОП 5 транзакций по сумме платежа за период
  top_transactions = get_top_transacrions(sorded_df, 5 )
#
# currensies = get_currency(PATH_TO_JSON)

# stoks = get_stoks()

# Пример структуры JSON-ответа
  data = {
    "greeting": greeting,
    "cards": cards,
     "top_transactions": top_transactions,
    # "currency_rates": currensies,
    # "stock_prices": stoks,
  }

  json_data = json.dumps(data, ensure_ascii=False, indent=4)
  return json_data





