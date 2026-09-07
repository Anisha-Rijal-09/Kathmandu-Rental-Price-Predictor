# Kathmandu Rental Price Predictor

## Project Overview
This project predicts monthly rental prices for houses, flats, and apartments in Kathmandu using machine learning. Listings were scraped from gharghaderi.com, cleaned and feature-engineered, then used to train a Random Forest regression model. The trained model is served through a FastAPI backend and deployed on Render, with a Streamlit app as the frontend for users to enter property details and get an instant rent estimate.

## Project Structure
```
├── models/                              # Saved trained pipeline + metadata
├── schema/                              # Pydantic request/response schemas for the API
├── datacleaningbefore.ipynb             # Initial data cleaning exploration
├── nepal_rental_main.ipynb              # Full pipeline: EDA, feature engineering, model training
├── nepal_rental_kathmandu_dataset.csv   # Scraped & cleaned dataset
├── scrape_gharghaderi.py                # Scraper for gharghaderi.com listings
├── app.py                               # FastAPI backend serving predictions
├── streamlit_app.py                     # Streamlit frontend
├── requirements.txt                     # Python dependencies
├── Dockerfile                           # Container definition
├── .dockerignore                        # Files excluded from Docker build
├── render.yaml                          # Render deployment config
└── .gitignore
```

## Dataset
- **Source:** Scraped from [gharghaderi.com](https://www.gharghaderi.com)
- **Scraper:** `scrape_gharghaderi.py`
- **Coverage:** Houses, flats, and apartments for rent in Kathmandu, Lalitpur, and Bhaktapur
- **File:** `nepal_rental_kathmandu_dataset.csv`
- **Raw columns:** listing ID, title, monthly rent (NPR), area, road width, location/ward/municipality/district, property type, house type, direction, bedrooms, bathrooms, living rooms, kitchens, total rooms, parking, built-up area, number of flats, built year, description, city, source
- **Cleaning steps:** dropped identifier/text-heavy columns (title, description, raw location fields), handled missing house type/direction/built year, converted built year to property age, parsed messy parking text into numeric parking spaces, and grouped rare localities into an "Other" bucket

## Installation
```bash
git clone https://github.com/Anisha-Rijal-09/Kathmandu-Rental-Price-Predictor.git
cd Kathmandu-Rental-Price-Predictor
pip install -r requirements.txt
```

## Run Locally
**Start the API:**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Start the frontend (in a separate terminal):**
```bash
streamlit run streamlit_app.py
```
> Set `API_URL` in `streamlit_app.py` to `http://127.0.0.1:8000/rental_prediction` when running locally.

## Run with Docker

**Build the image:**
```bash
docker build -t rental-price-api .
```

**Run the container:**
```bash
docker run -p 8000:8000 rental-price-api
```

**Or pull the pre-built image from Docker Hub:**
```bash
docker pull chickennugget09/rental-price-api
docker run -p 8000:8000 chickennugget09/rental-price-api
```

## Deployment
This project supports two deployment methods, both running the same FastAPI app:
1. **Render** (native Python) — configured via `render.yaml`, live at the URL below.
2. **Docker** — containerized via the included `Dockerfile`, image pushed to Docker Hub.

## API Usage

**Local API**
`http://127.0.0.1:8000`

**Live API**
`https://kathmandu-rental-price-predictor.onrender.com/`

**Swagger Documentation**
`https://kathmandu-rental-price-predictor.onrender.com/docs`

### Example Prediction
**Request:** `POST /rental_prediction`
```json
{
  "area_sqft_approx": 1200.0,
  "road_width_ft": 20.0,
  "bedrooms": 3.0,
  "bathrooms": 2.0,
  "living_rooms": 1.0,
  "kitchens": 1.0,
  "no_of_flats": 4.0,
  "property_age": 8.0,
  "parking_spaces": 2.0,
  "built_year_missing": 0,
  "ward": "10",
  "property_type": "house",
  "house_type": "Furnished",
  "direction": "North East",
  "city": "kathmandu",
  "location_locality_clean": "Bishalnagar"
}
```

**Response:**
```json
{
  "predicted_rent": 62000.0
}
```

## Results
The final model was evaluated on a held-out test set.

| Metric | Score |
|--------|------:|
| MAE | ₨55,414 |
| RMSE | ₨82,034 |
| R² | 0.4924 |

The final model explains approximately **49% of the variation in monthly rental prices**. Its predictions differ from the actual rent by about **₨55,000 on average**, as measured by MAE.

Random Forest performed better than the median baseline (`DummyRegressor`) and the other tested regression models during cross-validation, making it the strongest model among the approaches evaluated in this project.

The results also show that rental prices contain substantial variation that is not fully captured by the available features. More detailed location information, property condition, amenities, furnishing details, and other listing-specific characteristics could potentially improve future versions of the model.

## Model Persistence
The final model is saved as a single end-to-end pipeline:
```text
models/rent_prediction_pipeline.joblib
```

## Future Improvements
- Continue scraping over time to grow the dataset beyond the current ~150 listings, which is the main limiting factor on model accuracy
- Add richer features such as property condition, amenities, and furnishing details
- Automate weekly data collection and periodic model retraining
- Add CI/CD to auto-build and push the Docker image on every update

## Author
Built as a personal learning project to practice the full ML deployment lifecycle — scraping, modeling, API design, containerization, and deployment.
