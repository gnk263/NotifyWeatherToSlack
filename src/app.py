import json
import locale
import os
import requests
from datetime import datetime, timezone, timedelta

LATITUDE = os.environ['LATITUDE']
LONGITUDE = os.environ['LONGITUDE']
API_KEY = os.environ['API_KEY']
SLACk_URL = os.environ['SLACK_URL']

def lambda_handler(event, context):
    main()

def main():
    # 曜日表記を日本語にする
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

    # 気象情報を取得する
    weather_endpoint = get_weather_endpoint(LATITUDE, LONGITUDE, API_KEY)
    weather_data = get_weather_data(weather_endpoint)

    # Slack通知用のメッセージを作成する
    message = create_message(weather_data)
    print(json.dumps(message))

    # Slackに通知する
    # post_slack(message)

def get_weather_endpoint(latitude, longitude, api_key):
    base_url = 'https://api.openweathermap.org/data/2.5/onecall'
    return f'{base_url}?lat={latitude}&lon={longitude}&exclude=current&units=metric&lang=ja&appid={api_key}'

def get_weather_data(endpoint):
    res = requests.get(endpoint)
    return res.json()

def convert_unixtime_to_jst_datetime(unixtime):
    return datetime.fromtimestamp(unixtime, timezone(timedelta(hours=9)))

def get_icon_url(icon_name):
    return f'http://openweathermap.org/img/wn/{icon_name}@2x.png'

def create_message(weather_data):
    hourly = create_message_blocks_hourly(weather_data)
    daily = create_message_blocks_daily(weather_data)

    message_blocks = []
    message_blocks += hourly
    message_blocks.append({
        'type': 'divider'
    })
    message_blocks += daily
    return {
        'blocks': message_blocks
    }

def create_message_blocks_hourly(weather_data):
    message_blocks = []
    hourly = weather_data['hourly']

    # 見出しを作る
    first_datetime = convert_unixtime_to_jst_datetime(hourly[0]['dt'])
    message_blocks.append({
        'type': 'section',
        'text': {
            'type': 'plain_text',
            'text': first_datetime.strftime('%m/%d(%a)')
        }
    })

    # 1時間毎のメッセージを作る(12時間分)
    for i in range(12):
        item = hourly[i]
        target_datetime = convert_unixtime_to_jst_datetime(item['dt'])
        description = item['weather'][0]['description']
        icon_url = get_icon_url(item['weather'][0]['icon'])
        rain = item.get('rain', {'1h': 0}).get('1h')    # rainが無い場合は0mm/hとする
        temperature = item['temp']
        humidity = item['humidity']
        pressure = item['pressure']
        wind_speed = item['wind_speed']

        message_blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': target_datetime.strftime('%H:%M')
                },
                {
                    'type': 'image',
                    'image_url': icon_url,
                    'alt_text': description
                },
                {
                    'type': 'mrkdwn',
                    'text': f'{description:　<6}　{rain:>4.1f}mm/h　{temperature:>4.1f}℃　'
                            f'{humidity}％　{pressure:>4}hPa　{wind_speed:>4.1f}m/s'
                }
            ]
        })
    return message_blocks

def create_message_blocks_daily(weather_data):
    message_blocks = []
    daily = weather_data['daily']

    # 見出しを作る
    message_blocks.append({
        'type': 'section',
        'text': {
            'type': 'plain_text',
            'text': '週間天気'
        }
    })

    # 1日毎のメッセージを作る
    for item in daily:
        target_datetime = convert_unixtime_to_jst_datetime(item['dt'])
        description = item['weather'][0]['description']
        icon_url = get_icon_url(item['weather'][0]['icon'])
        rain = item.get('rain', 0)  # rainが無い場合は0mm/hとする
        temperature_min = item['temp']['min']
        temperature_max = item['temp']['max']
        humidity = item['humidity']
        pressure = item['pressure']
        wind_speed = item['wind_speed']

        message_blocks.append({
            'type': 'context',
            'elements': [
                {
                    'type': 'mrkdwn',
                    'text': target_datetime.strftime('%m/%d(%a)')
                },
                {
                    'type': 'image',
                    'image_url': icon_url,
                    'alt_text': description
                },
                {
                    'type': 'mrkdwn',
                    'text': f'{description:　<6}　{rain:>4.1f}mm/h　{temperature_min:>4.1f} - {temperature_max:>4.1f}℃　'
                            f'{humidity}％　{pressure:>4}hPa　{wind_speed:>4.1f}m/s'
                }
            ]
        })
    return message_blocks

def post_slack(payload):
    url = f'https://{SLACk_URL}'
    try:
        response = requests.post(url, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        print(response.status_code)
