import pygame
from constants import WIDTH, HEIGHT
from entities.platforms import Platform
from entities.spikes import Spike
from entities.teleporters import Teleporter
from entities.orbs import Orb
from entities.signs import Sign
from entities.player import Player

class Level:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group() #initialise sprites
        self.platforms = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.teleporters = pygame.sprite.Group()
        self.orbs = pygame.sprite.Group()
        self.signs = pygame.sprite.Group()
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
                        tele = Teleporter(x, y, int(parts[3]))
                        level.teleporters.add(tele)
                        level.all_sprites.add(tele)
                    elif obj_type == 'orb':
                        orb = Orb(x, y)
                        level.orbs.add(orb)
                        level.all_sprites.add(orb)
                    elif obj_type == 'sign':
                        message = ','.join(parts[3:])
                        sign = Sign(x, y, message)
                        level.signs.add(sign)
                        level.all_sprites.add(sign)
        except FileNotFoundError:
            print(f"Level {level_num} not found!")
            return LevelLoader.load(1)
        
        level.player = Player(400,300)
        level.all_sprites.add(level.player)
        return level
