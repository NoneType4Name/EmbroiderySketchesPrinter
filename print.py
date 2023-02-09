# import win32print
# import win32ui
# from PIL import Image, ImageWin
#
# #
# # Constants for GetDeviceCaps
# #
# #
# # HORZRES / VERTRES = printable area
# #
# HORZRES = 8
# VERTRES = 10
# #
# # LOGPIXELS = dots per inch
# #
# LOGPIXELSX = 88
# LOGPIXELSY = 90
# #
# # PHYSICALWIDTH/HEIGHT = total area
# #
# PHYSICALWIDTH = 110
# PHYSICALHEIGHT = 111
#
# #
# # PHYSICALOFFSETX/Y = left / top margin
# #
# PHYSICALOFFSETX = 112
# PHYSICALOFFSETY = 113
# file_name = "graph.png"
# hDC = win32ui.CreateDC()
# hDC.CreatePrinterDC(win32print.GetDefaultPrinter())
# printable_area = hDC.GetDeviceCaps(HORZRES), hDC.GetDeviceCaps(VERTRES)
# printer_size = hDC.GetDeviceCaps(PHYSICALWIDTH), hDC.GetDeviceCaps(PHYSICALHEIGHT)
# printer_margins = hDC.GetDeviceCaps(PHYSICALOFFSETX), hDC.GetDeviceCaps(PHYSICALOFFSETY)
# bmp = Image.open(file_name)
# if bmp.size[0] > bmp.size[1]:
#     bmp = bmp.rotate(90)
#
# ratios = [printer_size[0] / bmp.size[0], printer_size[1] / bmp.size[1]]
# scale = min(ratios)
# hDC.StartDoc(file_name)
# hDC.StartPage()
#
# dib = ImageWin.Dib(bmp)
# scaled_width, scaled_height = [int(scale * i) for i in bmp.size]
# x1 = round((printer_size[0] - scaled_width) / 2)
# y1 = round((printer_size[1] - scaled_height) / 2)
# x2 = x1 + scaled_width
# y2 = y1 + scaled_height
# dib.draw(hDC.GetHandleOutput(), (x1, y1, x2, y2))
#
# hDC.EndPage()
# hDC.EndDoc()
# hDC.DeleteDC()
from PIL import Image, ImageDraw
image = Image.new("L", (1000, 1000), 255)
drawImage = ImageDraw.Draw(image)
drawImage.arc((0, 0, 100, 100), 30, 180, 0)
image.show()
