import heapq
import random
import time

import networkx as nx
import pygame
from clingo_additions.clingo_fire_generation import *
from clingo_additions.clingo_wall_coloring import *
from config import *
from models.obstacle import Obstacle
from models.player import Player
from models.treasure import Treasure
from models.wall import Wall
from settings import SettingsPage
from svc_training import get_random_test_object_prediction, start_training

# Initialize pygame
pygame.init()

# Define the font
font = pygame.font.SysFont(None, FONT_SIZE)

class Game:
    def __init__(self):
        # Set up the screen
        self.screen = pygame.display.set_mode((MAZE_WIDTH, MAZE_HEIGHT + SCORE_HEIGHT))
        pygame.display.set_caption("My Maze")

        settings_page = SettingsPage(self.screen)
        self.values = settings_page.run()

        self.game_state = "settings_menu"

        # Define the agent starting position
        self.player = Player("../assets/player.png")

        self.score = 0

        self.score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))

        self.info_text = font.render("", True, (255, 255, 255))

        # Set up the start button
        self.start_button = font.render("Start Game", True, (255, 255, 255))
        self.start_button_rect = self.start_button.get_rect()
        self.start_button_rect.center = (400, 500)

        self.player_size = PLAYER_SIZE

        self.player_speed = PLAYER_SPEED

        # Ending point
        self.treasure = Treasure("../assets/treasure.png")

        # Define the game loop
        self.running = True
    
    def check_collision(self, rect1, rect2):
        return rect1.colliderect(rect2)

    def handle_events(self):
        if self.player.rect.colliderect(self.treasure.rect):
            self.info_text = font.render("Congratulations! You've won!", True, (255, 255, 255))
        # Check for collisions between the player and fires
        if pygame.sprite.spritecollide(self.player, self.maze_fires, False):
            # Handle character death
            self.info_text = font.render("Oh no! You died.", True, (255, 255, 255))
        # Check for collisions between the player and coins
        if pygame.sprite.spritecollide(self.player, self.maze_coins, True):
            # Handle coin collection
            self.score += 10
            self.score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        # Check for collisions between the player and flowers
        if pygame.sprite.spritecollide(self.player, self.maze_flowers, True):
            # Pause for a few seconds
            # time.sleep(3)

            # How many points to add or subtract
            points = random.randint(0, 10)
            
            # Predict the class of the selected entry
            correctPrediction = get_random_test_object_prediction(self.model, self.X_test, self.y_test)

            # Compare the predicted class with the actual class
            if correctPrediction:
                self.score += points
            else:
                self.score -= points
            self.score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
            self.info_text = font.render(f'You {"predicted correctly and gained" if correctPrediction else "predicted incorrectly and lost"} {points} points!', True, (255, 255, 255))
        # Check for user input to move the player
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player.rect.y -= self.player_speed if self.player.rect.y - self.player_speed >= 0 else 0
                if pygame.sprite.spritecollide(self.player, self.maze_walls, False):
                    self.player.rect.y += self.player_speed
            if keys[pygame.K_DOWN]:
                self.player.rect.y += self.player_speed if self.player.rect.y + self.player_speed + self.player_size <= MAZE_HEIGHT else 0
                if pygame.sprite.spritecollide(self.player, self.maze_walls, False):
                    self.player.rect.y -= self.player_speed
            if keys[pygame.K_LEFT]:
                self.player.rect.x -= self.player_speed if self.player.rect.x - self.player_speed >= 0 else 0
                if pygame.sprite.spritecollide(self.player, self.maze_walls, False):
                    self.player.rect.x += self.player_speed
            if keys[pygame.K_RIGHT]:
                self.player.rect.x += self.player_speed if self.player.rect.x + self.player_speed + self.player_size <= MAZE_WIDTH else 0
                if pygame.sprite.spritecollide(self.player, self.maze_walls, False):
                    self.player.rect.x -= self.player_speed
            if keys[pygame.K_ESCAPE]:
                self.running = False


    def recursive_division(self, grid, x, y, width, height):
        if width < 2 or height < 2:
            return

        horizontal_split = random.choice([True, False]) if width != height else (True if width > height else False)
        wall_probability = 0.75  # Probability of creating a wall, lowering it reduces the number of walls

        if horizontal_split:
            hx = x + random.randint(0, width - 2)
            for hy in range(y, y + height):
                if hy != y and (hy != y + height - 1 or grid[hy][hx] & (S | N)) and random.random() < wall_probability:
                    grid[hy][hx] |= E
                    grid[hy][hx + 1] |= W

            divide_point = y + random.randint(1, height - 1)
            grid[divide_point][hx] &= ~E
            grid[divide_point][hx + 1] &= ~W

            self.recursive_division(grid, x, y, hx - x + 1, height)
            self.recursive_division(grid, hx + 1, y, width - (hx - x + 1), height)
        else:
            hy = y + random.randint(0, height - 2)
            for hx in range(x, x + width):
                if hx != x and (hx != x + width - 1 or grid[hy][hx] & (E | W)) and random.random() < wall_probability:
                    grid[hy][hx] |= S
                    grid[hy + 1][hx] |= N

            divide_point = x + random.randint(1, width - 1)
            grid[hy][divide_point] &= ~S
            grid[hy + 1][divide_point] &= ~N

            self.recursive_division(grid, x, y, width, hy - y + 1)
            self.recursive_division(grid, x, hy + 1, width, height - (hy - y + 1))

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, grid, start, end):
        neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = dict()
        g_score = {node: float('inf') for x in range(len(grid[0])) for y in range(len(grid)) for node in [(x, y)]}
        g_score[start] = 0
        f_score = {node: float('inf') for x in range(len(grid[0])) for y in range(len(grid)) for node in [(x, y)]}
        f_score[start] = self.heuristic(start, end)

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < len(grid[0]) and 0 <= neighbor[1] < len(grid):
                    if grid[neighbor[1]][neighbor[0]] & (E | S):
                        continue
                    tentative_g_score = g_score[current] + 1
                    if tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, end)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []
    
    def create_graph_from_grid(self, grid):
        graph = nx.Graph()
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if not (cell & (E | S)):
                    for dx, dy in [(0, 1), (1, 0)]:
                        if 0 <= x + dx < len(row) and 0 <= y + dy < len(grid) and not (grid[y + dy][x + dx] & (E | S)):
                            graph.add_edge((x, y), (x + dx, y + dy))
        return graph

    def dfs_path(self, graph, start):
        try:
            path = nx.dfs_preorder_nodes(graph, source=start)
            return list(path)
        except:
            return []

    def generate_maze(self):
        grid_width = MAZE_WIDTH // GRID_SIZE
        grid_height = MAZE_HEIGHT // GRID_SIZE
        grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        self.recursive_division(grid, 0, 0, grid_width, grid_height)

        maze_walls = pygame.sprite.Group()  # Create a sprite group for the walls
        maze_fires = pygame.sprite.Group()  # Create a sprite group for the fires
        maze_coins = pygame.sprite.Group()  # Create a sprite group for the coins
        maze_flowers = pygame.sprite.Group()  # Create a sprite group for the flowers
        clingo_walls_fires = ""
        clingo_walls_colors = ""
        start_x, start_y = 1, 1
        end_x, end_y = grid_width - 2, grid_height - 2 # Change the end point to avoid the wall

        print(self.values["Algorithm"])

        # Find a path between the starting point and the ending point
        if not self.values["Algorithm"]:
            self.path = self.a_star(grid, (start_x, start_y), (end_x, end_y))
        else:
            graph = self.create_graph_from_grid(grid)
            self.path = self.dfs_path(graph, (start_x, start_y), (end_x, end_y))

        for y in range(grid_height):
            for x in range(grid_width):
                if x == start_x and y == start_y:
                    continue
                if x == end_x and y == end_y:
                    continue
                if (x, y) in self.path:
                    continue
                if grid[y][x] & E:
                    # wall = Wall(x * GRID_SIZE, y * GRID_SIZE)
                    # maze_walls.add(wall)
                    clingo_walls_fires += f"wall({x}, {y}). "
                    clingo_walls_colors += f"wall({x}, {y}). "
                if grid[y][x] & S:
                    # wall = Wall(x * GRID_SIZE, y * GRID_SIZE)
                    # maze_walls.add(wall)
                    clingo_walls_fires += f"wall({x}, {y}). "
                    clingo_walls_colors += f"wall({x}, {y}). "

        # Get fire positions using the clingo_walls
        fire_positions = get_fire_positions(clingo_walls_fires)

        # Get wall colors using the clingo_walls
        wall_colors = get_wall_colors(clingo_walls_colors)

        # Create wall instances and add them to maze_walls sprite group
        for (x, y), color in wall_colors.items(): 
            wall = Wall(x * GRID_SIZE, y * GRID_SIZE, color)
            maze_walls.add(wall)

        # Create fire instances and add them to maze_fires sprite group
        for x, y in fire_positions:
            fire = Obstacle('../assets/fire.png', x, y)
            maze_fires.add(fire)
                
        for x, y in self.path:
            # Choose a random direction to place the coin
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            coin_x, coin_y = x, y
            # Move the coin 1 or 2 spaces in the chosen direction
            for i in range(random.randint(1, 2)):
                coin_x += dx
                coin_y += dy
                if (coin_x + 2, coin_y + 2) not in fire_positions and (coin_x + 2, coin_y + 2) in self.path:
                    prob_coin = 0.65
                else:
                    prob_coin = 0.02
                prob_flower = 0.1
                # Add a coin with the computed probability
                if random.random() < prob_coin:
                    coin = Obstacle('../assets/coin.png', coin_x, coin_y)
                    maze_coins.add(coin)  

                # Add a flower with the computed probability
                if random.random() < prob_flower:
                    flower = Obstacle('../assets/flower.png', x, y)
                    maze_flowers.add(flower)   

        self.maze_walls = maze_walls
        self.maze_fires = maze_fires
        self.maze_coins = maze_coins  
        self.maze_flowers = maze_flowers 

    def draw(self):
        # Keep the player within the screen
        PLAYER_POS[0] = max(0, min(MAZE_WIDTH - self.player_size, PLAYER_POS[0]))
        PLAYER_POS[1] = max(0, min(MAZE_HEIGHT - self.player_size, PLAYER_POS[1]))

        # Clear the screen
        self.screen.fill((0, 0, 0))
       
        # Draw score
        score_rect = self.score_text.get_rect(topright=(MAZE_WIDTH - 10, 10))
        self.screen.blit(self.score_text, score_rect)

        # Draw info
        info_rect = self.info_text.get_rect(topleft=(10, 10))
        self.screen.blit(self.info_text, info_rect)


        # Draw maze walls
        for wall in self.maze_walls:
            self.screen.blit(wall.image, wall.rect.move(0, SCORE_HEIGHT))

        # Draw maze fires
        for fire in self.maze_fires:
            self.screen.blit(fire.image, fire.rect.move(0, SCORE_HEIGHT))

        # Draw maze coins
        for coin in self.maze_coins:
            self.screen.blit(coin.image, coin.rect.move(0, SCORE_HEIGHT))

        # Draw maze flowers
        for flower in self.maze_flowers:
            self.screen.blit(flower.image, flower.rect.move(0, SCORE_HEIGHT))

        # Draw player
        self.screen.blit(self.player.image, self.player.rect.move(0, SCORE_HEIGHT))

        # Draw treasure
        self.screen.blit(self.treasure.image, self.treasure.rect.move(0, SCORE_HEIGHT))

        # Update display
        pygame.display.flip()


    def run(self):
        # Train on data
        self.model, self.X_test, self.y_test = start_training()
        # Generate the maze
        self.generate_maze()
        while self.running:
            self.handle_events()
            if self.values["Auto-play"]:
                self.player.move_along_path(self.path)
            self.draw()
            if self.values["Auto-play"]:
                pygame.time.delay(200) 
    
        # Quit pygame
        pygame.quit()