#constants
import os
import json

GRAVITY = 0.5
JUMP_STRENGTH = 12
PLAYER_SPEED = 5
SPRINT_SPEED = 8
SPRINT_ACCELERATION = 1.2
NUM_LEVELS = 5
BG_IMAGE_PATH="assets/images/background.png"

COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "TRANSPARENT_ACCENT": (54,54,54, 30),
    "RED": (255, 0, 0),
    "DARK_RED": (150, 0, 0),
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
        self._width = 800
        self._height = 600
        self.fullscreen = False
        self.fps = 60
        self.LANGUAGE = "en"
        self.load_config()
        
    @property
    def WIDTH(self):
        return self._width
        
    @property
    def HEIGHT(self):
        return self._height
        
    def set_resolution(self, width: int, height: int):
        self._width = width
        self._height = height
        self.save_config()
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.save_config()
    
    def set_language(self, lang: str):
        self.LANGUAGE = lang
        self.save_config()
    
    def save_config(self):
        config_data = {
            "width": self._width,
            "height": self._height,
            "language": self.LANGUAGE,
            "fullscreen": self.fullscreen
        }
        os.makedirs("config", exist_ok=True)
        with open("config/settings.json", "w") as f:
            json.dump(config_data, f)
    
    def load_config(self):
        try:
            with open("config/settings.json", "r") as f:
                config_data = json.load(f)
                self._width = config_data.get("width", 800)
                self._height = config_data.get("height", 600)
                self.LANGUAGE = config_data.get("language", "en")
                self.fullscreen = config_data.get("fullscreen", False)
        except FileNotFoundError:
            pass

CONFIG = GameConfig()