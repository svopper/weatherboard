import datetime
import math
import os
from io import BytesIO
from typing import List, Tuple, Union

import pytz
import cairo

from weather import WeatherClient
from holidays import holidays

# BLACK = 0
# WHITE = 1
# GREEN = 2
# BLUE = 3
# RED = 4
# YELLOW = 5
# ORANGE = 6
# PALETTE = [0,0,0,255,255,255,0,200,0,0,0,200,200,0,0,230,230,0,200,100,0]
BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
GREEN = (0, 1, 0)
BLUE = (0, 0, 1)
RED = (1, 0, 0)
YELLOW = (1, 1, 0)
PURPLE = (0.5, 0, 1)
ORANGE = (1, 0.55, 0)
GREY = (0.4, 0.4, 0.4)
fonts = {}
icons = {}


class ImageComposer7:
    def __init__(self, api_key, lat, long, timezone):
        self.api_key = api_key
        self.lat = lat
        self.long = long
        self.timezone = pytz.timezone(timezone)
        self.width = 800
        self.height = 480

    def render(self):
        # Fetch weather
        self.weather = WeatherClient(self.lat, self.long, self.timezone)
        self.weather.load(self.api_key)
        # Create image
        with cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height) as surface:
            context = cairo.Context(surface)
            context.rectangle(0, 0, self.width, self.height)
            context.set_source_rgb(1, 1, 1)
            context.fill()
            # Draw features
            self.draw_date(context)
            self.draw_temps(context)
            self.draw_column(context, self.weather.hourly_summary(0), 120, 30)
            self.draw_column(context, self.weather.hourly_summary(2 * 3600), 120, 155)
            self.draw_column(context, self.weather.hourly_summary(5 * 3600), 120, 280)
            self.draw_column(context, self.weather.daily_summary(1), 120, 440)
            self.draw_meteogram(context)
            self.draw_alerts(context)
            self.draw_stats(context)
            # Save out as bytestream
            output = BytesIO()
            surface.write_to_png(output)
            return output

    def draw_date(self, context: cairo.Context):
        now = datetime.datetime.now(self.timezone)
        # Day name
        left: int = 5
        self.draw_text(
            context,
            text=now.strftime("%A"),
            position=(left, 55),
            size=60,
            weight="light",
        )
        # Day number
        left += self.draw_text(
            context,
            text=now.strftime("%-d. %B").lower(),
            position=(left, 90),
            size=30,
            color=BLACK,
            weight="bold",
        )

    def draw_temps(self, context: cairo.Context):
        # Draw on temperature ranges
        temp_min, temp_max = self.weather.temp_range_24hr()
        c_to_f = lambda c: (c * (9 / 5)) + 32
        # Draw background rects
        self.draw_roundrect(context, 335, 5, 85, 90, 5)
        context.set_source_rgb(*BLUE)
        context.fill()
        self.draw_roundrect(context, 510, 5, 85, 90, 5)
        context.set_source_rgb(*RED)
        context.fill()
        self.draw_text(
            context,
            position=(377, 55),
            text=round(temp_min),
            color=WHITE,
            weight="bold",
            size=50,
            align="center",
        )
        self.draw_text(
            context,
            position=(377, 82),
            text="Min.",
            color=WHITE,
            size=23,
            align="center",
        )
        self.draw_text(
            context,
            position=(465, 55),
            text=round(self.weather.temp_current()),
            color=BLACK,
            weight="bold",
            size=50,
            align="center",
        )
        self.draw_text(
            context,
            position=(465, 82),
            text="Nu",
            color=BLACK,
            size=23,
            align="center",
        )
        self.draw_text(
            context,
            position=(553, 55),
            text=round(temp_max),
            color=WHITE,
            weight="bold",
            size=50,
            align="center",
        )
        self.draw_text(
            context,
            position=(553, 82),
            text="Max.",
            color=WHITE,
            size=23,
            align="center",
        )

    def draw_meteogram(self, context: cairo.Context):
        top = 310
        left = 10
        width = 425
        height = 85
        left_axis = 18
        hours = 24
        y_interval = 10
        graph_width = width - left_axis
        # Establish function that converts hour offset into X
        hour_to_x = lambda hour: left + left_axis + (hour * (graph_width / hours))
        # Draw day boundary lines
        today = self.weather.hourly_summary(0)["day"]
        for hour in range(hours):
            day = self.weather.hourly_summary(hour * 3600)["day"]
            if day != today:
                context.save()
                context.move_to(hour_to_x(hour) - 0.5, top)
                context.line_to(hour_to_x(hour) - 0.5, top + height)
                context.set_line_width(1)
                context.set_source_rgb(*BLACK)
                context.set_dash([1, 1])
                context.stroke()
                context.restore()
                today = day
        # Establish temperature-to-y function
        temps = [
            self.weather.hourly_summary(hour * 3600)["temperature"]
            for hour in range(hours + 1)
        ]
        temp_min = min(temps)
        temp_max = max(temps)
        scale_min = math.floor(temp_min / y_interval) * y_interval
        scale_max = math.ceil(temp_max / y_interval) * y_interval
        temp_to_y = lambda temp: top + (scale_max - temp) * (
            height / (scale_max - scale_min)
        )
        # Draw rain/snow curves
        precip_to_y = lambda rain: top + 1 + (max(4 - rain, 0) * (height / 4))
        rain_points = []
        snow_points = []
        for hour in range(hours + 1):
            conditions = self.weather.hourly_summary(hour * 3600)
            rain_points.append((hour_to_x(hour), precip_to_y(conditions["rain"])))
            snow_points.append((hour_to_x(hour), precip_to_y(conditions["snow"])))
        self.draw_precip_curve(
            context, points=rain_points, bottom=int(precip_to_y(0)), color=BLUE
        )
        self.draw_precip_curve(
            context, points=snow_points, bottom=int(precip_to_y(0)), color=PURPLE
        )
        # Draw value lines
        for t in range(scale_min, scale_max + 1, y_interval):
            y = temp_to_y(t)
            context.move_to(left + left_axis, y + 0.5)
            context.line_to(left + left_axis + graph_width, y + 0.5)
            context.set_line_width(1)
            context.set_source_rgb(*BLACK)
            context.save()
            context.set_dash([1, 1])
            context.stroke()
            context.restore()
            self.draw_text(
                context,
                text=t,
                position=(left + left_axis - 6, y),
                size=14,
                color=BLACK,
                align="right",
                valign="middle",
            )
        # Draw temperature curve
        for hour in range(hours + 1):
            conditions = self.weather.hourly_summary(hour * 3600)
            if hour == 0:
                context.move_to(hour_to_x(hour), temp_to_y(conditions["temperature"]))
            else:
                context.line_to(hour_to_x(hour), temp_to_y(conditions["temperature"]))
        context.set_source_rgb(*WHITE)
        context.set_line_width(6)
        context.stroke_preserve()
        lg3 = cairo.LinearGradient(0, temp_to_y(0), 0, temp_to_y(0) + 1)
        lg3.add_color_stop_rgb(0, *RED)
        lg3.add_color_stop_rgb(1, *BLUE)
        context.set_source(lg3)
        context.set_line_width(3)
        context.stroke()
        # Draw hours and daylight/UV bar
        bar_top = top + height + 13
        for hour in range(hours + 1):
            conditions = self.weather.hourly_summary(hour * 3600)
            x = hour_to_x(hour)
            # Hour label
            if hour % 3 == 0 and hour < hours:
                self.draw_text(
                    context,
                    text=conditions["hour"],
                    position=(x, bar_top + 19),
                    size=15,
                    align="center",
                    valign="bottom",
                )
            # Conditions bar
            if hour < hours:
                color = BLACK
                if conditions["uv"]:
                    color = ORANGE
                if conditions["uv"] > 7:
                    color = RED
                context.rectangle(x, bar_top, (graph_width / hours) + 1, 8)
                context.set_source_rgb(*color)
                context.fill()

    def draw_column(self, context: cairo.Context, conditions, top, left):
        # Heading
        if "date" in conditions:
            time_text = (
                conditions["date"].astimezone(self.timezone).strftime("%A").title()
            )
        else:
            time_text = (
                conditions["time"].astimezone(self.timezone).strftime("%-H").lower()
            )
        self.draw_text(
            context,
            text=time_text,
            position=(left + 50, top + 25),
            color=BLACK,
            size=28,
            align="center",
        )
        self.draw_icon(context, conditions["icon"], (left, top + 33))

    def draw_alerts(self, context: cairo.Context):
        # Load weather alerts
        alerts = self.weather.active_alerts()
        for alert in alerts:
            alert["color"] = RED
        # Add holidays
        for holiday_date, holiday_name in holidays.items():
            days_until = (holiday_date - datetime.date.today()).days
            if 0 <= days_until <= 14:
                alerts.append(
                    {
                        "text": holiday_name,
                        "subtext": (
                            "om %i dage" % days_until if days_until != 1 else "i morgen"
                        ),
                        "color": BLUE,
                    }
                )
        # Add no alert pill if there weren't any
        if not alerts:
            alerts = [{"text": "Ingen advarsler", "color": BLACK}]
        top = 265
        left = 5
        for alert in alerts:
            text = alert["text"].upper()
            text_width = self.draw_text(
                context,
                text,
                position=(0, 0),
                size=20,
                weight="bold",
                noop=True,
            )
            self.draw_roundrect(context, left, top, text_width + 15, 30, 4)
            context.set_source_rgb(*alert["color"])
            context.fill()
            left += self.draw_text(
                context,
                text,
                position=(left + 8, top + 23),
                size=20,
                color=WHITE,
                weight="bold",
            )
            if alert.get("subtext"):
                subtext_width = self.draw_text(
                    context,
                    alert["subtext"],
                    position=(left + 20, top + 26),
                    size=15,
                    color=BLACK,
                )
            else:
                subtext_width = 0
            left += 30 + subtext_width

    def draw_stats(self, context: cairo.Context):
        # Draw sunrise, sunset, AQI icon and values
        self.draw_icon(context, "rise-set-aqi", (450, 300))
        self.draw_text(
            context,
            position=(505, 337),
            text=self.weather.sunrise().astimezone(self.timezone).strftime("%H:%M"),
            color=BLACK,
            size=32,
        )
        self.draw_text(
            context,
            position=(505, 385),
            text=self.weather.sunset().astimezone(self.timezone).strftime("%H:%M"),
            color=BLACK,
            size=32,
        )
        # Pick AQI text and color
        aqi = self.weather.aqi()
        if aqi < 50:
            color = GREEN
        elif aqi < 150:
            color = ORANGE
        else:
            color = RED
        text_width = self.draw_text(context, "N/A", size=30, weight="bold", noop=True)
        self.draw_roundrect(context, 505, 402, text_width + 13, 36, 3)
        context.set_source_rgb(*color)
        context.fill()
        self.draw_text(
            context, position=(510, 430), text="N/A", color=WHITE, size=30, weight="bold"
        )

    def draw_roundrect(self, context, x, y, width, height, r):
        context.move_to(x, y + r)
        context.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        context.arc(x + width - r, y + r, r, 3 * math.pi / 2, 0)
        context.arc(x + width - r, y + height - r, r, 0, math.pi / 2)
        context.arc(x + r, y + height - r, r, math.pi / 2, math.pi)
        context.close_path()

    def draw_text(
        self,
        context: cairo.Context,
        text: Union[str, int],
        size: int,
        position: Tuple[int, int] = (0, 0),
        color=BLACK,
        weight="regular",
        align="left",
        valign="top",
        noop=False,
    ) -> int:
        text = str(text)
        if weight == "light":
            context.select_font_face("Roboto Light")
        elif weight == "bold":
            context.select_font_face(
                "Roboto", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD
            )
        else:
            context.select_font_face("Roboto")
        context.set_source_rgb(*color)
        context.set_font_size(size)
        xbear, ybear, width, height = context.text_extents(text)[:4]
        if align == "right":
            x = position[0] - width - xbear
        elif align == "center":
            x = position[0] - (width / 2) - xbear
        else:
            x = position[0]
        if valign == "middle":
            y = position[1] + (height / 2)
        elif valign == "bottom":
            y = position[1] + height
        else:
            y = position[1]
        if not noop:
            context.move_to(x, y)
            context.show_text(text)
        return int(width)

    def draw_precip_curve(
        self,
        context: cairo.Context,
        points: List[Tuple[int, int]],
        bottom: int,
        color,
        curviness: float = 7,
    ):
        # Draw the top curves
        for i, point in enumerate(points):
            if i == 0:
                context.move_to(*point)
            else:
                last_point = points[i - 1]
                context.curve_to(
                    last_point[0] + curviness,
                    last_point[1],
                    point[0] - curviness,
                    point[1],
                    point[0],
                    point[1],
                )
        # Draw the rest and fill
        context.line_to(points[-1][0], bottom)
        context.line_to(points[0][0], bottom)
        context.close_path()
        context.set_source_rgb(*color)
        context.fill()

    def draw_icon(self, context: cairo.Context, icon: str, position: Tuple[int, int]):
        image = cairo.ImageSurface.create_from_png(
            os.path.join(os.path.dirname(__file__), "icons-7", f"{icon}.png")
        )
        context.save()
        context.translate(*position)
        context.set_source_surface(image)
        context.paint()
        context.restore()
