import math
import os
import sys
import time
import numpy
import pygame
import random
import psutil
import string
import win32ui
import win32api
import win32print
import win32process

import GUI
from constants import *
from screeninfo import get_monitors
from PIL import Image, ImageWin, ImageDraw, ImageFont

PUNCTUATION = string.punctuation + ' '
ESCAPE_CHARS = '\n\a\b\f\r\t\v\x00'
ESCAPE_CHARS_TRANSLATER = str.maketrans(dict.fromkeys(list(ESCAPE_CHARS), None))

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
FULL_SIZE = SIZE((win32api.GetSystemMetrics(16) + 2, win32api.GetSystemMetrics(17) + 2))


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
            strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (
            *win32api.GetFileVersionInfo(name, '\\VarFileInfo\\Translation')[0], propName)
            strInfo[propName] = win32api.GetFileVersionInfo(name, strInfoPath)

        props['StringFileInfo'] = strInfo
    except Exception:
        pass
    return DATA(props)


class Printer:
    def __init__(self, printer_name: str):
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
    return tuple(
        i[2] for i in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS))


def GetDefaultPrinter() -> str:
    """

    Return string of name default printer.
    """
    return win32print.GetDefaultPrinter()


def make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = pascal_row(n - 1)

    def bezier(ts):
        result = []
        for t in ts:
            tpowers = (t ** i for i in range(n))
            upowers = reversed([(1 - t) ** i for i in range(n)])
            coefs = [c * a * b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef * p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result

    return bezier


def pascal_row(n):
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n // 2 + 1):
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n & 1 == 0:
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    return result


def GetCommonPoints(points1, points2: (float, float)):
    c = []
    for i in range(len(points1)-1):
        x1y1, x2y2 = points1[i], points1[i+1]
        x3y3, x4y4 = points2
        try:
            x = ((x1y1[0]*x2y2[1]-x1y1[1]*x2y2[0])*(x3y3[0]-x4y4[0])-(x1y1[0]-x2y2[0])*(x3y3[0]*x4y4[1]-x3y3[1]*x4y4[0]) ) / ( (x1y1[0]-x2y2[0])*(x3y3[1]-x4y4[1])-(x1y1[1]-x2y2[1])*(x3y3[0]-x4y4[0]) )
            y = ((x1y1[0]*x2y2[1]-x1y1[1]*x2y2[0])*(x3y3[1]-x4y4[1])-(x1y1[1]-x2y2[1])*(x3y3[0]*x4y4[1]-x3y3[1]*x4y4[0]) ) / ( (x1y1[0]-x2y2[0])*(x3y3[1]-x4y4[1])-(x1y1[1]-x2y2[1])*(x3y3[0]-x4y4[0]) )
            c.append((x, y))
        except ZeroDivisionError:
            pass
    return sorted(c)


# 'Основание груди', 'Обхват талии', 'Обхват низа корсета', 'Высота основания груди', 'Высота бока вверх', 'Высота бока вниз', 'Утяжка'

class DrawSketch:
    def __init__(self, OG, OT, ONK, VOG, VBU, VBD, Y, printer: Printer):
        self.VOG = VOG+10
        self.OG = OG
        self.OT = OT
        self.ONK = ONK
        self.VOG = VOG
        self.VBU = VBU
        self.VBD = VBD
        self.Y = Y
        self.printer = printer
        self.billetW = 142
        self.billetH = 85
        self.billetDifferential = 17
        self.upper_padding = 18
        self.techno_padding = 10
        self.font = ImageFont.truetype(DATAS_FOLDER_NAME+'/font.ttf', 256)

    def FirstElement(self):
        image = Image.new('L', (self.printer.mmTOpx((self.OG / 4 + 0.5) / 3 + self.techno_padding*2), self.printer.mmTOpx(self.billetH + self.VOG + self.VBD + self.techno_padding*2)), 255)
        sketch = ImageDraw.Draw(image)

        sketch.line(((0, 0), (0, self.printer.mmTOpx(self.billetH + self.VOG + self.VBD + self.techno_padding*2))), 0, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding)), (self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG + self.VBD))),0, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx((self.OG / 4 + 0.5) / 3 + self.techno_padding*2), 0), (self.printer.mmTOpx((self.OG / 4 + 0.5) / 3 + self.techno_padding*2), self.printer.mmTOpx(self.techno_padding * 2 + self.billetH + self.VOG + self.VBD))), 0, self.printer.mmTOpx(1))

        sketch.line(((self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding)), (self.printer.mmTOpx(self.techno_padding + 10), self.printer.mmTOpx(self.techno_padding))), 0,
                    self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(0), self.printer.mmTOpx(0)), (self.printer.mmTOpx(self.techno_padding*2 + 10), self.printer.mmTOpx(0))), 0,
                    self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding + 10), self.printer.mmTOpx(self.techno_padding)), (self.printer.mmTOpx(self.techno_padding + 10), self.printer.mmTOpx(self.techno_padding + 5))),
                    0, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding*2+10), self.printer.mmTOpx(0)), (self.printer.mmTOpx(self.techno_padding*2+ 10), self.printer.mmTOpx(5))), 0, self.printer.mmTOpx(1))

        w_exemplar = 100
        h_exemplar = 62
        ts = [t / 100.0 for t in range(101)]
        x, y = self.printer.mmTOpx(self.techno_padding + 10), self.printer.mmTOpx(self.techno_padding - self.billetDifferential + 5)
        bezier = make_bezier(tuple(map(lambda cord: (cord[0] * (self.printer.mmTOpx(self.billetW)/w_exemplar) + x, cord[1] * (self.printer.mmTOpx(self.billetH)/h_exemplar) + y), ((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))))
        points = bezier(ts)

        xy = [(self.printer.mmTOpx((self.OG / 4 + 0.5) / 3 + self.techno_padding), self.printer.mmTOpx(self.billetH - self.billetDifferential + self.techno_padding)),
              (self.printer.mmTOpx((self.OG / 4 + 0.5) / 3 + self.techno_padding), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG + self.VBD))]
        tg = 20 / self.VOG
        xy = GetCommonPoints(points, xy)[0], (
        self.printer.mmTOpx((self.OG / 4 + 0.5) / 3 + self.techno_padding - tg * (self.VOG + self.VBD)), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG + self.VBD))
        sketch.line(xy, 0, self.printer.mmTOpx(1))
        points_new = [(GetCommonPoints((points[i], points[i + 1]), xy)[0]) for i in range(len(points) - 1)]
        sketch.line(points[:points_new.index(sorted(points_new)[-1]) + 2], 0, self.printer.mmTOpx(1))
        _xy = list(xy[0])
        _xy = (_xy[0] + self.printer.mmTOpx(self.techno_padding), _xy[1] - self.printer.mmTOpx(self.techno_padding)), (self.printer.mmTOpx((self.OG / 4 + 0.5) / 3 + self.techno_padding - tg * (self.VOG + self.VBD) + self.techno_padding), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG + self.VBD + self.techno_padding))
        sketch.line(_xy, 0, self.printer.mmTOpx(1))

        x, y = self.printer.mmTOpx(self.techno_padding*2+10), self.printer.mmTOpx(-self.billetDifferential + 5)
        bezier = make_bezier([*map(lambda cord: (cord[0] * (self.printer.mmTOpx(self.billetW)/w_exemplar) + x, cord[1] * (self.printer.mmTOpx(self.billetH)/h_exemplar) + y), ((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))])
        points = bezier(ts)
        sketch.line(points, 0, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG + self.VBD)), (self.printer.mmTOpx((self.OG / 4 + 0.5) / 3 + self.techno_padding - tg * (self.VOG + self.VBD)), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG + self.VBD))), 0,self.printer.mmTOpx(1))
        sketch.line((0, self.printer.mmTOpx(self.billetH + self.VOG + self.VBD + self.techno_padding*2), (self.printer.mmTOpx((self.OG / 4 + 0.5) / 3 + self.techno_padding*2 - tg * (self.VOG + self.VBD)), self.printer.mmTOpx(self.techno_padding*2 + self.billetH + self.VOG + self.VBD))), 0, self.printer.mmTOpx(1))

        line_xy = [(self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG)), (self.printer.mmTOpx((self.OG / 4 + 0.5) / 3 + self.techno_padding*2), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG))]
        line_xy[1] = GetCommonPoints(xy, line_xy)[0]
        sketch.line(tuple(line_xy), 0, self.printer.mmTOpx(1))

        sketch.line(((self.printer.mmTOpx(self.techno_padding+self.billetW*0.15), self.printer.mmTOpx(self.techno_padding+self.billetH)), (self.printer.mmTOpx(self.techno_padding+self.billetW*0.15), self.printer.mmTOpx(self.techno_padding+self.billetH*1.5))), 0, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding+self.billetW*0.15-5), self.printer.mmTOpx(self.techno_padding+self.billetH*1.3)), (self.printer.mmTOpx(self.techno_padding+self.billetW*0.15), self.printer.mmTOpx(self.techno_padding+self.billetH*1.5)), (self.printer.mmTOpx(self.techno_padding+self.billetW*0.15+5), self.printer.mmTOpx(self.techno_padding+self.billetH*1.3))), 0, self.printer.mmTOpx(1))
        sketch.text((self.printer.mmTOpx(self.techno_padding+self.billetW*0.15+5), self.printer.mmTOpx(self.techno_padding+self.billetH*1.5)), 'I', 100, font=self.font)

        image.show()
        exit()


