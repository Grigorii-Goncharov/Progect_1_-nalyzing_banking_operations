import json
from pkgutil import get_data
from typing import AnyStr

from utils import time_greeting
from typing import Dict, Any

def main_info(datetime_string: str) -> Dict[str, Any]:
  '''
  функций и главную функцию, принимающую на вход строку с датой и временем в формате "2025-04-22 18:16:00"
  и возвращающую JSON
  '''

  greeting = time_greeting()
  time_period = get_data_time(datetime_string)
# cards = get_cerds_with_spent()
#
# top_transactions = get_top_transacrions(PATH_TO_EXCEL)
#
# currensies = get_currency(PATH_TO_JSON)

# stoks = get_stoks()

# Пример структуры JSON-ответа
  data = {
    "greeting": greeting
    # ,"cards": cards,
    # "top_transactions": top_transactions,
    # "currency_rates": currensies,
    # "stock_prices": stoks,
  }

  json_data = json.dumps(data, ensure_ascii=False, indent=4)
  return json_data





