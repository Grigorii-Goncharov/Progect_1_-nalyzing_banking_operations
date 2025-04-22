import datetime


def time_greeting(datetime_string):
    '''
    Функция для страницы «Главная» принимает на вход строку с датой и временем в формате  YYYY-MM-DD HH:MM:SS
    и возвращает в зависимости от времени суток приветствие:
    Доброе утро / Добрый день / Добрый вечер / Доброй ночи
    '''

    # Определяем приветствие в зависимости от времени суток
    dt = datetime.datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
    hour = dt.hour

    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"
