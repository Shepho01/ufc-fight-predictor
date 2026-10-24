from pathlib import Path
import csv
import json


FEATURE_NAMES = [
    "sig_str_accuracy_diff",
    "td_accuracy_diff",
    "total_str_landed_per_min_diff",
    "sig_ground_str_landed_per_min_diff",
]


def main():
    input_path = Path("data/processed/historical_features.json")
    output_path = Path("data/processed/training_table.csv")

    fights = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    rows = []

    for fight in fights:
        matchup = fight["features"]["matchup"]
        label = fight["labels"]["fighter_a_win"]

        row = {
            "fight_id": fight["fight_id"],
            "event_date": fight["event_date"],
            "fighter_a_name": fight["fighter_a_name"],
            "fighter_b_name": fight["fighter_b_name"],
        }

        for feature_name in FEATURE_NAMES:
            row[feature_name] = matchup[feature_name]

        row["fighter_a_win"] = label

        # Ready only when all selected inputs and the label exist.
        row["complete_case"] = (
            label is not None
            and all(
                row[name] is not None
                for name in FEATURE_NAMES
            )
        )

        rows.append(row)

    rows.sort(
        key=lambda row: (row["event_date"], row["fight_id"])
    )

    fieldnames = [
        "fight_id",
        "event_date",
        "fighter_a_name",
        "fighter_b_name",
        *FEATURE_NAMES,
        "fighter_a_win",
        "complete_case",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    complete_count = sum(
        row["complete_case"] for row in rows
    )

    print(f"Saved {len(rows)} rows to {output_path}")
    print(f"Rows with all four inputs and a label: {complete_count}")
    print(f"Rows with missing inputs or label: {len(rows) - complete_count}")


if __name__ == "__main__":
    main()