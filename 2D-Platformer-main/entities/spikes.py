import pygame
from entities.game_object import GameObject
import os

class Spike(GameObject):
    def __init__(self, x: int, y: int, platforms_group: pygame.sprite.Group):
        super().__init__(x, y)

        normal_sprite = pygame.image.load(os.path.join("assets", "images", "spike.png")).convert_alpha()
        alt_sprite = pygame.image.load(os.path.join("assets", "images", "spike2.png")).convert_alpha()

        rect_above = pygame.Rect(x, y - 30, 30, 30)
        is_covered = any(platform.rect.colliderect(rect_above) for platform in platforms_group)

        self.image = alt_sprite if is_covered else normal_sprite
        self.rect = self.image.get_rect(topleft=(x, y))
