from flask import Blueprint, request, jsonify
from datetime import datetime
import csv
import os
import threading
from database.db import mongo
from models.predict_simple import predict_risk_level


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
    "tds",
    "fluoride",
    "nitrate",
    "chloride",
    "ec",
    "ai_prediction",
    "ai_confidence",
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


@health_bp.route("/prediction", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'ph' not in data or 'cases' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required fields: ph and cases are required"
            }), 400
        
        # Prepare input data for prediction
        input_data = {
            'ph': float(data['ph']),
            'cases': int(data['cases'])
        }
        
        # Add optional fields if provided
        optional_fields = ['tds', 'fluoride', 'nitrate', 'chloride', 'ec']
        for field in optional_fields:
            if field in data and data[field] is not None:
                input_data[field] = float(data[field])
        
        # Get prediction
        result = predict_risk_level(input_data)
        
        return jsonify({
            "success": True,
            "prediction": result['predicted_risk_level'],
            "confidence": result['confidence'],
            "probabilities": result['probabilities'],
            "interpretation": result['interpretation'],
            "input_features": result['input_features']
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@health_bp.route("/prediction/features", methods=["GET"])
def get_features():
    return jsonify({
        "required_features": [
            {
                "name": "ph",
                "description": "pH level of water (6.5-8.5 is optimal)",
                "type": "float",
                "unit": "pH units"
            },
            {
                "name": "cases",
                "description": "Number of disease cases in the area",
                "type": "int",
                "unit": "count"
            }
        ],
        "optional_features": [
            {
                "name": "tds",
                "description": "Total Dissolved Solids",
                "type": "float",
                "unit": "mg/L",
                "default": 414.0
            },
            {
                "name": "fluoride",
                "description": "Fluoride content",
                "type": "float",
                "unit": "mg/L",
                "default": 0.35
            },
            {
                "name": "nitrate",
                "description": "Nitrate content",
                "type": "float",
                "unit": "mg/L",
                "default": 13.0
            },
            {
                "name": "chloride",
                "description": "Chloride content",
                "type": "float",
                "unit": "mg/L",
                "default": 50.0
            },
            {
                "name": "ec",
                "description": "Electrical Conductivity",
                "type": "float",
                "unit": "μS/cm",
                "default": 643.0
            }
        ],
        "risk_levels": ["No Risk", "Low Risk", "Medium Risk", "High Risk"]
    })


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
                    "tds": float(row["tds"]) if row.get("tds") else None,
                    "fluoride": float(row["fluoride"]) if row.get("fluoride") else None,
                    "nitrate": float(row["nitrate"]) if row.get("nitrate") else None,
                    "chloride": float(row["chloride"]) if row.get("chloride") else None,
                    "ec": float(row["ec"]) if row.get("ec") else None,
                    "ai_prediction": row.get("ai_prediction"),
                    "ai_confidence": float(row["ai_confidence"]) if row.get("ai_confidence") else None,
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
    
    # Additional water quality parameters
    tds = to_float(data.get("tds"))
    fluoride = to_float(data.get("fluoride"))
    nitrate = to_float(data.get("nitrate"))
    chloride = to_float(data.get("chloride"))
    ec = to_float(data.get("ec"))
    
    # AI Prediction
    ai_prediction = None
    ai_confidence = None
    if ph is not None and cases is not None:
        try:
            input_data = {'ph': ph, 'cases': cases}
            if tds is not None: input_data['tds'] = tds
            if fluoride is not None: input_data['fluoride'] = fluoride
            if nitrate is not None: input_data['nitrate'] = nitrate
            if chloride is not None: input_data['chloride'] = chloride
            if ec is not None: input_data['ec'] = ec
            
            result = predict_risk_level(input_data)
            ai_prediction = result['predicted_risk_level']
            ai_confidence = result['confidence']
        except Exception as e:
            print(f"AI prediction failed: {e}")
            # Continue without AI prediction

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
            "tds": tds,
            "fluoride": fluoride,
            "nitrate": nitrate,
            "chloride": chloride,
            "ec": ec,
            "ai_prediction": ai_prediction,
            "ai_confidence": ai_confidence,
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
            tds if tds is not None else "",
            fluoride if fluoride is not None else "",
            nitrate if nitrate is not None else "",
            chloride if chloride is not None else "",
            ec if ec is not None else "",
            ai_prediction or "",
            ai_confidence if ai_confidence is not None else "",
        ]
        with csv_lock:
            with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(row)
    except Exception:
        # Intentionally ignore CSV fallback errors to not block API success
        pass

    # Return AI prediction if available, otherwise fallback to simple risk calculation
    risk = ai_prediction if ai_prediction else compute_risk(cases, turbidity)
    return jsonify({"status": "ok", "risk": risk, "ai_prediction": ai_prediction, "ai_confidence": ai_confidence}), 201


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
        # Use AI prediction if available, otherwise fallback to simple calculation
        if r.get("ai_prediction"):
            risk = r.get("ai_prediction")
        else:
            risk = compute_risk(r.get("cases"), r.get("turbidity"))
        
        # Convert AI risk levels to simple format for alerts
        if risk in ("Medium Risk", "High Risk", "Medium", "High"):
            alert_risk = "Medium" if risk in ("Medium Risk", "Medium") else "High"
            alerts_out.append({
                "timestamp": r.get("timestamp"),
                "message": f"{alert_risk} Risk Alert",
                "risk": alert_risk,
                "location_name": r.get("location_name") or "Unknown",
                "lat": r.get("lat"),
                "lng": r.get("lng"),
                "details": ", ".join(filter(None, [
                    f"cases={r['cases']}" if r.get("cases") is not None else None,
                    f"turbidity={r['turbidity']}" if r.get("turbidity") is not None else None,
                    f"AI Confidence: {int(r['ai_confidence']*100)}%" if r.get("ai_confidence") else None,
                ]))
            })
    return jsonify({"alerts": alerts_out})


@health_bp.route("/clear", methods=["POST"])
def clear_data():
    try:
        # Clear MongoDB
        mongo.db.reports.drop()
        
        # Clear CSV file
        if os.path.exists(CSV_PATH):
            os.remove(CSV_PATH)
        
        return jsonify({"status": "ok", "message": "All data cleared successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# health_routes.py placeholder
