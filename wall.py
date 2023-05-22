import pygame
from config import *


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface([GRID_SIZE, GRID_SIZE])
        self.image.fill(COLOR_MAP[color])  # Set the wall color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

