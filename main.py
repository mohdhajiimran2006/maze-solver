"""
main.py - Maze Solver
=====================
An interactive application and visualizer demonstrating how the
Stack data structure powers Depth-First Search (DFS) and Backtracking.

Game Modes:
  1. 🎮 Player Adventure: Manual gameplay with arrow keys/WASD, score, coins, fog of war.
  2. 🤖 Stack AI Solver: Real-time visualizer of the DFS Stack algorithm.
  3. ⚡ Race Mode: Player vs Stack AI! Compete to reach the exit portal first.
"""

import math
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Set, Tuple

# Ensure local imports work regardless of execution directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stack import Stack
from maze import Maze, CellType
from solver import MazeSolver, SolverStep


# ----------------------------------------------------------------------
# Sound Helper (Non-blocking using native winsound on Windows)
# ----------------------------------------------------------------------
def play_tone(freq: int, duration_ms: int, sound_enabled: bool = True) -> None:
    """Emit a non-blocking synthesized frequency tone."""
    if not sound_enabled:
        return
    try:
        import winsound
        def _beep():
            try:
                winsound.Beep(freq, duration_ms)
            except Exception:
                pass
        threading.Thread(target=_beep, daemon=True).start()
    except Exception:
        pass


def play_fanfare(sound_enabled: bool = True) -> None:
    """Play a short winning fanfare."""
    if not sound_enabled:
        return
    try:
        import winsound
        def _fanfare():
            for f in [523, 659, 784, 1046]:
                try:
                    winsound.Beep(f, 90)
                except Exception:
                    pass
                time.sleep(0.04)
        threading.Thread(target=_fanfare, daemon=True).start()
    except Exception:
        pass


# ----------------------------------------------------------------------
# Color Palette (Futuristic Dark Cyberpunk Theme)
# ----------------------------------------------------------------------
THEME = {
    "bg": "#0c1017",
    "panel_bg": "#151b26",
    "panel_border": "#212d40",
    "text": "#e2e8f0",
    "text_muted": "#8892b0",
    "wall": "#162032",
    "wall_border": "#0d1420",
    "path": "#1e293b",
    "grid_line": "#182234",
    "player": "#38bdf8",          # Cyan / Electric Blue
    "player_glow": "#0284c7",
    "ai_player": "#ec4899",       # Hot Pink
    "ai_glow": "#be185d",
    "start": "#10b981",           # Emerald Green
    "exit": "#f43f5e",            # Radiant Rose / Exit Portal
    "coin": "#fbbf24",            # Amber Gold
    "stack_head": "#f59e0b",      # Warm Amber for AI Search Head
    "stack_path": "#06b6d4",      # Cyan line for active stack path
    "visited": "#1e3a5f",         # Muted Blue for explored cells
    "dead_end": "#7f1d1d",        # Dark Crimson for popped dead ends
    "final_path": "#10b981",      # Emerald Green for solved path
    "fog": "#070a0f",
}


