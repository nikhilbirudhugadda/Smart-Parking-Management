"""
Depth-First Search (DFS) Algorithm Implementation.
Used in the Smart Parking System for:
  1. Checking facility reachability (verifying all parking bays are reachable from the entrance).
  2. Finding alternative scenic/maintenance driving paths.
  3. Detecting dead-ends or isolated cul-de-sacs in the layout.
"""

from typing import Dict, List, Optional, Set, Tuple
from structures.graph import Graph


def dfs_path(
    graph: Graph, start_node: str, target_node: str
) -> Tuple[Optional[List[str]], float]:
    """
    Finds a path between start_node and target_node using DFS (exploring deep before wide).

    :param graph: The parking lot graph.
    :param start_node: Starting node ID.
    :param target_node: Target node ID.
    :return: A tuple of (path, total_distance) or (None, 0.0) if no path exists.
    """
    if start_node not in graph.nodes or target_node not in graph.nodes:
        return None, 0.0

    visited: Set[str] = set()

    def _dfs(current: str, path: List[str]) -> Optional[List[str]]:
        if current == target_node:
            return path
        visited.add(current)

        for neighbor, _ in graph.get_neighbors(current):
            if neighbor not in visited:
                result = _dfs(neighbor, path + [neighbor])
                if result is not None:
                    return result
        return None

    path = _dfs(start_node, [start_node])
    if not path:
        return None, 0.0

    total_dist = 0.0
    for i in range(len(path) - 1):
        total_dist += graph.adj.get(path[i], {}).get(path[i + 1], 0.0)

    return path, round(total_dist, 1)


def dfs_reachability(graph: Graph, start_node: str) -> Set[str]:
    """
    Traverses the graph using DFS to return all nodes reachable from start_node.
    Used during parking lot audits to ensure no bays are trapped or cut off.
    """
    if start_node not in graph.nodes:
        return set()

    visited: Set[str] = set()
    stack: List[str] = [start_node]

    while stack:
        current = stack.pop()
        if current not in visited:
            visited.add(current)
            for neighbor, _ in graph.get_neighbors(current):
                if neighbor not in visited:
                    stack.append(neighbor)

    return visited


def dfs_find_dead_ends(graph: Graph) -> List[str]:
    """
    Identifies slots or junctions that only have a single incoming/outgoing lane,
    which represents a dead-end or turnaround point.
    """
    dead_ends: List[str] = []
    for node_id, neighbors in graph.adj.items():
        node_meta = graph.get_node(node_id)
        # Check if node has only 1 edge and is not an entrance/exit gate
        if len(neighbors) == 1 and node_meta and node_meta.node_type != "GATE":
            dead_ends.append(node_id)
    return dead_ends

