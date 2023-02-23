from functions import *

pygame.font.init()


class MainFont:
    def __init__(self, font_path):
        if font_path:
            self.font = pygame.font.Font(font_path, 256)
        else:
            self.font = pygame.font.SysFont("Arial", 256)

    def render(self, text: str, text_rect: pygame.Rect, antialias: bool, color: pygame.Color,
               background=None) -> pygame.Surface:
        srf = self.font.render(text, antialias, color, background)
        return pygame.transform.smoothscale(
            srf,
            numpy.array(srf.get_size()) / max(numpy.array(srf.get_size()) / numpy.array((text_rect.w, text_rect.h))))


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

        font = Font.render(self.text, pygame.Rect(*self.text_rect.topleft, self.text_rect.w - self.border * 2,
                                                  self.text_rect.h - self.border * 2), True, self.text_color)
        size = font.get_size()
        self.image_base = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_base.blit(RoundedRect(self.rect, self.color, self.radius, self.border, self.border_color), (0, 0))
        self.image_base.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))

        font = Font.render(self.text_active,
                           pygame.Rect(*self.text_rect_active.topleft, self.text_rect_active.w - self.border_active * 2,
                                       self.text_rect_active.h - self.border_active * 2), True, self.color_act_text)
        size = font.get_size()
        self.image_active = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_active.blit(
            RoundedRect(self.rect, self.color_active, self.radius_active, self.border_active, self.border_color_active),
            (0, 0))
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
        font = Font.render(self.text, pygame.Rect(*self.text_rect.topleft, self.text_rect.w - self.border * 2,
                                                  self.text_rect.h - self.border * 2), True, self.text_color)
        size = font.get_size()
        self.image_base = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_base.blit(RoundedRect(self.rect, self.color, self.radius, self.border, self.border_color), (0, 0))
        self.image_base.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        font = Font.render(self.text_active,
                           pygame.Rect(*self.text_rect_active.topleft, self.text_rect_active.w - self.border_active * 2,
                                       self.text_rect_active.h - self.border_active * 2), True, self.color_act_text)
        size = font.get_size()
        self.image_active = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self.image_active.blit(
            RoundedRect(self.rect, self.color_active, self.radius_active, self.border_active, self.border_color_active),
            (0, 0))
        self.image_active.blit(font, (self.rect.w * 0.5 - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))

    def isCollide(self):
        return pygame.Rect(*self.real_pos, self.rect.w, self.rect.h).collidepoint(
            pygame.mouse.get_pos()) if self.real_pos is not None else self.rect.collidepoint(pygame.mouse.get_pos())

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


def GetListsCounts(self, printer_name=None):
    if printer_name is not None:
        self.DrawSketch.printer = Printer(printer_name)
    self.printer_label2.value = 'Листов к печати: {}'.format(len(self.DrawSketch.printer.NewSketch(self.DrawSketch.Elements(self.sketches), 10)))


