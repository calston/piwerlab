import pygame
import math

from pygame.locals import *

class Colours(object):
    white = (255, 255, 255)
    light_gray = (128, 128, 128)
    gray = (32, 32, 32)
    black = (0, 0, 0)

    sepia = (120, 100, 82)

    red = (255, 0, 0)
    green = (0, 255, 0)

    blue = (0, 0, 255)
    electric_blue = (0, 191, 255)

class Pannel(object):
    def __init__(self, display):
        self.widgets = []
        self.display = display

    def addWidget(self, widgetClass, *args, **kw):
        w = widgetClass(*args, **kw)
        w.setDisplay(self.display)
        self.widgets.append(w)
        return w

    def sendEvent(self, event):
        for w in reversed(self.widgets):
            if w.sendEvent(event):
                break

    def draw(self):
        for w in self.widgets:
            w.draw()
        self.display.flip()

    def update(self):
        fl = False
        for w in self.widgets:
            r = w.update()
            fl = fl or r

        if fl:
            self.display.flip()

class Widget(object):
    def __init__(self, x, y, w=1, h=1):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.display = None
        self.surf = None

    def update(self):
        # Called on every display loop - must return True if re-render required
        return False

    def draw(self):
        # Draw the initial widget
        pass

    def setDisplay(self, display):
        self.display = display
        self.surf = display.display

    def inside(self, x, y):
        inx = (x > self.x) and (y < (self.x + self.w))
        iny = (y > self.y) and (y < (self.y + self.h))

        if inx and iny:
            return True
        else:
            return False

    def touched(self):
        pass

    def sendEvent(self, event):
        # Dispatch any events which affect this widget
        if event.type == MOUSEBUTTONDOWN:
            x, y = event.pos

            if self.inside(x, y):
                self.touched()
                return True

        return False

class SevenSegment(Widget):
    charMap = {
        '0': (True,  True,  True,  True,  True,  True,  False),
        '1': (False, True,  True,  False, False, False, False),
        '2': (True,  True,  False, True,  True,  False, True),
        '3': (True,  True,  True,  True,  False, False, True),
        '4': (False, True,  True,  False, False, True,  True),
        '5': (True,  False, True,  True,  False, True,  True),
        '6': (True,  False, True,  True,  True,  True,  True),
        '7': (True,  True,  True,  False, False, False, False),
        '8': (True,  True,  True,  True,  True,  True,  True),
        '9': (True,  True,  True,  False, False, True,  True)
    }

    def __init__(self, x, y, w, h, value = 0, digits = 2, colour = Colours.red, digit_pad = 5):
        Widget.__init__(self, x, y, w, h)

        self.digits = digits

        self.colour = colour

        self.lastV = self.value = value
        self.digit_pad = digit_pad

        self.constructSurface()

    def constructSurface(self):
        self.digit = pygame.Surface((self.w, self.h))

        
        self.dw = int((self.w / self.digits) - self.digit_pad)

        dh = (self.h / 2) - self.digit_pad

        # Horizontal segment
        self.h_dark = pygame.Surface((self.dw - 10, 10), pygame.SRCALPHA)
        self.h_light = pygame.Surface((self.dw - 10, 10), pygame.SRCALPHA)

        h_shape = [
            (0, 5),
            (5, 0),
            (self.dw - 15, 0),
            (self.dw - 10, 5),
            (self.dw - 15, 10),
            (5, 10)
        ]
        pygame.draw.polygon(self.h_dark, Colours.gray, h_shape)
        pygame.draw.polygon(self.h_light, self.colour, h_shape)

        self.v_dark = pygame.Surface((10, dh), pygame.SRCALPHA)
        self.v_light = pygame.Surface((10, dh), pygame.SRCALPHA)

        v_shape = [
            (5, 0),
            (10, 5),
            (10, dh - 15),
            (5, dh - 10),
            (0, dh - 15),
            (0, 5),
        ]
        pygame.draw.polygon(self.v_dark, Colours.gray, v_shape)
        pygame.draw.polygon(self.v_light, self.colour, v_shape)

        for i in range(self.digits):
            x = (self.dw + self.digit_pad) * i

            # Horizontal segments
            self.digit.blit(self.h_dark, (x+5, 0))
            self.digit.blit(self.h_dark, (x+5, (self.h/2) - 5))
            self.digit.blit(self.h_dark, (x+5, self.h - 10))

            # Vertical segments
            self.digit.blit(self.v_dark, (x, 10))
            self.digit.blit(self.v_dark, (x+self.dw-10, 10))
            self.digit.blit(self.v_dark, (x, 5+self.h/2))
            self.digit.blit(self.v_dark, (x+self.dw-10, 5+self.h/2))

    def lightSegments(self):
        panel = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        dst = (self.h_dark, self.h_light, self.v_dark, self.v_light)

        v = ("%f" % self.value)
        cn = 0
        for c in v:
            if cn > self.digits:
                break

            if c in self.charMap:
                x = (self.dw + self.digit_pad) * cn
                cn += 1
                segments = [
                    (0, (x+5, 0)),
                    (2, (x+self.dw-10, 10)),
                    (2, (x+self.dw-10, 5 + self.h/2)),
                    (0, (x+5, self.h - 10)),
                    (2, (x, 5+self.h/2)),
                    (2, (x, 10)),
                    (0, (x+5, (self.h/2) - 5)),
                ]

                for i, v in enumerate(self.charMap[c]):
                    if v:
                        args = (dst[segments[i][0] + 1], segments[i][1])
                    else:
                        args = (dst[segments[i][0]], segments[i][1])

                    panel.blit(*args)

            if (c == '.') and cn < self.digits:
                pygame.draw.circle(panel, self.colour, (x + self.dw + 2, self.h-5), 5)

        return panel

    def draw(self):
        if self.digit:
            self.display.blit(self.digit, (self.x, self.y))
            self.display.blit(self.lightSegments(), (self.x, self.y))

    def update(self):
        if self.value != self.lastV:
            self.draw()
            self.lastV = self.value
            return True

