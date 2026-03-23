import pygame

class Slider:
    def __init__(self, x, y, width, height, min_val=0, max_val=100, initial_val=50,
                 bg_color=(200,200,200), fg_color=(100,100,100), knob_color=(50,50,50),
                 callback=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.knob_color = knob_color
        self.callback = callback
        self.dragging = False
        self.rect = pygame.Rect(x, y, width, height)
        self.knob_rect = pygame.Rect(0, 0, 20, height)
        self._update_knob()

    def _update_knob(self):
        knob_x = self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * (self.width - 20)
        self.knob_rect = pygame.Rect(knob_x, self.y, 20, self.height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.x
            ratio = max(0, min(1, rel_x / self.width))
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            self._update_knob()
            if self.callback:
                self.callback(self.value)

    def draw(self, screen):
        # Фон
        pygame.draw.rect(screen, self.bg_color, self.rect)
        # Полоса
        bar_rect = pygame.Rect(self.x + 10, self.y + self.height // 2 - 2, self.width - 20, 4)
        pygame.draw.rect(screen, self.fg_color, bar_rect)
        # Ручка
        pygame.draw.rect(screen, self.knob_color, self.knob_rect)

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = max(self.min_val, min(self.max_val, value))
        self._update_knob()