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
                 color, color_active, text_color, text_color_active, border_color=(), border_color_active=(),
                 border=0, radius=0.5, border_active=0, radius_active=0.5, func=None, args=(), real_pos=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.real_pos = real_pos
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.text_rect = pygame.Rect(text_rect)
        self.text_rect_active = pygame.Rect(text_rect_active)
        self.text = text
        self.text_active = text_active
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)
        self.text_color = pygame.Color(text_color)
        self.color_act_text = pygame.Color(text_color_active)
        self.border = border
        self.border_active = border_active
        self.border_color = border_color
        self.border_color_active = border_color_active
        self.radius = radius
        self.radius_active = radius_active
        self.func = func if func else lambda s, a=(): s
        self.args = args

        font = Font.render(self.text, pygame.Rect(*self.text_rect.topleft, self.text_rect.w - self.border * 2, self.text_rect.h - self.border * 2), True, self.text_color)
        size = font.get_size()
        self.image_base = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_base.blit(RoundedRect(self.rect, self.color, self.radius, self.border, self.border_color), (0, 0))
        self.image_base.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))

        font = Font.render(self.text_active, pygame.Rect(*self.text_rect_active.topleft, self.text_rect_active.w - self.border_active * 2, self.text_rect_active.h - self.border_active * 2), True, self.color_act_text)
        size = font.get_size()
        self.image_active = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_active.blit(RoundedRect(self.rect, self.color_active, self.radius_active, self.border_active, self.border_color_active), (0, 0))
        self.image_active.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        self.collide = False

    def update(self):
        if self.isCollide() and not self.collide:
            self.collide = True
        elif not self.isCollide() and self.collide:
            self.collide = False

        if self.collide:
            self.parent.parent.cursor = pygame.SYSTEM_CURSOR_HAND
            self.image = self.image_active
            if self.parent.parent.mouse_left_release:
                self.image = self.image_base
                self.Function()
        else:
            self.image = self.image_base

    def UpdateImage(self):
        font = Font.render(self.text, pygame.Rect(*self.text_rect.topleft, self.text_rect.w - self.border * 2, self.text_rect.h - self.border * 2), True, self.text_color)
        size = font.get_size()
        self.image_base = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_base.blit(RoundedRect(self.rect, self.color, self.radius, self.border, self.border_color), (0, 0))
        self.image_base.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        font = Font.render(self.text_active, pygame.Rect(*self.text_rect_active.topleft, self.text_rect_active.w - self.border_active * 2, self.text_rect_active.h - self.border_active * 2), True, self.color_act_text)
        size = font.get_size()
        self.image_active = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_active.blit(RoundedRect(self.rect, self.color_active, self.radius_active, self.border_active, self.border_color_active), (0, 0))
        self.image_active.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))

    def isCollide(self):
        return pygame.Rect(*self.real_pos, self.rect.w, self.rect.h).collidepoint(pygame.mouse.get_pos()) if self.real_pos is not None else self.rect.collidepoint(pygame.mouse.get_pos())

    def Function(self):
        if self.args:
            self.func(self, *self.args)
        else:
            self.func(self)

    def RectEdit(self, x=0, y=0, real=False):
        if real:
            if self.real_pos is not None:
                self.real_pos[0] += x
                self.real_pos[1] += y
        else:
            self.rect.x += x
            self.rect.y += y


