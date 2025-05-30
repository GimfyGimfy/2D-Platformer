import pygame
from entities.game_object import GameObject
from constants import COLORS
from language_manager import LANG

class Sign(GameObject):
    def __init__(self, x: int, y: int, message_key: str):
        super().__init__(x, y)
        self.image = pygame.Surface((30, 30))
        self.image.fill(COLORS["YELLOW"])
        self.message_key = message_key
        self.message = LANG.strings["signs"].get(message_key, message_key)
        self.detection_radius = 100 #pixels around sign to trigger message