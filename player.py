import pygame
import random
from config import *

class Player(pygame.sprite.Sprite):
    def __init__(self, image, grid_x=1, grid_y=1):
        super().__init__()
        # if x == 0 and y == 0:
        #     x = random.randint(0, WIDTH - PLAYER_SIZE)
        #     y = random.randint(0, HEIGHT - PLAYER_SIZE)
        self.image = pygame.image.load(image)

        # Scale the image to the desired size
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))

        self.rect = self.image.get_rect()
        self.set_position(grid_x, grid_y)
        self.path_index = 0

    def set_position(self, grid_x, grid_y):
        self.rect.topleft = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)

    def move_along_path(self, path):
        if self.path_index < len(path):
            next_position = path[self.path_index]
            self.set_position(next_position[0], next_position[1])
            self.path_index += 1

    def colliding(self, things):
        if self.rect.collidelist(things) != -1:
            return True
        return False
