import pygame
from entities.game_object import GameObject
from constants import COLORS, GRAVITY, JUMP_STRENGTH, PLAYER_SPEED, SPRINT_SPEED, SPRINT_ACCELERATION, WIDTH, HEIGHT

class Player(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.image = pygame.Surface((30, 50)) #sprite 30x50
        self.rect = self.image.get_rect(midbottom=(x + 15, y)) #fixed collisions
        self.image.fill(COLORS["GREEN"])
        self.velocity_y = 0
        self.gravity_direction = 1
        self.on_ground = False
        self.charged = True
        self.current_speed = PLAYER_SPEED
        self.is_sprinting = False
        self.reset_cooldown = 0

    #movement stuff

    def apply_physics(self, platforms: pygame.sprite.Group) -> None:
        if self.reset_cooldown > 0:
            self.reset_cooldown -= 1
            return

        self.velocity_y += GRAVITY * self.gravity_direction
        self._handle_vertical_collision(platforms)

    def _handle_vertical_collision(self, platforms: pygame.sprite.Group) -> None:
        step = int(abs(self.velocity_y)) + 1 #small step for checking changes in position
        step_dir = 1 if self.velocity_y > 0 else -1
        self.on_ground = False

        for _ in range(step):
            self.rect.y += step_dir
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    self._resolve_vertical_collision(platform, step_dir)
                    return

    def _resolve_vertical_collision(self, platform: GameObject, step_dir: int) -> None:
        if self.gravity_direction == 1:
            if step_dir == 1:
                self.rect.bottom = platform.rect.top
                self.on_ground = True
            else:
                self.rect.top = platform.rect.bottom
        else:
            if step_dir == -1:
                self.rect.top = platform.rect.bottom
                self.on_ground = True
            else:
                self.rect.bottom = platform.rect.top
        self.velocity_y = 0
        if self.on_ground:
            self.charged = True
            self.image.fill(COLORS["GREEN"])

    def jump(self) -> None:
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH * self.gravity_direction

    def flip_gravity(self) -> None:
        if self.charged:
            self.gravity_direction *= -1
            self.velocity_y = 0
            self.charged = False
            self.image.fill(COLORS["WHITE"])

    def reset_position(self) -> None:
        self.rect.midbottom = (415,300) #fixed bugs with restarting in wrong spot
        self.velocity_y = 0
        self.gravity_direction = 1
        self.reset_cooldown = 2
