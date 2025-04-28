import pytest
import pandas as pd
import json
from unittest.mock import patch
from src.services import analyze_cashback


# Фикстура для создания временного Excel файла
@pytest.fixture
def create_temp_excel_file(tmp_path):
    def _create_temp_excel_file(data, filename):
        file_path = tmp_path / filename
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        return str(file_path)

    return _create_temp_excel_file


# Тестовые данные
correct_test_data = [
    {
        "Дата операции": "01.01.2023 12:00:00",
        "Категория": "Супермаркеты",
        "Сумма платежа": -1500
    },
    {
        "Дата операции": "15.01.2023 12:00:00",
        "Категория": "Фастфуд",
        "Сумма платежа": -1000
    },
    {
        "Дата операции": "20.01.2023 12:00:00",
        "Категория": "Супермаркеты",
        "Сумма платежа": -500
    }
]

test_data_with_income = [
    {
        "Дата операции": "01.01.2023 12:00:00",
        "Категория": "Супермаркеты",
        "Сумма платежа": -1500
    },
    {
        "Дата операции": "15.01.2023 12:00:00",
        "Категория": "Зарплата",
        "Сумма платежа": 50000
    }
]

test_data_wrong_format = [
    {
        "Дата операции": "2023-01-01",
        "Категория": "Супермаркеты",
        "Сумма платежа": -1500
    }
]


def test_analyze_cashback_success(create_temp_excel_file):
    """Тест успешного выполнения функции"""
    file_path = create_temp_excel_file(correct_test_data, "test_data.xlsx")
    result = analyze_cashback(file_path, 2023, 1)

    expected_result = {
        "Супермаркеты": 20,
        "Фастфуд": 10
    }

    assert json.loads(result) == expected_result


def test_analyze_cashback_no_data_for_period(create_temp_excel_file):
    """Тест случая, когда нет данных за указанный период"""
    file_path = create_temp_excel_file(correct_test_data, "test_data.xlsx")
    result = analyze_cashback(file_path, 2024, 1)
    assert result == {}


def test_analyze_cashback_file_not_found():
    """Тест случая, когда файл не существует"""
    result = analyze_cashback("nonexistent_file.xlsx", 2023, 1)
    assert result == {}


def test_analyze_cashback_with_income(create_temp_excel_file):
    """Тест фильтрации доходов (положительных сумм)"""
    file_path = create_temp_excel_file(test_data_with_income, "test_data.xlsx")
    result = analyze_cashback(file_path, 2023, 1)

    expected_result = {
        "Супермаркеты": 15
    }

    assert json.loads(result) == expected_result


def test_analyze_cashback_wrong_date_format(create_temp_excel_file):
    """Тест обработки неверного формата даты"""
    file_path = create_temp_excel_file(test_data_wrong_format, "test_data.xlsx")
    result = analyze_cashback(file_path, 2023, 1)
    assert result == {}


def test_analyze_cashback_empty_file(create_temp_excel_file):
    """Тест обработки пустого файла"""
    file_path = create_temp_excel_file([], "empty.xlsx")
    result = analyze_cashback(file_path, 2023, 1)
    assert result == {}