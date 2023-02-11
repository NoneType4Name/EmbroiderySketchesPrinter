import os
import sys
import numpy
import pygame
import psutil
import win32ui
import win32api
import win32print
import win32process
from constants import *
from screeninfo import get_monitors
from PIL import Image, ImageWin, ImageDraw

pygame.init()


class DATA:
    """
    Custom dictionary.
    """
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return DATA(value) if isinstance(value, dict) else value

    def __repr__(self):
        return '{%s}' % str(', '.join("'%s': %s" % (k, repr(v)) for (k, v) in self.__dict__.items()))


class SIZE(tuple):
    def __init__(self, data):
        super().__init__()
        self.w, self.h = map(int, data)


# FULL_SIZE = SIZE((get_monitors()[0].width, get_monitors()[0].height))
FULL_SIZE = SIZE((win32api.GetSystemMetrics(16), win32api.GetSystemMetrics(17)))


def getFileProperties(name: str) -> DATA:
    """
    Read all properties of the given file return them as a DATA.
    """
    propNames = ('Comments', 'InternalName', 'ProductName',
                 'CompanyName', 'LegalCopyright', 'ProductVersion',
                 'FileDescription', 'LegalTrademarks', 'PrivateBuild',
                 'FileVersion', 'OriginalFilename', 'SpecialBuild')

    props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

    try:
        fixedInfo = win32api.GetFileVersionInfo(name, '\\')
        props['FixedFileInfo'] = fixedInfo
        props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
                                                fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
                                                fixedInfo['FileVersionLS'] % 65536)
        strInfo = {}
        for propName in propNames:
            strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (*win32api.GetFileVersionInfo(name, '\\VarFileInfo\\Translation')[0], propName)
            strInfo[propName] = win32api.GetFileVersionInfo(name, strInfoPath)

        props['StringFileInfo'] = strInfo
    except Exception:
        pass
    return DATA(props)


class Printer:
    def __init__(self, printer_name:str):
        self._print_image = None
        self._hDC = win32ui.CreateDC()
        self._hDC.CreatePrinterDC(printer_name)
        self.printable_area = self._hDC.GetDeviceCaps(HORZRES), self._hDC.GetDeviceCaps(VERTRES)
        self.printer_size = self._hDC.GetDeviceCaps(PHYSICALWIDTH), self._hDC.GetDeviceCaps(PHYSICALHEIGHT)
        self.printer_dpi = self._hDC.GetDeviceCaps(LOGPIXELSX)

    def mmTOpx(self, mm: int) -> int:
        """

        mm:     millimeters :   int
        Return: pixels      :   int
        """
        return round((mm * self.printer_dpi) / 25.4)

    def newTask(self, image, task_name):
        if type(image) is str:
            self._print_image = Image.open(image)
        elif type(image) is Image.Image:
            self._print_image = image
        else:
            raise TypeError(f'Unsupported type for image (type: {type(image)}')

        self._print_image.rotate(90 if self._print_image.size[0] > self._print_image.size[1] else 0)
        self._hDC.StartDoc(task_name)
        self._hDC.StartPage()
        ImageWin.Dib(self._print_image).draw(self._hDC.GetHandleOutput(), (0, 0, *self.printable_area))
        self._hDC.EndPage()
        self._hDC.EndDoc()
        self._print_image = None

    def close(self):
        self._hDC.DeleteDC()


def get_pid_by_hwnd(hwnd: int) -> int:
    """

    hwnd:   HWND (int)
    Return: PID
    """
    return win32process.GetWindowThreadProcessId(hwnd)[1]


def GetPrintersList() -> tuple:
    """

    Return tuple of name all available printers.
    """
    return tuple(i[2] for i in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS))


def GetDefaultPrinter() -> str:
    """

    Return string of name default printer.
    """
    return win32print.GetDefaultPrinter()
