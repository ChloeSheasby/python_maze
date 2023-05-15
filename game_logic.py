from player import Player
from treasure import Treasure
import pygame
import random
from config import *
from wall import Wall
import heapq
import networkx as nx

# Initialize pygame
pygame.init()


# Define the font
font = pygame.font.SysFont(FONT, FONT_SIZE)

class Game:
    def __init__(self):
        # Set up the screen
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("My Maze")

        # Define the agent starting position
        player_image_path = "./assets/Player.png"
        self.player = Player(player_image_path)

        self.player_size = PLAYER_SIZE

        self.player_speed = PLAYER_SPEED

        # Ending point
        treasure_image_path = "./assets/Treasure.png"
        self.treasure = Treasure(treasure_image_path)

        # Define the game loop
        self.running = True
    
    def check_collision(self, rect1, rect2):
        return rect1.colliderect(rect2)

    def handle_events(self):
        if self.player.rect.colliderect(self.treasure.rect):
            print("Congratulations! You've won!")
            self.running = False

        # Check for user input to move the player
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player.rect.y -= self.player_speed if self.player.rect.y - self.player_speed >= 0 else 0
                if pygame.sprite.spritecollide(self.player, self.maze_walls, False):
                    print("collision moving up")
                    self.player.rect.y += self.player_speed
            if keys[pygame.K_DOWN]:
                self.player.rect.y += self.player_speed if self.player.rect.y + self.player_speed + self.player_size <= HEIGHT else 0
                if pygame.sprite.spritecollide(self.player, self.maze_walls, False):
                    print("collision moving down")
                    self.player.rect.y -= self.player_speed
            if keys[pygame.K_LEFT]:
                self.player.rect.x -= self.player_speed if self.player.rect.x - self.player_speed >= 0 else 0
                if pygame.sprite.spritecollide(self.player, self.maze_walls, False):
                    print("collision moving left")
                    self.player.rect.x += self.player_speed
            if keys[pygame.K_RIGHT]:
                self.player.rect.x += self.player_speed if self.player.rect.x + self.player_speed + self.player_size <= WIDTH else 0
                if pygame.sprite.spritecollide(self.player, self.maze_walls, False):
                    print("collision moving right")
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

    def dfs_path(self, graph, start, end):
        try:
            path = nx.dfs_preorder_nodes(graph, source=start)
            return list(path)
        except:
            return []

    def generate_maze(self):
        grid_width = WIDTH // GRID_SIZE
        grid_height = HEIGHT // GRID_SIZE
        grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        self.recursive_division(grid, 0, 0, grid_width, grid_height)

        maze_walls = pygame.sprite.Group()  # Create a sprite group for the walls
        start_x, start_y = 1, 1
        end_x, end_y = grid_width - 2, grid_height - 2  # Change the end point to avoid the wall

        # Find a path between the starting point and the ending point
        self.path = self.a_star(grid, (start_x, start_y), (end_x, end_y))
        # graph = self.create_graph_from_grid(grid)
        # self.path = self.dfs_path(graph, (start_x, start_y), (end_x, end_y))

        for y in range(grid_height):
            for x in range(grid_width):
                if x == start_x and y == start_y:
                    continue
                if x == end_x and y == end_y:
                    continue
                if (x, y) in self.path:
                    continue
                if grid[y][x] & E:
                    wall = Wall(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    maze_walls.add(wall)
                if grid[y][x] & S:
                    wall = Wall(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    maze_walls.add(wall)

        return maze_walls


    def draw(self):
        # Keep the player within the screen
        PLAYER_POS[0] = max(0, min(WIDTH - self.player_size, PLAYER_POS[0]))
        PLAYER_POS[1] = max(0, min(HEIGHT - self.player_size, PLAYER_POS[1]))

        # Clear the screen
        self.screen.fill((0, 0, 0))

        # Draw maze walls
        for wall in self.maze_walls:
            pygame.draw.rect(self.screen, (0, 0, 255), wall)

        # Draw player
        self.screen.blit(self.player.image, self.player.rect)

        # Draw treasure
        self.screen.blit(self.treasure.image, self.treasure.rect)
 
        # Update display
        pygame.display.flip()

    def run(self):
         # Generate the maze
        self.maze_walls = self.generate_maze()

        while self.running:
            self.handle_events()
            self.player.move_along_path(self.path)
            self.draw()
            pygame.time.delay(200) 

        # Quit pygame
        pygame.quit()
