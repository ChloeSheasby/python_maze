# Python Maze Game
This repository is for a maze game written for the AI Projects course at OC.

## Task 2
### Instructions
1. Implement your own game (or modify the example code).
2. Make the agent follow the generated path to the goal.
3. Implement two more search algorithms for path generation.

### Demo Video

https://github.com/ChloeSheasby/python_maze/assets/47607144/ad255711-81fd-4fa5-8f1d-f98619e59ce3


### Demo Screenshots
- The maze is generated randomly each time the project is run.
<img width="774" alt="Screenshot 2023-05-15 at 6 18 50 PM" src="https://github.com/ChloeSheasby/python_maze/assets/47607144/5280d727-6c96-4163-85a5-2b3d2021dec9">

- The agent can make their way through the maze.
<img width="774" alt="Screenshot 2023-05-15 at 6 19 01 PM" src="https://github.com/ChloeSheasby/python_maze/assets/47607144/f5005e0e-2999-4f96-a473-9c5cb9955d52">
<img width="774" alt="Screenshot 2023-05-15 at 6 19 13 PM" src="https://github.com/ChloeSheasby/python_maze/assets/47607144/93086624-d8f6-40a2-9192-9623520ef033">

- When the agent makes it to the treasure chest, they have won.
<img width="499" alt="Screenshot 2023-05-15 at 6 19 34 PM" src="https://github.com/ChloeSheasby/python_maze/assets/47607144/9d5ed680-f890-4b3f-86c9-16083b25e336">

### Searching Algorithms
#### A* Path Generation

```
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
```

#### DFS Path Generation
- This uses NetworkX's Depth First Search algorithm. 
- The player jumps around the maze with this function since the algorithm is testing the whole path.

```
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
```
