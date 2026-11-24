# ACADEMIC PROJECT REPORT
## Title: Maze Solver
**Subtitle:** Maze Solving and Backtracking Using Stack Data Structure (LIFO)  
**Course:** Data Structures & Algorithms (DSA)  
**Author:** MD Haji Imran  
**Language:** Python 3  
**Files:** `maze_solver.py`  

---

## 1. Problem Statement
Given an $R \times C$ two-dimensional grid representing a maze where:
- `0` denotes an open walkable path.
- `1` denotes an obstacle/wall.
- A **Start** coordinate $(S_r, S_c)$ and an **Exit** coordinate $(E_r, E_c)$.

The objective is to design, implement, and analyze an algorithm using the **Stack Data Structure** that determines whether a path exists from Start to Exit, displays the exploration process including backtracking, and outputs the final contiguous path coordinates.

---

## 2. Theoretical Background

### 2.1 The Stack Data Structure
A **Stack** is a linear data structure that follows the **Last-In, First-Out (LIFO)** principle. The element added most recently is the first one to be removed.

Key Operations:
1. **`push(x)`**: Inserts element $x$ onto the top of the stack. $\mathcal{O}(1)$
2. **`pop()`**: Removes and returns the element currently at the top. $\mathcal{O}(1)$
3. **`peek()`**: Reads the top element without removing it. $\mathcal{O}(1)$
4. **`is_empty()`**: Checks whether the stack has zero elements. $\mathcal{O}(1)$
5. **`size()`**: Returns current count of elements. $\mathcal{O}(1)$

### 2.2 Why Stack for Maze Traversal?
Finding a path through a labyrinth requires **Depth-First Search (DFS)**:
- Moving into a new unvisited corridor is a **forward exploration** $\rightarrow$ **`PUSH`**.
- When entering a dead-end (no valid unvisited neighbors), we must retreat to the most recent branching junction $\rightarrow$ **`POP` (Backtrack)**.
- At any point in time, the elements stored inside the Stack form the **exact, unbroken active path** from the Start position to the current exploration point.
- When the Exit is reached, the contents of the Stack naturally represent the solution path!

---

## 3. Algorithm & Pseudocode

### 3.1 Pseudocode

```text
ALGORITHM SolveMazeUsingStack(Maze, Start, Exit):
    INPUT:
        Maze: 2D array of size R x C (0 = path, 1 = wall)
        Start: tuple (start_r, start_c)
        Exit:  tuple (exit_r, exit_c)
    OUTPUT:
        SolutionPath: List of coordinates from Start to Exit, or Empty if no path

    1. Initialize Stack S
    2. Initialize VisitedSet V
    3. S.push(Start)
    4. V.add(Start)

    5. WHILE S is NOT empty DO:
         current = S.peek()

         IF current == Exit THEN:
             RETURN S.to_list()   // Success!

         neighbor_found = FALSE
         FOR each direction (DOWN, RIGHT, UP, LEFT) DO:
             next_cell = current + direction
             IF next_cell is within Maze bounds AND
                Maze[next_cell] == 0 AND
                next_cell is NOT in V THEN:
                 
                 V.add(next_cell)
                 S.push(next_cell)       // Forward step
                 neighbor_found = TRUE
                 BREAK                   // Follow this path

         IF neighbor_found == FALSE THEN:
             S.pop()                     // Dead-end: Backtrack

    6. RETURN Failure (No path exists)
```

---

## 4. Dry Run & Trace Table (Dead-End Demonstration)

Consider moving from $(0, 0)$ with neighbors $(1, 0)$ and $(0, 1)$ where $(1, 0)$ leads to a dead end at $(2, 0)$:

| Step | Current Head | Action | Stack Contents (Bottom $\rightarrow$ Top) | Notes / State |
| :---: | :---: | :---: | :--- | :--- |
| **1** | `(0, 0)` | `PUSH (0, 0)` | `[(0, 0)]` | Start node initialized |
| **2** | `(1, 0)` | `PUSH (1, 0)` | `[(0, 0), (1, 0)]` | Move DOWN |
| **3** | `(2, 0)` | `PUSH (2, 0)` | `[(0, 0), (1, 0), (2, 0)]` | Move DOWN |
| **4** | `(2, 0)` | `POP (2, 0)` | `[(0, 0), (1, 0)]` | **Dead End!** Backtrack to `(1, 0)` |
| **5** | `(1, 0)` | `POP (1, 0)` | `[(0, 0)]` | **Dead End!** Backtrack to `(0, 0)` |
| **6** | `(0, 1)` | `PUSH (0, 1)` | `[(0, 0), (0, 1)]` | Move RIGHT towards Exit |

