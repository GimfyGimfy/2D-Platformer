import pygame
import os
from entities.game_object import GameObject
from constants import COLORS, GRAVITY, JUMP_STRENGTH, PLAYER_SPEED, SPRINT_SPEED, SPRINT_ACCELERATION

class Player(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)

        base_path = os.path.join("assets", "images")
        idle = pygame.image.load(os.path.join(base_path, "idle.png")).convert_alpha()
        walk1 = pygame.image.load(os.path.join(base_path, "walk1.png")).convert_alpha()
        walk2 = pygame.image.load(os.path.join(base_path, "walk2.png")).convert_alpha()

        run1 = pygame.image.load(os.path.join(base_path, "Run1.png")).convert_alpha()
        run2 = pygame.image.load(os.path.join(base_path, "Run2.png")).convert_alpha()
        run3 = pygame.image.load(os.path.join(base_path, "Run3.png")).convert_alpha()

        jump_up = pygame.image.load(os.path.join(base_path, "JumpUp.png")).convert_alpha()
        jump_down = pygame.image.load(os.path.join(base_path, "JumpDown.png")).convert_alpha()
        jump_down_alt = pygame.image.load(os.path.join(base_path, "JumpDownAlt.png")).convert_alpha()

        self.animations_normal = {
            "right": {
                "idle": idle,
                "walk1": walk1,
                "walk2": walk2,
                "run1": run1,
                "run2": run2,
                "run3": run3,
                "JumpUp": jump_up,
                "JumpDown": jump_down,
                "JumpDownAlt": jump_down_alt
            },
            "left": {
                "idle": pygame.transform.flip(idle, True, False),
                "walk1": pygame.transform.flip(walk1, True, False),
                "walk2": pygame.transform.flip(walk2, True, False),
                "run1": pygame.transform.flip(run1, True, False),
                "run2": pygame.transform.flip(run2, True, False),
                "run3": pygame.transform.flip(run3, True, False),
                "JumpUp": pygame.transform.flip(jump_up, True, False),
                "JumpDown": pygame.transform.flip(jump_down, True, False),
                "JumpDownAlt": pygame.transform.flip(jump_down_alt, True, False)
            }
        }

        self.animations_upside_down = {
            "right": {k: pygame.transform.flip(v, False, True) for k, v in self.animations_normal["right"].items()},
            "left": {k: pygame.transform.flip(v, False, True) for k, v in self.animations_normal["left"].items()}
        }

        self.walk_frames = ["walk1", "idle", "walk2", "idle"]
        self.run_frames = ["run1", "run2", "run1", "run3"]
        self.animation_index = 0
        self.animation_timer = 0
        self.direction = "right"

        self.image = self.animations_normal[self.direction]["idle"]
        self.rect = self.image.get_rect(midbottom=(x + 15, y))

        # Fizyczne właściwości
        self.velocity_y = 0
        self.gravity_direction = 1
        self.on_ground = False
        self.charged = True
        self.current_speed = PLAYER_SPEED
        self.is_sprinting = False
        self.reset_cooldown = 0
        self.just_flipped = False
        self.reset_x = x
        self.reset_y = y

    def apply_physics(self, platforms: pygame.sprite.Group) -> None:
        if self.reset_cooldown > 0:
            self.reset_cooldown -= 1
            return

        self.velocity_y += GRAVITY * self.gravity_direction
        self._handle_vertical_collision(platforms)

    def _handle_vertical_collision(self, platforms: pygame.sprite.Group) -> None:
        step = int(abs(self.velocity_y)) + 1
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

    def jump(self) -> None:
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH * self.gravity_direction

    def flip_gravity(self) -> None:
        if self.charged:
            self.gravity_direction *= -1
            self.velocity_y = 0
            self.charged = False
            self.just_flipped = True

    def set_position(self, x: int, y: int) -> None:
        self.rect.x = x
        self.rect.y = y

    def set_reset_position(self, x: int, y: int):
        self.reset_x = x
        self.reset_y = y

    def reset_position(self):
        self.rect = self.image.get_rect(midbottom=(self.reset_x + 15, self.reset_y))
        self.velocity_y = 0
        self.gravity_direction = 1

    def reset_flip_flag(self) -> None:
        self.just_flipped = False

    def update_animation(self, x_velocity: float) -> None:
        animations = self.animations_normal if self.gravity_direction == 1 else self.animations_upside_down
        direction_anim = animations[self.direction]

        if self.just_flipped:
            self.image = direction_anim.get("JumpDown", direction_anim["idle"])
            self.just_flipped = False
            return

        speed = abs(x_velocity)
        walk_animation_speed = 5
        run_animation_speed = 4

        if not self.on_ground:
            if self.velocity_y * self.gravity_direction < 0:
                frame = "JumpUp"
            else:
                if self.charged:
                    frame = "JumpDown"
                else:
                    frame = "JumpDownAlt"
            self.image = direction_anim.get(frame, direction_anim["idle"])
            self.animation_timer = 0
            self.animation_index = 0
            return

        if speed > 0.1:
            if self.is_sprinting:
                animation_speed = 1 / run_animation_speed
                frames = self.run_frames
            else:
                animation_speed = 1 / walk_animation_speed
                frames = self.walk_frames

            self.animation_timer += animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.animation_index = (self.animation_index + 1) % len(frames)
                frame_name = frames[self.animation_index]
                self.image = direction_anim[frame_name]
        else:
            self.image = direction_anim["idle"]
            self.animation_index = 0
            self.animation_timer = 0

    def update(self, x_velocity: float):
        if x_velocity > 0:
            self.direction = "right"
        elif x_velocity < 0:
            self.direction = "left"

        self.rect.x += int(x_velocity)
        self.update_animation(x_velocity)
