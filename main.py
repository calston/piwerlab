#!/usr/bin/env python
import time
import serial

import pygame

from pygame.locals import *
from ui import widgets, surface
import psu

import random

class ConfigScreen(object):
    def __init__(self, display, psu, channel, parent):
        self.display = display
        self.channel = channel
        self.parent = parent
        self.psu = psu
        self.active = False

        self.configScreen = widgets.Pannel(display)
        self.configScreen.addWidget(widgets.Frame, "Voltage", 1, 1, 130, 155)
        self.configScreen.addWidget(widgets.SevenSegment, 10, 50, 120, 60, digits=4, colour=widgets.Colours.electric_blue)
        self.configScreen.addWidget(widgets.UpButton, 19, 26, 20, 20)
        self.configScreen.addWidget(widgets.UpButton, 57, 26, 20, 20)
        self.configScreen.addWidget(widgets.UpButton, 98, 26, 20, 20)
        self.configScreen.addWidget(widgets.DownButton, 19, 113, 20, 20)
        self.configScreen.addWidget(widgets.DownButton, 57, 113, 20, 20)
        self.configScreen.addWidget(widgets.DownButton, 98, 113, 20, 20)

    def activate(self):
        self.active = True
        self.display.clear()
        self.configScreen.draw()
        self.mainLoop()

    def mainLoop(self):
        while self.active:
            self.configScreen.update()

            self.parent.clock.tick(40)

            for event in pygame.event.get():
                if event.type in (QUIT, KEYDOWN):
                    self.active = False

                self.configScreen.sendEvent(event)
        self.parent.activate()

class PowerSupply(object):
    def __init__(self, display, ser):
        self.display = display
        self.psu = psu.PSU(ser)
        self.maxV = 16

        self.mainScreen = widgets.Pannel(display)
        self.configScreen1 = ConfigScreen(display, psu, 1, self)
        self.configScreen2 = ConfigScreen(display, psu, 2, self)

        self.screen = self.mainScreen

        # Channel 1
        ch1 = self.mainScreen.addWidget(widgets.Frame, "Channel 1", 1, 1, 220, 110)
        self.posv = ch1.addWidget(widgets.FancyGauge,
            1, 3, 40,
            units="Volts",
            colour=widgets.Colours.electric_blue,
            valueFormat="%.2f",
            maxScale=self.maxV
        )
        self.posc = ch1.addWidget(widgets.FancyGauge,
            85, 3, 40,
            units="Amps",
            colour=widgets.Colours.electric_blue,
            valueFormat="%.2f",
            maxScale=self.maxV
        )
        self.mainScreen.addWidget(widgets.Button, "Setup", 175, 70, 40, 30,
                                  callback=self.btnConfig1)

        # Channel 2
        self.mainScreen.addWidget(widgets.Frame, "Channel 2", 1, 120, 220, 110)
        self.negv = self.mainScreen.addWidget(widgets.FancyGauge,
            5, 145, 40,
            units="Volts",
            colour=widgets.Colours.electric_blue,
            valueFormat="-%.2f",
            maxScale=self.maxV
        )
        self.negc = self.mainScreen.addWidget(widgets.FancyGauge,
            90, 145, 40,
            units="Amps",
            colour=widgets.Colours.electric_blue,
            valueFormat="%.2f",
            maxScale=self.maxV
        )
        self.mainScreen.addWidget(widgets.Button, "Setup", 175, 190, 40, 30,
                                  callback=self.btnConfig2)

        # PDU frame
        self.mainScreen.addWidget(widgets.Frame, "PDU", 225, 1, 90, 110)

        # Toggle buttons 
        self.toggle_widgets = [
            self.mainScreen.addWidget(widgets.ToggleButton,
                "On", "Off", 175, 30, 40, 30, callback=self.btnEn1),
            self.mainScreen.addWidget(widgets.ToggleButton,
                "On", "Off", 175, 150, 40, 30, callback=self.btnEn2),
            self.mainScreen.addWidget(widgets.ToggleButton,
                "AC 1", "AC 1", 235, 30, 30, 30, callback=self.btnAc1),
            self.mainScreen.addWidget(widgets.ToggleButton,
                "AC 2", "AC 2", 275, 30, 30, 30, callback=self.btnAc2),
            self.mainScreen.addWidget(widgets.ToggleButton,
                "AC 3", "AC 3", 235, 70, 30, 30, callback=self.btnAc3),
            self.mainScreen.addWidget(widgets.ToggleButton,
                "AC 4", "AC 4", 275, 70, 30, 30, callback=self.btnAc4),
        ]

        self.clock = pygame.time.Clock()
        self.c = time.time()
        self.long_c = time.time()
        self.active = False

        self.activate()

    def activate(self):
        self.display.clear()
        self.mainScreen.draw()
        if not self.active:
            self.active = True
            self.mainLoop()

    def btnConfig1(self):
        self.configScreen1.activate()

    def btnConfig2(self):
        pass

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
        self.psu.tick()

    def slowTick(self):
        self.psu.updateState()
        self.posv.value = self.psu.voltageP/1000.0
        self.negv.value = -1*(self.psu.voltageN/1000.0)

        q = False

        for i, w in enumerate(self.toggle_widgets):
            q = q or w.setState(self.psu.state_ar[i])

        if q:
            self.mainScreen.display.flip()

    def mainLoop(self):
        while self.active:
            self.mainScreen.update()

            if (time.time() - self.c > 0.1):
                self.c = time.time()
                self.tick()

            if (time.time() - self.long_c > 0.5):
                self.long_c = time.time()
                self.slowTick()

            self.clock.tick(40)

            for event in pygame.event.get():
                if event.type in (QUIT, KEYDOWN):
                    self.active = False

                self.mainScreen.sendEvent(event)

if __name__ == '__main__': 
    ser = serial.Serial('/dev/serial0', 9600)
    #ser = psu.FakePSU(None, None)
    mypsu = PowerSupply(surface.TouchScreen(), ser)
    #mypsu = PowerSupply(surface.Dev(), ser)
    mypsu.activate()
