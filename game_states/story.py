import pygame
from typing import List
from game_states.base import GameState
from constants import CONFIG, COLORS
from ui.button import Button
from language_manager import LANG

class GameStateStory(GameState):
    def __init__(self, state_manager, target_level: int):
        self.state_manager = state_manager
        self.current_page = 0
        self.target_level=target_level
        self.alpha = 0
        self.fade_speed = 5
        
        story_map = {
            2: "level2",
            3: "level3",
            4: "level4",
            5: "level5",
            6: "level6",
            7: "level7",
            8: "level8",
            9: "level9",
            10: "level10",
            99: "ending1",
            98: "ending2"
        }
        
        self.story_pages = []
        story_key = story_map.get(target_level)
        if story_key and story_key in LANG.strings["story"]:
            page_keys = LANG.strings["story"][story_key]
            for key in page_keys:
                if key in LANG.strings["story"]:
                    self.story_pages.append(LANG.strings["story"][key])
        self.active=bool(self.story_pages) #activate only if we have story pages
        self.skip_button = Button(
            CONFIG.WIDTH - 120, 20, 100, 30, #right top corner
            LANG.strings["ui"]["skip"], self.skip_story,
            text_color=COLORS["WHITE"],
            bg_color=COLORS["BLACK"],
            hover_color=COLORS["TRANSPARENT_ACCENT"]
        )
    
    def skip_story(self):
        self.active = False
        self.state_manager.pop_state()
        if self.target_level == 99 or self.target_level == 98:
            from game_states.menu import GameStateMenu
            self.state_manager.push_state(GameStateMenu(self.state_manager))
        else:
            from game_states.play import GameStatePlay
            self.state_manager.push_state(GameStatePlay(self.state_manager, self.target_level))

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.skip_button.check_hover(mouse_pos)
        if not self.active:
            return
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and self.skip_button.is_hovered:
                self.skip_button.action()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if self.alpha < 255:
                        #skip fade if text isn't fully visible
                        self.alpha = 255
                    else:
                        self.current_page += 1
                        self.alpha = 0
                        if self.current_page >= len(self.story_pages):
                            self.state_manager.pop_state()
                            if self.target_level == 99 or self.target_level == 98: #ending
                                from game_states.menu import GameStateMenu
                                self.state_manager.push_state(GameStateMenu(self.state_manager))
                            else:  #level stories
                                from game_states.play import GameStatePlay
                                self.state_manager.push_state(GameStatePlay(self.state_manager, self.target_level))

    def update(self) -> None:
        self.skip_button.rect.x = CONFIG.WIDTH - 120
        self.skip_button.rect.y = 20
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed)

    def draw(self, screen: pygame.Surface) -> None:
        if not self.active or self.current_page >= len(self.story_pages):
            return
        screen.fill(COLORS["BLACK"])
        
        line_height = 40
        start_y = CONFIG.HEIGHT//2 - (len(self.story_pages[self.current_page]))*line_height//2
        
        font = pygame.freetype.Font('fonts/Silver.ttf',44)
        for i, line in enumerate(self.story_pages[self.current_page]):
            text_surf, _ = font.render(line, COLORS["WHITE"])
            text_surf.set_alpha(self.alpha)
            text_rect = text_surf.get_rect(
                center=(CONFIG.WIDTH//2, start_y + i*line_height)
            )
            screen.blit(text_surf, text_rect)
        
        if self.alpha == 255:
            prompt_font = pygame.freetype.Font('fonts/Silver.ttf',40)
            prompt_text = LANG.strings["ui"]["press_z"] 
            if self.current_page == len(self.story_pages) - 1:
                prompt_text = LANG.strings["ui"]["begin"]
            
            prompt_surf, _ = prompt_font.render(prompt_text, COLORS["WHITE"])
            prompt_rect = prompt_surf.get_rect(
                center=(CONFIG.WIDTH//2, CONFIG.HEIGHT - 50)
            )
            screen.blit(prompt_surf, prompt_rect)
        
        self.skip_button.draw(screen)
        pygame.display.flip()