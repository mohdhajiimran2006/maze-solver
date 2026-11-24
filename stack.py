"""
stack.py - Custom Stack Data Structure Implementation
-----------------------------------------------------
Core DSA Component for the Maze Solver & Gaming Project.
Implements the Last-In, First-Out (LIFO) principle with full telemetry
(peak depth tracking, operation counters, and state inspection).
"""

from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class StackEmptyError(Exception):
    """Raised when an operation attempts to access or remove from an empty stack."""
    pass


class Stack(Generic[T]):
    """
    A robust, LIFO (Last-In, First-Out) Stack data structure designed for
    algorithm visualization, backtracking, and depth-first search (DFS).
    
    Attributes:
        _items (List[T]): Internal dynamic array holding stack elements.
        pushes (int): Total number of push operations performed.
        pops (int): Total number of pop operations performed.
        peak_size (int): Maximum depth reached during the stack's lifecycle.
    """

    def __init__(self) -> None:
        self._items: List[T] = []
        self.pushes: int = 0
        self.pops: int = 0
        self.peak_size: int = 0

    def push(self, item: T) -> None:
        """
        Push an item onto the top of the stack.
        Time Complexity: O(1) amortized
        Space Complexity: O(1)
        """
        self._items.append(item)
        self.pushes += 1
        if len(self._items) > self.peak_size:
            self.peak_size = len(self._items)

    def pop(self) -> T:
        """
        Remove and return the top item from the stack.
        Time Complexity: O(1)
        Raises StackEmptyError if the stack is empty.
        """
        if self.is_empty():
            raise StackEmptyError("Cannot pop from an empty stack.")
        self.pops += 1
        return self._items.pop()

    def peek(self) -> T:
        """
        Return the top item without removing it.
        Time Complexity: O(1)
        Raises StackEmptyError if the stack is empty.
        """
        if self.is_empty():
            raise StackEmptyError("Cannot peek into an empty stack.")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Return True if the stack contains no items, False otherwise."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the current number of elements in the stack."""
        return len(self._items)

    def clear(self) -> None:
        """Reset the stack to an empty state."""
        self._items.clear()

    def reset_stats(self) -> None:
        """Reset operational counters (pushes, pops, peak_size)."""
        self.pushes = 0
        self.pops = 0
        self.peak_size = len(self._items)

    def to_list(self) -> List[T]:
        """
        Return a copy of items from bottom (index 0) to top (index -1).
        """
        return list(self._items)

    def get_stats(self) -> dict:
        """Return diagnostic metrics of the stack."""
        return {
            "current_size": self.size(),
            "peak_size": self.peak_size,
            "pushes": self.pushes,
            "pops": self.pops,
        }

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return not self.is_empty()

    def __iter__(self):
        # Iterate from top to bottom
        return reversed(self._items)

    def __repr__(self) -> str:
        return f"Stack(size={self.size()}, top={self._items[-1] if self._items else None})"

    def __str__(self) -> str:
        if self.is_empty():
            return "Stack [ <BOTTOM> -> <TOP> ]: (empty)"
        items_str = ", ".join(repr(x) for x in self._items)
        return f"Stack [ <BOTTOM> {items_str} <TOP> ]"
