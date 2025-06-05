import pygame
import math
from entities.game_object import GameObject
from constants import COLORS

class Boss(GameObject):
    def __init__(self, x: int, y: int, speed: float = 3.0):
        super().__init__(x, y)
        self.image = pygame.Surface((120, 2000))
        self.image.fill(COLORS["RED"])
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.detection_range = 1000 #pixels where boss can detect player
        self.active = False
        
    def update(self, player_rect: pygame.Rect) -> None:
        #activate boss if player is within detection range
        if not self.active:
            distance = math.sqrt((self.rect.centerx - player_rect.centerx)**2 + 
                               (self.rect.centery - player_rect.centery)**2)
            if distance < self.detection_range:
                self.active = True
                self.image.fill(COLORS["DARK_RED"])
            return
        
        #chase player when active
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = max(1, math.sqrt(dx*dx + dy*dy)) #avoid division by zero
        
        #normalize direction and apply speed, move only to the right
        self.rect.x += (dx / distance) * self.speed
