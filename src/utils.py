from datetime import datetime


def time_greeting(datetime_string):
    '''
        Функция для страницы «Главная» принимает на вход строку с датой и временем в формате  YYYY-MM-DD HH:MM:SS
        и возвращает в зависимости от времени суток приветствие: Доброе утро / Добрый день / Добрый вечер / Доброй ночи
    '''

    user_time = datetime.now().hour

    if 5 <= user_time < 12:
        return "Доброе утро"
    elif 12 <= user_time < 18:
        return "Добрый день"
    elif 18 <= user_time < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_data_period(datetime_string: str, data_format = "%Y-%m-%d %H:%M:%S") -> list[str]:
    '''
        Функция получения периода даты. Если дата на вход подана дата: 20.05.2020,то данные для анализа
        будут в диапазоне 01.05.2020 - 20.05.2020.я
        Дополнительно: преобразование даты из "%Y-%m-%d %H:%M:%S" в "%d.%m.%Y %H:%M:%S" (согласно формату даты в Excel)
    '''

    dt = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
    start = dt.replace(day=1)

    return [start.strftime("%d.%m.%Y %H:%M:%S"), dt.strftime("%d.%m.%Y %H:%M:%S") ]


datetime_string = "2025-04-23 18:16:00"  # Строка для теста Функции
print(time_greeting(datetime_string))  # Проверка работы функции приветствия относительно текущего времени пользователя
print(get_data_period(datetime_string))  # Проверка работы Функции получения периода даты