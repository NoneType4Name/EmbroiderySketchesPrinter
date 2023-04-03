import GUI
from functions import *


class SceneMain:
    def __init__(self, parent):
        self.type = MAIN
        self.parent = parent
        self.size = parent.size
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.notifications = pygame.sprite.Group()
        self.notifications_thread = threading.Thread()
        self.sketch = self._sketch = self._sketch_zoomed = None
        self.sketch_pos = numpy.array((0, 0))
        self.sketch_zoom = 1
        self.sketch_zoom_precise_y = 0
        self.sketch_zoom_precise_y_t = 0
        self.updated_data = False
        self.monitor = Printer(DUMMY_MONITOR)
        self.ruler_x = pygame.surface.Surface((self.monitor.mmTOpx(self.monitor.width_mm//10*10, 10)), pygame.SRCALPHA)
        self.ruler_y = pygame.surface.Surface((self.monitor.mmTOpx(10, self.monitor.height_mm//10*10)), pygame.SRCALPHA)
        threading.Thread(target=self._draw_ruler, daemon=True).start()
        

        self.data_panel = GUI.DataPanel(
            self,
            (-(self.size.w * 0.2 + self.size.h * 0.8) * 0.003*8, self.size.h * 0.05, self.size.w * 0.2, self.size.h * 0.9), 0.2, (self.size.w * 0.2 + self.size.h * 0.8) * 0.003
        )
        self.data_panel_thread = threading.Thread()

        self.print_button = GUI.Button(self,
                                       (self.size.w * 0.45, self.size.h * 0.7, self.size.w * 0.1, self.size.h * 0.05),
                                       (self.size.w * 0.45, self.size.h * 0.7, self.size.w * 0.1, self.size.h * 0.05),
                                       (self.size.w * 0.45, self.size.h * 0.7, self.size.w * 0.1, self.size.h * 0.05),
                                       LANGUAGE.ButtonPrintEmbroidery,
                                       LANGUAGE.ButtonPrintEmbroidery,
                                       COLORS.button.background,
                                       COLORS.button.backgroundActive,
                                       COLORS.button.text,
                                       COLORS.button.textActive,
                                       COLORS.button.border,
                                       COLORS.button.borderActive,
                                       (self.size.w * 0.05 + self.size.h * 0.05) * 0.01,
                                       .4,
                                       (self.size.w * 0.05 + self.size.h * 0.05) * 0.01,
                                       .4,
                                       func=lambda _:
                                       self.notifications.add(GUI.PrintWindow(
                                           self,
                                           # (random.randrange(0, int(self.size.w * 0.7)), random.randrange(0, int(self.size.h * 0.6)), self.size.w * 0.3, self.size.h * 0.4),
                                           (self.size.w//2-self.size.w * 0.15, self.size.h//2-self.size.h * 0.2, self.size.w * 0.3, self.size.h * 0.4),
                                           LANGUAGE.DescriptionPrintEmbroidery, tuple(LANGUAGE.DefaultMetrics.values()), self.data_panel.allowed_sketches, 0.1, 1, 1)
                                       ))
        self.AboutLabel = GUI.Label(
            self,
            (self.size.w * 0.4, self.size.h * 0.975, self.size.w * 0.3, self.size.h * 0.025),
            (self.size.w * 0.4, self.size.h * 0.975, self.size.w * 0.3, self.size.h * 0.025),
            0.5,
            LANGUAGE.About.format(m=round(self.sketch_zoom*100),v=self.parent.Version if self.parent.isEXE else f"Is't builded app", s=self.parent.size, d=self.monitor.dpi),
            COLORS.label.About.background,
            COLORS.label.About.backgroundActive,
            COLORS.label.About.text,
            COLORS.label.About.textActive,
            COLORS.label.About.border,
            COLORS.label.About.borderActive,
        )
        self.GitLabel = GUI.Label(
            self,
            (self.AboutLabel.rect.bottomright[0], self.AboutLabel.rect.y, self.size.w * 0.04, self.AboutLabel.rect.h),
            (self.AboutLabel.rect.bottomright[0], self.AboutLabel.rect.y, self.size.w * 0.04, self.AboutLabel.rect.h),
            0.5,
            LANGUAGE.Github,
            COLORS.label.Git.background,
            COLORS.label.Git.backgroundActive,
            COLORS.label.Git.text,
            COLORS.label.Git.textActive,
            COLORS.label.Git.border,
            COLORS.label.Git.borderActive,
            func=lambda s: webbrowser.open_new_tab(f'{GITHUB}/{AUTHOR}/{"".join(NAME.replace(" ", ""))}')
        )
        self.TgLabel = GUI.Label(
            self,
            (self.GitLabel.rect.bottomright[0], self.AboutLabel.rect.y, self.size.w * 0.045, self.AboutLabel.rect.h),
            (self.GitLabel.rect.bottomright[0], self.AboutLabel.rect.y, self.size.w * 0.045, self.AboutLabel.rect.h),
            0.5,
            LANGUAGE.Telegram,
            COLORS.label.Tg.background,
            COLORS.label.Tg.backgroundActive,
            COLORS.label.Tg.text,
            COLORS.label.Tg.textActive,
            COLORS.label.Tg.border,
            COLORS.label.Tg.borderActive,
            func=lambda s: webbrowser.open_new_tab(TELEGRAM)
        )
        self.UpdateStatusLabel = GUI.Label(
            self,
            (self.TgLabel.rect.bottomright[0]+self.size.w * 0.01, self.AboutLabel.rect.y, self.size.w * 0.13, self.AboutLabel.rect.h),
            (self.TgLabel.rect.bottomright[0]+self.size.w * 0.01, self.AboutLabel.rect.y, self.size.w * 0.13, self.AboutLabel.rect.h),
            0.5,
            LANGUAGE.Update.Getting,
            COLORS.label.UpdateStatus.background,
            COLORS.label.UpdateStatus.backgroundActive,
            COLORS.label.UpdateStatus.text,
            COLORS.label.UpdateStatus.textActive,
            COLORS.label.UpdateStatus.border,
            COLORS.label.UpdateStatus.borderActive,
        )
        self.UpdateLabel = GUI.Label(
            self,
            (self.UpdateStatusLabel.rect.bottomright[0]+self.size.w * 0.005, self.AboutLabel.rect.y, self.size.w * 0.07, self.AboutLabel.rect.h),
            (self.UpdateStatusLabel.rect.bottomright[0]+self.size.w * 0.005, self.AboutLabel.rect.y, self.size.w * 0.07, self.AboutLabel.rect.h),
            0.5,
            LANGUAGE.Update.GettingButton,
            COLORS.label.UpdateButton.background,
            COLORS.label.UpdateButton.backgroundActive,
            COLORS.label.UpdateButton.text,
            COLORS.label.UpdateButton.textActive,
            COLORS.label.UpdateButton.border,
            COLORS.label.UpdateButton.borderActive,
            func=lambda s: s
        )
        threading.Thread(target=GetUpdate, args=[self, self.UpdateStatusLabel, self.UpdateLabel], daemon=True).start()
        self.AboutLabel.update()
        self.GitLabel.update()
        self.TgLabel.update()
        self.NewSketch()

    def _draw_ruler(self):
        # pygame.draw.line(self.ruler_x, (0, 0, 0), (0, 0))
        for num in numpy.arange(0, self.monitor.width_mm//10+1, 0.5):
            pygame.draw.line(self.ruler_x, (0, 0, 0), self.monitor.mmTOpx(num*10, 0), self.monitor.mmTOpx(num*10, 10 if int(num)==num else 7), self.monitor.mmTOpx(0.5 if int(num)==num else 0.2))
            # self.ruler_x.blit(GUI.Font.render(self.value, pygame.Rect(0, 0, ), True, self.text_color))

    def update(self):
        t = time.time()
        self.image.fill(COLORS.background)
        self.image.blit(self.sketch, (0, 0))
        if self.sketch_zoom == 1:
            self.image.blit(self.ruler_x, (0, 0))
        self.image.blit(self.print_button.image, self.print_button.rect.topleft)
        self.image.blit(self.AboutLabel.image, self.AboutLabel.rect.topleft)
        self.image.blit(self.GitLabel.image, self.GitLabel.rect.topleft)
        self.image.blit(self.TgLabel.image, self.TgLabel.rect.topleft)
        self.image.blit(self.UpdateStatusLabel.image, self.UpdateStatusLabel.rect.topleft)
        self.image.blit(self.UpdateLabel.image, self.UpdateLabel.rect.topleft)
        self.image.blit(self.data_panel.image, self.data_panel.rect.topleft)
        if self.notifications.sprites():
            self.notifications.update()
            self.notifications.draw(self.image)
        else:
            self.data_panel.update()
            self.print_button.update()
            self.UpdateStatusLabel.update()
            if self.UpdateLabel.isCollide():
                self.UpdateLabel.update()
            labels = set(map(lambda l: l if l.isCollide() else False, (self.GitLabel, self.TgLabel, self.UpdateLabel, self.UpdateStatusLabel)))
            labels.remove(False)
            tuple(map(lambda l: l.update(),labels))

            if self.updated_data:
                threading.Thread(target=self.NewSketch, daemon=True).start()
                self.updated_data = False
            # if self.sketch_zoom_precise_y_t and time.time()-self.sketch_zoom_precise_y_t >= 3:
                # self.sketch_zoom_precise_y_t = 0
                # threading.Thread(target=self.UpdateZoom, daemon=True, args=[Image.LANCZOS]).start()
            if any(map(lambda e: ((e.type == pygame.MOUSEMOTION and e.buttons[0]) or (e.type == pygame.MOUSEWHEEL and 0 < self.sketch_zoom + e.precise_y/10)), self.parent.events)) and ((not self.data_panel.isCollide()) if self.data_panel.open else True):
                for event in self.parent.events:
                    if event.type == pygame.MOUSEMOTION:
                        if event.buttons[0]:
                            self.sketch_pos+=event.rel
                            self.SketchCrop()
                    elif event.type == pygame.MOUSEWHEEL:
                        if not self.sketch_zoom_precise_y_t:
                            self.sketch_zoom_precise_y_t = time.time()
                        elif 0 < self.sketch_zoom + event.precise_y/10:
                            self.sketch_zoom_precise_y_t = time.time()
                            # self.sketch_zoom_precise_y += event.precise_y
                            self.sketch_zoom = round(self.sketch_zoom + event.precise_y / 10, 1)
                        threading.Thread(target=self.UpdateZoom, daemon=True, args=[Image.NEAREST]).start()
        return self.image
    
    def UpdateZoom(self, mode):
        self._sketch_zoomed = self._sketch.resize(tuple(map(math.ceil, numpy.array(self._sketch.size)*self.sketch_zoom)), mode)
        self.AboutLabel.value = LANGUAGE.About.format(m=round(self.sketch_zoom*100),v=self.parent.Version if self.parent.isEXE else f"Is't builded app", s=self.parent.size, d=self.monitor.dpi)
        self.AboutLabel.update()
        self.SketchCrop()
    
    def SketchCrop(self):
        cropt = self._sketch_zoomed.crop((*-self.sketch_pos, *tuple(numpy.array(-self.sketch_pos)+(self.size))))
        self.sketch = pygame.image.fromstring(cropt.tobytes(), cropt.size, cropt.mode)


    def NewSketch(self):
        try:
            images = DrawSketch(*tuple(map(int, self.data_panel.data)), printer=self.monitor).Elements(self.data_panel.allowed_sketches)
            if images:
                pad = self.monitor.mmTOpx(DEFAULT_SKETCHES_PADDING)
                w = sum(map(lambda i: i.size[0], images)) + pad * len(images)
                h = max(map(lambda i: i.size[1], images))
                im = Image.new('RGBA', (w, h), (0, 0, 0, 100))
                x = 0
                for i in images:
                    im.paste(i, (x, h - i.size[1]))
                    x += i.size[0] + pad
                self._sketch = im
                self.sketch = pygame.image.fromstring(im.tobytes(), im.size, im.mode)
                self.UpdateZoom(Image.NEAREST)
                self.sketch_pos = numpy.array(self.size)/2 - numpy.array(self.sketch.get_size())/2
            else:
                self.sketch_pos = (0, 0)
                self.sketch_zoom = 1
                self.sketch = pygame.surface.Surface(FULL_SIZE, pygame.SRCALPHA)
        except Exception:
            try:
                self.data_panel.data = list(LANGUAGE.DefaultMetrics.values())
                self.data_panel.update_texts()
                self.updated_data = True
                element = [*LANGUAGE.Print.FuncNames.values()].index(sys.exc_info()[2].tb_next.tb_next.tb_next.tb_frame.f_code.co_name) + 1
                line = sys.exc_info()[2].tb_next.tb_next.tb_next.tb_frame.f_lineno
                tb = ''.join(traceback.TracebackException(*sys.exc_info()).format())
                print(tb)
                if ctypes.windll.user32.MessageBoxW(self.parent.GAME_HWND,
                                                    LANGUAGE.Print.BuildErrorText.format(n=element, c=line),
                                                    LANGUAGE.Print.BuildErrorDescription, 17) == 1:
                    try:
                        import report
                        variables = {}
                        for a in dir(sys.exc_info()[2].tb_next.tb_next.tb_next.tb_frame.f_locals['self']):
                            if a[0] != '_':
                                d = getattr(sys.exc_info()[2].tb_next.tb_next.tb_next.tb_frame.f_locals['self'], a)
                                if isinstance(d, (bool, int, float, str, tuple, list)):
                                    variables[a] = d
                        for a in dir(sys.exc_info()[2].tb_next.tb_next.tb_next.tb_frame.f_locals['self'].printer):
                            if a[0] != '_':
                                d = getattr(sys.exc_info()[2].tb_next.tb_next.tb_next.tb_frame.f_locals['self'].printer, a)
                                if isinstance(d, (bool, int, float, str, tuple, list)):
                                    variables[a] = d
                        msg = '\n'.join('{}:\t\t{}'.format(k, v) for k, v in zip(variables.keys(), variables.values())) + '\n' + tb
                        threading.Thread(target=report.send_message, args=[['alexkim0710@gmail.com'], f'Exception in element: {element}, code: {line}.', msg, self.parent.Version]).start()
                    except ImportError:
                        pass
            except Exception:
                print(''.join(traceback.TracebackException(*sys.exc_info()).format()))
                ctypes.windll.user32.MessageBoxW(self.parent.GAME_HWND,LANGUAGE.Print.UnexpectedError, None, 16)
                self.parent.RUN = False