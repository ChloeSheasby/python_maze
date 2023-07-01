import random

from config import *


def generate_maze():
    # create grid of cells
    grid = [[{'top': True, 'right': True, 'bottom': True, 'left': True} for x in range(10)] for y in range(10)]

    # choose starting cell
    current_cell = (random.randint(0, 10 - 1), random.randint(0, 10 - 1))
    grid[current_cell[1]][current_cell[0]]['visited'] = True

    # add walls of starting cell to list of walls
    walls = []
    if current_cell[1] > 0:
        walls.append((current_cell[0], current_cell[1], 'top'))
    if current_cell[0] < 10 - 1:
        walls.append((current_cell[0], current_cell[1], 'right'))
    if current_cell[1] < 10 - 1:
        walls.append((current_cell[0], current_cell[1], 'bottom'))
    if current_cell[0] > 0:
        walls.append((current_cell[0], current_cell[1], 'left'))

    # generate maze using Prim's algorithm
    while walls:
        wall = random.choice(walls)
        walls.remove(wall)
        x, y, direction = wall
        if direction == 'top':
            next_cell = (x, y - 1)
        elif direction == 'right':
            next_cell = (x + 1, y)
        elif direction == 'bottom':
            next_cell = (x, y + 1)
        else:
            next_cell = (x - 1, y)
        if (next_cell[0] >= 0 and next_cell[0] < 10 and next_cell[1] >= 0 and next_cell[1] < 10
            and 'visited' not in grid[next_cell[1]][next_cell[0]]):
            grid[y][x][direction] = False
            grid[next_cell[1]][next_cell[0]][{'top': 'bottom', 'right': 'left', 'bottom': 'top', 'left': 'right'}[direction]] = False
            grid[next_cell[1]][next_cell[0]]['visited'] = True
            if next_cell[1] > 0 and 'visited' not in grid[next_cell[1] - 1][next_cell[0]]:
                walls.append((next_cell[0], next_cell[1] - 1, 'top'))
            if next_cell[0] < 10 - 1 and 'visited' not in grid[next_cell[1]][next_cell[0] + 1]:
                walls.append((next_cell[0], next_cell[1], 'right'))
            if next_cell[1] < 10 - 1 and 'visited' not in grid[next_cell[1] + 1][next_cell[0]]:
                walls.append((next_cell[0], next_cell[1], 'bottom'))
            if next_cell[0] > 0 and 'visited' not in grid[next_cell[1]][next_cell[0] - 1]:
                walls.append((next_cell[0] - 1, next_cell[1], 'left'))

    print(grid)

    return grid

def choose_start_end(maze):
    width = len(maze[0])
    height = len(maze)
    top_row = [(x, 0) for x in range(width)]
    bottom_row = [(x, height - 1) for x in range(width)]
    start = random.choice(top_row)
    end = random.choice(bottom_row)
    return start, end

def breadth_first_search(maze, start, end):
    queue = [(start, [start])]
    visited = set()

    while queue:
        (x, y), path = queue.pop(0)
        if (x, y) == end:
            return path
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy, direction in [(0, -1, 'top'), (1, 0, 'right'), (0, 1, 'bottom'), (-1, 0, 'left')]:
            next_x, next_y = x + dx, y + dy
            if (next_x >= 0 and next_x < len(maze[0]) and next_y >= 0 and next_y < len(maze)
                and not maze[y][x][direction]
                and (next_x, next_y) not in visited):
                queue.append(((next_x, next_y), path + [(next_x, next_y)]))
    
    return None

def find_all_paths(maze, start, end):
    queue = [(start, [start])]
    visited = set()
    paths = []

    while queue:
        (x, y), path = queue.pop(0)
        if (x, y) == end:
            paths.append(path)
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy, direction in [(0, -1, 'top'), (1, 0, 'right'), (0, 1, 'bottom'), (-1, 0, 'left')]:
            next_x, next_y = x + dx, y + dy
            if (next_x >= 0 and next_x < len(maze[0]) and next_y >= 0 and next_y < len(maze)
                and not maze[y][x][direction]
                and (next_x, next_y) not in visited):
                queue.append(((next_x, next_y), path + [(next_x, next_y)]))
    
    return paths


def print_maze(maze, path=[]):
    # print top border
    print("+" + "---+" * len(maze[0]))

    # print rows
    for y, row in enumerate(maze):
        # print left border
        print("|", end="")
        # print cells
        for x, cell in enumerate(row):
            if cell['bottom']:
                print("   ", end="")
            else:
                print("___", end="")
            if cell['right']:
                print("|", end="")
            else:
                print(" ", end="")
            if (x, y) in path:
                print("#", end="")
            else:
                print(" ", end="")
        # print right border
        print("|")

        # print bottom border
        print("+" + "---+" * len(maze[0]))


maze = generate_maze()
start, end = choose_start_end(maze)
paths = find_all_paths(maze, start, end)
print(start, end, paths)
# print_maze(maze, paths)