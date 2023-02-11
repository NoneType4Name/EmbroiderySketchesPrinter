from main import *

if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
    MAIN_DIR = os.path.dirname(sys.executable)
    EXE = True
else:
    os.chdir(os.path.split(__file__)[0])
    MAIN_DIR = os.path.dirname(__file__)
    EXE = False

window = Window(__file__, MAIN_DIR, EXE)
window.init("Embroidery Sketches Printer", f"{DATAS_FOLDER_NAME}/ico.png", SIZE((FULL_SIZE.w * 0.7, FULL_SIZE.h * 0.7)))
while window.RUN:
    window.update()
