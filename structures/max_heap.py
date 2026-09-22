"""
Generic Max-Heap Implementation from scratch.
Used in the Smart Parking System to monitor vehicles parked for the longest
duration or accumulating the highest parking fees.
"""

from typing import Any, Callable, List, Optional


class MaxHeap:
    """
    A binary max-heap where the element with the maximum key is always at the root (index 0).
    
    Index Math:
        - Parent of i:      (i - 1) // 2
        - Left child of i:   2 * i + 1
        - Right child of i:  2 * i + 2
    """

    def __init__(self, key_func: Optional[Callable[[Any], Any]] = None):
        """
        :param key_func: Optional function to extract comparison key from elements.
                         Defaults to identity lambda x: x.
        """
        self.heap: List[Any] = []
        self.key_func = key_func if key_func is not None else (lambda x: x)

    def is_empty(self) -> bool:
        """Returns True if the heap contains no elements."""
        return len(self.heap) == 0

    def size(self) -> int:
        """Returns the number of elements in the heap."""
        return len(self.heap)

    def peek(self) -> Optional[Any]:
        """
        Returns the maximum element without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.heap[0]

    def push(self, item: Any) -> None:
        """
        Inserts a new item into the max-heap and restores the heap property.
        Time Complexity: O(log n)
        """
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)

    def pop(self) -> Optional[Any]:
        """
        Removes and returns the maximum element from the max-heap.
        Time Complexity: O(log n)
        """
        if self.is_empty():
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root

    def _sift_up(self, index: int) -> None:
        """
        Bubbles up the element at index until heap invariant is satisfied.
        """
        item = self.heap[index]
        item_key = self.key_func(item)

        while index > 0:
            parent_idx = (index - 1) // 2
            parent = self.heap[parent_idx]
            if item_key > self.key_func(parent):
                self.heap[index] = parent
                index = parent_idx
            else:
                break
        self.heap[index] = item

    def _sift_down(self, index: int) -> None:
        """
        Bubbles down the element at index until heap invariant is satisfied.
        """
        size = len(self.heap)
        item = self.heap[index]
        item_key = self.key_func(item)

        while True:
            left_child_idx = 2 * index + 1
            right_child_idx = 2 * index + 2
            largest_idx = index
            largest_key = item_key

            # Check left child
            if left_child_idx < size:
                left_key = self.key_func(self.heap[left_child_idx])
                if left_key > largest_key:
                    largest_idx = left_child_idx
                    largest_key = left_key

            # Check right child
            if right_child_idx < size:
                right_key = self.key_func(self.heap[right_child_idx])
                if right_key > largest_key:
                    largest_idx = right_child_idx
                    largest_key = right_key

            # If largest is not current index, swap and continue
            if largest_idx != index:
                self.heap[index] = self.heap[largest_idx]
                index = largest_idx
            else:
                break
        self.heap[index] = item

    def to_list(self) -> List[Any]:
        """Returns a shallow copy of the underlying array."""
        return list(self.heap)

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"MaxHeap(size={self.size()}, max={self.peek()})"

