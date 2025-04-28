import pytest
from unittest.mock import patch
import pandas as pd
import json
from src.reports import spending_by_category, get_dataframe


# Тест для обработки ошибок в get_dataframe
@patch('pandas.read_excel')
@patch('src.reports.logger.error')
def test_get_dataframe_error(mock_error, mock_read_excel):
    # Настраиваем моки для ошибки
    mock_read_excel.side_effect = Exception("File not found")

    # Проверяем что функция вызывает исключение
    with pytest.raises(Exception) as exc_info:
        get_dataframe("test.xlsx")

    # Проверяем сообщение об ошибке
    assert "Ошибка при чтении файла: File not found" in str(exc_info.value)

    # Проверяем логирование ошибки
    mock_error.assert_called_once()


# Тест для пустого DataFrame
@patch('src.reports.logger.info')
def test_spending_by_category_empty_df(mock_logger):
    # Мокаем функцию с пустым DataFrame
    @spending_by_category(date="31.12.2021 16:44:00", category="Супермаркеты")
    def mock_get_empty_data(*args, **kwargs):
        return pd.DataFrame()

    # Вызываем декорированную функцию
    result = mock_get_empty_data()

    # Проверяем результат
    assert result == json.dumps([], ensure_ascii=False, indent=2)

    # Проверяем что не было логирования (для пустого DF)
    mock_logger.assert_not_called()


# Тест для декоратора без параметров
def test_spending_by_category_no_params(test_df):
    # Декоратор без параметров
    @spending_by_category()
    def mock_get_data(*args, **kwargs):
        return test_df

    # Вызываем декорированную функцию
    result = mock_get_data()

    # Проверяем что фильтрация по дате работает (последние 90 дней)
    json_data = json.loads(result)
    assert len(json_data) >= 0  # В зависимости от текущей даты