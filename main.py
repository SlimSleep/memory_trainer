import pygame
import sys

from config import window_width, window_height, fps
from modules.ui.screen_manager import ScreenManager

def main():
    pygame.init()

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Memory Trainer")

    screen_manager = ScreenManager(screen)
    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(fps) / 1000.0
        
        for event in pygame.event.get():
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
