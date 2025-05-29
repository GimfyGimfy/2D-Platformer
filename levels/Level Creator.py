import pygame
import sys
import os

TILE_SIZE = 32
GRID_WIDTH = 60
GRID_HEIGHT = 40
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE

COLORS = {
    "platform": (150, 150, 150),
    "spike": (255, 0, 0),
    "orb": (0, 255, 255),
    "teleport": (0, 0, 139),
    "sign": (255, 255, 0),
    "player": (0, 255, 0),
    "background": (30, 30, 30),
    "grid": (50, 50, 50)
}

LEVEL_FILENAME = "New_Level.txt"

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Edytor poziomu - Nieskończona mapa")
clock = pygame.time.Clock()

x, y = 0, 0
elements = {}
font = pygame.font.SysFont(None, 24)

half_width = GRID_WIDTH // 2
half_height = GRID_HEIGHT // 2

#key state tracking
key_states = {
    pygame.K_LEFT: False,
    pygame.K_RIGHT: False,
    pygame.K_UP: False,
    pygame.K_DOWN: False,
    pygame.K_z: False,
    pygame.K_x: False,
    pygame.K_c: False,
    pygame.K_v: False,
    pygame.K_b: False,
    pygame.K_e: False
}

#timers for continuous actions
move_timer = 0
block_timer = 0
move_delay = 100 #ms between movement repeats
block_delay = 100 #ms between block placement repeats

def load_level():
    if not os.path.exists(LEVEL_FILENAME):
        print(f"Plik {LEVEL_FILENAME} nie istnieje. Tworzę nowy poziom.")
        return {}

    loaded_elements = {}
    with open(LEVEL_FILENAME, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) != 3:
                print(f"Niepoprawna linia w pliku: {line}")
                continue
            etype, xs, ys = parts
            try:
                px = int(xs)
                py = int(ys)
            except ValueError:
                print(f"Niepoprawne współrzędne w linii: {line}")
                continue
            if etype == "teleporter":
                etype = "teleport"
            loaded_elements[(px, py)] = etype
    print(f"Wczytano {len(loaded_elements)} elementów z pliku {LEVEL_FILENAME}.")
    return loaded_elements

def save_level():
    with open(LEVEL_FILENAME, 'w') as f:
        for (ex, ey), etype in elements.items():
            f.write(f"{etype},{ex},{ey}\n")
    print(f"Poziom zapisany do pliku {LEVEL_FILENAME}.")

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
    pos_text = font.render(f"Pozycja: ({x}, {y})", True, (255, 255, 255))
    screen.blit(pos_text, (10, SCREEN_HEIGHT - 25))

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
    draw_ui()
    pygame.display.flip()

    #handle movement with key repeat
    if move_timer >= move_delay:
        if key_states[pygame.K_LEFT]:
            x -= 1
        if key_states[pygame.K_RIGHT]:
            x += 1
        if key_states[pygame.K_UP]:
            y += 1
        if key_states[pygame.K_DOWN]:
            y -= 1
        move_timer = 0

    #handle block placement with key repeat
    if block_timer >= block_delay:
        if key_states[pygame.K_z]:
            if (x, y) not in elements:
                elements[(x, y)] = "platform"
        if key_states[pygame.K_x]:
            if (x, y) not in elements:
                elements[(x, y)] = "spike"
        if key_states[pygame.K_c]:
            if (x, y) not in elements:
                elements[(x, y)] = "orb"
        if key_states[pygame.K_v]:
            if (x, y) not in elements:
                elements[(x, y)] = "teleport"
        if key_states[pygame.K_b]:
            if (x, y) not in elements:
                elements[(x, y)] = "sign"
        if key_states[pygame.K_e]:
            if (x, y) in elements:
                elements.pop((x, y))
        block_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_level()
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_level()
                running = False
            
            #update key states
            if event.key in key_states:
                key_states[event.key] = True
                
                #handle initial key press immediately
                if event.key == pygame.K_LEFT:
                    x -= 1
                elif event.key == pygame.K_RIGHT:
                    x += 1
                elif event.key == pygame.K_UP:
                    y += 1
                elif event.key == pygame.K_DOWN:
                    y -= 1
                elif event.key == pygame.K_z:
                    if (x, y) not in elements:
                        elements[(x, y)] = "platform"
                elif event.key == pygame.K_x:
                    if (x, y) not in elements:
                        elements[(x, y)] = "spike"
                elif event.key == pygame.K_c:
                    if (x, y) not in elements:
                        elements[(x, y)] = "orb"
                elif event.key == pygame.K_v:
                    if (x, y) not in elements:
                        elements[(x, y)] = "teleport"
                elif event.key == pygame.K_b:
                    if (x, y) not in elements:
                        elements[(x, y)] = "sign"
                elif event.key == pygame.K_e:
                    if (x, y) in elements:
                        elements.pop((x, y))

        elif event.type == pygame.KEYUP:
            if event.key in key_states:
                key_states[event.key] = False

pygame.quit()
sys.exit()
