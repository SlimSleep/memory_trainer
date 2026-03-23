import pygame

class Button:
    def __init__(self, x, y, width, height, image_path,
                  hover_image_path=None, click_image_path = None, click_sound_path=None,
                  font=None, text='', text_color=(0,0,0), callback=None):

            """
            x, y: координаты верхнего левого угла
            width, height: размер кнопки (будет масштабировать изображения)
            image_path: путь к изображению для обычного состояния
            hover_image_path: путь для состояния наведения (опционально)
            click_image_path: путь для состояния нажатия (опционально)
            font: шрифт Pygame для текста
            text: текст на кнопке
            text_color: цвет текста
            callback: функция, вызываемая при клике
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

            # Загружаем исходные изображения (сохраняем для повторного масштабирования)
            self.orig_image = pygame.image.load(image_path).convert_alpha()
            self.orig_hover_image = pygame.image.load(hover_image_path).convert_alpha() if hover_image_path else None
            self.orig_click_image = pygame.image.load(click_image_path).convert_alpha() if click_image_path else None

            # Масштабируем изображения под начальный размер
            self.scale_images()
            
            self.hoverd = False
            self.clicked = False

    def scale_images(self):
            """Масштабирует все загруженные изображения под текущий размер кнопки"""
            self.image = pygame.transform.scale(self.orig_image, (self.width, self.height))
            if self.orig_hover_image:
                self.hover_image = pygame.transform.scale(self.orig_hover_image, (self.width, self.height))
            if self.orig_click_image:
                self.click_image = pygame.transform.scale(self.orig_click_image, (self.width, self.height))

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

    def handle_event(self, event): #event - событие, передаваемое из основного цикла игры
        """Обрабатывает события мыши"""
        if event.type == pygame.MOUSEMOTION: # MOUSEMOTION для отслеживания наведения
            self.hovered = self.rect.collidepoint(event.pos) #hovered - флаг, указывающий, находится ли курсор над кнопкой
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # MOUSEBUTTONDOWN для отслеживания нажатия event.button == 1 - левая кнопка мыши
            if self.rect.collidepoint(event.pos): #collidepoint проверяет, находится ли курсор внутри прямоугольника кнопки
                self.clicked = True
                if self.callback: #callback - функция, которая будет вызвана при клике на кнопку
                    self.callback()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1: # MOUSEBUTTONUP для отслеживания отпускания кнопки мыши
            self.clicked = False
    
    def draw(self, screen):
        """Отрисовывает кнопку с учётом текущего состояния"""
        # Выбираем изображение в зависимости от состояния
        if self.clicked and self.orig_click_image:
            current_image = self.click_image
        elif self.hovered and self.orig_hover_image:
            current_image = self.hover_image
        else:
            current_image = self.image

        screen.blit(current_image, self.rect) #blit - метод для отрисовки изображения на экране, self.rect - позиция и размер кнопки

        # Если есть текст, рисуем его поверх
        if self.text and self.font:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)