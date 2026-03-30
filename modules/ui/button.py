import pygame
from modules import audio


class Button:
    def __init__(self, x, y, width, height, image_path=None,
                  hover_image_path=None, click_image_path=None, click_sound_path=None,
                  font=None, text='', text_color=(0, 0, 0), callback=None, text_key=None, localizer=None):
        """
        Инициализация кнопки с поддержкой спрайтов и текста.
        
        :param x, y: координаты верхнего левого угла
        :param width, height: размер кнопки (будет масштабировать изображения)
        :param image_path: путь к изображению для обычного состояния (опционально)
        :param hover_image_path: путь для состояния наведения (опционально)
        :param click_image_path: путь для состояния нажатия (опционально)
        :param click_sound_path: путь к звуку при клике (опционально)
        :param font: шрифт Pygame для текста
        :param text: текст на кнопке
        :param text_color: цвет текста
        :param callback: функция, вызываемая при клике
        :param text_key: ключ для локализации текста
        :param localizer: объект локализатора
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback
        self.font = font
        self.text = text
        self.text_color = text_color
        self.text_key = text_key
        self.localizer = None

        # Загружаем исходные изображения с обработкой ошибок
        self.orig_image = self._load_image(image_path)
        self.orig_hover_image = self._load_image(hover_image_path)
        self.orig_click_image = self._load_image(click_image_path)
        self.click_sound_path = click_sound_path
        self.click_sound = self._load_sound(click_sound_path)

        # Масштабируем изображения под начальный размер
        self.scale_images()

        self.hovered = False
        self.clicked = False

        self.set_localizer(localizer)

    def _load_image(self, path):
        """
        Загружает изображение из файла с обработкой ошибок.
        Если файл не найден или не может быть загружен, возвращает None.
        
        :param path: путь к файлу изображения
        :return: pygame.Surface или None
        """
        if not path:
            return None
        
        try:
            image = pygame.image.load(path).convert_alpha()
            print(f"✓ Спрайт загружен: {path}")
            return image
        except FileNotFoundError:
            print(f"⚠ Файл спрайта не найден: {path}. Используется заглушка.")
            return None
        except pygame.error as e:
            print(f"⚠ Ошибка при загрузке спрайта {path}: {e}. Используется заглушка.")
            return None

    def _load_sound(self, path):
        """
        Загружает звук из файла для кнопки.
        """
        return audio.load_sound(path)

    def _get_text(self):
        """
        Возвращает локализованную строку текста или исходный ключ/текст.
        """
        if self.localizer and self.text_key:
            return self.localizer.get(self.text_key)
        return self.text_key or self.text or ""

    def set_localizer(self, localizer):
        """
        Устанавливает локализатор и обновляет текст. Подписывается на обновления языка.
        """
        if hasattr(self, 'localizer') and self.localizer is not None:
            try:
                self.localizer.unregister_observer(self._update_text)
            except Exception:
                pass

        self.localizer = localizer

        if self.localizer is not None and hasattr(self.localizer, 'register_observer'):
            self.localizer.register_observer(self._update_text)

        self._update_text()

    def _update_text(self):
        """Обновляет текст при смене языка."""
        self.text = self._get_text()

    def __del__(self):
        """Отписывается от локализатора при уничтожении объекта."""
        if getattr(self, 'localizer', None) is not None:
            try:
                self.localizer.unregister_observer(self._update_text)
            except Exception:
                pass

    def scale_images(self):
        """Масштабирует все загруженные изображения под текущий размер кнопки"""
        # Обычное состояние
        if self.orig_image:
            self.image = pygame.transform.scale(self.orig_image, (self.width, self.height))
        else:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((200, 200, 200))  # серый фон по умолчанию

        # Состояние наведения
        if self.orig_hover_image:
            self.hover_image = pygame.transform.scale(self.orig_hover_image, (self.width, self.height))
        else:
            self.hover_image = pygame.Surface((self.width, self.height))
            self.hover_image.fill((220, 220, 220))  # светло-серый для hover

        # Состояние нажатия
        if self.orig_click_image:
            self.click_image = pygame.transform.scale(self.orig_click_image, (self.width, self.height))
        else:
            self.click_image = pygame.Surface((self.width, self.height))
            self.click_image.fill((180, 180, 180))  # тёмно-серый для click

    def set_size(self, width, height):
        """Устанавливает новый размер кнопки и масштабирует изображения"""
        self.width = width
        self.height = height
        self.rect.size = (width, height)
        self.scale_images()

    def set_position(self, x, y):
        """Перемещает кнопку в новую позицию"""
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)

    def handle_event(self, event):
        """Обрабатывает события мыши"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                if self.click_sound:
                    try:
                        self.click_sound.play()
                    except pygame.error:
                        pass
                if self.callback:
                    self.callback()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.clicked = False

    def draw(self, screen):
        """Отрисовывает кнопку с учётом текущего состояния"""
        # Приоритет: нажатие → наведение → обычное
        if self.clicked:
            current_image = self.click_image
        elif self.hovered:
            current_image = self.hover_image
        else:
            current_image = self.image

        screen.blit(current_image, self.rect)

        # Если есть текст, рисуем его поверх изображения с центрированием
        if self.text and self.font:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def set_text(self, text_key):
        """Обновляет текст кнопки"""
        self.text_key = text_key
        self._update_text()
