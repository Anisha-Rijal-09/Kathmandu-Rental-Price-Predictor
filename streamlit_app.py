import streamlit as st
import requests

st.set_page_config(
    page_title="Kathmandu Rental Price Predictor",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Kathmandu Rental Price Predictor")
st.write("Enter the property details to predict the monthly rental price.")

# Your deployed FastAPI URL
API_URL = "https://kathmandu-rental-price-predictor.onrender.com/rental_prediction"



with st.form("rental_form"):

    st.subheader("Property Details")

    area_sqft_approx = st.number_input(
        "Area (sq ft)",
        min_value=1.0,
        value=1200.0
    )

    road_width_ft = st.number_input(
        "Road Width (ft)",
        min_value=1.0,
        value=20.0
    )

    bedrooms = st.number_input(
        "Bedrooms",
        min_value=0.0,
        value=3.0,
        step=1.0
    )

    bathrooms = st.number_input(
        "Bathrooms",
        min_value=0.0,
        value=2.0,
        step=1.0
    )

    living_rooms = st.number_input(
        "Living Rooms",
        min_value=0.0,
        value=1.0,
        step=1.0
    )

    kitchens = st.number_input(
        "Kitchens",
        min_value=0.0,
        value=1.0,
        step=1.0
    )

    no_of_flats = st.number_input(
        "Number of Flats",
        min_value=0.0,
        value=4.0,
        step=1.0
    )

    property_age = st.number_input(
        "Property Age (years)",
        min_value=0.0,
        value=8.0
    )

    parking_spaces = st.number_input(
        "Parking Spaces",
        min_value=0.0,
        value=2.0,
        step=1.0
    )

    built_year_missing = st.selectbox(
        "Built Year Missing?",
        options=[0, 1],
        format_func=lambda x: "No" if x == 0 else "Yes"
    )

    st.subheader("Location & Property Type")

    ward = st.text_input(
        "Ward",
        value="10"
    )

    property_type = st.selectbox(
        "Property Type",
        ["house", "apartments", "flats"]
    )

    house_type = st.selectbox(
        "House Type",
        [
            "Furnished",
            "Residential",
            "Commercial",
            "Bungalow",
            "Choose Type",
            "Semi-commercial",
            "Non-Furnished",
            "Semi-furnished"
        ]
    )

    direction = st.text_input(
        "Direction",
        value="North East"
    )

    city = st.selectbox(
        "City",
        ["kathmandu", "bhaktapur", "lalitpur"]
    )

    location_locality_clean = st.text_input(
        "Locality",
        value="Bishalnagar"
    )

    submitted = st.form_submit_button(
        "🔮 Predict Rent"
    )


if submitted:

    payload = {
        "area_sqft_approx": area_sqft_approx,
        "road_width_ft": road_width_ft,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "living_rooms": living_rooms,
        "kitchens": kitchens,
        "no_of_flats": no_of_flats,
        "property_age": property_age,
        "parking_spaces": parking_spaces,
        "built_year_missing": built_year_missing,
        "ward": ward,
        "property_type": property_type,
        "house_type": house_type,
        "direction": direction,
        "city": city,
        "location_locality_clean": location_locality_clean
    }

    try:
        with st.spinner("Predicting rent..."):

            response = requests.post(
                API_URL,
                json=payload,
                timeout=120
            )

        if response.status_code == 200:

            result = response.json()

            predicted_rent = result["predicted_rent"]

            st.success("Rent predicted successfully! 🎉")

            st.metric(
                label="Predicted Monthly Rent",
                value=f"Rs. {predicted_rent:,.0f}"
            )

        else:

            st.error(
                f"API Error: {response.status_code}"
            )

            st.json(response.json())

    except requests.exceptions.RequestException as e:

        st.error(
            f"Could not connect to the FastAPI server: {e}"
        )
