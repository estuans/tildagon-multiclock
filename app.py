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

from .faces import StockFace, BeatFace, BinFace

def cycle(p):
    try:
        len(p)
    except TypeError:
        # len() is not defined for this type. Assume it is
        # a finite iterable so we must cache the elements.
        cache = []
        for i in p:
            yield i
            cache.append(i)
        p = cache
    while p:
        yield from p


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

FACES = cycle([StockFace, BeatFace, BinFace])

class MultiClockApp(app.App):

    def __init__(self):
        super().__init__()
        self.button_states = Buttons(self)
        # init -> wificonnect -> ntp -> clock
        # init -> clock
        self.state = "init"
        self.flip = False
        self.led_control = False
        self.face = next(FACES)(self)

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            if self.led_control:
                # print(f"secs_led {self.secs_led} clearing")
                # This doesn't seem to work from update()...?
                # tildagonos.leds[self.secs_led] = (0, 0, 0)

                eventbus.emit(PatternEnable())
                self.led_control = False

            self.minimise()
            return
        
        if self.button_states.get(BUTTON_TYPES["RIGHT"]):
            self.button_states.clear()
            self.face = next(FACES)(self)
            return

        if self.state == "wificonnect":
            if wifi.status():
                self.state = "ntp"

        if self.state == "ntp":
            ntptime.settime()
            self.state = "clock"

        if self.state == "init" or self.state == "clock":
            self.update_time()

            self.accel_data = imu.acc_read()
            # Way sensor is orientated, x val is 9.8 when hanging down normally,
            # and thus -9.8 when lifted up the other way. -5 is about right for
            # when held up a bit.
            self.flip = self.accel_data[0] < -5

    def update_time(self):
        
        self.yy, self.mm, self.dd, self.h, self.m, self.s, self.wday, _ = self.ntime = time.gmtime()
        if self.yy == 2000:
            # the default time

            if not wifi.status():
                wifi.connect()
                self.state = "wificonnect"
            else:
                self.state = "ntp"

        else:
            self.state = "clock"
            #self.secs_led = (self.s // 5) + 1
            #tildagonos.leds[self.secs_led] = SEC_LEDS[self.s % 5]

    # def background_update(self, delta):
    #     self.update_time()

    def draw(self, ctx):
        ctx.save()
        ctx.rotate(math.pi if self.flip else 0)

        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
                
        if self.state == "wificonnect" or self.state == "test":
            ctx.move_to(0, -10).text("Connecting")
            ctx.move_to(0, 10).text("to wifi...")

        if self.state == "clock":
            self.face.draw(ctx)

        ctx.restore()
        # self.draw_overlays(ctx)

    def draw_outer(self, ctx):
        self.face.draw_outer(ctx)

__app_export__ = MultiClockApp
