from pathlib import Path
from datetime import datetime
import json
import re


RAW_PATH = Path(
    "data/processed/ufc_284_raw.json"
)

CLEAN_PATH = Path(
    "data/processed/ufc_284_clean.json"
)


def load_raw_event(raw_path):
    with open(
        raw_path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def parse_event_date(value):
    if value is None or value == "---":
        return None, None, None

    date = datetime.strptime(
        value,
        "%B %d, %Y"
    )

    return date.day, date.month, date.year


def parse_time_to_seconds(value):
    if value is None or value == "---":
        return None

    minutes, seconds = value.split(":")

    return (
        int(minutes) * 60
        + int(seconds)
    )


def clean_fight(fight):
    return {
        "fight_id": fight["fight_id"],
        "fighter_a": fight["fighter_a"],
        "fighter_b": fight["fighter_b"],
        "winner": fight["winner"],
        "weight_class": fight["weight_class"],
        "method": fight["method"],
        "round": int(
            fight["round"]
        ),
        "time_seconds": parse_time_to_seconds(
            fight["time"]
        ),
        "fight_url": fight["fight_url"]
    }


def clean_event(raw_event):
    event = raw_event["event"]

    event_day, event_month, event_year = (
        parse_event_date(
            event["event_date"]
        )
    )

    return {
        "event": {
            "event_id": event["event_id"],
            "event_name": event["event_name"],

            "event_day": event_day,
            "event_month": event_month,
            "event_year": event_year,

            "location": event["location"]
        },

        "fights": [
            clean_fight(fight)
            for fight in raw_event["fights"]
        ]
    }


def save_clean_event(cleaned_event, output_path):
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            cleaned_event,
            file,
            indent=4
        )


def main():
    input_dir = Path("data/processed/events/parsed")
    output_dir = Path("data/processed/events/cleaned")

    for raw_path in sorted(input_dir.glob("*_raw.json")):
        event_id = raw_path.name.removesuffix("_raw.json")

        # Only process files named with an event ID.
        if not re.fullmatch(r"[0-9a-f]{16}", event_id):
            continue

        raw_event = load_raw_event(raw_path)

        cleaned_event = clean_event(raw_event)

        output_path = output_dir / f"{event_id}_clean.json"

        save_clean_event(cleaned_event, output_path)

        print(f"Cleaned event saved to: {output_path}")


if __name__ == "__main__":
    main()