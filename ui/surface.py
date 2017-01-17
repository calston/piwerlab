import pygame, sys, os
from pygame.locals import *

class Display(object):
    def __init__(self):
        pygame.init()

        self.display = pygame.display.set_mode((320, 240), 0, 32)
        self.font = pygame.font.Font('carlito.ttf', 12)

    def splash(self):
        self.splash = pygame.image.load('images/pi_black_glow2.png').convert()

        self.blit(self.splash, (0,0))
        pygame.display.update()

    def blit(self, *a, **kw):
        self.display.blit(*a, **kw)

    def flip(self):
        pygame.display.flip()

class TouchScreen(Display):
    def __init__(self, fbdev='/dev/fb1', tsdev='/dev/input/touchscreen'):
        os.environ["SDL_FBDEV"] = fbdev
        os.environ["SDL_MOUSEDRV"] = "TSLIB"
        os.environ["SDL_MOUSEDEV"] = tsdev
        os.environ["TSLIB_CALIBFILE"] = "/etc/pointercal"
        os.environ["TSLIB_FBDEVICE"] = fbdev
        os.environ["TSLIB_TSDEVICE"] = tsdev

        Display.__init__(self)

        pygame.mouse.set_visible(0)

class Dev(Display):
    def __init__(self):
        Display.__init__(self)
