from flask import Blueprint, request, jsonify
import datetime
from bson import ObjectId

from database import get_collection

data_bp = Blueprint("data", __name__, url_prefix="/data")


def to_json(doc):
    """Convert Mongo doc to JSON-safe dict"""
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


# ----------------- DATASETS -----------------
@data_bp.route("/datasets", methods=["POST"])
def add_dataset():
    datasets = get_collection("DATASETS")
    data = request.get_json()
    data["created_at"] = datetime.datetime.utcnow()
    inserted = datasets.insert_one(data)
    return jsonify({"id": str(inserted.inserted_id)}), 201


@data_bp.route("/datasets", methods=["GET"])
def list_datasets():
    datasets = get_collection("DATASETS")
    docs = list(datasets.find().sort("created_at", -1).limit(20))
    return jsonify([to_json(d) for d in docs]), 200


# ----------------- PREDICTIONS -----------------
@data_bp.route("/predictions", methods=["POST"])
def add_prediction():
    predictions = get_collection("PREDICTIONS")
    data = request.get_json()
    data["created_at"] = datetime.datetime.utcnow()
    inserted = predictions.insert_one(data)
    return jsonify({"id": str(inserted.inserted_id)}), 201


@data_bp.route("/predictions", methods=["GET"])
def list_predictions():
    predictions = get_collection("PREDICTIONS")
    docs = list(predictions.find().sort("created_at", -1).limit(20))
    return jsonify([to_json(d) for d in docs]), 200


# ----------------- REPORTS -----------------
@data_bp.route("/reports", methods=["POST"])
def add_report():
    reports = get_collection("REPORTS")
    data = request.get_json()
    data["created_at"] = datetime.datetime.utcnow()
    inserted = reports.insert_one(data)
    return jsonify({"id": str(inserted.inserted_id)}), 201


@data_bp.route("/reports", methods=["GET"])
def list_reports():
    reports = get_collection("REPORTS")
    docs = list(reports.find().sort("created_at", -1).limit(20))
    return jsonify([to_json(d) for d in docs]), 200


# ----------------- ALERTS -----------------
@data_bp.route("/alerts", methods=["POST"])
def add_alert():
    alerts = get_collection("ALERTS")
    data = request.get_json()
    data["created_at"] = datetime.datetime.utcnow()
    inserted = alerts.insert_one(data)
    return jsonify({"id": str(inserted.inserted_id)}), 201


@data_bp.route("/alerts", methods=["GET"])
def list_alerts():
    alerts = get_collection("ALERTS")
    docs = list(alerts.find().sort("created_at", -1).limit(20))
    return jsonify([to_json(d) for d in docs]), 200
# ----------------- LOGS -----------------
@data_bp.route("/logs", methods=["POST"])
def add_log():
    logs = get_collection("LOGS")
    data = request.get_json()
    data["created_at"] = datetime.datetime.utcnow()
    inserted = logs.insert_one(data)
    return jsonify({"id": str(inserted.inserted_id)}), 201