import numpy as np
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


def prepare_input_data(inputs: dict) -> pd.DataFrame:
    input_df = pd.DataFrame([inputs])

    input_df['year'] = pd.to_numeric(input_df['year'], errors='coerce')
    input_df['buildYear'] = pd.to_numeric(input_df['buildYear'], errors='coerce')
    input_df['floor'] = pd.to_numeric(input_df['floor'], errors='coerce')
    input_df['floorCount'] = pd.to_numeric(input_df['floorCount'], errors='coerce')

    input_df['age'] = input_df['year'] - input_df['buildYear']
    input_df.loc[(input_df['age'] < 0) | (input_df['age'] > 200), 'age'] = np.nan
    input_df['age'] = input_df['age'].fillna(30)  # Using a reasonable default for imputation

    input_df['floor_ratio'] = (input_df['floor'] / input_df['floorCount']).replace([np.inf, -np.inf], np.nan).fillna(0)

    columns_to_exclude = [
        'buildYear', 'price', 'year', 'month', 'latitude', 'longitude',
        'floor', 'floorCount', 'floor_ratio'
    ]
    numeric_cols = input_df.select_dtypes(include=np.number).columns.tolist()
    columns_to_normalize = [col for col in numeric_cols if col not in columns_to_exclude]

    for col in columns_to_normalize:
        input_df[col] = normalize_feature(input_df[col].iloc[0], col)

    for col in MODEL_COLUMNS:
        if col not in input_df.columns:
            input_df[col] = 0

    return input_df[MODEL_COLUMNS]


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
    return prediction.iloc[0]
