"""
B-Tree Implementation from scratch (Order / Minimum Degree t >= 2).
Used in the Smart Parking System to index historical parking transactions and audit logs,
mimicking database page indexing on disk.

Properties:
  - Every node has at most 2t - 1 keys and 2t children.
  - Every non-root node has at least t - 1 keys.
  - All leaves are at the same depth.
  - Keys within each node are kept sorted.
"""

from typing import Any, List, Optional, Tuple


class BTreeNode:
    """Represents a node in a B-Tree."""

    def __init__(self, leaf: bool = True):
        self.leaf: bool = leaf
        self.keys: List[Any] = []
        self.values: List[Any] = []
        self.children: List["BTreeNode"] = []

    def __repr__(self) -> str:
        return f"BTreeNode(keys={self.keys}, leaf={self.leaf})"


class BTree:
    """
    Self-balancing multi-way search tree.
    Minimum degree t >= 2:
      - Max keys per node = 2t - 1
      - Min keys per non-root node = t - 1
    """

    def __init__(self, t: int = 3):
        if t < 2:
            raise ValueError("Minimum degree t must be >= 2")
        self.t: int = t
        self.root: BTreeNode = BTreeNode(leaf=True)
        self._size: int = 0

    def search(self, key: Any) -> Optional[Any]:
        """
        Searches for a key in the B-Tree.
        Returns associated value, or None if not found.
        Time Complexity: O(t * log_t n)
        """
        return self._search_node(self.root, key)

    def _search_node(self, node: BTreeNode, key: Any) -> Optional[Any]:
        i = 0
        # Linear search through keys in the current node (can also be binary search)
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        # Found the key in this node!
        if i < len(node.keys) and key == node.keys[i]:
            return node.values[i]

        # Key is not here and this is a leaf node => not in tree
        if node.leaf:
            return None

        # Recurse down to the appropriate child
        return self._search_node(node.children[i], key)

    def insert(self, key: Any, value: Any) -> None:
        """
        Inserts a key-value pair into the B-Tree.
        If root is full (2t - 1 keys), it is split and height increases by 1.
        Time Complexity: O(t * log_t n)
        """
        root = self.root

        # If root is full, tree grows in height
        if len(root.keys) == (2 * self.t - 1):
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0, root)
            self.root = new_root
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)

        self._size += 1

    def _split_child(self, parent: BTreeNode, index: int, child: BTreeNode) -> None:
        """
        Splits a full child node (2t - 1 keys) into two nodes with (t - 1) keys each,
        and pushes the median key up into the parent node.
        """
        t = self.t
        # Create a new node to hold the upper (t - 1) keys of child
        sibling = BTreeNode(leaf=child.leaf)

        # Median key is at index (t - 1)
        median_key = child.keys[t - 1]
        median_value = child.values[t - 1]

        # Sibling gets keys and values from index t to end
        sibling.keys = child.keys[t:]
        sibling.values = child.values[t:]

        # If child is not a leaf, sibling also takes children from index t to end
        if not child.leaf:
            sibling.children = child.children[t:]
            child.children = child.children[:t]

        # Child keeps only the first (t - 1) keys and values
        child.keys = child.keys[: t - 1]
        child.values = child.values[: t - 1]

        # Insert new sibling into parent's children
        parent.children.insert(index + 1, sibling)

        # Push median key up into parent
        parent.keys.insert(index, median_key)
        parent.values.insert(index, median_value)

    def _insert_non_full(self, node: BTreeNode, key: Any, value: Any) -> None:
        """
        Inserts a key-value pair into a node guaranteed not to be full.
        """
        i = len(node.keys) - 1

        if node.leaf:
            # Insert key into sorted position in this leaf node
            node.keys.append(None)  # temporary slot
            node.values.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            # Find the child that should receive the new key
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            # If child is full, split it first
            if len(node.children[i].keys) == (2 * self.t - 1):
                self._split_child(node, i, node.children[i])
                if key > node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key, value)

    def traverse(self) -> List[Tuple[Any, Any]]:
        """
        Returns an in-order sorted list of (key, value) pairs stored in the B-Tree.
        """
        result: List[Tuple[Any, Any]] = []

        def _walk(node: BTreeNode):
            for i in range(len(node.keys)):
                if not node.leaf:
                    _walk(node.children[i])
                result.append((node.keys[i], node.values[i]))
            if not node.leaf and len(node.children) > len(node.keys):
                _walk(node.children[-1])

        _walk(self.root)
        return result

    def range_query(self, start_key: Any, end_key: Any) -> List[Tuple[Any, Any]]:
        """
        Finds all entries whose keys satisfy start_key <= key <= end_key.
        """
        all_items = self.traverse()
        return [item for item in all_items if start_key <= item[0] <= end_key]

    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return self.size()

