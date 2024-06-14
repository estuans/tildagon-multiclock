import math

from tildagonos import tildagonos
from system.eventbus import eventbus
from app_components import clear_background
from system.patterndisplay.events import *


from .abstract import Face

bits = ["32", "16", "8", "4", "2", "1"]


def b60_to_bin(input: int) -> str:
    return '{0:06b}'.format(input)

class BinFace(Face):
       
    def draw(self, ctx):
        clear_background(ctx)
        if not self.app.led_control:
            eventbus.emit(PatternDisable())
            self.app.led_control = True

        self.draw_outer(ctx)
        self.draw_time(ctx, self.app.h, self.app.m, self.app.s, self.app.wday)
    
        ctx.restore()
        # self.draw_overlays(ctx)
    
    def render_bintime(self, val, offset=1, palette=(5,5,5)):
        for i in range(len(val)):
            bs = val[i]
            if bs == "1":
                tildagonos.leds[i + offset] = palette
            else:
                tildagonos.leds[i + offset] = (0, 0, 0)

    def draw_time(self, ctx, h, m, s, wday):
        
        binsecs = b60_to_bin(s)
        binmin = b60_to_bin(m)
        binhr = b60_to_bin(h)

        self.render_bintime(binsecs)
        self.render_bintime(binmin, offset=7, palette=(5,0,0))

        ctx.font_size = 32
        ctx.rgb(0.5, 0.5, 0.5)

        ctx.move_to(0, -30).text(binhr)
        ctx.move_to(0, 0).text(binmin)
        ctx.move_to(0, 30).text(binsecs)

        ctx.font_size = 16
        ctx.rgb(0.2, 0.2, 0.2)
        ctx.move_to(30, 60).text("S")
        ctx.move_to(-30, 60).text("M")

    def draw_outer(self, ctx):
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()

        ctx.rgb(0.6, 0.6, 0.6)
        ctx.font_size = 20
        ctx.begin_path()

        for i in range(0, 24):
            if (i % 2) == 0 and i not in [0,12,24]:
                continue 
            deg = i * 15
            rad = (2 * math.pi) * (deg / 360)
            x = 120 * math.sin(rad)
            y = -120 * math.cos(rad)
            # display.hexagon(ctx, x, y, 10)
            llen = 115
            if i in [0,12,24]:
                llen = 80
            ctx.move_to(x, y)
            
            ctx.line_to(llen * math.sin(rad), -llen * math.cos(rad))
            #tildagonos.leds[1 + i] = (0, 0, 0)

        ctx.stroke()

        #TODO: Make less jank.
        m = 0
        for i in range(0, 12):
            if (i % 2) == 0:
                continue
            deg = i * 15
            rad = (2 * math.pi) * (deg / 360)
            numeral = bits[m]
            ctx.move_to(98 * math.sin(rad), -98 * math.cos(rad))
            ctx.text(numeral)
            m+=1
        
        m = len(bits) - 1
        for i in range(12,24):
            if (i % 2) == 0:
                continue
            deg = i * 15
            rad = (2 * math.pi) * (deg / 360)
            numeral = bits[m]
            ctx.move_to(98 * math.sin(rad), -98 * math.cos(rad))
            ctx.text(numeral)
            m-=1
    