from fastapi import FastAPI
from schema.user_input import ModelInput
import joblib
import pandas as pd

app = FastAPI(title="Kathmandu Rental Price Prediction API")

# Load trained ML pipeline
model = joblib.load("models/rent_prediction_pipeline.joblib")


# Home 
@app.get("/")
def home():
    return {
        "message": "Kathmandu Rental Price Prediction API is running!"
    }
# health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "OK",
        "model_status": "Loaded" if model else "Not Loaded"
    }

# Rental prediction
@app.post("/rental_prediction")
def predict(data: ModelInput):

    # Convert API input to DataFrame
    input_data = pd.DataFrame([data.model_dump()])

    # Make prediction
    prediction = model.predict(input_data)

    return {
        "predicted_rent": float(prediction[0]),
        "message": "Rent predicted successfully"
    }


