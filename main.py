import GUI
from functions import *


screen = pygame.display.set_mode(FULL_SIZE)


class graph:
    def __init__(self, width, height):
        self.image = pygame.surface.Surface((width, height))
        self.image.fill((255, 255, 255))

    def update(self, surface: pygame.Surface):
        self.image = surface

    def clear(self):
        self.image = pygame.surface.Surface(self.image.get_size())
        return self.image


Graph = graph(*screen.get_size())
pygame.draw.rect(Graph.image, (0,0,0), (3, 3, *tuple(map((lambda s: s-6), screen.get_size()))), MillimetersToPixels(3))
pygame.draw.line(Graph.image, (0, 0, 0), (MillimetersToPixels(200), MillimetersToPixels(10)), (MillimetersToPixels(100), MillimetersToPixels(10)), MillimetersToPixels(5))
notif = GUI.PrintWindow(None, (0, 0, 300, 500), 0.1, "Печать заготовок.", (255,255,255), (100, 100, 100), (255, 0, 0), 1, (200, 200, 200))
while RUN:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                RUN = False
    screen.blit(notif.update(), (200, 200))

    pygame.display.flip()
