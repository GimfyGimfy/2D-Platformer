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

key_repeat_delay = 250
key_repeat_interval = 50
pygame.key.set_repeat(key_repeat_delay, key_repeat_interval)

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
            # Konwersja starych danych
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
    screen.fill(COLORS["background"])
    draw_elements()
    draw_grid()
    draw_player()
    draw_ui()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_level()
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_level()
                running = False

            elif event.key == pygame.K_LEFT:
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
                else:
                    print(f"W tym miejscu jest już: {elements[(x, y)]}")

            elif event.key == pygame.K_x:
                if (x, y) not in elements:
                    elements[(x, y)] = "spike"
                else:
                    print(f"W tym miejscu jest już: {elements[(x, y)]}")

            elif event.key == pygame.K_c:
                if (x, y) not in elements:
                    elements[(x, y)] = "orb"
                else:
                    print(f"W tym miejscu jest już: {elements[(x, y)]}")

            elif event.key == pygame.K_v:
                if (x, y) not in elements:
                    elements[(x, y)] = "teleport"
                else:
                    print(f"W tym miejscu jest już: {elements[(x, y)]}")

            elif event.key == pygame.K_b:
                if (x, y) not in elements:
                    elements[(x, y)] = "sign"
                else:
                    print(f"W tym miejscu jest już: {elements[(x, y)]}")

            elif event.key == pygame.K_e:
                if (x, y) in elements:
                    removed = elements.pop((x, y))
                    print(f"Usunięto element '{removed}' z pozycji ({x}, {y})")
                else:
                    print("Brak elementu do usunięcia na tej pozycji.")

    clock.tick(60)

pygame.quit()
sys.exit()
