import pygame
from entities.game_object import GameObject
from constants import COLORS
import math

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
        
        blur_factor = 1.5 #to adjust blur strength
        
        for y in range(self.diameter):
            for x in range(self.diameter):
                #distance from the center
                dist = math.sqrt((x - self.radius) ** 2 + (y - self.radius) ** 2)
                
                if dist < self.radius:
                    #blur calculation
                    intensity = 255 - int((dist / self.radius) ** blur_factor * 255)
                    surface.set_at((x, y), (*color[:3], intensity))
                else:
                    surface.set_at((x, y), (0, 0, 0, 0)) #fully transparent outside the circle
        return surface

    def deactivate(self) -> None: #orbs deactivate on touch, reactivate after certain time
        if self.active:
            self.active = False
            self.image = self.inactive_image
            self.respawn_time = pygame.time.get_ticks() + 2000 #2 seconds

    def update(self) -> None:
        if not self.active and pygame.time.get_ticks() > self.respawn_time:
            self.active = True
            self.image = self.active_image
