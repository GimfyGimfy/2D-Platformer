import pygame
from entities.game_object import GameObject
from constants import COLORS, GRAVITY

class Speedline(GameObject):
    def __init__(self, x: int, y: int, g: int):
        super().__init__(x, y)
        self.image = pygame.Surface((2, 100))
        self.rect = self.image.get_rect(midbottom=(x + 15, y))
        self.image.fill(COLORS["WHITE"])
        self.gravity_direction = g
        self.velocity_y = 25 * self.gravity_direction
        self.on_ground = False

    def apply_physics(self) -> None:
        self.velocity_y += GRAVITY * self.gravity_direction
        self._handle_vertical_collision()

    def _handle_vertical_collision(self) -> None:
        step = int(abs(self.velocity_y)) + 1 #small step for checking changes in position
        step_dir = 1 if self.velocity_y > 0 else -1
        self.on_ground = False

        for _ in range(step):
            self.rect.y += step_dir
