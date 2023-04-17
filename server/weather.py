import time
import pytz
import math
import requests
from datetime import datetime

from requests.api import head


class WeatherClient:
    def __init__(self, latitude, longitude, timezone=None):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.timezone = timezone

    def load(self, api_key):
        self.data = requests.get(
            f"https://api.openweathermap.org/data/2.5/onecall?lat={self.latitude}&lon={self.longitude}&exclude=minutely&units=metric&appid={api_key}"
        ).json()
        self.current_time = self.data["current"]["dt"]


    def temp_current(self):
        return self.data["current"]["temp"]

    def uvi_max_24hr(self):
        return max(
            hour["uvi"]
            for hour in self.data["hourly"]
            if hour["dt"] - self.current_time < 86400
        )

    def uvi_current(self):
        return self.data["current"]["uvi"]

    def pressure_current(self):
        return self.data["current"]["pressure"]

    def humidity_current(self):
        return self.data["current"]["humidity"]
    
    def wind_speed_current(self):
        return self.data["current"]["wind_speed"]

    def sunrise(self):
        return datetime.utcfromtimestamp(self.data["current"]["sunrise"]).replace(
            tzinfo=pytz.utc
        )

    def sunset(self):
        return datetime.utcfromtimestamp(self.data["current"]["sunset"]).replace(
            tzinfo=pytz.utc
        )

    def hourly_summary(self, time_offset):
        # Find the right hour
        target = time.time() + time_offset
        for d1, d2 in zip(self.data["hourly"], self.data["hourly"][1:]):
            if d1["dt"] < target < d2["dt"]:
                break
        data = d1
        # Format a summary
        dt = datetime.utcfromtimestamp(data["dt"]).replace(tzinfo=pytz.utc)
        hour = dt.astimezone(self.timezone).strftime("%H")
        if hour == "":
            hour = "0"
        return {
            "time": dt,
            "hour": hour,
            "day": dt.astimezone(self.timezone).strftime("%d").lstrip("0"),
            "icon": self.code_to_icon(data["weather"][0]["id"], data["uvi"] == 0),
            "description": data["weather"][0]["main"].title(),
            "temperature": data["temp"],
            "wind": data["wind_speed"], # in m/s
            "wind-icon": self.wind_deg_to_icon(data["wind_deg"]),
            "rain": data.get("rain", {}).get("1h", 0),
            "snow": data.get("snow", {}).get("1h", 0),
            "clouds": data["clouds"],
            "uv": data["uvi"],
        }

    def daily_summary(self, day_offset):
        data = self.data["daily"][day_offset]
        # Format a summary
        return {
            "date": datetime.utcfromtimestamp(data["dt"]).replace(tzinfo=pytz.utc),
            "icon": self.code_to_icon(data["weather"][0]["id"]),
            "description": data["weather"][0]["main"].title(),
            "temperature_range": (data["temp"]["min"], data["temp"]["max"]),
            "wind": data["wind_speed"],
        }

    def active_alerts(self):
        result = []
        for alert in self.data.get("alerts", []):
            hours_left = math.ceil((alert["end"] - time.time()) / 3600)
            result.append(
                {
                    "text": alert["event"],
                    "subtext": (
                        "for %i hours" % hours_left
                        if hours_left != 1
                        else "for an hour"
                    ),
                }
            )
        return result

    def wind_deg_to_icon(self, deg):
        if deg < 22.5 or deg >= 337.5:
            return "arrow-down"
        elif deg < 67.5:
            return "arrow-down-left"
        elif deg < 112.5:
            return "arrow-left"
        elif deg < 157.5:
            return "arrow-up-left"
        elif deg < 202.5:
            return "arrow-up"
        elif deg < 247.5:
            return "arrow-up-right"
        elif deg < 292.5:
            return "arrow-right"
        else:
            return "arrow-down-right"

    # https://openweathermap.org/weather-conditions
    def code_to_icon(self, code, night=False):
        if code == 511:
            return "sleet"
        elif code == 771:
            return "thunderstorm"
        elif 200 <= code < 300:
            return "thunderstorm"
        elif 300 <= code < 400:
            return "showers"
        elif 500 <= code < 505:
            return "rain"
        elif 520 <= code < 600:
            return "showers"
        elif 611 <= code < 620:
            return "sleet"
        elif 600 <= code < 700:
            return "snow"
        elif 700 <= code < 800:
            return "fog"
        elif code == 800:
            return "clear-night" if night else "clear-day"
        elif 801 <= code < 804:
            return "clouds-few-night" if night else "clouds-few-day"
        else:
            return "clouds-scattered"
