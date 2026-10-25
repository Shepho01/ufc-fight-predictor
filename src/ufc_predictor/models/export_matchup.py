import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from evaluate_models import create_models
from train_baseline import FEATURES, TARGET, parse_date


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = PROJECT_ROOT / "data/processed/training_table.csv"
OUTPUT_PATH = PROJECT_ROOT / "data/processed/predictions/islam_vs_volk_1.json"

FIGHT_ID = "256894b49303537b"
CUTOFF = datetime(2023, 2, 11)

DESCRIPTIONS = {
    "Dummy baseline": "Uses the frequency of fighter A wins in training.",
    "Logistic regression": "Combines four historical statistical differences.",
    "Decision tree": "Uses branching rules learned from earlier fights.",
    "Random forest": "Combines estimates from multiple decision trees.",
}


def main():
    data = pd.read_csv(INPUT_PATH, dtype={"fight_id": str})
    data["event_date"] = data["event_date"].apply(parse_date)

    if data["fight_id"].duplicated().any():
        raise ValueError("Duplicate fight IDs found.")

    target = data[data["fight_id"] == FIGHT_ID]

    if len(target) != 1:
        raise ValueError("Expected exactly one target fight.")

    fight = target.iloc[0]

    if fight["event_date"] != CUTOFF:
        raise ValueError("Target fight date does not match the cutoff.")

    if (
        fight["fighter_a_name"] != "Islam Makhachev"
        or fight["fighter_b_name"] != "Alexander Volkanovski"
    ):
        raise ValueError("Unexpected fighters or fighter order.")

    train = data[data["event_date"] < CUTOFF]
    train = train.dropna(subset=FEATURES + [TARGET])
    train = train.sort_values(["event_date", "fight_id"])

    if not train[TARGET].isin([0, 1]).all():
        raise ValueError("Training labels must be 0 or 1.")

    if train[TARGET].nunique() != 2:
        raise ValueError("Training needs both winning outcomes.")

    for frame in (train, target):
        if not np.isfinite(
            frame[FEATURES].to_numpy(dtype=float)
        ).all():
            raise ValueError("Missing or invalid prediction inputs.")

    predictions = []

    for name, model in create_models().items():
        model.fit(train[FEATURES], train[TARGET].astype(int))

        probabilities = model.predict_proba(target[FEATURES])[0]
        islam_column = list(model.classes_).index(1)

        predictions.append({
            "name": name,
            # The frontend currently displays percentages from 0 to 100.
            "islamWinProbability": float(
                probabilities[islam_column] * 100
            ),
            "description": DESCRIPTIONS[name],
        })

    output = {
        "fightId": FIGHT_ID,
        "fighterA": fight["fighter_a_name"],
        "fighterB": fight["fighter_b_name"],
        "fightDate": CUTOFF.date().isoformat(),
        "trainingCutoff": CUTOFF.date().isoformat(),
        "trainingFights": len(train),
        "featureCount": len(FEATURES),
        "predictions": predictions,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=4, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print(f"Saved predictions to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()