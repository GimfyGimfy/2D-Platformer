import pygame
import os
from entities.game_object import GameObject
from constants import COLORS, GRAVITY, JUMP_STRENGTH, PLAYER_SPEED, SPRINT_SPEED, SPRINT_ACCELERATION

class AnimationHandler:
    def __init__(self, base_path: str):
        self.animations_normal = self._load_animations(base_path)
        self.animations_upside_down = self._create_upside_down_animations()
        self.walk_frames = ["walk1", "idle", "walk2", "idle"]
        self.run_frames = ["Run1", "Run2", "Run1", "Run3"]
        self.animation_index = 0
        self.animation_timer = 0

    def _load_animations(self, base_path: str) -> dict:
        frame_names = [
            "idle", "walk1", "walk2", 
            "Run1", "Run2", "Run3",
            "JumpUp", "JumpDown", "JumpDownAlt"
        ]
        
        #load right-facing frames
        right_frames = {}
        for name in frame_names:
            img = pygame.image.load(os.path.join(base_path, f"{name}.png")).convert_alpha()
            right_frames[name] = img
        
        #load left-facing frames
        left_frames = {}
        for name, img in right_frames.items():
            left_frames[name] = pygame.transform.flip(img, True, False)
        
        return {
            "right": right_frames,
            "left": left_frames
        }

    def _create_upside_down_animations(self) -> dict:
        upside_down = {}
        for direction in ["right", "left"]:
            upside_down[direction] = {
                name: pygame.transform.flip(img, False, True)
                for name, img in self.animations_normal[direction].items()
            }
        return upside_down

    def get_animation_set(self, gravity_direction: int) -> dict:
        """Get appropriate animation set based on gravity direction"""
        return self.animations_normal if gravity_direction == 1 else self.animations_upside_down

    def update_animation_state(self, is_sprinting: bool, speed: float, animation_speed: float) -> None:
        if speed > 0.1:
            self.animation_timer += animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                frames = self.run_frames if is_sprinting else self.walk_frames
                self.animation_index = (self.animation_index + 1) % len(frames)
        else:
            self.animation_index = 0
            self.animation_timer = 0

class Player(GameObject):
    def __init__(self, x: int, y: int, level_num: int):
        super().__init__(x, y)
        self.level_num = level_num
        
        #physics
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

        #animations
        self.animation_handler = AnimationHandler(os.path.join("assets", "images"))
        self.direction = "right"
        self.image = self._get_current_animation_set()["idle"]
        self.rect = self.image.get_rect(midbottom=(x + 15, y))

    def _get_current_animation_set(self) -> dict:
        return self.animation_handler.get_animation_set(self.gravity_direction)[self.direction]

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
            if self.level_num != 4:
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
        if self.just_flipped:
            self.image = self._get_current_animation_set().get("JumpDown", self._get_current_animation_set()["idle"])
            return

        if not self.on_ground:
            self._handle_jump_animation()
            return

        self._handle_ground_animation(x_velocity)

    def _handle_jump_animation(self):
        if self.velocity_y * self.gravity_direction < 0:
            frame = "JumpUp"
        else:
            frame = "JumpDown" if self.charged else "JumpDownAlt"
        self.image = self._get_current_animation_set().get(frame, self._get_current_animation_set()["idle"])
        self.animation_handler.animation_timer = 0
        self.animation_handler.animation_index = 0

    def _handle_ground_animation(self, x_velocity: float):
        speed = abs(x_velocity)
        animation_speed = 1 / (6 if self.is_sprinting else 5)
        frames = self.animation_handler.run_frames if self.is_sprinting else self.animation_handler.walk_frames
        
        self.animation_handler.update_animation_state(self.is_sprinting, speed, animation_speed)
        
        if speed > 0.1:
            frame_name = frames[self.animation_handler.animation_index]
            self.image = self._get_current_animation_set()[frame_name]
        else:
            self.image = self._get_current_animation_set()["idle"]

    def update(self, x_velocity: float):
        if x_velocity > 0:
            self.direction = "right"
        elif x_velocity < 0:
            self.direction = "left"

        self.rect.x += int(x_velocity)
        self.update_animation(x_velocity)