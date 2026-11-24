"""
=============================================================================
                                MAZE SOLVER
                     USING STACK DATA STRUCTURE (LIFO)
=============================================================================
Author: MD Haji Imran
Topic:  Maze Traversal and Backtracking using Stack Data Structure (LIFO)
Language: Python 3
=============================================================================
"""


# =============================================================================
# PART 1: CUSTOM STACK DATA STRUCTURE IMPLEMENTATION (LIFO)
# =============================================================================
class Stack:
    """
    A textbook implementation of the Stack Data Structure using the
    Last-In, First-Out (LIFO) principle.
    """

    def __init__(self):
        self.items = []          # Internal array to store elements
        self.push_count = 0      # Total push operations
        self.pop_count = 0       # Total pop (backtrack) operations
        self.peak_size = 0       # Maximum depth reached by the stack

    def push(self, item):
        """
        Push an element onto the top of the stack.
        Time Complexity: O(1)
        """
        self.items.append(item)
        self.push_count += 1
        if len(self.items) > self.peak_size:
            self.peak_size = len(self.items)

    def pop(self):
        """
        Remove and return the top element from the stack.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise IndexError("Pop from empty stack.")
        self.pop_count += 1
        return self.items.pop()

    def peek(self):
        """
        Return the top element without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise IndexError("Peek from empty stack.")
        return self.items[-1]

    def is_empty(self):
        """Return True if the stack has no elements, else False."""
        return len(self.items) == 0

    def size(self):
        """Return the current number of elements in the stack."""
        return len(self.items)

    def to_list(self):
        """Return a copy of the stack elements from bottom to top."""
        return list(self.items)

    def display(self):
        """Display the current contents of the stack."""
        if self.is_empty():
            print("  Stack: [ Empty ]")
        else:
            formatted = " -> ".join(f"({r},{c})" for r, c in self.items)
            print(f"  Stack (Bottom to Top): [ {formatted} ]")


# =============================================================================
# PART 2: MAZE REPRESENTATION & HELPER FUNCTIONS
# =============================================================================
# Grid Convention:
#   0 = Open Path (Walkable)
#   1 = Wall (Blocked / Obstacle)

def print_maze(maze, path=None, start=(0, 0), exit_pos=None):
    """
    Pretty print the maze in the terminal.
    Legend:
      '#' = Wall (1)
      ' ' = Open Path (0)
      'S' = Start Position
      'E' = Exit Position
      '*' = Solution Path
    """
    rows = len(maze)
    cols = len(maze[0])
    path_set = set(path) if path else set()

    print("\n   " + " ".join(f"{c:2d}" for c in range(cols)))
    print("   " + "---" * cols)

    for r in range(rows):
        row_str = f"{r:2d}|"
        for c in range(cols):
            if (r, c) == start:
                row_str += " S "
            elif (r, c) == exit_pos:
                row_str += " E "
            elif (r, c) in path_set:
                row_str += " * "   # Part of the solution path
            elif maze[r][c] == 1:
                row_str += " # "   # Wall
            else:
                row_str += " . "   # Open path
        print(row_str)
    print()


# =============================================================================
# PART 3: STACK-BASED MAZE SOLVER ALGORITHM (DFS WITH BACKTRACKING)
# =============================================================================
def solve_maze(maze, start=(0, 0), exit_pos=None, show_steps=True):
    """
    Solves a 2D maze using Depth-First Search (DFS) with a Stack.
    
    Algorithm Explanation:
      1. Create an empty Stack and push the Start cell: stack.push(start)
      2. Mark Start as visited.
      3. While the Stack is not empty:
         a. Look at the current cell: curr = stack.peek()
         b. If curr == exit, the path is found! Return the Stack items.
         c. Search for an unvisited open neighbor (Up, Down, Left, Right).
         d. If an unvisited neighbor exists:
              - Mark it as visited.
              - stack.push(neighbor)  --> Move forward
         e. If NO unvisited neighbors exist (Dead End):
              - stack.pop()           --> Backtrack to previous cell
      4. If the Stack becomes empty, no path exists from Start to Exit.
    """
    rows = len(maze)
    cols = len(maze[0])

    if exit_pos is None:
        exit_pos = (rows - 1, cols - 1)

    # Validate start and exit positions
    if maze[start[0]][start[1]] == 1:
        print(f"Error: Start position {start} is inside a wall!")
        return None
    if maze[exit_pos[0]][exit_pos[1]] == 1:
        print(f"Error: Exit position {exit_pos} is inside a wall!")
        return None

    # Directions: (row_delta, col_delta, direction_name)
    # Order of exploration: Down, Right, Up, Left
    directions = [
        (1, 0, "DOWN"),
        (0, 1, "RIGHT"),
        (-1, 0, "UP"),
        (0, -1, "LEFT"),
    ]

    # Initialize Stack and Visited tracking
    stack = Stack()
    visited = set()

    # Step 1: Push start cell onto the stack
    stack.push(start)
    visited.add(start)

    step_number = 1
    if show_steps:
        print("=" * 65)
        print("          STEP-BY-STEP STACK TRACE & BACKTRACKING LOG")
        print("=" * 65)
        print(f"Step {step_number:3d}: PUSH Start {start} onto Stack.")
        stack.display()

    # Step 2: Main DFS Loop
    while not stack.is_empty():
        curr_r, curr_c = stack.peek()

        # Check if we reached the exit
        if (curr_r, curr_c) == exit_pos:
            solution_path = stack.to_list()
            if show_steps:
                print("-" * 65)
                print(f" SUCCESS! Exit reached at {exit_pos}!")
                print(f" Solution Path found using {len(solution_path)} steps.")
                print("-" * 65)
            return {
                "solved": True,
                "path": solution_path,
                "stack": stack,
                "visited": visited,
            }

        # Find an unvisited open neighbor
        moved = False
        for dr, dc, dir_name in directions:
            nr, nc = curr_r + dr, curr_c + dc

            # Check bounds and if cell is open and not visited
            if 0 <= nr < rows and 0 <= nc < cols:
                if maze[nr][nc] == 0 and (nr, nc) not in visited:
                    # Found a valid next move: PUSH to stack
                    visited.add((nr, nc))
                    stack.push((nr, nc))
                    step_number += 1
                    moved = True
                    if show_steps:
                        print(f"Step {step_number:3d}: Move {dir_name:5s} -> PUSH ({nr},{nc}) | Stack Depth: {stack.size()}")
                    break

        if not moved:
            # Dead End reached: POP from stack (Backtrack)
            popped_cell = stack.pop()
            step_number += 1
            if show_steps:
                next_top = stack.peek() if not stack.is_empty() else "None"
                print(f"Step {step_number:3d}: [DEAD END] at {popped_cell} -> POP (Backtrack to {next_top})")

    # If stack becomes empty and exit was not reached
    if show_steps:
        print("\n❌ Failed: No valid path exists from Start to Exit!")
    return {
        "solved": False,
        "path": [],
        "stack": stack,
        "visited": visited,
    }


