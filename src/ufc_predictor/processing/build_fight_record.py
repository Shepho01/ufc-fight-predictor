"""Join cleaned fights, events and fighter profiles by ID."""
import argparse
from datetime import date
import json
from pathlib import Path


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def add_unique(index, identifier, data, path):
    if not identifier or identifier in index:
        raise ValueError(
            f"Missing or duplicate ID {identifier!r} in {path}"
        )

    index[identifier] = data


def load_clean_data(input_dir):
    events = {}
    fighters = {}
    fights = {}

    clean_paths = []

    for category in ("events", "fighters", "fights"):
        folder = input_dir / category / "cleaned"
        clean_paths.extend(folder.glob("*_clean.json"))

    for path in sorted(clean_paths):
        data = load_json(path)

        if "event" in data and "fights" in data:
            add_unique(
                events,
                data["event"]["event_id"],
                data,
                path,
            )

        elif (
            "fight" in data
            and "fighter_a" in data
            and "fighter_b" in data
        ):
            add_unique(
                fights,
                data["fight"]["fight_id"],
                (path, data),
                path,
            )

        elif "fighter_id" in data:
            add_unique(
                fighters,
                data["fighter_id"],
                data,
                path,
            )

        else:
            raise ValueError(f"Unrecognised cleaned file: {path}")

    return events, fighters, fights


def calculate_age(profile, event_date):
    parts = [
        profile.get(key)
        for key in ("dob_year", "dob_month", "dob_day")
    ]

    if any(part is None for part in parts):
        return None

    birthday = date(*parts)

    if birthday > event_date:
        raise ValueError("Date of birth is after the fight date")

    return event_date.year - birthday.year - (
        (event_date.month, event_date.day)
        < (birthday.month, birthday.day)
    )


def difference(a, b):
    return a - b if a is not None and b is not None else None


def build_fight_record(fight_data, event_data, profiles):
    fight = fight_data["fight"]
    event = event_data["event"]

    if fight["event_id"] != event["event_id"]:
        raise ValueError(
            f"Event mismatch for fight {fight['fight_id']}"
        )

    matches = [
        item
        for item in event_data["fights"]
        if item["fight_id"] == fight["fight_id"]
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Fight {fight['fight_id']} must appear once in its event"
        )

    event_date = date(
        event["event_year"],
        event["event_month"],
        event["event_day"],
    )

    sides = {}

    for side in ("fighter_a", "fighter_b"):
        stats = fight_data[side]
        fighter_id = stats["fighter_id"]

        if fighter_id not in profiles:
            raise ValueError(
                f"Missing fighter profile {fighter_id} "
                f"for {fight['fight_id']}"
            )

        profile = profiles[fighter_id]

        sides[side] = {
            "fighter_id": fighter_id,
            "name": profile["name"],
            "age_at_fight": calculate_age(profile, event_date),

            # Profile snapshots, not verified historical measurements.
            "height_cm": profile.get("height_cm"),
            "weight_lbs": profile.get("weight_lbs"),
            "reach_cm": profile.get("reach_cm"),
            "stance": profile.get("stance"),

            "fight_stats": stats,
        }

    a = sides["fighter_a"]
    b = sides["fighter_b"]

    if a["fighter_id"] == b["fighter_id"]:
        raise ValueError(
            f"Identical opponents in {fight['fight_id']}"
        )

    return {
        "fight": {
            **fight,
            "event_name": event["event_name"],
            "event_day": event_date.day,
            "event_month": event_date.month,
            "event_year": event_date.year,
            "location": event.get("location"),
        },

        **sides,

        "matchup": {
            "age_diff": difference(
                a["age_at_fight"],
                b["age_at_fight"],
            ),
            "height_diff_cm": difference(
                a["height_cm"],
                b["height_cm"],
            ),
            "reach_diff_cm": difference(
                a["reach_cm"],
                b["reach_cm"],
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/processed"),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed"),
    )

    args = parser.parse_args()

    events, profiles, fights = load_clean_data(args.input_dir)

    if not fights:
        parser.error(
            f"No cleaned fights found in {args.input_dir}"
        )

    # Validate and build all records before writing any files.
    outputs = {}

    for fight_id, (source, fight_data) in fights.items():
        event_id = fight_data["fight"]["event_id"]

        if event_id not in events:
            raise ValueError(
                f"Missing event {event_id} for fight {fight_id}"
            )

        record = build_fight_record(
            fight_data,
            events[event_id],
            profiles,
        )

        filename = (
            source.name.removesuffix("_clean.json")
            + "_record.json"
        )

        outputs[args.output_dir / filename] = record

    # Prevent duplicate records caused by renamed source files.
    for path in args.output_dir.glob("*_record.json"):
        existing_id = load_json(path)["fight"]["fight_id"]

        if existing_id in fights and path not in outputs:
            raise ValueError(
                f"Existing record for {existing_id} at {path}; "
                "resolve duplicate first"
            )

        if (
            path in outputs
            and existing_id != outputs[path]["fight"]["fight_id"]
        ):
            raise ValueError(
                f"Output path belongs to another fight: {path}"
            )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for path, record in outputs.items():
        path.write_text(
            json.dumps(record, indent=4, allow_nan=False) + "\n",
            encoding="utf-8",
        )

        print(f"Saved: {path}")

    print(f"Built {len(outputs)} fight record(s).")


if __name__ == "__main__":
    main()