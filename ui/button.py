import pygame
from constants import COLORS

#stuff for buttons

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action, text_color=None, 
                 bg_color=None, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

        #colors with defaults
        self.text_color = text_color or COLORS["BUTTON_TEXT"]
        self.bg_color = bg_color or COLORS["BUTTON"]
        self.hover_color = hover_color or COLORS["BUTTON_HOVER"]

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface):
        #draw background
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        
        #draw text
        font = pygame.freetype.SysFont('Arial', 24)
        text_surf, text_rect = font.render(self.text, self.text_color)
        text_rect.center = self.rect.center
        surface.blit(text_surf, text_rect)
        
    def set_text(self, new_text):
        self.text = new_text