from fastapi import FastAPI
from pydantic import BaseModel,Field

import joblib
import pandas as pd
from typing import Annotated,Literal

app = FastAPI(title="Kathmandu Rental Price Prediction API")


# Input features expected by the model
class ModelInput(BaseModel):
    area_sqft_approx: Annotated[float, Field(..., description="Approximate area of the property in square feet",examples=[1200])]

    road_width_ft: Annotated[float, Field(..., description="Width of the road in front of the property in feet",examples=[20])]

    bedrooms: Annotated[float, Field(..., description="Number of bedrooms in the property",examples=[3])]

    bathrooms: Annotated[float, Field(..., description="Number of bathrooms in the property")]

    living_rooms: Annotated[float, Field(..., description="Number of living rooms in the property")]

    kitchens: Annotated[float, Field(..., description="Number of kitchens in the property")]

    no_of_flats: Annotated[float, Field(..., description="Number of flats in the building")]

    property_age: Annotated[float, Field(..., description="Age of the property in years")]

    parking_spaces: Annotated[float, Field(..., description="Number of parking spaces available")]

    built_year_missing: Annotated[float, Field(..., description="Indicates whether the built year is missing")]

    ward: Annotated[str, Field(..., description="Ward number of the property")]
    property_type: Annotated[Literal["house", "apartments", "flats"], Field(..., description="Type of property")]

    house_type: Annotated[Literal[ "Furnished", "Residential", "Commercial", "Bungalow", "Choose Type", "Semi-commercial", "Non-Furnished", "Semi-furnished" ], Field(..., description="Type of house")]

    direction: Annotated[str, Field(..., description="Direction or facing of the property",examples=["North East"])]
    city: Annotated[Literal[ "kathmandu", "bhaktapur", "lalitpur" ], Field(..., description="City where the property is located")]

    location_locality_clean: Annotated[str, Field(..., description="Cleaned locality name of the property")]



# Load trained ML pipeline
model = joblib.load("models/rent_prediction_pipeline.joblib")


# Home / health check
@app.get("/")
def home():
    return {
        "message": "Kathmandu Rental Price Prediction API is running!"
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
    
