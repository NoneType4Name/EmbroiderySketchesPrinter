from functions import *
pygame.font.init()


class MainFont:
    def __init__(self, font_path):
        if font_path:
            self.font = pygame.font.Font(font_path, 256)
        else:
            self.font = pygame.font.SysFont("Arial", 256)

    def render(self, text: str, text_rect: pygame.Rect, antialias: bool, color: pygame.Color, background=None) -> pygame.Surface:
        srf = self.font.render(text, antialias, color, background)
        return pygame.transform.smoothscale(
            srf, numpy.array(srf.get_size()) / max(numpy.array(srf.get_size()) / numpy.array((text_rect.w, text_rect.h))))


Font = MainFont(None)


def draw_round_rect(rect, color, radius):
    rect = pygame.Rect(rect)
    color = pygame.Color(color)
    alpha = color.a
    color.a = 0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)

    circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)

    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)

    return rectangle


def RoundedRect(rect: tuple, color: tuple, radius=0.4, border=0, border_color=()) -> pygame.Surface:
    """
    RoundedRect(rect, color, radius=0.4, width=0)

    rect        : rectangle     :tuple
    color       : rgb or rgba   :tuple
    radius      : 0 <= radius<=1:float
    border      : integer       :int
    border_color: rgb or rgba:  :tuple

    return  ->  rectangle image
    """
    rect = pygame.Rect(0, 0, rect[2], rect[3])
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    border = round(border)
    if border:
        surf.blit(draw_round_rect(rect, border_color, radius), (0, 0))
    surf.blit(draw_round_rect((0, 0, rect.w - border * 2, rect.h - border * 2), color, radius), (border, border))
    return surf


class Button(pygame.sprite.Sprite):
    def __init__(self, parent, rect, text_rect, text_rect_active, text, text_active,
                 color, color_active, text_color, text_color_active,
                 border=0, radius=0.5, border_active=0, radius_active=0.5, func=None, args=()):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.text_rect = pygame.Rect(text_rect)
        self.text_rect_active = pygame.Rect(text_rect_active)
        self.text = text
        self.text_active = text_active
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)
        self.text_color = pygame.Color(text_color)
        self.color_act_text = pygame.Color(text_color_active)
        self.border_active = border
        self.radius = radius
        self.border = border_active
        self.radius_active = radius_active
        self.func = func if func else lambda s, a=(): s
        self.args = args

        # font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, text, self.text_rect))
        font = Font.render(self.text, self.text_rect, True, self.text_color)
        size = font.get_size()

        self.image_base = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_base.blit(RoundedRect(self.rect, self.color, self.radius), (0, 0))
        self.image_base.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        # font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, text_active, self.text_rect_active))
        font = Font.render(self.text_active, self.text_rect_active, True, self.color_act_text)
        size = font.get_size()
        self.image_active = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_active.blit(RoundedRect(self.rect, self.color_active, self.radius_active), (0, 0))
        self.image_active.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        self.collide = False

    def update(self):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.isCollide() and not self.collide:
            self.collide = True
        elif not self.isCollide() and self.collide:
            self.collide = False
        if self.collide:
            self.image = self.image_active
        else:
            self.image = self.image_base

    def UpdateImage(self):
        font = Font.render(self.text, self.text_rect, True, self.text_color)
        size = font.get_size()
        self.image_base = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_base.blit(RoundedRect(self.rect, self.color, self.radius), (0, 0))
        self.image_base.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        font = Font.render(self.text_active, self.text_rect_active, True, self.color_act_text)
        size = font.get_size()
        self.image_active = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_active.blit(RoundedRect(self.rect, self.color_active, self.radius_active), (0, 0))
        self.image_active.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))

    def isCollide(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def RectEdit(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y

    def Function(self):
        if self.args:
            self.func(self, *self.args)
        else:
            self.func(self)


class PrintWindow(pygame.sprite.Sprite):
    def __init__(self, parent, rect, radius, description,
                 description_color, description_background,
                 close_button_color, close_button_radius,
                 # button_color, button_border, button_text_color,
                 # button_color_active, button_border_active, button_text_color_active,
                 # select_bar_color, select_bar_border, select_bar_text,
                 background,
                 ):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.image = pygame.surface.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.radius = radius
        self.description = description
        self.description_color = description_color
        self.description_background = description_background
        self.close_button_color = close_button_color
        self.close_button_radius = close_button_radius
        # self.button_color = button_color
        # self.button_border = button_border
        # self.button_text_color = button_text_color
        # self.button_color_active = button_color_active
        # self.button_border_active = button_border_active
        # self.button_text_color_active = button_text_color_active
        # self.select_bar_color = select_bar_color
        # self.select_bar_border = select_bar_border
        # self.select_bar_text = select_bar_text
        self.background = background

    def update(self):
        self.image.blit(RoundedRect(self.rect, self.background, self.radius), (0, 0))
        self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h*0.1), self.description_background, self.radius), (0, 0))
        font = Font.render(self.description, pygame.Rect(0, 0, self.rect.w*0.9, self.rect.h * 0.05), True, self.description_color)
        self.image.blit(font, (self.rect.w * 0.5 - font.get_size()[0] * 0.5, self.rect.h * 0.1 * 0.5 - font.get_size()[1] * 0.5))
        self.image.blit(RoundedRect((0, 0, self.rect.h * 0.05, self.rect.h * 0.05), self.close_button_color, self.close_button_radius),(self.rect.w - self.rect.h * 0.06, self.rect.h * 0.025))

        return self.image


class Label(pygame.sprite.Sprite):
    def __init__(self, parent, rect, text_rect, left_padding, text,
                 color, color_active, text_color, text_color_active,
                 gradient=False, gradient_start=(), gradient_end=(),
                 gradient_active=False, gradient_start_active=(), gradient_end_active=(),
                 border=0, radius=0.5, border_active=0, radius_active=0.5, func=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.text_rect = pygame.Rect(text_rect)
        self.left_padding = left_padding
        self.value = text
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)
        self.color_active = pygame.Color(color_active)
        self.text_color = pygame.Color(text_color)
        self.text_color_active = pygame.Color(text_color_active)
        self.gradient = gradient
        self.gradient_start = gradient_start
        self.gradient_end = gradient_end
        self.gradient_active = gradient_active
        self.gradient_start_active = gradient_start_active
        self.gradient_end_active = gradient_end_active
        self.border = border
        self.border_active = border_active
        self.radius = radius
        self.radius_active = radius_active
        self.func = func if func else lambda s: s

    def update(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        if self.isCollide():
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color_active,self.radius_active,
                                        self.gradient_active, self.gradient_start_active), (0, 0))
            font = Font.render(self.value, self.text_rect, True, self.text_color_active)
            size = font.get_size()
        else:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color, self.radius,
                                        self.gradient, self.gradient_start), (0, 0))
            font = Font.render(self.value, self.text_rect, True, self.text_color)
            size = font.get_size()
            self.image.blit(font,
                            (self.rect.w * self.left_padding - size[0] // 2, self.rect.h // 2 - size[1] // 2))
        self.image.blit(font,
                        (self.rect.w * self.left_padding - size[0] // 2, self.rect.h // 2 - size[1] // 2))
        return self.image

    def isCollide(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    # def NewFont(self):
    #     self.font = pygame.font.Font(FONT_PATH, GetFontSize(FONT_PATH, self.value, self.text_rect))
    #     self.size = self.font.size(self.value)

    def Function(self):
        self.func(self)
