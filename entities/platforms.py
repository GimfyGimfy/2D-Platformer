import pygame
from entities.game_object import GameObject
import os

class Platform(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        sprite_path = os.path.join("assets", "images", "platform.png")
        self.image = pygame.image.load(sprite_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
