"""
Vehicle Model and Types for Smart Parking System.
"""

from datetime import datetime
from enum import Enum
import math
from typing import Any, Dict, Optional, Tuple


class VehicleType(str, Enum):
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    ELECTRIC = "ELECTRIC"
    TRUCK = "TRUCK"


# Hourly parking rates in USD
HOURLY_RATES: Dict[VehicleType, float] = {
    VehicleType.MOTORCYCLE: 1.50,
    VehicleType.CAR: 3.00,
    VehicleType.ELECTRIC: 3.50,  # includes charging support
    VehicleType.TRUCK: 5.00,
}


class Vehicle:
    """
    Represents a vehicle parked or entering the smart parking facility.
    """

    def __init__(
        self,
        license_plate: str,
        vehicle_type: VehicleType,
        entry_time: Optional[datetime] = None,
        ticket_id: Optional[str] = None,
    ):
        self.license_plate: str = license_plate.strip().upper()
        self.vehicle_type: VehicleType = (
            vehicle_type if isinstance(vehicle_type, VehicleType) else VehicleType(vehicle_type)
        )
        self.entry_time: datetime = entry_time if entry_time else datetime.now()
        self.ticket_id: Optional[str] = ticket_id

    def get_hourly_rate(self) -> float:
        """Returns the hourly parking rate based on the vehicle type."""
        return HOURLY_RATES.get(self.vehicle_type, 3.00)

    def calculate_fee(self, exit_time: Optional[datetime] = None) -> Tuple[float, float]:
        """
        Calculates the stay duration (in hours) and the total fee.
        Minimum billing interval is 1 hour.
        
        :return: (duration_in_hours, total_fee)
        """
        if exit_time is None:
            exit_time = datetime.now()

        duration_seconds = max(0.0, (exit_time - self.entry_time).total_seconds())
        # Convert seconds to fractional hours
        hours = duration_seconds / 3600.0
        # Round fractional hours to 2 decimal places to prevent microsecond boundary ceil jumps
        rounded_hours = round(hours, 2)
        # Round up to nearest whole hour, with a 1-hour minimum charge
        billable_hours = max(1, math.ceil(rounded_hours)) if rounded_hours > 0.05 else 0.5
        total_fee = round(billable_hours * self.get_hourly_rate(), 2)

        return rounded_hours, total_fee

    def to_dict(self) -> Dict[str, Any]:
        """Serializes vehicle object to a dictionary for JSON persistence."""
        return {
            "license_plate": self.license_plate,
            "vehicle_type": self.vehicle_type.value,
            "entry_time": self.entry_time.isoformat(),
            "ticket_id": self.ticket_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vehicle":
        """Reconstructs a Vehicle object from a serialized dictionary."""
        entry_time = (
            datetime.fromisoformat(data["entry_time"])
            if "entry_time" in data and data["entry_time"]
            else datetime.now()
        )
        return cls(
            license_plate=data["license_plate"],
            vehicle_type=VehicleType(data["vehicle_type"]),
            entry_time=entry_time,
            ticket_id=data.get("ticket_id"),
        )

    def __repr__(self) -> str:
        return f"Vehicle({self.license_plate}, {self.vehicle_type.value})"