---

## 5. Complexity Analysis

### 5.1 Time Complexity: $\mathcal{O}(V + E)$
- Let $V$ be the number of open walkable cells ($V \le R \times C$).
- Each walkable cell is visited at most once and pushed onto the stack at most once.
- Each cell has at most 4 neighboring edges ($E \le 4V$).
- In the worst case where every open cell is explored before finding the exit, the algorithm performs at most $V$ pushes and $V$ pops.
- **Overall Time Complexity:** $\mathcal{O}(R \times C)$ linear in the size of the grid.

### 5.2 Space Complexity: $\mathcal{O}(V)$
- **Stack Storage:** In the worst-case scenario (e.g., a single snake-like corridor with no branches), the stack holds all $V$ cells simultaneously.
- **Visited Set:** Stores at most $V$ coordinates.
- **Overall Space Complexity:** $\mathcal{O}(R \times C)$.

---

## 6. Sample Execution Output

```text
=================================================================
       DATA STRUCTURES PROJECT: MAZE SOLVER USING STACK
=================================================================

[1] ORIGINAL INPUT MAZE:
Legend: '#' = Wall, '.' = Open Path, 'S' = Start, 'E' = Exit

    0  1  2  3  4  5  6  7
   ------------------------
 0| S  .  .  .  #  .  .  . 
 1| .  #  #  .  #  .  #  . 
 2| .  #  .  .  .  .  #  . 
 3| #  #  .  #  #  .  #  . 
 4| .  .  .  #  .  .  .  . 
 5| .  #  #  #  .  #  #  . 
 6| .  .  .  .  .  #  .  . 
 7| #  #  #  #  .  .  .  E 

=================================================================
          STEP-BY-STEP STACK TRACE & BACKTRACKING LOG
=================================================================
Step   1: PUSH Start (0, 0) onto Stack.
Step   2: Move DOWN  -> PUSH (1,0) | Stack Depth: 2
Step   3: Move DOWN  -> PUSH (2,0) | Stack Depth: 3
Step   4: [DEAD END] at (2, 0) -> POP (Backtrack to (1, 0))
Step   5: [DEAD END] at (1, 0) -> POP (Backtrack to (0, 0))
Step   6: Move RIGHT -> PUSH (0,1) | Stack Depth: 2
...
Step  19: Move DOWN  -> PUSH (7,7) | Stack Depth: 15
-----------------------------------------------------------------
 SUCCESS! Exit reached at (7, 7)!
 Solution Path found using 15 steps.
-----------------------------------------------------------------

[2] SOLVED MAZE (PATH MARKED WITH '*'):
 0| S  *  *  *  #  .  .  . 
 1| .  #  #  *  #  .  #  . 
 2| .  #  .  *  *  *  #  . 
 3| #  #  .  #  #  *  #  . 
 4| .  .  .  #  .  *  *  * 
 5| .  #  #  #  .  #  #  * 
 6| .  .  .  .  .  #  .  * 
 7| #  #  #  #  .  .  .  E 

[3] DATA STRUCTURE (STACK) PERFORMANCE METRICS:
  - Total PUSH Operations (Forward steps): 17
  - Total POP Operations (Backtracks):    2
  - Peak Stack Size (Max Memory Used):     15
  - Solution Path Length:                  15 cells
```

---

## 7. Viva Voce / Exam Q&A Preparation

**Q1: Why did you use a Stack instead of a Queue?**  
> *Answer:* A Stack implements Depth-First Search (DFS), which actively goes deep into one path until reaching the exit or hitting a dead-end, making backtracking natural through LIFO. A Queue implements Breadth-First Search (BFS), which explores level-by-level in all directions simultaneously and requires extra parent pointers to reconstruct the path.

**Q2: What happens when the maze has no solution?**  
> *Answer:* The algorithm will explore all reachable paths, hit dead ends, pop all nodes one by one until the Stack becomes empty (`is_empty() == True`), and correctly report that no path exists.

**Q3: How do you prevent infinite loops (cycles)?**  
> *Answer:* By maintaining a `visited` set. Before pushing any neighbor onto the stack, we verify that it is not already in `visited`.

**Q4: Does Stack-based DFS always guarantee the shortest path?**  
> *Answer:* DFS guarantees finding *a* valid path if one exists. To find the guaranteed *shortest* path in an unweighted grid, BFS (using a Queue) or Dijkstra / A* is used.
