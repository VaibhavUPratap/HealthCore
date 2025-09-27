import pickle
import numpy as np
import pandas as pd

# Load trained health risk prediction model
try:
    with open('models/health_risk_prediction_model.pkl', 'rb') as f:
        model_package = pickle.load(f)
    
    model = model_package['model']
    scaler = model_package['scaler']
    feature_names = model_package['feature_names']
    classes = model_package['classes']
    
    print("Health risk prediction model loaded successfully")
    print(f"Model accuracy: {model_package['accuracy']:.4f}")
    print(f"Features: {feature_names}")
    print(f"Risk levels: {list(classes)}")
    
except FileNotFoundError:
    print("Model file 'health_risk_prediction_model.pkl' not found")
    print("Please ensure the model is trained and saved first")
    model = None

def predict_risk_level(input_data):
    """
    Predict health risk level based on input parameters
    
    Parameters:
    input_data (dict): Dictionary containing:
        - ph: pH level (required)
        - cases: Number of total cases (required)  
        - tds: Total Dissolved Solids (optional)
        - fluoride: Fluoride content (optional)
        - nitrate: Nitrate content (optional)
        - chloride: Chloride content (optional)
        - ec: Electrical Conductivity (optional)
        - temp: Temperature (not used in current model, included for compatibility)
    
    Returns:
    dict: Dictionary containing:
        - predicted_risk_level: Predicted risk level
        - probabilities: Probability for each risk level
        - confidence: Confidence score
        - input_features: Features used for prediction
    """
    
    if model is None:
        return {
            'error': 'Model not loaded. Please train and save the model first.',
            'predicted_risk_level': None,
            'probabilities': None,
            'confidence': None
        }
    
    try:
        # Extract required features
        ph = input_data.get('ph')
        cases = input_data.get('cases', input_data.get('total_cases', 0))
        
        if ph is None:
            raise ValueError("pH is required for prediction")
        
        # Create feature array with defaults for missing values
        # Features: ['pH', 'Total_Cases', 'TDS', 'F', 'NO3', 'Cl', 'EC in μS/cm']
        features = [
            ph,                                          # pH
            cases,                                       # Total_Cases
            input_data.get('tds', 414.0),               # TDS (median default)
            input_data.get('fluoride', 0.35),           # F (median default)
            input_data.get('nitrate', 13.0),            # NO3 (median default)
            input_data.get('chloride', 50.0),           # Cl (median default)
            input_data.get('ec', 643.0)                 # EC (median default)
        ]
        
        # Convert to numpy array and reshape for prediction
        feature_array = np.array(features).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(feature_array)[0]
        probabilities = model.predict_proba(feature_array)[0]
        
        # Create probability dictionary
        prob_dict = dict(zip(classes, probabilities))
        confidence = max(probabilities)
        
        return {
            'predicted_risk_level': prediction,
            'probabilities': prob_dict,
            'confidence': float(confidence),
            'input_features': dict(zip(feature_names, features)),
            'interpretation': _interpret_risk_level(prediction, confidence)
        }
        
    except Exception as e:
        return {
            'error': f'Prediction failed: {str(e)}',
            'predicted_risk_level': None,
            'probabilities': None,
            'confidence': None
        }

def _interpret_risk_level(risk_level, confidence):
    """Provide interpretation of the risk level prediction"""
    interpretations = {
        'No Risk': 'Water quality and health indicators suggest minimal risk. Conditions are within acceptable ranges.',
        'Low Risk': 'Some concerns identified. Preventive monitoring recommended.',
        'Medium Risk': 'Moderate risk detected. Intervention and closer monitoring advised.',
        'High Risk': 'Significant risk identified. Immediate action and investigation required.'
    }
    
    interpretation = interpretations.get(risk_level, 'Unknown risk level')
    confidence_text = f"Prediction confidence: {confidence:.1%}"
    
    return f"{interpretation} {confidence_text}"

def predict_outbreak(input_data):
    """
    Legacy function for backward compatibility
    Maps to the new risk prediction function
    """
    result = predict_risk_level(input_data)
    
    if result.get('error'):
        return result['error']
    
    # Map risk levels to numerical values for backward compatibility
    risk_mapping = {
        'No Risk': 0,
        'Low Risk': 1,
        'Medium Risk': 2,
        'High Risk': 3
    }
    
    return risk_mapping.get(result['predicted_risk_level'], -1)

# Example usage and testing
if __name__ == "__main__":
    print("Health Risk Prediction Model - Testing")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            'name': 'Normal conditions',
            'data': {'ph': 7.2, 'cases': 0}
        },
        {
            'name': 'High cases',
            'data': {'ph': 7.0, 'cases': 50, 'tds': 800}
        },
        {
            'name': 'Extreme pH',
            'data': {'ph': 10.5, 'cases': 5, 'fluoride': 2.5}
        },
        {
            'name': 'Multiple risk factors',
            'data': {'ph': 6.0, 'cases': 25, 'tds': 1200, 'nitrate': 60}
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"Input: {test_case['data']}")
        
        result = predict_risk_level(test_case['data'])
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        else:
            print(f"Risk Level: {result['predicted_risk_level']}")
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Interpretation: {result['interpretation']}")
            
        print("-" * 30)