# =============================================================================
# PART 4: SAMPLE MAZES & DEMONSTRATION RUNNER
# =============================================================================
def get_sample_maze():
    """
    Standard academic sample maze (8x8) containing dead-ends to
    explicitly demonstrate both PUSH (exploration) and POP (backtracking):
      0 = Open path
      1 = Wall
    """
    return [
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [1, 1, 0, 1, 1, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0],
    ]


def run_assignment_demo():
    """Execute the assignment demonstration."""
    print("\n" + "=" * 65)
    print("                           MAZE SOLVER")
    print("                Using Stack Data Structure (LIFO)")
    print("=" * 65)

    maze = get_sample_maze()
    start = (0, 0)
    exit_pos = (7, 7)

    print("\n[1] ORIGINAL INPUT MAZE:")
    print("Legend: '#' = Wall, '.' = Open Path, 'S' = Start, 'E' = Exit")
    print_maze(maze, start=start, exit_pos=exit_pos)

    # Solve with complete step-by-step trace
    result = solve_maze(maze, start=start, exit_pos=exit_pos, show_steps=True)

    if result and result["solved"]:
        path = result["path"]
        stack = result["stack"]

        print("\n[2] SOLVED MAZE (PATH MARKED WITH '*'):")
        print_maze(maze, path=path, start=start, exit_pos=exit_pos)

        print("[3] FINAL SOLUTION PATH COORDINATES:")
        path_str = " -> ".join(f"({r},{c})" for r, c in path)
        print(f"  {path_str}")

        print("\n[4] DATA STRUCTURE (STACK) PERFORMANCE METRICS:")
        print(f"  - Total PUSH Operations (Forward steps): {stack.push_count}")
        print(f"  - Total POP Operations (Backtracks):    {stack.pop_count}")
        print(f"  - Peak Stack Size (Max Memory Used):     {stack.peak_size}")
        print(f"  - Solution Path Length:                  {len(path)} cells")
        print(f"  - Total Cells Explored:                  {len(result['visited'])} cells")
    else:
        print("\nNo solution exists for the given maze.")


# =============================================================================
# PART 5: INTERACTIVE MENU (FOR LAB VIVA / SUBMISSION DEMO)
# =============================================================================
def interactive_menu():
    while True:
        print("\n" + "=" * 50)
        print("       MAZE SOLVER USING STACK - MENU")
        print("=" * 50)
        print("1. Run Default Academic Sample Maze (8x8)")
        print("2. Run Custom Small Maze (5x5)")
        print("3. Test Dead-End / Unsolvable Maze")
        print("4. Exit")
        print("=" * 50)
        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            run_assignment_demo()
        elif choice == "2":
            small_maze = [
                [0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0],
                [1, 1, 0, 1, 0],
                [0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0],
            ]
            print("\n--- 5x5 SMALL MAZE ---")
            print_maze(small_maze, start=(0, 0), exit_pos=(4, 4))
            res = solve_maze(small_maze, start=(0, 0), exit_pos=(4, 4), show_steps=True)
            if res["solved"]:
                print_maze(small_maze, path=res["path"], start=(0, 0), exit_pos=(4, 4))
        elif choice == "3":
            blocked_maze = [
                [0, 1, 0],
                [1, 1, 0],
                [0, 0, 0],
            ]
            print("\n--- BLOCKED / UNSOLVABLE MAZE ---")
            print_maze(blocked_maze, start=(0, 0), exit_pos=(2, 2))
            solve_maze(blocked_maze, start=(0, 0), exit_pos=(2, 2), show_steps=True)
        elif choice == "4":
            print("Exiting program. Best of luck with your assignment!")
            break
        else:
            print("Invalid choice, please select 1, 2, 3, or 4.")


if __name__ == "__main__":
    # If run directly from terminal without arguments, execute the demo!
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--menu":
        interactive_menu()
    else:
        run_assignment_demo()
