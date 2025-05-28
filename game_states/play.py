import pygame
from pygame.math import Vector2
import random
from entities.speedlines import Speedline
from typing import List
from game_states.base import GameState
from game_states.paused import GameStatePaused
from level import Level, LevelLoader
from collision_system import CollisionSystem
from constants import COLORS, PLAYER_SPEED, SPRINT_ACCELERATION, SPRINT_SPEED, CONFIG, BG_IMAGE_PATH

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_states.state_manager import StateManager

class GameStatePlay(GameState):
    def __init__(self, state_manager: 'StateManager', level_num: int = 1):
        self.state_manager = state_manager
        self.level_num = level_num
        self.level = LevelLoader.load(level_num)
        self.camera = (0, 0)
        self.background = pygame.image.load(BG_IMAGE_PATH).convert()
        self.background = pygame.transform.scale(self.background,(CONFIG.WIDTH,CONFIG.HEIGHT))
        self.speed_lines = pygame.sprite.Group()

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.level.player.flip_gravity()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    self.level.player.flip_gravity()
                if event.key == pygame.K_SPACE:
                    self.level.player.jump()
                if event.key == pygame.K_r:
                    self.level.player.reset_position()
                if event.key == pygame.K_ESCAPE:
                    self.state_manager.push_state(GameStatePaused(self.state_manager))

    def update(self) -> None:
        keys = pygame.key.get_pressed()
        dx = 0
        self.level.player.is_sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        if self.level.player.is_sprinting:
            self.level.player.current_speed = min(SPRINT_SPEED, self.level.player.current_speed + SPRINT_ACCELERATION)
        else:
            self.level.player.current_speed = max(PLAYER_SPEED, self.level.player.current_speed - SPRINT_ACCELERATION*1.2)

        if keys[pygame.K_a]:
            dx -= self.level.player.current_speed
        if keys[pygame.K_d]:
            dx += self.level.player.current_speed

        self.level.player.rect.x += dx
        self._handle_horizontal_collision()
        self.level.player.apply_physics(self.level.platforms)
        CollisionSystem.handle_collisions(self.level.player, self.level, self.state_manager)
        self.level.orbs.update()
        if self.level.player.just_flipped:
            self._create_speedlines()
            self.level.player.reset_flip_flag()

        self.speed_lines.update()
        
    def _create_speedlines(self) -> None:
        direction = Vector2(0, self.level.player.gravity_direction)
        camera_left = self.camera[0]
        camera_right = self.camera[0] + CONFIG.WIDTH
        player_y = self.level.player.rect.centery

        #create lines across the entire visible width
        for _ in range(random.randint(30, 40)):
            x = random.randint(camera_left, camera_right)
            y = player_y + random.randint(-200, 200) #vertical spread
            
            #random horizontal offset
            offset = Vector2(
                random.randint(-50, 50),
                random.randint(-100, 100)
            )
            pos = Vector2(x, y) + offset
            
            self.speed_lines.add(Speedline(pos, direction))

    def _handle_horizontal_collision(self) -> None:
        for platform in self.level.platforms:
            if self.level.player.rect.colliderect(platform.rect):
                if self.level.player.rect.centerx < platform.rect.centerx:
                    self.level.player.rect.right = platform.rect.left
                else:
                    self.level.player.rect.left = platform.rect.right

    def draw(self, screen: pygame.Surface) -> None: #drawing the game
        self.camera = (
            self.level.player.rect.centerx - CONFIG.WIDTH // 2,
            self.level.player.rect.centery - CONFIG.HEIGHT // 2
        ) #create camera with offset
        parallax_offset = -self.camera[0] * 0.5 #background parallax effect (scrolling at half speed of camera)
        bg_width = self.background.get_width()

        for i in range(-1, CONFIG.WIDTH // bg_width + 3):
            x = (parallax_offset % bg_width) + i * bg_width - bg_width
            screen.blit(self.background, (x, 0))
        
        for sprite in self.level.all_sprites: #drawing all the sprites on the screen
            screen_x = sprite.rect.x - self.camera[0]
            screen_y = sprite.rect.y - self.camera[1]
            if -30 < screen_x < CONFIG.WIDTH + 30 and -30 < screen_y < CONFIG.HEIGHT + 30:
                screen.blit(sprite.image, (screen_x, screen_y))
        
        for line in self.speed_lines:
            line.offset.update(self.camera)
            screen.blit(line.image, 
                       (line.rect.x - line.offset.x, 
                        line.rect.y - line.offset.y))
        
        self._draw_ui(screen)
        pygame.display.flip()

    def _draw_ui(self, screen: pygame.Surface) -> None: #stuff in the top left corner
        player = self.level.player
        current_level = self.level_num
        
        #defining instructions and game info
        instructions = [
            f"Level: {current_level}",
            "A & D: Move left and right",
            "Space: Jump",
            "Shift: Sprint",
            "Left Click / L: Flip Gravity",
            "R: Reset Position",
            "ESC: Pause Game",
            f"Gravity-Flip ready: {player.charged}"
        ]

        font_small = pygame.freetype.SysFont('Arial', 20)
        line_height = 30
        start_x = 10
        start_y = 40

        gravity_text = "Gravity: DOWN" if player.gravity_direction == 1 else "Gravity: UP"
        text_surf, _ = font_small.render(gravity_text, COLORS["WHITE"])
        screen.blit(text_surf, (10, 10))

        for i, text in enumerate(instructions):
            text_surf, _ = font_small.render(text, COLORS["WHITE"])
            screen.blit(text_surf, (start_x, start_y + i * line_height))
        if self.level.active_sign:
            sign = self.level.active_sign
            font = pygame.freetype.SysFont('Arial', 24)
            
            #calculating screen position relative to camera
            sign_screen_x = sign.rect.x - self.camera[0]
            sign_screen_y = sign.rect.y - self.camera[1] - 40  #position above sign
            
            #text background
            text_surf, text_rect = font.render(sign.message, COLORS["WHITE"])
            bg_rect = text_rect.inflate(20, 10)
            bg_rect.center = (sign_screen_x + sign.rect.width//2, sign_screen_y)
            
            pygame.draw.rect(screen, COLORS["BLACK"], bg_rect)
            pygame.draw.rect(screen, COLORS["WHITE"], bg_rect, 2)
            screen.blit(text_surf, (bg_rect.x + 10, bg_rect.y + 5))
