from pathlib import Path
from datetime import datetime
import json


RAW_PATH = Path(
    "data/processed/ufc_284_raw.json"
)

CLEAN_PATH = Path(
    "data/processed/ufc_284_clean.json"
)


def load_raw_event():
    with open(
        RAW_PATH,
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


def save_clean_event(cleaned_event):
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
            cleaned_event,
            file,
            indent=4
        )


def main():
    raw_event = load_raw_event()

    cleaned_event = clean_event(
        raw_event
    )

    save_clean_event(
        cleaned_event
    )

    print(
        f"Cleaned event saved to: {CLEAN_PATH}"
    )


if __name__ == "__main__":
    main()