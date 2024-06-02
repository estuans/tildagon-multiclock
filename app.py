import app
import display
from events.input import Buttons, BUTTON_TYPES
import imu
import math
import ntptime
from system.eventbus import eventbus
from system.patterndisplay.events import *
from tildagonos import tildagonos
import time
import wifi

HOUR_HAND_LEN = 60
MINUTE_HAND_LEN = 80
LED_BRIGHTNESS = 30

# R, G, B, Y, M
# SEC_LEDS = (
#     (LED_BRIGHTNESS, 0, 0),
#     (0, LED_BRIGHTNESS, 0),
#     (0, 0, LED_BRIGHTNESS),
#     (LED_BRIGHTNESS, LED_BRIGHTNESS, 0),
#     (LED_BRIGHTNESS, 0, LED_BRIGHTNESS)
# )

SEC_LEDS = (
    (5, 5, 5),
    (10, 10, 10),
    (15, 15, 15),
    (20, 20, 20),
    (25, 25, 25)
)


class ClockApp(app.App):
    def __init__(self):
        super().__init__()
        self.button_states = Buttons(self)
        eventbus.emit(PatternDisable())
        # clock -> wificonnect -> ntp -> clock
        self.state = "clock"
        self.flip = False

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            if self.secs_led is not None:
                # print(f"secs_led {self.secs_led} clearing")
                # This doesn't seem to work from update()...?
                tildagonos.leds[self.secs_led] = (0, 0, 0)
            self.minimise()
            return

        if self.state == "wificonnect":
            if wifi.status():
                self.state = "ntp"

        if self.state == "ntp":
            ntptime.settime()
            self.state = "clock"

        if self.state == "clock":
            self.update_time()

            self.accel_data = imu.acc_read()
            # Way sensor is orientated, x val is 9.8 when hanging down normally,
            # and thus -9.8 when lifted up the other way. -5 is about right for
            # when held up a bit.
            self.flip = self.accel_data[0] < -5

    def update_time(self):
        self.yy, self.mm, self.dd, self.h, self.m, self.s, _, _ = time.gmtime()
        if self.yy == 2000:
            # the default time

            if not wifi.status():
                wifi.connect()
                self.state = "wificonnect"
            else:
                self.state = "ntp"

        else:
            self.state = "clock"
            self.secs_led = (self.s // 5) + 1
            tildagonos.leds[self.secs_led] = SEC_LEDS[self.s % 5]

    def background_update(self):
        self.update_time()

    def draw(self, ctx):
        ctx.save()

        ctx.rotate(math.pi if self.flip else 0)

        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        
        self.draw_outer(ctx)
        
        if self.state == "wificonnect" or self.state == "test":
            ctx.move_to(0, -10).text("Connecting")
            ctx.move_to(0, 10).text("to wifi...")

        if self.state == "clock":
            self.draw_time(ctx, self.h, self.m, self.s)

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

    def draw_time(self, ctx, h, m, s):
        h = h % 12
        h = h + 1 # Manually adjust for BST due to NTP not seeming to do local time right
        hangle = (2 * math.pi) * ((h + m / 60) * 30) / 360
        mangle = (2 * math.pi) * (m * 6) / 360
        ctx.begin_path()
        ctx.move_to(0, 0).line_to(HOUR_HAND_LEN * math.sin(hangle), -HOUR_HAND_LEN * math.cos(hangle))
        ctx.move_to(0, 0).line_to(MINUTE_HAND_LEN * math.sin(mangle), -MINUTE_HAND_LEN * math.cos(mangle))
        ctx.stroke()

        # ctx.move_to(0, 0).text(f"{self.accel_data[0]}")
        # ctx.move_to(0, 20).text(f"{self.accel_data[1]}")
        # ctx.move_to(0, 40).text(f"{self.accel_data[2]}")

        self.secs_led = (s // 5) + 1
        tildagonos.leds[self.secs_led] = SEC_LEDS[s % 5]


__app_export__ = ClockApp
