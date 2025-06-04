import pygame
import sys
import os

TILE_SIZE = 32
GRID_WIDTH = 40
GRID_HEIGHT = 25
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE

COLORS = {
    "checkpoint": (88, 88, 88),
    "platform": (150, 150, 150),
    "spike": (255, 0, 0),
    "orb": (0, 255, 255),
    "teleport": (0, 0, 139),
    "sign": (255, 255, 0),
    "player": (0, 255, 0),
    "background": (30, 30, 30),
    "grid": (50, 50, 50)
}

LEVEL_FILENAME = "level1.txt"

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Edytor poziomu - Nieskończona mapa")
clock = pygame.time.Clock()

x, y = 0, 0
elements = {}
font = pygame.font.SysFont(None, 28)

half_width = GRID_WIDTH // 2
half_height = GRID_HEIGHT // 2

key_states = {k: False for k in [
    pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
    pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v,
    pygame.K_b, pygame.K_e, pygame.K_n
]}

move_timer = 0
block_timer = 0
move_delay = 100
block_delay = 100
move_initial_delay = 250

move_press_times = {
    pygame.K_LEFT: None,
    pygame.K_RIGHT: None,
    pygame.K_UP: None,
    pygame.K_DOWN: None
}

def load_level():
    if not os.path.exists(LEVEL_FILENAME):
        print(f"Plik {LEVEL_FILENAME} nie istnieje. Tworzę nowy poziom.")
        return {}
    loaded_elements = {}
    with open(LEVEL_FILENAME, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) != 3:
                continue
            etype, xs, ys = parts
            try:
                px, py = int(xs), int(ys)
            except ValueError:
                continue
            if etype == "teleporter":
                etype = "teleport"
            loaded_elements[(px, py)] = etype
    return loaded_elements

def save_level():
    with open(LEVEL_FILENAME, 'w') as f:
        for (ex, ey), etype in elements.items():
            f.write(f"{etype},{ex},{ey}\n")

def draw_grid():
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLORS["grid"], rect, 1)

def draw_elements():
    cam_x_start = x - half_width
    cam_y_start = y + half_height
    for (ex, ey), etype in elements.items():
        rel_x = ex - cam_x_start
        rel_y = cam_y_start - ey
        if 0 <= rel_x < GRID_WIDTH and 0 <= rel_y < GRID_HEIGHT:
            color = COLORS.get(etype, (255, 255, 255))
            rect = pygame.Rect(rel_x * TILE_SIZE, rel_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)

def draw_player():
    rect = pygame.Rect(half_width * TILE_SIZE, half_height * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, COLORS["player"], rect)

def draw_ui():
    # Statyczna pozycja tekstu
    pos_text = font.render(f"Pozycja: ({x}, {y})", True, (255, 255, 255))
    screen.blit(pos_text, (10, 10))  # Lewy górny róg

elements = load_level()

running = True
while running:
    dt = clock.tick(60)
    move_timer += dt
    block_timer += dt

    screen.fill(COLORS["background"])
    draw_elements()
    draw_grid()
    draw_player()
    draw_ui()  # ← rysujemy UI na końcu, żeby było na wierzchu
    pygame.display.flip()

    for key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
        if key_states[key]:
            press_time = move_press_times[key]
            if press_time is not None:
                held_time = pygame.time.get_ticks() - press_time
                if held_time >= move_initial_delay and move_timer >= move_delay:
                    if key == pygame.K_LEFT: x -= 1
                    elif key == pygame.K_RIGHT: x += 1
                    elif key == pygame.K_UP: y += 1
                    elif key == pygame.K_DOWN: y -= 1
                    move_timer = 0

    if block_timer >= block_delay:
        if key_states[pygame.K_z]: elements.setdefault((x, y), "platform")
        if key_states[pygame.K_x]: elements.setdefault((x, y), "spike")
        if key_states[pygame.K_c]: elements.setdefault((x, y), "orb")
        if key_states[pygame.K_v]: elements.setdefault((x, y), "teleport")
        if key_states[pygame.K_b]: elements.setdefault((x, y), "sign")
        if key_states[pygame.K_n]: elements.setdefault((x, y), "checkpoint")
        if key_states[pygame.K_e]: elements.pop((x, y), None)
        block_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_level()
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_level()
                running = False
            if event.key in key_states:
                key_states[event.key] = True
                if event.key in move_press_times:
                    move_press_times[event.key] = pygame.time.get_ticks()
                if event.key == pygame.K_LEFT: x -= 1
                elif event.key == pygame.K_RIGHT: x += 1
                elif event.key == pygame.K_UP: y += 1
                elif event.key == pygame.K_DOWN: y -= 1
                elif event.key == pygame.K_z: elements.setdefault((x, y), "platform")
                elif event.key == pygame.K_x: elements.setdefault((x, y), "spike")
                elif event.key == pygame.K_c: elements.setdefault((x, y), "orb")
                elif event.key == pygame.K_v: elements.setdefault((x, y), "teleport")
                elif event.key == pygame.K_b: elements.setdefault((x, y), "sign")
                elif event.key == pygame.K_n: elements.setdefault((x, y), "checkpoint")
                elif event.key == pygame.K_e: elements.pop((x, y), None)
        elif event.type == pygame.KEYUP:
            if event.key in key_states:
                key_states[event.key] = False
                if event.key in move_press_times:
                    move_press_times[event.key] = None

pygame.quit()
sys.exit()
