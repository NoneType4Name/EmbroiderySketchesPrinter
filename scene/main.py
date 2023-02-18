import GUI
from functions import *


class SceneMain:
    def __init__(self, parent):
        self.type = MAIN
        self.parent = parent
        self.size = parent.size
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.notifications = pygame.sprite.Group()
        self.sketch = None
        self.updated_data = False
        self.events = self.parent.events

        self.mouse_left_press = self.parent.mouse_left_press
        self.mouse_right_press = self.parent.mouse_right_press
        self.mouse_middle_press = self.parent.mouse_middle_press

        self.mouse_left_release = self.parent.mouse_left_release
        self.mouse_right_release = self.parent.mouse_right_release
        self.mouse_middle_release = self.parent.mouse_middle_release

        self.mouse_wheel_x = self.parent.mouse_wheel_x
        self.mouse_wheel_y = self.parent.mouse_wheel_y

        self.mouse_pos = self.parent.mouse_pos
        self.cursor = self.parent.cursor

        self.data_panel = GUI.DataPanel(
            self.parent,
            (-(self.size.w * 0.2 + self.size.h * 0.8) * 0.003*8, self.size.h * 0.05, self.size.w * 0.2, self.size.h * 0.9),
            (100, 200, 200), 0.2, (self.size.w * 0.2 + self.size.h * 0.8) * 0.003, (255,255,255)
        )

        self.print_button = GUI.Button(self,
                                       (self.size.w * 0.45, self.size.h * 0.7, self.size.w * 0.1, self.size.h * 0.05),
                                       (self.size.w * 0.45, self.size.h * 0.7, self.size.w * 0.1, self.size.h * 0.05),
                                       (self.size.w * 0.45, self.size.h * 0.7, self.size.w * 0.1, self.size.h * 0.05),
                                       'Печать выкройки.',
                                       'Печать выкройки.',
                                       (255, 255, 255),
                                       (202, 219, 252),
                                       (0, 0, 0),
                                       (0, 0, 0),
                                       (102, 153, 255),
                                       (0, 0, 255),
                                       (self.size.w * 0.05 + self.size.h * 0.05) * 0.01,
                                       .4,
                                       (self.size.w * 0.05 + self.size.h * 0.05) * 0.01,
                                       .4,
                                       func=lambda _:
                                       self.notifications.add(GUI.PrintWindow(
                                           self,
                                           (random.randrange(0, int(self.size.w * 0.7)), random.randrange(0, int(self.size.h * 0.6)), self.size.w * 0.3, self.size.h * 0.4),
                                           "Печать заготовок.", None, 0.1, (255,255,255), (100, 100, 100), (255, 0, 0), 1, (100, 200, 200),
                                           1, (100, 100, 100))
                                       ))
        self.NewSketch()

    def update(self):
        last_data = tuple(self.data_panel.data)
        self.image.fill((200, 200, 200))
        self.image.blit(self.sketch, (numpy.array(self.size) - self.sketch.get_size())/2)
        self.image.blit(self.print_button.image, self.print_button.rect.topleft)
        self.image.blit(self.data_panel.image, self.data_panel.rect.topleft)
        if self.notifications.sprites():
            self.notifications.update()
            self.notifications.draw(self.image)
        else:
            self.data_panel.update()
            self.print_button.update()
            if list(last_data) != self.data_panel.data:
                self.NewSketch()
        #
        # self.events = self.parent.events
        #
        # self.mouse_left_press = self.parent.mouse_left_press
        # self.mouse_right_press = self.parent.mouse_right_press
        # self.mouse_middle_press = self.parent.mouse_middle_press
        #
        # self.mouse_left_release = self.parent.mouse_left_release
        # self.mouse_right_release = self.parent.mouse_right_release
        # self.mouse_middle_release = self.parent.mouse_middle_release
        #
        # self.mouse_wheel_x = self.parent.mouse_wheel_x
        # self.mouse_wheel_y = self.parent.mouse_wheel_y
        #
        # self.mouse_pos = self.parent.mouse_pos
        # self.parent.cursor = self.cursor
        #
        # self.parent.mouse_left_release = self.mouse_left_release
        # self.parent.mouse_right_release = self.mouse_right_release
        # self.parent.mouse_middle_release = self.mouse_middle_release
        #
        # self.parent.mouse_left_press = self.mouse_left_press
        # self.parent.mouse_right_press = self.mouse_right_press
        # self.parent.mouse_middle_press = self.mouse_middle_press
        #
        # self.parent.mouse_wheel_x = self.mouse_wheel_x
        # self.parent.mouse_wheel_y = self.mouse_wheel_y
        #
        # self.parent.mouse_pos = self.mouse_pos
        return self.image

    def NewSketch(self):
        images = DrawSketch(*tuple(map(int, self.data_panel.data)), printer=Printer('monitorHDC')).Elements([1,2])
        w = sum(map(lambda i: i.size[0], images))
        h = max(map(lambda i: i.size[1], images))
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        x = 0
        for i in images:
            im.paste(i, (x, h - i.size[1]))
            x += i.size[0]
        if im.size[0] > self.size[0]:
            im = im.resize((self.size[0], int(im.size[1] * (self.size[0] / im.size[0]))), Image.ANTIALIAS)
        if im.size[1] > self.size[1]:
            im = im.resize((int(im.size[0] * (self.size[1] / im.size[1])), self.size[1]), Image.ANTIALIAS)
        self.sketch = pygame.image.fromstring(im.tobytes(), im.size, im.mode)
