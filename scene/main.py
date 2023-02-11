import GUI
from functions import *


class SceneMain:
    def __init__(self, parent):
        self.type = MAIN
        self.parent = parent
        self.size = parent.size
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.notifications = pygame.sprite.Group()
        self.print_button = GUI.Button(self,
                                       (self.size.w * 0.45, self.size.h * 0.7, self.size.w * 0.1, self.size.h * 0.05),
                                       (self.size.w * 0.45, self.size.h * 0.7, self.size.w * 0.1, self.size.h * 0.05),
                                       (self.size.w * 0.45, self.size.h * 0.7, self.size.w * 0.1, self.size.h * 0.05),
                                       'Печать выкройки.',
                                       'Печать выкройки.',
                                       (255,255,255),
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
                                           (self.size.w * 0.3, self.size.h * 0.05, self.size.w * 0.3, self.size.h * 0.4),
                                           "Печать заготовок.", None, 0.1, (255,255,255), (100, 100, 100), (255, 0, 0), 1, (100, 200, 200)))
                                       )

    def update(self):
        self.image.fill((200, 200, 200))
        self.image.blit(self.print_button.image, self.print_button.rect.topleft)
        if self.notifications.sprites():
            self.notifications.update()
            self.notifications.draw(self.image)
        else:
            self.print_button.update()
        return self.image
