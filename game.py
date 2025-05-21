import pygame
import sys
from game_states.state_manager import StateManager
from game_states.menu import GameStateMenu

def main():
    pygame.init()
    from constants import CONFIG
    from game_states.story import GameStateStory
    from game_states.menu import GameStateMenu
    
    screen = pygame.display.set_mode((CONFIG.WIDTH, CONFIG.HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Gravity Platformer")
    clock = pygame.time.Clock()
    
    state_manager = StateManager()
    menu_state = GameStateMenu(state_manager)
    state_manager.menu_state = menu_state
    
    # Start with story state
    state_manager.push_state(GameStateStory(state_manager))
    
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
        
        pygame.display.flip()
        clock.tick(CONFIG.FPS)

if __name__ == "__main__":
    main()
