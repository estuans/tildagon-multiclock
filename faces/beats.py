from .abstract import Face

from tildagonos import tildagonos
from system.eventbus import eventbus
from app_components import clear_background
from system.patterndisplay.events import *

import time

SEC_LEDS = (
    (5, 5, 5),
    (10, 10, 10),
    (15, 15, 15),
    (20, 20, 20),
    (25, 25, 25)
)

class BeatFace(Face):

    def draw(self, ctx):
        clear_background(ctx)
        self.draw_time(ctx, self.app.h, self.app.m, self.app.s, self.app.wday)

        ctx.restore()
        # self.draw_overlays(ctx)

    def itime(self):
        """Calculate and return Swatch Internet Time

        :returns: No. of beats (Swatch Internet Time)
        :rtype: float
        """
        UTC_OFFSET = 1 * 60 * 60
        zurich_time = time.localtime(time.time() + UTC_OFFSET)
        h, m, s = zurich_time[3:6]

        beats = ((h * 3600) + (m * 60) + s) / 86.4

        if beats > 1000:
            beats -= 1000
        elif beats < 0:
            beats += 1000

        return beats
    
    def draw_time(self, ctx, h, m, s, wday):
        ctx.font_size = 48

        itime = self.itime()
        beat_fract = int(itime % 1 * 100)
        t_str = "@{:.2f}".format(itime)
        ctx.rgb(0.5, 0.5, 0.5)
        wday_h = 48
        wday_w = ctx.text_width(t_str) + 4
        ctx.move_to(0, 0).text(t_str)
        ctx.font_size = 28
        ctx.move_to(0, 50).text(".beats")
        ctx.rectangle(0 - wday_w // 2, -wday_h // 2, wday_w, wday_h).stroke()

        if not self.app.led_control:
            eventbus.emit(PatternDisable())
            self.app.led_control = True

        self.secs_led =  int(beat_fract / (100 / 13)) + 1
        tildagonos.leds[self.secs_led - 1] = (0,0,0)
        tildagonos.leds[self.secs_led] = SEC_LEDS[beat_fract % 5]

        if self.secs_led == 1:
            tildagonos.leds[12] = (0,0,0)


