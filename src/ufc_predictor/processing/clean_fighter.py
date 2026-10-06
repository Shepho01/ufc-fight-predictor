from pathlib import Path
from datetime import datetime

import json


RAW_PATH = Path(
    "data/processed/alex_volkanovski_raw.json"
)

CLEAN_PATH = Path(
    "data/processed/alex_volkanovski_clean.json"
)


def load_raw_fighter():
    with open(RAW_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_height_to_cm(value):
    if value is None or value == "---":
        return None

    feet, inches = value.replace('"', "").split("'")

    feet = int(feet.strip())
    inches = int(inches.strip())

    total_inches = (feet * 12) + inches

    return total_inches * 2.54


def parse_reach_to_cm(value):
    if value is None or value == "---":
        return None

    inches = int(
        value.replace('"', "").strip()
    )

    return inches * 2.54


def parse_weight_to_lbs(value):
    if value is None or value == "---":
        return None

    return int(
        value.replace("lbs.", "").strip()
    )


def parse_dob(value):
    if value is None or value == "---":
        return None, None, None

    date = datetime.strptime(
        value,
        "%b %d, %Y"
    )

    return date.day, date.month, date.year

def parse_record(value):
    if value is None or value == "---":
        return None, None, None

    wins, losses, draws = value.split("-")

    return int(wins), int(losses), int(draws)


def parse_percentage(value):
    if value is None or value == "---":
        return None

    number = value.replace("%", "")

    return int(number) / 100

def clean_fighter(fighter):
    dob_day, dob_month, dob_year = parse_dob(
        fighter["dob"]
    )

    wins, losses, draws = parse_record(
        fighter["record"]
    )

    return {
        "fighter_id": fighter["fighter_id"],
        "name": fighter["name"],

        "wins": wins,
        "losses": losses,
        "draws": draws,

        "height_cm": parse_height_to_cm(
            fighter["height"]
        ),

        "weight_lbs": parse_weight_to_lbs(
            fighter["weight"]
        ),

        "reach_cm": parse_reach_to_cm(
            fighter["reach"]
        ),

        "stance": fighter["stance"],

        "dob_day": dob_day,
        "dob_month": dob_month,
        "dob_year": dob_year,
        
        "sig_strikes_landed_per_min": float(
        fighter["sig_strikes_landed_per_min"]
        ),

        "sig_striking_accuracy": parse_percentage(
            fighter["sig_striking_accuracy"]
        ),

        "sig_strikes_absorbed_per_min": float(
            fighter["sig_strikes_absorbed_per_min"]
        ),

        "sig_strike_defense": parse_percentage(
            fighter["sig_strike_defense"]
        ),

        "takedowns_landed_per_15_min": float(
            fighter["takedowns_landed_per_15_min"]
        ),

        "takedown_accuracy": parse_percentage(
            fighter["takedown_accuracy"]
        ),

        "takedown_defense": parse_percentage(
            fighter["takedown_defense"]
        ),

        "submission_attempts_per_15_min": float(
            fighter["submission_attempts_per_15_min"]
        )
    }


def save_clean_fighter(fighter):
    CLEAN_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        CLEAN_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            fighter,
            file,
            indent=4
        )


def main():
    raw_fighter = load_raw_fighter()

    cleaned_fighter = clean_fighter(
        raw_fighter
    )

    save_clean_fighter(
        cleaned_fighter
    )

    print(
        f"Cleaned fighter saved to: {CLEAN_PATH}"
    )


if __name__ == "__main__":
    main()