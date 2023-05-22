# Flags for different game plays
AUTOMATE_PLAYER = False
A_STAR = True

# Define the grid size and the window size
WIDTH = 800
HEIGHT = 500
GRID_SIZE = 25

# Define the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Define the agent starting position
PLAYER_POS = [0, 0]
PLAYER_SIZE = 25
PLAYER_SPEED = 25

# Define the goal position
GOAL_POS = (WIDTH-1, HEIGHT-1)

# Define the font
FONT = 'Comic Sans MS'
FONT_SIZE = 50

P = 0b1000

COLOR_MAP = {
    'color1': (0, 0, 205),
    'color2': (173, 216, 230),
    'color3': (65, 105, 225),
    'color4': (30, 144, 255),
    'color5': (70, 130, 180),
    'color6': (100, 149, 237)
}

# Define the directions to help with maze creation
N, S, E, W = 1, 2, 4, 8
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {E: W, W: E, N: S, S: N}