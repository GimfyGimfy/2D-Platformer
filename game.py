import pygame
import sys
import pygame.freetype
from abc import ABC, abstractmethod
from typing import List, Dict, Type

#constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = 12
PLAYER_SPEED = 5
SPRINT_SPEED = 8
SPRINT_ACCELERATION = 1.2
NUM_LEVELS = 3

COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "PLATFORM": (100, 100, 100),
    "MENU_BG": (30, 30, 50),
    "BUTTON": (70, 70, 90),
    "BUTTON_HOVER": (100, 100, 120),
    "BUTTON_TEXT": (200, 200, 220),
    "PAUSE_OVERLAY": (50, 50, 70, 180)
}

#abstract base class defining the interface for all game states (menu, play, pause)
class GameState(ABC):
    @abstractmethod
    def handle_events(self, events: List[pygame.event.Event]) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass

#manages game states
class StateManager:
    def __init__(self):
        self._states: List[GameState] = []
    
    def push_state(self, state: GameState) -> None:
        self._states.append(state)
    
    def pop_state(self) -> None:
        if self._states:
            self._states.pop()
    
    @property
    def current_state(self) -> GameState:
        return self._states[-1] if self._states else None


#base sprite class for all game objects
class GameObject(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Platform(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.image.fill(COLORS["PLATFORM"])

class Spike(GameObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.image.fill(COLORS["RED"])

class Teleporter(GameObject):
    def __init__(self, x: int, y: int, width: int, height: int, target_level: int):
        super().__init__(x, y)
        self.image = pygame.Surface((width, height))
        self.image.fill(COLORS["BLUE"])
        self.target_level = target_level

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
        self.rect.midbottom = (WIDTH // 2 + 15, HEIGHT // 2) #fixed bugs with restarting in wrong spot
        self.velocity_y = 0
        self.gravity_direction = 1
        self.reset_cooldown = 2

class Level:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group() #initialise sprites
        self.platforms = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.teleporters = pygame.sprite.Group()
        self.orbs = pygame.sprite.Group()
        self.player = None

class LevelLoader: #load levels from file
    @staticmethod
    def load(level_num: int) -> Level:
        level = Level()
        try:
            with open(f'levels/level{level_num}.txt', 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if not parts:
                        continue
                    obj_type = parts[0]
                    x = int(parts[1]) * 30 + 400
                    y = -int(parts[2]) * 30 + 300

                    if obj_type == 'platform':
                        platform = Platform(x, y)
                        level.platforms.add(platform)
                        level.all_sprites.add(platform)
                    elif obj_type == 'spike':
                        spike = Spike(x, y)
                        level.spikes.add(spike)
                        level.all_sprites.add(spike)
                    elif obj_type == 'teleport':
                        tele = Teleporter(x, y, int(parts[3]), int(parts[4]), int(parts[5]))
                        level.teleporters.add(tele)
                        level.all_sprites.add(tele)
                    elif obj_type == 'orb':
                        orb = Orb(x, y)
                        level.orbs.add(orb)
                        level.all_sprites.add(orb)
        except FileNotFoundError:
            print(f"Level {level_num} not found!")
            return LevelLoader.load(1)
        
        level.player = Player(WIDTH//2, HEIGHT//2 - 30)
        level.all_sprites.add(level.player)
        return level

class CollisionSystem: #check for touching objects
    @staticmethod
    def handle_collisions(player: Player, level: Level, state_manager: StateManager) -> None:
        teleporters = pygame.sprite.spritecollide(player, level.teleporters, False)
        if teleporters:
            state_manager.push_state(GameStatePlay(state_manager, teleporters[0].target_level))

        if pygame.sprite.spritecollide(player, level.spikes, False):
            player.reset_position()

        for orb in pygame.sprite.spritecollide(player, level.orbs, False):
            if orb.active:
                orb.deactivate()
                player.charged = True
                player.image.fill(COLORS["GREEN"])

class GameStatePlay(GameState):
    def __init__(self, state_manager: StateManager, level_num: int = 1):
        self.state_manager = state_manager
        self.level_num = level_num
        self.level = LevelLoader.load(level_num)
        self.camera = (0, 0)
        self.active_message = None

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.level.player.flip_gravity()
            if event.type == pygame.KEYDOWN:
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

    def _handle_horizontal_collision(self) -> None:
        for platform in self.level.platforms:
            if self.level.player.rect.colliderect(platform.rect):
                if self.level.player.rect.centerx < platform.rect.centerx:
                    self.level.player.rect.right = platform.rect.left
                else:
                    self.level.player.rect.left = platform.rect.right

    def draw(self, screen: pygame.Surface) -> None: #drawing the game + camera with offset
        screen.fill(COLORS["BLACK"])
        self.camera = (self.level.player.rect.centerx - WIDTH//2,
                      self.level.player.rect.centery - HEIGHT//2)
        
        for sprite in self.level.all_sprites:
            screen.blit(sprite.image, (sprite.rect.x - self.camera[0], 
                                      sprite.rect.y - self.camera[1]))
        
        self._draw_ui(screen)
        pygame.display.flip()

    def _draw_ui(self, screen: pygame.Surface) -> None: #stuff in the top left corner
        player = self.level.player
        current_level = self.level_num
        
        # Define instructions and game info
        instructions = [
            f"Level: {current_level}",
            "A & D: Move left and right",
            "Space: Jump",
            "Shift: Sprint",
            "Left Click: Flip Gravity",
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

class GameStatePaused(GameState):
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.buttons = [
            Button(WIDTH//2-150, HEIGHT//2, 300, 60, "Continue", self.continue_game),
            Button(WIDTH//2-150, HEIGHT//2+80, 300, 60, "Main Menu", self.main_menu)
        ]

    def continue_game(self) -> None:
        self.state_manager.pop_state()

    def main_menu(self) -> None:
        self.state_manager.pop_state()
        self.state_manager.push_state(GameStateMenu(self.state_manager))

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            for button in self.buttons:
                button.check_hover(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN and button.is_hovered:
                    button.action()

    def update(self) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLORS["PAUSE_OVERLAY"])
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.freetype.SysFont('Arial', 60)
        title_surf, title_rect = font_large.render("PAUSED", COLORS["WHITE"])
        title_rect.center = (WIDTH//2, HEIGHT//2 - 100)
        screen.blit(title_surf, title_rect)
        
        for button in self.buttons:
            button.draw(screen)
        
        pygame.display.flip()

class GameStateMenu(GameState):
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.buttons = [
            Button(WIDTH//2-150, 200, 300, 60, "Start Game", self.start_game),
            Button(WIDTH//2-150, 280, 300, 60, "Load Game", self.empty_function),
            Button(WIDTH//2-150, 360, 300, 60, "Settings", self.empty_function),
            Button(WIDTH//2-150, 440, 300, 60, "Quit", self.quit_game)
        ]

    def empty_function(self) -> None:
        """Placeholder function for buttons that don't do anything yet"""
        pass

    def start_game(self) -> None:
        self.state_manager.push_state(GameStatePlay(self.state_manager))

    def quit_game(self) -> None:
        pygame.quit()
        sys.exit()

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            for button in self.buttons:
                button.check_hover(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN and button.is_hovered:
                    button.action()

    def update(self) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLORS["MENU_BG"])
        font_large = pygame.freetype.SysFont('Arial', 60)
        title_surf, title_rect = font_large.render("Gravity Platformer", COLORS["WHITE"])
        title_rect.center = (WIDTH//2, 100)
        screen.blit(title_surf, title_rect)
        
        for button in self.buttons:
            button.draw(screen)
        
        pygame.display.flip()

#stuff for buttons

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action: callable):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, surface: pygame.Surface) -> None:
        color = COLORS["BUTTON_HOVER"] if self.is_hovered else COLORS["BUTTON"]
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["BLACK"], self.rect, 2, border_radius=10)
        font = pygame.freetype.SysFont('Arial', 40)
        text_surf, text_rect = font.render(self.text, COLORS["BUTTON_TEXT"])
        text_rect.center = self.rect.center
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos: tuple) -> bool:
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gravity Platformer")
    clock = pygame.time.Clock()
    
    state_manager = StateManager()
    state_manager.push_state(GameStateMenu(state_manager))

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_state = state_manager.current_state
        current_state.handle_events(events)
        current_state.update()
        current_state.draw(screen)
        clock.tick(FPS)

if __name__ == "__main__":
    main()
