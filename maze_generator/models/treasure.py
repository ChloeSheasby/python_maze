import pygame
from config import *


class Treasure(pygame.sprite.Sprite):
    def __init__(self, image, grid_x=(MAZE_WIDTH // GRID_SIZE) - 2, grid_y=(MAZE_HEIGHT // GRID_SIZE) - 2):
        super().__init__()
        self.image = pygame.image.load(image)

        # Scale the image to the desired size
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))

        self.rect = self.image.get_rect()
        self.set_position(grid_x, grid_y)

    def set_position(self, grid_x, grid_y):
        self.rect.topleft = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)

    def colliding(self, things):
        if self.rect.collidelist(things) != -1:
            return True
        return False
