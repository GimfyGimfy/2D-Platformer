import pygame
from typing import List
from game_states.base import GameState
from game_states.menu import GameStateMenu
from ui.button import Button
from constants import COLORS, WIDTH, HEIGHT

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_states.state_manager import StateManager

class GameStatePaused(GameState):
    def __init__(self, state_manager: 'StateManager'):
        self.state_manager = state_manager
        self.buttons = [
            Button(WIDTH//2-150, HEIGHT//2, 300, 60, "Continue", self.continue_game),
            Button(WIDTH//2-150, HEIGHT//2+80, 300, 60, "Main Menu", self.main_menu)
        ]

    def continue_game(self) -> None:
        self.state_manager.pop_state()

    def main_menu(self) -> None:
        self.state_manager.pop_state()
        self.state_manager.push_state(GameStateMenu(self.state_manager))

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
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLORS["PAUSE_OVERLAY"])
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.freetype.SysFont('Arial', 60)
        title_surf, title_rect = font_large.render("PAUSED", COLORS["WHITE"])
        title_rect.center = (WIDTH//2, HEIGHT//2 - 100)
        screen.blit(title_surf, title_rect)
        
        for button in self.buttons:
            button.draw(screen)
        
        pygame.display.flip()
