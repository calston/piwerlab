#!/usr/bin/env python
import time

import pygame

from pygame.locals import *
from ui import widgets, surface

display = surface.Dev()
#display.splash()

mainScreen = widgets.Pannel(display)
#mainScreen.addWidget(widgets.Button, "test", 10, 10, 100, 100, )
#meter = mainScreen.addWidget(widgets.Meter, 10, 10)
m2 = mainScreen.addWidget(widgets.SevenSegment, 1, 1, 300, 70, colour=widgets.Colours.green, digits=5)
m3 = mainScreen.addWidget(widgets.FancyGauge, 1, 70, 50, units="Volts", maxScale=999)
mainScreen.draw()

clock = pygame.time.Clock()


def main():
    running = True
    cnt = 100
    c = time.time()
    while running:
        mainScreen.update()

        if (time.time() - c > .01):
            c = time.time()
            cnt += 0.5
            if cnt > 999:
                cnt = 0
            m2.value = cnt
            m3.value = cnt

        clock.tick(40)

        for event in pygame.event.get():
            if event.type in (QUIT, KEYDOWN):
                running = False

            mainScreen.sendEvent(event)

if __name__ == '__main__': 
    main()

