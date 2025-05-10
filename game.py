import pygame
import sys
import pygame.freetype  # better rendering

pygame.init()

# parameters
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = 12
PLAYER_SPEED = 5
SPRINT_SPEED = 8
SPRINT_ACCELERATION = 1.2
NUM_LEVELS = 3
current_level = 1
VICTORY = 4 #temporary

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PLAYER_COLOR = GREEN
PLATFORM_COLOR = (100, 100, 100)
SPIKE_COLOR = RED
MENU_BG = (30, 30, 50)
BUTTON_COLOR = (70, 70, 90)
BUTTON_HOVER = (100, 100, 120)
BUTTON_TEXT = (200, 200, 220)
PAUSE_OVERLAY = (50, 50, 70, 180)

# create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Platformer")
clock = pygame.time.Clock()

# game states
MENU = 0
GAME = 1
PAUSED = 2
current_state = MENU

# font setup
font_large = pygame.freetype.SysFont('Arial', 60)
font_medium = pygame.freetype.SysFont('Arial', 40)
font_small = pygame.freetype.SysFont('Arial', 30)


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        text_surf, text_rect = font_medium.render(self.text, BUTTON_TEXT)
        text_rect.center = self.rect.center
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # when click
            if self.is_hovered and self.action:
                return self.action()
        return None

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_y = 0
        self.gravity_direction = 1  # 1 for down, -1 for up
        self.on_ground = False
        self.charged = True
        self.current_speed = PLAYER_SPEED
        self.is_sprinting = False

    def update(self, platforms):
        # handle horizontal movement
        dx = 0
        keys = pygame.key.get_pressed()
        self.is_sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        if self.is_sprinting:
            # accelerate to sprint speed
            if self.current_speed < SPRINT_SPEED:
                self.current_speed += SPRINT_ACCELERATION
        else:
            # decelerate to normal speed
            if self.current_speed > PLAYER_SPEED:
                self.current_speed -= SPRINT_ACCELERATION * 1.2  # faster deceleration

        self.current_speed = max(PLAYER_SPEED, min(self.current_speed, SPRINT_SPEED))
        
        if keys[pygame.K_LEFT]:
            dx -= self.current_speed
        if keys[pygame.K_RIGHT]:
            dx += self.current_speed
        
        self.rect.x += dx

        # check horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0:  # moving right
                    self.rect.right = platform.rect.left
                elif dx < 0:  # moving left
                    self.rect.left = platform.rect.right

         # vertical movement
        self.velocity_y += GRAVITY * self.gravity_direction
        dy = self.velocity_y
        step = int(abs(dy)) + 1
        step_direction = int(dy / abs(dy)) if dy != 0 else 0

        self.on_ground = False
        for i in range(step):
            self.rect.y += step_direction
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.gravity_direction == 1:  # gravity down
                        if step_direction > 0:
                            self.rect.bottom = platform.rect.top
                            self.velocity_y = 0
                            self.on_ground = True
                            self.charged = True
                            self.image.fill(PLAYER_COLOR)
                        elif step_direction < 0:
                            self.rect.top = platform.rect.bottom
                            self.velocity_y = 0
                    else:  # gravity up
                        if step_direction < 0:
                            self.rect.top = platform.rect.bottom
                            self.velocity_y = 0
                            self.on_ground = True
                            self.charged = True
                            self.image.fill(PLAYER_COLOR)
                        elif step_direction > 0:
                            self.rect.bottom = platform.rect.top
                            self.velocity_y = 0
                    break  # stop checking after a collision

        # platform collision
        hits = pygame.sprite.spritecollide(self, teleporters, False)
        if hits:
            create_game_objects(hits[0].target_level)
            
        # spike collision
        hits_spike = pygame.sprite.spritecollide(self, spikes, False)
        if hits_spike:
            player.gravity_direction = 1
            player.rect.x = WIDTH // 2
            player.rect.y = HEIGHT // 2 - 30
            player.velocity_y = 0
            
        # orb collision
        hits_orb = pygame.sprite.spritecollide(self, orbs, False)
        if hits_orb:
            self.charged = True
            self.image.fill(PLAYER_COLOR)
            

    def jump(self):
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH * self.gravity_direction

    def flip_gravity(self):
        if self.charged:
            self.gravity_direction *= -1
            self.velocity_y = 0
            self.charged = False
            self.image.fill(WHITE)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(SPIKE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Sign(pygame.sprite.Sprite):
    def __init__(self, x, y, message):
        super().__init__()
        self.image = pygame.Surface((20,20))
        self.image.fill((200, 200, 0))
        self.rect = self.image.get_rect(center=(x,y))
        self.message = message

class Orb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.active =  True

class Teleporter(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, target_level):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.target_level = target_level


def create_game_objects(level=1):
    global all_sprites, platforms, spikes, signs, orbs, player, teleporters, current_level
    
    current_level = level  # Store current level
    
    # Clear existing sprites
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    teleporters = pygame.sprite.Group()
    signs = pygame.sprite.Group()
    orbs = pygame.sprite.Group()
    
    # Create player
    player = Player(WIDTH // 2, HEIGHT // 2)
    all_sprites.add(player)

    # Load level data
    filename = f'levels/level{level}.txt'
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    obj_type = parts[0]
                    
                    if obj_type == 'platform':
                        x, y = map(int, parts[1:3])
                        p = Platform(x*30+400, -y*30+300)
                        platforms.add(p)
                        all_sprites.add(p)

                    elif obj_type == 'spike':
                        x, y = map(int, parts[1:3])
                        s = Spike(x*30+400, -y*30+300)
                        spikes.add(s)
                        all_sprites.add(s)
                        
                    elif obj_type == 'teleport':
                        x, y, w, h, target = map(int, parts[1:6])
                        t = Teleporter(x, y, w, h, target)
                        teleporters.add(t)
                        all_sprites.add(t)
                        
                    elif obj_type == 'sign':
                        x_grid, y_grid = map(int, parts[1:3])
                        message = ','.join(parts[3:])  #join remaining parts as message
                        x = x_grid * 30 + 400
                        y = y_grid * 30 + 300
                        sign = Sign(x, y, message)
                        signs.add(sign)
                        all_sprites.add(sign)

                    elif obj_type == 'orb':
                        x, y = map(int, parts[1:3])
                        o = Orb(x*30+400, -y*30+300)
                        orbs.add(o)
                        all_sprites.add(o)
                        
    except FileNotFoundError:
        if level > current_level:  # Only show victory if progressing forward
            current_state = VICTORY
            return
        else:
            # Handle fallback for missing level files
            print(f"Level {level} not found!")
            current_level = 1
            create_game_objects(1)
        

def draw_menu():
    screen.fill(MENU_BG)

    # title
    title_surf, title_rect = font_large.render("Gravity Platformer", WHITE)
    title_rect.center = (WIDTH // 2, 100)
    screen.blit(title_surf, title_rect)

    # buttons
    for button in menu_buttons:
        button.draw(screen)

    pygame.display.flip()


def draw_game():
    screen.fill(BLACK)
    
    #calculate camera offset
    camera_x = player.rect.centerx - WIDTH //2
    camera_y = player.rect.centery - HEIGHT // 2
    
    #draw all sprites but include camera offset
    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y - camera_y))

    #check for active sign message
    active_message = None
    for sign in signs:
        #distance
        distance = pygame.math.Vector2(player.rect.center).distance_to(sign.rect.center)
        if distance < 150:
            active_sign = sign
            break

    #draw sign message
    if active_message:
        #background
        text_bg = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
        text_bg.fill((0, 0, 0, 128))
        # text rendering
        text_surface, text_rect = font_medium.render(active_message, WHITE)
        text_rect.center = (WIDTH // 2, 25)
        text_bg.blit(text_surface, text_rect)
        screen.blit(text_bg, (0, 0))

    # info
    gravity_text = "Gravity: DOWN" if player.gravity_direction == 1 else "Gravity: UP"
    text_surface, text_rect = font_small.render(gravity_text, WHITE)
    screen.blit(text_surface, (10, 10))

    instructions = [
        f"Level: {current_level}",
        "Space: Jump",
        "Shift: Sprint",
        "F: Flip Gravity",
        "R: Reset Position",
        "ESC: Pause Game",
        "Charge: " + str(player.charged)
    ]
    for i, instruction in enumerate(instructions):
        instr_text, instr_rect = font_small.render(instruction, WHITE)
        screen.blit(instr_text, (10, 50 + i * 30))

    pygame.display.flip()

def draw_victory():
    screen.fill(MENU_BG)
    
    title_surf, title_rect = font_large.render("CONGRATULATIONS!", GREEN)
    title_rect.center = (WIDTH // 2, HEIGHT // 2 - 50)
    screen.blit(title_surf, title_rect)
    
    sub_surf, sub_rect = font_medium.render("You've completed all levels!", WHITE)
    sub_rect.center = (WIDTH // 2, HEIGHT // 2 + 50)
    screen.blit(sub_surf, sub_rect)
    
    pygame.display.flip()

def draw_pause_menu():
    # overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(PAUSE_OVERLAY)
    screen.blit(overlay, (0, 0))

    title_surf, title_rect = font_large.render("PAUSED", WHITE)
    title_rect.center = (WIDTH // 2, HEIGHT // 2 - 100)
    screen.blit(title_surf, title_rect)

    for button in pause_buttons:
        button.draw(screen)

    pygame.display.flip()


def quit_game():
    pygame.quit()
    sys.exit()


def start_game():
    global current_state
    current_state = GAME
    create_game_objects()


def continue_game():
    global current_state
    current_state = GAME


def dummy_action():
    print(f"This button doesn't do anything yet")


def return_to_menu():
    global current_state
    current_state = MENU


def toggle_pause():
    global current_state
    if current_state == GAME:
        current_state = PAUSED
    elif current_state == PAUSED:
        current_state = GAME


# main menu buttons
menu_buttons = [
    Button(WIDTH // 2 - 150, 200, 300, 60, "Start Game", start_game),
    Button(WIDTH // 2 - 150, 280, 300, 60, "Save Game", dummy_action),
    Button(WIDTH // 2 - 150, 280, 300, 60, "Load Game", dummy_action),
    Button(WIDTH // 2 - 150, 360, 300, 60, "Settings", dummy_action),
    Button(WIDTH // 2 - 150, 440, 300, 60, "End Game", quit_game)
]

# pause menu buttons
pause_buttons = [
    Button(WIDTH // 2 - 150, HEIGHT // 2, 300, 60, "Continue", continue_game),
    Button(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, "Main Menu", return_to_menu)
]

def set_state(new_state):
    global current_state
    current_state = new_state

def start_game(level=1):
    create_game_objects(level)
    set_state(GAME)


# main game loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == MENU:
            for button in menu_buttons:
                button.check_hover(mouse_pos)
                button.handle_event(event)
        elif current_state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_f:  # flip gravity
                    player.flip_gravity()
                if event.key == pygame.K_r:  # reset position
                    player.rect.x = WIDTH // 2
                    player.rect.y = HEIGHT // 2 - 30
                    player.velocity_y = 0
                    player.gravity_direction=1
                if event.key == pygame.K_ESCAPE:  # toggle pause
                    toggle_pause()
        elif current_state == PAUSED:
            for button in pause_buttons:
                button.check_hover(mouse_pos)
                button.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # unpause if paused
                    toggle_pause()

    # drawing screen based on the game state
    if current_state == MENU:
        draw_menu()
    elif current_state == GAME:
        player.update(platforms)
        draw_game()
    elif current_state == PAUSED:
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY)
        screen.blit(overlay, (0, 0))

        # title
        title_surf, title_rect = font_large.render("PAUSED", WHITE)
        title_rect.center = (WIDTH // 2, HEIGHT // 2 - 100)
        screen.blit(title_surf, title_rect)

        # hovering and button drawing
        for button in pause_buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)

        pygame.display.flip()
    elif current_state == VICTORY:
        draw_victory()

    clock.tick(FPS)

pygame.quit()
sys.exit()
