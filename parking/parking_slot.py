"""
Parking Slot Model and Management.
"""

from enum import Enum
from typing import Any, Dict, Optional
from parking.vehicle import Vehicle, VehicleType


class SlotType(str, Enum):
    MOTORCYCLE = "MOTORCYCLE"
    COMPACT = "COMPACT"
    REGULAR = "REGULAR"
    LARGE = "LARGE"
    EV = "EV"


# Map which vehicle types can park in which slot types (ordered by preference)
COMPATIBILITY_MAP = {
    VehicleType.MOTORCYCLE: [SlotType.MOTORCYCLE, SlotType.COMPACT, SlotType.REGULAR],
    VehicleType.CAR: [SlotType.REGULAR, SlotType.COMPACT],
    VehicleType.ELECTRIC: [SlotType.EV, SlotType.REGULAR],
    VehicleType.TRUCK: [SlotType.LARGE],
}


class ParkingSlot:
    """
    Represents an individual parking spot in the facility.
    Implements comparison operators (__lt__) so it can be pushed directly
    onto a Min-Heap sorted by physical distance from the main gate.
    """

    def __init__(
        self,
        slot_id: str,
        slot_type: SlotType,
        floor: int = 1,
        distance_from_gate: float = 10.0,
        graph_node_id: Optional[str] = None,
    ):
        self.slot_id: str = slot_id
        self.slot_type: SlotType = (
            slot_type if isinstance(slot_type, SlotType) else SlotType(slot_type)
        )
        self.floor: int = floor
        self.distance_from_gate: float = float(distance_from_gate)
        self.graph_node_id: str = graph_node_id if graph_node_id else f"SLOT_{slot_id.replace('-', '_')}"
        self.is_occupied: bool = False
        self.current_vehicle: Optional[Vehicle] = None

    def can_fit(self, vehicle_type: VehicleType) -> bool:
        """Checks if a vehicle type can physically occupy this slot type."""
        allowed_slots = COMPATIBILITY_MAP.get(vehicle_type, [])
        return self.slot_type in allowed_slots

    def assign_vehicle(self, vehicle: Vehicle) -> None:
        """Parks a vehicle into this slot."""
        self.is_occupied = True
        self.current_vehicle = vehicle

    def vacate(self) -> Optional[Vehicle]:
        """Vacates the slot and returns the departing vehicle."""
        departed = self.current_vehicle
        self.is_occupied = False
        self.current_vehicle = None
        return departed

    def __lt__(self, other: "ParkingSlot") -> bool:
        """
        Comparator for MinHeap:
        Slots closer to the entrance gate have higher priority (lower numerical value).
        Ties are broken by alphanumeric slot_id.
        """
        if self.distance_from_gate == other.distance_from_gate:
            return self.slot_id < other.slot_id
        return self.distance_from_gate < other.distance_from_gate

    def __repr__(self) -> str:
        status = f"OCCUPIED ({self.current_vehicle.license_plate})" if self.is_occupied else "VACANT"
        return f"Slot[{self.slot_id} | {self.slot_type.value} | Dist: {self.distance_from_gate}m | {status}]"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes slot metadata to a dictionary."""
        return {
            "slot_id": self.slot_id,
            "slot_type": self.slot_type.value,
            "floor": self.floor,
            "distance_from_gate": self.distance_from_gate,
            "graph_node_id": self.graph_node_id,
            "is_occupied": self.is_occupied,
            "vehicle": self.current_vehicle.to_dict() if self.current_vehicle else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParkingSlot":
        """Recreates a ParkingSlot from a dictionary."""
        slot = cls(
            slot_id=data["slot_id"],
            slot_type=SlotType(data["slot_type"]),
            floor=data.get("floor", 1),
            distance_from_gate=data.get("distance_from_gate", 10.0),
            graph_node_id=data.get("graph_node_id"),
        )
        slot.is_occupied = data.get("is_occupied", False)
        if data.get("vehicle"):
            slot.current_vehicle = Vehicle.from_dict(data["vehicle"])
        return slot

