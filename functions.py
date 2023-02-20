import ctypes
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
        if printer_name != 'monitorHDC':
            self._hDC = win32ui.CreateDC()
            self._hDC.CreatePrinterDC(printer_name)
            self.printable_area = self._hDC.GetDeviceCaps(HORZRES), self._hDC.GetDeviceCaps(VERTRES)
            self.printer_size = self._hDC.GetDeviceCaps(PHYSICALWIDTH), self._hDC.GetDeviceCaps(PHYSICALHEIGHT)
            self.printer_dpi = self._hDC.GetDeviceCaps(LOGPIXELSX)
        else:
            self._hDC = None
            self.printable_area = FULL_SIZE
            self.printer_size = FULL_SIZE
            self.printer_dpi = ctypes.windll.user32.GetDpiForSystem()
        self.HORIZONTAL = True if self.printable_area[0] > self.printable_area[1] else False
        self.glue_padding = self.mmTOpx(3)

    def mmTOpx(self, mm: int) -> int:
        """

        mm:     millimeters :   int
        Return: pixels      :   int
        """
        return round((mm * self.printer_dpi) / 25.4)

    def NewSketch(self, sketches, sketches_padding=1):
        all_images = []
        remainderLastSketchW = 0

        sketches = [Image.open(s) if s is str else s for s in sketches if type(s) in (str, Image.Image)] if not all(s is Image.Image for s in sketches) else sketches
        # list_count_w = math.ceil((math.ceil(sum(s.size[0] for s in sketches) / self.printable_area[0]) * 2 * self.glue_padding + sum(s.size[0] for s in sketches))/self.printable_area[0])
        w = self.printable_area[0] - self.glue_padding
        images_h = []
        for sketch in sketches:
            while w > 0:  # unlimited sketches while W list is not < 0
                sketch_h = sketch.size[1]
                list_by_h = 0
                while sketch_h > 0:
                    if not len(images_h) or len(images_h) - 1 < list_by_h:
                        images_h.append(Image.new('L', self.printable_area, 255))
                        ImageDraw.Draw(images_h[list_by_h]).rectangle((-self.glue_padding, -self.glue_padding, *self.printable_area), 255, 100, self.glue_padding)
                    i = sketch.crop((remainderLastSketchW, sketch.size[1] - sketch_h,
                                     sketch.size[0] if sketch.size[0] <= w else w,
                                     sketch.size[1] if sketch_h < self.printable_area[1] - self.glue_padding else self.printable_area[1] - self.glue_padding))
                    images_h[list_by_h].paste(i, ((self.printable_area[0] - self.glue_padding) - w, 0), mask=i.split()[3])
                    sketch_h -= self.printable_area[0] - self.glue_padding
                    list_by_h += 1
                w -= sketch.size[0] - remainderLastSketchW if remainderLastSketchW else sketch.size[0] + self.mmTOpx(sketches_padding)
                remainderLastSketchW = 0
            else:
                remainderLastSketchW = abs(w)
                w = self.printable_area[0] - self.glue_padding
                all_images += images_h
                images_h = []
        for n, im in enumerate(all_images):
            im.save(DATAS_FOLDER_NAME+'/'+str(n)+'.png')
        return all_images

    def newTask(self, image, task_name):
        if type(image) is str:
            self._print_image = Image.open(image)
        elif type(image) is Image.Image:
            self._print_image = image
        else:
            raise TypeError(f'Unsupported type for image (type: {type(image)})')

        self._print_image = self._print_image.rotate(90 if self._print_image.size[0] > self._print_image.size[1] and self.HORIZONTAL else 0, fillcolor=255)
        if self._hDC is not None:
            self._hDC.StartDoc(task_name)
            self._hDC.StartPage()
            ImageWin.Dib(self._print_image).draw(self._hDC.GetHandleOutput(), (0, 0, *image.size))
            self._hDC.EndPage()
            self._hDC.EndDoc()
        self._print_image = None

    def close(self):
        if self._hDC is not None:
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
    return sorted(c, key=lambda v: v[1])


