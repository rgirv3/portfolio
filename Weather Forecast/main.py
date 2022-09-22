import http.client
import json
import urllib
from requests import get

data = get('https://api.weather.gov/gridpoints/OKX/25,38/forecast').text
weather_json = json.loads(data)


def send_push(title, message_to_send):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": "",
        "user": "",
        "title": title,
        "message": message_to_send,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()


def title():
    weather = weather_json['properties']['periods'][1]['shortForecast']
    day = weather_json['properties']['periods'][1]['name']
    title = f"{weather} {day}!"
    return title


def tomorrow_forecast():
    notification = weather_json['properties']['periods'][1]['detailedForecast']
    return notification


send_push(title(), tomorrow_forecast())
