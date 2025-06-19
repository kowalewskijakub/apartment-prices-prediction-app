from config import NORMALIZATION_RANGES


def normalize_feature(value, feature_name):
    """
    Normalizuje cechę za pomocą skalowania Min-Max.

    Args:
        value (float): Wartość cechy do znormalizowania.
        feature_name (str): Nazwa cechy.

    Returns:
        float: Znormalizowana wartość cechy.
    """
    if feature_name in NORMALIZATION_RANGES:
        min_val, max_val = NORMALIZATION_RANGES[feature_name]
        if max_val > min_val:
            return (value - min_val) / (max_val - min_val)
    return value