Sketch = DrawSketch(760, 640, 840, 120, 220, 120, 5, Printer(GetDefaultPrinter()))
Sketch.FirstElement()

# W, H = printer.mmTOpx(OG*0.5), printer.mmTOpx(upper_padding+billetH+VOG+VBD)
# list_count = math.ceil(W/printer.mmTOpx(a4[0])), math.ceil(H/printer.mmTOpx(a4[1]))
# image =
# sketch = ImageDraw.Draw(image)
# sketch.line(((0, printer.mmTOpx(upper_padding+billetDifferencial)), (0, printer.mmTOpx(upper_padding+billetH+VOG+VBD))), 0, printer.mmTOpx(1))
# sketch.line(((0, printer.mmTOpx(upper_padding+billetH)), (printer.mmTOpx(OG/2), printer.mmTOpx(upper_padding+billetH))), 0, printer.mmTOpx(1))
# sketch.line(((0, printer.mmTOpx(upper_padding+billetH+VOG)), (printer.mmTOpx(OG/2), printer.mmTOpx(upper_padding+billetH+VOG))), 0, printer.mmTOpx(1))
#
# sketch.line(((printer.mmTOpx(OG*0.5), printer.mmTOpx(upper_padding)), (printer.mmTOpx(OG*0.5), printer.mmTOpx(upper_padding+billetH+VOG+VBD))), 0, printer.mmTOpx(1))
# sketch.line(((printer.mmTOpx(OG*0.5-25), printer.mmTOpx(upper_padding)), (printer.mmTOpx(OG*0.5-25), printer.mmTOpx(upper_padding+billetH+VOG+VBD))), 0, printer.mmTOpx(1))
# sketch.line(((printer.mmTOpx(OG*0.5-25-34), printer.mmTOpx(upper_padding)), (printer.mmTOpx(OG*0.5-25-34), printer.mmTOpx(upper_padding+billetH+VOG+VBD))), 0, printer.mmTOpx(1))
#
# sketch.line(((printer.mmTOpx((OG/4+5)/3), printer.mmTOpx(upper_padding+billetH)), printer.mmTOpx((OG/4+5)/3), printer.mmTOpx(upper_padding+billetH+VOG+VBD)), 0, printer.mmTOpx(1))
# sketch.line(((printer.mmTOpx((OG/4+5)/3*2), printer.mmTOpx(upper_padding+billetH)), printer.mmTOpx((OG/4+5)/3*2), printer.mmTOpx(upper_padding+billetH+VOG+VBD)), 0, printer.mmTOpx(1))
# sketch.line(((printer.mmTOpx((OG/4+5)), printer.mmTOpx((upper_padding+billetH)-(VBU-VOG))), printer.mmTOpx((OG/4+5)), printer.mmTOpx(upper_padding+billetH+VOG+VBD)), 0, printer.mmTOpx(1))
# sketch.line(((printer.mmTOpx((OG/4+5)+((OG/4-5-25-34)/2)), printer.mmTOpx(upper_padding+billetH)), printer.mmTOpx((OG/4+5)+((OG/4-5-25-34)/2)), printer.mmTOpx(upper_padding+billetH+VOG+VBD)), 0, printer.mmTOpx(1))
#
#
# sketch.line(((printer.mmTOpx((OG/4+5)+((OG/4-5)/3)), printer.mmTOpx(upper_padding+billetH)), printer.mmTOpx((OG/4+5)+((OG/4-5)/3)), printer.mmTOpx(upper_padding+billetH+VOG+VBD)), 0, printer.mmTOpx(1))
# sketch.line(((printer.mmTOpx((OG/4+5)+((OG/4-5)/3*2)), printer.mmTOpx(upper_padding+billetH)), printer.mmTOpx((OG/4+5)+((OG/4-5)/3*2)), printer.mmTOpx(upper_padding+billetH+VOG+VBD)), 0, printer.mmTOpx(1))
#
#
# sketch.line(((0, printer.mmTOpx(upper_padding+billetDifferencial)),(printer.mmTOpx(10), printer.mmTOpx(billetDifferencial+upper_padding))), 0, printer.mmTOpx(1))
# sketch.line(((printer.mmTOpx(10), printer.mmTOpx(upper_padding+billetDifferencial)), (printer.mmTOpx(10), printer.mmTOpx(upper_padding+billetDifferencial+5))), 0, printer.mmTOpx(1))
# a = (100, 62)
# w = printer.mmTOpx(billetW)
# h = printer.mmTOpx(billetH)
# at_x = w/a[0]
# at_y = h/a[1]
# ts = [t / 100.0 for t in range(101)]
# x, y = printer.mmTOpx(10), printer.mmTOpx(18)
# bezier = make_bezier([*map(lambda xy: (xy[0]*at_x + x, xy[1] * at_y + y), ((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))])
# points = bezier(ts)
# sketch.line(points, 0, printer.mmTOpx(1))
# sketch.line(((w+x, 0), (w+x, printer.mmTOpx(18))), 0, printer.mmTOpx(1))
# sketch.line(((w+x, 0), (w+x+printer.mmTOpx(5), 0)), 0, printer.mmTOpx(1))
# tg = 20/VOG
# xys1 = [(printer.mmTOpx((OG/4+5)/3+5), printer.mmTOpx(upper_padding+billetH-5/tg)),(printer.mmTOpx((OG/4+5)/3-(tg*(VOG+VBD))), printer.mmTOpx(upper_padding+billetH+VOG+VBD))]
# xys1[0] = GetCommonPoints(points, xys1)
# sketch.line(xys1, 0, printer.mmTOpx(1))
# xys2 = [(printer.mmTOpx((OG/4+5)/3*2+20), printer.mmTOpx(upper_padding+billetH-20/tg)),(printer.mmTOpx((OG/4+5)/3*2-(tg*(VOG+VBD))), printer.mmTOpx(upper_padding+billetH+VOG+VBD))]
# xys2[0] = GetCommonPoints(points, xys2)
# sketch.line(xys2, 0, printer.mmTOpx(1))
#
# a = (300, 70)
# w = printer.mmTOpx(300)
# h = printer.mmTOpx(70)
# at_x = w/a[0]
# at_y = h/a[1]
# x, y = printer.mmTOpx(billetW+10+5), 0
# xys = [*map(lambda xy: (xy[0]*at_x + x, xy[1] * at_y + y), ((0, 0), (165, 55), (300, 70)))]
# bezier = make_bezier(xys)
# points = bezier(ts)
# sketch.line(points, 0, printer.mmTOpx(1))
#
# image.show()
# # 215 -
# # 220 - 165 55 (300, 70)
# # 225 - 145 30 (300, 30)
#
# a = (300, 70)
# w = printer.mmTOpx(300)
# h = printer.mmTOpx(70)
# at_x = w/a[0]
# at_y = h/a[1]
# x, y = printer.mmTOpx(billetW+10+5), 0
# xys = [*map(lambda xy: (xy[0]*at_x + x, xy[1] * at_y + y), ((0, 0), (165, 55), (300, 70)))]
# bezier = make_bezier(xys)
# points = bezier(ts)
# sketch.line(points, 0, printer.mmTOpx(1))
#
# image.show()
# 215 -
# 220 - 165 55 (300, 70)
# 225 - 145 30 (300, 30)


# def mmtpx(mm):
#     return round((mm * 243) / 25.4)
#
#
# if __name__ == '__main__':
#     a = (300, 100)
#     w = printer.mmTOpx(300)
#     h = printer.mmTOpx(100)
#     at_x = w/a[0]
#     at_y = h/a[1]
#     im = Image.new('RGBA', (w, h), (255, 255, 255))
#     draw = ImageDraw.Draw(im)
#     ts = [t / 100.0 for t in range(101)]
#
#     xys = [(0, 0), (80, 50), (230, 90), (300, 100)]  line
    # xys = [*map(lambda xy: (xy[0]*at_x, xy[1] * at_y), ((0, 0), (80, 50), (230, 90), (300, 100)))]
    # bezier = make_bezier(xys)
    # points = bezier(ts)
    #
    # draw.line(points, fill='black', width=mmtpx(1))
    # im.show()
#