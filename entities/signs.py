import pygame
from entities.game_object import GameObject
import os
from language_manager import LANG

class Sign(GameObject):
    def __init__(self, x: int, y: int, message_key: str):
        super().__init__(x, y)
        self.image = pygame.Surface((30, 30))
        sprite_path = os.path.join("assets", "images", "sign.png")
        self.image = pygame.image.load(sprite_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.message_key = message_key
        self.message = LANG.strings["signs"].get(message_key, message_key)
        self.detection_radius = 100 #pixels around sign to trigger message
