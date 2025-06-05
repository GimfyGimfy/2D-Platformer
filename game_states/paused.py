import pygame
import json
import os
from typing import List
from game_states.base import GameState
from game_states.menu import GameStateMenu
from ui.button import Button
from constants import COLORS, CONFIG
from language_manager import LANG

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_states.state_manager import StateManager

class GameStatePaused(GameState):
    def __init__(self, state_manager: 'StateManager'):
        self.state_manager = state_manager
        self.save_message_timer = 0
        self.buttons = [
            Button(CONFIG.WIDTH//2-150, CONFIG.HEIGHT//2-60, 300, 60,LANG.strings["ui"]["continue"], self.continue_game),
            Button(CONFIG.WIDTH//2-150, CONFIG.HEIGHT//2+20, 300, 60,LANG.strings["ui"]["save_game"], self.save_game),
            Button(CONFIG.WIDTH//2-150, CONFIG.HEIGHT//2+100, 300, 60,LANG.strings["ui"]["main_menu"], self.main_menu)
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
        if self.save_message_timer > 0:
            self.save_message_timer -= 1/CONFIG.fps #decrease by frame rate
    
    def save_game(self) -> None:
        from game_states.play import GameStatePlay
        #get current play state
        current_play_state = None
        for state in reversed(self.state_manager._states):
            if isinstance(state, GameStatePlay):
                current_play_state = state
                break
        
        if current_play_state:
            save_data = {
                "level": current_play_state.level_num,
                "player_x": current_play_state.level.player.rect.x,
                "player_y": current_play_state.level.player.rect.y,
                "reset_x": current_play_state.level.player.reset_x,
                "reset_y": current_play_state.level.player.reset_y,
                "gravity": current_play_state.level.player.gravity_direction
            }
            
            try:
                with open("saves/save.json", "w") as f:
                    json.dump(save_data, f)
                self.save_message_timer = 2.5
                print("Game saved successfully!")
            except Exception as e:
                print(f"Save failed: {str(e)}")

    def draw(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((CONFIG.WIDTH, CONFIG.HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLORS["PAUSE_OVERLAY"])
        screen.blit(overlay, (0, 0))
        
        font_large = font = pygame.freetype.Font('fonts/Silver.ttf',70)
        title_surf, title_rect = font_large.render(LANG.strings["ui"]["paused"], COLORS["WHITE"])
        title_rect.center = (CONFIG.WIDTH//2, CONFIG.HEIGHT//2 - 100)
        screen.blit(title_surf, title_rect)
        
        for button in self.buttons:
            button.draw(screen)
        
        if self.save_message_timer > 0:
            font = pygame.freetype.Font('fonts/Silver.ttf',34)
            text_surf, text_rect = font.render(LANG.strings["ui"]["game_saved"], COLORS["GREEN"])
            text_rect.bottomright = (CONFIG.WIDTH - 20, CONFIG.HEIGHT - 20)
            screen.blit(text_surf, text_rect)

        
        pygame.display.flip()
