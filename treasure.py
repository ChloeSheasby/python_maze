import pygame
import random
from config import *

class Treasure(pygame.sprite.Sprite):
    def __init__(self, image, grid_x=(WIDTH // GRID_SIZE) - 1, grid_y=(HEIGHT // GRID_SIZE) - 1):
        super().__init__()
        # if x == 0 and y == 0:
        #     x = random.randint(0, WIDTH - PLAYER_SIZE)
        #     y = random.randint(0, HEIGHT - PLAYER_SIZE)
        self.image = pygame.image.load(image)

        # Scale the image to the desired size
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))

        self.rect = self.image.get_rect()
        self.set_position(grid_x, grid_y)

    def set_position(self, grid_x, grid_y):
        self.rect.bottomright = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)

    def colliding(self, things):
        if self.rect.collidelist(things) != -1:
            return True
        return False