def GetCommonPointsForBezierCurve(points1, points2):
    for i in range(len(points1)-(1 if len(points1)-1 else 0)):
        x1, y1, x2, y2 = points1[i][0], points1[i][1], points1[i+1][0], points1[i+1][1]
        x3, y3, x4, y4 = points2[0][0], points2[0][1], points2[1][0], points2[1][1]
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        if x3 > x4:
            x3, x4 = x4, x3
            y3, y4 = y4, y3

        if y2 == y1 or x1 == x2:
            k1 = 0
        else:
            k1 = (y2 - y1) / (x2 - x1)

        if y3 == y4 or x4 == x3:
            k2 = 0
        else:
            k2 = (y4 - y3) / (x4 - x3)

        b1 = y1 - k1 * x1
        b2 = y3 - k2 * x3
        x = (b2 - b1) / (k1 - k2)
        y = k1*x+b1
        if x1 <= x <= x2 and y1 <= y <= y2:
            return x, y


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
        self.billetDifferential = 16
        self.upper_padding = 18
        self.techno_padding = 10
        self.font = ImageFont.truetype(DATAS_FOLDER_NAME+'/font.ttf', int(sum(self.printer.printable_area)/100))
        self.sketch_lines_color = (0, 0, 0)

    def Elements(self, elements: tuple):
        imgs = []
        if 1 in elements:
            imgs.append(self.FirstElement())
        if 2 in elements:
            imgs.append(self.SecondElement())
        if 3 in elements:
            imgs.append(self.ThirdElement())
        if 4 in elements:
            imgs.append(self.FourthElement())
        return imgs

    def FirstElement(self):
        image = Image.new('RGBA', (self.printer.mmTOpx((self.OG / 4 + 5) / 3 + self.techno_padding*2), self.printer.mmTOpx(self.billetH + self.VOG + self.VBD + self.techno_padding*2)), (0, 0, 0, 0))
        sketch = ImageDraw.Draw(image)

        sketch.line(((0, 0), (0, self.printer.mmTOpx(self.billetH + self.VOG + self.VBD + self.techno_padding*2))), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding)), (self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG + self.VBD))), self.sketch_lines_color, self.printer.mmTOpx(1))

        sketch.line(((self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding)), (self.printer.mmTOpx(self.techno_padding + 10), self.printer.mmTOpx(self.techno_padding))), self.sketch_lines_color,
                    self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(0), self.printer.mmTOpx(0)), (self.printer.mmTOpx(self.techno_padding*2+10), self.printer.mmTOpx(0))), self.sketch_lines_color,
                    self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding + 10), self.printer.mmTOpx(self.techno_padding)), (self.printer.mmTOpx(self.techno_padding + 10), self.printer.mmTOpx(self.techno_padding + 5))),
                    self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding*2+5*2), self.printer.mmTOpx(0)), (self.printer.mmTOpx(self.techno_padding*2+5*2), self.printer.mmTOpx(5))), self.sketch_lines_color, self.printer.mmTOpx(1))

        w_exemplar = 100
        h_exemplar = 62
        ts = [t / 100.0 for t in range(101)]
        x, y = self.printer.mmTOpx(self.techno_padding + 10), self.printer.mmTOpx(self.techno_padding - self.billetDifferential + 5)
        bezier = make_bezier(tuple(map(lambda cord: (cord[0] * (self.printer.mmTOpx(self.billetW)/w_exemplar) + x, cord[1] * (self.printer.mmTOpx(self.billetH)/h_exemplar) + y), ((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))))
        points = bezier(ts)

        tg = (20+(self.OG-(self.OT-self.Y))/2/3/2/2) / self.VOG
        xy = [(self.printer.mmTOpx((self.OG / 4 + 5) / 3 + self.techno_padding), self.printer.mmTOpx(self.billetH - self.billetDifferential + self.techno_padding)),
              (self.printer.mmTOpx((self.OG / 4 + 5) / 3 + self.techno_padding - tg * self.VOG), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG))]
        xy = max([i for i in GetCommonPoints(points, xy) if i[1] > 0]), (
        self.printer.mmTOpx((self.OG / 4 + 5) / 3 + self.techno_padding - tg * self.VOG), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG))

        sketch.line(xy, self.sketch_lines_color, self.printer.mmTOpx(1))

        curve_end = GetCommonPointsForBezierCurve(points, xy)
        sketch.line((*points[:points.index(min(points, key=lambda v: tuple(abs(numpy.array(v)-numpy.array(curve_end)))))], curve_end), self.sketch_lines_color, self.printer.mmTOpx(1))

        x, y = self.printer.mmTOpx(self.techno_padding*2+10), self.printer.mmTOpx(-self.billetDifferential + 5)
        bezier = make_bezier([*map(lambda cord: (cord[0] * (self.printer.mmTOpx(self.billetW) / w_exemplar) + x,
                                                 cord[1] * (self.printer.mmTOpx(self.billetH) / h_exemplar) + y),
                                   ((0, 12), (5, 70), (30, 65), (90, 80), (100, 0)))])
        points = bezier(ts)
        sketch.line(points, self.sketch_lines_color, self.printer.mmTOpx(1))
        _xy = list(xy[0])
        _xy = [(_xy[0] + self.printer.mmTOpx(self.techno_padding), _xy[1] - self.printer.mmTOpx(self.techno_padding)), (self.printer.mmTOpx((self.OG / 4 + 5) / 3 + self.techno_padding - tg * self.VOG + self.techno_padding), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG))]
        _xy[0] = GetCommonPointsForBezierCurve(points, _xy)
        sketch.line(_xy, self.sketch_lines_color, self.printer.mmTOpx(1))
        tg = 20 / self.VOG
        sketch.line(((_xy[1][0]-self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG)), (self.printer.mmTOpx((self.OG / 4 + 5) / 3 + self.techno_padding - tg * (self.VOG + self.VBD)), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG + self.VBD))), self.sketch_lines_color, self.printer.mmTOpx(1))

        sketch.line((_xy[1], (self.printer.mmTOpx((self.OG / 4 + 5) / 3 + self.techno_padding - tg * (self.VOG + self.VBD) + self.techno_padding), self.printer.mmTOpx(self.techno_padding * 2 + self.billetH + self.VOG + self.VBD))), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG + self.VBD)), (self.printer.mmTOpx((self.OG / 4 + 5) / 3 + self.techno_padding - tg * (self.VOG + self.VBD)), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG + self.VBD))), self.sketch_lines_color,self.printer.mmTOpx(1))
        sketch.line((0, self.printer.mmTOpx(self.billetH + self.VOG + self.VBD + self.techno_padding*2), (self.printer.mmTOpx((self.OG / 4 + 5) / 3 + self.techno_padding*2 - tg * (self.VOG + self.VBD)), self.printer.mmTOpx(self.techno_padding * 2 + self.billetH + self.VOG + self.VBD))), self.sketch_lines_color, self.printer.mmTOpx(1))

        line_xy = [(self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG)), (self.printer.mmTOpx((self.OG / 4 + 5) / 3 + self.techno_padding*2), self.printer.mmTOpx(self.techno_padding + self.billetH + self.VOG))]
        line_xy[1] = GetCommonPoints(xy, line_xy)[0]
        sketch.line(tuple(line_xy), self.sketch_lines_color, self.printer.mmTOpx(1))

        sketch.line((self.printer.mmTOpx(self.techno_padding+(self.OG / 4 + 5) / 3 * 0.3), self.printer.mmTOpx((self.billetH + self.VOG + self.techno_padding) * 0.5), self.printer.mmTOpx(self.techno_padding+(self.OG / 4 + 5) / 3 * 0.3), self.printer.mmTOpx((self.billetH + self.VOG + self.techno_padding) * 0.7)), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding+(self.OG / 4 + 5) / 3 * 0.2), self.printer.mmTOpx((self.billetH + self.VOG + self.techno_padding) * 0.6)),(self.printer.mmTOpx(self.techno_padding+(self.OG / 4 + 5) / 3 * 0.3), self.printer.mmTOpx((self.billetH + self.VOG + self.techno_padding) * 0.7)),(self.printer.mmTOpx(self.techno_padding+(self.OG / 4 + 5) / 3 * 0.4), self.printer.mmTOpx((self.billetH + self.VOG + self.techno_padding) * 0.60))), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.text((self.printer.mmTOpx(self.techno_padding+(self.OG / 4 + 5) / 3 * 0.3), self.printer.mmTOpx((self.billetH + self.VOG + self.techno_padding) * 0.7)), 'I', self.sketch_lines_color, font=self.font)
        return image

    def SecondElement(self):
        tg = 20 / self.VOG
        xy = [(self.printer.mmTOpx(tg*(self.VOG+self.VBD)), self.printer.mmTOpx(self.billetH)),
              (0, self.printer.mmTOpx(self.VOG+self.VBD+self.billetH))]
        w_exemplar = 100
        h_exemplar = 62
        ts = [t / 100.0 for t in range(101)]

        x, y = xy[0][0]-self.printer.mmTOpx((self.OG/4+5)/3-10), self.printer.mmTOpx(-self.billetDifferential)
        bezier = make_bezier(tuple(map(lambda cord: (
            cord[0] * (self.printer.mmTOpx(self.billetW)/w_exemplar) + x,
            cord[1] * (self.printer.mmTOpx(self.billetH)/h_exemplar) + y),((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))))
        points = bezier(ts)
        xy2 = [(self.printer.mmTOpx(tg*(self.VOG+self.VBD+self.billetH)+(self.OG/4+5)/3), 0),
               (self.printer.mmTOpx((self.OG/4+5)/3), self.printer.mmTOpx(self.VOG+self.VBD+self.billetH))]
        common_point = [i for i in GetCommonPoints(points, xy2) if i[1] > 0][0]
        upper_padding = self.printer.mmTOpx(self.billetH) - common_point[1]
        # del xy, xy2, points, bezier, x, y

        image = Image.new('RGBA', (round(common_point[0]+self.printer.mmTOpx(self.techno_padding)),
                                   round(upper_padding + self.printer.mmTOpx(self.VOG + self.VBD + self.techno_padding*2))), (0, 0, 0, 0))
        sketch = ImageDraw.Draw(image)

        tg2 = (20-(self.OG-(self.OT-self.Y))/2/3/2/2) / self.VOG
        tg3 = (20+(self.OG-(self.OT-self.Y))/2/3/2/2) / self.VOG
        xy0 = [(self.printer.mmTOpx(tg * (self.VOG + self.VBD) + self.techno_padding), self.printer.mmTOpx(self.techno_padding)),
               (self.printer.mmTOpx((tg * (self.VOG + self.VBD)-tg2 * self.VOG) + self.techno_padding), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG)),
               (self.printer.mmTOpx(self.techno_padding), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG + self.VBD))]

        x, y = xy0[0][0] - self.printer.mmTOpx((self.OG / 4 + 5) / 3 - 10), self.printer.mmTOpx(-self.billetDifferential-self.techno_padding)
        bezier = make_bezier(tuple(map(lambda cord: (
            cord[0] * (self.printer.mmTOpx(self.billetW) / w_exemplar) + x,
            cord[1] * (self.printer.mmTOpx(self.billetH) / h_exemplar) + y),
                                       ((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))))
        points0 = bezier(ts)

        bezier = make_bezier(tuple(map(lambda cord: (
            cord[0] * (self.printer.mmTOpx(self.billetW-self.techno_padding) / w_exemplar) + x,
            cord[1] * (self.printer.mmTOpx(self.billetH-self.techno_padding) / h_exemplar) + y),
                                       ((0, 12), (5, 65), (50, 75), (90, 65), (100, 5)))))
        points1 = bezier(ts)

        xy01 = [(xy0[0][0] - self.printer.mmTOpx(self.techno_padding), xy0[0][1] - self.printer.mmTOpx(self.techno_padding)),
                (xy0[1][0] - self.printer.mmTOpx(self.techno_padding), xy0[1][1]),
                (xy0[2][0] - self.printer.mmTOpx(self.techno_padding), xy0[2][1] + self.printer.mmTOpx(self.techno_padding))]
        xy0[0] = max([i for i in GetCommonPoints(points0, xy0[:2]) if i[1] > 0])
        xy01[0] = max([i for i in GetCommonPoints(points1, xy01[:2]) if i[1] > 0])

        xy1 = [(self.printer.mmTOpx(tg * (self.VOG + self.VBD) + self.techno_padding+(self.OG / 4 + 5) / 3), self.printer.mmTOpx(self.techno_padding)),
               (self.printer.mmTOpx((tg * (self.VOG + self.VBD)-(tg3 * self.VOG)) + self.techno_padding+(self.OG / 4 + 5) / 3), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG)),
               ((self.printer.mmTOpx(self.techno_padding + (self.OG-(self.OT-self.Y))/2/3/2/2+(self.OG / 4 + 5) / 3)), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG + self.VBD))]

        xy11 = [(xy1[0][0] + self.printer.mmTOpx(self.techno_padding), xy1[0][1] - self.printer.mmTOpx(self.techno_padding)),
                (xy1[1][0] + self.printer.mmTOpx(self.techno_padding), xy1[1][1]),
                (xy1[2][0] + self.printer.mmTOpx(self.techno_padding), xy1[2][1] + self.printer.mmTOpx(self.techno_padding))]
        xy1[0] = max([i for i in GetCommonPoints(points0, xy1[:2]) if i[1] > 0])
        xy11[0] = xy1[0][0] + self.printer.mmTOpx(self.techno_padding), xy1[0][1] - self.printer.mmTOpx(self.techno_padding)
        xy2 = ((self.printer.mmTOpx(self.techno_padding), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG + self.VBD)),
               (self.printer.mmTOpx(self.techno_padding + (self.OG-(self.OT-self.Y))/2/3/2/2 + (self.OG / 4 + 5) / 3), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG + self.VBD)))
        xy21 = [(xy2[0][0] - self.printer.mmTOpx(self.techno_padding), xy2[0][1] + self.printer.mmTOpx(self.techno_padding)),
                (xy2[1][0] + self.printer.mmTOpx(self.techno_padding), xy2[1][1] + self.printer.mmTOpx(self.techno_padding))]
        xy3 = ((self.printer.mmTOpx((tg * (self.VOG + self.VBD)-tg2 * self.VOG) + self.techno_padding), upper_padding+self.printer.mmTOpx(self.techno_padding + self.VOG)),
               (self.printer.mmTOpx((tg * (self.VOG + self.VBD)-(tg3 * self.VOG)) + self.techno_padding + (self.OG / 4 + 5) / 3),upper_padding+self.printer.mmTOpx(self.techno_padding + self.VOG)))

        sketch.line((xy0[0], *points0[points0.index(min(points0, key=lambda v: tuple(abs(numpy.array(v)-numpy.array(xy0[0]))))):points0.index(min(points0, key=lambda v: tuple(abs(numpy.array(v)-numpy.array(xy1[0])))))], xy1[0]), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line((xy01[0], *points1[points1.index(min(points1, key=lambda v: tuple(abs(numpy.array(v)-numpy.array(xy0[0]))))):points1.index(min(points1, key=lambda v: tuple(abs(numpy.array(v)-numpy.array(xy1[0])))))], xy11[0]), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy0, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy01, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy1, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy11, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy2, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy21, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy3, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD)-tg2 * self.VOG + (self.OG / 4 + 5) / 3 * 0.5)), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG) * 0.6), (self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD)-tg2 * self.VOG + (self.OG / 4 + 5) / 3 * 0.5)), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG) * 0.9)), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD)-tg2 * self.VOG + (self.OG / 4 + 5) / 3 * 0.4)), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG) * 0.8),
                     (self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD)-tg2 * self.VOG + (self.OG / 4 + 5) / 3 * 0.5)), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG) * 0.9),
                     (self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD)-tg2 * self.VOG + (self.OG / 4 + 5) / 3 * 0.6)), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG) * 0.8)), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.text((self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD)-tg2 * self.VOG + (self.OG / 4 + 5) / 3 * 0.6)), upper_padding + self.printer.mmTOpx(self.techno_padding + self.VOG) * 0.8), 'II', self.sketch_lines_color, font=self.font)
        return image

    def ThirdElement(self):
        up_line = 18
        tg = 20 / self.VOG
        tg3 = (20+(self.OG-(self.OT-self.Y))/2/3/2/2) / self.VOG
        tg4 = ((self.OG-(self.OT-self.Y))/2/3/2/2) / self.VOG
        tg_mid0 = ((self.OG-(self.OT-self.Y))/2/3/2) / (self.VOG - 10)
        tg_mid1 = ((self.OG-(self.OT-self.Y))/2/3/2 + 5) / (self.VOG - 10)
        w_exemplar = 100
        h_exemplar = 62
        ts = [t / 100.0 for t in range(101)]
        image = Image.new('RGBA', (self.printer.mmTOpx(self.techno_padding * 2 + (self.OG / 4 + 5) / 3 + ((self.ONK-self.OG)/2/3+5) + (tg * (self.VOG + self.VBD) - (self.OG-(self.OT-self.Y))/2/3/2/2)),
                                   self.printer.mmTOpx(self.techno_padding * 2 + up_line + self.billetH + self.VOG + self.VBD)), (0, 0, 0, 0))
        sketch = ImageDraw.Draw(image)
        xy0 = [
            (self.printer.mmTOpx(self.techno_padding + tg3 * self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH)),
            (self.printer.mmTOpx(self.techno_padding + tg * self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG)),
            (self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG + self.VBD))
        ]
        xy01 = [(xy0[0][0] - self.printer.mmTOpx(self.techno_padding), xy0[0][1] - self.printer.mmTOpx(self.techno_padding)),
                (xy0[1][0] - self.printer.mmTOpx(self.techno_padding), xy0[1][1]),
                (xy0[2][0] - self.printer.mmTOpx(self.techno_padding), xy0[2][1] + self.printer.mmTOpx(self.techno_padding))]
        x, y = self.printer.mmTOpx(self.techno_padding-((self.OG/4+5)/3*2-10)+tg * (self.VOG + self.VBD)), self.printer.mmTOpx(self.techno_padding + up_line)
        bezier = make_bezier(tuple(map(lambda cord: (
            cord[0] * (self.printer.mmTOpx(self.billetW) / w_exemplar) + x,
            cord[1] * (self.printer.mmTOpx(self.billetH) / h_exemplar) + y),
                                       ((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))))
        points0 = bezier(ts)
        bezier = make_bezier(tuple(map(lambda cord: (
            cord[0] * (self.printer.mmTOpx(self.billetW-self.techno_padding) / w_exemplar) + x,
            cord[1] * (self.printer.mmTOpx(self.billetH-self.techno_padding) / h_exemplar) + y),
                                       ((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))))
        points1 = bezier(ts)
        xy0[0] = max([i for i in GetCommonPoints(points0, xy0[:2]) if i[1] > 0])
        xy01[0] = max([i for i in GetCommonPoints(points1, xy01[:2]) if i[1] > 0])

        xy1 = [
            (self.printer.mmTOpx(self.billetW) - abs(x), self.printer.mmTOpx(self.techno_padding + up_line)),
            (self.printer.mmTOpx(self.billetW) - abs(x), self.printer.mmTOpx(self.techno_padding)),
            (self.printer.mmTOpx(self.billetW + 5) - abs(x), self.printer.mmTOpx(self.techno_padding))
        ]
        xy11 = [(xy1[0][0] - self.printer.mmTOpx(self.techno_padding), xy1[0][1]),
                (xy1[1][0] - self.printer.mmTOpx(self.techno_padding), xy1[1][1] - self.printer.mmTOpx(self.techno_padding)),
                (xy1[2][0] + self.printer.mmTOpx(self.techno_padding), xy1[2][1] - self.printer.mmTOpx(self.techno_padding))
                ]

        _points = ((self.printer.mmTOpx((tg * (self.VOG + self.VBD) - (self.OG-(self.OT-self.Y))/2/3/2/2) + self.techno_padding + (self.OG / 4 + 5) / 3), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH)),
                   (self.printer.mmTOpx(self.techno_padding + tg * (self.VOG + self.VBD) - (self.OG-(self.OT-self.Y))/2/3/2/2 + ((self.OG / 4 + 5) / 3) - tg_mid1 * self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG - 10)),
                   (self.printer.mmTOpx(self.techno_padding + tg * (self.VOG + self.VBD) - (self.OG-(self.OT-self.Y))/2/3/2/2 + ((self.OG / 4 + 5) / 3) - tg_mid0 * self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG)))

        xy2_2 = make_bezier(_points)(ts)
        xy2_21 = make_bezier((numpy.array(_points) + (self.printer.mmTOpx(self.techno_padding), 0)))(ts)

        _points = [
            (self.printer.mmTOpx(self.techno_padding + tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) - tg_mid0 * self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG)),
            (self.printer.mmTOpx(self.techno_padding + tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) + ((self.ONK - self.OG) / 2 / 3 + 5)), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG + self.VBD)),
        ]
        points2 = (_points[0], ((_points[0][0] + self.printer.mmTOpx(5) + _points[1][0] + self.printer.mmTOpx(5))/2, (_points[0][1] + _points[1][1])/2), _points[1])
        points3 = ((points2[0][0] + self.printer.mmTOpx(self.techno_padding), points2[0][1]),
                   (points2[1][0] + self.printer.mmTOpx(self.techno_padding), points2[1][1]),
                   (points2[2][0] + self.printer.mmTOpx(self.techno_padding), points2[2][1] + self.printer.mmTOpx(self.techno_padding))
                   )
        xy2_3 = make_bezier(points2)(ts)
        xy2_31 = make_bezier(points3)(ts)

        xy3 = (
            (self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG + self.VBD)),
            (self.printer.mmTOpx(self.techno_padding + tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) + ((self.ONK - self.OG) / 2 / 3 + 5)), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG + self.VBD))
        )
        xy31 = (
            (xy3[0][0] - self.printer.mmTOpx(self.techno_padding), xy3[0][1] + self.printer.mmTOpx(self.techno_padding)),
            (xy3[1][0] + self.printer.mmTOpx(self.techno_padding), xy3[1][1] + self.printer.mmTOpx(self.techno_padding)))

        _curve = make_bezier(tuple(map(lambda cord: (
            cord[0] * (self.printer.mmTOpx(self.printer.mmTOpx(30)) / 300) + self.printer.mmTOpx(self.billetW + 5) - abs(x),
            cord[1] * (self.printer.mmTOpx(self.printer.mmTOpx(7)) / 70) + self.printer.mmTOpx(self.techno_padding)),
                                       ((0, 0), (165, 55), (300, 70)))))(ts)
        _points = (
            (self.printer.mmTOpx((tg * (self.VOG + self.VBD) - (self.OG-(self.OT-self.Y))/2/3/2/2) + self.techno_padding + (self.OG / 4 + 5) / 3 - tg_mid1 * (up_line + self.billetH)), self.printer.mmTOpx(self.techno_padding)),
            (self.printer.mmTOpx((tg * (self.VOG + self.VBD) - (self.OG-(self.OT-self.Y))/2/3/2/2) + self.techno_padding + (self.OG / 4 + 5) / 3), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH))
        )
        common_point = min([i for i in GetCommonPoints(_curve, _points) if i[1] > 0])

        h_padding_line2 = common_point[1] - self.printer.mmTOpx(self.techno_padding)

        xy2 = (
            (self.printer.mmTOpx((tg * (self.VOG + self.VBD) - (self.OG-(self.OT-self.Y))/2/3/2/2) + self.techno_padding + (self.OG / 4 + 5) / 3) + tg_mid0 * (self.printer.mmTOpx(up_line + self.billetH) - h_padding_line2), self.printer.mmTOpx(self.techno_padding) + h_padding_line2),
            (self.printer.mmTOpx((tg * (self.VOG + self.VBD) - (self.OG-(self.OT-self.Y))/2/3/2/2) + self.techno_padding + (self.OG / 4 + 5) / 3), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH))
        )
        xy21 = (
            (xy2[0][0] + self.printer.mmTOpx(self.techno_padding), xy2[0][1] - self.printer.mmTOpx(self.techno_padding)),
            (xy2[1][0] + self.printer.mmTOpx(self.techno_padding), xy2[1][1])
        )

        xy4 = (
            (self.printer.mmTOpx(self.billetW + 5) - abs(x), self.printer.mmTOpx(self.techno_padding)),
            (self.printer.mmTOpx((tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2) + self.techno_padding + (self.OG / 4 + 5) / 3) + tg_mid0 * (self.printer.mmTOpx(up_line + self.billetH) - h_padding_line2),self.printer.mmTOpx(self.techno_padding) + h_padding_line2)
        )
        xy41 = (
            (xy4[0][0] + self.printer.mmTOpx(self.techno_padding), xy4[0][1] - self.printer.mmTOpx(self.techno_padding)),
            (xy4[1][0] + self.printer.mmTOpx(self.techno_padding), xy4[1][1] - self.printer.mmTOpx(self.techno_padding)),
        )

        xy5 = [
            (self.printer.mmTOpx(self.techno_padding + tg * self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG)),
            (self.printer.mmTOpx(self.techno_padding + tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) - tg_mid0 * self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG - 10))
        ]
        xy5[1] = max([i for i in GetCommonPoints(xy2_2, xy5) if i[1] > 0])
        sketch.line(xy0, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy01, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy1, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy11, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy2, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy21, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy2_2, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy2_21, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy2_3, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy2_31, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy3, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy31, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy4, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy41, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy5, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line((xy0[0], *points0[points0.index(min(points0, key=lambda v: tuple(abs(numpy.array(v)-numpy.array(xy0[0]))))):]), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line((xy01[0], *points1[points1.index(min(points1, key=lambda v: tuple(abs(numpy.array(v)-numpy.array(xy01[0]))))):]), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.5 - tg_mid0 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.2))), (self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.5 - tg_mid0 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.5)))), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.4 - tg_mid0 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.4))), (self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.5 - tg_mid0 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.5))), (self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.6 - tg_mid0 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.4)))), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.text((self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.5 - tg_mid0 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.5))), 'III', self.sketch_lines_color, font=self.font)
        return image

    def FourthElement(self):
        up_line = 18
        tg = 20 / self.VOG
        tg1 = ((self.OG-(self.OT-self.Y))/2/3/2/2) / self.VOG
        tg_mid1 = ((self.OG-(self.OT-self.Y))/2/3/2+5) / (self.VOG - 10)
        ts = [t / 100.0 for t in range(101)]
        image = Image.new('RGBA', (self.printer.mmTOpx(self.techno_padding * 2 + (self.OG / 4 - 5) / 2 + ((self.ONK-self.OG)/2/3) * 1.5),
                                   self.printer.mmTOpx(self.techno_padding * 2 + up_line + self.billetH + self.VOG + self.VBD)), (0, 0, 0, 0))
        sketch = ImageDraw.Draw(image)

        _points = [
            (self.printer.mmTOpx(self.techno_padding + ((self.ONK-self.OG)/2/3) + tg1 * self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG)),
            (self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG + self.VBD)),
        ]
        points0 = (_points[0], ((_points[0][0] - self.printer.mmTOpx(5) + _points[1][0] - self.printer.mmTOpx(5))/2, (_points[0][1] + _points[1][1])/2), _points[1])
        points1 = ((points0[0][0] - self.printer.mmTOpx(self.techno_padding), points0[0][1]),
                   (points0[1][0] - self.printer.mmTOpx(self.techno_padding), points0[1][1]),
                   (points0[2][0] - self.printer.mmTOpx(self.techno_padding), points0[2][1] + self.printer.mmTOpx(self.techno_padding))
                   )

        points2 = (
            (self.printer.mmTOpx(self.techno_padding + ((self.ONK-self.OG)/2/3)), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH)),
            (self.printer.mmTOpx(self.techno_padding + ((self.ONK-self.OG)/2/3) + tg_mid1 * (self.VOG - 10)), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG - 10)),
            (self.printer.mmTOpx(self.techno_padding + ((self.ONK - self.OG)/2/3) + tg1 * self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG)))
        points3 = tuple(numpy.array(points2) - (self.printer.mmTOpx(self.techno_padding), 0))

        xy0 = make_bezier(points0)(ts)
        xy01 = make_bezier(points1)(ts)
        xy1 = make_bezier(points2)(ts)
        xy11 = make_bezier(points3)(ts)

        x, y = self.printer.mmTOpx(-(self.OG/4+5) + 10 + self.billetW + 5), self.printer.mmTOpx(self.techno_padding)
        _curve = make_bezier(tuple(map(lambda cord: (
            cord[0] * (self.printer.mmTOpx(self.printer.mmTOpx(30*2)) / 300) + x,
            cord[1] * (self.printer.mmTOpx(self.printer.mmTOpx(7*2)) / 70) + y),
                                       ((0, 0), (165, 55), (300, 70)))))(ts)
        _points = (
            ((self.printer.mmTOpx(self.techno_padding + tg1 * (up_line + self.billetH))), self.printer.mmTOpx(self.techno_padding)),
            (self.printer.mmTOpx(self.techno_padding + (self.ONK-self.OG)/2/3), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH))
        )
        xy2 = (min([i for i in GetCommonPoints(_curve, _points) if i[1] > 0]), _points[1])
        xy21 = (
            (xy2[0][0] - self.printer.mmTOpx(self.techno_padding), xy2[0][1] - self.printer.mmTOpx(self.techno_padding)),
            (xy2[1][0] - self.printer.mmTOpx(self.techno_padding), xy2[1][1]),
        )
        xy3 = [
            (self.printer.mmTOpx(self.techno_padding + (self.OG / 4 - 5) / 2+tg1*(up_line + self.billetH + self.VOG)), self.printer.mmTOpx(self.techno_padding)),
            (self.printer.mmTOpx(self.techno_padding + (self.OG / 4 - 5) / 2-tg1*self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG)),
            (self.printer.mmTOpx(self.techno_padding + ((self.ONK-self.OG)/2/3) * 1.5 + (self.OG / 4 - 5) / 2), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG + self.VBD))
        ]
        xy3[0] = min([i for i in GetCommonPoints(_curve, xy3[:2]) if i[1] > 0])
        xy31 = ((xy3[0][0] + self.printer.mmTOpx(self.techno_padding), xy3[0][1] - self.printer.mmTOpx(self.techno_padding)),
                (xy3[1][0] + self.printer.mmTOpx(self.techno_padding), xy3[1][1]),
                (xy3[2][0] + self.printer.mmTOpx(self.techno_padding), xy3[2][1] + self.printer.mmTOpx(self.techno_padding)))
        xy4 = (xy2[0], xy3[0])
        xy41 = ((xy4[0][0] - self.printer.mmTOpx(self.techno_padding), xy4[0][1] - self.printer.mmTOpx(self.techno_padding)),
                (xy4[1][0] + self.printer.mmTOpx(self.techno_padding), xy4[1][1] - self.printer.mmTOpx(self.techno_padding)))

        xy5 = (
            (self.printer.mmTOpx(self.techno_padding), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG + self.VBD)),
            (self.printer.mmTOpx(self.techno_padding + ((self.ONK - self.OG) / 2 / 3) * 1.5 + (self.OG / 4 - 5) / 2), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG + self.VBD))
        )
        xy51 = ((xy5[0][0] - self.printer.mmTOpx(self.techno_padding), xy5[0][1] + self.printer.mmTOpx(self.techno_padding)),
                (xy5[1][0] + self.printer.mmTOpx(self.techno_padding), xy5[1][1] + self.printer.mmTOpx(self.techno_padding)))
        xy6 = [
            (self.printer.mmTOpx(self.techno_padding + tg_mid1 * self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG - 10)),
            (self.printer.mmTOpx(self.techno_padding + (self.OG / 4 - 5) / 2-tg1*self.VOG), self.printer.mmTOpx(self.techno_padding + up_line + self.billetH + self.VOG))]
        xy6[0] = min([i for i in GetCommonPoints(xy1, xy6) if i[1] > 0])

        sketch.line(xy0, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy01, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy1, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy11, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy2, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy21, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy3, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy31, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy4, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy41, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy5, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy51, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(xy6, self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.5 - tg_mid1 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.2))), (self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.5 - tg_mid1 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.5)))), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.line(((self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.4 - tg_mid1 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.4))), (self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.5 - tg_mid1 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.5))), (self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.6 - tg_mid1 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.4)))), self.sketch_lines_color, self.printer.mmTOpx(1))
        sketch.text((self.printer.mmTOpx(self.techno_padding + (tg * (self.VOG + self.VBD) - (self.OG - (self.OT - self.Y)) / 2 / 3 / 2 / 2 + ((self.OG / 4 + 5) / 3) * 0.5 - tg_mid1 * self.VOG)), (self.printer.mmTOpx((self.techno_padding + up_line + self.billetH) + self.VOG * 0.5))), 'IV', self.sketch_lines_color, font=self.font)

        return image


Sketch = DrawSketch(OG=760, OT=640, ONK=850, VOG=120, VBU=220, VBD=120, Y=50, printer=Printer('monitorHDC'))
# Sketch.FirstElement().show()
# Sketch.SecondElement().show()
Sketch.printer.NewSketch(Sketch.Elements([1,2,3,4]))
# Sketch.FourthElement().show()
# Sketch.printer.NewSketch(Sketch.FirstElement())

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