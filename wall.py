import pygame
from config import *

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill((255, 255, 255))  # Set the wall color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

