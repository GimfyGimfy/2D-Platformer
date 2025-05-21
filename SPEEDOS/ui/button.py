import pygame
from constants import COLORS

#stuff for buttons

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action: callable):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, surface: pygame.Surface) -> None:
        color = COLORS["BUTTON_HOVER"] if self.is_hovered else COLORS["BUTTON"]
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["BLACK"], self.rect, 2, border_radius=10)
        font = pygame.freetype.SysFont('Arial', 40)
        text_surf, text_rect = font.render(self.text, COLORS["BUTTON_TEXT"])
        text_rect.center = self.rect.center
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos: tuple) -> bool:
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
