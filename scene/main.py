from functions import *


class SceneMain:
    def __init__(self, parent):
        self.type = MAIN
        self.parent = parent
        self.image = pygame.Surface(parent.size, pygame.SRCALPHA)

    def update(self):
        self.image.fill((200, 200, 200))
        return self.image
