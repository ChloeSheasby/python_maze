import pygame
from config import *


class Coin(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = pygame.image.load(image)

        # Scale the image to the desired size
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))

        self.rect = self.image.get_rect()
        self.set_position(x, y)

    def set_position(self, x, y):
        self.rect.topleft = (x * GRID_SIZE, y * GRID_SIZE)

