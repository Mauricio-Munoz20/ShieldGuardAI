"""Create a clearly synthetic, reproducible training set for coursework demos."""

import argparse
import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from features import FEATURE_FIELDS, TARGET_FIELD, TIMESTAMP_FIELD


CHANNELS = ["POS_CHIP", "POS_CONTACTLESS", "ECOMMERCE_CNP", "ATM"]
MCCS = ["5411", "5311", "5732", "5094", "7995", "5812"]


def sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def generate_row(rng: random.Random, timestamp: datetime) -> dict:
    baseline = max(1000.0, rng.lognormvariate(math.log(35000), 0.65))
    amount = max(500, int(rng.lognormvariate(math.log(baseline), 0.85)))
    ratio = amount / baseline
    channel = rng.choices(CHANNELS, weights=[42, 30, 23, 5], k=1)[0]
    mcc = rng.choices(MCCS, weights=[30, 15, 12, 7, 8, 28], k=1)[0]
    tx_count = rng.randint(0, 90)
    minutes_since = rng.randint(1, 2400)
    city_changed = int(rng.random() < 0.12)

    # The synthetic label intentionally depends on observable features. This
    # demonstrates the ML pipeline; it is not a proxy for real bank performance.
    log_odds = -5.25
    log_odds += 0.55 * max(0.0, math.log(max(ratio, 0.01)))
    log_odds += 0.72 if channel == "ECOMMERCE_CNP" else 0.0
    log_odds += 0.65 if amount >= 180000 else 0.0
    log_odds += 0.55 if mcc in {"5732", "5094", "7995"} else 0.0
    log_odds += 0.75 if city_changed and minutes_since < 45 else 0.0
    log_odds += 0.30 if tx_count >= 55 else 0.0
    probability = sigmoid(log_odds)
    label = int(rng.random() < probability)

    return {
        TIMESTAMP_FIELD: timestamp.isoformat(),
        "amount_clp": amount,
        "amount_vs_baseline": round(ratio, 4),
        "tx_count_card": tx_count,
        "minutes_since_last_tx": minutes_since,
        "channel": channel,
        "mcc": mcc,
        "city_changed": city_changed,
        TARGET_FIELD: label,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=12000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "data" / "synthetic_transactions.csv")
    args = parser.parse_args()
    if args.rows < 100:
        parser.error("--rows must be at least 100")

    rng = random.Random(args.seed)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    records = []
    for index in range(args.rows):
        timestamp = start + timedelta(seconds=index * 540)
        records.append(generate_row(rng, timestamp))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [TIMESTAMP_FIELD, *FEATURE_FIELDS, TARGET_FIELD]
    with args.output.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    positives = sum(row[TARGET_FIELD] for row in records)
    print(f"Wrote {len(records)} synthetic rows to {args.output}")
    print(f"Synthetic positive rate: {positives / len(records):.3%}")
    print("Labels are generated from the listed features and are for pipeline demonstration only.")


if __name__ == "__main__":
    main()