class PrintWindow(pygame.sprite.Sprite):
    def __init__(self, parent, rect, description, metrics, sketches, radius,
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
        self.metrics = tuple(map(int, metrics))
        self.sketches = sketches
        self.DrawSketch = DrawSketch(*self.metrics, Printer(GetDefaultPrinter()))
        self.updated_printer = False

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
            real_pos=numpy.array(self.rect.topleft) + numpy.array(
                (self.rect.w - self.rect.h * 0.06, self.rect.h * 0.025))
        )

        self.printer_label = Label(
            self,
            (self.rect.w * 0.1, self.rect.h * 0.3, self.rect.w * 0.25, self.rect.h * 0.08),
            (self.rect.w * 0.1, self.rect.h * 0.3, self.rect.w * 0.25, self.rect.h * 0.08),
            0.5,
            'Принтер',
            self.background,
            self.background,
            (255, 255, 255),
            (255, 255, 255))
        self.printer_name_label = Label(
            self.parent,
            (self.rect.w * 0.4, self.rect.h * 0.3, self.rect.w * 0.35, self.rect.h * 0.08),
            (self.rect.w * 0.4, self.rect.h * 0.3, self.rect.w * 0.35, self.rect.h * 0.08),
            0.5,
            self._printers[self._printer],
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
            func=lambda _: (setattr(self, '_printer', (self._printer + (
                1 if self._printer + 1 <= len(self._printers) - 1 else -self._printer)))) or setattr(
                self.printer_name_label, 'value', self._printers[self._printer]) or setattr(self, 'updated_printer', True),
            real_pos=numpy.array(self.rect.topleft) + numpy.array((self.rect.w * 0.8, self.rect.h * 0.3))

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
            func=lambda _: (setattr(self, '_printer', (
                    self._printer - (1 if self._printer - 1 >= 0 else -(len(self._printers) - 1))))) or setattr(
                self.printer_name_label, 'value', self._printers[self._printer]) or setattr(self, 'updated_printer', True),
            real_pos=numpy.array(self.rect.topleft) + numpy.array((self.rect.w * 0.9, self.rect.h * 0.3)))

        self.printer_label3 = Label(
            self,
            (self.rect.w * 0.1, self.rect.h * 0.5, self.rect.w * 0.8, self.rect.h * 0.08),
            (self.rect.w * 0.1, self.rect.h * 0.5, self.rect.w * 0.8, self.rect.h * 0.08),
            0.5,
            'Печать по умолчанию только черными чернилами.',
            self.background,
            self.background,
            (255, 255, 255),
            (255, 255, 255))

        self.printer_label2 = Label(
            self,
            (self.rect.w * 0.1, self.rect.h * 0.8, self.rect.w * 0.8, self.rect.h * 0.08),
            (self.rect.w * 0.1, self.rect.h * 0.8, self.rect.w * 0.8, self.rect.h * 0.08),
            0.25,
            'Постройка чертежа...',
            self.background,
            self.background,
            (255, 255, 255),
            (255, 255, 255))
        threading.Thread(target=GetListsCounts, args=[self], daemon=True).start()

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
            func=lambda s: self.DrawSketch.printer.PrintAll(self.DrawSketch.printer.NewSketch(self.DrawSketch.Elements(self.sketches, (255, 255, 255)), 10), NAME_PRINT_PROCESS) or self.kill(),
            real_pos=numpy.array(self.rect.topleft) + numpy.array((self.rect.w * 0.75, self.rect.h * 0.8)))

        self._drag = False
        self.elements.add(self.printer_name_label, self.printer_label, self.printer_label2, self.printer_label3)
        self.selectable_elements = pygame.sprite.Group(self.close_button, self.printer_name_select_down,
                                                       self.printer_name_select_up, self.cancelButton, self.printButton)

    def update(self):
        self.image.blit(RoundedRect(self.rect, self.background, self.radius, self.border, self.border_color), (0, 0))
        self.image.blit(RoundedRect((0, 0, self.rect.w, self.rect.h * 0.1), self.description_background, self.radius),
                        (0, 0))
        font = Font.render(self.description, pygame.Rect(0, 0, self.rect.w * 0.9, self.rect.h * 0.05), True,
                           self.description_color)
        self.image.blit(font, (
            self.rect.w * 0.5 - font.get_size()[0] * 0.5, self.rect.h * 0.1 * 0.5 - font.get_size()[1] * 0.5))
        self.elements.update()
        self.selectable_elements.update()
        if self.updated_printer:
            self.updated_printer = False
            self.printer_label2.value = 'Постройка чертежа...'
            threading.Thread(target=GetListsCounts, args=[self, self.printer_name_label.value], daemon=True).start()
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
                        self.selected_item_num += 1 if self.selected_item_num + 1 <= len(
                            self.selectable_elements) - 1 else -self.selected_item_num
                elif event.key in (pygame.K_SPACE, pygame.K_KP_ENTER, pygame.KSCAN_KP_ENTER):
                    if self.selected_item_num is not None:
                        self.selectable_elements.sprites()[self.selected_item_num].Function()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(*self.rect.topleft, self.rect.w, self.rect.h * 0.1).collidepoint(
                        self.parent.parent.mouse_pos):
                    self._drag = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if pygame.Rect(*self.rect.topleft, self.rect.w, self.rect.h * 0.1).collidepoint(
                        self.parent.parent.mouse_pos):
                    self._drag = False
            elif event.type == pygame.MOUSEMOTION:
                if self._drag:
                    rel = numpy.array(self.rect.topleft) + numpy.array(event.rel)
                    eve_rel = [*event.rel]
                    if 0 <= rel[0] <= self.parent.parent.size.w - self.rect.w:
                        self.rect.x += event.rel[0]
                    else:
                        eve_rel[0] = 0
                    if 0 <= rel[1] <= self.parent.parent.size.h - self.rect.h * 0.1:
                        self.rect.y += event.rel[1]
                    else:
                        eve_rel[1] = 0
                    tuple(s.RectEdit(*eve_rel, real=True) for s in
                          self.selectable_elements.sprites() + self.elements.sprites())
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
            self.image.blit(
                RoundedRect((0, 0, self.rect.w, self.rect.h), self.color_active, self.radius_active, self.border_active,
                            self.border_color_active), (0, 0))
            font = Font.render(self.value, pygame.Rect(*self.text_rect.topleft, self.text_rect.w - self.border * 2,
                                                       self.text_rect.h - self.border * 2), True,
                               self.text_color_active)
            size = font.get_size()
        else:
            self.image.blit(
                RoundedRect((0, 0, self.rect.w, self.rect.h), self.color, self.radius, self.border, self.border_color),
                (0, 0))
            font = Font.render(self.value, pygame.Rect(*self.text_rect.topleft, self.text_rect.w - self.border * 2,
                                                       self.text_rect.h - self.border * 2), True, self.text_color)
            size = font.get_size()
            self.image.blit(font,
                            (self.rect.w * self.left_padding - size[0] // 2, self.rect.h // 2 - size[1] // 2))
        self.image.blit(font,
                        (self.rect.w * self.left_padding - size[0] // 2, self.rect.h // 2 - size[1] // 2))
        return self.image

    def isCollide(self):
        return pygame.Rect(*self.real_pos, self.rect.w, self.rect.h).collidepoint(
            pygame.mouse.get_pos()) if self.real_pos is not None else self.rect.collidepoint(pygame.mouse.get_pos())

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


class TextInput(pygame.sprite.Sprite):
    def __init__(self, parent, rect, text_rect, default_text, text, left_padding: float,
                 color, color_active, text_color, text_color_active,
                 border_color=(), border_color_active=(), border=0, radius=0.5, border_active=0,
                 radius_active=0.5, func_activate=None, func_deactivate=None, real_pos=None, max_len=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)

        self.text_rect = pygame.Rect(text_rect)
        self.default = default_text
        self.text = text
        self.value = self.text if self.text else self.default
        self.left_padding = left_padding
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)

        self.text_color = pygame.Color(text_color)
        self.text_color_active = pygame.Color(text_color_active)
        self.border = border
        self.border_color = border_color
        self.radius = radius
        self.border_active = border_active
        self.border_color_active = border_color_active
        self.radius_active = radius_active
        self.func_activate = func_activate if func_activate else lambda s: s
        self.func_deactivate = func_deactivate if func_deactivate else lambda s: s
        self.real_pos = real_pos
        self.max_len = max_len

        self.active = False
        self.pos = len(self.value)

    def update(self, parent):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        font = Font.render(self.value, pygame.Rect(*self.text_rect.topleft, self.text_rect.w - self.border * 2,
                                                   self.text_rect.h - self.border * 2), True, self.text_color)
        font_active = Font.render(self.value,
                                  pygame.Rect(*self.text_rect.topleft, self.text_rect.w - self.border_active * 2,
                                              self.text_rect.h - self.border_active * 2), True, self.text_color_active)
        size = font.get_size()
        if self.active:
            if self.isCollide():
                parent.cursor = pygame.SYSTEM_CURSOR_IBEAM
            self.image.blit(
                RoundedRect(self.rect, self.color_active, self.radius, self.border_active, self.border_color_active),
                (0, 0))
            if time.time() % 1 > 0.5:
                ft = Font.render(self.text[:self.pos], self.text_rect, True, (0, 0, 0))
                sz = ft.get_size()
                width = 2
                pygame.draw.line(self.image,
                                 (self.color_active.r - 100 if self.color_active.r - 100 > 0 else 100,
                                  self.color_active.g - 100 if self.color_active.g - 100 > 0 else 100,
                                  self.color_active.b - 100 if self.color_active.b - 100 > 0 else 100),
                                 ((self.text_rect.w * self.left_padding - size[0] * 0.5) - width + sz[
                                     0] + self.text_rect.x,
                                  self.text_rect.h * 0.5 - size[1] * 0.5 + self.text_rect.y),
                                 ((self.text_rect.w * self.left_padding - size[0] * 0.5) - width + sz[
                                     0] + self.text_rect.x,
                                  self.text_rect.h * 0.5 + size[1] * 0.5 + self.text_rect.y),
                                 width)
        else:
            self.image.blit(RoundedRect(self.rect, self.color, self.radius, self.border, self.border_color), (0, 0))
            if self.isCollide():
                parent.cursor = pygame.SYSTEM_CURSOR_HAND
        if self.text:
            self.image.blit(font_active,
                            (self.rect.w * self.left_padding - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        else:
            self.image.blit(font,
                            (self.rect.w * self.left_padding - size[0] * 0.5, self.rect.h * 0.5 - size[1] * 0.5))
        if self.isCollide() and parent.mouse_left_release and not self.active:
            self.Activate()
        elif not self.isCollide() and parent.mouse_left_release and self.active:
            self.Deactivate()

        if any(map(lambda e: e.type in (pygame.KEYDOWN, pygame.KEYUP, pygame.TEXTEDITING, pygame.TEXTINPUT),
                   parent.events)) and self.active:
            for event in parent.events:
                if self.active:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            if self.pos:
                                if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                                    for n, sim in enumerate(self.text[self.pos::-1]):
                                        if sim in PUNCTUATION:
                                            self.text = self.text[:self.pos - (n if n != 0 else 1)] + self.text[
                                                                                                      self.pos:]
                                            self.pos -= n if n != 0 else 1
                                            break
                                    else:
                                        self.text = self.text[self.pos:]
                                        self.pos = 0
                                else:
                                    self.text = self.text[:self.pos - 1] + self.text[self.pos:]
                                    self.pos -= 1
                        elif event.key == pygame.K_LEFT:
                            if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                                for n, sim in enumerate(self.text[:self.pos][::-1]):
                                    if sim in PUNCTUATION:
                                        self.pos -= n if n != 0 else 1
                                        break
                                else:
                                    self.pos = 0
                            elif self.pos - 1 >= 0:
                                self.pos -= 1
                        elif event.key == pygame.K_RIGHT:
                            if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                                for n, sim in enumerate(self.text[self.pos:]):
                                    if sim in PUNCTUATION:
                                        self.pos += n if n != 0 else 1
                                        break
                                else:
                                    self.pos = len(self.text)
                            elif self.pos + 1 <= len(self.text):
                                self.pos += 1
                        elif event.key == pygame.K_DELETE:
                            if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                                for n, sim in enumerate(self.text[self.pos:]):
                                    if sim in PUNCTUATION:
                                        self.text = self.text[:self.pos] + self.text[self.pos + n if n != 0 else 1:]
                                        break
                                else:
                                    self.text = self.text[:self.pos]
                            else:
                                self.text = self.text[:self.pos] + self.text[self.pos + 1:]
                        elif event.key == pygame.K_HOME:
                            self.pos = 0
                        elif event.key == pygame.K_END:
                            self.pos = len(self.text)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            if pygame.key.get_mods() & pygame.KMOD_LCTRL and not self.text:
                                self.text = self.default
                                self.pos = len(self.text)
                            else:
                                self.Deactivate()
                        elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                            pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)
                            paste_text = pygame.scrap.get(pygame.SCRAP_TEXT).decode().translate(ESCAPE_CHARS_TRANSLATER)
                            if paste_text:
                                paste_text = paste_text[:self.max_len - len(
                                    self.text) if self.max_len is not None and self.pos + len(
                                    paste_text) > self.max_len else None]
                                self.text = self.text = self.text[:self.pos] + paste_text + self.text[self.pos:]
                                self.pos += len(paste_text)
                    elif event.type == pygame.TEXTINPUT:
                        text = event.text[:self.max_len - len(self.text) if self.max_len is not None and self.pos + len(
                            event.text) > self.max_len else None]
                        self.text = self.text[:self.pos] + text + self.text[self.pos:]
                        self.pos += len(text)
                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_ESCAPE:
                            self.Deactivate()
                    self.value = self.text if self.text else self.default
        return self.image

    def isCollide(self):
        return pygame.Rect(*self.real_pos, self.rect.w, self.rect.h).collidepoint(
            pygame.mouse.get_pos()) if self.real_pos is not None else self.rect.collidepoint(pygame.mouse.get_pos())

    def Activate(self):
        self.active = True
        self.pos = len(self.text)
        while not pygame.key.get_focused() or not pygame.key.get_repeat()[0]:
            pygame.key.start_text_input()
            pygame.key.set_repeat(500, 50)
        self.func_activate(self)

    def Deactivate(self):
        self.active = False
        pygame.key.set_repeat(0, 0)
        self.func_deactivate(self)


class Switch(pygame.sprite.Sprite):
    def __init__(self, parent, rect, name, value, color, color_active, color_on, color_off, real_pos=None, func=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.color = pygame.Color(color)
        self.color_active = pygame.Color(color_active)
        self.color_on = pygame.Color(color_on)
        self.color_off = pygame.Color(color_off)
        self.name = name
        self.value = value
        self.real_pos = real_pos
        self.func = func if func else lambda s: s

    def update(self, parent):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.value:
            self.image.blit(RoundedRect(self.rect, self.color_active, 1), (0, 0))
            pygame.draw.circle(self.image, self.color_on, (self.rect.w / 2 + self.rect.h * 0.55, self.rect.h / 2),
                               self.rect.h / 2 - self.rect.h * 0.1)
        elif not self.value:
            self.image.blit(RoundedRect(self.rect, self.color, 1), (0, 0))
            pygame.draw.circle(self.image, self.color_off, (self.rect.w / 2 - self.rect.h / 2, self.rect.h / 2),
                               self.rect.h / 2 - self.rect.h * 0.1)
        if self.isCollide():
            parent.cursor = pygame.SYSTEM_CURSOR_HAND
            if parent.mouse_left_release:
                self.value = not self.value
                self.func(self)

    def isCollide(self):
        return pygame.Rect(*self.real_pos, self.rect.w, self.rect.h).collidepoint(
            pygame.mouse.get_pos()) if self.real_pos is not None else self.rect.collidepoint(pygame.mouse.get_pos())

    def RectEdit(self, x=0, y=0, real=False):
        if real:
            if self.real_pos is not None:
                self.real_pos[0] += x
                self.real_pos[1] += y
        else:
            self.rect.x += x
            self.rect.y += y

    def Function(self):
        self.func(self)


# lambda this: (setattr(this.parent, 'allowed_sketches', [*range(SKETCHES)]) if this.value else this.parent.allowed_sketches.clear()) if this.name is str else this.parent.allowed_sketches.append(this.name) if this.value else this.parent.allowed_sketches.remove(this.name)
def IncludeExcludeElement(self):
    self.parent.parent.updated_data = True
    if type(self.name) is str:
        if self.value:
            self.parent.allowed_sketches = [*range(1, SKETCHES+1)]
            tuple(setattr(i, 'value', True) for i in self.parent.allowed_sketches_elements)
        else:
            tuple(setattr(i, 'value', False) for i in self.parent.allowed_sketches_elements)
            self.parent.allowed_sketches.clear()
    else:
        if self.value:
            self.parent.allowed_sketches.append(self.name)
            if sorted(self.parent.allowed_sketches) == [*range(1, SKETCHES+1)]:
                self.parent.allowed_sketches_elements.sprites()[0].value = True
        else:
            self.parent.allowed_sketches.remove(self.name)
            self.parent.allowed_sketches_elements.sprites()[0].value = False


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
        # self.TextBoxLabel1 = Label(
        #     self.parent,
        #     (self.rect.w * 0.1, self.rect.h * 0.1, self.rect.w * 0.4, self.rect.h * 0.05),
        #     (self.rect.w * 0.1, self.rect.h * 0.1, self.rect.w * 0.4, self.rect.h * 0.05),
        #     0.5,
        #     'Основание груди',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.1, self.rect.h * 0.1))
        # )
        #
        # self.TextBox1 = TextInput(self,
        #                           (self.rect.w * 0.6, self.rect.h * 0.1, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           (self.rect.w * 0.6, self.rect.h * 0.1, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           '', '', 0.5,
        #                           (255, 255, 255),
        #                           (202, 219, 252),
        #                           (0, 0, 0),
        #                           (0, 0, 0),
        #                           (102, 153, 255),
        #                           (0, 0, 255),
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #                               (self.rect.w * 0.6, self.rect.h * 0.1)),
        #                           max_len=3
        #                           )
        # self.TextBoxLabel1_2 = Label(
        #     self.parent,
        #     (self.rect.w * 0.77, self.rect.h * 0.1, self.rect.w * 0.15, self.rect.h * 0.05),
        #     (self.rect.w * 0.77, self.rect.h * 0.1, self.rect.w * 0.15, self.rect.h * 0.05),
        #     0.5,
        #     'mm',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.77, self.rect.h * 0.1))
        # )
        #
        # self.TextBox2 = TextInput(self,
        #                           (self.rect.w * 0.6, self.rect.h * 0.2, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           (self.rect.w * 0.6, self.rect.h * 0.2, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           '', '', 0.5,
        #                           (255, 255, 255),
        #                           (202, 219, 252),
        #                           (0, 0, 0),
        #                           (0, 0, 0),
        #                           (102, 153, 255),
        #                           (0, 0, 255),
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #                               (self.rect.w * 0.6, self.rect.h * 0.2)),
        #                           max_len=3
        #                           )
        #
        # self.TextBoxLabel2 = Label(
        #     self.parent,
        #     (self.rect.w * 0.1, self.rect.h * 0.2, self.rect.w * 0.4, self.rect.h * 0.05),
        #     (self.rect.w * 0.1, self.rect.h * 0.2, self.rect.w * 0.4, self.rect.h * 0.05),
        #     0.5,
        #     'Обхват талии',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.1, self.rect.h * 0.2))
        # )
        #
        # self.TextBox2 = TextInput(self,
        #                           (self.rect.w * 0.6, self.rect.h * 0.2, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           (self.rect.w * 0.6, self.rect.h * 0.2, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           '', '', 0.5,
        #                           (255, 255, 255),
        #                           (202, 219, 252),
        #                           (0, 0, 0),
        #                           (0, 0, 0),
        #                           (102, 153, 255),
        #                           (0, 0, 255),
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #                               (self.rect.w * 0.6, self.rect.h * 0.2)),
        #                           max_len=3
        #                           )
        # self.TextBoxLabel2_2 = Label(
        #     self.parent,
        #     (self.rect.w * 0.77, self.rect.h * 0.2, self.rect.w * 0.15, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
        #     0.5,
        #     'mm',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.77, self.rect.h * 0.2))
        # )
        #
        # self.TextBoxLabel3 = Label(
        #     self.parent,
        #     (self.rect.w * 0.1, self.rect.h * 0.3, self.rect.w * 0.4, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.4, self.rect.h * 0.05),
        #     0.5,
        #     'Обхват низа корсета',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.1, self.rect.h * 0.3))
        # )
        #
        # self.TextBox3 = TextInput(self,
        #                           (self.rect.w * 0.6, self.rect.h * 0.3, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           (self.rect.w * 0.6, self.rect.h * 0.3, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           '', '', 0.5,
        #                           (255, 255, 255),
        #                           (202, 219, 252),
        #                           (0, 0, 0),
        #                           (0, 0, 0),
        #                           (102, 153, 255),
        #                           (0, 0, 255),
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #                               (self.rect.w * 0.6, self.rect.h * 0.3)),
        #                           max_len=3
        #                           )
        # self.TextBoxLabel3_2 = Label(
        #     self.parent,
        #     (self.rect.w * 0.77, self.rect.h * 0.3, self.rect.w * 0.15, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
        #     0.5,
        #     'mm',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.77, self.rect.h * 0.3))
        # )
        #
        # self.TextBoxLabel4 = Label(
        #     self.parent,
        #     (self.rect.w * 0.1, self.rect.h * 0.4, self.rect.w * 0.4, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.4, self.rect.h * 0.05),
        #     0.5,
        #     'Высота основания груди',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.1, self.rect.h * 0.4))
        # )
        #
        # self.TextBox4 = TextInput(self,
        #                           (self.rect.w * 0.6, self.rect.h * 0.4, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           '', '', 0.5,
        #                           (255, 255, 255),
        #                           (202, 219, 252),
        #                           (0, 0, 0),
        #                           (0, 0, 0),
        #                           (102, 153, 255),
        #                           (0, 0, 255),
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #                               (self.rect.w * 0.6, self.rect.h * 0.4)),
        #                           max_len=3
        #                           )
        # self.TextBoxLabel4_2 = Label(
        #     self.parent,
        #     (self.rect.w * 0.77, self.rect.h * 0.4, self.rect.w * 0.15, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
        #     0.5,
        #     'mm',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.77, self.rect.h * 0.4))
        # )
        # self.TextBoxLabel5 = Label(
        #     self.parent,
        #     (self.rect.w * 0.1, self.rect.h * 0.5, self.rect.w * 0.4, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.4, self.rect.h * 0.05),
        #     0.5,
        #     'Высота бока вверх',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.1, self.rect.h * 0.5))
        # )
        #
        # self.TextBox5 = TextInput(self,
        #                           (self.rect.w * 0.6, self.rect.h * 0.5, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           '', '', 0.5,
        #                           (255, 255, 255),
        #                           (202, 219, 252),
        #                           (0, 0, 0),
        #                           (0, 0, 0),
        #                           (102, 153, 255),
        #                           (0, 0, 255),
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #                               (self.rect.w * 0.6, self.rect.h * 0.5)),
        #                           max_len=3
        #                           )
        # self.TextBoxLabel5_2 = Label(
        #     self.parent,
        #     (self.rect.w * 0.77, self.rect.h * 0.5, self.rect.w * 0.15, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
        #     0.5,
        #     'mm',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.77, self.rect.h * 0.5))
        # )
        #
        # self.TextBoxLabel6 = Label(
        #     self.parent,
        #     (self.rect.w * 0.1, self.rect.h * 0.6, self.rect.w * 0.4, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.4, self.rect.h * 0.05),
        #     0.5,
        #     'Высота бока вниз',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.1, self.rect.h * 0.6))
        # )
        #
        # self.TextBox6 = TextInput(self,
        #                           (self.rect.w * 0.6, self.rect.h * 0.6, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           '', '', 0.5,
        #                           (255, 255, 255),
        #                           (202, 219, 252),
        #                           (0, 0, 0),
        #                           (0, 0, 0),
        #                           (102, 153, 255),
        #                           (0, 0, 255),
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #                               (self.rect.w * 0.6, self.rect.h * 0.6)),
        #                           max_len=3
        #                           )
        # self.TextBoxLabel6_2 = Label(
        #     self.parent,
        #     (self.rect.w * 0.77, self.rect.h * 0.6, self.rect.w * 0.15, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
        #     0.5,
        #     'mm',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.77, self.rect.h * 0.6))
        # )
        # self.TextBoxLabel7 = Label(
        #     self.parent,
        #     (self.rect.w * 0.1, self.rect.h * 0.7, self.rect.w * 0.4, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.4, self.rect.h * 0.05),
        #     0.5,
        #     'Утяжка',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.1, self.rect.h * 0.7))
        # )
        #
        # self.TextBox7 = TextInput(self,
        #                           (self.rect.w * 0.6, self.rect.h * 0.7, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
        #                           '', '', 0.5,
        #                           (255, 255, 255),
        #                           (202, 219, 252),
        #                           (0, 0, 0),
        #                           (0, 0, 0),
        #                           (102, 153, 255),
        #                           (0, 0, 255),
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
        #                           0.4,
        #                           real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #                               (self.rect.w * 0.6, self.rect.h * 0.7)),
        #                           max_len=3
        #                           )
        # self.TextBoxLabel7_2 = Label(
        #     self.parent,
        #     (self.rect.w * 0.77, self.rect.h * 0.7, self.rect.w * 0.15, self.rect.h * 0.05),
        #     (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
        #     0.5,
        #     'mm',
        #     self.background,
        #     self.background,
        #     (255, 255, 255),
        #     (255, 255, 255),
        #     real_pos=numpy.array(self.rect.topleft) + numpy.array(
        #         (self.rect.w * 0.77, self.rect.h * 0.7))
        # )
        self.elements = pygame.sprite.Group()
        self.text_input_elements = pygame.sprite.Group()
        ru = ['Основание груди', 'Обхват талии', 'Обхват низа корсета',
              'Высота основания груди', 'Высота бока вверх', 'Высота бока вниз', 'Утяжка']
        self.data = ['760', '640', '840', '120', '220', '120', '50']
        self.input_text_active = 0

        for n, name in enumerate(ru, 1):
            l1 = Label(
                self.parent,
                (self.rect.w * 0.1, self.rect.h * 0.1 * n - 1, self.rect.w * 0.4, self.rect.h * 0.05),
                (0, 0, self.rect.w * 0.4, self.rect.h * 0.05),
                0.5,
                name,
                self.background,
                self.background,
                (255, 255, 255),
                (255, 255, 255),
                real_pos=numpy.array(self.rect.topleft) + numpy.array(
                    (self.rect.w * 0.1, self.rect.h * 0.1 * n - 1))
            )
            t = TextInput(
                self,
                (self.rect.w * 0.6, self.rect.h * 0.1 * n - 1, self.rect.w * 0.15, self.rect.h * 0.05),
                (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
                '', self.data[n-1], 0.5,
                (255, 255, 255),
                (202, 219, 252),
                (0, 0, 0),
                (0, 0, 0),
                (102, 153, 255),
                (0, 0, 255),
                (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
                0.4,
                (self.rect.w * 0.05 + self.rect.h * 0.05) * 0.01,
                0.4,
                real_pos=numpy.array(self.rect.topleft) + numpy.array(
                    (self.rect.w * 0.6, self.rect.h * 0.1 * n - 1)),
                max_len=3,
                func_activate=lambda s: setattr(s, 'last', s.value) or setattr(s, 'text', '') or setattr(s.parent, 'input_text_active', s.num),
                func_deactivate=lambda s: (setattr(s, 'value', s.last) if not s.value else
                                           (setattr(s.parent.parent, 'updated_data', True) or setattr(s, 'last', s.value) if s.value != s.last else False)) or
                                           setattr(s, 'text', s.value) or s.parent.data.__setitem__(s.num, s.value)

            )
            t.num = n-1
            t.last = t.value
            l2 = Label(
                self.parent,
                (self.rect.w * 0.77, self.rect.h * 0.1 * n - 1, self.rect.w * 0.15, self.rect.h * 0.05),
                (0, 0, self.rect.w * 0.15, self.rect.h * 0.05),
                0.5,
                'mm',
                self.background,
                self.background,
                (255, 255, 255),
                (255, 255, 255),
                real_pos=numpy.array(self.rect.topleft) + numpy.array(
                    (self.rect.w * 0.77, self.rect.h * 0.1 * n - 1))
            )
            self.elements.add(l1, l2)
            self.text_input_elements.add(t)

        self.OCButton = Button(
            self.parent,
            (self.rect.w * 0.95, self.rect.h * 0.45, self.rect.w * 0.05, self.rect.h * 0.1),
            (self.rect.w * 0.95, self.rect.h * 0.45, self.rect.w * 0.05, self.rect.h * 0.1),
            (self.rect.w * 0.95, self.rect.h * 0.45, self.rect.w * 0.05, self.rect.h * 0.1),
            '<',
            '<',
            self.background,
            self.background,
            (255, 255, 255),
            (255, 255, 255),
            radius=0,
            radius_active=0,
            func=lambda s: self.OpenClose(),
            real_pos=numpy.array(self.rect.topleft) + numpy.array((self.rect.w * 0.95, self.rect.h * 0.45))
        )
        self.allowed_sketches_elements = pygame.sprite.Group()
        self.allowed_sketches = [*range(1, SKETCHES+1)]
        sketches = ['Все', 'Элемент {}']
        for s in range(SKETCHES+1):
            label = Label(
                self,
                (self.rect.w * 0.1, self.rect.h * (0.78+(0.03 * s)), self.rect.w * 0.4, self.rect.h * 0.02),
                (0, 0, self.rect.w * 0.4, self.rect.h * 0.02),
                0.5,
                sketches[1 if s else 0].format(s if s else None),
                self.background,
                self.background,
                (255, 255, 255),
                (255, 255, 255),
                real_pos=numpy.array(self.rect.topleft) + numpy.array(
                    (self.rect.w * 0.1, self.rect.h * (0.78+(0.03 * s))))
            )
            sw = Switch(self,
                        (self.rect.w * 0.6, self.rect.h * (0.78+(0.03 * s)), self.rect.w * 0.1, self.rect.h * 0.02),
                        s if s else 'all',
                        True,
                        (255, 255, 255),
                        (202, 219, 252),
                        (255, 255, 255),
                        self.background,
                        real_pos=numpy.array(self.rect.topleft) + numpy.array(
                            (self.rect.w * 0.6, self.rect.h * (0.78+(0.03 * s)))),
                        func=lambda this: IncludeExcludeElement(this))
            self.allowed_sketches_elements.add(sw)
            self.elements.add(label)

        # self.elements = pygame.sprite.Group(
        #     self.TextBoxLabel1, self.TextBox1, self.TextBoxLabel1_2,
        #     self.TextBoxLabel2, self.TextBox2, self.TextBoxLabel2_2,
        #     self.TextBoxLabel3, self.TextBox3, self.TextBoxLabel3_2,
        #     self.TextBoxLabel4, self.TextBox4, self.TextBoxLabel4_2,
        #     self.TextBoxLabel5, self.TextBox5, self.TextBoxLabel5_2,
        #     self.TextBoxLabel6, self.TextBox6, self.TextBoxLabel6_2,
        #     self.TextBoxLabel7, self.TextBox7, self.TextBoxLabel7_2,
        # )

    def update(self):
        if self.open:
            self.image.blit(
                RoundedRect((0, 0, self.rect.w * 0.95, self.rect.h), self.background, self.radius, self.border,
                            self.border_color), (0, 0))
            self.elements.update()
            self.text_input_elements.update(self.parent.parent)
            self.allowed_sketches_elements.update(self.parent.parent)
            self.elements.draw(self.image)
            self.text_input_elements.draw(self.image)
            self.allowed_sketches_elements.draw(self.image)
            if any(map(lambda e: e.type == pygame.KEYDOWN and e.key == pygame.K_TAB, self.parent.parent.events)):
                if self.text_input_elements.sprites()[self.input_text_active].active:
                    self.text_input_elements.sprites()[self.input_text_active].Deactivate()
                    self.text_input_elements.sprites()[self.input_text_active + 1 if len(self.text_input_elements.sprites()) > self.input_text_active + 1 else 0].Activate()
                else:
                    self.text_input_elements.sprites()[0].Activate()
        self.OCButton.update()
        self.image.blit(self.OCButton.image, self.OCButton.rect.topleft)

    def OpenClose(self):
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        if self.open:
            self.open = False
            self.OCButton.text = self.OCButton.text_active = '>'
            self.OCButton.rect.x = self.border * 8
            self.OCButton.real_pos[0] = 0
        else:
            self.open = True
            self.OCButton.text = self.OCButton.text_active = '<'
            self.OCButton.rect.x = self.rect.w * 0.95
            self.OCButton.real_pos[0] = self.rect.w * 0.95 + self.rect.x
        self.OCButton.UpdateImage()

