from pathlib import Path
from datetime import datetime

import json
import re

RAW_PATH = Path(
    "data/processed/alex_volkanovski_raw.json"
)

CLEAN_PATH = Path(
    "data/processed/alex_volkanovski_clean.json"
)


def load_raw_fighter(raw_path):
    with open(raw_path, "r", encoding="utf-8") as file:
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
    if value is None:
        return None

    value = value.strip()

    if value in ("", "-", "--", "---"):
        return None

    inches = float(
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
    if value is None or value.strip() in ("", "---"):
        return None, None, None, None

    match = re.fullmatch(
        r"\s*(\d+)-(\d+)-(\d+)(?:\s*\((\d+)\s+NC\))?\s*",
        value,
    )

    if match is None:
        raise ValueError(f"Unrecognised fighter record: {value!r}")

    wins = int(match.group(1))
    losses = int(match.group(2))
    draws = int(match.group(3))

    no_contests = (
        int(match.group(4))
        if match.group(4) is not None
        else 0
    )

    return wins, losses, draws, no_contests


def parse_percentage(value):
    if value is None or value == "---":
        return None

    number = value.replace("%", "")

    return int(number) / 100

def clean_fighter(fighter):
    dob_day, dob_month, dob_year = parse_dob(
        fighter["dob"]
    )

    wins, losses, draws, no_contests = parse_record(
        fighter["record"]
    )

    return {
        "fighter_id": fighter["fighter_id"],
        "name": fighter["name"],

        "wins": wins,
        "losses": losses,
        "draws": draws,
        "no_conests": no_contests,

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


def save_clean_fighter(fighter, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(fighter, file, indent=4)


def main():
    input_dir = Path("data/processed/fighters/parsed")
    output_dir = Path("data/processed/fighters/cleaned")

    paths = sorted(input_dir.glob("*_raw.json"))

    if not paths:
        print(f"No parsed fighter files found in {input_dir}")
        return

    for raw_path in paths:
        raw_fighter = load_raw_fighter(raw_path)

        cleaned_fighter = clean_fighter(raw_fighter)

        fighter_id = cleaned_fighter["fighter_id"]
        output_path = output_dir / f"{fighter_id}_clean.json"

        save_clean_fighter(cleaned_fighter, output_path)

        print(f"Cleaned fighter saved to: {output_path}")


if __name__ == "__main__":
    main()