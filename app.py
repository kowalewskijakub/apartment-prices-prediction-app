import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import io

from azure.storage.blob import BlobServiceClient

# Set page title and configuration
st.set_page_config(page_title="Apartment Price Predictor", layout="wide")
st.title("Apartment Price Prediction App")

# Azure Storage settings
@st.cache_resource
def download_model_from_azure():
    try:
        # These should be stored in environment variables or secrets in production
        connection_string = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = st.secrets["AZURE_CONTAINER_NAME"]
        blob_name = "predictor.pkl"

        # Create the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Get the blob client
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Download the blob
        blob_data = blob_client.download_blob().readall()

        # Load the model from the downloaded data
        model = pickle.loads(blob_data)

        st.success("Model successfully loaded from Azure Storage!")
        return model
    except Exception as e:
        st.error(f"Error downloading model: {str(e)}")
        return None

# Try to load the model
model = download_model_from_azure()

# Sidebar for inputs
st.sidebar.header("Apartment Features")

# City selection
city = st.sidebar.selectbox("City", ["krakow", "warszawa", "wroclaw", "poznan", "gdansk"])

# Apartment type
apt_type = st.sidebar.selectbox("Apartment Type", ["apartmentBuilding", "tenement", "blockOfFlats", "loft"])

# Basic features
sqm = st.sidebar.number_input("Square Meters", min_value=10.0, max_value=500.0, value=50.0, step=1.0)
rooms = st.sidebar.number_input("Number of Rooms", min_value=1.0, max_value=10.0, value=2.0, step=1.0)
floor = st.sidebar.number_input("Floor", min_value=0.0, max_value=50.0, value=2.0, step=1.0)
floor_count = st.sidebar.number_input("Total Floors in Building", min_value=1.0, max_value=50.0, value=5.0, step=1.0)
build_year = st.sidebar.number_input("Building Year", min_value=1900, max_value=2023, value=2000, step=1)

# Location features
with st.sidebar.expander("Location Details"):
    latitude = st.number_input("Latitude", min_value=49.0, max_value=55.0, value=50.0, step=0.01)
    longitude = st.number_input("Longitude", min_value=14.0, max_value=24.0, value=20.0, step=0.01)
    centre_distance = st.number_input("Distance to City Center (km)", min_value=0.0, max_value=30.0, value=3.0, step=0.1)
    poi_count = st.number_input("Points of Interest Count", min_value=0.0, max_value=100.0, value=10.0, step=1.0)

# Distance features
with st.sidebar.expander("Distance to Amenities (km)"):
    school_distance = st.number_input("School Distance", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
    clinic_distance = st.number_input("Clinic Distance", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
    post_office_distance = st.number_input("Post Office Distance", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
    kindergarten_distance = st.number_input("Kindergarten Distance", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
    restaurant_distance = st.number_input("Restaurant Distance", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
    college_distance = st.number_input("College Distance", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    pharmacy_distance = st.number_input("Pharmacy Distance", min_value=0.0, max_value=10.0, value=0.5, step=0.1)

# Categorical features
with st.sidebar.expander("Property Details"):
    ownership = st.selectbox("Ownership Type", ["condominium", "cooperative", "fullOwnership"])
    building_material = st.selectbox("Building Material", ["brick", "concrete", "wood", "other"])
    condition = st.selectbox("Condition", ["basic", "good", "premium"])

# Boolean features
with st.sidebar.expander("Additional Features"):
    has_parking = st.checkbox("Has Parking Space")
    has_balcony = st.checkbox("Has Balcony")
    has_elevator = st.checkbox("Has Elevator")
    has_security = st.checkbox("Has Security")
    has_storage = st.checkbox("Has Storage Room")

# Current date for age calculation
current_month = st.sidebar.number_input("Current Month (1-12)", min_value=1, max_value=12, value=8, step=1)
current_year = st.sidebar.number_input("Current Year", min_value=2023, max_value=2030, value=2023, step=1)

# Calculate derived features
age = current_year - build_year
floor_ratio = floor / floor_count if floor_count > 0 else 0

# Prediction section
st.header("Price Prediction")

if st.button("Predict Price"):
    if model is not None:
        # Create a dataframe with the input values
        data = {
            'id': 0,  # Add dummy ID as required by the model
            'city': city,
            'type': apt_type,
            'squareMeters': sqm,
            'rooms': rooms,
            'floor': floor,
            'floorCount': floor_count,
            'buildYear': build_year,
            'latitude': latitude,
            'longitude': longitude,
            'centreDistance': centre_distance,
            'poiCount': poi_count,
            'schoolDistance': school_distance,
            'clinicDistance': clinic_distance,
            'postOfficeDistance': post_office_distance,
            'kindergartenDistance': kindergarten_distance,
            'restaurantDistance': restaurant_distance,
            'collegeDistance': college_distance,
            'pharmacyDistance': pharmacy_distance,
            'ownership': ownership,
            'buildingMaterial': building_material,
            'condition': condition,
            'hasParkingSpace': 'yes' if has_parking else 'no',
            'hasBalcony': 'yes' if has_balcony else 'no',
            'hasElevator': 'yes' if has_elevator else 'no',
            'hasSecurity': 'yes' if has_security else 'no',
            'hasStorageRoom': 'yes' if has_storage else 'no',
            'month': current_month,
            'year': current_year,
            'age': age,
            'floor_ratio': floor_ratio,
            'price_per_m2': 10000  # Add placeholder value as required by the model
        }

        # Create a DataFrame for prediction
        input_df = pd.DataFrame([data])

        try:
            # Make prediction
            prediction = model.predict(input_df)

            # Display prediction results
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Predicted Price:")
                st.markdown(f"<h1 style='color: #1E88E5;'>{int(prediction[0]):,} PLN</h1>", unsafe_allow_html=True)

            with col2:
                st.subheader("Price per m²:")
                price_per_m2 = prediction[0] / sqm
                st.markdown(f"<h1 style='color: #1E88E5;'>{int(price_per_m2):,} PLN/m²</h1>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")
    else:
        st.error("Failed to load the model. Please check your Azure Storage configuration.")

# Display apartment summary
with st.expander("Apartment Summary"):
    st.write(f"A {sqm}m² {apt_type} in {city} with {int(rooms)} rooms")
    st.write(f"Building year: {build_year} (Age: {age} years)")
    st.write(f"Floor: {int(floor)} out of {int(floor_count)} (Ratio: {floor_ratio:.2f})")
    st.write(f"Condition: {condition}")
    
    # Create two columns for features
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Amenities")
        st.write(f"✓ Parking" if has_parking else "✗ No Parking")
        st.write(f"✓ Balcony" if has_balcony else "✗ No Balcony")
        st.write(f"✓ Elevator" if has_elevator else "✗ No Elevator")
        st.write(f"✓ Security" if has_security else "✗ No Security")
        st.write(f"✓ Storage Room" if has_storage else "✗ No Storage Room")
    
    with col2:
        st.subheader("Location")
        st.write(f"Distance to center: {centre_distance} km")
        st.write(f"POI count: {int(poi_count)}")