# ----------------------------------------------------------------------
# Main Application GUI
# ----------------------------------------------------------------------
class MazeGameApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Maze Solver")
        self.root.geometry("1240x820")
        self.root.minsize(1050, 720)
        self.root.configure(bg=THEME["bg"])

        # Maze parameters
        self.maze_size = 21
        self.maze = Maze(self.maze_size, self.maze_size)
        self.maze.generate_dfs(braid_factor=0.08, num_coins=6)
        self.solver = MazeSolver(self.maze)

        # Game & Simulation State
        self.mode = "GAME"  # "GAME", "AI_SOLVE", "RACE"
        self.player_pos: Tuple[int, int] = self.maze.start
        self.player_moves: int = 0
        self.player_score: int = 0
        self.collected_coins: Set[Tuple[int, int]] = set()
        self.game_start_time: float = time.time()
        self.game_timer_running: bool = False
        self.game_won: bool = False

        # AI Solver State
        self.ai_stepper = None
        self.ai_running: bool = False
        self.ai_timer_id = None
        self.ai_path: List[Tuple[int, int]] = []
        self.ai_visited: Set[Tuple[int, int]] = set()
        self.ai_dead_ends: Set[Tuple[int, int]] = set()
        self.ai_head: Optional[Tuple[int, int]] = None
        self.ai_stack_snapshot: List[Tuple[int, int]] = []
        self.ai_won: bool = False

        # Options
        self.fog_of_war = tk.BooleanVar(value=False)
        self.sound_enabled = tk.BooleanVar(value=True)
        self.solve_speed_ms = tk.IntVar(value=35)

        self._build_ui()
        self._bind_keys()
        self.reset_game_state()
        self._update_timer_loop()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        # 1. Top Header Banner
        header = tk.Frame(self.root, bg=THEME["panel_bg"], height=64, highlightthickness=1, highlightbackground=THEME["panel_border"])
        header.pack(fill=tk.X, side=tk.TOP, padx=10, pady=(10, 5))

        title_box = tk.Frame(header, bg=THEME["panel_bg"])
        title_box.pack(side=tk.LEFT, padx=16, pady=8)

        lbl_title = tk.Label(
            title_box,
            text="MAZE SOLVER",
            font=("Segoe UI", 16, "bold"),
            fg="#38bdf8",
            bg=THEME["panel_bg"],
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            title_box,
            text="Using Stack Data Structure (LIFO & Backtracking)",
            font=("Segoe UI", 9),
            fg=THEME["text_muted"],
            bg=THEME["panel_bg"],
        )
        lbl_sub.pack(anchor="w")

        # Mode Selector Buttons in Header
        mode_box = tk.Frame(header, bg=THEME["panel_bg"])
        mode_box.pack(side=tk.RIGHT, padx=16, pady=8)

        self.btn_mode_game = tk.Button(
            mode_box,
            text="🎮 Player Adventure",
            font=("Segoe UI", 10, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=lambda: self.switch_mode("GAME"),
        )
        self.btn_mode_game.pack(side=tk.LEFT, padx=4)

        self.btn_mode_ai = tk.Button(
            mode_box,
            text="🤖 Stack AI Visualizer",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["panel_border"],
            fg=THEME["text"],
            activebackground="#334155",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=lambda: self.switch_mode("AI_SOLVE"),
        )
        self.btn_mode_ai.pack(side=tk.LEFT, padx=4)

        self.btn_mode_race = tk.Button(
            mode_box,
            text="⚡ Race vs Stack AI",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["panel_border"],
            fg=THEME["text"],
            activebackground="#334155",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=lambda: self.switch_mode("RACE"),
        )
        self.btn_mode_race.pack(side=tk.LEFT, padx=4)

        # 2. Main Body (Maze Canvas Left, Sidebar Right)
        body = tk.Frame(self.root, bg=THEME["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left: Canvas Container
        canvas_card = tk.Frame(body, bg=THEME["panel_bg"], highlightthickness=1, highlightbackground=THEME["panel_border"])
        canvas_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6), pady=0)

        self.canvas = tk.Canvas(
            canvas_card,
            bg=THEME["bg"],
            highlightthickness=0,
            cursor="crosshair",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.canvas.bind("<Configure>", lambda e: self.render_maze())

        # Right: Sidebar (DSA Stack Inspector & Telemetry)
        sidebar = tk.Frame(body, bg=THEME["panel_bg"], width=390, highlightthickness=1, highlightbackground=THEME["panel_border"])
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0), pady=0)
        sidebar.pack_propagate(False)

        self._build_sidebar(sidebar)

        # 3. Bottom Control Toolbar
        toolbar = tk.Frame(self.root, bg=THEME["panel_bg"], height=52, highlightthickness=1, highlightbackground=THEME["panel_border"])
        toolbar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(5, 10))

        self._build_toolbar(toolbar)

    def _build_sidebar(self, parent: tk.Frame) -> None:
        """Construct the right-hand DSA Stack and gameplay telemetry panel."""
        # Section A: Game HUD & Stats
        hud_frame = tk.LabelFrame(
            parent,
            text=" GAME TELEMETRY ",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg=THEME["panel_bg"],
            padx=8,
            pady=6,
        )
        hud_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        stats_row = tk.Frame(hud_frame, bg=THEME["panel_bg"])
        stats_row.pack(fill=tk.X)

        # Score
        col1 = tk.Frame(stats_row, bg=THEME["panel_bg"])
        col1.pack(side=tk.LEFT, expand=True)
        tk.Label(col1, text="SCORE", font=("Segoe UI", 8), fg=THEME["text_muted"], bg=THEME["panel_bg"]).pack()
        self.lbl_score = tk.Label(col1, text="0", font=("Segoe UI", 14, "bold"), fg="#fbbf24", bg=THEME["panel_bg"])
        self.lbl_score.pack()

        # Moves
        col2 = tk.Frame(stats_row, bg=THEME["panel_bg"])
        col2.pack(side=tk.LEFT, expand=True)
        tk.Label(col2, text="MOVES", font=("Segoe UI", 8), fg=THEME["text_muted"], bg=THEME["panel_bg"]).pack()
        self.lbl_moves = tk.Label(col2, text="0", font=("Segoe UI", 14, "bold"), fg="#38bdf8", bg=THEME["panel_bg"])
        self.lbl_moves.pack()

        # Time
        col3 = tk.Frame(stats_row, bg=THEME["panel_bg"])
        col3.pack(side=tk.LEFT, expand=True)
        tk.Label(col3, text="TIME", font=("Segoe UI", 8), fg=THEME["text_muted"], bg=THEME["panel_bg"]).pack()
        self.lbl_time = tk.Label(col3, text="00:00", font=("Segoe UI", 14, "bold"), fg="#a78bfa", bg=THEME["panel_bg"])
        self.lbl_time.pack()

        # Coins Remaining
        self.lbl_coins_status = tk.Label(
            hud_frame,
            text="Gems: 0/0 Collected",
            font=("Segoe UI", 9),
            fg=THEME["text_muted"],
            bg=THEME["panel_bg"],
            pady=2,
        )
        self.lbl_coins_status.pack()

        # Section B: DSA Stack Data Structure Inspector
        dsa_frame = tk.LabelFrame(
            parent,
            text=" STACK (LIFO) LIVE INSPECTOR ",
            font=("Segoe UI", 9, "bold"),
            fg="#ec4899",
            bg=THEME["panel_bg"],
            padx=8,
            pady=6,
        )
        dsa_frame.pack(fill=tk.X, padx=10, pady=5)

        # 4 Metric badges
        metric_grid = tk.Frame(dsa_frame, bg=THEME["panel_bg"])
        metric_grid.pack(fill=tk.X, pady=2)

        # Depth & Peak
        m1 = tk.Frame(metric_grid, bg="#1a2436", padx=6, pady=4, highlightthickness=1, highlightbackground=THEME["panel_border"])
        m1.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        tk.Label(m1, text="Current Stack Depth", font=("Segoe UI", 7), fg=THEME["text_muted"], bg="#1a2436").pack()
        self.lbl_stack_size = tk.Label(m1, text="0", font=("Segoe UI", 12, "bold"), fg="#38bdf8", bg="#1a2436")
        self.lbl_stack_size.pack()

        m2 = tk.Frame(metric_grid, bg="#1a2436", padx=6, pady=4, highlightthickness=1, highlightbackground=THEME["panel_border"])
        m2.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk.Label(m2, text="Peak Stack Size", font=("Segoe UI", 7), fg=THEME["text_muted"], bg="#1a2436").pack()
        self.lbl_stack_peak = tk.Label(m2, text="0", font=("Segoe UI", 12, "bold"), fg="#ec4899", bg="#1a2436")
        self.lbl_stack_peak.pack()

        # Pushes & Pops
        m3 = tk.Frame(metric_grid, bg="#1a2436", padx=6, pady=4, highlightthickness=1, highlightbackground=THEME["panel_border"])
        m3.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        tk.Label(m3, text="Total PUSH Ops", font=("Segoe UI", 7), fg=THEME["text_muted"], bg="#1a2436").pack()
        self.lbl_pushes = tk.Label(m3, text="0", font=("Segoe UI", 12, "bold"), fg="#10b981", bg="#1a2436")
        self.lbl_pushes.pack()

        m4 = tk.Frame(metric_grid, bg="#1a2436", padx=6, pady=4, highlightthickness=1, highlightbackground=THEME["panel_border"])
        m4.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        tk.Label(m4, text="Backtrack (POPs)", font=("Segoe UI", 7), fg=THEME["text_muted"], bg="#1a2436").pack()
        self.lbl_pops = tk.Label(m4, text="0", font=("Segoe UI", 12, "bold"), fg="#f43f5e", bg="#1a2436")
        self.lbl_pops.pack()

        metric_grid.columnconfigure(0, weight=1)
        metric_grid.columnconfigure(1, weight=1)

        # Section C: Graphical Stack Frames (Top of Stack)
        frames_header = tk.Label(
            dsa_frame,
            text="Top of Stack Frames [LIFO]:",
            font=("Segoe UI", 8, "bold"),
            fg=THEME["text"],
            bg=THEME["panel_bg"],
            anchor="w",
            pady=2,
        )
        frames_header.pack(fill=tk.X)

        self.stack_canvas = tk.Canvas(
            dsa_frame,
            bg="#0e131b",
            height=90,
            highlightthickness=1,
            highlightbackground="#233044",
        )
        self.stack_canvas.pack(fill=tk.X, pady=(0, 4))

        # Section D: DSA Action Console / Log
        log_frame = tk.LabelFrame(
            parent,
            text=" ALGORITHM REASONING LOG ",
            font=("Segoe UI", 9, "bold"),
            fg="#a78bfa",
            bg=THEME["panel_bg"],
            padx=6,
            pady=4,
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.log_listbox = tk.Listbox(
            log_frame,
            bg="#0e131b",
            fg="#cbd5e1",
            font=("Consolas", 8),
            selectbackground="#2563eb",
            relief="flat",
            highlightthickness=0,
        )
        self.log_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scroll = tk.Scrollbar(log_frame, orient="vertical", command=self.log_listbox.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_listbox.config(yscrollcommand=log_scroll.set)

    def _build_toolbar(self, parent: tk.Frame) -> None:
        """Construct the bottom control bar."""
        # Maze Size
        tk.Label(parent, text="Size:", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["panel_bg"]).pack(side=tk.LEFT, padx=(10, 4))
        self.size_var = tk.StringVar(value="21x21 (Medium)")
        size_menu = ttk.Combobox(
            parent,
            textvariable=self.size_var,
            values=["15x15 (Easy)", "21x21 (Medium)", "27x27 (Hard)", "35x35 (Labyrinth)"],
            width=15,
            state="readonly",
        )
        size_menu.pack(side=tk.LEFT, padx=4)
        size_menu.bind("<<ComboboxSelected>>", self._on_size_change)

        # New Maze Button
        btn_new_maze = tk.Button(
            parent,
            text="🎲 New Maze",
            font=("Segoe UI", 9, "bold"),
            bg="#334155",
            fg="white",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.generate_new_maze,
        )
        btn_new_maze.pack(side=tk.LEFT, padx=6)

        # Reset / Clear Path
        btn_reset = tk.Button(
            parent,
            text="🔄 Reset Level",
            font=("Segoe UI", 9),
            bg="#1e293b",
            fg="#94a3b8",
            relief="flat",
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.reset_game_state,
        )
        btn_reset.pack(side=tk.LEFT, padx=4)

        # Separator
        ttk.Separator(parent, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=4)

        # AI Control Buttons
        self.btn_solve = tk.Button(
            parent,
            text="▶ Solve with Stack",
            font=("Segoe UI", 9, "bold"),
            bg="#059669",
            fg="white",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.toggle_ai_solve,
        )
        self.btn_solve.pack(side=tk.LEFT, padx=4)

        self.btn_step = tk.Button(
            parent,
            text="⏭ Single Step",
            font=("Segoe UI", 9),
            bg="#1e293b",
            fg="#cbd5e1",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.step_ai_once,
        )
        self.btn_step.pack(side=tk.LEFT, padx=4)

        # Speed Slider
        tk.Label(parent, text="Speed:", font=("Segoe UI", 8), fg=THEME["text_muted"], bg=THEME["panel_bg"]).pack(side=tk.LEFT, padx=(10, 2))
        speed_slider = tk.Scale(
            parent,
            from_=1,
            to=120,
            orient=tk.HORIZONTAL,
            variable=self.solve_speed_ms,
            showvalue=0,
            bg=THEME["panel_bg"],
            troughcolor="#1e293b",
            activebackground="#38bdf8",
            highlightthickness=0,
            length=80,
        )
        speed_slider.pack(side=tk.LEFT, padx=2)

        # Checkboxes: Fog of War and Audio
        chk_fog = tk.Checkbutton(
            parent,
            text="🌫️ Fog of War",
            variable=self.fog_of_war,
            font=("Segoe UI", 9),
            fg=THEME["text"],
            bg=THEME["panel_bg"],
            activebackground=THEME["panel_bg"],
            activeforeground="#38bdf8",
            selectcolor="#0f172a",
            command=self.render_maze,
        )
        chk_fog.pack(side=tk.LEFT, padx=8)

        chk_sound = tk.Checkbutton(
            parent,
            text="🔊 Sound FX",
            variable=self.sound_enabled,
            font=("Segoe UI", 9),
            fg=THEME["text"],
            bg=THEME["panel_bg"],
            activebackground=THEME["panel_bg"],
            activeforeground="#38bdf8",
            selectcolor="#0f172a",
        )
        chk_sound.pack(side=tk.LEFT, padx=6)

    # ------------------------------------------------------------------
    # Keyboard Navigation & Gameplay Controls
    # ------------------------------------------------------------------
    def _bind_keys(self) -> None:
        self.root.bind("<Up>", lambda e: self.move_player(-1, 0))
        self.root.bind("<Down>", lambda e: self.move_player(1, 0))
        self.root.bind("<Left>", lambda e: self.move_player(0, -1))
        self.root.bind("<Right>", lambda e: self.move_player(0, 1))

        self.root.bind("w", lambda e: self.move_player(-1, 0))
        self.root.bind("s", lambda e: self.move_player(1, 0))
        self.root.bind("a", lambda e: self.move_player(0, -1))
        self.root.bind("d", lambda e: self.move_player(0, 1))

        self.root.bind("<space>", lambda e: self.toggle_ai_solve())
        self.root.bind("<Return>", lambda e: self.generate_new_maze())

    def move_player(self, dr: int, dc: int) -> None:
        """Handle player movement via keyboard in GAME or RACE mode."""
        if self.game_won or self.ai_won:
            return

        cr, cc = self.player_pos
        nr, nc = cr + dr, cc + dc

        if not self.maze.is_walkable(nr, nc):
            play_tone(180, 40, self.sound_enabled.get())
            return

        # Start timer on first move
        if not self.game_timer_running:
            self.game_start_time = time.time()
            self.game_timer_running = True

        self.player_pos = (nr, nc)
        self.player_moves += 1
        play_tone(520, 25, self.sound_enabled.get())

        # Collect coin
        if (nr, nc) in self.maze.coins and (nr, nc) not in self.collected_coins:
            self.collected_coins.add((nr, nc))
            self.player_score += 150
            play_tone(880, 50, self.sound_enabled.get())
            self.log_message(f"⭐ Gem collected at {(nr, nc)}! +150 Pts")

        # Check win condition
        if (nr, nc) == self.maze.exit:
            self.game_won = True
            self.game_timer_running = False
            bonus = max(0, 1000 - self.player_moves * 10)
            self.player_score += 500 + bonus
            play_fanfare(self.sound_enabled.get())
            self.log_message(f"🏆 VICTORY! Reached Exit in {self.player_moves} moves. Final Score: {self.player_score}")
            if self.mode == "RACE":
                messagebox.showinfo("VICTORY!", f"You beat the Stack AI to the exit!\nMoves: {self.player_moves}\nScore: {self.player_score}")
            else:
                messagebox.showinfo("MAZE CONQUERED!", f"Congratulations!\nMoves: {self.player_moves}\nScore: {self.player_score}")

        self._update_stats_display()
        self.render_maze()

    # ------------------------------------------------------------------
    # Mode Management
    # ------------------------------------------------------------------
    def switch_mode(self, new_mode: str) -> None:
        """Switch between Adventure, AI Visualizer, and Race modes."""
        self.stop_ai()
        self.mode = new_mode

        # Update button highlights
        self.btn_mode_game.configure(bg="#2563eb" if new_mode == "GAME" else THEME["panel_border"])
        self.btn_mode_ai.configure(bg="#2563eb" if new_mode == "AI_SOLVE" else THEME["panel_border"])
        self.btn_mode_race.configure(bg="#2563eb" if new_mode == "RACE" else THEME["panel_border"])

        self.reset_game_state()

        if new_mode == "GAME":
            self.log_message("🎮 Switched to Adventure Mode. Use Arrow Keys or WASD to navigate!")
            self.btn_solve.configure(state="normal", text="▶ Solve with Stack")
        elif new_mode == "AI_SOLVE":
            self.log_message("🤖 Switched to Stack AI Mode. Press 'Solve with Stack' or 'Single Step'.")
            self.btn_solve.configure(state="normal", text="▶ Run Stack AI")
        elif new_mode == "RACE":
            self.log_message("⚡ RACE MODE! Both Player and Stack AI start simultaneously! Go!")
            self.btn_solve.configure(state="normal", text="⏸ Pause AI")
            self.start_ai()

    # ------------------------------------------------------------------
    # AI Stack Solver Animation Loop
    # ------------------------------------------------------------------
    def toggle_ai_solve(self) -> None:
        """Start or pause the AI solver animation."""
        if self.ai_running:
            self.stop_ai()
        else:
            self.start_ai()

    def start_ai(self) -> None:
        """Initialize and run the Stack-based DFS Solver generator."""
        if self.ai_stepper is None or self.ai_won:
            self.solver.reset()
            self.ai_stepper = self.solver.solve_step_by_step()
            self.ai_visited.clear()
            self.ai_dead_ends.clear()
            self.ai_path.clear()
            self.ai_head = None
            self.ai_won = False

        self.ai_running = True
        self.btn_solve.configure(text="⏸ Pause AI", bg="#dc2626")
        self._ai_tick()

    def stop_ai(self) -> None:
        """Halt the AI solver animation."""
        self.ai_running = False
        if self.ai_timer_id is not None:
            self.root.after_cancel(self.ai_timer_id)
            self.ai_timer_id = None
        self.btn_solve.configure(text="▶ Solve with Stack", bg="#059669")

    def step_ai_once(self) -> None:
        """Advance the Stack DFS algorithm by exactly one step."""
        if self.ai_stepper is None or self.ai_won:
            self.solver.reset()
            self.ai_stepper = self.solver.solve_step_by_step()
            self.ai_visited.clear()
            self.ai_dead_ends.clear()
            self.ai_path.clear()
            self.ai_head = None
            self.ai_won = False

        self._advance_ai_step()

    def _ai_tick(self) -> None:
        """Continuous timer step for AI solver animation."""
        if not self.ai_running:
            return

        has_more = self._advance_ai_step()
        if has_more and not self.ai_won:
            # Schedule next step with inverted speed (higher slider value = faster)
            delay = max(5, 130 - self.solve_speed_ms.get())
            self.ai_timer_id = self.root.after(delay, self._ai_tick)
        else:
            self.stop_ai()

    def _advance_ai_step(self) -> bool:
        """Execute one state yield of the Stack DFS solver generator."""
        try:
            step: SolverStep = next(self.ai_stepper)
            self.ai_head = step.current_cell
            self.ai_stack_snapshot = step.stack_snapshot

            if step.action == "START" or step.action == "VISIT":
                if step.current_cell:
                    self.ai_visited.add(step.current_cell)
                    self.ai_path = list(step.stack_snapshot)
                play_tone(640, 15, self.sound_enabled.get() and self.solve_speed_ms.get() < 80)

            elif step.action == "BACKTRACK":
                if step.current_cell:
                    self.ai_dead_ends.add(step.current_cell)
                    self.ai_path = list(step.stack_snapshot)
                play_tone(280, 20, self.sound_enabled.get() and self.solve_speed_ms.get() < 80)

            elif step.action == "SUCCESS":
                self.ai_won = True
                self.ai_path = step.stack_snapshot
                self.log_message(f"🎉 {step.message}")
                play_fanfare(self.sound_enabled.get())
                if self.mode == "RACE" and not self.game_won:
                    messagebox.showinfo("AI WINS!", "The Stack DFS Algorithm reached the exit before you!")
                self._update_dsa_telemetry(step)
                self.render_maze()
                return False

            elif step.action == "NO_SOLUTION":
                self.log_message(f"❌ {step.message}")
                return False

            self._update_dsa_telemetry(step)
            self.render_maze()
            return True

        except StopIteration:
            return False

    # ------------------------------------------------------------------
    # Telemetry and Inspector Updates
    # ------------------------------------------------------------------
    def _update_dsa_telemetry(self, step: SolverStep) -> None:
        stats = self.solver.stack.get_stats()
        self.lbl_stack_size.configure(text=str(stats["current_size"]))
        self.lbl_stack_peak.configure(text=str(stats["peak_size"]))
        self.lbl_pushes.configure(text=str(stats["pushes"]))
        self.lbl_pops.configure(text=str(stats["pops"]))

        # Log entry for educational insight
        if step.action in ("START", "SUCCESS", "NO_SOLUTION") or stats["pushes"] % 4 == 0 or step.action == "BACKTRACK":
            self.log_message(f"[{step.action[:4]}] {step.message}")

        self._render_stack_frames()

    def _render_stack_frames(self) -> None:
        """Draw visual vertical stack representation of top elements."""
        self.stack_canvas.delete("all")
        w = self.stack_canvas.winfo_width() or 340
        h = self.stack_canvas.winfo_height() or 90

        if not self.ai_stack_snapshot:
            self.stack_canvas.create_text(
                w // 2, h // 2,
                text="Stack is empty (LIFO Idle)",
                fill=THEME["text_muted"],
                font=("Segoe UI", 9, "italic"),
            )
            return

        # Show up to 4 top items horizontally or vertically
        items_to_show = self.ai_stack_snapshot[-5:]
        box_width = max(55, (w - 30) // len(items_to_show))
        box_h = 32
        y = (h - box_h) // 2

        x_start = 10
        for idx, coord in enumerate(items_to_show):
            is_top = (idx == len(items_to_show) - 1)
            fill_col = "#0284c7" if is_top else "#1e293b"
            border_col = "#38bdf8" if is_top else "#334155"

            # Draw cell box
            self.stack_canvas.create_rectangle(
                x_start, y, x_start + box_width, y + box_h,
                fill=fill_col, outline=border_col, width=2 if is_top else 1
            )
            # Label
            label_text = f"({coord[0]},{coord[1]})"
            self.stack_canvas.create_text(
                x_start + box_width // 2, y + box_h // 2,
                text=label_text,
                fill="white" if is_top else THEME["text"],
                font=("Consolas", 8, "bold" if is_top else "normal"),
            )
            if is_top:
                self.stack_canvas.create_text(
                    x_start + box_width // 2, y - 9,
                    text="▲ TOP",
                    fill="#38bdf8",
                    font=("Segoe UI", 7, "bold"),
                )
            x_start += box_width + 4

    def log_message(self, msg: str) -> None:
        """Add entry to live algorithm console."""
        self.log_listbox.insert(tk.END, msg)
        self.log_listbox.see(tk.END)

    def _update_stats_display(self) -> None:
        self.lbl_score.configure(text=str(self.player_score))
        self.lbl_moves.configure(text=str(self.player_moves))
        total_coins = len(self.maze.coins)
        found_coins = len(self.collected_coins)
        self.lbl_coins_status.configure(
            text=f"Gems: {found_coins}/{total_coins} Collected  (+{found_coins * 150} pts)"
        )

    def _update_timer_loop(self) -> None:
        """Update the stopwatch timer."""
        if self.game_timer_running and not self.game_won:
            elapsed = int(time.time() - self.game_start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            self.lbl_time.configure(text=f"{mins:02d}:{secs:02d}")
        self.root.after(500, self._update_timer_loop)

    # ------------------------------------------------------------------
    # Maze Generation & Reset
    # ------------------------------------------------------------------
    def _on_size_change(self, event=None) -> None:
        val = self.size_var.get()
        if "15x15" in val:
            self.maze_size = 15
        elif "21x21" in val:
            self.maze_size = 21
        elif "27x27" in val:
            self.maze_size = 27
        elif "35x35" in val:
            self.maze_size = 35
        self.generate_new_maze()

    def generate_new_maze(self) -> None:
        """Procedurally generate a fresh solvable maze."""
        self.stop_ai()
        self.maze = Maze(self.maze_size, self.maze_size)
        num_coins = max(3, self.maze_size // 3)
        self.maze.generate_dfs(braid_factor=0.08, num_coins=num_coins)
        self.solver = MazeSolver(self.maze)
        self.log_message(f"🎲 Generated new {self.maze.rows}x{self.maze.cols} maze via Stack DFS.")
        self.reset_game_state()

    def reset_game_state(self) -> None:
        """Reset player and AI exploration positions."""
        self.stop_ai()
        self.player_pos = self.maze.start
        self.player_moves = 0
        self.player_score = 0
        self.collected_coins.clear()
        self.game_start_time = time.time()
        self.game_timer_running = False
        self.game_won = False

        self.ai_stepper = None
        self.ai_head = None
        self.ai_visited.clear()
        self.ai_dead_ends.clear()
        self.ai_path.clear()
        self.ai_stack_snapshot.clear()
        self.ai_won = False

        self.lbl_time.configure(text="00:00")
        self.lbl_stack_size.configure(text="0")
        self.lbl_stack_peak.configure(text="0")
        self.lbl_pushes.configure(text="0")
        self.lbl_pops.configure(text="0")
        self.stack_canvas.delete("all")

        self._update_stats_display()
        self.render_maze()

    # ------------------------------------------------------------------
    # Canvas Rendering
    # ------------------------------------------------------------------
    def render_maze(self) -> None:
        """Render the complete maze grid, fog, player, and AI Stack paths."""
        self.canvas.delete("all")
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw <= 10 or ch <= 10:
            return

        rows = self.maze.rows
        cols = self.maze.cols

        # Cell size calculated to fit square in canvas
        cell_size = min(cw / cols, ch / rows)
        offset_x = (cw - (cell_size * cols)) / 2
        offset_y = (ch - (cell_size * rows)) / 2

        pr, pc = self.player_pos
        fog_enabled = self.fog_of_war.get() and self.mode == "GAME"
        vision_radius = 4

        # 1. Draw Maze Cells
        for r in range(rows):
            for c in range(cols):
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # Fog check
                dist_to_player = math.hypot(r - pr, c - pc)
                if fog_enabled and dist_to_player > vision_radius:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=THEME["fog"], outline="")
                    continue

                cell_val = self.maze.grid[r][c]

                if cell_val == CellType.WALL:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=THEME["wall"],
                        outline=THEME["wall_border"],
                    )
                else:
                    # Path base
                    bg_color = THEME["path"]

                    # AI Visualizer states
                    if (r, c) in self.ai_dead_ends:
                        bg_color = THEME["dead_end"]
                    elif (r, c) in self.ai_visited:
                        bg_color = THEME["visited"]
                    if (r, c) in self.ai_path:
                        bg_color = THEME["final_path"] if self.ai_won else THEME["stack_path"]

                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=bg_color,
                        outline=THEME["grid_line"],
                    )

                # Draw start and exit portals
                if (r, c) == self.maze.start:
                    pad = cell_size * 0.15
                    self.canvas.create_rectangle(
                        x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                        fill=THEME["start"],
                        outline="#34d399",
                        width=2,
                    )
                elif (r, c) == self.maze.exit:
                    pad = cell_size * 0.15
                    self.canvas.create_oval(
                        x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                        fill=THEME["exit"],
                        outline="#fda4af",
                        width=2,
                    )
                    # Portal spiral/symbol
                    self.canvas.create_text(
                        (x1 + x2) / 2, (y1 + y2) / 2,
                        text="★",
                        fill="white",
                        font=("Segoe UI", int(cell_size * 0.5), "bold"),
                    )

                # Draw Collectible Coins
                if (r, c) in self.maze.coins and (r, c) not in self.collected_coins:
                    if not (fog_enabled and dist_to_player > vision_radius):
                        cx = (x1 + x2) / 2
                        cy = (y1 + y2) / 2
                        radius = cell_size * 0.22
                        self.canvas.create_oval(
                            cx - radius, cy - radius, cx + radius, cy + radius,
                            fill=THEME["coin"],
                            outline="#fef08a",
                            width=1,
                        )

        # 2. Draw AI Search Head
        if self.ai_head and (self.mode in ("AI_SOLVE", "RACE")):
            hr, hc = self.ai_head
            hx1 = offset_x + hc * cell_size
            hy1 = offset_y + hr * cell_size
            pad = cell_size * 0.12
            self.canvas.create_oval(
                hx1 + pad, hy1 + pad, hx1 + cell_size - pad, hy1 + cell_size - pad,
                fill=THEME["ai_player"],
                outline=THEME["ai_glow"],
                width=3,
            )

        # 3. Draw Player
        if self.mode in ("GAME", "RACE"):
            px1 = offset_x + pc * cell_size
            py1 = offset_y + pr * cell_size
            pad = cell_size * 0.12
            # Glow halo
            self.canvas.create_oval(
                px1 + pad - 2, py1 + pad - 2, px1 + cell_size - pad + 2, py1 + cell_size - pad + 2,
                outline=THEME["player_glow"],
                width=2,
            )
            # Player Body
            self.canvas.create_oval(
                px1 + pad, py1 + pad, px1 + cell_size - pad, py1 + cell_size - pad,
                fill=THEME["player"],
                outline="#ffffff",
                width=2,
            )


# ----------------------------------------------------------------------
# Application Entry Point
# ----------------------------------------------------------------------
def main() -> None:
    root = tk.Tk()
    app = MazeGameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
