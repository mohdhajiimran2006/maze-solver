"""
maze.py - Maze Model and Stack-Based Generator
----------------------------------------------
Provides grid representation, cell classification, and procedural maze
generation using the Randomized Depth-First Search algorithm powered by
the custom Stack data structure.
"""

import random
from typing import List, Set, Tuple, Optional
from stack import Stack


class CellType:
    WALL = 1
    PATH = 0
    START = 2
    EXIT = 3
    COIN = 4


class Maze:
    """
    Represents a 2D tile-based Maze grid with support for walls, paths,
    collectibles, start/exit points, and procedural generation.
    """

    def __init__(self, rows: int = 21, cols: int = 21) -> None:
        # Maze dimensions should ideally be odd for DFS wall carving
        self.rows: int = rows if rows % 2 != 0 else rows + 1
        self.cols: int = cols if cols % 2 != 0 else cols + 1
        
        # 2D Grid: 1 = Wall, 0 = Open Path
        self.grid: List[List[int]] = [[CellType.WALL for _ in range(self.cols)] for _ in range(self.rows)]
        
        self.start: Tuple[int, int] = (1, 1)
        self.exit: Tuple[int, int] = (self.rows - 2, self.cols - 2)
        self.coins: Set[Tuple[int, int]] = set()

    def is_valid(self, r: int, c: int) -> bool:
        """Check if row and column coordinates are within bounds."""
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, r: int, c: int) -> bool:
        """Check if a coordinate can be traversed (not a wall)."""
        return self.is_valid(r, c) and self.grid[r][c] != CellType.WALL

    def get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Return cardinal walkable neighboring coordinates (Up, Right, Down, Left)."""
        neighbors = []
        for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            nr, nc = r + dr, c + dc
            if self.is_walkable(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

    def generate_dfs(self, seed: Optional[int] = None, braid_factor: float = 0.05, num_coins: int = 5) -> "Maze":
        """
        Generate a maze using the classic Randomized DFS algorithm
        implemented with our custom Stack data structure (LIFO backtracking).
        
        Args:
            seed: Random seed for reproducible generation.
            braid_factor: Chance [0.0 - 1.0] of removing dead-end walls to create loops.
            num_coins: Number of collectible coins/gems to scatter on valid paths.
        """
        if seed is not None:
            random.seed(seed)

        # 1. Reset entire grid to solid walls
        self.grid = [[CellType.WALL for _ in range(self.cols)] for _ in range(self.rows)]
        self.coins.clear()

        # 2. Initialize Stack with start coordinate
        start_cell = (1, 1)
        self.grid[start_cell[0]][start_cell[1]] = CellType.PATH
        
        generation_stack: Stack[Tuple[int, int]] = Stack()
        generation_stack.push(start_cell)
        
        visited = {start_cell}

        # 3. Iterative DFS Carving using Stack
        while not generation_stack.is_empty():
            curr_r, curr_c = generation_stack.peek()
            
            # Find unvisited neighbors at step distance of 2
            unvisited_neighbors = []
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nr, nc = curr_r + dr, curr_c + dc
                if 1 <= nr < self.rows - 1 and 1 <= nc < self.cols - 1:
                    if (nr, nc) not in visited:
                        unvisited_neighbors.append((nr, nc, dr, dc))

            if unvisited_neighbors:
                # Pick a random unvisited neighbor
                nr, nc, dr, dc = random.choice(unvisited_neighbors)
                
                # Carve the wall between current cell and chosen neighbor
                wall_r, wall_c = curr_r + dr // 2, curr_c + dc // 2
                self.grid[wall_r][wall_c] = CellType.PATH
                self.grid[nr][nc] = CellType.PATH
                
                visited.add((nr, nc))
                generation_stack.push((nr, nc))
            else:
                # Dead-end reached: Pop the stack to backtrack
                generation_stack.pop()

        # 4. Set start and exit coordinates
        self.start = (1, 1)
        self.exit = (self.rows - 2, self.cols - 2)
        self.grid[self.start[0]][self.start[1]] = CellType.PATH
        self.grid[self.exit[0]][self.exit[1]] = CellType.PATH

        # 5. Optional Braiding (remove dead ends to add loops for gaming variety)
        if braid_factor > 0:
            for r in range(1, self.rows - 1):
                for c in range(1, self.cols - 1):
                    if self.grid[r][c] == CellType.PATH:
                        walkable_neighbors = self.get_neighbors(r, c)
                        if len(walkable_neighbors) == 1 and random.random() < braid_factor:
                            # Knock down one adjacent wall
                            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                wr, wc = r + dr, c + dc
                                if 1 <= wr < self.rows - 1 and 1 <= wc < self.cols - 1:
                                    if self.grid[wr][wc] == CellType.WALL:
                                        self.grid[wr][wc] = CellType.PATH
                                        break

        # 6. Scatter collectible coins
        open_cells = [
            (r, c) for r in range(self.rows) for c in range(self.cols)
            if self.grid[r][c] == CellType.PATH and (r, c) not in (self.start, self.exit)
        ]
        if open_cells:
            sample_count = min(num_coins, len(open_cells))
            self.coins = set(random.sample(open_cells, sample_count))

        return self

    def load_preset(self, preset_name: str = "classic") -> "Maze":
        """Load a predefined handcrafted maze."""
        presets = {
            "mini": [
                [1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1, 0, 1],
                [1, 1, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 1, 1, 0, 1],
                [1, 0, 0, 0, 1, 0, 1],
                [1, 1, 1, 1, 1, 1, 1],
            ],
            "classic": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1],
                [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
                [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ],
        }
        grid = presets.get(preset_name, presets["classic"])
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.grid = [row[:] for row in grid]
        self.start = (1, 1)
        self.exit = (self.rows - 2, self.cols - 2)
        self.coins = {(3, 5), (5, 1), (7, 3)} if preset_name == "classic" else {(3, 3)}
        return self

    def __str__(self) -> str:
        chars = {CellType.WALL: "█", CellType.PATH: " "}
        output = []
        for r in range(self.rows):
            row_str = ""
            for c in range(self.cols):
                if (r, c) == self.start:
                    row_str += "S"
                elif (r, c) == self.exit:
                    row_str += "E"
                elif (r, c) in self.coins:
                    row_str += "o"
                else:
                    row_str += chars.get(self.grid[r][c], "?")
            output.append(row_str)
        return "\n".join(output)
