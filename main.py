#!/usr/bin/env python
import time

import pygame

from pygame.locals import *
from ui import widgets, surface

import random

display = surface.Dev()
#display.splash()

maxV = 31

mainScreen = widgets.Pannel(display)
#mainScreen.addWidget(widgets.Button, "test", 10, 10, 100, 100, )
m1 = mainScreen.addWidget(widgets.OldSchoolMeter, 100, 1, maxScale=maxV)
m2 = mainScreen.addWidget(widgets.SevenSegment, 1, 1, 100, 70, colour=widgets.Colours.green, digits=2)
m3 = mainScreen.addWidget(widgets.FancyGauge, 1, 70, 50, units="Volts", maxScale=maxV)
mainScreen.draw()

clock = pygame.time.Clock()



def main():
    running = True
    cnt = 1
    c = time.time()
    spinTo = random.random() * maxV
    dir = 0.1
    while running:
        mainScreen.update()

        if (time.time() - c > 0.01):
            c = time.time()

            cnt = cnt + dir
            if ((cnt >= spinTo) and (dir > 0)) or ((dir < 0) and (cnt <= spinTo)):
                spinTo = random.random() * maxV
                if cnt > spinTo:
                    dir = -0.1
                else:
                    dir = 0.1

            m2.value = cnt
            m3.value = cnt
            m1.value = cnt

        clock.tick(40)

        for event in pygame.event.get():
            if event.type in (QUIT, KEYDOWN):
                running = False

            mainScreen.sendEvent(event)

if __name__ == '__main__': 
    main()

