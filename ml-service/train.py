"""Train and evaluate a CatBoost baseline using a temporal holdout."""

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from catboost import CatBoostClassifier

from features import CATEGORICAL_FIELDS, FEATURE_FIELDS, TARGET_FIELD, TIMESTAMP_FIELD


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        required = {TIMESTAMP_FIELD, *FEATURE_FIELDS, TARGET_FIELD}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"dataset is missing columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    if len(rows) < 100:
        raise ValueError("at least 100 labelled rows are required")
    for row in rows:
        row[TIMESTAMP_FIELD] = datetime.fromisoformat(row[TIMESTAMP_FIELD].replace("Z", "+00:00"))
        for field in ("amount_clp", "amount_vs_baseline", "tx_count_card", "minutes_since_last_tx", "city_changed", TARGET_FIELD):
            row[field] = float(row[field])
        row["channel"] = str(row["channel"])
        row["mcc"] = str(row["mcc"])
        if row[TARGET_FIELD] not in (0, 1):
            raise ValueError(f"{TARGET_FIELD} must contain only 0 and 1")
    rows.sort(key=lambda row: row[TIMESTAMP_FIELD])
    return rows


def average_precision(labels: list[int], scores: list[float]) -> float:
    positives = sum(labels)
    if positives == 0:
        return 0.0
    order = sorted(range(len(scores)), key=scores.__getitem__, reverse=True)
    true_positives = 0
    precision_sum = 0.0
    for rank, index in enumerate(order, start=1):
        if labels[index] == 1:
            true_positives += 1
            precision_sum += true_positives / rank
    return precision_sum / positives


def metrics_at_threshold(labels: list[int], scores: list[float], threshold: float) -> dict:
    tp = fp = fn = tn = 0
    for label, score in zip(labels, scores):
        predicted = score >= threshold
        if predicted and label:
            tp += 1
        elif predicted:
            fp += 1
        elif label:
            fn += 1
        else:
            tn += 1
    return {
        "threshold": threshold,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "false_positive_rate": fp / (fp + tn) if fp + tn else 0.0,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path(__file__).parent / "data" / "synthetic_transactions.csv")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "artifacts")
    parser.add_argument("--scope", choices=["synthetic", "approved_labeled"], default="synthetic")
    parser.add_argument("--verbose", action="store_true", help="Mostrar progreso e iteraciones de entrenamiento")
    args = parser.parse_args()

    rows = load_rows(args.data)
    split = int(len(rows) * 0.8)
    train_rows, test_rows = rows[:split], rows[split:]
    train_labels = [int(row[TARGET_FIELD]) for row in train_rows]
    test_labels = [int(row[TARGET_FIELD]) for row in test_rows]
    if len(set(train_labels)) != 2 or len(set(test_labels)) != 2:
        raise ValueError("both temporal partitions must contain positive and negative labels")

    def matrix(records: list[dict]) -> list[list]:
        return [[record[field] for field in FEATURE_FIELDS] for record in records]

    verbose_level = 20 if args.verbose else False
    model = CatBoostClassifier(
        iterations=400,
        depth=6,
        learning_rate=0.04,
        loss_function="Logloss",
        eval_metric="AUC",
        auto_class_weights="Balanced",
        random_seed=42,
        allow_writing_files=False,
        verbose=verbose_level,
    )
    model.fit(
        matrix(train_rows),
        train_labels,
        cat_features=[FEATURE_FIELDS.index(name) for name in CATEGORICAL_FIELDS],
        eval_set=(matrix(test_rows), test_labels),
        early_stopping_rounds=40,
        verbose=verbose_level,
    )
    scores = [float(pair[1]) for pair in model.predict_proba(matrix(test_rows))]
    evaluation = {
        "test_rows": len(test_rows),
        "test_positive_rate": sum(test_labels) / len(test_labels),
        "average_precision": average_precision(test_labels, scores),
        "at_0_50": metrics_at_threshold(test_labels, scores, 0.5),
        "note": "Synthetic scope demonstrates a pipeline only; these metrics are not evidence of real fraud detection performance." if args.scope == "synthetic" else "Temporal holdout metrics; verify representativeness and calibration before operational use.",
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_path = args.output_dir / "catboost.cbm"
    model.save_model(str(model_path))
    model_version = f"catboost-demo-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    metadata = {
        "model_version": model_version,
        "model_type": "CatBoostClassifier",
        "model_scope": args.scope,
        "features": FEATURE_FIELDS,
        "categorical_features": CATEGORICAL_FIELDS,
        "target": TARGET_FIELD,
        "probability_calibrated": False,
        "train_rows": len(train_rows),
        "train_positive_rate": sum(train_labels) / len(train_labels),
        "dataset_path": str(args.data),
        "evaluation": evaluation,
    }
    (args.output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (args.output_dir / "feature_importance.json").write_text(
        json.dumps(dict(zip(FEATURE_FIELDS, map(float, model.feature_importances_))), indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))
    print(f"Saved model to {model_path}")


if __name__ == "__main__":
    main()
