"""Feature contract shared by the trainer and online inference service."""

FEATURE_FIELDS = [
    "amount_clp",
    "amount_vs_baseline",
    "tx_count_card",
    "minutes_since_last_tx",
    "channel",
    "mcc",
    "city_changed",
]
CATEGORICAL_FIELDS = ["channel", "mcc"]
TARGET_FIELD = "label_fraud"
TIMESTAMP_FIELD = "timestamp"


def validate_features(features: dict) -> dict:
    missing = [field for field in FEATURE_FIELDS if field not in features]
    if missing:
        raise ValueError(f"missing required features: {', '.join(missing)}")

    normalized = {}
    for field in FEATURE_FIELDS:
        value = features[field]
        if field in CATEGORICAL_FIELDS:
            normalized[field] = str(value)
        elif field == "city_changed":
            normalized[field] = int(bool(value))
        else:
            number = float(value)
            if number != number or number in (float("inf"), float("-inf")):
                raise ValueError(f"{field} must be finite")
            normalized[field] = number
    if normalized["amount_clp"] < 0:
        raise ValueError("amount_clp cannot be negative")
    if normalized["amount_vs_baseline"] < 0:
        raise ValueError("amount_vs_baseline cannot be negative")
    if normalized["tx_count_card"] < 0 or normalized["minutes_since_last_tx"] < 0:
        raise ValueError("transaction history features cannot be negative")
    return normalized
