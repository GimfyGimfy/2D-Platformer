import pygame
import sys
from constants import WIDTH, HEIGHT,FPS
from game_states.state_manager import StateManager
from game_states.menu import GameStateMenu

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gravity Platformer")
    clock = pygame.time.Clock()
    
    state_manager = StateManager()
    state_manager.push_state(GameStateMenu(state_manager))

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_state = state_manager.current_state
        current_state.handle_events(events)
        current_state.update()
        current_state.draw(screen)
        clock.tick(FPS)

if __name__ == "__main__":
    main()
