from flask import Blueprint, request, jsonify
from models.predict_simple import predict_risk_level
import traceback

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/", methods=["POST"])
def predict():
    """
    Predict health risk level based on water quality and health data
    Expected input:
    {
        "ph": float (required),
        "cases": int (required),
        "tds": float (optional),
        "fluoride": float (optional),
        "nitrate": float (optional),
        "chloride": float (optional),
        "ec": float (optional)
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        if 'ph' not in data:
            return jsonify({"error": "pH is required"}), 400
        
        if 'cases' not in data and 'total_cases' not in data:
            return jsonify({"error": "Cases count is required"}), 400
        
        # Make prediction
        result = predict_risk_level(data)
        
        if 'error' in result:
            return jsonify({"error": result['error']}), 500
        
        return jsonify({
            "success": True,
            "prediction": result['predicted_risk_level'],
            "probabilities": result['probabilities'],
            "confidence": result['confidence'],
            "interpretation": result['interpretation'],
            "input_features": result['input_features']
        })
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@prediction_bp.route("/features", methods=["GET"])
def get_features():
    """Get information about required and optional features for prediction"""
    return jsonify({
        "required_features": [
            {
                "name": "ph",
                "type": "float",
                "description": "pH level of water (6.5-8.5 is optimal)",
                "unit": "pH units"
            },
            {
                "name": "cases",
                "type": "int", 
                "description": "Number of disease cases in the area",
                "unit": "count"
            }
        ],
        "optional_features": [
            {
                "name": "tds",
                "type": "float",
                "description": "Total Dissolved Solids",
                "unit": "mg/L",
                "default": 414.0
            },
            {
                "name": "fluoride",
                "type": "float", 
                "description": "Fluoride content",
                "unit": "mg/L",
                "default": 0.35
            },
            {
                "name": "nitrate",
                "type": "float",
                "description": "Nitrate content", 
                "unit": "mg/L",
                "default": 13.0
            },
            {
                "name": "chloride",
                "type": "float",
                "description": "Chloride content",
                "unit": "mg/L", 
                "default": 50.0
            },
            {
                "name": "ec",
                "type": "float",
                "description": "Electrical Conductivity",
                "unit": "μS/cm",
                "default": 643.0
            }
        ],
        "risk_levels": [
            "No Risk",
            "Low Risk", 
            "Medium Risk",
            "High Risk"
        ]
    })
