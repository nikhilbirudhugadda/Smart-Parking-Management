# 🚗 Smart Parking Management System

An algorithmic, terminal-based Smart Parking Management System implemented from scratch in pure Python. Every classical data structure and algorithm in this project maps directly to a physical component of a real-world parking facility.

---

## 📁 Project Structure

```text
parking/
│
├── main.py                     # Interactive CLI Application & Simulation
├── test_smart_parking.py       # Automated Comprehensive Test Suite
├── README.md                   # Documentation & Viva/Explanation Guide
│
├── structures/                 # Core Data Structures (implemented from scratch)
│   ├── avl_tree.py             # Balanced BST for O(log n) license plate indexing
│   ├── b_tree.py               # Disk-optimized multi-way search tree for audit logs
│   ├── min_heap.py             # Priority queue for nearest available slot allocation
│   ├── max_heap.py             # Priority queue tracking longest parked vehicles
│   └── graph.py                # Adjacency-list parking lot topological map
│
├── parking/                    # Domain Models & Business Logic
│   ├── parking_lot.py          # Facility topology, floors, and graph initialization
│   ├── parking_slot.py         # Slot entity, vehicle compatibility, and distance
│   ├── vehicle.py              # Vehicle types (Car, EV, Motorcycle, Truck) & fee logic
│   └── parking_manager.py      # Central coordinator connecting all structures
│
├── algorithms/                 # Graph Traversal Algorithms
│   ├── bfs.py                  # Breadth-First Search for shortest driving route
│   └── dfs.py                  # Depth-First Search for reachability & dead-end checks
│
└── data/
    └── parking_records.json    # Persistent JSON storage for tickets and receipts
```

---

## ⚡ How to Run

You can run the application directly using `uv` (pre-installed on your system) or Python 3.9+:

### 1. Launch the Interactive Application
```bash
cd C:\Users\SahithRam\.gemini\antigravity\scratch\parking
uv run python main.py
```
*(Or if standard python is configured: `python main.py`)*

### 2. Run the Automated Test Suite
```bash
uv run python test_smart_parking.py
```

---

## 🧠 Data Structure & Algorithm Cheat Sheet

When presenting or explaining this project, use this cheat sheet to describe why each data structure was chosen:

| Data Structure / Algorithm | Real-World Parking Problem | Why this specific structure? | Time Complexity |
| :--- | :--- | :--- | :--- |
| **Min-Heap** (`min_heap.py`) | Allocating the **closest empty parking slot** to an entrance gate. | The slot with minimum physical distance is always at the root. | Peek: $\mathcal{O}(1)$<br>Pop/Push: $\mathcal{O}(\log n)$ |
| **Max-Heap** (`max_heap.py`) | Monitoring **longest parked vehicles** or highest accumulated fees. | The vehicle with maximum parked duration is always at the root. | Peek: $\mathcal{O}(1)$<br>Pop/Push: $\mathcal{O}(\log n)$ |
| **AVL Tree** (`avl_tree.py`) | Instant search for an active car by **license plate**. | Prevents worst-case BST degeneration into a linked list through auto-rotations (LL, RR, LR, RL). | Search/Insert/Delete: $\mathcal{O}(\log n)$ |
| **B-Tree** (`b_tree.py`) | Storing historical **billing receipts and audit logs**. | Standard index structure used in relational databases (MySQL/PostgreSQL) for block/disk persistence. | Search/Insert: $\mathcal{O}(t \log_t n)$ |
| **Graph** (`graph.py`) | Road network of gates, junctions, and parking bays. | Adjacency list representation of directional lanes and meter distances. | Space: $\mathcal{O}(V + E)$ |
| **BFS** (`bfs.py`) | Generating **turn-by-turn driving directions** to the slot. | BFS guarantees finding the route with the minimum number of intersections/hops. | $\mathcal{O}(V + E)$ |
| **DFS** (`dfs.py`) | Checking facility **reachability** & detecting cul-de-sacs. | Recursively explores paths to identify dead-ends or isolated bays. | $\mathcal{O}(V + E)$ |

---

## 🎮 CLI Features & Menu Options

1. **🚗 Park a Vehicle**:
   - Prompts for license plate, vehicle type (`Car`, `Motorcycle`, `EV`, `Truck`), and entrance gate (`North` or `South`).
   - Min-Heap automatically extracts the nearest compatible bay.
   - BFS generates turn-by-turn driving directions from the gate to the assigned bay.
   - Inserts ticket into AVL tree.

2. **🏁 Unpark / Checkout Vehicle**:
   - Fast $\mathcal{O}(\log n)$ AVL tree lookup by license plate.
   - Calculates duration and billing amount according to vehicle type rates.
   - Returns slot to Min-Heap for immediate reuse.
   - Logs receipt into the B-Tree audit trail.

3. **🔍 Search Active Vehicle**:
   - Queries the AVL Tree in microseconds.

4. **📊 View Parking Lot Status & Floor Map**:
   - Shows colored status of all bays on Floor 1 and Floor 2 (`🔴 OCCUPIED`, `🟢 VACANT`).

5. **⏱️ View Longest Parked Vehicles**:
   - Max-Heap query extracting top overtime vehicles.

6. **🗺️ Compare Route Planning (BFS vs DFS)**:
   - Compares the shortest hop route (BFS) vs deep exploration route (DFS).

7. **🧠 Inspect Data Structures**:
   - ASCII visual tree printout showing AVL balance factors (`BF=+0`, `BF=-1`, `H=3`).
   - Array inspection of Min-Heap available slots.
   - B-Tree sorted key inspection.

8. **⚡ Run Quick Automated Simulation**:
   - Simulates multiple vehicle arrivals and departures to demonstrate the entire lifecycle automatically.

