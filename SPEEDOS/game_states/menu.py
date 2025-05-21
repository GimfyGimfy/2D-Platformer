import pygame
import sys
from typing import List
from ui.button import Button
from constants import COLORS, CONFIG
from game_states.base import GameState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_states.state_manager import StateManager
    from game_states.play import GameStatePlay

class GameStateMenu(GameState):
    def __init__(self, state_manager: 'StateManager'):
        self.state_manager = state_manager
        self.buttons = [
            Button(CONFIG.WIDTH//2-150, 200, 300, 60, "Start Game", self.start_game),
            Button(CONFIG.WIDTH//2-150, 280, 300, 60, "Load Game", self.empty_function),
            Button(CONFIG.WIDTH//2-150, 360, 300, 60, "Settings", self.open_settings),
            Button(CONFIG.WIDTH//2-150, 440, 300, 60, "Quit", self.quit_game),
            Button(CONFIG.WIDTH//2-150, 440, 300, 60, "Replay Story", self.replay_story)
        ]

    def empty_function(self) -> None:
        """Placeholder function for buttons that don't do anything yet"""
        pass

    def start_game(self) -> None:
        from game_states.play import GameStatePlay  #local import
        self.state_manager.push_state(GameStatePlay(self.state_manager))
    
    def open_settings(self):
        from game_states.settings import GameStateSettings
        self.state_manager.push_state(GameStateSettings(self.state_manager))

    def quit_game(self) -> None:
        pygame.quit()
        sys.exit()
        
    def replay_story(self): #doesn't work yet
        from game_states.story import GameStateStory
        self.state_manager.push_state(GameStateStory(self.state_manager))

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            for button in self.buttons:
                button.check_hover(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN and button.is_hovered:
                    button.action()

    def update(self) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLORS["MENU_BG"])
        font_large = pygame.freetype.SysFont('Arial', 60)
        title_surf, title_rect = font_large.render("Gravity Platformer", COLORS["WHITE"])
        title_rect.center = (CONFIG.WIDTH//2, 100)
        screen.blit(title_surf, title_rect)
        
        for button in self.buttons:
            button.draw(screen)
        
        pygame.display.flip()