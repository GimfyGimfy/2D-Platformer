import pygame
import sys
import json
import os
from typing import List
from ui.button import Button
from constants import COLORS, CONFIG
from game_states.base import GameState
from language_manager import LANG
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_states.state_manager import StateManager
    from game_states.play import GameStatePlay

class GameStateMenu(GameState):
    def __init__(self, state_manager: 'StateManager'):
        self.state_manager = state_manager
        self.last_width = 0
        self.last_height = 0
        self.last_lang = LANG.current_lang #track current language
        self.buttons = []
        self.button_keys = [] #store translation keys for buttons
        self._create_buttons()

    def _create_buttons(self):
        #store current dimensions and language
        self.last_width = CONFIG.WIDTH
        self.last_height = CONFIG.HEIGHT
        self.last_lang = LANG.current_lang
        
        #create buttons with translation keys
        self.button_keys = [
            ("start_game", self.start_game),
            ("load_game", self.load_game),
            ("settings", self.open_settings),
            ("quit", self.quit_game)
        ]

        y_positions = [200, 280, 360, 440]
        self.buttons = []
        
        for i, (key, action) in enumerate(self.button_keys):
            self.buttons.append(Button(
                CONFIG.WIDTH//2-150, 
                y_positions[i], 
                300, 60, 
                LANG.strings["ui"][key], 
                action
            ))

    def update(self) -> None:
        #recreate buttons if resolution or language changed
        if (CONFIG.WIDTH != self.last_width or 
            CONFIG.HEIGHT != self.last_height or
            LANG.current_lang != self.last_lang):
            self._create_buttons()

    def start_game(self) -> None:
        from game_states.play import GameStatePlay
        self.state_manager.push_state(GameStatePlay(self.state_manager))
    
    def open_settings(self):
        from game_states.settings import GameStateSettings
        self.state_manager.push_state(GameStateSettings(self.state_manager))

    def quit_game(self) -> None:
        pygame.quit()
        sys.exit()
    
    def load_game(self) -> None:
        try:
            with open("saves/save.json", "r") as f:
                save_data = json.load(f)
            
            #clear existing states
            while self.state_manager._states:
                self.state_manager.pop_state()
            
            #create new play state with saved data
            from game_states.play import GameStatePlay
            play_state = GameStatePlay(self.state_manager, save_data["level"])
            play_state.level.player.set_position(save_data["player_x"], save_data["player_y"])
            play_state.level.player.set_reset_position(save_data["reset_x"], save_data["reset_y"])
            play_state.level.player.gravity_direction = save_data.get("gravity", 1)
            self.state_manager.push_state(play_state)
            
        except Exception as e:
            print(f"Load failed: {str(e)}")
    
    def on_activate(self):
        #refresh buttons when menu becomes active
        self._create_buttons()

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            for button in self.buttons:
                button.check_hover(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN and button.is_hovered:
                    button.action()
                    
    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLORS["MENU_BG"])
        font_large = pygame.freetype.SysFont('Arial', 60)
        title_surf, title_rect = font_large.render("Gravity Platformer", COLORS["WHITE"])
        title_rect.center = (CONFIG.WIDTH//2, 100)
        screen.blit(title_surf, title_rect)
        
        for button in self.buttons:
            button.draw(screen)
        
        pygame.display.flip()