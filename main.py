#!/usr/bin/env python
import time
import serial

import pygame

from pygame.locals import *
from ui import widgets, surface
import psu

import random

class ConfigScreen(object):
    def __init__(self, display, psu, channel, parent, negative=False):
        self.display = display
        self.channel = channel
        self.parent = parent
        self.psu = psu
        self.active = False
        self.negative = negative

        self.configScreen = widgets.Pannel(display)

        frame = self.configScreen.addWidget(widgets.Frame,
            "Voltage", 2, 2, 150, 155)
        self.vdisp = frame.addWidget(widgets.SevenSegment, 5, 37, 143, 60,
            digits=3, msd=2, colour=widgets.Colours.electric_blue)
        
        bw = 28
        frame.addWidget(widgets.UpButton, 59, 4, bw, bw, self.setVDisp(1),
            colour=widgets.Colours.electric_blue)
        frame.addWidget(widgets.UpButton, 106, 4, bw, bw, self.setVDisp(0.1),
            colour=widgets.Colours.electric_blue)
        frame.addWidget(widgets.DownButton, 59, 100, bw, bw, self.setVDisp(-1),
            colour=widgets.Colours.electric_blue)
        frame.addWidget(widgets.DownButton, 106, 100, bw, bw, self.setVDisp(-0.1),
            colour=widgets.Colours.electric_blue)

        cframe = self.configScreen.addWidget(widgets.Frame,
            "Current", 162, 2, 150, 155)
        self.cdisp = cframe.addWidget(widgets.SevenSegment, 5, 37, 143, 60,
            digits=3, msd=1, colour=widgets.Colours.electric_blue)

        cframe.addWidget(widgets.UpButton, 12, 4, bw, bw, self.setCDisp(1),
            colour=widgets.Colours.electric_blue)
        cframe.addWidget(widgets.UpButton, 59, 4, bw, bw, self.setCDisp(0.1),
            colour=widgets.Colours.electric_blue)
        cframe.addWidget(widgets.UpButton, 106, 4, bw, bw, self.setCDisp(0.01),
            colour=widgets.Colours.electric_blue)

        cframe.addWidget(widgets.DownButton, 12, 100, bw, bw, self.setCDisp(-1),
            colour=widgets.Colours.electric_blue)
        cframe.addWidget(widgets.DownButton, 59, 100, bw, bw, self.setCDisp(-0.1),
            colour=widgets.Colours.electric_blue)
        cframe.addWidget(widgets.DownButton, 106, 100, bw, bw, self.setCDisp(-0.01),
            colour=widgets.Colours.electric_blue)

        self.configScreen.addWidget(widgets.Button, "Save", 140, 190, 80, 40, self.save)
        self.configScreen.addWidget(widgets.Button, "Cancel", 230, 190, 80, 40, self.cancel)

    def setMax(self, disp, inc, mx):
        disp.value += inc

        if disp.value > mx:
            disp.value = mx
        if disp.value < 0:
            disp.value = 0

    def save(self):
        self.psu.setCurrent(self.channel, int(self.cdisp.value*1000))
        self.psu.setVoltage(self.channel, int(self.vdisp.value*1000))
        self.active = False

    def cancel(self):
        self.active = False

    def setVDisp(self, inc):
        return lambda: self.setMax(self.vdisp, inc, 15) 

    def setCDisp(self, inc):
        return lambda: self.setMax(self.cdisp, inc, 1.5) 

    def activate(self):
        self.vdisp.value = self.psu.vset[self.channel - 1]/1000.0
        self.cdisp.value = self.psu.cset[self.channel - 1]/1000.0
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
        self.configScreen1 = ConfigScreen(display, self.psu, 1, self)
        self.configScreen2 = ConfigScreen(display, self.psu, 2, self, True)

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
        ch1.addWidget(widgets.Button, "Setup", 172, 52, 40, 30,
                        callback=self.btnConfig1)

        # Channel 2
        ch2 = self.mainScreen.addWidget(widgets.Frame, "Channel 2", 1, 120, 220, 110)
        self.negv = ch2.addWidget(widgets.FancyGauge,
            1, 3, 40,
            units="Volts",
            colour=widgets.Colours.electric_blue,
            valueFormat="-%.2f",
            maxScale=self.maxV
        )
        self.negc = ch2.addWidget(widgets.FancyGauge,
            85, 3, 40,
            units="Amps",
            colour=widgets.Colours.electric_blue,
            valueFormat="%.2f",
            maxScale=self.maxV
        )
        ch2.addWidget(widgets.Button, "Setup", 172, 52, 40, 30,
                                  callback=self.btnConfig2)

        # PDU frame
        pdu = self.mainScreen.addWidget(widgets.Frame, "PDU", 225, 1, 90, 110)

        # Toggle buttons 
        self.toggle_widgets = [
            ch1.addWidget(widgets.ToggleButton,
                "On", "Off", 172, 10, 40, 30, callback=self.btnEn1),
            ch2.addWidget(widgets.ToggleButton,
                "On", "Off", 172, 10, 40, 30, callback=self.btnEn2),
            pdu.addWidget(widgets.ToggleButton,
                "AC 1", "AC 1", 10, 10, 30, 30, callback=self.btnAc1),
            pdu.addWidget(widgets.ToggleButton,
                "AC 2", "AC 2", 50, 10, 30, 30, callback=self.btnAc2),
            pdu.addWidget(widgets.ToggleButton,
                "AC 3", "AC 3", 10, 50, 30, 30, callback=self.btnAc3),
            pdu.addWidget(widgets.ToggleButton,
                "AC 4", "AC 4", 50, 50, 30, 30, callback=self.btnAc4),
        ]

        self.clock = pygame.time.Clock()
        self.c = time.time()
        self.long_c = time.time()
        self.active = False

        self.ncvals = []
        self.pcvals = []

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
        self.configScreen2.activate()

    def btnEn1(self, state):
        if not state:
            self.psu.outputEnable(1)
        else:
            self.psu.outputDisable(1)

    def btnEn2(self, state):
        if not state:
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
        if self.psu.currentP >= 0:
            self.pcvals.append(self.psu.currentP/1000.0)
            self.posc.value = max(self.pcvals)
            if len(self.pcvals) > 5:
                self.pcvals.pop(0)
        
        self.negv.value = -1*(self.psu.voltageN/1000.0)

        if self.psu.currentN >= 0:
            self.ncvals.append(self.psu.currentN/1000.0)
            self.negc.value = max(self.ncvals)
            if len(self.ncvals) > 5:
                self.ncvals.pop(0)

        q = False

        for i, w in enumerate(self.toggle_widgets):
            q = q or w.setState(self.psu.state_ar[i])

        if q:
            self.mainScreen.display.flip()

    def mainLoop(self):
        while self.active:
            self.mainScreen.update()

            if (time.time() - self.c > 0.02):
                self.c = time.time()
                self.tick()

            if (time.time() - self.long_c > 0.3):
                self.long_c = time.time()
                self.slowTick()

            self.clock.tick(40)

            for event in pygame.event.get():
                if event.type in (QUIT, KEYDOWN):
                    self.active = False

                self.mainScreen.sendEvent(event)

if __name__ == '__main__': 
    ser = serial.Serial('/dev/serial0', 57600)
    #ser = psu.FakePSU(None, None)
    mypsu = PowerSupply(surface.TouchScreen(), ser)
    #mypsu = PowerSupply(surface.Dev(), ser)
    mypsu.activate()
