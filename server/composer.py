import os
import pytz
import math
import cairo
import datetime
from io import BytesIO
from weather import WeatherClient
from typing import List, Tuple, Union
from locationService import LocationService


BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
BLUE = (0, 0, 1)
LIGHT_BLUE = (0.5, 0.75, 1)
RED = (1, 0, 0)
PURPLE = (0.5, 0, 1)
ORANGE = (1, 0.55, 0)
GREY = (0.4, 0.4, 0.4)

RAIN_COLOR = BLUE
SNOW_COLOR = LIGHT_BLUE

fonts = {}
icons = {}


class ImageComposer:
    def __init__(self, api_key, lat, long, timezone):
        self.api_key = api_key
        self.lat = lat
        self.long = long
        self.width = 800
        self.height = 480

        if timezone not in pytz.all_timezones:
            raise ValueError("Invalid timezone")
        self.timezone = pytz.timezone(timezone)

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
            self.draw_city(context)
            self.draw_uvi(context)
            self.draw_temps(context)
            self.draw_column(context, self.weather.hourly_summary(0), 135, 30)
            self.draw_column(context, self.weather.hourly_summary(2 * 3600), 135, 155)
            self.draw_column(context, self.weather.hourly_summary(4 * 3600), 135, 280)
            self.draw_column(context, self.weather.hourly_summary(6 * 3600), 135, 405)
            self.draw_vertical_bar(context, 515, 135, 290)
            self.draw_column(context, self.weather.daily_summary(1), 135, 530)
            self.draw_column(context, self.weather.daily_summary(2), 135, 655)
            self.draw_meteogram(context)
            self.draw_stats(context)
            # Save out as bytestream
            output = BytesIO()
            surface.write_to_png(output)
            return output

    
    def draw_city(self, context: cairo.Context):
        location_service = LocationService(os.environ.get('MAPS_API_KEY'))
        
        city = location_service.get_city(self.lat, self.long)
        self.draw_text(
            context,
            text=city,
            position=(5, 125),
            align="left",
            size=30,
            color=BLACK,
            weight="light",
        )

    def draw_date(self, context: cairo.Context):
        now = datetime.datetime.now(self.timezone)
        # Day name
        left: int = 5
        self.draw_text(
            context,
            text=now.strftime("%A").title(),
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

    # TODO make this nicer
    def draw_uvi(self, context: cairo.Content):
        left = 500
        max_uvi = self.weather.uvi_max_today()
        self.draw_icon(context, "uv", (300, 5), 0.7)

        self.draw_text(
            context,
            position=(left, 35),
            text=f"Max: {round(max_uvi)}",
            color=BLACK,
            size=30,
            align="right"
        )

        current_uvi = self.weather.uvi_current()
        self.draw_text(
            context,
            position=(left, 65),
            text=f"Nu: {round(current_uvi)}",
            color=BLACK,
            size=30,
            align="right"
        )

    def draw_temps(self, context: cairo.Context):
        # Draw on temperature ranges
        daily = self.weather.daily_summary(0)
        temp_min, temp_max = daily["temperature_range"][0], daily["temperature_range"][1]
        # Draw background rects
        self.draw_roundrect(context, 535, 5, 85, 90, 5)
        context.set_source_rgb(*BLUE)
        context.fill()
        self.draw_roundrect(context, 710, 5, 85, 90, 5)
        context.set_source_rgb(*RED)
        context.fill()
        self.draw_text(
            context,
            position=(577, 55),
            text=f"{round(temp_min)}°",
            color=WHITE,
            weight="bold",
            size=50,
            align="center",
        )
        self.draw_text(
            context,
            position=(577, 82),
            text="Min.",
            color=WHITE,
            size=23,
            align="center",
        )
        self.draw_text(
            context,
            position=(665, 55),
            text=f"{round(self.weather.temp_current())}°",
            color=BLACK,
            weight="bold",
            size=50,
            align="center",
        )
        self.draw_text(
            context,
            position=(665, 82),
            text="Nu",
            color=BLACK,
            size=23,
            align="center",
        )
        self.draw_text(
            context,
            position=(753, 55),
            text=f"{round(temp_max)}°",
            color=WHITE,
            weight="bold",
            size=50,
            align="center",
        )
        self.draw_text(
            context,
            position=(753, 82),
            text="Max.",
            color=WHITE,
            size=23,
            align="center",
        )

    def draw_meteogram(self, context: cairo.Context):
        top = 310
        left = 10
        width = 625
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
        precip_to_y = lambda precip: top + 1 + (max(4 - precip, 0) * (height / 4))
        rain_points = []
        snow_points = []
        has_rain = False
        has_snow = False
        for hour in range(hours + 1):
            conditions = self.weather.hourly_summary(hour * 3600)
            if conditions["rain"] > 0:
                has_rain = True
            rain_points.append((hour_to_x(hour), precip_to_y(conditions["rain"])))
            if conditions["snow"] > 0:
                has_snow = True
            snow_points.append((hour_to_x(hour), precip_to_y(conditions["snow"])))
        self.draw_precip_curve(
            context, points=rain_points, bottom=int(precip_to_y(0)), color=RAIN_COLOR
        )
        self.draw_precip_curve(
            context, points=snow_points, bottom=int(precip_to_y(0)), color=SNOW_COLOR
        )

        # Agenda below the chart if there is rain or snow. Agenda is colored dots with text on the right
        left_cursor = left + left_axis
        if has_rain:
            left_cursor += self.draw_circle(context, left_cursor, top + 150, 6)
            context.set_source_rgb(*RAIN_COLOR)
            context.fill()
            left_cursor += self.draw_text(
                context,
                position=(left_cursor, top + 157),
                text="Regn",
                color=BLACK,
                size=20,
            )
            left_cursor += 40

        if has_snow:
            left_cursor += self.draw_circle(context, left_cursor, top + 150, 6)
            context.set_source_rgb(*SNOW_COLOR)
            context.fill()
            left_cursor += self.draw_text(
                context,
                position=(left_cursor, top + 157),
                text="Sne",
                color=BLACK,
                size=20,
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
                text=f"{t}°",
                position=(left + left_axis - 2, y),
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
            if hour % 2 == 0 and hour < hours:
                self.draw_text(
                    context,
                    text=conditions["hour"]+":00",
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
                if conditions["uv"] >= 3:
                    color = RED
                if conditions["uv"] >= 7:
                    color = PURPLE
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
                conditions["time"].astimezone(self.timezone).strftime("%H").lower()
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

        if "temperature" in conditions:
            self.draw_text(
                context,
                text=f"{round(conditions['temperature'])}°",
                position=(left + 30, top + 150),
                color=BLACK,
                size=28,
                align="right",
                weight="bold"
            )

        if "wind" in conditions and "wind-icon" in conditions:
            self.draw_icon(context, conditions["wind-icon"], (left + 40, top + 125), scaleFactor=0.5)
            self.draw_text(
                context,
                text=f"{round(conditions['wind'])}",
                position=(left + 70, top + 150),
                color=BLACK,
                size=28,
                align="left",
            )

        
        if "temperature_range" in conditions:
            self.draw_text(
                context,
                text=f"{round(conditions['temperature_range'][0])}° • {round(conditions['temperature_range'][1])}°",
                position=(left + 50, top + 150),
                color=BLACK,
                size=28,
                align="center",
            )

    def draw_vertical_bar(self, context: cairo.Context, x, y1, y2):
        context.set_line_width(2)
        context.set_source_rgb(*GREY)
        context.move_to(x, y1)
        context.line_to(x, y2)
        context.stroke()

    def draw_stats(self, context: cairo.Context):
        # Draw sunrise, sunset, AQI icon and values
        self.draw_icon(context, "rise-set", (650, 300))
        self.draw_text(
            context,
            position=(705, 337),
            text=self.weather.sunrise().astimezone(self.timezone).strftime("%H:%M"),
            color=BLACK,
            size=32,
        )
        self.draw_text(
            context,
            position=(705, 385),
            text=self.weather.sunset().astimezone(self.timezone).strftime("%H:%M"),
            color=BLACK,
            size=32,
        )

        # Draw ride stats
        self.draw_icon(context, "ocean-temp", (657, 402), scaleFactor=0.5)
        self.draw_text(
            context,
            text=f'{WeatherClient.ocean_temp(self)}°',
            position=(705, 430),
            align="left",
            size=30,
            color=BLACK,
            weight="bold"
        )

    def draw_roundrect(self, context, x, y, width, height, r):
        context.move_to(x, y + r)
        context.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        context.arc(x + width - r, y + r, r, 3 * math.pi / 2, 0)
        context.arc(x + width - r, y + height - r, r, 0, math.pi / 2)
        context.arc(x + r, y + height - r, r, math.pi / 2, math.pi)
        context.close_path()

    def draw_circle(self, context, x, y, r) -> int:
        context.arc(x, y, r, 0, 2 * math.pi)
        context.close_path()
        return r*2 # return diameter

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

    def draw_icon(self, context: cairo.Context, icon: str, position: Tuple[int, int], scaleFactor: float = 1):
        image = cairo.ImageSurface.create_from_png(
            os.path.join(os.path.dirname(__file__), "icons", f"{icon}.png")
        )
        context.save()
        context.translate(*position)
        context.scale(scaleFactor, scaleFactor)
        context.set_source_surface(image)
        context.paint()
        context.restore()
