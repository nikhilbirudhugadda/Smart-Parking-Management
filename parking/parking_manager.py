"""
Parking Manager - Central Orchestration Controller.
Integrates Min-Heap (nearest slot allocation), AVL Tree (license plate index),
B-Tree (historical audit logs), Max-Heap (longest parked vehicles),
and Graph + BFS (turn-by-turn navigation).
"""

from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from algorithms.bfs import bfs_shortest_path
from algorithms.dfs import dfs_path, dfs_reachability
from parking.parking_lot import ParkingLot
from parking.parking_slot import COMPATIBILITY_MAP, ParkingSlot, SlotType
from parking.vehicle import Vehicle, VehicleType
from structures.avl_tree import AVLTree
from structures.b_tree import BTree
from structures.max_heap import MaxHeap
from structures.min_heap import MinHeap


def format_duration(duration_seconds: float) -> str:
    """
    Format duration based on length of stay:
      - First 60 minutes (< 3600 seconds): display in minutes, e.g. '1 min', '25 mins'.
      - After 60 minutes (>= 3600 seconds): display in hours, e.g. '1 hr', '1.5 hrs', '2 hrs'.
    """
    total_seconds = max(0.0, float(duration_seconds))
    if total_seconds < 3600:
        mins = int(round(total_seconds / 60.0))
        if mins <= 1:
            return "1 min"
        return f"{mins} mins"
    else:
        hours = total_seconds / 3600.0
        rounded_hours = round(hours, 2)
        if rounded_hours.is_integer() or round(rounded_hours, 1) == int(rounded_hours):
            val = int(rounded_hours)
            return f"{val} hr" if val == 1 else f"{val} hrs"
        if round(rounded_hours, 1) == rounded_hours:
            return f"{rounded_hours:.1f} hrs"
        return f"{rounded_hours:.2f} hrs"


