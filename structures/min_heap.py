"""
Generic Min-Heap Implementation from scratch.
Used in the Smart Parking System to find and allocate the closest available
parking slot to an entrance gate in O(1) peek and O(log n) insertion/extraction.
"""

from typing import Any, Callable, List, Optional


class MinHeap:
    """
    A binary min-heap where the element with the minimum key is always at the root (index 0).
    
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
        Returns the minimum element without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self.heap[0]

    def push(self, item: Any) -> None:
        """
        Inserts a new item into the min-heap and restores the heap property.
        Time Complexity: O(log n)
        """
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)

    def pop(self) -> Optional[Any]:
        """
        Removes and returns the minimum element from the min-heap.
        Time Complexity: O(log n)
        """
        if self.is_empty():
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        # Move the last element to the root, then sift down
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root

    def remove(self, item: Any) -> bool:
        """
        Removes an arbitrary item from the heap if present.
        Time Complexity: O(n) search + O(log n) sift
        """
        try:
            index = self.heap.index(item)
        except ValueError:
            return False

        last_item = self.heap.pop()
        if index < len(self.heap):
            self.heap[index] = last_item
            # Sift up or down depending on new value vs parent/children
            parent = (index - 1) // 2
            if index > 0 and self.key_func(self.heap[index]) < self.key_func(self.heap[parent]):
                self._sift_up(index)
            else:
                self._sift_down(index)
        return True

    def _sift_up(self, index: int) -> None:
        """
        Bubbles up the element at index until heap invariant is satisfied.
        """
        item = self.heap[index]
        item_key = self.key_func(item)

        while index > 0:
            parent_idx = (index - 1) // 2
            parent = self.heap[parent_idx]
            if item_key < self.key_func(parent):
                # Swap with parent
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
            smallest_idx = index
            smallest_key = item_key

            # Check left child
            if left_child_idx < size:
                left_key = self.key_func(self.heap[left_child_idx])
                if left_key < smallest_key:
                    smallest_idx = left_child_idx
                    smallest_key = left_key

            # Check right child
            if right_child_idx < size:
                right_key = self.key_func(self.heap[right_child_idx])
                if right_key < smallest_key:
                    smallest_idx = right_child_idx
                    smallest_key = right_key

            # If smallest is not current index, swap and continue
            if smallest_idx != index:
                self.heap[index] = self.heap[smallest_idx]
                index = smallest_idx
            else:
                break
        self.heap[index] = item

    def to_list(self) -> List[Any]:
        """Returns a shallow copy of the underlying array."""
        return list(self.heap)

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"MinHeap(size={self.size()}, min={self.peek()})"

