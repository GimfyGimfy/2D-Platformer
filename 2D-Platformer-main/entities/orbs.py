import pygame
from entities.game_object import GameObject
from constants import COLORS

class Orb(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.diameter = 75
        self.radius = self.diameter // 2
        self.active_image = self._create_image((0, 255, 255))
        self.inactive_image = self._create_image((100, 100, 100))
        self.image = self.active_image
        self.rect = self.image.get_rect(center=(x + 15, y + 15))
        self.active = True
        self.respawn_time = 0

    def _create_image(self, color: tuple) -> pygame.Surface:
        surface = pygame.Surface((self.diameter, self.diameter), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (self.radius, self.radius), self.radius)
        return surface

    def deactivate(self) -> None: #orbs deactivate on touch, reactivate after certain time
        if self.active:
            self.active = False
            self.image = self.inactive_image
            self.respawn_time = pygame.time.get_ticks() + 2000 #2 seconds

    def update(self) -> None: #check for conditions
        if not self.active and pygame.time.get_ticks() > self.respawn_time:
            self.active = True
            self.image = self.active_image
