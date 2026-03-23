import pygame
class ScreenManager:
    def __init__(self, screen): #screen это объект pygame.Surface, на котором будут отрисовываться все экраны
        self.screen = screen
        self.screens = {} #словарь для хранения всех экранов, ключ - имя экрана, значение - объект экрана
        self.current_screen = None #текущее имя экрана, который отображается в данный момент

    def add_screen(self, name, screen_obj): #
        self.screens[name] = screen_obj

    def set_screen(self, name):
        """
        Устанавливает текущий экран по имени. Если экран с таким именем существует, 
        он становится активным, и вызывается его метод on_enter() для выполнения 
        любых необходимых действий при входе на экран.
        """
        if name in self.screens:
            self.current_screen = name
            self.screens[name].on_enter()

    def handle_event(self, event):
        """
        Обрабатывает событие, передавая его текущему экрану.
        Если текущий экран установлен, его метод handle_event() 
        вызывается для обработки события. Это позволяет каждому экрану 
        самостоятельно обрабатывать события, такие как нажатия клавиш или 
        движения мыши, в зависимости от его функциональности.
        """
        if self.current_screen:
            self.screens[self.current_screen].handle_event(event)

    def draw(self):
        if self.current_screen:
            self.screens[self.current_screen].draw(self.screen)
        pygame.display.flip() 

    def update(self):
        if self.current_screen:
            self.screens[self.current_screen].update()