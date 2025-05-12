import pygame

#base sprite class for all game objects
class GameObject(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
