import streamlit as st


def get_user_inputs():
    """
    Pobiera dane wejściowe od użytkownika za pomocą paska bocznego Streamlit.

    Returns:
        dict: Słownik z danymi wejściowymi użytkownika.
    """
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

    inputs = {
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
    }

    return inputs
