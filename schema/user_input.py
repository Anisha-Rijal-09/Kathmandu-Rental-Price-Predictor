from pydantic import BaseModel,Field, field_validator
from typing import Annotated,Literal

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


    @field_validator("property_type", mode="before")
    @classmethod
    def normalize_property_type(cls, v: str) -> str:
      return v.strip().lower()


    @field_validator("house_type", mode="before")
    @classmethod
    def normalize_house_type(cls, v: str) -> str:
      return v.strip().title()


    @field_validator("city", mode="before")
    @classmethod
    def normalize_city(cls, v: str) -> str:
      return v.strip().lower()
