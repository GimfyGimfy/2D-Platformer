import pygame
from entities.game_object import GameObject
from constants import COLORS

class Checkpoint(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.image = pygame.Surface((30, 30))
        self.image.fill(COLORS["GREEN"]) #active color
        self.rect = self.image.get_rect(topleft=(x, y))
        self.active = True
    
    def deactivate(self):
        self.active = False
        self.image.fill(COLORS["TRANSPARENT_ACCENT"]) #deactivated color