import numpy
import pygame
import win32print
from screeninfo import get_monitors

pygame.init()
FULL_SIZE = (get_monitors()[0].width, get_monitors()[0].height)

DPI = 600


def MillimetersToPixels(mm):
    return round((mm * DPI) / 25.4)


def GetPrintersList():
    return tuple(i[2] for i in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS))


def GetDefaultPrinter():
    return win32print.GetDefaultPrinter()

