from tildagonos import tildagonos
from system.eventbus import eventbus
from system.patterndisplay.events import *

import math

from .abstract import Face

HOUR_HAND_LEN = 60
MINUTE_HAND_LEN = 85
WEEKDAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")

SEC_LEDS = (
    (5, 5, 5),
    (10, 10, 10),
    (15, 15, 15),
    (20, 20, 20),
    (25, 25, 25)
)


class StockFace(Face):

    def draw(self, ctx):
        ctx.save()
        
        self.draw_outer(ctx)
        self.draw_time(ctx, self.app.h, self.app.m, self.app.s, self.app.wday)

        ctx.restore()
        # self.draw_overlays(ctx)

    def draw_outer(self, ctx):
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()

        ctx.rgb(1, 1, 1)
        ctx.font_size = 24
        ctx.begin_path()

        for i in range(0, 12):
            deg = i * 30
            rad = (2 * math.pi) * (deg / 360)
            x = 120 * math.sin(rad)
            y = -120 * math.cos(rad)
            # display.hexagon(ctx, x, y, 10)
            ctx.move_to(x, y)
            ctx.line_to(115 * math.sin(rad), -115 * math.cos(rad))
            tildagonos.leds[1 + i] = (0, 0, 0)

        ctx.stroke()

        for i in range(0, 12):
            deg = i * 30
            rad = (2 * math.pi) * (deg / 360)
            numeral = str(i if i != 0 else 12)
            ctx.move_to(98 * math.sin(rad), -98 * math.cos(rad))
            ctx.text(numeral)

    def draw_time(self, ctx, h, m, s, wday):
        h = h % 12
        h = h + 1 # Manually adjust for BST due to NTP not seeming to do local time right
        hangle = (2 * math.pi) * ((h + m / 60) * 30) / 360
        mangle = (2 * math.pi) * (m * 6) / 360

        ctx.font_size = 20
        ctx.rgb(0.5, 0.5, 0.5)
        wday_str = WEEKDAYS[wday]
        wday_w = ctx.text_width(wday_str) + 4
        wday_h = 24
        ctx.move_to(50, 0).text(wday_str)
        ctx.rectangle(50 - wday_w // 2, -wday_h // 2, wday_w, wday_h).stroke()

        ctx.rgb(1, 1, 1)
        ctx.begin_path()
        ctx.move_to(0, 0).line_to(HOUR_HAND_LEN * math.sin(hangle), -HOUR_HAND_LEN * math.cos(hangle))
        ctx.move_to(0, 0).line_to(MINUTE_HAND_LEN * math.sin(mangle), -MINUTE_HAND_LEN * math.cos(mangle))
        ctx.stroke()

        # ctx.move_to(0, 0).text(f"{self.accel_data[0]}")
        # ctx.move_to(0, 20).text(f"{self.accel_data[1]}")
        # ctx.move_to(0, 40).text(f"{self.accel_data[2]}")

        if not self.app.led_control:
            eventbus.emit(PatternDisable())
            self.app.led_control = True

        self.secs_led = (s // 5) + 1
        tildagonos.leds[self.secs_led] = SEC_LEDS[s % 5]



