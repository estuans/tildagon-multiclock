from tildagonos import tildagonos

class Face:
    def __init__(self,app):
        self.app = app
        self.clear_leds()

    def clear_leds(self):
        for i in range(0,12):
            tildagonos.leds[i+1] = (0, 0, 0)
    
    def draw(self,ctx):
        pass