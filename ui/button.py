import pygame
from constants import COLORS

#stuff for buttons

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface):
        color = COLORS["BUTTON_HOVER"] if self.is_hovered else COLORS["BUTTON"]
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        
        font = pygame.freetype.SysFont('Arial', 24)
        text_surf, text_rect = font.render(self.text, COLORS["BUTTON_TEXT"])
        text_rect.center = self.rect.center
        surface.blit(text_surf, text_rect)