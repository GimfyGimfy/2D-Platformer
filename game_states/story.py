import pygame
from typing import List
from game_states.base import GameState
from constants import CONFIG, COLORS

class GameStateStory(GameState):
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.current_page = 0
        self.alpha = 0
        self.fade_speed = 5
        self.story_pages = [
            [
                "In a world where gravity bends",
                "to the will of unknown,",
                "a lone hero must navigate",
                "the long journey of fate."
            ],
            [
                "Armed with the power to",
                "reverse gravitational pull,",
                "they journey through dangerous",
                "realms to restore balance..."
            ],
            [
                "But beware! The path is",
                "littered with dangers and",
                "mysterious events that",
                "lead to unknown dimensions."
            ]
        ]

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if self.alpha < 255:
                        #skip fade if text isn't fully visible
                        self.alpha = 255
                    else:
                        self.current_page += 1
                        self.alpha = 0
                        if self.current_page >= len(self.story_pages):
                            self.state_manager.push_state(
                                self.state_manager.menu_state
                            )
                elif event.key == pygame.K_ESCAPE:
                    self.state_manager.push_state(
                        self.state_manager.menu_state
                    )

    def update(self) -> None:
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLORS["BLACK"])
        
        #calculate positions
        line_height = 40
        if self.current_page >= len(self.story_pages):
            return
        start_y = CONFIG.HEIGHT//2 - (len(self.story_pages[self.current_page]))*line_height//2
        
        #draw current page with fade
        font = pygame.freetype.SysFont('Arial', 36)
        for i, line in enumerate(self.story_pages[self.current_page]):
            text_surf, _ = font.render(line, COLORS["WHITE"])
            text_surf.set_alpha(self.alpha)
            text_rect = text_surf.get_rect(
                center=(CONFIG.WIDTH//2, start_y + i*line_height)
            )
            screen.blit(text_surf, text_rect)
        
        #draw prompt
        if self.alpha == 255:
            prompt_font = pygame.freetype.SysFont('Arial', 24)
            prompt_text = "Press Z to continue" 
            if self.current_page == len(self.story_pages) - 1:
                prompt_text = "Press Z to begin"
            
            prompt_surf, _ = prompt_font.render(prompt_text, COLORS["WHITE"])
            prompt_rect = prompt_surf.get_rect(
                center=(CONFIG.WIDTH//2, CONFIG.HEIGHT - 50)
            )
            screen.blit(prompt_surf, prompt_rect)
        
        pygame.display.flip()
