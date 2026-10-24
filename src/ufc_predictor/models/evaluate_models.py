from datetime import datetime

import numpy as np
import pandas as pd

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from train_baseline import INPUT_PATH, FEATURES, TARGET, parse_date


def create_models():
    # Create fresh models for each evaluation.
    return {
        "Dummy baseline": DummyClassifier(strategy="prior"),

        "Logistic regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=1.0,
                solver="lbfgs",
                max_iter=1000,
            ),
        ),

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


def main():
    data = pd.read_csv(INPUT_PATH, dtype={"fight_id": str})
    data["event_date"] = data["event_date"].apply(parse_date)

    # Exclude the target fight's date and all later dates.
    cutoff = datetime(2023, 2, 11)
    data = data[data["event_date"] < cutoff].copy()

    data = data.dropna(subset=FEATURES + [TARGET])

    if data["fight_id"].duplicated().any():
        raise ValueError("Duplicate fight IDs found.")

    if not data[TARGET].isin([0, 1]).all():
        raise ValueError("Winner labels must be 0 or 1.")

    if not np.isfinite(
        data[FEATURES].to_numpy(dtype=float)
    ).all():
        raise ValueError("Features must contain finite numbers.")

    data[TARGET] = data[TARGET].astype(int)
    data = data.sort_values(["event_date", "fight_id"])

    # Split dates, rather than rows, to keep same-day fights together.
    dates = data["event_date"].drop_duplicates().to_numpy()

    if len(dates) < 4:
        raise ValueError("Need at least four different fight dates.")

    date_groups = np.array_split(dates, 4)

    all_predictions = []
    fold_scores = []

    print(f"Complete fights before cutoff: {len(data)}")

    for fold in range(1, 4):
        test_dates = date_groups[fold]

        train = data[data["event_date"] < test_dates[0]]
        test = data[data["event_date"].isin(test_dates)]

        if train[TARGET].nunique() != 2:
            raise ValueError(
                f"Evaluation {fold}: training needs both outcomes."
            )

        X_train = train[FEATURES]
        y_train = train[TARGET]
        X_test = test[FEATURES]
        y_test = test[TARGET]

        print(f"\nEvaluation {fold}")
        print(
            f"Train: {train['event_date'].min().date()} to "
            f"{train['event_date'].max().date()} "
            f"({len(train)} fights)"
        )
        print(
            f"Test: {test['event_date'].min().date()} to "
            f"{test['event_date'].max().date()} "
            f"({len(test)} fights)"
        )

        for name, model in create_models().items():
            model.fit(X_train, y_train)

            predictions = model.predict(X_test)
            probabilities = model.predict_proba(X_test)
            a_column = list(model.classes_).index(1)
            a_probabilities = probabilities[:, a_column]

            accuracy = accuracy_score(y_test, predictions)
            loss = log_loss(
                y_test,
                probabilities,
                labels=[0, 1],
            )

            fold_scores.append({
                "fold": fold,
                "model": name,
                "training_fights": len(train),
                "testing_fights": len(test),
                "accuracy": accuracy,
                "log_loss": loss,
            })

            print(
                f"{name}: accuracy={accuracy:.1%}, "
                f"log loss={loss:.3f}"
            )

            for position, (_, row) in enumerate(test.iterrows()):
                all_predictions.append({
                    "fold": fold,
                    "model": name,
                    "fight_id": row["fight_id"],
                    "event_date": row["event_date"].date().isoformat(),
                    "fighter_a_name": row["fighter_a_name"],
                    "fighter_b_name": row["fighter_b_name"],
                    "actual_a_win": int(row[TARGET]),
                    "predicted_a_win": int(predictions[position]),
                    "probability_a_win": float(
                        a_probabilities[position]
                    ),
                })

    predictions_table = pd.DataFrame(all_predictions)

    # Combine each model's predictions across all three test periods.
    summary = []

    for name, rows in predictions_table.groupby("model", sort=False):
        probabilities_a = rows["probability_a_win"].to_numpy()

        summary.append({
            "model": name,
            "tested_fights": len(rows),
            "accuracy": accuracy_score(
                rows["actual_a_win"],
                rows["predicted_a_win"],
            ),
            "log_loss": log_loss(
                rows["actual_a_win"],
                np.column_stack(
                    [1 - probabilities_a, probabilities_a]
                ),
                labels=[0, 1],
            ),
        })

    print("\nCombined results across the three test periods")

    for result in summary:
        print(
            f"{result['model']}: "
            f"{result['tested_fights']} fights, "
            f"accuracy={result['accuracy']:.1%}, "
            f"log loss={result['log_loss']:.3f}"
        )

    output_dir = INPUT_PATH.parent / "evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(fold_scores).to_csv(
        output_dir / "fold_scores.csv",
        index=False,
    )
    predictions_table.to_csv(
        output_dir / "predictions.csv",
        index=False,
    )
    pd.DataFrame(summary).to_csv(
        output_dir / "summary.csv",
        index=False,
    )

    print(f"\nSaved evaluation results to: {output_dir}")


if __name__ == "__main__":
    main()