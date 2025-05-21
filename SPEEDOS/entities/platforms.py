import pygame
from entities.game_object import GameObject
from constants import COLORS

class Platform(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.image.fill(COLORS["PLATFORM"])
