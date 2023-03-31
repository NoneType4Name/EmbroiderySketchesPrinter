import os
import sys
import time
import math
import json
import numpy
import pygame
import ctypes
import random
import psutil
import string
import win32con
import win32gui
import win32ui
import win32api
import requests
import threading
import subprocess
import urlextract
import webbrowser
import pywintypes
import win32print
import win32process
from constants import *
from bs4 import BeautifulSoup
from ctypes import wintypes, byref
# from screeninfo import get_monitors
from PIL import Image, ImageWin, ImageDraw, ImageFont

PUNCTUATION = string.punctuation + ' '
ESCAPE_CHARS = '\n\a\b\f\r\t\v\x00'
ESCAPE_CHARS_TRANSLATER = str.maketrans(dict.fromkeys(list(ESCAPE_CHARS), None))

pygame.init()


class DATA(dict):
    """
    Custom dictionary.
    """

    def __init__(self, data):
        for name, value in data.items():
            setattr(self, str(name), self._wrap(value))
        super().__init__(data)

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return DATA(value) if isinstance(value, dict) else value

    def __repr__(self):
        return '{%s}' % str(', '.join("'%s': %s" % (k, repr(v)) for (k, v) in self.__dict__.items()))


LANGUAGE = DATA(TRANSLATE)
COLORS = DATA(COLORS)


class SIZE(tuple):
    def __init__(self, data):
        super().__init__()
        self.w, self.h = map(int, data)

    def __repr__(self):
        return f'{self.w}x{self.h}'


monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0,0)))
FULL_SIZE = SIZE((monitor_info['Work'][2]-monitor_info['Work'][0], monitor_info['Work'][3]-monitor_info['Work'][1]-(win32api.GetSystemMetrics(33) + win32api.GetSystemMetrics(4) + win32api.GetSystemMetrics(92))))
PANEL_SIZE = SIZE((win32api.GetSystemMetrics(0)-monitor_info['Work'][2]-monitor_info['Work'][0], win32api.GetSystemMetrics(1)-monitor_info['Work'][3]-monitor_info['Work'][1]))


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


class Version:
    def __init__(self, string_version: str):
        vers = {
            'major': 0,
            'minor': 0,
            'micro': 0,
            'type': 0,
            'name': '_'.join(string_version.split('_')[1:]),
        }
        [vers.update({list(vers.keys())[key_n]: value}) for key_n, value in
         enumerate(map(int, string_version.split('.')))]
        self.major, self.minor, self.micro, self.type, self.name = vers.values()
        self.string_version = '.'.join(list(map(str, vers.values()))[:-1]) + (f'/{self.name}' if self.name else '')

    def __repr__(self):
        return self.string_version

    def __gt__(self, other):
        if type(other) is not Version:
            other = Version(other)
        if self.major > other.major:
            return True
        elif self.major == other.major:
            if self.minor > other.minor:
                return True
            elif self.minor == other.minor:
                if self.micro > other.micro:
                    return True
                elif self.micro == other.micro:
                    if self.type > other.type:
                        return True
        return False

    def __lt__(self, other):
        if type(other) is not Version:
            other = Version(other)
        if self.major < other.major:
            return True
        elif self.major == other.major:
            if self.minor < other.minor:
                return True
            elif self.minor == other.minor:
                if self.micro < other.micro:
                    return True
                elif self.micro == other.micro:
                    if self.type < other.type:
                        return True
        return False


def GetUpdate(self, status, button):
    self.NewVersion = None
    self.NewVersionContent = b''
    button.func = lambda s: None
    status.value = LANGUAGE.Update.Getting
    button.value = LANGUAGE.Update.GettingButton
    status.color = COLORS.label.UpdateStatus.check.background
    status.color_active = COLORS.label.UpdateStatus.check.backgroundActive
    status.text_color = COLORS.label.UpdateStatus.check.text
    status.text_color_active = COLORS.label.UpdateStatus.check.textActive
    status.border_color = COLORS.label.UpdateStatus.check.border
    status.border_color_active = COLORS.label.UpdateStatus.check.borderActive
    while not self.NewVersion:
        try:
            version = BeautifulSoup(requests.get('https://github.com/NoneType4Name/EmbroiderySketchesPrinter/releases/latest/').text, "lxml").find('h1', {'data-view-component':"true", 'class':"d-inline mr-3"}).text
            self.NewVersion = Version(version)
            if self.parent.Version < self.NewVersion:
                status.value = LANGUAGE.Update.Loading
                button.value = LANGUAGE.Update.LoadingButton
                status.color = COLORS.label.UpdateStatus.load.background
                status.color_active = COLORS.label.UpdateStatus.load.backgroundActive
                status.text_color = COLORS.label.UpdateStatus.load.text
                status.text_color_active = COLORS.label.UpdateStatus.load.textActive
                status.border_color = COLORS.label.UpdateStatus.load.border
                status.border_color_active = COLORS.label.UpdateStatus.load.borderActive
                con = requests.get(
                    f'{GITHUB}/{AUTHOR}/{"".join(NAME.split(" "))}/releases/latest/download/{"".join(NAME.split(" "))}.exe', stream=True)
                for chunk in con.iter_content(4096*2):
                    self.NewVersionContent += chunk
                    status.value = f'{LANGUAGE.Update.Loading} {round(len(self.NewVersionContent)/int(con.headers["Content-Length"])*100, 1)}%'

                status.value = LANGUAGE.Update.Available
                button.value = LANGUAGE.Update.AvailableButton

                status.color = COLORS.label.UpdateStatus.available.background
                status.color_active = COLORS.label.UpdateStatus.available.backgroundActive
                status.text_color = COLORS.label.UpdateStatus.available.text
                status.text_color_active = COLORS.label.UpdateStatus.available.textActive
                status.border_color = COLORS.label.UpdateStatus.available.border
                status.border_color_active = COLORS.label.UpdateStatus.available.borderActive
                button.func = lambda s: threading.Thread(target=InstallUpdate, args=[self, status, button], daemon=True).start()
            else:
                button.func = lambda s: threading.Thread(target=GetUpdate, args=[self, status, button], daemon=True).start()
                status.value = LANGUAGE.Update.Actual
                button.value = LANGUAGE.Update.ActualButton
                status.color = COLORS.label.UpdateStatus.background
                status.color_active = COLORS.label.UpdateStatus.backgroundActive
                status.text_color = COLORS.label.UpdateStatus.text
                status.text_color_active = COLORS.label.UpdateStatus.textActive
                status.border_color = COLORS.label.UpdateStatus.border
                status.border_color_active = COLORS.label.UpdateStatus.borderActive
        except requests.exceptions.ConnectionError:
            continue


def InstallUpdate(self, status, button):
    if self.NewVersionContent:
        self._name_exe = f'{"".join(NAME.split(" "))}_{self.NewVersion.string_version}.exe'
        with open(f'{self.parent.MAIN_DIR}/{self._name_exe}', 'wb') as f:
            f.write(self.NewVersionContent)
        status.color = COLORS.label.UpdateStatus.install.background
        status.color_active = COLORS.label.UpdateStatus.install.backgroundActive
        status.text_color = COLORS.label.UpdateStatus.install.text
        status.text_color_active = COLORS.label.UpdateStatus.install.textActive
        status.border_color = COLORS.label.UpdateStatus.install.border
        status.border_color_active = COLORS.label.UpdateStatus.install.borderActive
        status.value = LANGUAGE.Update.Open
        button.value = LANGUAGE.Update.OpenButton
        button.func = lambda s: threading.Thread(target=OpenUpdate, args=[self, status, button], daemon=True).start()


