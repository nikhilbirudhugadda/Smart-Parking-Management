"""
Parking Lot Facility and Topological Layout.
Manages physical floors, slot catalog, and the physical road/lane navigation Graph.
"""

from typing import Dict, List, Optional
from structures.graph import Graph
from parking.parking_slot import ParkingSlot, SlotType


class ParkingLot:
    """
    Represents the complete parking facility, including all slots, floors,
    gates, and the physical navigation graph network.
    """

    def __init__(self, name: str = "Central Metro Smart Parking"):
        self.name: str = name
        self.slots: Dict[str, ParkingSlot] = {}
        self.graph: Graph = Graph()
        self._initialize_layout()

    def _initialize_layout(self) -> None:
        r"""
        Builds the default parking facility layout with gates, junctions,
        slots, and weighted lane distances.

        Layout Diagram:
                     [GATE_NORTH]
                          │ (12m)
                         [J1] ──(15m)── [J2] ──(15m)── [J3]
                        /    \           |    \           \
                    A-101   A-102      A-103  A-104       EV-101
                    (Comp)  (Comp)     (Reg)  (Reg)       (EV)
                          │ (20m)        │ (20m)          │ (20m)
                         [J4] ──(15m)── [J5] ──(15m)── [J6]
                        /    \           |    \           \
                    M-101   M-102      T-101  T-102       EV-102
                    (Moto)  (Moto)     (Trk)  (Trk)       (EV)
                          │ (15m)
                     [GATE_SOUTH]
        """
        # Step 1: Add Gates
        self.graph.add_node("GATE_NORTH", "North Entrance Gate", "GATE")
        self.graph.add_node("GATE_SOUTH", "South Entrance Gate", "GATE")

        # Step 2: Add Junctions / Intersections
        junctions = ["J1", "J2", "J3", "J4", "J5", "J6"]
        for j in junctions:
            self.graph.add_node(j, f"Intersection {j}", "INTERSECTION")

        # Step 3: Connect Gates to Junctions
        self.graph.add_edge("GATE_NORTH", "J1", weight=12.0)
        self.graph.add_edge("GATE_SOUTH", "J4", weight=15.0)

        # Step 4: Connect Main Driving Lanes between Junctions
        self.graph.add_edge("J1", "J2", weight=15.0)
        self.graph.add_edge("J2", "J3", weight=15.0)
        self.graph.add_edge("J4", "J5", weight=15.0)
        self.graph.add_edge("J5", "J6", weight=15.0)
        self.graph.add_edge("J1", "J4", weight=20.0)
        self.graph.add_edge("J2", "J5", weight=20.0)
        self.graph.add_edge("J3", "J6", weight=20.0)

        # Step 5: Define Parking Slots and attach them to adjacent Junctions
        # (slot_id, slot_type, floor, attached_junction, distance_from_junction)
        slot_definitions = [
            # Floor 1 - Compact Cars
            ("A-101", SlotType.COMPACT, 1, "J1", 4.0),
            ("A-102", SlotType.COMPACT, 1, "J1", 6.0),
            # Floor 1 - Regular Cars
            ("A-103", SlotType.REGULAR, 1, "J2", 5.0),
            ("A-104", SlotType.REGULAR, 1, "J2", 7.0),
            ("A-105", SlotType.REGULAR, 1, "J2", 9.0),
            # Floor 1 - Electric Vehicles (with Charging Stations)
            ("EV-101", SlotType.EV, 1, "J3", 5.0),
            ("EV-102", SlotType.EV, 1, "J6", 6.0),
            # Floor 1 - Motorcycles
            ("M-101", SlotType.MOTORCYCLE, 1, "J4", 3.0),
            ("M-102", SlotType.MOTORCYCLE, 1, "J4", 5.0),
            ("M-103", SlotType.MOTORCYCLE, 1, "J4", 7.0),
            # Floor 1 - Large / Heavy Vehicles / Trucks
            ("T-101", SlotType.LARGE, 1, "J5", 8.0),
            ("T-102", SlotType.LARGE, 1, "J5", 10.0),
            # Floor 2 - Additional Regular & Compact Slots
            ("B-201", SlotType.REGULAR, 2, "J3", 22.0),
            ("B-202", SlotType.REGULAR, 2, "J3", 25.0),
            ("B-203", SlotType.COMPACT, 2, "J6", 24.0),
            ("EV-201", SlotType.EV, 2, "J6", 26.0),
        ]

        # Calculate approximate base distance from GATE_NORTH for Min-Heap priority
        for slot_id, slot_type, floor, junction, offset in slot_definitions:
            node_id = f"SLOT_{slot_id.replace('-', '_')}"
            # Add slot as a node in the graph
            self.graph.add_node(node_id, f"Bay {slot_id} ({slot_type.value})", "SLOT")
            # Connect slot to its adjacent junction
            self.graph.add_edge(junction, node_id, weight=offset)

            # Approximate baseline distance from GATE_NORTH for default min-heap priority
            base_dist_gate_north = 12.0  # Gate to J1
            if junction in ("J2", "J4"):
                base_dist_gate_north += 18.0
            elif junction in ("J3", "J5"):
                base_dist_gate_north += 32.0
            elif junction == "J6":
                base_dist_gate_north += 45.0
            total_estimated_dist = round(base_dist_gate_north + offset, 1)

            slot = ParkingSlot(
                slot_id=slot_id,
                slot_type=slot_type,
                floor=floor,
                distance_from_gate=total_estimated_dist,
                graph_node_id=node_id,
            )
            self.slots[slot_id] = slot

    def get_slot(self, slot_id: str) -> Optional[ParkingSlot]:
        """Retrieves a slot by its ID."""
        return self.slots.get(slot_id.upper())

    def get_all_slots(self) -> List[ParkingSlot]:
        """Returns all parking slots in the facility."""
        return list(self.slots.values())

    def get_vacant_slots(self) -> List[ParkingSlot]:
        """Returns all unoccupied slots."""
        return [slot for slot in self.slots.values() if not slot.is_occupied]

    def get_occupied_slots(self) -> List[ParkingSlot]:
        """Returns all currently occupied slots."""
        return [slot for slot in self.slots.values() if slot.is_occupied]

    def get_summary(self) -> Dict[str, int]:
        """Returns total, occupied, and vacant slot counts."""
        total = len(self.slots)
        occupied = sum(1 for s in self.slots.values() if s.is_occupied)
        return {
            "total_slots": total,
            "occupied_slots": occupied,
            "vacant_slots": total - occupied,
        }

