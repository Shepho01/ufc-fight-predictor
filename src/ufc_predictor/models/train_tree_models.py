from datetime import datetime

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, log_loss
from sklearn.tree import DecisionTreeClassifier, export_text

from train_baseline import INPUT_PATH, FEATURES, TARGET, parse_date


def main():
    data = pd.read_csv(
        INPUT_PATH,
        dtype={"fight_id": str},
    )

    data["event_date"] = data["event_date"].apply(parse_date)

    # Keep rows with all four inputs and a known winner.
    data = data.dropna(subset=FEATURES + [TARGET]).copy()

    if not data[TARGET].isin([0, 1]).all():
        raise ValueError("Winner labels must be 0 or 1.")

    if not np.isfinite(
        data[FEATURES].to_numpy(dtype=float)
    ).all():
        raise ValueError("Features must contain finite numbers.")

    if data["fight_id"].duplicated().any():
        raise ValueError("Duplicate fight IDs found.")

    data[TARGET] = data[TARGET].astype(int)

    data = data.sort_values(
        ["event_date", "fight_id"]
    ).reset_index(drop=True)

    # Islam vs Volkanovski's first fight.
    cutoff_date = datetime(2023, 2, 11)
    target_fight_id = "256894b49303537b"

    # Exclude the target fight and every fight on or after its date.
    train = data[data["event_date"] < cutoff_date]

    # Evaluate only the target fight.
    test = data[data["fight_id"] == target_fight_id]

    if len(test) != 1:
        raise ValueError(
            "Expected exactly one complete row "
            "for Islam vs Volkanovski."
        )

    if test.iloc[0]["event_date"] != cutoff_date:
        raise ValueError("Target fight date does not match the cutoff.")

    # Class 1 means fighter A wins. Verify that A is Islam.
    if test.iloc[0]["fighter_a_name"] != "Islam Makhachev":
        raise ValueError("Expected Islam Makhachev as fighter A.")

    if train.empty:
        raise ValueError("No complete training fights before the cutoff.")

    if train[TARGET].nunique() != 2:
        raise ValueError(
            "Training data must contain both winning outcomes."
        )

    X_train = train[FEATURES]
    y_train = train[TARGET]

    X_test = test[FEATURES]
    y_test = test[TARGET]

    print(f"Complete rows: {len(data)}")
    print(f"Training fights: {len(train)}")
    print(f"Testing fights: {len(test)}")
    print(f"Training uses fights before: {cutoff_date.date()}")
    print("Target: Islam Makhachev vs Alexander Volkanovski")

    print(
        f"Training labels: "
        f"A wins = {(y_train == 1).sum()}, "
        f"B wins = {(y_train == 0).sum()}"
    )

    models = {
        "Decision tree": DecisionTreeClassifier(
            max_depth=3,
            min_samples_leaf=10,
            random_state=42,
        ),

        "Random forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=3,
            min_samples_leaf=10,
            max_features="sqrt",
            random_state=42,
            n_jobs=-1,
        ),
    }

    for name, model in models.items():
        model.fit(X_train, y_train)

        train_predictions = model.predict(X_train)

        # Only the four historical features enter the prediction.
        test_predictions = model.predict(X_test)
        test_probabilities = model.predict_proba(X_test)

        islam_column = list(model.classes_).index(1)
        islam_probability = test_probabilities[0, islam_column]

        predicted_winner = (
            "Islam Makhachev"
            if test_predictions[0] == 1
            else "Alexander Volkanovski"
        )

        train_accuracy = accuracy_score(
            y_train,
            train_predictions,
        )

        # The target's actual result is used only for evaluation.
        test_accuracy = accuracy_score(
            y_test,
            test_predictions,
        )

        test_loss = log_loss(
            y_test,
            test_probabilities,
            labels=[0, 1],
        )

        print(f"\n{name}")
        print(f"Islam win estimate: {islam_probability:.1%}")
        print(
            f"Volkanovski win estimate: "
            f"{1 - islam_probability:.1%}"
        )
        print(f"Predicted winner: {predicted_winner}")
        print(f"Training accuracy: {train_accuracy:.1%}")
        print(f"Target-fight accuracy: {test_accuracy:.1%}")
        print(f"Target-fight log loss: {test_loss:.3f}")

    print("\nDecision tree rules")
    print("Class 0 = fighter B wins; class 1 = fighter A wins\n")

    print(
        export_text(
            models["Decision tree"],
            feature_names=FEATURES,
            decimals=3,
        )
    )

    print(
        "\nThis evaluates one fight. It does not measure "
        "overall prediction performance."
    )


if __name__ == "__main__":
    main()