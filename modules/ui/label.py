import pygame


class Label:
    def __init__(self, x, y, text_key=None, font=None, color=(0,0,0), center=False, localizer=None):
        self.x = x
        self.y = y
        self.text_key = text_key
        self.font = font
        self.color = color
        self.center = center
        self.localizer = None
        self.set_localizer(localizer)
        
    def _get_text(self):
        """
        Возвращает локализованную строку текста или исходный ключ/текст.
        """
        if self.localizer and self.text_key:
            return self.localizer.get(self.text_key)
        return self.text_key or ""

    def _update_surface(self):
        """
        Обновляет поверхность текста для отображения.
        Рендерит текст с использованием шрифта и цвета, создаёт прямоугольник для позиционирования.
        """
        text = self._get_text()
        self.image = self.font.render(text, True, self.color)  # Рендерит текст в изображение с антиалиасингом
        self.rect = self.image.get_rect()  # Получает прямоугольник для изображения
        if self.center:
            self.rect.center = (self.x, self.y)  # Центрирует прямоугольник по координатам
        else:
            self.rect.topleft = (self.x, self.y)  # Устанавливает верхний левый угол по координатам
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def set_text_key(self, key):
        """
        Устанавливает новый ключ для текста и обновляет поверхность.
        Используется для изменения отображаемого текста без создания нового объекта Label.
        """
        self.text_key = key
        self._update_surface()

    def set_localizer(self, localizer):
        """
        Устанавливает локализатор и обновляет текст. Подписывается на обновления языка.
        """
        if hasattr(self, 'localizer') and self.localizer is not None:
            try:
                self.localizer.unregister_observer(self._update_surface)
            except Exception:
                pass

        self.localizer = localizer

        if self.localizer is not None and hasattr(self.localizer, 'register_observer'):
            self.localizer.register_observer(self._update_surface)

        self._update_surface()

    def __del__(self):
        if getattr(self, 'localizer', None) is not None:
            try:
                self.localizer.unregister_observer(self._update_surface)
            except Exception:
                pass

    