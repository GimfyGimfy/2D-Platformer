import pygame
from typing import List
from game_states.base import GameState
from ui.button import Button
from constants import CONFIG, COLORS
from language_manager import LANG

class GameStateSettings(GameState):
    def __init__(self, state_manager):
        super().__init__()
        self.state_manager = state_manager
        self._create_buttons()

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            for button in self.buttons:
                button.check_hover(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN and button.is_hovered:
                    button.action()

    def update(self) -> None:
        pass  #no updates needed

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLORS["MENU_BG"])
        font = pygame.freetype.SysFont('Arial', 60)
        
        #draw section headers
        font_section = pygame.freetype.SysFont('Arial', 30)
        res_text, res_rect = font_section.render(LANG.strings["ui"]["resolution"], COLORS["WHITE"])
        res_rect.midleft = (CONFIG.WIDTH//2 - 150, self.resolution_label_y)
        screen.blit(res_text, res_rect)
        
        lang_text, lang_rect = font_section.render(LANG.strings["ui"]["language"], COLORS["WHITE"])
        lang_rect.midleft = (CONFIG.WIDTH//2 - 150, self.language_label_y)
        screen.blit(lang_text, lang_rect)
        
        for button in self.buttons:
            button.draw(screen)
        
        pygame.display.flip()

    def _create_buttons(self):
        button_height = 60
        button_spacing = 20
        total_height = (7 * button_height) + (6 * button_spacing)
        start_y = (CONFIG.HEIGHT - total_height) // 2 + 40
        
        #section headers
        self.resolution_label_y = start_y - 40
        self.language_label_y = start_y + 4*(button_height + button_spacing) - 40
        
        self.buttons = [
            #resolution buttons
            Button(CONFIG.WIDTH//2 - 150, start_y, 300, button_height, 
                   "800x600", lambda: self.set_resolution(800, 600)),
            Button(CONFIG.WIDTH//2 - 150, start_y + button_height + button_spacing, 
                   300, button_height, "1024x768", lambda: self.set_resolution(1024, 768)),
            Button(CONFIG.WIDTH//2 - 150, start_y + 2*(button_height + button_spacing), 
                   300, button_height, "1280x720", lambda: self.set_resolution(1280, 720)),
            Button(CONFIG.WIDTH//2 - 150, start_y + 3*(button_height + button_spacing), 
                   300, button_height, "1920x1080", lambda: self.set_resolution(1920, 1080)),
            
            #language buttons
            Button(CONFIG.WIDTH//2 - 150, start_y + 4*(button_height + button_spacing), 
                   140, button_height, LANG.strings["ui"]["english"], lambda: self.set_language("en")),
            Button(CONFIG.WIDTH//2 + 10, start_y + 4*(button_height + button_spacing), 
                   140, button_height, LANG.strings["ui"]["russian"], lambda: self.set_language("ru")),
            
            #back button
            Button(CONFIG.WIDTH//2 - 150, start_y + 5*(button_height + button_spacing), 
                   300, button_height, LANG.strings["ui"]["back"], self.go_back)
        ]

    def set_resolution(self, width: int, height: int):
        CONFIG.set_resolution(width, height)
        if self.state_manager.resize_callback:
            self.state_manager.resize_callback()
        self._create_buttons()
    
    def set_language(self, lang_code: str):
        CONFIG.set_language(lang_code)
        LANG.set_language(lang_code)
        if self.state_manager.resize_callback:
            self.state_manager.resize_callback()
        self._create_buttons()

    def go_back(self):
        from game_states.menu import GameStateMenu
        if self.state_manager._states and len(self.state_manager._states) >= 2:
            prev_state = self.state_manager._states[-2]
            if isinstance(prev_state, GameStateMenu):
                prev_state.on_activate()
        self.state_manager.pop_state()