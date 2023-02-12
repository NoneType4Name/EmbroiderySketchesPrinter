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


image = Image.new("L", printable_area, 255)
drawImage = ImageDraw.Draw(image)
# drawImage.rectangle((0,0,*image.size), outline=0, width=MillimetersToPixels(1))
DrawCircle(drawImage, MillimetersToPixels(100), MillimetersToPixels(100), MillimetersToPixels(5), outline=0, width=10)

image = image.rotate(90 if image.size[0] > image.size[1] else 0)
hDC.StartDoc('Graphic print.')
hDC.StartPage()

ImageWin.Dib(image).draw(hDC.GetHandleOutput(), (0, 0, *printable_area))
ImageWin.Dib(image).draw(hDC.GetHandleOutput(), (0, 0, *printable_area))

hDC.EndPage()
hDC.EndDoc()
hDC.DeleteDC()
