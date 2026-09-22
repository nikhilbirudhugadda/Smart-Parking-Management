r"""
AVL Tree (Adelson-Velsky and Landis) Implementation from scratch.
Used in the Smart Parking System to index active parked vehicles by license plate,
guaranteeing O(log n) time complexity for search, insertion, and deletion.

Rotations Visual:
  Right Rotation (LL Case):
          y                           x
         / \     RightRotate(y)      / \
        x   T3   -------------->   T1   y
       / \                             / \
      T1  T2                          T2  T3

  Left Rotation (RR Case):
        x                             y
       / \       LeftRotate(x)       / \
      T1  y      -------------->    x   T3
         / \                       / \
        T2  T3                    T1  T2
"""

from typing import Any, List, Optional, Tuple


class AVLNode:
    """Represents a single node in the AVL Tree."""

    def __init__(self, key: str, value: Any):
        self.key: str = key
        self.value: Any = value
        self.height: int = 1
        self.left: Optional["AVLNode"] = None
        self.right: Optional["AVLNode"] = None

    def __repr__(self) -> str:
        return f"AVLNode(key={self.key}, height={self.height})"


class AVLTree:
    """
    Self-balancing Binary Search Tree.
    Guarantees that the height difference (balance factor) between left and right
    subtrees of any node never exceeds 1.
    """

    def __init__(self):
        self.root: Optional[AVLNode] = None
        self._count: int = 0

    def get_height(self, node: Optional[AVLNode]) -> int:
        """Returns the height of a node (0 if None)."""
        if not node:
            return 0
        return node.height

    def get_balance(self, node: Optional[AVLNode]) -> int:
        """
        Balance Factor = Height(Left Subtree) - Height(Right Subtree)
        A balanced AVL node has a balance factor in {-1, 0, 1}.
        """
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def _right_rotate(self, y: AVLNode) -> AVLNode:
        """
        Performs a right rotation around node y.
        Used when left subtree is too tall (LL or LR case).
        """
        x = y.left
        assert x is not None
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights (child first, then parent)
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))

        # Return new root of this subtree
        return x

    def _left_rotate(self, x: AVLNode) -> AVLNode:
        """
        Performs a left rotation around node x.
        Used when right subtree is too tall (RR or RL case).
        """
        y = x.right
        assert y is not None
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights (child first, then parent)
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        # Return new root of this subtree
        return y

    def insert(self, key: str, value: Any) -> None:
        """
        Public method to insert a key-value pair into the AVL tree.
        Time Complexity: O(log n)
        """
        self.root = self._insert_node(self.root, key, value)
        self._count += 1

    def _insert_node(self, node: Optional[AVLNode], key: str, value: Any) -> AVLNode:
        # Step 1: Standard BST insertion
        if not node:
            return AVLNode(key, value)

        if key < node.key:
            node.left = self._insert_node(node.left, key, value)
        elif key > node.key:
            node.right = self._insert_node(node.right, key, value)
        else:
            # Duplicate key: update value
            node.value = value
            return node

        # Step 2: Update height of this ancestor node
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

        # Step 3: Get the balance factor to check whether this node became unbalanced
        balance = self.get_balance(node)

        # Step 4: If unbalanced, there are 4 cases:

        # Case 1 - Left Left (LL)
        if balance > 1 and node.left and key < node.left.key:
            return self._right_rotate(node)

        # Case 2 - Right Right (RR)
        if balance < -1 and node.right and key > node.right.key:
            return self._left_rotate(node)

        # Case 3 - Left Right (LR)
        if balance > 1 and node.left and key > node.left.key:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Case 4 - Right Left (RL)
        if balance < -1 and node.right and key < node.right.key:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def search(self, key: str) -> Optional[Any]:
        """
        Searches for a key in the AVL tree.
        Time Complexity: O(log n)
        """
        current = self.root
        while current:
            if key == current.key:
                return current.value
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None

    def delete(self, key: str) -> bool:
        """
        Deletes a key from the AVL tree.
        Returns True if the key was found and deleted, False otherwise.
        Time Complexity: O(log n)
        """
        if not self.search(key):
            return False
        self.root = self._delete_node(self.root, key)
        self._count -= 1
        return True

    def _get_min_value_node(self, node: AVLNode) -> AVLNode:
        """Finds the node with the smallest key in a subtree."""
        current = node
        while current.left:
            current = current.left
        return current

    def _delete_node(self, root: Optional[AVLNode], key: str) -> Optional[AVLNode]:
        # Step 1: Standard BST delete
        if not root:
            return root

        if key < root.key:
            root.left = self._delete_node(root.left, key)
        elif key > root.key:
            root.right = self._delete_node(root.right, key)
        else:
            # Node to delete found!
            # Node with only one child or no child
            if not root.left:
                return root.right
            elif not root.right:
                return root.left

            # Node with two children: Get the inorder successor (smallest in the right subtree)
            temp = self._get_min_value_node(root.right)
            root.key = temp.key
            root.value = temp.value
            root.right = self._delete_node(root.right, temp.key)

        # If the tree had only one node
        if not root:
            return root

        # Step 2: Update height of current node
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        # Step 3: Rebalance the node if necessary
        balance = self.get_balance(root)

        # Left Left Case
        if balance > 1 and self.get_balance(root.left) >= 0:
            return self._right_rotate(root)

        # Left Right Case
        if balance > 1 and self.get_balance(root.left) < 0:
            assert root.left is not None
            root.left = self._left_rotate(root.left)
            return self._right_rotate(root)

        # Right Right Case
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self._left_rotate(root)

        # Right Left Case
        if balance < -1 and self.get_balance(root.right) > 0:
            assert root.right is not None
            root.right = self._right_rotate(root.right)
            return self._left_rotate(root)

        return root

    def inorder(self) -> List[Tuple[str, Any]]:
        """
        Returns all key-value pairs sorted alphabetically by key.
        Time Complexity: O(n)
        """
        result: List[Tuple[str, Any]] = []

        def _traverse(node: Optional[AVLNode]):
            if node:
                _traverse(node.left)
                result.append((node.key, node.value))
                _traverse(node.right)

        _traverse(self.root)
        return result

    def size(self) -> int:
        """Returns the number of elements stored in the tree."""
        return self._count

    def visualize(self) -> str:
        """
        Generates a human-readable ASCII representation of the AVL Tree,
        including balance factors.
        """
        if not self.root:
            return "(Empty AVL Tree)"

        lines: List[str] = []

        def _build_tree_str(node: Optional[AVLNode], prefix: str = "", is_left: bool = True):
            if not node:
                return
            branch = "├── " if is_left else "└── "
            balance = self.get_balance(node)
            lines.append(f"{prefix}{branch}[{node.key}] (BF={balance:+d}, H={node.height})")

            child_prefix = prefix + ("│   " if is_left else "    ")
            children = []
            if node.left:
                children.append((node.left, True))
            if node.right:
                children.append((node.right, False))

            for i, (child, is_l) in enumerate(children):
                # If it's the last child, format with └──
                is_last = (i == len(children) - 1)
                _build_tree_str(child, child_prefix, not is_last)

        _build_tree_str(self.root, "", False)
        return "\n".join(lines)

