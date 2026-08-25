from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import json
import pandas as pd

app=FastAPI(title="Kathmandu Rental Price Prediction API")



# input features expected by the model
class model_input(BaseModel):
    
    area_sqft_approx: float
    road_width_ft: float
    bedrooms: float
    bathrooms: float
    living_rooms: float
    kitchens: float
    no_of_flats: float
    property_age: float
    parking_spaces: float
    built_year_missing: float

    ward: str
    property_type: str
    house_type: str
    direction: str
    city: str
    location_locality_clean: str


# Load trained ML pipeline
model = joblib.load("models/rent_prediction_pipeline.joblib")

@app.get("/")
def home():
    return {
        "message": "Kathmandu Rental Price Prediction API is running!"
    }


@app.post('/rental_prediction')
def predict(data:model_input):
    

     # Convert API input to DataFrame
    input_data = pd.DataFrame([data.model_dump()])

    # Make prediction
    prediction = model.predict(input_data)

    return {
        "predicted_rent": float(prediction[0])
    }



