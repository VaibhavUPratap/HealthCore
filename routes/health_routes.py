from flask import Blueprint, request, jsonify
from datetime import datetime
import csv
import os
import threading
from database.db import mongo


health_bp = Blueprint("health", __name__)


CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "reports.csv")

# Canonical CSV field order must match existing file schema
CSV_FIELDS = [
    "timestamp",
    "reporter",
    "symptoms",
    "cases",
    "turbidity",
    "ph",
    "chlorine",
    "lat",
    "lng",
    "location_name",
]

# Simple process-level lock to avoid interleaved writes
csv_lock = threading.Lock()


def ensure_csv_header():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_FIELDS)


def compute_risk(cases: int | None, turbidity: float | None) -> str:
    if (cases is not None and cases > 10) or (turbidity is not None and turbidity > 20):
        return "High"
    if (cases is not None and cases > 5) or (turbidity is not None and turbidity > 10):
        return "Medium"
    return "Low"


def get_reports(limit: int = 200):
    items = []
    # Try MongoDB first
    try:
        cursor = mongo.db.reports.find().sort("timestamp", -1).limit(limit)
        for r in cursor:
            r.pop("_id", None)
            items.append(r)
        if items:
            return items
    except Exception:
        pass

    # Fallback to CSV
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            for row in list(csv.DictReader(f))[-limit:]:
                items.append({
                    "timestamp": row.get("timestamp"),
                    "reporter": row.get("reporter"),
                    "location_name": row.get("location_name"),
                    "lat": float(row["lat"]) if row.get("lat") else None,
                    "lng": float(row["lng"]) if row.get("lng") else None,
                    "symptoms": row.get("symptoms"),
                    "cases": int(row["cases"]) if row.get("cases") else None,
                    "turbidity": float(row["turbidity"]) if row.get("turbidity") else None,
                    "ph": float(row["ph"]) if row.get("ph") else None,
                    "chlorine": float(row["chlorine"]) if row.get("chlorine") else None,
                })
    return items


@health_bp.route("/report", methods=["POST"])
def report():
    data = request.get_json(silent=True) or request.form.to_dict()

    def to_int(v):
        try:
            return int(v) if v not in (None, "") else None
        except Exception:
            return None

    def to_float(v):
        try:
            return float(v) if v not in (None, "") else None
        except Exception:
            return None

    timestamp = datetime.utcnow().isoformat()
    reporter = data.get("reporter")
    location_name = data.get("location_name")
    lat = to_float(data.get("lat"))
    lng = to_float(data.get("lng"))
    symptoms = data.get("symptoms")
    cases = to_int(data.get("cases"))
    turbidity = to_float(data.get("turbidity"))
    ph = to_float(data.get("ph"))
    chlorine = to_float(data.get("chlorine"))

    # Write to MongoDB (primary storage)
    try:
        mongo.db.reports.insert_one({
            "timestamp": timestamp,
            "reporter": reporter,
            "location_name": location_name,
            "lat": lat,
            "lng": lng,
            "symptoms": symptoms,
            "cases": cases,
            "turbidity": turbidity,
            "ph": ph,
            "chlorine": chlorine,
        })
    except Exception:
        # Ignore Mongo failure and proceed to CSV fallback
        pass

    # Also append to CSV as a portable log (fallback)
    try:
        ensure_csv_header()
        row = [
            timestamp,
            reporter or "",
            symptoms or "",
            cases if cases is not None else "",
            turbidity if turbidity is not None else "",
            ph if ph is not None else "",
            chlorine if chlorine is not None else "",
            lat if lat is not None else "",
            lng if lng is not None else "",
            location_name or "",
        ]
        with csv_lock:
            with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(row)
    except Exception:
        # Intentionally ignore CSV fallback errors to not block API success
        pass

    return jsonify({"status": "ok", "risk": compute_risk(cases, turbidity)}), 201


@health_bp.route("/reports", methods=["GET"])
def reports():
    try:
        limit = int(request.args.get('limit', '200'))
    except Exception:
        limit = 200
    limit = max(1, min(limit, 1000))
    return jsonify({"items": get_reports(limit)})


@health_bp.route("/alerts", methods=["GET"])
def alerts():
    try:
        limit = int(request.args.get('limit', '200'))
    except Exception:
        limit = 200
    limit = max(1, min(limit, 1000))

    alerts_out = []
    for r in get_reports(limit):
        risk = compute_risk(r.get("cases"), r.get("turbidity"))
        if risk in ("Medium", "High"):
            alerts_out.append({
                "timestamp": r.get("timestamp"),
                "message": f"{risk} Risk Alert",
                "risk": risk,
                "location_name": r.get("location_name") or "Unknown",
                "lat": r.get("lat"),
                "lng": r.get("lng"),
                "details": ", ".join(filter(None, [
                    f"cases={r['cases']}" if r.get("cases") is not None else None,
                    f"turbidity={r['turbidity']}" if r.get("turbidity") is not None else None,
                ]))
            })
    return jsonify({"alerts": alerts_out})

# health_routes.py placeholder
