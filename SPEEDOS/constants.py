#constants
GRAVITY = 0.5
JUMP_STRENGTH = 12
PLAYER_SPEED = 5
SPRINT_SPEED = 8
SPRINT_ACCELERATION = 1.2
NUM_LEVELS = 3
BG_IMAGE_PATH="assets/images/background.png"

COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "PLATFORM": (100, 100, 100),
    "MENU_BG": (30, 30, 50),
    "BUTTON": (70, 70, 90),
    "BUTTON_HOVER": (100, 100, 120),
    "BUTTON_TEXT": (200, 200, 220),
    "PAUSE_OVERLAY": (50, 50, 70, 180)
}

class GameConfig:
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 60

CONFIG = GameConfig()