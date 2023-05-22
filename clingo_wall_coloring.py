import clingo
from config import *

colored_walls = {}

def on_model(model):
    for atom in model.symbols(atoms=True):
        if atom.name == "colored_wall":
            x, y, color = atom.arguments
            colored_walls[(x.number, y.number)] = str(color)


def get_wall_colors(clingo_walls_colors):
    ctl = clingo.Control()

    ctl.add("base", [], f"""
    % Define maze walls as facts
    {clingo_walls_colors}

    % Define colors as facts
    color(color1). color(color2). color(color3). color(color4). color(color5). color(color6).

    % Each wall should have exactly one color assigned
    1 {{colored_wall(WallX, WallY, Color) : color(Color)}} 1 :- wall(WallX, WallY).

    % Adjacency constraint
    :- colored_wall(X, Y, C), colored_wall(X+1, Y, C).
    :- colored_wall(X, Y, C), colored_wall(X, Y+1, C).
    :- colored_wall(X+1, Y, C), colored_wall(X+1, Y+1, C).
    :- colored_wall(X, Y+1, C), colored_wall(X+1, Y+1, C).
    """)

    ctl.ground([("base", [])])
    ctl.configuration.solve.models = 0

    # Solve the program and get the colored walls
    with ctl.solve(yield_=True) as handle:
        result = handle.get()  # Get the result of the solve function
        if result.satisfiable:
            for model in handle:
                on_model(model)
                break
        else:
            print("No model found")

    return colored_walls
