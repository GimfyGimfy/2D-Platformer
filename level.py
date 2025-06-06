import pygame
from constants import CONFIG
from entities.platforms import Platform
from entities.spikes import Spike
from entities.teleporters import Teleporter
from entities.orbs import Orb
from entities.signs import Sign
from entities.player import Player
from entities.checkpoint import Checkpoint
from entities.boss import Boss
from language_manager import LANG

class Level:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group() #initialise sprites
        self.platforms = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.teleporters = pygame.sprite.Group()
        self.orbs = pygame.sprite.Group()
        self.signs = pygame.sprite.Group()
        self.player = None
        self.checkpoints = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        self.active_checkpoint = None

class LevelLoader: #load levels from file
    @staticmethod
    def load(level_num: int) -> Level:
        level = Level()
        platform_data = []
        other_data = []

        try:
            with open(f'levels/level{level_num}.txt', 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if not parts:
                        continue
                    if parts[0] == 'platform':
                        platform_data.append(parts)
                    else:
                        other_data.append(parts)

            # Najpierw platformy
            for parts in platform_data:
                x = int(parts[1]) * 30 + 400
                y = -int(parts[2]) * 30 + 300
                platform = Platform(x, y)
                level.platforms.add(platform)
                level.all_sprites.add(platform)

            # Potem reszta
            for parts in other_data:
                obj_type = parts[0]
                x = int(parts[1]) * 30 + 400
                y = -int(parts[2]) * 30 + 300

                if obj_type == 'spike':
                    spike = Spike(x, y, level.platforms)
                    level.spikes.add(spike)
                    level.all_sprites.add(spike)
                elif obj_type == 'teleport':
                    tele = Teleporter(x, y, int(parts[3]))
                    level.teleporters.add(tele)
                    level.all_sprites.add(tele)
                elif obj_type == 'orb':
                    orb = Orb(x, y)
                    level.orbs.add(orb)
                    level.all_sprites.add(orb)
                elif obj_type == 'sign':
                    sign_key = parts[3]
                    message = LANG.strings["signs"].get(sign_key, sign_key)
                    sign = Sign(x, y, message)
                    level.signs.add(sign)
                    level.all_sprites.add(sign)
                elif obj_type == 'checkpoint':
                    checkpoint = Checkpoint(x, y)
                    level.checkpoints.add(checkpoint)
                    level.all_sprites.add(checkpoint)
                elif obj_type == 'boss':
                    boss_speed = float(parts[3]) if len(parts) > 3 else 3.0
                    boss = Boss(x, y, boss_speed)
                    level.bosses.add(boss)
                    level.all_sprites.add(boss)

        except FileNotFoundError:
            print(f"Level {level_num} not found!")
            return LevelLoader.load(1)

        level.player = Player(400, 300, level_num)
        level.all_sprites.add(level.player)
        return level
