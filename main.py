from functions import *
from scene.main import SceneMain


class Window:
    def __init__(self, run_from: str, main_dir: str, exe: bool):
        self.PARENT_PATH = run_from
        self.MAIN_DIR = main_dir
        self.isEXE = exe
        self.mouse_pos = (0, 0)
        self.mouse_right_press = False
        self.mouse_right_release = False
        self.mouse_left_press = False
        self.mouse_left_release = False
        self.mouse_middle_press = False
        self.mouse_middle_release = False
        self.mouse_wheel_x = 0
        self.mouse_wheel_y = 0
        self.cursor = pygame.SYSTEM_CURSOR_ARROW
        self.events = []

        self.FPS = GAME_FPS

        self.GAME_HWND = 0
        self.GAME_PROCESS = None
        self.GAME_PID = 0
        self.RUN = False
        self.size = None
        self.flag = None
        self.depth = None
        self.display = None
        self.vsync = None
        self.caption = None
        self.screen = None
        self.clock = pygame.time.Clock()
        self.Scene = None

        self.Properties = getFileProperties(sys.executable)
        self.Version = Version(str(self.Properties.FileVersion))

    def init(self, caption: str, icon_path: str, size: SIZE, flag=0, depth=0, display=0, vsync=0):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.size = size
        self.flag = flag
        self.depth = depth
        self.display = display
        self.vsync = vsync
        self.caption = caption
        self.screen = pygame.display.set_mode(self.size, self.flag, self.depth, self.display, self.vsync)
        pygame.display.set_icon(pygame.image.load(icon_path))
        pygame.display.set_caption(caption)
        pygame.font.init()
        pygame.scrap.init()
        self.GAME_HWND = pygame.display.get_wm_info()['window']
        work_area = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(self.GAME_HWND, byref(work_area))
        win32gui.SetWindowPos(self.GAME_HWND, win32con.HWND_TOP, (work_area.left-PANEL_SIZE.w//2), -1 if PANEL_SIZE.h >= 0 else -PANEL_SIZE.h, self.size.w, self.size.h, 0)
        self.GAME_PID = get_pid_by_hwnd(self.GAME_HWND)
        self.GAME_PROCESS = psutil.Process(self.GAME_PID)
        self.Scene = SceneMain(self)
        self.RUN = True

    def update(self):
        self.UpdateEvents()
        self.Scene.update()
        self.screen.blit(self.Scene.image, (0, 0))
        if type(self.cursor) is int:
            pygame.mouse.set_cursor(self.cursor)
            pygame.mouse.set_visible(True)
        elif type(self.cursor) is bool:
            pygame.mouse.set_visible(self.cursor)
        pygame.display.flip()
        self.clock.tick(self.FPS)

    def UpdateEvents(self):
        self.mouse_left_release = False
        self.mouse_right_release = False
        self.mouse_middle_release = False

        self.mouse_wheel_x = 0
        self.mouse_wheel_y = 0

        self.mouse_pos = pygame.mouse.get_pos()
        self.cursor = pygame.SYSTEM_CURSOR_ARROW
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.RUN = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    self.mouse_left_press = event.pos
                    self.mouse_left_release = False
                elif event.button == pygame.BUTTON_RIGHT:
                    self.mouse_right_press = event.pos
                    self.mouse_right_release = False
                elif event.button == pygame.BUTTON_MIDDLE:
                    self.mouse_middle_press = event.pos
                    self.mouse_middle_release = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    self.mouse_left_press = False
                    self.mouse_left_release = event.pos
                elif event.button == pygame.BUTTON_RIGHT:
                    self.mouse_right_press = False
                    self.mouse_right_release = event.pos
                elif event.button == pygame.BUTTON_MIDDLE:
                    self.mouse_middle_press = False
                    self.mouse_middle_release = event.pos
            elif event.type == pygame.MOUSEWHEEL:
                self.mouse_wheel_x = event.x
                self.mouse_wheel_y = event.y

            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0] or event.touch:
                    self.mouse_wheel_x = event.rel[0]
                    self.mouse_wheel_y = event.rel[1]
