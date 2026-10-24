from datetime import datetime
from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


INPUT_PATH = Path("data/processed/training_table.csv")

FEATURES = [
    "sig_str_accuracy_diff",
    "td_accuracy_diff",
    "total_str_landed_per_min_diff",
    "sig_ground_str_landed_per_min_diff",
]

TARGET = "fighter_a_win"


def parse_date(value):
    # Accept the script's original dates and spreadsheet-formatted dates.
    for date_format in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            continue

    raise ValueError(f"Unexpected date: {value!r}")


def main():
    data = pd.read_csv(INPUT_PATH, dtype={"fight_id": str})

    data["event_date"] = data["event_date"].apply(parse_date)

    # Keep rows with all four inputs and a known winner.
    data = data.dropna(subset=FEATURES + [TARGET]).copy()

    if not data[TARGET].isin([0, 1]).all():
        raise ValueError("Winner labels must be 0 or 1.")

    data[TARGET] = data[TARGET].astype(int)
    data = data.sort_values(["event_date", "fight_id"])

    if len(data) < 10:
        raise ValueError("Too few complete rows for this experiment.")

    # Predict Islam vs Volkanovski's first fight.
    cutoff_date = datetime(2023, 2, 11)
    target_fight_id = "256894b49303537b"

    # Learn only from fights before the target fight's date.
    train = data[data["event_date"] < cutoff_date]

    # Evaluate only the selected fight.
    test = data[data["fight_id"] == target_fight_id]

    if len(test) != 1:
        raise ValueError(
            "Expected exactly one complete row for Islam vs Volkanovski."
        )

    if train.empty or test.empty:
        raise ValueError("The date split produced an empty dataset.")

    if train[TARGET].nunique() != 2:
        raise ValueError("Training data must contain both winning outcomes.")

    X_train = train[FEATURES]
    y_train = train[TARGET]

    X_test = test[FEATURES]
    y_test = test[TARGET]

    print(f"Complete rows: {len(data)}")
    print(f"Training fights: {len(train)}")
    print(f"Testing fights: {len(test)}")
    print(f"Test period begins: {cutoff_date.date()}")

    print(
        f"Training labels: "
        f"A wins = {(y_train == 1).sum()}, "
        f"B wins = {(y_train == 0).sum()}"
    )

    print(
        f"Testing labels: "
        f"A wins = {(y_test == 1).sum()}, "
        f"B wins = {(y_test == 0).sum()}"
    )

    models = {
        # Predicts using the training set's overall win frequency.
        "Dummy baseline": DummyClassifier(strategy="prior"),

        "Logistic regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=1.0,
                solver="lbfgs",
                max_iter=1000,
            ),
        ),
    }

    for name, model in models.items():
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)
        
        print(
            f"\n{name}: Islam's estimated win probability: "
            f"{probabilities[0, 1]:.1%}"
        )

        accuracy = accuracy_score(y_test, predictions)
        loss = log_loss(y_test, probabilities, labels=[0, 1])

        print(f"\n{name}")
        print(f"Test accuracy: {accuracy:.1%}")
        print(f"Test log loss: {loss:.3f}")


if __name__ == "__main__":
    main()