class FancyGauge(Widget):
    def __init__(self, x, y, r, showPercentage = False, valueFormat = "%d", colour=Colours.green, units = None, maxScale = 25):
        Widget.__init__(self, x, y)
        self.r = r
        self.h = self.w = (2 * r) + 2

        self.value = 0
        self.lastV = self.value
        self.valueFormat = valueFormat
        self.showPercentage = showPercentage

        self.colour = colour
        self.units = units
        self.maxScale = maxScale

        self.constructSurface()

    def constructSurface(self):
        self.meter = pygame.Surface((self.h, self.w))

        pygame.draw.circle(self.meter, Colours.gray, (int(self.w/2), int(self.h/2)), self.r, int(self.r*0.25))

        self.valueFont = pygame.font.Font('carlito.ttf', int(self.r*0.6))

        if self.units:
            unitFont = pygame.font.Font('carlito.ttf', int(self.r*0.30))
            w, h = unitFont.size(self.units)
            units = unitFont.render(self.units, True, Colours.light_gray)
            self.meter.blit(units, ((self.w / 2) - (w/2), ((self.h/2) - (h/2)) + h))

    def arcSlice(self, center, rad1, rad2, angle):
        arc1 = []
        arc2 = []
        pi = math.pi
        for n in range(-90,angle-90):
            # Trig is expensive, do it once.
            cs = math.cos(n*pi/180)
            ss = math.sin(n*pi/180)
            
            arc1.append((center[0] + int(rad1 * cs), center[1] + int(rad1 * ss)))
            arc2.insert(0, (center[0] + int(rad2 * cs), center[1] + int(rad2 * ss)))

        if not arc1:
            return []

        arc2.extend(arc1[0])
        arc1.extend(arc2)
        return arc1

    def draw(self):
        submeter = pygame.Surface((self.h, self.w))
        submeter.blit(self.meter, (0,0))

        # Draw value text
        pv = self.value / self.maxScale
        if pv > 1:
            pv = 1

        if self.showPercentage:
            vt = "%d%%" % int(pv*100)
        else:
            vt = self.valueFormat % self.value
            
        w, h = self.valueFont.size(vt)
        val = self.valueFont.render(vt, True, self.colour)

        submeter.blit(val, ((self.w / 2) - (w/2), (self.h/2) - (h/2) - 5))


        # Draw the value arc
        if (pv > 0):
            sm2 = pygame.Surface((self.h, self.w), pygame.SRCALPHA)
            arcSliceD = int(math.ceil(360 * pv))
            poly = self.arcSlice((int(self.w/2), int(self.h/2)), self.r, self.r*0.75, arcSliceD)
            if poly:
                pygame.draw.polygon(sm2, self.colour, poly)
                submeter.blit(sm2, (0, 0))

        self.display.blit(submeter, (self.x, self.y))

    def update(self):
        if (self.value != self.lastV) and (self.value <= self.maxScale):
            self.draw()
            self.lastV = self.value
            return True


class OldSchoolMeter(Widget):
    def __init__(self, x, y, maxScale = 25):
        Widget.__init__(self, x, y)
        self.h, self.w = 100, 146
        self.maxScale = maxScale
        self.value = 0
        self.lastV = self.value
        self.constructSurface()

    def constructSurface(self):
        self.meter = pygame.image.load('images/meter-bg.png').convert()
        font = pygame.font.Font('carlito.ttf', 12)
        # Calculate the increment between text
        segments = math.ceil(self.maxScale / 6.0)

        r = 60.0

        # Render display markings
        for i in range(6):
            text = font.render(str(i*segments), True, Colours.sepia) 

            a = float(50.0 - (i * 20.0))

            text = pygame.transform.rotate(text, a)

            aR = (a+90) * (math.pi / 180.0)

            self.meter.blit(text, (67 + int(math.cos(aR) * (r*1.05)), 92 - int(math.sin(aR) * r)))

    def update(self):
        if self.value != self.lastV:
            self.draw()
            self.lastV = self.value
            return True

    def draw(self):
        surf = pygame.Surface((self.w, self.h))

        surf.blit(self.meter, (0, 0))

        r1 = 70.0
        r2 = 10.0

        aR = (140 - ((self.value / self.maxScale) * 107)) * (math.pi / 180.0)

        pygame.draw.aaline(surf, (43, 28, 18), 
            (72 + int(math.cos(aR) * (r1*1.05)), 92 - int(math.sin(aR) * r1)),
            (72 + int(math.cos(aR) * (r2*1.05)), 92 - int(math.sin(aR) * r2)),
        )

        self.display.blit(surf, (self.x, self.y))

class Button(Widget):
    def __init__(self, text, x, y, w, h, callback=None):
        Widget.__init__(self, x, y, w, h)
        self.text = text
        self.callback = callback

    def draw(self):
        btText = self.display.font.render(self.text, True, Colours.white)
        
        pygame.draw.rect(self.display.display, Colours.white, (self.x, self.y, self.w, self.h), 2)

        self.display.blit(btText, (self.x+15, self.y+12))

    def touched(self):
        pygame.draw.rect(self.surf, Colours.black, 
            (self.x, self.y, self.w, self.h), 2)
        self.display.flip()
        if self.callback:
            self.callback()
