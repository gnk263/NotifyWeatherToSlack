import json

import pytest

from src import app

def test_lambda_handler():
    pass

@pytest.mark.parametrize(
    'latitude, longitude, api_key, expected', [
        (
            '123.456789', '76.54321', 'xxxyyyzzz',
            'https://api.openweathermap.org/data/2.5/onecall?lat=123.456789&lon=76.54321&exclude=current&units=metric&lang=ja&appid=xxxyyyzzz'
        ),
    ])
def test_get_weather_endpoint(latitude, longitude, api_key, expected):
    actual = app.get_weather_endpoint(latitude, longitude, api_key)
    assert expected == actual
