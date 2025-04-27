import pytest
from unittest.mock import patch
from src.utils import time_greeting

# тесты time_greeting
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

