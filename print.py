import win32print
import win32ui
from PIL import Image, ImageWin, ImageDraw
from win32con import *
# all used constant for printer get from: learn.microsoft.com/windows/win32/api/wingdi/nf-wingdi-getdevicecaps

hDC = win32ui.CreateDC()
hDC.CreatePrinterDC(win32print.GetDefaultPrinter())
printable_area = hDC.GetDeviceCaps(HORZRES), hDC.GetDeviceCaps(VERTRES)
printer_size = hDC.GetDeviceCaps(PHYSICALWIDTH), hDC.GetDeviceCaps(PHYSICALHEIGHT)
DPI = hDC.GetDeviceCaps(LOGPIXELSX)


def MillimetersToPixels(mm: int) -> int:
    return round((mm * DPI) / 25.4)


def DrawCircle(img, x, y, r, fill=None, outline=None, width=1):
    img.ellipse((x-r, y-r, x+r, y+r), fill, outline, width)



# image = image.rotate(90 if image.size[0] > image.size[1] and printable_area[0] > printable_area[1] else 0)
# hDC.StartDoc('Graphic print.')
# hDC.StartPage()
#
# ImageWin.Dib(image).draw(hDC.GetHandleOutput(), (0, 0, *image.size))
#
# hDC.EndPage()
# hDC.EndDoc()
# hDC.DeleteDC()
