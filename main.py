import pygame
import sys

from config import window_width, window_height, fps
from modules.ui.screen_manager import ScreenManager

def main():
    pygame.init()

    screen_manager = ScreenManager((window_width, window_height)) 
    clock = pygame.time.clock()

    running = True
    while running == True:
        dt = clock.tick(fps) / 1000.0
        
        for event in  pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                screen_manager.handle_event(event)
        screen_manager.update()
        screen_manager.draw()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
