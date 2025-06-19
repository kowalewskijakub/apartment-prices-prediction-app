import pandas as pd

from feature_utils import normalize_feature

MODEL_COLUMNS = [
    'city', 'type', 'squareMeters', 'rooms', 'floor', 'floorCount',
    'buildYear', 'latitude', 'longitude', 'centreDistance', 'poiCount',
    'schoolDistance', 'clinicDistance', 'postOfficeDistance',
    'kindergartenDistance', 'restaurantDistance', 'collegeDistance',
    'pharmacyDistance', 'ownership', 'buildingMaterial', 'condition',
    'hasParkingSpace', 'hasBalcony', 'hasElevator', 'hasSecurity',
    'hasStorageRoom', 'month', 'year', 'age', 'floor_ratio'
]


def prepare_input_data(inputs, normalization_ranges):
    """
    Przygotowuje dane wejściowe do predykcji, normalizując cechy i dodając cechy pochodne.

    Args:
        inputs (dict): Słownik z danymi wejściowymi.
        normalization_ranges (dict): Słownik z zakresami normalizacji.

    Returns:
        pd.DataFrame: DataFrame z danymi gotowymi do predykcji.
    """
    age = inputs['year'] - inputs['buildYear']
    floor_ratio = inputs['floor'] / inputs['floorCount'] if inputs['floorCount'] > 0 else 0

    features_to_normalize = [
        'squareMeters', 'rooms', 'centreDistance', 'poiCount', 'schoolDistance',
        'clinicDistance', 'postOfficeDistance', 'kindergartenDistance',
        'restaurantDistance', 'collegeDistance', 'pharmacyDistance', 'age'
    ]

    feature_data = {}
    for key, value in inputs.items():
        if key in features_to_normalize:
            feature_data[key] = normalize_feature(value, key)
        else:
            feature_data[key] = float(value) if key in ['floor', 'floorCount', 'buildYear', 'month', 'year'] else value

    feature_data['age'] = normalize_feature(age, 'age')
    feature_data['floor_ratio'] = floor_ratio

    input_df = pd.DataFrame([feature_data], columns=MODEL_COLUMNS)
    return input_df


def make_prediction(model, input_df):
    """
    Dokonuje predykcji za pomocą modelu i zwraca wynik.

    Args:
        model (TabularPredictor): Wczytany model.
        input_df (pd.DataFrame): DataFrame z danymi wejściowymi.

    Returns:
        float: Przewidywana cena mieszkania.
    """
    prediction = model.predict(input_df)
    return prediction[0]
