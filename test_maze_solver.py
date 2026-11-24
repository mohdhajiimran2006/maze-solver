"""
test_maze_solver.py - Unit Test Suite
-------------------------------------
Validates correctness of:
  - Stack Data Structure (LIFO, peak depth, push/pop metrics, edge cases)
  - Maze Generator (DFS procedural carving, reachability, bounds)
  - Maze Solver (Stack-based DFS backtracking, path continuity, wall collision check)
"""

import unittest
import sys
import os

# Ensure local modules are accessible
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stack import Stack, StackEmptyError
from maze import Maze, CellType
from solver import MazeSolver, SolverStep


class TestStackDataStructure(unittest.TestCase):
    def setUp(self):
        self.stack = Stack[int]()

    def test_lifo_order(self):
        """Verify Last-In, First-Out sequence."""
        self.stack.push(10)
        self.stack.push(20)
        self.stack.push(30)
        self.assertEqual(self.stack.pop(), 30)
        self.assertEqual(self.stack.pop(), 20)
        self.assertEqual(self.stack.pop(), 10)
        self.assertTrue(self.stack.is_empty())

    def test_peek(self):
        """Verify peek does not remove the element."""
        self.stack.push(42)
        self.assertEqual(self.stack.peek(), 42)
        self.assertEqual(self.stack.size(), 1)
        self.assertEqual(self.stack.pop(), 42)

    def test_empty_stack_exceptions(self):
        """Verify pop/peek on empty stack raises StackEmptyError."""
        with self.assertRaises(StackEmptyError):
            self.stack.pop()
        with self.assertRaises(StackEmptyError):
            self.stack.peek()

    def test_peak_depth_telemetry(self):
        """Verify maximum stack depth is accurately recorded."""
        self.assertEqual(self.stack.peak_size, 0)
        self.stack.push(1)
        self.stack.push(2)
        self.stack.push(3)
        self.assertEqual(self.stack.peak_size, 3)
        self.stack.pop()
        self.stack.pop()
        self.stack.push(4)
        self.assertEqual(self.stack.peak_size, 3)
        self.assertEqual(self.stack.size(), 2)

    def test_push_pop_counters(self):
        """Verify operation counters tally accurately."""
        self.stack.push(1)
        self.stack.push(2)
        self.stack.pop()
        self.assertEqual(self.stack.pushes, 2)
        self.assertEqual(self.stack.pops, 1)

    def test_to_list(self):
        """Verify to_list returns bottom-to-top order."""
        self.stack.push('a')
        self.stack.push('b')
        self.stack.push('c')
        self.assertEqual(self.stack.to_list(), ['a', 'b', 'c'])


class TestMazeModel(unittest.TestCase):
    def test_dimensions_odd_adjusted(self):
        """Verify even dimensions are converted to odd for DFS carving."""
        m = Maze(10, 10)
        self.assertEqual(m.rows % 2, 1)
        self.assertEqual(m.cols % 2, 1)

    def test_preset_loading(self):
        """Verify classic preset loads correct grid."""
        m = Maze().load_preset("classic")
        self.assertEqual(m.grid[m.start[0]][m.start[1]], CellType.PATH)
        self.assertEqual(m.grid[m.exit[0]][m.exit[1]], CellType.PATH)
        self.assertTrue(len(m.coins) > 0)

    def test_maze_generation(self):
        """Verify DFS generation creates an open start and exit with valid walls."""
        m = Maze(15, 15).generate_dfs(seed=123)
        self.assertTrue(m.is_walkable(m.start[0], m.start[1]))
        self.assertTrue(m.is_walkable(m.exit[0], m.exit[1]))
        # Perimeter must be solid walls
        for c in range(m.cols):
            self.assertEqual(m.grid[0][c], CellType.WALL)
            self.assertEqual(m.grid[m.rows - 1][c], CellType.WALL)
        for r in range(m.rows):
            self.assertEqual(m.grid[r][0], CellType.WALL)
            self.assertEqual(m.grid[r][m.cols - 1], CellType.WALL)


class TestMazeSolver(unittest.TestCase):
    def test_solve_generated_maze(self):
        """Verify Stack DFS successfully finds a path from start to exit."""
        m = Maze(17, 17).generate_dfs(seed=999)
        solver = MazeSolver(m)
        result = solver.solve()

        self.assertTrue(result["solved"])
        path = result["path"]
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], m.start)
        self.assertEqual(path[-1], m.exit)

        # Verify continuity of the path: each step must be cardinal distance of 1
        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            dist = abs(r1 - r2) + abs(c1 - c2)
            self.assertEqual(dist, 1, f"Discontinuous step between {path[i]} and {path[i+1]}")
            self.assertTrue(m.is_walkable(r1, c1))
            self.assertTrue(m.is_walkable(r2, c2))

    def test_solver_step_by_step_generator(self):
        """Verify generator yields valid SolverStep states."""
        m = Maze(11, 11).generate_dfs(seed=42)
        solver = MazeSolver(m)
        steps = list(solver.solve_step_by_step())

        self.assertGreater(len(steps), 0)
        self.assertEqual(steps[0].action, "START")
        self.assertEqual(steps[-1].action, "SUCCESS")

    def test_unsolvable_maze(self):
        """Verify solver correctly handles mazes with no valid path."""
        m = Maze(7, 7)
        # Block the entire grid around start
        m.grid = [[CellType.WALL for _ in range(7)] for _ in range(7)]
        m.grid[1][1] = CellType.PATH  # Start
        m.grid[5][5] = CellType.PATH  # Exit (isolated)
        m.start = (1, 1)
        m.exit = (5, 5)

        solver = MazeSolver(m)
        result = solver.solve()
        self.assertFalse(result["solved"])
        self.assertEqual(len(result["path"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