class PrintWindow(pygame.sprite.Sprite):
    def __init__(self, parent, rect, description, files, radius,
                 description_color, description_background,
                 close_button_color, close_button_radius,
                 # button_color, button_border, button_text_color,
                 # button_color_active, button_border_active, button_text_color_active,
                 # select_bar_color, select_bar_border, select_bar_text,
                 background,
                 border=0,
                 border_color=()
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
        self.border = border
        self.border_color = border_color

        self._printers = GetPrintersList()
        self._printer = self._printers.index(GetDefaultPrinter())

        self.elements = pygame.sprite.Group()
        self.close_button = Button(
            self.parent,
            (self.rect.w - self.rect.h * 0.06, self.rect.h * 0.025, self.rect.h * 0.05, self.rect.h * 0.05),
            (0, 0, self.rect.h * 0.08, self.rect.h * 0.08),
            (0, 0, self.rect.h * 0.08, self.rect.h * 0.08),
            '×',
            '×',
            self.close_button_color,
            self.close_button_color,
            (255, 255, 255),
            (255, 255, 255),
            radius=self.close_button_radius,
            radius_active=self.close_button_radius,
            func=lambda _: self.kill(),
            real_pos=numpy.array(self.rect.topleft)+numpy.array((self.rect.w - self.rect.h * 0.06, self.rect.h * 0.025))
        )

        self.printer_label = Label(
            self,
            (self.rect.w * 0.1, self.rect.h * 0.3, self.rect.w * 0.25, self.rect.h * 0.08),
            (self.rect.w * 0.1, self.rect.h * 0.3, self.rect.w * 0.25, self.rect.h * 0.08),
            0.5,
            'Принтер',
            self.background,
            self.background,
            (255,255,255),
            (255,255,255))
        self.printer_name_label = Label(
            self.parent,
            (self.rect.w * 0.4, self.rect.h * 0.3, self.rect.w * 0.35, self.rect.h * 0.08),
            (self.rect.w * 0.4, self.rect.h * 0.3, self.rect.w * 0.35, self.rect.h * 0.08),
            0.5,
            GetDefaultPrinter(),
            (255, 255, 255),
            (202, 219, 252),
            (0, 0, 0),
            (0, 0, 0),
            (102, 153, 255),
            (102, 153, 255),
            (self.rect.w * 0.1 + (self.rect.h * 0.05)) * 0.04,
            0.4,
            (self.rect.w * 0.1 + (self.rect.h * 0.05)) * 0.04,
            0.4,
            real_pos=numpy.array(self.rect.topleft) + numpy.array((self.rect.w * 0.4, self.rect.h * 0.3))
        )
        self.printer_name_select_down = Button(
            self.parent,
            (self.rect.w * 0.8, self.rect.h * 0.3, self.rect.h * 0.08, self.rect.h * 0.08),
            (0, 0, self.rect.h * 0.08, self.rect.h * 0.08),
            (0, 0, self.rect.h * 0.08, self.rect.h * 0.08),
            ' ▼',
            ' ▼',
            (255, 255, 255),
            (202, 219, 252),
            (0, 0, 0),
            (0, 0, 0),
            (102, 153, 255),
            (102, 153, 255),
            (self.rect.h * 0.08 * 2) * 0.04,
            1,
            (self.rect.h * 0.08 * 2) * 0.04,
            1,
            func=lambda _: (setattr(self, '_printer', (self._printer + (1 if self._printer + 1 <= len(self._printers) - 1 else -self._printer)))) or setattr(self.printer_name_label, 'value', self._printers[self._printer]),
            real_pos=numpy.array(self.rect.topleft) + numpy.array((self.rect.w * 0.8, self  .rect.h * 0.3))

        )
        self.selected_item_num = None
        self.printer_name_select_up = Button(
            self.parent,
            (self.rect.w * 0.9, self.rect.h * 0.3, self.rect.h * 0.08, self.rect.h * 0.08),
            (0, 0, self.rect.h * 0.08, self.rect.h * 0.08),
            (0, 0, self.rect.h * 0.08, self.rect.h * 0.08),
            ' ▲',
            ' ▲',
            (255, 255, 255),
            (202, 219, 252),
            (0, 0, 0),
            (0, 0, 0),
            (102, 153, 255),
            (102, 153, 255),
            (self.rect.h * 0.08 * 2) * 0.04,
            1,
            (self.rect.h * 0.08 * 2) * 0.04,
            1,
            func=lambda _: (setattr(self, '_printer', (self._printer - (1 if self._printer - 1 >= 0 else -(len(self._printers) - 1))))) or setattr(self.printer_name_label, 'value', self._printers[self._printer]),
            real_pos=numpy.array(self.rect.topleft) + numpy.array((self.rect.w * 0.9, self.rect.h * 0.3)))

        self.printer_label3 = Label(
            self,
            (self.rect.w * 0.1, self.rect.h * 0.5, self.rect.w * 0.8, self.rect.h * 0.08),
            (self.rect.w * 0.1, self.rect.h * 0.5, self.rect.w * 0.8, self.rect.h * 0.08),
            0.5,
            'Печать по умолчанию только черными чернилами.',
            self.background,
            self.background,
            (255,255,255),
            (255,255,255))

        self.printer_label2 = Label(
            self,
            (self.rect.w * 0.1, self.rect.h * 0.8, self.rect.w * 0.8, self.rect.h * 0.08),
            (self.rect.w * 0.1, self.rect.h * 0.8, self.rect.w * 0.8, self.rect.h * 0.08),
            0.25,
            'Листов к печати: N',
            self.background,
            self.background,
            (255,255,255),
            (255,255,255))

        self.cancelButton = Button(
            self.parent,
            (self.rect.w * 0.5, self.rect.h * 0.8, self.rect.w * 0.20, self.rect.h * 0.08),
            (0, 0, self.rect.w * 0.2, self.rect.h * 0.08),
            (0, 0, self.rect.w * 0.2, self.rect.h * 0.08),
            'Отмена.',
            'Отмена.',
            (255, 255, 255),
            (202, 219, 252),
            (0, 0, 0),
            (0, 0, 0),
            (102, 153, 255),
            (102, 153, 255),
            (self.rect.h * 0.08 * 2) * 0.04,
            .5,
            (self.rect.h * 0.08 * 2) * 0.04,
            .5,
            func=lambda _: self.kill(),
            real_pos=numpy.array(self.rect.topleft) + numpy.array((self.rect.w * 0.5, self.rect.h * 0.8)))
        self.printButton = Button(
            self.parent,
            (self.rect.w * 0.75, self.rect.h * 0.8, self.rect.w * 0.20, self.rect.h * 0.08),
            (0, 0, self.rect.w * 0.2, self.rect.h * 0.08),
            (0, 0, self.rect.w * 0.2, self.rect.h * 0.08),
            'Печать.',
            'Печать.',
            (255, 255, 255),
            (202, 219, 252),
            (0, 0, 0),
            (0, 0, 0),
            (102, 153, 255),
            (102, 153, 255),
            (self.rect.h * 0.08 * 2) * 0.04,
            .5,
            (self.rect.h * 0.08 * 2) * 0.04,
            .5,
            func=lambda _: self.kill(),
            real_pos=numpy.array(self.rect.topleft) + numpy.array((self.rect.w * 0.75, self.rect.h * 0.8)))

        self._drag = False
        self.elements.add(self.printer_name_label, self.printer_label, self.printer_label2, self.printer_label3)
        self.selectable_elements = pygame.sprite.Group(self.close_button, self.printer_name_select_down, self.printer_name_select_up, self.cancelButton, self.printButton)

    def update(self):
        self.image.blit(RoundedRect(self.rect, self.background, self.radius,self.border, self.border_color), (0, 0))
        self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h*0.1), self.description_background, self.radius), (0, 0))
        font = Font.render(self.description, pygame.Rect(0, 0, self.rect.w*0.9, self.rect.h * 0.05), True, self.description_color)
        self.image.blit(font, (self.rect.w * 0.5 - font.get_size()[0] * 0.5, self.rect.h * 0.1 * 0.5 - font.get_size()[1] * 0.5))
        self.elements.update()
        self.selectable_elements.update()
        if self.selected_item_num is not None:
            self.selectable_elements.sprites()[self.selected_item_num].collide = True
        self.elements.draw(self.image)
        self.selectable_elements.draw(self.image)
        for event in self.parent.parent.events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.kill()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if self.selected_item_num is None:
                        self.selected_item_num = 0
                    else:
                        self.selected_item_num += 1 if self.selected_item_num + 1 <= len(self.selectable_elements) - 1 else -self.selected_item_num
                elif event.key in (pygame.K_SPACE, pygame.K_KP_ENTER, pygame.KSCAN_KP_ENTER):
                    if self.selected_item_num is not None:
                        self.selectable_elements.sprites()[self.selected_item_num].Function()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(*self.rect.topleft, self.rect.w, self.rect.h*0.1).collidepoint(self.parent.parent.mouse_pos):
                    self._drag = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if pygame.Rect(*self.rect.topleft, self.rect.w, self.rect.h * 0.1).collidepoint(self.parent.parent.mouse_pos):
                    self._drag = False
            elif event.type == pygame.MOUSEMOTION:
                if self._drag:
                    rel = numpy.array(self.rect.topleft) + numpy.array(event.rel)
                    eve_rel = [*event.rel]
                    if 0 <= rel[0] <= self.parent.parent.size.w-self.rect.w:
                        self.rect.x += event.rel[0]
                    else:
                        eve_rel[0] = 0
                    if 0 <= rel[1] <= self.parent.parent.size.h-self.rect.h*0.1:
                        self.rect.y += event.rel[1]
                    else:
                        eve_rel[1] = 0
                    tuple(s.RectEdit(*eve_rel, real=True) for s in self.selectable_elements.sprites() + self.elements.sprites())
            elif event.type == pygame.WINDOWLEAVE:
                if self._drag:
                    self._drag = False

        return self.image


