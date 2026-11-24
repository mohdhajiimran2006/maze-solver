# Maze Solver

An interactive **Maze Solver** and algorithm visualizer engineered to demonstrate the application of the **Stack Data Structure (LIFO - Last In, First Out)** in Depth-First Search (DFS) and Backtracking.

---

## 📌 Project Overview

In Computer Science and Data Structures & Algorithms (DSA), a **Stack** is one of the most fundamental linear data structures. This project brings textbook DSA concepts to life through an interactive desktop game and real-time visualizer built with standard Python (zero external dependencies required!).

### How Stack Powers the System:
1. **Procedural Maze Generation (Randomized DFS)**: Uses a custom Stack to carve guaranteed-solvable labyrinth networks with no unreachable nodes.
2. **Backtracking Maze Solver**: Uses a custom Stack where:
   - Moving into an unvisited path **pushes** `(row, col)` onto the Stack.
   - Hitting a dead-end **pops** `(row, col)` off the Stack, backtracking to the previous junction.
   - Reaching the exit guarantees that the remaining items in the Stack represent the exact solved path!

---

## 🎮 Game Modes

| Mode | Icon | Description |
| :--- | :---: | :--- |
| **Player Adventure** | 🎮 | Navigate the maze using `Arrow Keys` or `WASD`. Collect golden gems (`+150 pts`), race against the clock, toggle **Fog of War (Torchlight)**, and reach the exit portal! |
| **Stack AI Visualizer** | 🤖 | Watch the Stack-based DFS algorithm explore the maze in real time. Inspect live stack frames, watch dead ends turn red, and use the **Single Step** button to study each push and pop. |
| **Race vs Stack AI** | ⚡ | Compete against the Depth-First Search algorithm! Can human intuition and pathfinding beat the machine's Stack-driven exploration to the exit portal? |

---

## 📂 Project Architecture

```
dsa project/
│
├── stack.py             # Pure Stack Data Structure implementation (LIFO)
│                        #   - Methods: push, pop, peek, is_empty, size, to_list
│                        #   - Telemetry: peak depth, push/pop counters, state tracking
│
├── maze.py              # Maze Grid Model & Procedural Generator
│                        #   - Randomized DFS wall-carving using Stack
│                        #   - Collectible gems, start/exit portals, and presets
│
├── solver.py            # Stack-Powered DFS Maze Solver
│                        #   - Iterative Backtracking algorithm
│                        #   - Step-by-step generator for animations & telemetry
│
├── main.py              # Modern Tkinter GUI Game & Visualizer
│                        #   - 3 Game Modes, Live Stack Inspector, Audio FX, Fog of War
│
├── game.py              # Quick Launcher alias for main.py
│
├── test_maze_solver.py  # Comprehensive automated unit test suite (12 test cases)
│
└── README.md            # Project documentation and DSA technical analysis
```

---

## 🧠 Data Structure Deep Dive: The Stack

### Stack Operations (`stack.py`):
- **`push(item)`**: Inserts a coordinate `(r, c)` on top of the stack. Increments push telemetry and updates `peak_depth`. Complexity: $\mathcal{O}(1)$.
- **`pop()`**: Removes and returns the top coordinate. Increments backtrack telemetry. Raises `StackEmptyError` if empty. Complexity: $\mathcal{O}(1)$.
- **`peek()`**: Examines the top coordinate without removing it. Complexity: $\mathcal{O}(1)$.
- **`is_empty()`**: Checks whether any nodes remain in the stack. Complexity: $\mathcal{O}(1)$.

### Algorithmic Mechanics: DFS Backtracking

```
[Start Portal (1, 1)]
         │
         ▼
     PUSH (1, 1)
         │
         ▼
 ┌───► Look for Unvisited Walkable Neighbor
 │       │
 │   ┌───┴───────────────────────────────┐
 │   │ Neighbor Found                    │ No Neighbor (Dead End Hit!)
 │   ▼                                   ▼
 │  PUSH Neighbor to Stack             POP Top from Stack (Backtrack)
 │   │                                   │
 │   ▼                                   ▼
 │  Target Reached?                    Stack Empty?
 │   ├─ Yes ──► RETURN Stack (Solved)   ├─ Yes ──► NO SOLUTION
 │   └─ No  ──► Loop Again              └─ No  ──► Loop Again
 └───────────────────────────────────────────────────┘
```

### Complexity Analysis
- **Time Complexity**: $\mathcal{O}(V + E)$
  - In a grid of dimensions $R \times C$, $V \le R \times C$ and each cell has at most 4 cardinal edges ($E \le 4V$).
  - Every open cell is pushed to the stack at most once and popped at most once.
- **Space Complexity**: $\mathcal{O}(V)$
  - In the worst-case scenario (a long winding serpentine corridor), the stack depth equals the total number of walkable path cells. The peak stack depth is displayed live in the application's telemetry panel.

---

## 🚀 How to Run

### Requirements
- **Python 3.8+** (Standard installation includes `tkinter` and `winsound` on Windows).
- **No external pip packages needed!** Runs 100% out of the box.

### 1. Launch the Game
Open a terminal in this directory and run:

```bash
python main.py
```
*(or equivalently)*
```bash
python game.py
```

### 2. Run the Unit Test Suite
To run all 12 automated unit tests:

```bash
python test_maze_solver.py
```

---

## ⌨️ Controls & Keybindings

| Key / Control | Action |
| :--- | :--- |
| `↑` `↓` `←` `→` / `W` `A` `S` `D` | Move Player avatar |
| `Spacebar` | Start / Pause AI Stack Solver |
| `Enter` | Generate New Maze |
| `Size Dropdown` | Select 15x15, 21x21, 27x27, or 35x35 maze |
| `Speed Slider` | Adjust visualizer simulation speed |
| `Single Step (⏭)` | Execute one individual PUSH or POP operation |
| `Fog of War (🌫️)` | Toggle torchlight radius for challenging exploration |
| `Sound FX (🔊)` | Toggle synthesized retro sound effects |

---

## 🎨 Visual Color Legend

- 🟦 **Electric Cyan Circle**: Player Avatar
- 🟪 **Hot Pink Circle**: AI Solver Head
- 🟩 **Emerald Green Cell**: Start Position `(1, 1)` / Final Solved Path
- 🟥 **Radiant Rose Portal with Star**: Exit Portal `(rows-2, cols-2)`
- 🟨 **Golden Circles**: Collectible Gems (`+150 Pts`)
- 🟦 **Dark Navy Cells**: Explored / Visited Cells
- 🟥 **Crimson Cells**: Dead-End Backtracked Nodes (Popped from Stack)
- ⬛ **Obsidian**: Solid Walls
