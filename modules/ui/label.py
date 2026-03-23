import pygame


class Label:
    def __init__(self, x, y, text_key, font, color=(0,0,0), center = False):
        self.x = x
        self.y = y
        self.text_key = text_key #ключ для локолизации текста
        self.font = font
        self.color = color
        self.center = center
        self._update_surface()
        
    def _update_surface(self):
        """
        Обновляет поверхность текста для отображения.
        Рендерит текст с использованием шрифта и цвета, создаёт прямоугольник для позиционирования.
        """
        text = self.text_key #здесь должна быть функция для получения текста по ключу, например: get_localized_text(self.text_key)
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

    