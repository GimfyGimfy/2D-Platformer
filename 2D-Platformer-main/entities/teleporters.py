import pygame
from entities.game_object import GameObject
from constants import COLORS

class Teleporter(GameObject):
    def __init__(self, x: int, y: int, target_level: int):
        super().__init__(x, y)
        self.image = pygame.Surface((30,30))
        self.image.fill(COLORS["BLUE"])
        self.target_level = target_level
