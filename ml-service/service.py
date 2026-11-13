"""Local/private HTTP inference service for an approved CatBoost artifact."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from catboost import CatBoostClassifier, Pool

from features import CATEGORICAL_FIELDS, FEATURE_FIELDS, validate_features


ROOT = Path(__file__).parent
MODEL_PATH = Path(os.getenv("SHIELDGUARD_MODEL", ROOT / "artifacts" / "catboost.cbm"))
METADATA_PATH = Path(os.getenv("SHIELDGUARD_MODEL_METADATA", ROOT / "artifacts" / "metadata.json"))
HOST = os.getenv("SHIELDGUARD_ML_ADDR", "127.0.0.1")
PORT = int(os.getenv("SHIELDGUARD_ML_PORT", "8090"))
MODEL = CatBoostClassifier()
METADATA = {}


def load_artifact() -> None:
    if not MODEL_PATH.is_file() or not METADATA_PATH.is_file():
        raise RuntimeError("model artifact or metadata not found; run train.py first")
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    if metadata.get("features") != FEATURE_FIELDS:
        raise RuntimeError("model feature contract does not match the service")
    MODEL.load_model(str(MODEL_PATH))
    METADATA.update(metadata)


def reason_codes(features: dict) -> list[str]:
    reasons = []
    if features["amount_vs_baseline"] >= 2.5:
        reasons.append("amount_above_customer_baseline")
    if features["channel"] == "ECOMMERCE_CNP":
        reasons.append("card_not_present_channel")
    if features["mcc"] in {"5732", "5094", "7995"}:
        reasons.append("sensitive_merchant_category")
    if features["city_changed"] and features["minutes_since_last_tx"] < 45:
        reasons.append("rapid_location_change")
    if features["tx_count_card"] >= 55:
        reasons.append("high_card_transaction_count")
    return reasons


class Handler(BaseHTTPRequestHandler):
    server_version = "ShieldGuardML/0.1"

    def _json(self, status: int, body: dict) -> None:
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "UP", "modelVersion": METADATA["model_version"], "modelScope": METADATA["model_scope"]})
            return
        if self.path == "/internal/v1/model-info":
            self._json(200, {
                "modelVersion": METADATA["model_version"],
                "modelScope": METADATA["model_scope"],
                "probabilityCalibrated": METADATA.get("probability_calibrated", False),
                "features": FEATURE_FIELDS,
                "evaluation": METADATA.get("evaluation", {}),
            })
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/internal/v1/predict":
            self._json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 32768:
                raise ValueError("request body size must be between 1 and 32768 bytes")
            payload = json.loads(self.rfile.read(length))
            features = validate_features(payload.get("features", {}))
            matrix = [[features[field] for field in FEATURE_FIELDS]]
            categorical_indices = [FEATURE_FIELDS.index(name) for name in CATEGORICAL_FIELDS]
            probability = float(MODEL.predict_proba(Pool(matrix, cat_features=categorical_indices))[0][1])
            self._json(200, {
                "experimentalScore": round(probability * 100, 1),
                "modelVersion": METADATA["model_version"],
                "modelScope": METADATA["model_scope"],
                "probabilityCalibrated": bool(METADATA.get("probability_calibrated", False)),
                "reasonCodes": reason_codes(features),
            })
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._json(400, {"error": "invalid_request", "message": str(error)})
        except Exception:
            self._json(503, {"error": "inference_failed"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def main() -> None:
    load_artifact()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"ShieldGuardAI ML service listening on http://{HOST}:{PORT}")
    print(f"Loaded {METADATA['model_version']} (scope={METADATA['model_scope']})")
    server.serve_forever()


if __name__ == "__main__":
    main()
