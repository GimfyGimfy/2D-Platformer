import pygame
from typing import List
from game_states.base import GameState
from ui.button import Button
from constants import CONFIG
# doesn't work yet properly
class GameStateSettings(GameState):
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.buttons = [
            Button(CONFIG.WIDTH//2-150, 200, 300, 60, 
                  "800x600", lambda: self.set_resolution(800, 600)),
            Button(CONFIG.WIDTH//2-150, 280, 300, 60, 
                  "1024x768", lambda: self.set_resolution(1024, 768)),
            Button(CONFIG.WIDTH//2-150, 360, 300, 60, 
                  "Back", self.state_manager.pop_state)
        ]

    def set_resolution(self, width: int, height: int):
        CONFIG.WIDTH = width
        CONFIG.HEIGHT = height
        #notify main game to resize window
        if hasattr(self.state_manager, 'on_resize'):
            self.state_manager.on_resize()
        self.state_manager.pop_state()

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            for button in self.buttons:
                button.check_hover(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN and button.is_hovered:
                    button.action()

    def update(self):
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((30, 30, 50))
        font = pygame.freetype.SysFont('Arial', 60)
        text_surf, text_rect = font.render("Settings", (255, 255, 255))
        text_rect.center = (CONFIG.WIDTH//2, 100)
        screen.blit(text_surf, text_rect)
        for button in self.buttons:
            button.draw(screen)
        pygame.display.flip()