class ParkingManager:
    """
    Central Controller for the Smart Parking System.
    """

    def __init__(self, records_file: str = "data/parking_records.json"):
        self.records_file: str = records_file
        self.parking_lot: ParkingLot = ParkingLot()

        # Min-Heaps for available slots partitioned by SlotType for optimal lookup
        self.min_heaps: Dict[SlotType, MinHeap] = {
            st: MinHeap() for st in SlotType
        }

        # AVL Tree for active vehicles (Key: license_plate, Value: ticket_record)
        self.active_vehicles: AVLTree = AVLTree()

        # B-Tree for completed transactions/audit log (Key: ticket_id, Value: receipt)
        self.audit_btree: BTree = BTree(t=3)

        # Ticket sequence counter
        self._ticket_seq: int = 1000

        # Initialize slot pools in Min-Heaps
        self._populate_heaps()

        # Load existing records if available
        if os.path.exists(self.records_file):
            self.load_from_json(self.records_file)

    def _populate_heaps(self) -> None:
        """Pushes all vacant slots into their respective type's Min-Heap."""
        for slot in self.parking_lot.get_all_slots():
            if not slot.is_occupied:
                self.min_heaps[slot.slot_type].push(slot)

    def _generate_ticket_id(self) -> str:
        self._ticket_seq += 1
        return f"TKT-{self._ticket_seq}"

    # -------------------------------------------------------------------------
    # PARKING OPERATIONS
    # -------------------------------------------------------------------------

    def park_vehicle(
        self,
        license_plate: str,
        vehicle_type: VehicleType,
        entry_gate: str = "GATE_NORTH",
    ) -> Dict[str, Any]:
        """
        Allocates the closest available slot using Min-Heap, computes navigation route
        using BFS, and records the vehicle in the AVL Tree in O(log n) time.
        """
        license_plate = license_plate.strip().upper()

        # 1. Check if vehicle is already parked inside
        existing = self.active_vehicles.search(license_plate)
        if existing:
            return {
                "success": False,
                "error": f"Vehicle with plate '{license_plate}' is already parked in slot {existing['slot_id']}.",
            }

        # 2. Find compatible slot types for this vehicle
        compatible_types = COMPATIBILITY_MAP.get(vehicle_type, [])
        best_slot: Optional[ParkingSlot] = None
        best_heap_type: Optional[SlotType] = None

        # Inspect candidate slots at the root of each compatible Min-Heap
        for slot_type in compatible_types:
            heap = self.min_heaps[slot_type]
            candidate: Optional[ParkingSlot] = heap.peek()
            if candidate:
                if best_slot is None or candidate.distance_from_gate < best_slot.distance_from_gate:
                    best_slot = candidate
                    best_heap_type = slot_type

        if not best_slot or best_heap_type is None:
            return {
                "success": False,
                "error": f"No available parking slots for {vehicle_type.value}.",
            }

        # 3. Pop the chosen slot from its Min-Heap (O(log n))
        allocated_slot: ParkingSlot = self.min_heaps[best_heap_type].pop()

        # 4. Create Vehicle and Ticket
        ticket_id = self._generate_ticket_id()
        vehicle = Vehicle(
            license_plate=license_plate,
            vehicle_type=vehicle_type,
            entry_time=datetime.now(),
            ticket_id=ticket_id,
        )
        allocated_slot.assign_vehicle(vehicle)

        # 5. Insert into AVL Tree for instant O(log n) search by license plate
        ticket_record = {
            "ticket_id": ticket_id,
            "license_plate": license_plate,
            "vehicle_type": vehicle_type.value,
            "slot_id": allocated_slot.slot_id,
            "entry_time": vehicle.entry_time.isoformat(),
            "floor": allocated_slot.floor,
        }
        self.active_vehicles.insert(license_plate, ticket_record)

        # 6. Compute Navigation Route using BFS (Shortest hop-count path)
        path, distance, directions = bfs_shortest_path(
            self.parking_lot.graph, entry_gate, allocated_slot.graph_node_id
        )

        # 7. Persist updated state
        self.save_to_json(self.records_file)

        return {
            "success": True,
            "ticket_id": ticket_id,
            "license_plate": license_plate,
            "vehicle_type": vehicle_type.value,
            "slot_id": allocated_slot.slot_id,
            "slot_type": allocated_slot.slot_type.value,
            "floor": allocated_slot.floor,
            "entry_time": vehicle.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
            "distance_meters": distance,
            "navigation_path": path,
            "directions": directions,
        }

    def unpark_vehicle(
        self, license_plate: str, exit_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Unparks a vehicle: searches in AVL Tree (O(log n)), calculates fee,
        returns slot back to Min-Heap (O(log n)), logs receipt to B-Tree, and deletes
        from AVL Tree.
        """
        license_plate = license_plate.strip().upper()

        # 1. Search in AVL Tree
        ticket_record = self.active_vehicles.search(license_plate)
        if not ticket_record:
            return {
                "success": False,
                "error": f"Vehicle with plate '{license_plate}' not found in active records.",
            }

        slot_id = ticket_record["slot_id"]
        slot = self.parking_lot.get_slot(slot_id)
        if not slot or not slot.current_vehicle:
            return {
                "success": False,
                "error": f"Internal state mismatch: Slot {slot_id} is not marked occupied.",
            }

        # 2. Calculate fee & duration
        if exit_time is None:
            exit_time = datetime.now()
        vehicle = slot.current_vehicle
        duration_seconds = max(0.0, (exit_time - vehicle.entry_time).total_seconds())
        duration_hours, fee = vehicle.calculate_fee(exit_time)

        # 3. Vacate slot and push back onto Min-Heap
        slot.vacate()
        self.min_heaps[slot.slot_type].push(slot)

        # 4. Remove from AVL Tree
        self.active_vehicles.delete(license_plate)

        # 5. Create receipt and index into B-Tree for historical audit
        receipt = {
            "ticket_id": ticket_record["ticket_id"],
            "license_plate": license_plate,
            "vehicle_type": ticket_record["vehicle_type"],
            "slot_id": slot_id,
            "entry_time": ticket_record["entry_time"],
            "exit_time": exit_time.isoformat(),
            "duration_hours": duration_hours,
            "duration_display": format_duration(duration_seconds),
            "fee_paid": fee,
        }
        self.audit_btree.insert(receipt["ticket_id"], receipt)

        # 6. Persist to file
        self.save_to_json(self.records_file)

        return {
            "success": True,
            "receipt": receipt,
        }

    # -------------------------------------------------------------------------
    # LOOKUP & ANALYTICS
    # -------------------------------------------------------------------------

    def search_vehicle(self, license_plate: str) -> Optional[Dict[str, Any]]:
        """
        Fast O(log n) vehicle search using the AVL Tree.
        """
        return self.active_vehicles.search(license_plate.strip().upper())

    def get_longest_parked_vehicles(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Uses a Max-Heap to extract the top-k longest parked vehicles currently in the facility.
        Time Complexity: O(n log n) to heapify, O(k log n) to extract top k.
        """
        now = datetime.now()
        active_list = self.active_vehicles.inorder()

        # Create a MaxHeap keyed by parked duration in seconds
        max_heap = MaxHeap(key_func=lambda x: x["duration_seconds"])

        for _, record in active_list:
            entry_dt = datetime.fromisoformat(record["entry_time"])
            duration_sec = (now - entry_dt).total_seconds()
            enriched_record = dict(record)
            enriched_record["duration_seconds"] = duration_sec
            enriched_record["duration_formatted"] = format_duration(duration_sec)
            max_heap.push(enriched_record)

        results: List[Dict[str, Any]] = []
        for _ in range(min(limit, max_heap.size())):
            item = max_heap.pop()
            if item:
                results.append(item)

        return results

    def compare_routes(
        self, start_gate: str, target_slot_id: str
    ) -> Dict[str, Any]:
        """
        Compares shortest-hop path (BFS) vs exploratory path (DFS) to a slot.
        """
        slot = self.parking_lot.get_slot(target_slot_id)
        if not slot:
            return {"error": f"Slot {target_slot_id} not found"}

        bfs_nodes, bfs_dist, bfs_dirs = bfs_shortest_path(
            self.parking_lot.graph, start_gate, slot.graph_node_id
        )
        dfs_nodes, dfs_dist = dfs_path(
            self.parking_lot.graph, start_gate, slot.graph_node_id
        )

        return {
            "bfs": {
                "path": bfs_nodes,
                "distance": bfs_dist,
                "hops": len(bfs_nodes) - 1 if bfs_nodes else 0,
                "directions": bfs_dirs,
            },
            "dfs": {
                "path": dfs_nodes,
                "distance": dfs_dist,
                "hops": len(dfs_nodes) - 1 if dfs_nodes else 0,
            },
        }

    # -------------------------------------------------------------------------
    # PERSISTENCE (JSON)
    # -------------------------------------------------------------------------

    def save_to_json(self, file_path: str) -> None:
        """Saves active tickets and historical logs to JSON file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        active_list = [item[1] for item in self.active_vehicles.inorder()]
        completed_list = [item[1] for item in self.audit_btree.traverse()]

        data = {
            "lot_name": self.parking_lot.name,
            "active_tickets": active_list,
            "completed_records": completed_list,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_from_json(self, file_path: str) -> None:
        """Loads state from JSON file and restores heaps, AVL tree, and B-Tree."""
        if not os.path.exists(file_path):
            return

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return

        # Restore active tickets
        for tkt in data.get("active_tickets", []):
            plate = tkt["license_plate"]
            slot_id = tkt["slot_id"]
            slot = self.parking_lot.get_slot(slot_id)
            if slot:
                # Remove slot from its vacant Min-Heap
                self.min_heaps[slot.slot_type].remove(slot)
                # Reconstruct vehicle
                vehicle = Vehicle(
                    license_plate=plate,
                    vehicle_type=VehicleType(tkt["vehicle_type"]),
                    entry_time=datetime.fromisoformat(tkt["entry_time"]),
                    ticket_id=tkt["ticket_id"],
                )
                slot.assign_vehicle(vehicle)
                # Reinsert into AVL tree
                self.active_vehicles.insert(plate, tkt)

                # Track sequence ID
                tkt_num = int(tkt["ticket_id"].replace("TKT-", ""))
                if tkt_num > self._ticket_seq:
                    self._ticket_seq = tkt_num

        # Restore completed records into B-Tree
        for rec in data.get("completed_records", []):
            self.audit_btree.insert(rec["ticket_id"], rec)
            tkt_num = int(rec["ticket_id"].replace("TKT-", ""))
            if tkt_num > self._ticket_seq:
                self._ticket_seq = tkt_num

