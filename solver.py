"""
solver.py - Stack-Based Maze Solver Algorithm
---------------------------------------------
Implements Iterative Depth-First Search (DFS) with explicit Backtracking
using the custom Stack data structure.

Every state change can either be solved instantly or yielded step-by-step
as a generator to power GUI animations and live DSA stack visualizers.
"""

import time
from typing import Dict, Generator, List, NamedTuple, Optional, Set, Tuple
from stack import Stack
from maze import Maze


class SolverStep(NamedTuple):
    action: str  # 'START', 'VISIT', 'BACKTRACK', 'SUCCESS', 'NO_SOLUTION'
    current_cell: Optional[Tuple[int, int]]
    stack_snapshot: List[Tuple[int, int]]
    visited_count: int
    backtrack_count: int
    message: str


class MazeSolver:
    """
    Solves a Maze using explicit Stack-based DFS Backtracking.
    
    Principles of Stack in Maze Solving:
    1. Active Path: The elements in the stack represent the unbroken path
       from the Start position to the current exploration head.
    2. Decision Choice: Moving to an unvisited neighbor PUSHES that cell to the Stack.
    3. Backtracking: When hitting a dead-end (no unvisited neighbors), the algorithm
       POPS the current cell from the Stack, retreating to the previous junction.
    4. Path Reconstruction: Upon reaching the Exit, the stack contents naturally
       contain the exact solution path without requiring reverse-pointer lookups!
    """

    def __init__(self, maze: Maze) -> None:
        self.maze: Maze = maze
        self.stack: Stack[Tuple[int, int]] = Stack()
        self.visited: Set[Tuple[int, int]] = set()
        self.dead_ends: Set[Tuple[int, int]] = set()
        self.path: List[Tuple[int, int]] = []
        self.backtrack_count: int = 0
        self.execution_time: float = 0.0

    def reset(self) -> None:
        """Reset solver state."""
        self.stack.clear()
        self.stack.reset_stats()
        self.visited.clear()
        self.dead_ends.clear()
        self.path.clear()
        self.backtrack_count = 0
        self.execution_time = 0.0

    def solve_step_by_step(
        self,
        start: Optional[Tuple[int, int]] = None,
        target: Optional[Tuple[int, int]] = None,
    ) -> Generator[SolverStep, None, Optional[List[Tuple[int, int]]]]:
        """
        Generator yielding each state change of the stack algorithm.
        Enables visual animation, step-by-step debug, and interactive gaming.
        """
        self.reset()
        start_pos = start if start is not None else self.maze.start
        target_pos = target if target is not None else self.maze.exit

        if not self.maze.is_walkable(start_pos[0], start_pos[1]):
            yield SolverStep("NO_SOLUTION", start_pos, [], 0, 0, "Start position is blocked!")
            return None

        # 1. Push start node
        self.stack.push(start_pos)
        self.visited.add(start_pos)
        yield SolverStep(
            "START",
            start_pos,
            self.stack.to_list(),
            len(self.visited),
            self.backtrack_count,
            f"Pushed Start {start_pos} onto Stack.",
        )

        # 2. Main DFS Loop
        while not self.stack.is_empty():
            curr = self.stack.peek()

            # Reached target exit!
            if curr == target_pos:
                self.path = self.stack.to_list()
                yield SolverStep(
                    "SUCCESS",
                    curr,
                    self.path,
                    len(self.visited),
                    self.backtrack_count,
                    f"Target reached at {curr}! Solution path found with {len(self.path)} steps.",
                )
                return self.path

            # Look for an unvisited walkable neighbor
            neighbors = self.maze.get_neighbors(curr[0], curr[1])
            unvisited = [n for n in neighbors if n not in self.visited]

            if unvisited:
                # Prioritize neighbors (prefer directions towards target if tied)
                # Standard DFS: pick first available branch
                next_node = unvisited[0]
                self.visited.add(next_node)
                self.stack.push(next_node)
                yield SolverStep(
                    "VISIT",
                    next_node,
                    self.stack.to_list(),
                    len(self.visited),
                    self.backtrack_count,
                    f"Advanced to {next_node}. PUSH to Stack (Depth: {self.stack.size()}).",
                )
            else:
                # Dead-end hit! Backtrack by popping
                popped = self.stack.pop()
                self.dead_ends.add(popped)
                self.backtrack_count += 1
                curr_top = self.stack.peek() if not self.stack.is_empty() else None
                yield SolverStep(
                    "BACKTRACK",
                    curr_top,
                    self.stack.to_list(),
                    len(self.visited),
                    self.backtrack_count,
                    f"Dead-end at {popped}! POP from Stack, backtracking to {curr_top}.",
                )

        yield SolverStep(
            "NO_SOLUTION",
            None,
            [],
            len(self.visited),
            self.backtrack_count,
            "No valid path exists to the target.",
        )
        return None

    def solve(
        self,
        start: Optional[Tuple[int, int]] = None,
        target: Optional[Tuple[int, int]] = None,
    ) -> Dict:
        """
        Execute the solver synchronously to completion and return
        comprehensive benchmark statistics and path results.
        """
        start_time = time.perf_counter()
        stepper = self.solve_step_by_step(start, target)
        last_step = None
        for step in stepper:
            last_step = step
        self.execution_time = (time.perf_counter() - start_time) * 1000.0  # in ms

        stats = self.stack.get_stats()
        return {
            "solved": bool(self.path),
            "path": self.path,
            "path_length": len(self.path),
            "visited_count": len(self.visited),
            "dead_ends_count": len(self.dead_ends),
            "backtracks": self.backtrack_count,
            "pushes": stats["pushes"],
            "pops": stats["pops"],
            "peak_depth": stats["peak_size"],
            "execution_time_ms": round(self.execution_time, 3),
        }