class Label(pygame.sprite.Sprite):
    def __init__(self, parent, rect, text_rect, left_padding, value,
                 color, color_active, text_color, text_color_active,
                 border_color=(), border_color_active=(),
                 border=0, radius=0.5, border_active=0, radius_active=0.5, func=None, real_pos=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.real_pos = real_pos
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.text_rect = pygame.Rect(text_rect)
        self.left_padding = left_padding
        self.value = str(value)
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)
        self.color_active = pygame.Color(color_active)
        self.text_color = pygame.Color(text_color)
        self.text_color_active = pygame.Color(text_color_active)
        self.border = border
        self.border_active = border_active
        self.border_color = border_color
        self.border_color_active = border_color_active
        self.radius = radius
        self.radius_active = radius_active
        self.func = func if func else lambda s: s

    def update(self):
        # self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        if self.isCollide():
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color_active, self.radius_active, self.border_active, self.border_color_active), (0, 0))
            font = Font.render(self.value, pygame.Rect(*self.text_rect.topleft, self.text_rect.w - self.border * 2, self.text_rect.h - self.border * 2), True, self.text_color_active)
            size = font.get_size()
        else:
            self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h), self.color, self.radius, self.border, self.border_color), (0, 0))
            font = Font.render(self.value, pygame.Rect(*self.text_rect.topleft, self.text_rect.w - self.border * 2, self.text_rect.h - self.border * 2), True, self.text_color)
            size = font.get_size()
            self.image.blit(font,
                            (self.rect.w * self.left_padding - size[0] // 2, self.rect.h // 2 - size[1] // 2))
        self.image.blit(font,
                        (self.rect.w * self.left_padding - size[0] // 2, self.rect.h // 2 - size[1] // 2))
        return self.image

    def isCollide(self):
        return pygame.Rect(*self.real_pos, self.rect.w, self.rect.h).collidepoint(pygame.mouse.get_pos()) if self.real_pos is not None else self.rect.collidepoint(pygame.mouse.get_pos())

    def Function(self):
        self.func(self)

    def RectEdit(self, x=0, y=0, real=False):
        if real:
            if self.real_pos is not None:
                self.real_pos[0] += x
                self.real_pos[1] += y
        else:
            self.rect.x += x
            self.rect.y += y


class DataPanel(pygame.sprite.Sprite):
    def __init__(self, parent, rect, background, radius=0.5, border=0, border_color=()):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.background = background
        self.radius = radius
        self.border = border
        self.border_color = border_color

        self.open = True
        self.OCButton = Button(
            self,
            (self.rect.w * 0.95, self.rect.h * 0.45, self.rect.w * 0.05, self.rect.h * 0.1),
            (self.rect.w * 0.95, self.rect.h * 0.45, self.rect.w * 0.05, self.rect.h * 0.1),
            (self.rect.w * 0.95, self.rect.h * 0.45, self.rect.w * 0.05, self.rect.h * 0.1),
            '<',
            '<',
            self.background,
            self.background,
            (255, 255, 255),
            (255, 255, 255),
            # border=(self.rect.w * 0.05 + self.rect.h * 0.1) * 0.05,
            # border_color=self.background,
            # border_active=(self.rect.w * 0.05 + self.rect.h * 0.1) * 0.05,
            # border_color_active=self.background,
            radius=0,
            radius_active=0,
            func=lambda s: s.parent.OpenClose(),
            real_pos=numpy.array(self.rect.topleft)+numpy.array((self.rect.w * 0.95, self.rect.h * 0.45))
        )
        self.selectable_elements = pygame.sprite.Group(self.OCButton)

    def update(self):
        if self.open:
            self.image.blit(RoundedRect((0, 0, self.rect.w * 0.95, self.rect.h), self.background, self.radius, self.border, self.border_color), (0, 0))
        self.selectable_elements.update()
        self.selectable_elements.draw(self.image)

    def OpenClose(self):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.open:
            self.open = False
            self.OCButton.text = self.OCButton.text_active = '>'
            self.OCButton.rect.x = self.border*4
            self.OCButton.real_pos[0] = 0
        else:
            self.open = True
            self.OCButton.text = self.OCButton.text_active = '<'
            self.OCButton.rect.x = self.rect.w * 0.95
            self.OCButton.real_pos[0] = self.rect.w * 0.95 + self.rect.x
            # self.OCButton.RectEdit(self.rect.w * 0.95, 0)
            # numpy.array(self.rect.topleft) + numpy.array((self.rect.w * 0.95, self.rect.h * 0.45))
            # self.rect.x = 0
        self.OCButton.UpdateImage()
