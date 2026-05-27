import os

from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
MAX_HISTORY = 5
recent_searches = []


def add_recent_city(city: str) -> None:
    if city in recent_searches:
        recent_searches.remove(city)
    recent_searches.insert(0, city)
    if len(recent_searches) > MAX_HISTORY:
        recent_searches.pop()


def get_weather(city: str, units: str = "metric") -> dict:
    if not API_KEY:
        return {"error": "缺少环境变量 OPENWEATHER_API_KEY。请先设置 API Key。"}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units,
        "lang": "zh_cn",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("message", "无法获取天气数据。")}

        weather = data["weather"][0]
        return {
            "city": f"{data['name']}, {data['sys'].get('country', '')}",
            "temperature": round(data["main"]["temp"]),
            "description": weather["description"].capitalize(),
            "icon_url": f"https://openweathermap.org/img/wn/{weather['icon']}@2x.png",
            "humidity": data["main"].get("humidity"),
            "wind_speed": round(data["wind"].get("speed", 0), 1),
            "wind_unit": "m/s" if units == "metric" else "mph",
            "temp_unit": "°C" if units == "metric" else "°F",
        }

    except requests.RequestException as error:
        return {"error": f"请求天气服务失败：{error}"}


@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    error = None
    city = None
    units = "metric"

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        units = request.form.get("units", "metric")
        if not city:
            error = "请输入城市名称。"
        else:
            weather = get_weather(city, units)
            if "error" in weather:
                error = weather["error"]
                weather = None
            else:
                add_recent_city(weather["city"])

    return render_template(
        "index.html",
        city=city,
        weather=weather,
        error=error,
        units=units,
        recent_searches=recent_searches,
    )





if __name__ == "__main__":
    app.run(debug=True)
