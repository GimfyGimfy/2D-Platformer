import pygame
import sys
from constants import CONFIG
from game_states.state_manager import StateManager
from game_states.story import GameStateStory
from game_states.menu import GameStateMenu

def main():
    pygame.init()
    
    #screen initialisation with current config
    screen = pygame.display.set_mode((CONFIG.WIDTH, CONFIG.HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Gravity Platformer")
    clock = pygame.time.Clock()
    
    state_manager = StateManager()
    
    #resize handler
    def handle_resize():
        nonlocal screen
        screen = pygame.display.set_mode(
            (CONFIG.WIDTH, CONFIG.HEIGHT),
            pygame.RESIZABLE
        )
        #refresh all states
        for state in state_manager._states:
            state.draw(screen)  #forcing redraw with new resolution

    state_manager.set_resize_callback(handle_resize)
    
    #initial state - start with intro story (level 0)
    state_manager.push_state(GameStateStory(state_manager, 0))
    
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_state = state_manager.current_state
        if current_state:
            current_state.handle_events(events)
            current_state.update()
            current_state.draw(screen)
        
        pygame.display.flip()
        clock.tick(CONFIG.fps)

if __name__ == "__main__":
    main()
