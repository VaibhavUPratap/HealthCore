from flask import Blueprint, request, jsonify
from models.predict import predict_outbreak

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/", methods=["POST"])
def predict():
    data = request.json
    prediction = predict_outbreak(data)
    return jsonify({"prediction": prediction})
