import pygame

class TextBox:
    """
    Класс для создания поля ввода текста в Pygame.
    Поддерживает локализацию placeholder, ограничение длины текста,
    автоматическое обновление при смене языка.
    """
    def __init__(self, x, y, width, height, font, 
                 bg_color=(255,255,255), text_color=(0,0,0), 
                 active_color=(200,200,255), placeholder='', text_key=None, localizer=None, max_length=20):
        """
        Инициализация TextBox.
        
        :param x, y: координаты верхнего левого угла
        :param width, height: размеры поля
        :param font: шрифт Pygame для текста
        :param bg_color: цвет фона неактивного поля
        :param text_color: цвет текста
        :param active_color: цвет фона активного поля
        :param placeholder: текст placeholder (если не указан text_key)
        :param text_key: ключ для локализации placeholder
        :param localizer: объект Localizer для перевода
        :param max_length: максимальная длина текста
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.active_color = active_color
        self.text = ""
        self.active = False
        self.placeholder = placeholder
        self.text_key = text_key
        self.localizer = None
        self.max_length = max_length
        self.set_localizer(localizer)

    def _get_placeholder(self):
        """Возвращает локализованный placeholder или исходный текст."""
        if self.localizer and self.text_key:
            return self.localizer.get(self.text_key)
        return self.placeholder

    def set_localizer(self, localizer):
        """Устанавливает локализатор и подписывается на обновления языка."""
        if hasattr(self, 'localizer') and self.localizer is not None:
            try:
                self.localizer.unregister_observer(self._update_placeholder)
            except Exception:
                pass

        self.localizer = localizer

        if self.localizer is not None and hasattr(self.localizer, 'register_observer'):
            self.localizer.register_observer(self._update_placeholder)

        self._update_placeholder()

    def _update_placeholder(self):
        """Обновляет placeholder при смене языка."""
        self.placeholder = self._get_placeholder()

    def __del__(self):
        """Отписывается от локализатора при уничтожении объекта."""
        if getattr(self, 'localizer', None) is not None:
            try:
                self.localizer.unregister_observer(self._update_placeholder)
            except Exception:
                pass

    def handle_event(self, event):
        """
        Обрабатывает события мыши и клавиатуры.
        Активирует поле при клике, обрабатывает ввод текста.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                # Можно добавить callback для Enter
                pass
            elif event.key == pygame.K_TAB:
                pass  # Игнорируем Tab
            else:
                if len(self.text) < self.max_length and event.unicode:
                    self.text += event.unicode

    def draw(self, screen):
        """
        Отрисовывает поле ввода: фон, текст или placeholder.
        Placeholder отображается серым цветом, если текст пустой.
        """
        color = self.active_color if self.active else self.bg_color
        pygame.draw.rect(screen, color, self.rect)
        # Отрисовка текста или placeholder
        display_text = self.text if self.text else self._get_placeholder()
        text_color = self.text_color if self.text else (150, 150, 150)  # Серый для placeholder
        text_surf = self.font.render(display_text, True, text_color)
        # Обрезаем текст, показывая конец
        if text_surf.get_width() > self.rect.width - 10:
            while text_surf.get_width() > self.rect.width - 10 and len(display_text) > 0:
                display_text = display_text[1:]
                text_surf = self.font.render(display_text, True, text_color)
        screen.blit(text_surf, (self.rect.x+5, self.rect.y+5))

    def get_text(self):
        """Возвращает введённый текст."""
        return self.text

    def clear(self):
        """Очищает текст."""
        self.text = ""

    def set_text(self, text):
        """Устанавливает текст, урезая до max_length."""
        self.text = text[:self.max_length]