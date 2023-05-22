import clingo
from config import *

fires = []

def on_model(model):
    for atom in model.symbols(shown=True):
        if atom.name == "fire":
            fires.append((atom.arguments[0].number, atom.arguments[1].number))

def get_fire_positions(clingo_walls_fires):
    # Initialize Clingo control
    ctl = clingo.Control()
    width = WIDTH // GRID_SIZE
    height = HEIGHT // GRID_SIZE

    # Load the ASP program
    ctl.add("base", [], f"""
    % Define the dimensions of the maze
    #const width = {width}.
    #const height = {height}.

    % Define the number of fires
    #const num_fires = 20.

    % Define walls
    {clingo_walls_fires}
    
    % Define fires
    {{ fire(X, Y) : X = 1..width, Y = 1..height }} = num_fires.

    % Ensure the start and end positions are not obstacles
    :- fire(1, 1).
    :- fire(width, height).

    % Ensure fires do not render on top of walls
    :- fire(X, Y), wall(X, Y).

    % Ensure no more than 3 fires in the same row
    :- X = 1..width, #count {{ Y : fire(X, Y) }} > 3.

    % Ensure no more than 3 fires in the same column
    :- Y = 1..height, #count {{ X : fire(X, Y) }} > 3.

    % Ensure fires are not right next to each other
    :- fire(X, Y), fire(X+1, Y).
    :- fire(X, Y), fire(X-1, Y).
    :- fire(X, Y), fire(X, Y+1).
    :- fire(X, Y), fire(X, Y-1).
    """)

    # Ground the program
    ctl.ground([("base", [])])

    # Solve the program and get the obstacles
    ctl.solve(on_model=on_model)

    return fires
