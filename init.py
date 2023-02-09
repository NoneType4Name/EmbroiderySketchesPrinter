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
window.init("Embroidery Sketches Printer", "assets/ico.png", FULL_SIZE, pygame.RESIZABLE)
while window.RUN:
    window.update()
