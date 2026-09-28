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

        # Step 2: Add Junctions — Floor 1: J1–J6 | Floor 2: J7–J12
        junctions = ["J1","J2","J3","J4","J5","J6",
                     "J7","J8","J9","J10","J11","J12"]
        for j in junctions:
            self.graph.add_node(j, f"Intersection {j}", "INTERSECTION")

        # Step 3: Connect Gates to Junctions
        self.graph.add_edge("GATE_NORTH", "J1", weight=12.0)
        self.graph.add_edge("GATE_SOUTH", "J4", weight=15.0)

        # Step 4: Floor 1 lane connections
        self.graph.add_edge("J1", "J2", weight=15.0)
        self.graph.add_edge("J2", "J3", weight=15.0)
        self.graph.add_edge("J4", "J5", weight=15.0)
        self.graph.add_edge("J5", "J6", weight=15.0)
        self.graph.add_edge("J1", "J4", weight=20.0)
        self.graph.add_edge("J2", "J5", weight=20.0)
        self.graph.add_edge("J3", "J6", weight=20.0)

        # Ramp to Floor 2 (J3→J7, J6→J10, 30m ramp cost)
        self.graph.add_edge("J3",  "J7",  weight=30.0)
        self.graph.add_edge("J6",  "J10", weight=30.0)

        # Floor 2 lane connections
        self.graph.add_edge("J7",  "J8",  weight=15.0)
        self.graph.add_edge("J8",  "J9",  weight=15.0)
        self.graph.add_edge("J10", "J11", weight=15.0)
        self.graph.add_edge("J11", "J12", weight=15.0)
        self.graph.add_edge("J7",  "J10", weight=20.0)
        self.graph.add_edge("J8",  "J11", weight=20.0)
        self.graph.add_edge("J9",  "J12", weight=20.0)

        # Step 5: Slot definitions
        # (slot_id, slot_type, floor, junction, offset_from_junction)
        slot_definitions = [
            # ── Floor 1 ──────────────────────────────────────────
            ("A-101",  SlotType.COMPACT,    1, "J1",  4.0),
            ("A-102",  SlotType.COMPACT,    1, "J1",  6.0),
            ("A-103",  SlotType.REGULAR,    1, "J2",  5.0),
            ("A-104",  SlotType.REGULAR,    1, "J2",  7.0),
            ("A-105",  SlotType.REGULAR,    1, "J2",  9.0),
            ("EV-101", SlotType.EV,         1, "J3",  5.0),
            ("EV-102", SlotType.EV,         1, "J6",  6.0),
            ("M-101",  SlotType.MOTORCYCLE, 1, "J4",  3.0),
            ("M-102",  SlotType.MOTORCYCLE, 1, "J4",  5.0),
            ("M-103",  SlotType.MOTORCYCLE, 1, "J4",  7.0),
            ("T-101",  SlotType.LARGE,      1, "J5",  8.0),
            ("T-102",  SlotType.LARGE,      1, "J5", 10.0),
            # ── Floor 2 ──────────────────────────────────────────
            ("B-201",  SlotType.COMPACT,    2, "J7",  4.0),
            ("B-202",  SlotType.COMPACT,    2, "J7",  6.0),
            ("B-203",  SlotType.REGULAR,    2, "J8",  5.0),
            ("B-204",  SlotType.REGULAR,    2, "J8",  7.0),
            ("B-205",  SlotType.REGULAR,    2, "J8",  9.0),
            ("EV-201", SlotType.EV,         2, "J9",  5.0),
            ("EV-202", SlotType.EV,         2, "J12", 6.0),
            ("B-M01",  SlotType.MOTORCYCLE, 2, "J10", 3.0),
            ("B-M02",  SlotType.MOTORCYCLE, 2, "J10", 5.0),
            ("B-M03",  SlotType.MOTORCYCLE, 2, "J10", 7.0),
            ("B-T01",  SlotType.LARGE,      2, "J11", 8.0),
            ("B-T02",  SlotType.LARGE,      2, "J11",10.0),
        ]

        # Calculate approximate base distance from GATE_NORTH for Min-Heap priority
        for slot_id, slot_type, floor, junction, offset in slot_definitions:
            node_id = f"SLOT_{slot_id.replace('-', '_')}"
            # Add slot as a node in the graph
            self.graph.add_node(node_id, f"Bay {slot_id} ({slot_type.value})", "SLOT")
            # Connect slot to its adjacent junction
            self.graph.add_edge(junction, node_id, weight=offset)

            # Approximate baseline distance from GATE_NORTH for Min-Heap priority
            # Floor 1 junctions
            base_dist_gate_north = 12.0  # Gate to J1
            if junction in ("J2", "J4"):
                base_dist_gate_north += 18.0
            elif junction in ("J3", "J5"):
                base_dist_gate_north += 32.0
            elif junction == "J6":
                base_dist_gate_north += 45.0
            # Floor 2 junctions (extra 30m ramp from J3 or J6)
            elif junction == "J7":
                base_dist_gate_north += 32.0 + 30.0          # via J3
            elif junction == "J8":
                base_dist_gate_north += 32.0 + 30.0 + 15.0
            elif junction == "J9":
                base_dist_gate_north += 32.0 + 30.0 + 30.0
            elif junction == "J10":
                base_dist_gate_north += 45.0 + 30.0          # via J6
            elif junction == "J11":
                base_dist_gate_north += 45.0 + 30.0 + 15.0
            elif junction == "J12":
                base_dist_gate_north += 45.0 + 30.0 + 30.0
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

