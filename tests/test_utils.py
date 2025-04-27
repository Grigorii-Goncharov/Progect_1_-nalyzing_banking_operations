import pytest
from unittest.mock import patch
from src.utils import time_greeting, get_data_period

# Тесты time_greeting
@pytest.mark.parametrize("hour, expected", [
    (5, "Доброе утро"),
    (11, "Доброе утро"),
    (12, "Добрый день"),
    (17, "Добрый день"),
    (18, "Добрый вечер"),
    (22, "Добрый вечер"),
    (23, "Доброй ночи"),
    (4, "Доброй ночи"),
])
def test_time_greeting(hour, expected):
    with patch('src.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = hour
        assert time_greeting() == expected

# Функции тестирования получения периода даты

@pytest.mark.parametrize("input_date, expected_output", [
    # Проверка обычного случая (май 2020)
    (
        "2020-05-20 15:30:00",
        ["01.05.2020 15:30:00", "20.05.2020 15:30:00"]
    ),
    (
        "2023-01-01 00:00:00",
        ["01.01.2023 00:00:00", "01.01.2023 00:00:00"]
    ),
    (
        "2025-12-31 23:59:59",
        ["01.12.2025 23:59:59", "31.12.2025 23:59:59"]
    ),
])
def test_get_data_period(input_date, expected_output):
    result = get_data_period(input_date)
    assert result == expected_output


def test_get_data_period_invalid_format():
    # Проверка на некорректный формат даты
    with pytest.raises(ValueError):
        get_data_period("20.05.2020")  # Неправильный формат (должен быть "%Y-%m-%d %H:%M:%S")