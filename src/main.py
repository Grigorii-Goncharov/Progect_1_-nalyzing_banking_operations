from config import PATH_TO_EXCEL
from reports import get_dataframe
from services import analyze_cashback
from views import main_info

if __name__ == "__main__":
    # Вызов функции main_info из модуля views
    print(main_info("2018-04-22 18:16:00"))

    # Вызов функции analyze_cashback из модуля services
    print(analyze_cashback(PATH_TO_EXCEL, 2018, 5))

    # Вызов функции spending_by_category с декоратором report_decorator из модуля reports
    print(get_dataframe(PATH_TO_EXCEL))
