# Apartment Price Prediction App

A Streamlit web application that predicts apartment prices based on various features.

## Features

- Downloads a trained machine learning model from Azure Blob Storage
- Allows users to input apartment details and characteristics
- Predicts apartment prices and price per square meter
- Provides a summary of selected apartment features

## Setup Instructions

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure Azure Storage credentials:
    - Create a `.streamlit/secrets.toml` file with your Azure Storage credentials:
   ```toml
   AZURE_STORAGE_CONNECTION_STRING = "Your Azure Storage connection string"
   AZURE_CONTAINER_NAME = "your_container_name"
   ```

3. Run the app:
   ```
   streamlit run app.py
   ```

## Required Model

The app expects a trained model named `predictor.pkl` in your Azure Storage container. The model should be capable of
predicting apartment prices based on the features listed in the application.

## Dataset Features

The model should be trained on data with the following features:

- City (e.g., Krakow, Warsaw)
- Apartment type (e.g., apartmentBuilding, tenement)
- Square meters
- Number of rooms
- Floor and total floor count
- Building year and age
- Geographic coordinates (latitude, longitude)
- Distance to city center and various amenities
- Property details (ownership type, building material, condition)
- Amenities (parking, balcony, elevator, security, storage)
