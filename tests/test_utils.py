import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.utils import (get_cards_with_spend, get_currency, get_data_period, get_path_to_file_and_period, get_stock,
                       get_top_transactions, time_greeting)


# Тесты time_greeting
@pytest.mark.parametrize(
    "hour, expected",
    [
        (5, "Доброе утро"),
        (6, "Доброе утро"),
        (12, "Добрый день"),
        (17, "Добрый день"),
        (18, "Добрый вечер"),
        (22, "Добрый вечер"),
        (23, "Доброй ночи"),
        (4, "Доброй ночи"),
    ],
)
def test_time_greeting(hour, expected):
    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value.hour = hour
        assert time_greeting() == expected


@pytest.fixture
def test_period():
    """Фикстура с тестовым периодом дат"""
    return ["01.01.2023 00:00:00", "31.01.2023 23:59:59"]


@pytest.fixture
def mock_currency_data():
    """Фикстура с мок-данными для теста валют"""
    return '{"user_currencies": ["USD", "EUR"]}'


@pytest.fixture
def mock_stock_data():
    """Фикстура с мок-данными для теста акций"""
    return '{"user_stocks": ["AAPL"]}'


@pytest.fixture
def test_df():
    """Фикстура с тестовыми данными DataFrame"""
    return pd.DataFrame(
        {
            "Дата операции": ["01.01.2023 12:00:00", "15.01.2023 12:00:00"],
            "Номер карты": ["1234****5678", "8765****4321"],
            "Сумма операции": [-100, 200],
            "Кэшбэк": [1, 0],
            "Сумма операции с округлением": [-100, 200],
            "Категория": ["Магазин", "Ресторан"],
            "Описание": ["Покупка +79123456789", "Обед"],
            "Дата платежа": ["02.01.2023", "16.01.2023"],
            "Статус": ["OK", "OK"],
            "Валюта операции": ["RUB", "RUB"],
            "Валюта платежа": ["RUB", "RUB"],
            "Сумма платежа": [-100, 200],  # Добавляем недостающую колонку
        }
    )


@pytest.fixture
def test_spending_df():
    data = {
        "Дата операции": ["31.12.2021 16:44:00", "15.01.2022 12:00:00"],
        "Категория": ["Супермаркеты", "Рестораны"],
        "Сумма операции": [1000, 2000],
        "Описание": ["Покупки в магазине", "Обед в кафе"],
    }
    return pd.DataFrame(data)


# Тестирование функции получения периода даты
@pytest.mark.parametrize(
    "input_date, expected_output",
    [
        ("2021-05-20 15:30:00", ["01.05.2021 15:30:00", "20.05.2021 15:30:00"]),
        ("2022-01-01 00:00:00", ["01.01.2022 00:00:00", "01.01.2022 00:00:00"]),
        ("2023-12-31 23:59:59", ["01.12.2023 23:59:59", "31.12.2023 23:59:59"]),
    ],
)
def test_get_data_period(input_date, expected_output):
    result = get_data_period(input_date)
    assert result == expected_output


def test_get_data_period_invalid_format():
    # Проверка на некорректный формат даты
    with pytest.raises(ValueError):
        get_data_period(
            "20.05.2020"
        )  # Неправильный формат (должен быть "%Y-%m-%d %H:%M:%S")


@patch("pandas.read_excel")  # Тест обработки на возврат тестового фрейма данных
def test_get_path_to_file_and_period(mock_read_excel, test_df, test_period):
    # Setup the mock to return your test dataframe
    mock_read_excel.return_value = test_df
    result = get_path_to_file_and_period("test.xlsx", test_period)
    assert len(result) == 2
    assert result.iloc[0]["Номер карты"] == "1234****5678"


def test_get_path_to_file_and_period_invalid_path(test_period):
    """Тест с несуществующим файлом"""
    with pytest.raises(FileNotFoundError):
        get_path_to_file_and_period("nonexistent.xlsx", test_period)


def test_get_path_to_file_and_period_wrong_sheet(tmp_path, test_period):
    """Тест с неверным именем листа"""
    df = pd.DataFrame({"Дата операции": ["01.01.2023"]})
    wrong_sheet_file = tmp_path / "wrong_sheet.xlsx"
    df.to_excel(wrong_sheet_file, sheet_name="WrongSheet")
    with pytest.raises(ValueError):
        get_path_to_file_and_period(wrong_sheet_file, test_period)


def test_get_cards_with_spend(
    test_df,
):  # Тест обработки DataFrame и возвращения списка карт с расходами
    test_df["Дата операции"] = pd.to_datetime(test_df["Дата операции"], dayfirst=True)
    result = get_cards_with_spend(test_df)
    assert len(result) == 1
    assert result[0]["last_digits"] == "12345678"


