import joblib

# Load trained ML model
model = joblib.load("models/saved_model.pkl")

def predict_outbreak(input_data):
    # input_data should be dict or list of features
    features = [input_data['temp'], input_data['ph'], input_data['cases']]
    prediction = model.predict([features])
    return prediction[0]
