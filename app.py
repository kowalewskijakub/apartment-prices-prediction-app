import streamlit as st
import pandas as pd
import numpy as np
import pickle
import io
import os
import tempfile
import shutil
import zipfile

from autogluon.tabular import TabularPredictor
from azure.storage.blob import BlobServiceClient, ContainerClient

# Set page title and configuration
st.set_page_config(page_title="Apartment Price Predictor", layout="wide")
st.title("Apartment Price Prediction App")


# --- Azure Blob Storage Model Loading ---
@st.cache_resource
def download_model_from_azure():
    """Downloads and caches the model from Azure Blob Storage."""
    try:
        connection_string = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = st.secrets["AZURE_CONTAINER_NAME"]
        model_folder = "autogluon"

        # Create a temporary directory to store the model
        temp_dir = tempfile.mkdtemp()
        model_dir = os.path.join(temp_dir, model_folder)
        os.makedirs(model_dir, exist_ok=True)

        # Connect to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # List all blobs with the model_folder prefix
        blobs_list = list(container_client.list_blobs(name_starts_with=model_folder))
        total_files = len(blobs_list)

        # Initialize progress bar
        progress_bar = st.progress(0)

        # Download each file in the model folder
        for index, blob in enumerate(blobs_list):
            # Get the relative path within the model folder
            relative_path = blob.name[len(model_folder):].lstrip('/')
            if not relative_path:  # Skip the directory itself
                continue

            # Create local directory structure if needed
            local_path = os.path.join(model_dir, relative_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Download the blob to the local path
            blob_client = container_client.get_blob_client(blob.name)
            with open(local_path, "wb") as file:
                file.write(blob_client.download_blob().readall())

            # Update progress bar
            progress_bar.progress(int((index + 1) * 100 / total_files))

        # Import AutoGluon here to avoid loading it unnecessarily

        # Load the model using AutoGluon's API
        model = TabularPredictor.load(
            model_dir,
            require_version_match = False
        )

        st.success("Model successfully loaded from Azure Storage!")
        return model
    except Exception as e:
        st.error(f"Error downloading model: {str(e)}")
        return None


# Load the model
model = download_model_from_azure()

# --- Feature Normalization Ranges ---
# These values must match those used during model training
normalization_ranges = {
    'squareMeters': (10.0, 500.0),
    'rooms': (1.0, 10.0),
    'floor': (0.0, 50.0),
    'floorCount': (1.0, 50.0),
    'buildYear': (1900, 2030),
    'latitude': (49.0, 55.0),
    'longitude': (14.0, 24.0),
    'centreDistance': (0.0, 30.0),
    'poiCount': (0.0, 100.0),
    'schoolDistance': (0.0, 10.0),
    'clinicDistance': (0.0, 10.0),
    'postOfficeDistance': (0.0, 10.0),
    'kindergartenDistance': (0.0, 10.0),
    'restaurantDistance': (0.0, 10.0),
    'collegeDistance': (0.0, 10.0),
    'pharmacyDistance': (0.0, 10.0),
    'month': (1, 12),
    'year': (2023, 2030),
    'age': (0, 150),
}


def normalize_feature(value, feature_name):
    """Normalizes a feature using Min-Max scaling."""
    if feature_name in normalization_ranges:
        min_val, max_val = normalization_ranges[feature_name]
        if max_val > min_val:
            return (value - min_val) / (max_val - min_val)
    return value


# --- Sidebar for User Inputs ---
st.sidebar.header("Apartment Features")

city = st.sidebar.selectbox("City", ["krakow", "warszawa", "wroclaw", "poznan", "gdansk", "katowice", "lublin"])
apt_type = st.sidebar.selectbox("Apartment Type", ["blockOfFlats", "tenement", "apartmentBuilding", "loft"])
sqm = st.sidebar.number_input("Square Meters", min_value=10.0, max_value=500.0, value=50.0)
rooms = st.sidebar.number_input("Number of Rooms", min_value=1.0, max_value=10.0, value=2.0)
floor = st.sidebar.number_input("Floor", min_value=0.0, max_value=50.0, value=2.0)
floor_count = st.sidebar.number_input("Total Floors in Building", min_value=1.0, max_value=50.0, value=5.0)
build_year = st.sidebar.number_input("Building Year", min_value=1900, max_value=2024, value=2000)

with st.sidebar.expander("Location Details"):
    latitude = st.number_input("Latitude", min_value=49.0, max_value=55.0, value=50.06, format="%.4f")
    longitude = st.number_input("Longitude", min_value=14.0, max_value=24.0, value=19.94, format="%.4f")
    centre_distance = st.number_input("Distance to City Center (km)", min_value=0.0, max_value=30.0, value=3.0)
    poi_count = st.number_input("Points of Interest Count", min_value=0.0, max_value=100.0, value=10.0)

with st.sidebar.expander("Distance to Amenities (km)"):
    school_distance = st.number_input("School Distance", min_value=0.0, max_value=10.0, value=0.5)
    clinic_distance = st.number_input("Clinic Distance", min_value=0.0, max_value=10.0, value=0.5)
    post_office_distance = st.number_input("Post Office Distance", min_value=0.0, max_value=10.0, value=0.5)
    kindergarten_distance = st.number_input("Kindergarten Distance", min_value=0.0, max_value=10.0, value=0.5)
    restaurant_distance = st.number_input("Restaurant Distance", min_value=0.0, max_value=10.0, value=0.5)
    college_distance = st.number_input("College Distance", min_value=0.0, max_value=10.0, value=1.0)
    pharmacy_distance = st.number_input("Pharmacy Distance", min_value=0.0, max_value=10.0, value=0.5)

with st.sidebar.expander("Property Details"):
    ownership = st.sidebar.selectbox("Ownership Type", ["condominium", "cooperative", "fullOwnership"])
    building_material = st.sidebar.selectbox("Building Material",
                                             ["brick", "concreteSlab", "concrete", "wood", "other"])
    condition = st.sidebar.selectbox("Condition", ["premium", "good", "low"])

with st.sidebar.expander("Additional Features"):
    has_parking = st.checkbox("Has Parking Space", value=True)
    has_balcony = st.checkbox("Has Balcony", value=True)
    has_elevator = st.checkbox("Has Elevator")
    has_security = st.checkbox("Has Security")
    has_storage = st.checkbox("Has Storage Room")

current_month = st.sidebar.number_input("Current Month", min_value=1, max_value=12, value=6)
current_year = st.sidebar.number_input("Current Year", min_value=2023, max_value=2030, value=2024)

# --- Derived Features ---
age = current_year - build_year
floor_ratio = floor / floor_count if floor_count > 0 else 0

# --- Prediction Logic ---
st.header("Price Prediction")

if st.button("Predict Price"):
    if model is not None:
        try:
            # This data dictionary MUST match the feature structure of the model's training data.
            # Columns like 'id' and the target variable ('price' or 'price_per_m2') should be excluded.
            feature_data = {
                'city': city,
                'type': apt_type,
                'squareMeters': normalize_feature(sqm, 'squareMeters'),
                'rooms': normalize_feature(rooms, 'rooms'),
                'floor': float(floor),
                'floorCount': float(floor_count),
                'buildYear': float(build_year),
                'latitude': latitude,
                'longitude': longitude,
                'centreDistance': normalize_feature(centre_distance, 'centreDistance'),
                'poiCount': normalize_feature(poi_count, 'poiCount'),
                'schoolDistance': normalize_feature(school_distance, 'schoolDistance'),
                'clinicDistance': normalize_feature(clinic_distance, 'clinicDistance'),
                'postOfficeDistance': normalize_feature(post_office_distance, 'postOfficeDistance'),
                'kindergartenDistance': normalize_feature(kindergarten_distance, 'kindergartenDistance'),
                'restaurantDistance': normalize_feature(restaurant_distance, 'restaurantDistance'),
                'collegeDistance': normalize_feature(college_distance, 'collegeDistance'),
                'pharmacyDistance': normalize_feature(pharmacy_distance, 'pharmacyDistance'),
                'ownership': ownership,
                'buildingMaterial': building_material,
                'condition': condition,
                'hasParkingSpace': 'yes' if has_parking else 'no',
                'hasBalcony': 'yes' if has_balcony else 'no',
                'hasElevator': 'yes' if has_elevator else 'no',
                'hasSecurity': 'yes' if has_security else 'no',
                'hasStorageRoom': 'yes' if has_storage else 'no',
                'month': float(current_month),
                'year': float(current_year),
                'age': normalize_feature(age, 'age'),
                'floor_ratio': floor_ratio
            }

            # Define the exact order of columns your model expects
            model_columns = [
                'city', 'type', 'squareMeters', 'rooms', 'floor', 'floorCount',
                'buildYear', 'latitude', 'longitude', 'centreDistance', 'poiCount',
                'schoolDistance', 'clinicDistance', 'postOfficeDistance',
                'kindergartenDistance', 'restaurantDistance', 'collegeDistance',
                'pharmacyDistance', 'ownership', 'buildingMaterial', 'condition',
                'hasParkingSpace', 'hasBalcony', 'hasElevator', 'hasSecurity',
                'hasStorageRoom', 'month', 'year', 'age', 'floor_ratio'
            ]

            # Create a DataFrame with the correct column order
            input_df = pd.DataFrame([feature_data], columns=model_columns)

            with st.expander("Debug: See Model Input"):
                st.dataframe(input_df)

            # Make prediction
            prediction = model.predict(input_df)

            # Display prediction
            st.subheader("Predicted Apartment Price:")
            price_str = f"<h1 style='text-align: center; color: #2E86C1;'>{int(prediction[0]):,} PLN</h1>"
            st.markdown(price_str, unsafe_allow_html=True)

            st.subheader("Predicted Price per Square Meter:")
            price_per_m2 = prediction[0] / sqm
            price_per_m2_str = f"<h2 style='text-align: center; color: #28B463;'>{int(price_per_m2):,} PLN/m²</h2>"
            st.markdown(price_per_m2_str, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")
            st.exception(e)  # Provides a full traceback for debugging
    else:
        st.error("Model is not loaded. Cannot make a prediction.")