def test_get_cards_with_spend_empty_df():
    """Тест с пустым DataFrame"""
    empty_df = pd.DataFrame()
    result = get_cards_with_spend(empty_df)
    assert result == []


def test_get_cards_with_spend_missing_columns():
    """Тест с DataFrame, в котором отсутствуют необходимые колонки"""
    df = pd.DataFrame({"Другая колонка": [1, 2, 3]})
    result = get_cards_with_spend(df)
    assert result == []


def test_get_cards_with_spend_no_negative_transactions():
    """Тест с DataFrame без отрицательных операций"""
    df = pd.DataFrame(
        {
            "Номер карты": ["1234****5678", "4321****8765"],
            "Сумма операции": [100, 200],
            "Кэшбэк": [1, 2],
            "Сумма операции с округлением": [100, 200],
        }
    )
    result = get_cards_with_spend(df)
    assert result == []


def test_get_cards_with_spend_column_case_sensitivity():
    """Тест с разным регистром в названиях колонок"""
    df = pd.DataFrame(
        {
            "НОМЕР КАРТЫ": ["1234****5678"],
            "Сумма Операции": [-100],
            "кэшбэк": [1],
            "Сумма операции с округлением": [-100],
        }
    )
    result = get_cards_with_spend(df)
    assert result == []


def test_get_cards_with_spend_no_negative():
    """Тест без отрицательных сумм операций"""
    df = pd.DataFrame(
        {
            "Номер карты": ["1234****5678"],
            "Сумма операции": [100],
            "Кэшбэк": [0],
            "Сумма операции с округлением": [100],
        }
    )
    result = get_cards_with_spend(df)
    assert result == []


def test_get_cards_with_spend_multiple_cards():
    """Тест с несколькими картами"""
    df = pd.DataFrame(
        {
            "Номер карты": ["1234****5678", "8765****4321", "9999****0000"],
            "Сумма операции": [-100, -200, 300],
            "Кэшбэк": [1, 2, 0],
            "Сумма операции с округлением": [-100, -200, 300],
        }
    )
    result = get_cards_with_spend(df)
    assert len(result) == 2
    assert result[0]["last_digits"] == "12345678"
    assert result[1]["last_digits"] == "87654321"


def test_get_top_transactions(
    test_df,
):  # Тест обработки DataFrame и возвращения списка ТОП 5 транзакций
    test_df["Дата операции"] = pd.to_datetime(test_df["Дата операции"], dayfirst=True)
    result = get_top_transactions(test_df, 1)
    assert len(result) == 1
    assert float(result[0]["amount"]) == 200


def test_get_top_transactions_more_than_exists(test_df):
    """Тест с запросом большего количества транзакций, чем есть"""
    result = get_top_transactions(test_df, 10)
    assert len(result) == 2  # В тестовых данных только 2 транзакции


def test_get_top_transactions_zero_top(test_df):
    """Тест с запросом 0 топ-транзакций"""
    result = get_top_transactions(test_df, 0)
    assert result == []


@patch("requests.get")
def test_get_currency_invalid_response(mock_get, tmp_path):
    """Тест с некорректным ответом API"""
    json_data = {"user_currencies": ["USD"]}
    json_file = tmp_path / "test.json"
    json_file.write_text(json.dumps(json_data), encoding="utf-8")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"wrong": "structure"}
    mock_get.return_value = mock_response
    result = get_currency(str(json_file))
    assert result == []


@patch("requests.get")
def test_get_currency_non_200_status(mock_get, tmp_path):
    """Тест с кодом ответа != 200"""
    json_data = {"user_currencies": ["USD"]}
    json_file = tmp_path / "test.json"
    json_file.write_text(json.dumps(json_data), encoding="utf-8")

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = get_currency(str(json_file))
    assert result == []


@patch("requests.get")  # Тест для получения стоимости акций
def test_get_stock_invalid_price_format(mock_get, tmp_path):
    """Тест с некорректным форматом цены"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"price": "not_a_number"}
    mock_get.return_value = mock_response

    config = {"user_stocks": ["AAPL"]}
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    result = get_stock(config_path)
    assert result == []


@patch("requests.get")
def test_get_stock_empty_stocks_list(mock_get, tmp_path):
    """Тест с пустым списком акций"""
    config = {"user_stocks": []}
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    result = get_stock(config_path)
    assert result == []


@patch("requests.get")
def test_get_stock_multiple_stocks(mock_get, tmp_path):
    """Тест с несколькими акциями"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"price": "150.0"}
    mock_get.return_value = mock_response
    config = {"user_stocks": ["AAPL", "GOOGL", "MSFT"]}
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    result = get_stock(config_path)
    assert len(result) == 3
    assert all(isinstance(item["price"], float) for item in result)
