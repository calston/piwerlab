#!/usr/bin/env python
import time
import serial

import pygame

from pygame.locals import *
from ui import widgets, surface
from psu import PSU

import random

class PowerSupply(object):
    def __init__(self, display):
        self.display = display
        self.maxV = 16
        self.mainScreen = widgets.Pannel(display)

        self.psu = PSU(serial.Serial('/dev/serial0', 9600))

        self.mainScreen.addWidget(widgets.Frame, "Channel 1", 1, 1, 220, 110)
        self.posv = self.mainScreen.addWidget(widgets.FancyGauge, 5, 25, 40, units="Volts", colour=widgets.Colours.electric_blue, valueFormat="%.2f", maxScale=self.maxV)
        self.posc = self.mainScreen.addWidget(widgets.FancyGauge, 90, 25, 40, units="Amps", colour=widgets.Colours.electric_blue, valueFormat="%.2f", maxScale=self.maxV)
        self.en1  = self.mainScreen.addWidget(widgets.ToggleButton, "On", "Off", 180, 55, 30, 30, callback=self.btnEn1)

        self.mainScreen.addWidget(widgets.Frame, "Channel 2", 1, 120, 220, 110)
        self.negv = self.mainScreen.addWidget(widgets.FancyGauge, 5, 145, 40, units="Volts", colour=widgets.Colours.electric_blue, valueFormat="-%.2f", maxScale=self.maxV)
        self.negc = self.mainScreen.addWidget(widgets.FancyGauge, 90, 145, 40, units="Amps", colour=widgets.Colours.electric_blue, valueFormat="%.2f", maxScale=self.maxV)
        self.en2  = self.mainScreen.addWidget(widgets.ToggleButton, "On", "Off", 180, 175, 30, 30, callback=self.btnEn2)

        self.mainScreen.addWidget(widgets.Frame, "PDU", 225, 1, 90, 110)
        self.ac1  = self.mainScreen.addWidget(widgets.ToggleButton, "AC 1", "AC 1", 235, 30, 30, 30, callback=self.btnAc1)
        self.ac2  = self.mainScreen.addWidget(widgets.ToggleButton, "AC 2", "AC 2", 275, 30, 30, 30, callback=self.btnAc2)
        self.ac3  = self.mainScreen.addWidget(widgets.ToggleButton, "AC 3", "AC 3", 235, 70, 30, 30, callback=self.btnAc3)
        self.ac4  = self.mainScreen.addWidget(widgets.ToggleButton, "AC 4", "AC 4", 275, 70, 30, 30, callback=self.btnAc4)

        self.mainScreen.draw()

        self.clock = pygame.time.Clock()

        self.cnt = 1
        self.c = time.time()
        self.spinTo = random.random() * self.maxV
        self.dir = 0.1

    def btnEn1(self, state):
        if state:
            self.psu.outputEnable(1)
        else:
            self.psu.outputDisable(1)

    def btnEn2(self, state):
        if state:
            self.psu.outputEnable(2)
        else:
            self.psu.outputDisable(2)

    def btnAc1(self, state):
        if state:
            self.psu.acEnable(1)
        else:
            self.psu.acDisable(1)

    def btnAc2(self, state):
        if state:
            self.psu.acEnable(2)
        else:
            self.psu.acDisable(2)

    def btnAc3(self, state):
        if state:
            self.psu.acEnable(3)
        else:
            self.psu.acDisable(3)

    def btnAc4(self, state):
        if state:
            self.psu.acEnable(4)
        else:
            self.psu.acDisable(4)

    def tick(self):
        self.cnt = self.cnt + self.dir
        if ((self.cnt >= self.spinTo) and (self.dir > 0)) or ((self.dir < 0) and (self.cnt <= self.spinTo)):
            self.spinTo = random.random() * self.maxV
            if self.cnt > self.spinTo:
                self.dir = -0.1
            else:
                self.dir = 0.1

        self.posv.value = self.cnt
        self.negv.value = self.cnt

    def mainLoop(self):
        self.running = True
        while self.running:
            self.mainScreen.update()

            if (time.time() - self.c > 0.01):
                self.c = time.time()

                self.tick()

            self.clock.tick(40)

            for event in pygame.event.get():
                if event.type in (QUIT, KEYDOWN):
                    self.running = False

                self.mainScreen.sendEvent(event)

if __name__ == '__main__': 
    mypsu = PowerSupply(surface.TouchScreen())
    mypsu.mainLoop()

