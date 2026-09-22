"""
Graph Data Structure Implementation.
Used in the Smart Parking System to represent the physical layout of the parking facility:
nodes represent entrance/exit gates, road junctions, and individual parking bays.
Edges represent driveways/lanes with distances in meters.
"""

from typing import Dict, List, Optional, Set, Tuple


class GraphNode:
    """Represents a location waypoint or spot in the parking lot."""

    def __init__(self, node_id: str, label: str, node_type: str = "INTERSECTION"):
        """
        :param node_id: Unique string identifier (e.g. 'GATE_NORTH', 'J1', 'SLOT_101')
        :param label: Human-readable name (e.g. 'North Entrance Gate', 'Junction 1')
        :param node_type: 'GATE', 'INTERSECTION', or 'SLOT'
        """
        self.node_id: str = node_id
        self.label: str = label
        self.node_type: str = node_type.upper()

    def __repr__(self) -> str:
        return f"GraphNode({self.node_id}, type={self.node_type})"


class Graph:
    """
    Adjacency-List Graph representing the physical parking lot topology.
    Supports directed and bidirectional weighted edges.
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        # adjacency list: node_id -> { neighbor_id: weight (distance in meters) }
        self.adj: Dict[str, Dict[str, float]] = {}

    def add_node(self, node_id: str, label: str = "", node_type: str = "INTERSECTION") -> GraphNode:
        """Adds a node to the graph if it doesn't already exist."""
        if node_id not in self.nodes:
            if not label:
                label = node_id
            node = GraphNode(node_id, label, node_type)
            self.nodes[node_id] = node
            self.adj[node_id] = {}
        return self.nodes[node_id]

    def add_edge(self, u: str, v: str, weight: float = 1.0, bidirectional: bool = True) -> None:
        """
        Adds a weighted lane/driveway between node u and node v.
        """
        if u not in self.nodes:
            self.add_node(u)
        if v not in self.nodes:
            self.add_node(v)

        self.adj[u][v] = weight
        if bidirectional:
            self.adj[v][u] = weight

    def get_neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        """Returns a list of (neighbor_node_id, distance) for a given node."""
        if node_id not in self.adj:
            return []
        return list(self.adj[node_id].items())

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Returns node metadata by id."""
        return self.nodes.get(node_id)

    def all_nodes(self) -> List[str]:
        """Returns all node IDs."""
        return list(self.nodes.keys())

    def total_nodes(self) -> int:
        return len(self.nodes)

    def total_edges(self) -> int:
        count = sum(len(neighbors) for neighbors in self.adj.values())
        return count // 2  # Assuming undirected count approximation