def OpenUpdate(self, status, button):
    status.color = COLORS.label.UpdateStatus.open.background
    status.color_active = COLORS.label.UpdateStatus.open.backgroundActive
    status.text_color = COLORS.label.UpdateStatus.open.text
    status.text_color_active = COLORS.label.UpdateStatus.open.textActive
    status.border_color = COLORS.label.UpdateStatus.open.border
    status.border_color_active = COLORS.label.UpdateStatus.open.borderActive
    status.value = LANGUAGE.Update.Launching
    button.value = LANGUAGE.Update.LaunchingButton
    try:

        subprocess.Popen(self._name_exe)
        self.parent.RUN = False
    except OSError as e:
        status.color = COLORS.label.UpdateStatus.error.background
        status.color_active = COLORS.label.UpdateStatus.error.backgroundActive
        status.text_color = COLORS.label.UpdateStatus.error.text
        status.text_color_active = COLORS.label.UpdateStatus.error.textActive
        status.border_color = COLORS.label.UpdateStatus.error.border
        status.border_color_active = COLORS.label.UpdateStatus.error.borderActive
        status.value = LANGUAGE.Update.LaunchingError.format(e.winerror)


class Printer:
    def __init__(self, printer_name: str):
        if printer_name != DUMMY_MONITOR:
            self.isLocal = True
            self.name = printer_name
            self._hDC = win32ui.CreateDC()
            self._hDC.CreatePrinterDC(printer_name)
            self.printable_area = self._hDC.GetDeviceCaps(HORZRES), self._hDC.GetDeviceCaps(VERTRES)
            self.printer_size = self._hDC.GetDeviceCaps(PHYSICALWIDTH), self._hDC.GetDeviceCaps(PHYSICALHEIGHT)
            self.dpi = self._hDC.GetDeviceCaps(LOGPIXELSX)
            try:
                self._pHD = win32print.OpenPrinter(printer_name, {"DesiredAccess": win32print.PRINTER_ALL_ACCESS})
                self.properties = win32print.GetPrinter(self._pHD, 2)
            except pywintypes.error:
                self._pHD = None
                self.properties = None
                self.isLocal = False
        else:
            self._hHD = None
            self._pHD = None
            self.isLocal = False
            self.printable_area = FULL_SIZE
            self.printer_size = FULL_SIZE
            try:
                self.dpi = ctypes.windll.user32.GetDpiForWindow(pygame.display.get_wm_info()['window'])
            except KeyError:
                self.dpi = ctypes.windll.user32.GetDpiForSystem()
        self.HORIZONTAL = True if self.printable_area[0] > self.printable_area[1] else False
        self.glue_padding = self.mmTOpx(GLUE_PADDING)

    def mmTOpx(self, *mm: int) -> int:
        """

        mm:     millimeters :   int
        Return: pixels      :   int
        """
        r = tuple(round((mm * self.dpi) / 25.4) for mm in mm)
        if len(r) - 1:
            return r
        return r[0]

    def ReInit(self):
        self.close()
        self._hDC = win32ui.CreateDC()
        self._hDC.CreatePrinterDC(self.name)
        self.printable_area = self._hDC.GetDeviceCaps(HORZRES), self._hDC.GetDeviceCaps(VERTRES)
        self.printer_size = self._hDC.GetDeviceCaps(PHYSICALWIDTH), self._hDC.GetDeviceCaps(PHYSICALHEIGHT)
        self.dpi = self._hDC.GetDeviceCaps(LOGPIXELSX)
        if self.isLocal:
            self._pHD = win32print.OpenPrinter(self.name, {"DesiredAccess": win32print.PRINTER_ALL_ACCESS})
            self.properties = win32print.GetPrinter(self._pHD, 2)

    def UpdateProperties(self):
        if self.isLocal:
            win32print.SetPrinter(self._pHD, 2, self.properties, 0)

    def Menu(self):
        if self.isLocal:
            win32print.DocumentProperties(pygame.display.get_wm_info()['window'], self._pHD, self.name, self.properties['pDevMode'], self.properties['pDevMode'], 5)
            self.UpdateProperties()
            self.ReInit()

    def Color(self, pos=None):
        if self.isLocal:
            self.properties['pDevMode'].Color = pos if pos is not None else 1 if self.properties['pDevMode'].Color-1 else 2
            self.UpdateProperties()
            self.ReInit()
            return self.properties['pDevMode'].Color - 1

    def NewSketch(self, sketches, sketches_padding=DEFAULT_SKETCHES_PADDING, l=False):
        start_time = time.time()
        all_images = []
        if not any(map(lambda i: type(i) is Image.Image, sketches)):
            sketches = [Image.open(s) if s is str else s for s in sketches if type(s) in (str, Image.Image)] if not all(
                s is Image.Image for s in sketches) else sketches
        if l:
            if sketches:
                _h_l = max(i.size[1] for i in sketches)
                return math.ceil((sum(map(lambda s: s.size[0] + self.glue_padding, sketches)) + (
                            len(sketches) - 1) * self.mmTOpx(sketches_padding)) / self.printable_area[0]) * math.ceil(
                    (_h_l + math.ceil(_h_l / self.printable_area[1]) * self.glue_padding * 2) / self.printable_area[1])
            return 0
        if not sketches:
            return all_images
        font = ImageFont.truetype(FONT_PATH, int(self.mmTOpx(sketches_padding) / SKETCHES_FONT_K))
        w = self.printable_area[0] - self.glue_padding * 2
        images_h = []
        sketch_num = 0
        sketch = sketches[sketch_num]
        sketch_w = sketch.size[0]
        sketch_h = sketch.size[1]
        while sketch_num < len(sketches) - 1 or sketch_w > 0:
            while w > 0 and (sketch_num < len(sketches) - 1 or sketch_w > 0):
                list_by_h = 0
                while sketch_h > 0:
                    if not len(images_h) or len(images_h) - 1 < list_by_h:
                        images_h.append(Image.new('L', self.printable_area, 255))

                        d = ImageDraw.Draw(images_h[list_by_h])
                        d.rectangle((0, 0, *self.printable_area), 255, 100, self.glue_padding)

                        d.text((0, 0), LANGUAGE.Sketch.LeftUp, fill=255, font=font)

                        t = LANGUAGE.Sketch.ListNum % str(len(all_images) + len(images_h))
                        s = font.getsize(t)
                        d.text((images_h[list_by_h].size[0] - s[0], images_h[list_by_h].size[1] - s[1]), t, fill=255,
                               font=font)

                        t = LANGUAGE.Sketch.MoreInfo.format(
                            w=images_h[list_by_h].size[0], h=images_h[list_by_h].size[1],
                            d=self.dpi,
                            m=round(time.time() - start_time, 2))
                        s = font.getsize(t)
                        i_f = Image.new('L', s, 0)
                        ImageDraw.Draw(i_f).text((0, 0), t, fill=255, font=font)
                        i_f = i_f.rotate(90, expand=True)
                        images_h[list_by_h].paste(i_f, (0, images_h[list_by_h].size[1] // 2 - s[0] // 2), i_f)

                        s = font.getsize(LANGUAGE.Sketch.Author)
                        i_f = Image.new('L', s, 0)
                        ImageDraw.Draw(i_f).text((0, 0), LANGUAGE.Sketch.Author, fill=255, font=font)
                        i_f = i_f.rotate(270, expand=True)
                        images_h[list_by_h].paste(i_f, (
                        images_h[list_by_h - 1].size[0] - s[1], images_h[list_by_h - 1].size[1] // 2), i_f)

                        if list_by_h:
                            t = LANGUAGE.Sketch.HeaderInfo % str(
                                len(all_images) + len(images_h) - 1)
                            s = font.getsize(t)
                            d.text((images_h[list_by_h].size[0] // 2 - s[0] // 2, 0), t, fill=255, font=font)
                        if sketch_h - (self.printable_area[1] - self.glue_padding) > 0:
                            t = LANGUAGE.Sketch.FooterInfo % str(
                                len(all_images) + len(images_h) + 1)
                            s = font.getsize(t)
                            d.text((images_h[list_by_h].size[0] // 2 - s[0] // 2, images_h[list_by_h].size[1] - s[1]),
                                   t,
                                   fill=255, font=font)

                    i = sketch.crop((
                        sketch.size[0] - sketch_w,
                        sketch.size[1] - sketch_h,
                        sketch.size[0] if sketch.size[0] < w else w,
                        sketch.size[1] if sketch_h < self.printable_area[1] - self.glue_padding * 2 else
                        self.printable_area[1] - self.glue_padding * 2))
                    images_h[list_by_h].paste(i, ((self.printable_area[0] - self.glue_padding) - w, self.glue_padding),
                                              mask=i.split()[3])
                    sketch_h = sketch_h - (self.printable_area[1] - self.glue_padding)

                    list_by_h += 1
                sketch_w -= i.size[0] + (self.mmTOpx(sketches_padding) if not sketch_w - i.size[0] else 0)
                w -= i.size[0] + (self.mmTOpx(sketches_padding) if not sketch_w else 0)
                if sketch_w <= 0 and sketch_num + 1 < len(sketches):
                    sketch_num += 1
                    sketch = sketches[sketch_num]
                    sketch_w = sketch.size[0]
                    sketch_h = sketch.size[1]

            else:
                w = self.printable_area[0] - self.glue_padding * 2
                if sketch_num < len(sketches) - 1:
                    t = LANGUAGE.Sketch.LastInfo.format(str(len(all_images) + len(images_h) + 1),
                                                                           len(all_images) + 1)
                    s = font.getsize(t)
                    i_f = Image.new('L', s, 0)
                    ImageDraw.Draw(i_f).text((0, 0), t, fill=255, font=font)
                    i_f = i_f.rotate(270, expand=True)
                    images_h[list_by_h - 1].paste(i_f, (images_h[list_by_h - 1].size[0] - s[1], s[0] // 2), i_f)
                all_images += images_h
                sketch_h = sketch.size[1]
                images_h = []
        else:
            all_images += images_h
        return all_images

    def PrintAll(self, images, task_group_name: str):
        self._hDC.StartDoc(task_group_name)
        # win32print.StartDocPrinter(self._pHD, 1, (task_group_name, None, "xps_pass"))
        for im in images:
            self.newTask(im)
        self._hDC.EndDoc()
        # win32print.EndDocPrinter(self._pHD)

    def newTask(self, image, task_name: str = None):
        if type(image) is str:
            _image = Image.open(image)
        elif type(image) is Image.Image:
            _image = image
        else:
            raise TypeError(f'Unsupported type for image (type: {type(image)})')
        _print_image = _image.rotate(
            90 if _image.size[0] > _image.size[1] and self.HORIZONTAL else 0, fillcolor=255)
        if self._hDC is not None:
            if task_name:
                self._hDC.StartDoc()
                # win32print.StartDocPrinter(self._pHD, 1, (task_name, None, "xps_pass"))
            self._hDC.StartPage()
            # win32print.StartPagePrinter(self._pHD)
            ImageWin.Dib(_print_image).draw(self._hDC.GetHandleOutput(), (0, 0, *image.size))
            # _img_byte_arr = io.BytesIO()
            # _print_image.save(_img_byte_arr, format='PNG')
            # win32print.WritePrinter(self._pHD, _img_byte_arr.getbuffer())
            self._hDC.EndPage()
            # win32print.EndPagePrinter(self._pHD)
            if task_name:
                self._hDC.EndDoc()
                # win32print.EndDocPrinter(self._pHD)
        _print_image = None

    def close(self):
        if self._hDC:
        # if self._pHD:
            self._hDC.DeleteDC()
            if self.isLocal:
                # for a in self._defaultPDEVMODE:
                #     if a != 'DriverData':
                #         try:
                #             setattr(self.properties['pDevMode'], a, self._defaultPDEVMODE[a])
                #         except Exception:
                #             continue
                # self.UpdateProperties()
                win32print.ClosePrinter(self._pHD)


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


def GetCommonPoints(points1, points2):
    c = []
    for i in range(len(points1) - 1):
        x1y1, x2y2 = points1[i], points1[i + 1]
        x3y3, x4y4 = points2
        try:
            x = ((x1y1[0] * x2y2[1] - x1y1[1] * x2y2[0]) * (x3y3[0] - x4y4[0]) - (x1y1[0] - x2y2[0]) * (
                        x3y3[0] * x4y4[1] - x3y3[1] * x4y4[0])) / (
                            (x1y1[0] - x2y2[0]) * (x3y3[1] - x4y4[1]) - (x1y1[1] - x2y2[1]) * (x3y3[0] - x4y4[0]))
            y = ((x1y1[0] * x2y2[1] - x1y1[1] * x2y2[0]) * (x3y3[1] - x4y4[1]) - (x1y1[1] - x2y2[1]) * (
                        x3y3[0] * x4y4[1] - x3y3[1] * x4y4[0])) / (
                            (x1y1[0] - x2y2[0]) * (x3y3[1] - x4y4[1]) - (x1y1[1] - x2y2[1]) * (x3y3[0] - x4y4[0]))
            c.append((x, y))
        except ZeroDivisionError:
            pass
    return c


def GetCommonPointsForBezierCurve(points1, points2):
    for i in range(len(points1) - (1 if len(points1) - 1 else 0)):
        x1, y1, x2, y2 = points1[i][0], points1[i][1], points1[i + 1][0], points1[i + 1][1]
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
        y = k1 * x + b1
        if x1 <= x <= x2 and y1 <= y <= y2:
            return x, y


def LineIntersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def GetCommonPointsForBezierCurve1(points1, points2):
    c = []
    for i in range(len(points1) - (1 if len(points1) - 1 else 0)):
        r = LineIntersection(((points1[i][0], points1[i][1]), (points1[i + 1][0], points1[i + 1][1])), ((points2[0][0], points2[0][1]), (points2[1][0], points2[1][1])))
        if r:
            c.append(r)
    return c


def GetLineLength(xy0, xy1):
    return ((xy1[0] - xy0[0]) ** 2 + (xy1[1] - xy0[1]) ** 2) ** 0.5


class DrawSketch:
    def __init__(self, OG, OT, ONK, VOG, VBU, VBD, Y, printer: Printer):
        self.VOG = VOG + 10
        self.OG = OG
        self.OT = OT
        self.ONK = ONK
        self.VOG = VOG
        self.VBU = VBU
        self.VBD = VBD
        self.Y = Y
        self.printer = printer
        self._mid_rise = 7
        self._mid_pad = 5
        self._radius = 7
        self.billetW = 150
        self.billetH = 90
        self.billetDifferential = 18
        self.upper_padding = 18
        self.techno_padding = 10
        self.font = ImageFont.truetype(FONT_PATH, int(sum(self.printer.printable_area) / SKETCHES_ELEMENTS_FONT_K))
        self.sketch_lines_color = (0, 0, 0)
        self.sketch_lines_width = 1
        self._ts = [t / 100.0 for t in range(101)]

    def Elements(self, elements: tuple, background=(0, 0, 0, 0)):
        return [getattr(self, LANGUAGE.Print.FuncNames[num]).__call__(background) for num in elements]

    def CreateFirstElementCurve(self, xy, dx=0, dy=0):
        return make_bezier(tuple(map(lambda cord: (self.printer.mmTOpx(cord[0])+xy[0]-self.sketch_lines_width*2,
                                                   self.printer.mmTOpx(cord[1])+xy[1]+self.sketch_lines_width*2),
                                     ((0+dx, self.billetDifferential+dy), (8+dx, 95+dy), (75, 109+dy), (135-dx, 95+dy), (150-dx, 0+dy)))))(self._ts)

    def FirstElement(self, bg=(0, 0, 0, 0)):
        tg_normal = self.printer.mmTOpx(20)/self.printer.mmTOpx(self.VOG)
        tg_Y = self.printer.mmTOpx(((self.OG-(self.OT-self.Y))/2/3/2/2))/self.printer.mmTOpx(self.VOG)

        xy1 = (self.printer.mmTOpx(self.techno_padding+10, self.techno_padding+self.billetDifferential+5),
               self.printer.mmTOpx(self.techno_padding+10, self.techno_padding+self.billetDifferential),
               self.printer.mmTOpx(self.techno_padding, self.techno_padding+self.billetDifferential),
               self.printer.mmTOpx(self.techno_padding, self.techno_padding+self.billetH+self.VOG),
               self.printer.mmTOpx(self.techno_padding, self.techno_padding+self.billetH+self.VOG+self.VBD))
        xy11 = (self.printer.mmTOpx(self.techno_padding*2+10, self.billetDifferential+5/2),
                self.printer.mmTOpx(self.techno_padding*2+10, self.billetDifferential),
                self.printer.mmTOpx(0, self.billetDifferential),
                self.printer.mmTOpx(0, self.techno_padding+self.billetH+self.VOG),
                self.printer.mmTOpx(0, self.techno_padding*2+self.billetH+self.VOG+self.VBD))
        points1 = self.CreateFirstElementCurve(self.printer.mmTOpx(self.techno_padding+10, self.techno_padding))
        points11 = self.CreateFirstElementCurve(self.printer.mmTOpx(self.techno_padding+10, self.techno_padding), self.techno_padding, -self.techno_padding)

        xy2 = (self.printer.mmTOpx(self.techno_padding+(self.OG/4+5)/3+tg_normal*self.billetH, self.techno_padding),
               self.printer.mmTOpx(self.techno_padding+(self.OG/4+5)/3, self.techno_padding+self.billetH),
               self.printer.mmTOpx(self.techno_padding+(self.OG/4+5)/3-tg_normal*self.VOG-tg_Y*self.VOG, self.techno_padding+self.billetH+self.VOG),
               self.printer.mmTOpx(self.techno_padding+(self.OG/4+5)/3-tg_normal*(self.VOG+self.VBD)-tg_Y*self.VOG, self.techno_padding+self.billetH+self.VOG+self.VBD))
        commons1 = GetCommonPoints(points1, xy2[:2])
        xy2 = (min(commons1, key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy2[0])))), *xy2[1:])
        points1 = *points1[:commons1.index(xy2[0])-1], xy2[0]
        xy21 = ((xy2[0][0]+self.printer.mmTOpx(self.techno_padding), xy2[0][1]-self.printer.mmTOpx(self.techno_padding)),
                (xy2[1][0]+self.printer.mmTOpx(self.techno_padding), xy2[1][1]),
                (xy2[2][0]+self.printer.mmTOpx(self.techno_padding), xy2[2][1]),
                (xy2[3][0]+self.printer.mmTOpx(self.techno_padding), xy2[3][1]+self.printer.mmTOpx(self.techno_padding))
                )
        commons11 = GetCommonPoints(points11, xy21[:2])
        xy21 = (min(commons11, key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy21[0])))), *xy21[1:])
        points11 = *points11[:commons11.index(xy21[0])-1], xy21[0]

        xy3 = xy1[-1], xy2[-1]
        xy31 = xy11[-1], xy21[-1]
        waistline = xy1[3], xy2[2]
        image = Image.new('RGBA', (math.ceil(xy21[0][0]+self.sketch_lines_width), self.printer.mmTOpx(self.billetH+self.VOG+self.VBD+self.techno_padding*2)), bg)
        sketch = ImageDraw.Draw(image)
        sketch.line(points1, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(points11, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy1, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy11, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy2, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy21, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy3, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy31, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(waistline, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.2)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.7))
                     ), self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.35, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.55)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.7)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.65, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.55))
                     ), self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.text((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.7)), 'I', self.sketch_lines_color, font=self.font)
        return image

    def SecondElement(self, bg=(0, 0, 0, 0)):
        tg_normal = self.printer.mmTOpx(20)/self.printer.mmTOpx(self.VOG)
        tg_Y = self.printer.mmTOpx(((self.OG-(self.OT-self.Y))/2/3/2/2))/self.printer.mmTOpx(self.VOG)
        x, y = self.printer.mmTOpx(-((self.OG/2/2+5)/3)+self.techno_padding+10+((tg_normal*(self.VOG+self.VBD))-tg_Y*self.VBD), self.techno_padding)
        points_from_1st_element = self.CreateFirstElementCurve((x, y))
        points_from_1st_element1 = self.CreateFirstElementCurve((x, y), self.techno_padding,-self.techno_padding)


        xy1 = (self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+tg_normal*self.billetH, self.techno_padding),
               self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD), self.techno_padding+self.billetH),
               self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)-(tg_normal*self.VOG-tg_Y*self.VOG), self.techno_padding+self.billetH+self.VOG),
               self.printer.mmTOpx(self.techno_padding, self.techno_padding+self.billetH+self.VOG+self.VBD))

        commons = GetCommonPoints(points_from_1st_element, xy1[:2])
        commons1 = GetCommonPoints(points_from_1st_element1, xy1[:2])
        common1 = min(commons1, key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy1[0]))))
        points_from_1st_element1 = points_from_1st_element1[commons1.index(common1):]

        xy1 = (min(commons, key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy1[0])))), *xy1[1:])
        xy11 = (points_from_1st_element1[0],
                (xy1[0][0] - self.printer.mmTOpx(self.techno_padding), xy1[0][1] - self.printer.mmTOpx(self.techno_padding)),
                (xy1[1][0] - self.printer.mmTOpx(self.techno_padding), xy1[1][1]),
                (xy1[2][0] - self.printer.mmTOpx(self.techno_padding), xy1[2][1]),
                (xy1[3][0] - self.printer.mmTOpx(self.techno_padding), xy1[3][1] + self.printer.mmTOpx(self.techno_padding)))

        points_from_1st_element = xy1[0], *points_from_1st_element[commons.index(xy1[0])+1:]

        xy2 = (self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+((self.OG/2/2+5)/3)+tg_normal*self.billetH, self.techno_padding),
               self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+((self.OG/2/2+5)/3), self.techno_padding+self.billetH),
               self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+((self.OG/2/2+5)/3)-tg_normal*self.VOG-tg_Y*self.VOG, self.techno_padding+self.billetH+self.VOG),
               self.printer.mmTOpx(self.techno_padding+((self.OG/2/2+5)/3), self.techno_padding+self.billetH+self.VOG+self.VBD))
        commons = GetCommonPoints(points_from_1st_element, xy2[:2])
        xy2 = (min(commons, key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy2[0])))), *xy2[1:])
        points_from_1st_element = *points_from_1st_element[:commons.index(xy2[0])-1], xy2[0]
        points_from_1st_element1 = points_from_1st_element1[:points_from_1st_element1.index(min(points_from_1st_element1, key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy2[0])))))-1]
        xy21 = (points_from_1st_element1[-1],
                (xy2[0][0] + self.printer.mmTOpx(self.techno_padding), xy2[0][1] - self.printer.mmTOpx(self.techno_padding)),
                (xy2[1][0] + self.printer.mmTOpx(self.techno_padding), xy2[1][1]),
                (xy2[2][0] + self.printer.mmTOpx(self.techno_padding), xy2[2][1]),
                (xy2[3][0] + self.printer.mmTOpx(self.techno_padding), xy2[3][1] + self.printer.mmTOpx(self.techno_padding)))
        xy3 = xy1[-1], xy2[-1]
        xy31 = xy11[-1], xy21[-1]
        waistline = xy1[2], xy2[2]

        image = Image.new('RGBA', tuple(map(math.ceil, (max(xy21[1][0], xy21[2][0], xy21[3][0], xy21[-1][0]), xy21[-1][1]))), bg)
        sketch = ImageDraw.Draw(image)
        sketch.line(points_from_1st_element, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(points_from_1st_element1, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy1, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy11, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy2, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy21, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy3, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy31, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(waistline, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.2)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.7))
                     ), self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.35, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.55)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.7)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.65, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.55))
                     ), self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.text((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.7)), 'II', self.sketch_lines_color, font=self.font)
        return image

    def ThirdElement(self, bg=(0, 0, 0, 0)):
        tg_normal = self.printer.mmTOpx(20)/self.printer.mmTOpx(self.VOG)
        tg_mid = self.printer.mmTOpx((self.OG-(self.OT-self.Y))/2/3/2)/self.printer.mmTOpx(self.VOG-self._mid_rise)
        tg_mid_with_pad = self.printer.mmTOpx((self.OG-(self.OT-self.Y))/2/3/2+self._mid_pad)/self.printer.mmTOpx(self.VOG-self._mid_rise)
        tg_Y = self.printer.mmTOpx(((self.OG-(self.OT-self.Y))/2/3/2/2))/self.printer.mmTOpx(self.VOG)

        x, y = self.printer.mmTOpx(-((self.OG/2/2+5)/3*2)+((tg_normal*(self.VOG+self.VBD))-tg_Y*self.VBD)+10+self.techno_padding, self.techno_padding+self.upper_padding)
        points0 = self.CreateFirstElementCurve((x, y))
        xy1 = (self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+tg_normal*(self.upper_padding+self.billetH), self.techno_padding),
               self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD), self.techno_padding+self.upper_padding+self.billetH),
               self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)-(tg_normal*self.VOG-tg_Y*self.VOG), self.techno_padding+self.upper_padding+self.billetH+self.VOG),
               self.printer.mmTOpx(self.techno_padding, self.techno_padding+self.upper_padding+self.billetH+self.VOG+self.VBD))

        common_points = GetCommonPoints(points0, xy1[:2])
        xy1 = (min(common_points, key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy1[0])))), *xy1[2:])
        points0 = (xy1[0],*points0[common_points.index(xy1[0])+1:])
        points0 = (*points0, (points0[-1][0] + self.printer.mmTOpx(self.upper_padding / ((points0[-4][1] - points0[-1][1])/(points0[-1][0] - points0[-4][0]))), points0[-1][1] - self.printer.mmTOpx(self.upper_padding * ((((points0[-4][1] - points0[-1][1])/(points0[-1][0] - points0[-4][0]))*((((points0[-4][1] - points0[-1][1])/(points0[-1][0] - points0[-4][0]))**2+1)**0.5))/(((points0[-4][1] - points0[-1][1])/(points0[-1][0] - points0[-4][0]))**2+1)))))
        points0 = (*points0, (points0[-1][0] + self.printer.mmTOpx(5), points0[-1][1]))

        points01 = self.CreateFirstElementCurve((x, y), self.techno_padding, -self.techno_padding)
        xy11 = (self.printer.mmTOpx((tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+tg_normal*(self.upper_padding+self.billetH), 0),
                self.printer.mmTOpx((tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD), self.techno_padding+self.upper_padding+self.billetH),
                self.printer.mmTOpx((tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)-(tg_normal*self.VOG-tg_Y*self.VOG), self.techno_padding+self.upper_padding+self.billetH+self.VOG),
                self.printer.mmTOpx(0, self.techno_padding*2+self.upper_padding+self.billetH+self.VOG+self.VBD))
        common_points1 = GetCommonPoints(points01, xy11[:2])
        xy11 = (min(common_points1, key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy11[0])))), *xy11[2:])
        points01 = (xy11[0],*points01[common_points1.index(xy11[0])+1:])
        points01 = (*points01, (points01[-1][0] + self.printer.mmTOpx(self.upper_padding / ((points01[-4][1] - points01[-1][1])/(points01[-1][0] - points01[-4][0]))), points01[-1][1] - self.printer.mmTOpx(self.upper_padding * ((((points01[-4][1] - points01[-1][1])/(points01[-1][0] - points01[-4][0]))*((((points01[-4][1] - points01[-1][1])/(points01[-1][0] - points01[-4][0]))**2+1)**0.5))/(((points01[-4][1] - points01[-1][1])/(points01[-1][0] - points01[-4][0]))**2+1)))))
        points01 = (*points01, (points01[-1][0]+self.printer.mmTOpx(5+self.techno_padding*2), points01[-1][1]))

        _line_vbu = [self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3, self.techno_padding+((self.upper_padding+self.billetH+self.VOG)-self.VBU)),
                     self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3, self.techno_padding+self.upper_padding+self.billetH+self.VOG),
                     ]
        xy_points1 = list(map(lambda cord: (cord[0] * (self.printer.mmTOpx(300) / 300) + points0[-1][0], cord[1] * (self.printer.mmTOpx(70) / 70) + points0[-1][1]), ((0, 0), (165, 55), (300, 70))))
        xy_points1.insert(1, min(GetCommonPoints(make_bezier(xy_points1)(self._ts), _line_vbu), key=lambda v: tuple(abs(numpy.array(v) - numpy.array(_line_vbu[0])))))
        xy_points1 = (points0[-1], _line_vbu[0], (xy_points1[0][0]+self.printer.mmTOpx(165), (xy_points1[0][1]+(xy_points1[1][1]-xy_points1[0][1]))+self.printer.mmTOpx(55)),
                      (xy_points1[0][0]+self.printer.mmTOpx(300), (xy_points1[0][1]+(xy_points1[1][1]-xy_points1[0][1]))+self.printer.mmTOpx(70)))
        points1 = xy_points1[0], *make_bezier(xy_points1[1:])(self._ts)

        _xy2 = (
            self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3-tg_mid*abs(self.VOG-self.VBU), self.techno_padding+((self.upper_padding+self.billetH+self.VOG)-self.VBU)),
            self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3, self.techno_padding+self.upper_padding+self.billetH))
        common_point = min(GetCommonPoints(points1[:2], _xy2), key=lambda v: tuple(abs(numpy.array(v) - numpy.array(_xy2[0]))))
        xy2 = (
            (self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3)*2-common_point[0], common_point[1]),
            self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3,self.techno_padding+self.upper_padding+self.billetH),
            self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3-tg_mid_with_pad*(self.VOG-self._mid_rise),self.techno_padding+self.upper_padding+self.billetH+(self.VOG-self._mid_rise)),
            self.printer.mmTOpx(((self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3-tg_mid*self.VOG)+self._radius+(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VOG)+(self.OG/2/2+5)/3+(self.ONK-self.OG)/2/3))/2, ((self.techno_padding+self.upper_padding+self.billetH+self.VOG)+self._radius+(self.techno_padding+self.upper_padding+self.billetH+self.VOG+self.VBD))/2),
            self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3+(self.ONK-self.OG)/2/3,self.techno_padding+self.upper_padding+self.billetH+self.VOG+self.VBD),
        )
        xy2 = *xy2[:2], *make_bezier(xy2[2:])(self._ts)

        xy21 = (
            (self.printer.mmTOpx(self.techno_padding)+xy2[0][0], xy2[0][1]-self.printer.mmTOpx(self.techno_padding)),
            self.printer.mmTOpx(self.techno_padding*2+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3,self.techno_padding+self.upper_padding+self.billetH),
            self.printer.mmTOpx(self.techno_padding*2+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3-tg_mid_with_pad*(self.VOG-self._mid_rise), self.techno_padding+self.upper_padding+self.billetH+(self.VOG-self._mid_rise)),
            self.printer.mmTOpx(((self.techno_padding*2+((self.techno_padding*2**0.5)-self.techno_padding)+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3+(self.ONK-self.OG)/2/3)+self._radius+(self.techno_padding*2+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VOG)+(self.OG/2/2+5)/3-tg_mid_with_pad*(self.VOG-self._mid_rise)))/2, ((self.techno_padding*2+self.upper_padding+self.billetH+self.VOG+self.VBD)+self._radius+(self.techno_padding+self.upper_padding+self.billetH+(self.VOG-self._mid_rise)))/2),
            self.printer.mmTOpx(self.techno_padding*2+((self.techno_padding*2**0.5)-self.techno_padding)+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3+(self.ONK-self.OG)/2/3, self.techno_padding*2+self.upper_padding+self.billetH+self.VOG+self.VBD),
        )
        xy21 = *xy21[:2], *make_bezier(xy21[2:])(self._ts)
        xy3 = (xy1[-1], xy2[-1])
        xy31 = (xy11[-1], xy21[-1])

        xy4 = (points0[-1], xy2[0])
        xy41 = (points01[-1], xy21[0])
        waistline = (xy1[1], self.printer.mmTOpx(self.techno_padding+(tg_normal*(self.VOG+self.VBD)-tg_Y*self.VBD)+(self.OG/2/2+5)/3-tg_mid_with_pad*(self.VOG-self._mid_rise),self.techno_padding+self.upper_padding+self.billetH+(self.VOG-self._mid_rise)))
        _line_vbu = xy_points1[1], _line_vbu[1]
        if min(xy21[0][1], points01[-1][1]) < 0:
            xy1, xy11, xy2, xy21, xy3, xy31, xy4, xy41, waistline, points0, points01 = tuple(tuple(map(lambda t: (t[0], t[1]+abs(min(xy21[0][1],points01[-1][1]))), v)) for v in (xy1, xy11, xy2, xy21, xy3, xy31, xy4, xy41, waistline, points0, points01))
        image = Image.new('RGBA', tuple(map(math.ceil, ((max((xy21[-1][0], xy21[0][0]))), xy21[-1][1]))), bg)
        sketch = ImageDraw.Draw(image)
        sketch.line(points0, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(points01, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy1, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy11, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy2, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy21, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy3, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy31, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy4, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy41, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(waistline, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))

        sketch.line(((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.3)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.8))
                     ), self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.35, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.65)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.8)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.65, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.65))
                     ), self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.text((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.8)), 'III', self.sketch_lines_color, font=self.font)
        return image

    def FourthElement(self, bg=(0, 0, 0, 0)):
        tg_Y = self.printer.mmTOpx(((self.OG-(self.OT-self.Y))/2/3/2))/self.printer.mmTOpx(self.VOG)
        tg_mid = self.printer.mmTOpx((self.OG-(self.OT-self.Y))/2/3/2)/self.printer.mmTOpx(self.VOG-self._mid_rise)
        tg_mid_with_pad = self.printer.mmTOpx((self.OG-(self.OT-self.Y))/2/3/2+self._mid_pad)/self.printer.mmTOpx(self.VOG-self._mid_rise)

        x, y = self.printer.mmTOpx((-(self.OG/2/2+5))+((self.ONK-self.OG)/2/3)+10+self.techno_padding, self.techno_padding+self.upper_padding)
        points_from_1st_element = make_bezier(tuple(map(lambda cord:
        (cord[0] * (self.printer.mmTOpx(self.billetW) / self.billetW) + x,
         cord[1] * (self.printer.mmTOpx(self.billetH) / self.billetH) + y),
        ((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))))(self._ts)
        points_from_1st_element = (*points_from_1st_element, (points_from_1st_element[-1][0] + self.printer.mmTOpx(self.upper_padding / ((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))), points_from_1st_element[-1][1] - self.printer.mmTOpx(self.upper_padding * ((((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))*((((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))**2+1)**0.5))/(((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))**2+1)))))
        points_from_1st_element = (*points_from_1st_element, (points_from_1st_element[-1][0] + self.printer.mmTOpx(5), points_from_1st_element[-1][1]))
        _line_vbu = (self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3, self.techno_padding+((self.upper_padding+self.billetH+self.VOG)-self.VBU)),
        self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3, self.techno_padding+((self.upper_padding+self.billetH+self.VOG))))
        xy_points1 = list(map(lambda cord: (cord[0] * (self.printer.mmTOpx(300) / 300) + points_from_1st_element[-1][0], cord[1] * (self.printer.mmTOpx(70) / 70) + points_from_1st_element[-1][1]), ((0, 0), (165, 55), (300, 70))))
        xy_points1.insert(1, min(GetCommonPoints(make_bezier(xy_points1)(self._ts), _line_vbu), key=lambda v: tuple(abs(numpy.array(v) - numpy.array(_line_vbu[0])))))

        points0 = (xy_points1[0], _line_vbu[0],
                    (xy_points1[0][0]+self.printer.mmTOpx(165), (xy_points1[0][1]+(xy_points1[1][1]-xy_points1[0][1]))+self.printer.mmTOpx(55)),
                    (xy_points1[0][0]+self.printer.mmTOpx(300), (xy_points1[0][1]+(xy_points1[1][1]-xy_points1[0][1]))+self.printer.mmTOpx(70)))

        xy_points1 = list(map(lambda cord: (cord[0] * (self.printer.mmTOpx(300) / 300) + (points_from_1st_element[-1][0]-self.printer.mmTOpx(self.techno_padding)), cord[1] * (self.printer.mmTOpx(70) / 70) + (points_from_1st_element[-1][1]-self.printer.mmTOpx(self.techno_padding))), ((0, 0), (165, 55), (300, 70))))
        xy_points1.insert(1, min(GetCommonPoints(make_bezier(xy_points1)(self._ts), _line_vbu), key=lambda v: tuple(abs(numpy.array(v) - numpy.array(_line_vbu[0])))))

        points01 = (xy_points1[0], _line_vbu[0],
                    (xy_points1[0][0]+self.printer.mmTOpx(165), (xy_points1[0][1]+(xy_points1[1][1]-xy_points1[0][1]))+self.printer.mmTOpx(55)),
                    (xy_points1[0][0]+self.printer.mmTOpx(300), (xy_points1[0][1]+(xy_points1[1][1]-xy_points1[0][1]))+self.printer.mmTOpx(70)))
        xy1 = (self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3-tg_mid*abs(self.VOG-self.VBU), self.techno_padding+((self.upper_padding+self.billetH+self.VOG)-self.VBU)),
               self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3, self.techno_padding+self.upper_padding+self.billetH),
               self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3+tg_mid_with_pad*(self.VOG-self._mid_rise), self.techno_padding+self.upper_padding+self.billetH+(self.VOG-self._mid_rise)),
               self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3+tg_mid*self.VOG, self.techno_padding+self.upper_padding+self.billetH+self.VOG),
               self.printer.mmTOpx((self.techno_padding+(self.ONK-self.OG)/2/3+tg_mid*self.VOG-self._radius+self.techno_padding)/2, (self.techno_padding+self.upper_padding+self.billetH+self.VOG-self._radius+self.techno_padding+self.upper_padding+self.billetH+self.VOG+self.VBD)/2),
               self.printer.mmTOpx(self.techno_padding, self.techno_padding+self.upper_padding+self.billetH+self.VOG+self.VBD),
               )
        common_points0 = GetCommonPoints(points0, xy1[:2])

        xy1 = (min(common_points0, key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy1[0])))), *xy1[1:])
        xy1 = (*xy1[:2], *make_bezier(xy1[2:])(self._ts))
        xy11 = ((xy1[0][0]-self.printer.mmTOpx(self.techno_padding), xy1[0][1]-self.printer.mmTOpx(self.techno_padding*2**0.5)),
                self.printer.mmTOpx((self.ONK-self.OG)/2/3, self.techno_padding+self.upper_padding+self.billetH),
                self.printer.mmTOpx((self.ONK-self.OG)/2/3+tg_mid_with_pad*(self.VOG-self._mid_rise), self.techno_padding+self.upper_padding+self.billetH+(self.VOG-self._mid_rise)),
                self.printer.mmTOpx((self.ONK-self.OG)/2/3+tg_mid*self.VOG, self.techno_padding+self.upper_padding+self.billetH+self.VOG),
                self.printer.mmTOpx(((self.ONK-self.OG)/2/3+tg_mid*self.VOG-self._radius)/2, (self.techno_padding+self.upper_padding+self.billetH+self.VOG-self._radius+self.techno_padding+self.upper_padding+self.billetH+self.VOG+self.VBD)/2),
                self.printer.mmTOpx(0, self.techno_padding*2+self.upper_padding+self.billetH+self.VOG+self.VBD),
                )
        xy11 = (*xy11[:2], *make_bezier(xy11[2:])(self._ts))

        _line_from_fifth_element = (self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3+(self.OG/2/2-5)/2-tg_Y*(self.upper_padding+self.billetH), self.techno_padding),
               self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3+(self.OG/2/2-5)/2 , self.techno_padding+self.upper_padding+self.billetH))
        _line_from_fifth_element = min(GetCommonPoints(points0[1:], _line_from_fifth_element), key=lambda v: tuple(abs(numpy.array(v) - numpy.array(_line_from_fifth_element[0])))), _line_from_fifth_element[1]
        xy2 = ((self.printer.mmTOpx((self.techno_padding+(self.ONK-self.OG)/2/3+(self.OG/2/2-5)/2)*2)-_line_from_fifth_element[0][0], _line_from_fifth_element[0][1]),
               self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3+(self.OG/2/2-5)/2-tg_Y*self.VOG, self.techno_padding+self.upper_padding+self.billetH+self.VOG),
               self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3+(self.OG/2/2-5)/2+(self.ONK-self.OG)/2/3/2, self.techno_padding+self.upper_padding+self.billetH+self.VOG+self.VBD))

        xy21 = ((self.printer.mmTOpx(self.techno_padding)+xy2[0][0], xy2[0][1]-self.printer.mmTOpx(self.techno_padding)),
                self.printer.mmTOpx(self.techno_padding*2+(self.ONK-self.OG)/2/3+(self.OG/2/2-5)/2-tg_Y*self.VOG, self.techno_padding+self.upper_padding+self.billetH+self.VOG),
                self.printer.mmTOpx(self.techno_padding*2+(self.ONK-self.OG)/2/3+(self.OG/2/2-5)/2+(self.ONK-self.OG)/2/3/2, self.techno_padding*2+self.upper_padding+self.billetH+self.VOG+self.VBD))
        xy3 = (xy1[0], xy2[0])
        xy31 = (xy11[0], xy21[0])
        xy4 = (xy1[-1], xy2[-1])
        xy41 = (xy11[-1], xy21[-1])
        waistline = (self.printer.mmTOpx(self.techno_padding+(self.ONK-self.OG)/2/3+tg_mid_with_pad*(self.VOG-self._mid_rise), self.techno_padding+self.upper_padding+self.billetH+(self.VOG-self._mid_rise)), xy2[1])
        if xy11[0][0] < xy11[-1][0]:
            xy1, xy11, xy2, xy21, xy3, xy31, xy4, xy41, waistline, points0, points01 = tuple(tuple(map(lambda t: (t[0]+abs(xy11[-1][0]-xy11[0][0]), t[1]), v)) for v in (xy1, xy11, xy2, xy21, xy3, xy31, xy4, xy41, waistline, points0, points01))
        if min(xy11[0][1], xy21[0][1]) < 0:
            xy1, xy11, xy2, xy21, xy3, xy31, xy4, xy41, waistline, points0, points01 = tuple(tuple(map(lambda t: (t[0], t[1]-min(xy11[0][1], xy21[0][1])), v)) for v in (xy1, xy11, xy2, xy21, xy3, xy31, xy4, xy41, waistline, points0, points01))
        image = Image.new('RGBA', tuple(map(math.ceil, ((xy21[0][0] if xy21[0][0] > xy21[-1][0] else xy21[-1][0]), xy21[-1][1]))), bg)
        sketch = ImageDraw.Draw(image)

        sketch.line(xy1, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy11, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy2, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy21, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy3, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy31, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy4, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy41, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(waistline, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.3)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.8))
                     ), self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.35, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.65)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.8)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.65, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.65))
                     ), self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.text((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.8)), 'IV', self.sketch_lines_color, font=self.font)
        return image

    def FifthElement(self, bg=(0, 0, 0, 0)):
        tg_Y = self.printer.mmTOpx(((self.OG-(self.OT-self.Y))/2/3/2/2))/self.printer.mmTOpx(self.VOG)

        x, y = self.printer.mmTOpx(-((self.OG/2/2+5)+(self.OG/2/2-5)/2+(self.ONK-self.OG)/2/3/2)+10+self.techno_padding, self.techno_padding+self.upper_padding)
        points_from_1st_element = make_bezier(tuple(map(lambda cord:
        (cord[0] * (self.printer.mmTOpx(self.billetW) / self.billetW) + x, 
         cord[1] * (self.printer.mmTOpx(self.billetH) / self.billetH) + y),
         ((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))))(self._ts)
        points_from_1st_element = (*points_from_1st_element, (points_from_1st_element[-1][0] + self.printer.mmTOpx(self.upper_padding / ((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))), points_from_1st_element[-1][1] - self.printer.mmTOpx(self.upper_padding * ((((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))*((((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))**2+1)**0.5))/(((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))**2+1)))))
        points_from_1st_element = (*points_from_1st_element, (points_from_1st_element[-1][0] + self.printer.mmTOpx(5), points_from_1st_element[-1][1]))
        _line_vbu = (self.printer.mmTOpx(-((self.OG/2/2-5)/2)+(self.ONK-self.OG)/2/3/2+self.techno_padding, self.techno_padding+((self.upper_padding+self.billetH+self.VOG)-self.VBU)),
                     self.printer.mmTOpx(-((self.OG/2/2-5)/2)+(self.ONK-self.OG)/2/3/2+self.techno_padding, self.techno_padding+((self.upper_padding+self.billetH+self.VOG))))

        xy_points1 = list(map(lambda cord: (cord[0] * (self.printer.mmTOpx(300) / 300) + (points_from_1st_element[-1][0]-self.printer.mmTOpx(self.techno_padding)), cord[1] * (self.printer.mmTOpx(70) / 70) + (points_from_1st_element[-1][1]-self.printer.mmTOpx(self.techno_padding))), ((0, 0), (165, 55), (300, 70))))
        xy_points1.insert(1, min(GetCommonPoints(make_bezier(xy_points1)(self._ts), _line_vbu), key=lambda v: tuple(abs(numpy.array(v) - numpy.array(_line_vbu[0])))))

        points1 = (xy_points1[0], _line_vbu[0],
                    (xy_points1[0][0]+self.printer.mmTOpx(165), (xy_points1[0][1]+(xy_points1[1][1]-xy_points1[0][1]))+self.printer.mmTOpx(55)),
                    (xy_points1[0][0]+self.printer.mmTOpx(300), (xy_points1[0][1]+(xy_points1[1][1]-xy_points1[0][1]))+self.printer.mmTOpx(70)))
        points1 = points1[0], *make_bezier(points1[1:])(self._ts)

        xy1 = (self.printer.mmTOpx(self.techno_padding+((self.ONK-self.OG)/2/3/2-tg_Y*(self.billetH+self.upper_padding)), self.techno_padding),
        self.printer.mmTOpx(self.techno_padding+((self.ONK-self.OG)/2/3/2+tg_Y*(self.VOG)), self.techno_padding+self.upper_padding+self.billetH+self.VOG),
        self.printer.mmTOpx(self.techno_padding, self.techno_padding+self.upper_padding+self.billetH+self.VOG+self.VBD),
        )
        xy1 = (min(GetCommonPoints(points1[1:], xy1[:2]), key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy1[0])))), *xy1[1:])

        xy11 = ((xy1[0][0]-self.printer.mmTOpx(self.techno_padding), xy1[0][1]-self.printer.mmTOpx(self.techno_padding*2**0.5)),
        self.printer.mmTOpx(((self.ONK-self.OG)/2/3/2+tg_Y*(self.VOG)), self.techno_padding+self.upper_padding+self.billetH+self.VOG),
        self.printer.mmTOpx(0, self.techno_padding*2+self.upper_padding+self.billetH+self.VOG+self.VBD),
        )

        xy2 = [self.printer.mmTOpx(self.techno_padding+((self.ONK-self.OG)/2/3/2+(self.OG/2/2-5)/2), self.techno_padding),
        [*self.printer.mmTOpx(self.techno_padding+((self.ONK-self.OG)/2/3/2+(self.OG/2/2-5)/2), self.techno_padding+self.upper_padding+self.billetH+self.VOG+self.VBD)]]
        xy2 = (xy2[0][0], min(GetCommonPoints(points1[1:], xy2), key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy2[0]))))[1]), tuple(xy2[1])

        xy21 = ((self.printer.mmTOpx(self.techno_padding*2+((self.ONK-self.OG)/2/3/2+(self.OG/2/2-5)/2)), xy2[0][1]-self.printer.mmTOpx(self.techno_padding)),
        self.printer.mmTOpx(self.techno_padding*2+((self.ONK-self.OG)/2/3/2+(self.OG/2/2-5)/2), self.techno_padding*2+self.upper_padding+self.billetH+self.VOG+self.VBD))

        xy3 = xy1[0], xy2[0]
        xy31 = xy11[0], xy21[0]

        xy4 = xy1[-1], xy2[-1]
        xy41 = xy11[-1], xy21[-1]

        waistline = xy1[1], (xy2[0][0], self.printer.mmTOpx(self.techno_padding+self.upper_padding+self.billetH+self.VOG))

        image = Image.new('RGBA', self.printer.mmTOpx(self.techno_padding*2+(self.ONK-self.OG)/2/3/2+(self.OG/2/2-5)/2, self.techno_padding*2+self.upper_padding+self.billetH+self.VOG+self.VBD), bg)
        sketch = ImageDraw.Draw(image)
        sketch.line(xy1, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy11, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy2, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy21, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy3, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy31, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy4, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy41, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(waistline, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(waistline, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.3)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.8))
                     ), self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.35, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.65)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.8)),
                     (waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.65, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.65))
                     ), self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.text((waistline[0][0]+(waistline[1][0]-waistline[0][0])*0.5, self.printer.mmTOpx(self.techno_padding + self.upper_padding + self.billetH + self.VOG * 0.8)), 'V', self.sketch_lines_color, font=self.font)
        return image

    def SixthElement(self, bg=(0, 0, 0, 0)):
        image = Image.new('RGBA', (self.printer.mmTOpx(self.techno_padding * 2 + 34), self.printer.mmTOpx(
            self.techno_padding * 2 + self.upper_padding + self.billetH + self.VOG + self.VBD)), bg)
        sketch = ImageDraw.Draw(image)

        x, y = self.printer.mmTOpx(-(self.OG/2)+10, self.techno_padding+self.upper_padding)
        points_from_1st_element = make_bezier(tuple(map(lambda cord:
        (cord[0] * (self.printer.mmTOpx(self.billetW) / self.billetW) + x,
         cord[1] * (self.printer.mmTOpx(self.billetH) / self.billetH) + y),
         ((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))))(self._ts)
        points_from_1st_element = (*points_from_1st_element, (points_from_1st_element[-1][0] + self.printer.mmTOpx(self.upper_padding / ((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))), points_from_1st_element[-1][1] - self.printer.mmTOpx(self.upper_padding * ((((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))*((((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))**2+1)**0.5))/(((points_from_1st_element[-4][1] - points_from_1st_element[-1][1])/(points_from_1st_element[-1][0] - points_from_1st_element[-4][0]))**2+1)))))
        points_from_1st_element = (*points_from_1st_element, (points_from_1st_element[-1][0] + self.printer.mmTOpx(5), points_from_1st_element[-1][1]))
        _line_vbu = (self.printer.mmTOpx(-(self.OG/2/2-5)+self.techno_padding, self.techno_padding+((self.upper_padding+self.billetH+self.VOG)-self.VBU)),
                     self.printer.mmTOpx(-(self.OG/2/2-5)+self.techno_padding, self.techno_padding+(self.upper_padding+self.billetH+self.VOG)))

        xy_points1 = list(map(lambda cord: (cord[0] * (self.printer.mmTOpx(300) / 300) + (points_from_1st_element[-1][0]-self.printer.mmTOpx(self.techno_padding)), cord[1] * (self.printer.mmTOpx(70) / 70) + (points_from_1st_element[-1][1]-self.printer.mmTOpx(self.techno_padding))), ((0, 0), (165, 55), (300, 70))))
        xy_points1.insert(1, min(GetCommonPoints(make_bezier(xy_points1)(self._ts), _line_vbu), key=lambda v: tuple(abs(numpy.array(v) - numpy.array(_line_vbu[0])))))

        points1 = (xy_points1[0], _line_vbu[0],
                    (xy_points1[0][0]+self.printer.mmTOpx(165), (xy_points1[0][1]+(xy_points1[1][1]-xy_points1[0][1]))+self.printer.mmTOpx(55)),
                    (xy_points1[0][0]+self.printer.mmTOpx(300), (xy_points1[0][1]+(xy_points1[1][1]-xy_points1[0][1]))+self.printer.mmTOpx(70)))

        xy1 = [self.printer.mmTOpx(self.techno_padding, self.techno_padding),
               (self.printer.mmTOpx(self.techno_padding, self.techno_padding+self.upper_padding+self.billetH+self.VOG+self.VBD))]
        xy1 = (xy1[0][0], min(GetCommonPoints(points1[1:], xy1), key=lambda v: tuple(abs(numpy.array(v) - numpy.array(xy1[0]))))[1]), tuple(xy1[1])
        xy11 = (
            (
            xy1[0][0] - self.printer.mmTOpx(self.techno_padding), xy1[0][1] - self.printer.mmTOpx(self.techno_padding)),
            (
            xy1[1][0] - self.printer.mmTOpx(self.techno_padding), xy1[1][1] + self.printer.mmTOpx(self.techno_padding)),
        )
        xy2 = ((self.printer.mmTOpx(self.techno_padding+34), xy1[0][1]),
               (self.printer.mmTOpx(self.techno_padding+34), xy1[1][1]),
               )
        xy21 = ((self.printer.mmTOpx(self.techno_padding*2+34), xy1[0][1]-self.printer.mmTOpx(self.techno_padding)),
                (self.printer.mmTOpx(self.techno_padding*2+34), xy1[1][1]+self.printer.mmTOpx(self.techno_padding)),
                )
        xy3 = xy1[0], xy2[0]
        xy31 = xy11[0], xy21[0]

        xy4 = xy1[-1], xy2[-1]
        xy41 = xy11[-1], xy21[-1]

        sketch.line(xy1, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy11, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy2, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy21, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy3, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy31, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy4, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        sketch.line(xy41, self.sketch_lines_color, self.printer.mmTOpx(self.sketch_lines_width))
        pad = ((xy1[1][1] - xy1[0][1]) - self.printer.mmTOpx(10 * 2 + 6 * 9)) / 8
        for n in range(9):
            sketch.line((
                (self.printer.mmTOpx(self.techno_padding) + (xy3[1][0] - xy3[0][0]) / 2,
                 self.printer.mmTOpx(10 + 6 * n) + xy1[0][1] + pad * n),
                (self.printer.mmTOpx(self.techno_padding) + (xy3[1][0] - xy3[0][0]) / 2,
                 self.printer.mmTOpx(10 + 6 * (n + 1)) + xy1[0][1] + pad * n)), self.sketch_lines_color,
                self.printer.mmTOpx(self.sketch_lines_width))
            sketch.line((
                (self.printer.mmTOpx(self.techno_padding - 3) + (xy3[1][0] - xy3[0][0]) / 2,
                 self.printer.mmTOpx(10 + 6 * (n + 1) - 3) + xy1[0][1] + pad * n),
                (self.printer.mmTOpx(self.techno_padding + 3) + (xy3[1][0] - xy3[0][0]) / 2,
                 self.printer.mmTOpx(10 + 6 * (n + 1) - 3) + xy1[0][1] + pad * n)), self.sketch_lines_color,
                self.printer.mmTOpx(self.sketch_lines_width))
        return image

if __name__ == '__main__':
    # self.billetW = 100
    # self.billetH = 62
    # self._ts = [t / 100.0 for t in range(101)]
    # image = Image.new('RGBA', (self.billetW, self.billetH), (255,255,255))
    # ImageDraw.Draw(image).line(make_bezier(((0, 12), (5, 65), (50, 75), (90, 65), (100, 0)))(self._ts), 0, 1)
    # image.save('blt.png')
    Sketch = DrawSketch(OG=760, OT=640, ONK=850, VOG=120, VBU=220, VBD=120, Y=50, printer=Printer('monitorHDC'))
    # Sketch.FirstElement((255,255,255)).show()
    # Sketch.SecondElement((255, 255, 255)).show()
    Sketch.ThirdElement((255, 255, 255)).show()
    # Sketch.FourthElement((255, 255, 255)).show()
    # Sketch.FifthElement((255, 255, 255)).show()
    # Sketch.SixthElement((255, 255, 255)).show()
