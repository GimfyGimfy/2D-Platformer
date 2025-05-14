import pygame
from entities.game_object import GameObject
from constants import COLORS

class Sign(GameObject):
    def __init__(self, x: int, y: int, message: str):
        super().__init__(x, y)
        self.image = pygame.Surface((30, 30))
        self.image.fill(COLORS["YELLOW"])
        self.message = message
        self.detection_radius = 100  # Pixels around sign to trigger message