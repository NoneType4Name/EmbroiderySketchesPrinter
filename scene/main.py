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
        self.monitor = Printer(DUMMY_MONITOR)

        self.data_panel = GUI.DataPanel(
            self,
            (-(self.size.w * 0.2 + self.size.h * 0.8) * 0.003*8, self.size.h * 0.05, self.size.w * 0.2, self.size.h * 0.9), 0.2, (self.size.w * 0.2 + self.size.h * 0.8) * 0.003
        )

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
            (self.size.w * 0.7, self.size.h * 0.975, self.size.w * 0.14, self.size.h * 0.015),
            (self.size.w * 0.7, self.size.h * 0.975, self.size.w * 0.14, self.size.h * 0.015),
            0,
            LANGUAGE.About.format(v=self.parent.Version, s=self.parent.size, d=self.monitor.dpi),
            COLORS.label.About.background,
            COLORS.label.About.backgroundActive,
            COLORS.label.About.text,
            COLORS.label.About.textActive,
            COLORS.label.About.border,
            COLORS.label.About.borderActive,
        )
        self.GitLabel = GUI.Label(
            self,
            (self.AboutLabel.rect.bottomright[0], self.size.h * 0.975, self.size.w * 0.02, self.size.h * 0.015),
            (self.AboutLabel.rect.bottomright[0], self.size.h * 0.975, self.size.w * 0.02, self.size.h * 0.015),
            0,
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
            (self.GitLabel.rect.bottomright[0], self.size.h * 0.975, self.size.w * 0.02, self.size.h * 0.015),
            (self.GitLabel.rect.bottomright[0], self.size.h * 0.975, self.size.w * 0.02, self.size.h * 0.015),
            0,
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
            (self.TgLabel.rect.bottomright[0]+self.size.w * 0.01, self.size.h * 0.975, self.size.w * 0.07, self.size.h * 0.015),
            (self.TgLabel.rect.bottomright[0]+self.size.w * 0.01, self.size.h * 0.975, self.size.w * 0.07, self.size.h * 0.015),
            0,
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
            (self.UpdateStatusLabel.rect.bottomright[0]+self.size.w * 0.005, self.size.h * 0.975, self.size.w * 0.03, self.size.h * 0.015),
            (self.UpdateStatusLabel.rect.bottomright[0]+self.size.w * 0.005, self.size.h * 0.975, self.size.w * 0.03, self.size.h * 0.015),
            0,
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
        self.NewSketch()

    def update(self):
        self.image.fill(COLORS.background)
        self.image.blit(self.sketch, (numpy.array(self.size) - self.sketch.get_size())/2)
        self.image.blit(self.print_button.image, self.print_button.rect.topleft)
        self.image.blit(self.AboutLabel.image, self.AboutLabel.rect.topleft)
        self.image.blit(self.GitLabel.image, self.GitLabel.rect.topleft)
        self.image.blit(self.TgLabel.image, self.TgLabel.rect.topleft)
        self.image.blit(self.UpdateStatusLabel.image, self.UpdateStatusLabel.rect.topleft)
        self.image.blit(self.UpdateLabel.image, self.UpdateLabel.rect.topleft)
        self.image.blit(self.data_panel.image, self.data_panel.rect.topleft)
        # if any(map(lambda e: e.type == pygame.KEYDOWN and e.key == pygame.K_F1, self.parent.events)) and not self.notifications:
        #     self.about_button.Function()
        if self.notifications.sprites():
            self.notifications.update()
            self.notifications.draw(self.image)
        else:
            self.data_panel.update()
            self.print_button.update()
            self.AboutLabel.update()
            self.GitLabel.update()
            self.TgLabel.update()
            self.UpdateStatusLabel.update()
            self.UpdateLabel.update()
            if self.updated_data:
                threading.Thread(target=self.NewSketch, daemon=True).start()
        return self.image

    def NewSketch(self):
        try:
            images = DrawSketch(*tuple(map(int, self.data_panel.data)), printer=self.monitor).Elements(self.data_panel.allowed_sketches)
            if images:
                pad = self.monitor.mmTOpx(10)
                w = sum(map(lambda i: i.size[0], images)) + pad * len(images)
                h = max(map(lambda i: i.size[1], images))
                im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
                x = 0
                for i in images:
                    im.paste(i, (x, h - i.size[1]))
                    x += i.size[0] + pad
                if im.size[0] > self.size[0]:
                    im = im.resize((self.size[0], int(im.size[1] * (self.size[0] / im.size[0]))), Image.ANTIALIAS)
                if im.size[1] > self.size[1]:
                    im = im.resize((int(im.size[0] * (self.size[1] / im.size[1])), self.size[1]), Image.ANTIALIAS)
                self.sketch = pygame.image.fromstring(im.tobytes(), im.size, im.mode)
            else:
                self.sketch = pygame.surface.Surface(FULL_SIZE, pygame.SRCALPHA)
            self.updated_data = False
        except Exception:
            try:
                # print(dir(sys.exc_info()[2].tb_next.tb_next.tb_next.tb_frame.f_lasti))
                self.data_panel.data = list(LANGUAGE.DefaultMetrics.values())
                self.data_panel.update_texts()
                self.updated_data = True
                ctypes.windll.user32.MessageBoxW(self.parent.GAME_HWND,
                                                 LANGUAGE.Print.BuildErrorText.format(n=[*LANGUAGE.Print.FuncNames.values()].index(sys.exc_info()[2].tb_next.tb_next.tb_next.tb_frame.f_code.co_name) + 1,
                                                                                      c=sys.exc_info()[2].tb_next.tb_next.tb_next.tb_frame.f_lineno),
                                      LANGUAGE.Print.BuildErrorDescription, 16)
            except Exception:
                ctypes.windll.user32.MessageBoxW(self.parent.GAME_HWND,LANGUAGE.Print.UnexpectedError, None, 16)
