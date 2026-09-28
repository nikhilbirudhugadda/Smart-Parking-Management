"""
Smart Parking Management System - Flask Web Application
Wraps the existing parking data structures into a full web interface.
Run:  .venv/Scripts/python.exe  app.py
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, redirect, render_template, request, url_for
from parking.parking_manager import ParkingManager
from parking.vehicle import VehicleType

import re
import time

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

RECORDS_PATH = os.path.join(BASE_DIR, "data", "parking_records.json")
manager = ParkingManager(records_file=RECORDS_PATH)

BUILD_TS = str(int(time.time()))


@app.after_request
def no_cache(response):
    """Tell browser never to cache any response."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.context_processor
def inject_globals():
    return {"build_ts": BUILD_TS}


# ──────────────────────────────────────────────────────────
#  INDIAN NUMBER PLATE VALIDATION
# ──────────────────────────────────────────────────────────

# All valid Indian state / UT codes (RTO)
_VALID_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CG", "CH", "DD", "DL", "DN",
    "GA", "GJ", "HP", "HR", "JH", "JK", "KA", "KL", "LA", "LD",
    "MH", "ML", "MN", "MP", "MZ", "NL", "OD", "PB", "PY", "RJ",
    "SK", "TN", "TR", "TS", "UK", "UP", "WB",
}

# Strict pattern: 2 state letters · 1-2 district digits · 1-3 series letters · 1-4 number digits
_PLATE_RE = re.compile(
    r"^([A-Z]{2})[\s\-]?(\d{1,2})[\s\-]?([A-Z]{1,3})[\s\-]?(\d{1,4})$"
)


def validate_indian_plate(raw: str):
    """
    Validate and normalise an Indian vehicle number plate.
    Returns (normalised_plate, error_message).
    On success error_message is None; on failure normalised_plate is None.
    """
    cleaned = raw.strip().upper().replace(" ", "").replace("-", "")
    m = _PLATE_RE.match(cleaned)
    if not m:
        return None, (
            "Invalid format. Expected: STATE  DISTRICT  SERIES  NUMBER "
            "(e.g. AP 16 AX 8921)"
        )
    state, district, series, number = m.groups()
    if state not in _VALID_STATE_CODES:
        return None, (
            f"'{state}' is not a valid Indian state/UT code. "
            f"Valid codes: {', '.join(sorted(_VALID_STATE_CODES))}"
        )
    # Return canonical spaced format
    return f"{state} {district} {series} {number}", None


# ──────────────────────────────────────────────────────────
#  PAGE ROUTES
# ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    summary = manager.parking_lot.get_summary()
    return render_template("index.html", summary=summary)


@app.route("/park", methods=["GET", "POST"])
def park():
    result = None
    error = None
    if request.method == "POST":
        raw_plate = request.form.get("plate", "").strip()
        plate, err = validate_indian_plate(raw_plate)
        if err:
            error = err
        else:
            vtype_str = request.form.get("vehicle_type", "CAR")
            try:
                vtype = VehicleType(vtype_str)
            except ValueError:
                vtype = VehicleType.CAR
            res = manager.park_vehicle(plate, vtype, "GATE_NORTH")
            if res["success"]:
                result = res
            else:
                error = res["error"]
    return render_template("park.html", result=result, error=error)


@app.route("/unpark", methods=["GET", "POST"])
def unpark():
    receipt = None
    error = None
    if request.method == "POST":
        raw_plate = request.form.get("plate", "").strip()
        plate, err = validate_indian_plate(raw_plate)
        if err:
            error = err
        else:
            res = manager.unpark_vehicle(plate)
            if res["success"]:
                receipt = res["receipt"]
            else:
                error = res["error"]
    return render_template("unpark.html", receipt=receipt, error=error)


@app.route("/search", methods=["GET", "POST"])
def search():
    record = None
    searched = False
    plate_query = ""
    if request.method == "POST":
        raw_plate = request.form.get("plate", "").strip()
        plate, err = validate_indian_plate(raw_plate)
        if err:
            plate_query = raw_plate.upper()
            error_msg = err
            return render_template("search.html", record=None, searched=True,
                                   plate_query=plate_query, error=error_msg)
        plate_query = plate
        record = manager.search_vehicle(plate)
        searched = True
    return render_template("search.html", record=record, searched=searched,
                           plate_query=plate_query, error=None)


@app.route("/status")
def status():
    slots = manager.parking_lot.get_all_slots()
    summary = manager.parking_lot.get_summary()
    floors = {}
    for s in slots:
        floors.setdefault(s.floor, []).append(s)
    floor_data = {f: sorted(floors[f], key=lambda x: x.slot_id) for f in sorted(floors)}
    return render_template("status.html", floor_data=floor_data, summary=summary)


@app.route("/overtime")
def overtime():
    vehicles = manager.get_longest_parked_vehicles(limit=10)
    return render_template("overtime.html", vehicles=vehicles)


# ──────────────────────────────────────────────────────────
#  JSON API (for live refresh)
# ──────────────────────────────────────────────────────────

@app.route("/api/summary")
def api_summary():
    return jsonify(manager.parking_lot.get_summary())


if __name__ == "__main__":
    print("=" * 55)
    print("  Smart Parking Management System")
    print("  Running at: http://127.0.0.1:5000")
    print("  Press Ctrl+C to stop the server")
    print("=" * 55)
    app.run(debug=False, host="0.0.0.0", port=5000)
