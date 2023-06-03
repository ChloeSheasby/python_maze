import heapq
import random

import networkx as nx
import pygame
from clingo_additions.clingo_fire_generation import *
from clingo_additions.clingo_wall_coloring import *
from config import *
from models.fire import Fire
from models.player import Player
from models.treasure import Treasure
from models.wall import Wall

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
        self.player = Player("../assets/Player.png")

        self.player_size = PLAYER_SIZE

        self.player_speed = PLAYER_SPEED

        # Ending point
        self.treasure = Treasure("../assets/Treasure.png")

        # Define the game loop
        self.running = True
    
    def check_collision(self, rect1, rect2):
        return rect1.colliderect(rect2)

    def handle_events(self):
        if self.player.rect.colliderect(self.treasure.rect):
            print("Congratulations! You've won!")
            self.running = False
        # Check for collisions between the player and fires
        if pygame.sprite.spritecollide(self.player, self.maze_fires, False):
            # Handle character death
            print("Oh no! You died.")
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

    def recursive_division(self, grid, x, y, width, height, horizontal_split=None):
        if width < 2 or height < 2:
            return

        if horizontal_split is None:
            horizontal_split = random.choice([True, False]) if width != height else (True if width > height else False)
        else:
            horizontal_split = not horizontal_split

        wall_probability = 1

        if horizontal_split:
            hx = x + random.randint(0, width - 2)
            passage_y = random.randint(y, y + height - 1)

            for hy in range(y, y + height):
                if hy != passage_y:  # Create a guaranteed passage through the walls
                    grid[hy][hx] |= E
                    grid[hy][hx + 1] |= W

            self.recursive_division(grid, x, y, hx - x + 1, height, horizontal_split)
            self.recursive_division(grid, hx + 1, y, width - (hx - x + 1), height, horizontal_split)
        else:
            hy = y + random.randint(0, height - 2)
            passage_x = random.randint(x, x + width - 1)

            for hx in range(x, x + width):
                if hx != passage_x:  # Create a guaranteed passage through the walls
                    grid[hy][hx] |= S
                    grid[hy + 1][hx] |= N

            self.recursive_division(grid, x, y, width, hy - y + 1, horizontal_split)
            self.recursive_division(grid, x, hy + 1, width, height - (hy - y + 1), horizontal_split)


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
        
    import random

    def generate_maze_backtracker(self, grid_width, grid_height):
        # Initialize the grid and visited cells
        grid = [[0 for _ in range(grid_height)] for _ in range(grid_width)]
        visited = set()

        def get_adjacent_cells(x, y):
            adjacent_cells = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            return adjacent_cells

        def visit_cell(x, y):
            grid[x][y] = 1
            visited.add((x, y))

        # Start at a random cell
        start_x, start_y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
        visit_cell(start_x, start_y)

        # Initialize the stack with the adjacent cells
        stack = []
        for nx, ny in get_adjacent_cells(start_x, start_y):
            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                stack.append((start_x, start_y, nx, ny))

        while stack:
            # Select a random cell from the stack
            cx, cy, nx, ny = stack.pop(random.randint(0, len(stack) - 1))

            # If the new cell is not visited, connect it to the current cell and mark it as visited
            if (nx, ny) not in visited:
                grid[(cx + nx) // 2][(cy + ny) // 2] = 1
                visit_cell(nx, ny)

                # Add the adjacent cells to the stack
                for nnx, nny in get_adjacent_cells(nx, ny):
                    if 0 <= nnx < grid_width and 0 <= nny < grid_height and (nnx, nny) not in visited:
                        stack.append((nx, ny, nnx, nny))

        # Select a random start and end point
        start_x, start_y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
        end_x, end_y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)

        return grid, (start_x, start_y), (end_x, end_y)


    def generate_maze_prim(self, grid_width, grid_height, start_x, start_y):
        random.seed()

        # Initialize the grid, edges, and visited cells
        grid = [[0 for _ in range(grid_height)] for _ in range(grid_width)]
        edges = [[0 for _ in range(grid_height)] for _ in range(grid_width)]
        visited = set()

        def get_adjacent_cells(x, y):
            adjacent_cells = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            return adjacent_cells

        def visit_cell(x, y):
            grid[x][y] = 1
            visited.add((x, y))

        # Start at the given position
        visit_cell(start_x - 1, start_y - 1)

        # Initialize the frontier with all the adjacent cells
        frontier = []
        for nx, ny in get_adjacent_cells(start_x - 1, start_y - 1):
            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                frontier.append((nx, ny))

        while frontier:
            # Select a random cell from the frontier
            x, y = random.choice(frontier)

            # Get the adjacent cells
            adjacent_cells = get_adjacent_cells(x, y)

            # Choose a random adjacent cell that is visited and has not already been connected
            random.shuffle(adjacent_cells)
            connected_cells = []
            for nx, ny in adjacent_cells:
                if (nx, ny) in visited and not edges[nx][ny]:
                    connected_cells.append((nx, ny))
            if connected_cells:
                nx, ny = random.choice(connected_cells)
                # Connect the current cell to the selected cell
                edges[x][y] = 1
                edges[nx][ny] = 1
                visit_cell(x, y)
                frontier.append((x, y))
                for nnx, nny in get_adjacent_cells(nx, ny):
                    if 0 <= nnx < grid_width and 0 <= nny < grid_height and (nnx, nny) not in visited:
                        frontier.append((nnx, nny))
            else:
                # If no adjacent cells are visited or connected, remove the current cell from the frontier
                frontier.remove((x, y))

        return grid, edges
    
    def dijkstra_path(self, graph, start, end):
        # Check that the start and end nodes are in the graph
        if start not in graph or end not in graph:
            raise ValueError("Start or end node not in graph")
    
        # Initialize the distances and previous nodes
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        previous = {node: None for node in graph}

        # Initialize the queue with the start node
        queue = [start]

        while queue:
            # Get the node with the smallest distance from the start
            current = min(queue, key=distances.get)

            # Stop if the end node is reached
            if current == end:
                break

            # Remove the current node from the queue
            queue.remove(current)

            # Update the distances and previous nodes for the neighbors of the current node
            for neighbor in graph[current]:
                distance = distances[current] + 1  # assume unit cost
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    if neighbor not in queue:
                        queue.append(neighbor)

        # Reconstruct the path from the end to the start
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        return path

    def generate_maze(self):
        grid_width = WIDTH // GRID_SIZE
        grid_height = HEIGHT // GRID_SIZE

        grid, (start_x, start_y), (end_x, end_y) = self.generate_maze_backtracker(grid_width, grid_height)

        # Generate the maze grid and edges
        # grid, edges = self.generate_maze_prim(grid_width, grid_height, 1, 1)

        print(grid)

        # Find a path from the starting cell to the ending cell
        # graph = self.create_graph_from_grid(grid)
        # self.path = self.dijkstra_path(graph, (0, 0), (grid_width - 1, grid_height - 1))

        self.path = self.a_star(grid, (start_x, start_y), (end_x, end_y))

        maze_walls = pygame.sprite.Group()  # Create a sprite group for the walls
        maze_fires = pygame.sprite.Group()  # Create a sprite group for the fires
        clingo_walls_fires = ""
        clingo_walls_colors = ""
        # start_x, start_y = 1, 1
        # end_x, end_y = grid_width - 2, grid_height - 2 # Change the end point to avoid the wall

        for y in range(grid_height):
            for x in range(grid_width):
                if x == start_x and y == start_y:
                    continue
                if x == end_x and y == end_y:
                    continue
                if (x, y) in self.path:
                    continue
                if grid[y][x] == 1:
                    clingo_walls_fires += f"wall({x}, {y}). "
                    clingo_walls_colors += f"wall({x}, {y}). "

        # Get fire positions using the clingo_walls
        print("Getting fire positions...")
        fire_positions = get_fire_positions(clingo_walls_fires)
        print("Fire positions obtained.")

        # Get wall colors using the clingo_walls
        print("Getting wall colors...")
        wall_colors = get_wall_colors(clingo_walls_colors)
        print("Wall colors obtained.")

        # Create wall instances and add them to maze_walls sprite group
        for (x, y), color in wall_colors.items(): 
            wall = Wall(x * GRID_SIZE, y * GRID_SIZE, color)
            maze_walls.add(wall)

        # Create fire instances and add them to maze_fires sprite group
        for x, y in fire_positions:
            fire = Fire('../assets/Fire.png', x, y)
            maze_fires.add(fire)

        self.maze_walls = maze_walls
        self.maze_fires = maze_fires

    def draw(self):
        # Keep the player within the screen
        PLAYER_POS[0] = max(0, min(WIDTH - self.player_size, PLAYER_POS[0]))
        PLAYER_POS[1] = max(0, min(HEIGHT - self.player_size, PLAYER_POS[1]))

        # Clear the screen
        self.screen.fill((0, 0, 0))

        # Draw maze walls
        for wall in self.maze_walls:
            self.screen.blit(wall.image, wall.rect)

        # Draw maze fires
        for fire in self.maze_fires:
            self.screen.blit(fire.image, fire.rect)

        # Draw player
        self.screen.blit(self.player.image, self.player.rect)

        # Draw treasure
        self.screen.blit(self.treasure.image, self.treasure.rect)
 
        # Update display
        pygame.display.flip()

    def run(self):
         # Generate the maze
        self.generate_maze()

        while self.running:
            self.handle_events()
            if AUTOMATE_PLAYER:
                self.player.move_along_path(self.path)
            self.draw()
            if AUTOMATE_PLAYER:
                pygame.time.delay(200) 

        # Quit pygame
        pygame.quit()
