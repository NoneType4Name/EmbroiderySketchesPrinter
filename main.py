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

        # self.CONSOLE_HWND = 0
        # self.CONSOLE_PROCESS = None
        # self.CONSOLE_PID = 0
        self.GAME_HWND = 0
        self.GAME_PROCESS = None
        self.GAME_PID = 0
        self.RUN = False
        self.size = None
        self.window_size = None
        self.flag = None
        self.depth = None
        self.display = None
        self.vsync = None
        self.caption = None
        self.screen = None
        self.clock = pygame.time.Clock()
        self.Scene = None

    def init(self, caption: str, icon_path: str, size: SIZE, flag=0, depth=0, display=0, vsync=0):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.window_size = size
        self.size = FULL_SIZE
        self.flag = flag
        self.depth = depth
        self.display = display
        self.vsync = vsync
        self.caption = caption
        self.screen = pygame.display.set_mode(self.window_size, self.flag, self.depth)
        pygame.display.set_icon(pygame.image.load(icon_path))
        pygame.display.set_caption(caption)
        pygame.font.init()
        pygame.scrap.init()
        self.GAME_HWND = pygame.display.get_wm_info()['window']
        self.GAME_PID = get_pid_by_hwnd(self.GAME_HWND)
        self.GAME_PROCESS = psutil.Process(self.GAME_PID)
        self.Scene = SceneMain(self)
        self.RUN = True

    def update(self):
        self.UpdateEvents()
        self.Scene.update()
        self.screen.blit(pygame.transform.smoothscale(self.Scene.image, self.window_size), (0, 0))
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
            elif event.type == pygame.WINDOWRESIZED:
                self.window_size = SIZE(pygame.display.get_window_size())

# notif = GUI.PrintWindow(None, (0, 0, 300, 500), 0.1, "Печать заготовок.", (255,255,255), (100, 100, 100), (255, 0, 0), 1, (200, 200, 200))
