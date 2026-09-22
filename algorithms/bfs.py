"""
Breadth-First Search (BFS) Algorithm Implementation.
Used in the Smart Parking System to compute the shortest driving path
(minimal hops / junctions) from an entrance gate to an allocated parking slot.
"""

from collections import deque
from typing import Dict, List, Optional, Tuple
from structures.graph import Graph


def bfs_shortest_path(
    graph: Graph, start_node: str, target_node: str
) -> Tuple[Optional[List[str]], float, List[str]]:
    """
    Finds the shortest path between start_node and target_node using BFS.

    :param graph: The parking lot graph.
    :param start_node: The starting node ID (e.g. 'GATE_NORTH').
    :param target_node: The destination node ID (e.g. 'SLOT_101').
    :return: A tuple of (path_nodes, total_distance_in_meters, step_directions).
             If no path exists, returns (None, 0.0, ["No route found"]).
    """
    if start_node not in graph.nodes or target_node not in graph.nodes:
        return None, 0.0, ["Invalid start or target node"]

    if start_node == target_node:
        return [start_node], 0.0, [f"Already at destination: {start_node}"]

    # Queue stores: (current_node, [path_so_far])
    queue: deque = deque([(start_node, [start_node])])
    visited = {start_node}

    while queue:
        current, path = queue.popleft()

        if current == target_node:
            # Path found! Compute total distance and turn-by-turn directions
            total_dist, directions = _generate_directions(graph, path)
            return path, total_dist, directions

        for neighbor, _ in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None, 0.0, ["No route found between gate and slot"]


def _generate_directions(graph: Graph, path: List[str]) -> Tuple[float, List[str]]:
    """
    Calculates cumulative distance and generates human-readable navigation steps.
    """
    total_distance = 0.0
    directions: List[str] = []

    start_meta = graph.get_node(path[0])
    directions.append(f"1. Start at {start_meta.label if start_meta else path[0]}")

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        dist = graph.adj.get(u, {}).get(v, 0.0)
        total_distance += dist
        v_meta = graph.get_node(v)
        v_name = v_meta.label if v_meta else v

        if i == len(path) - 2:
            directions.append(f"{i + 2}. Proceed {dist:.1f}m and pull into assigned bay: {v_name}")
        else:
            directions.append(f"{i + 2}. Drive {dist:.1f}m along lane to {v_name}")

    return round(total_distance, 1), directions

