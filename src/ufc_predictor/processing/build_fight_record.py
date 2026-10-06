from pathlib import Path
import json


EVENT_PATH = Path(
    "data/processed/ufc_284_clean.json"
)

FIGHT_PATH = Path(
    "data/processed/makhachev_vs_volkanovski_clean.json"
)

FIGHTER_A_PATH = Path(
    "data/processed/islam_makhachev_clean.json"
)

FIGHTER_B_PATH = Path(
    "data/processed/alex_volkanovski_clean.json"
)

OUTPUT_PATH = Path(
    "data/processed/makhachev_vs_volkanovski_record.json"
)


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def find_event_fight(event_data, fight_id):
    for fight in event_data["fights"]:
        if fight["fight_id"] == fight_id:
            return fight

    return None


def calculate_age(
    dob_day,
    dob_month,
    dob_year,
    event_day,
    event_month,
    event_year
):
    age = event_year - dob_year

    birthday_has_happened = (
        (event_month, event_day)
        >=
        (dob_month, dob_day)
    )

    if not birthday_has_happened:
        age -= 1

    return age


def main():
    event_data = load_json(
        EVENT_PATH
    )

    fight_data = load_json(
        FIGHT_PATH
    )

    fighter_a_profile = load_json(
        FIGHTER_A_PATH
    )

    fighter_b_profile = load_json(
        FIGHTER_B_PATH
    )

    # -------------------------
    # Fight ID
    # -------------------------

    fight_id = fight_data["fight"]["fight_id"]

    # -------------------------
    # Find fight inside event
    # -------------------------

    event_fight = find_event_fight(
        event_data,
        fight_id
    )

    if event_fight is None:
        raise ValueError(
            f"Fight {fight_id} not found in event file"
        )

    # -------------------------
    # Event date
    # -------------------------

    event = event_data["event"]

    event_day = event["event_day"]
    event_month = event["event_month"]
    event_year = event["event_year"]

    # -------------------------
    # Calculate fighter ages
    # -------------------------

    fighter_a_age = calculate_age(
        fighter_a_profile["dob_day"],
        fighter_a_profile["dob_month"],
        fighter_a_profile["dob_year"],
        event_day,
        event_month,
        event_year
    )

    fighter_b_age = calculate_age(
        fighter_b_profile["dob_day"],
        fighter_b_profile["dob_month"],
        fighter_b_profile["dob_year"],
        event_day,
        event_month,
        event_year
    )

    # -------------------------
    # Build fighter A
    # -------------------------

    fighter_a = {
        "fighter_id": fighter_a_profile["fighter_id"],
        "name": fighter_a_profile["name"],

        "age_at_fight": fighter_a_age,

        "height_cm": fighter_a_profile["height_cm"],
        "weight_lbs": fighter_a_profile["weight_lbs"],
        "reach_cm": fighter_a_profile["reach_cm"],
        "stance": fighter_a_profile["stance"],

        "fight_stats": fight_data["fighter_a"]
    }

    # -------------------------
    # Build fighter B
    # -------------------------

    fighter_b = {
        "fighter_id": fighter_b_profile["fighter_id"],
        "name": fighter_b_profile["name"],

        "age_at_fight": fighter_b_age,

        "height_cm": fighter_b_profile["height_cm"],
        "weight_lbs": fighter_b_profile["weight_lbs"],
        "reach_cm": fighter_b_profile["reach_cm"],
        "stance": fighter_b_profile["stance"],

        "fight_stats": fight_data["fighter_b"]
    }

    # -------------------------
    # Matchup differences
    # -------------------------

    matchup = {
        "age_diff": (
            fighter_a_age
            - fighter_b_age
        ),

        "height_diff_cm": (
            fighter_a_profile["height_cm"]
            - fighter_b_profile["height_cm"]
        ),

        "reach_diff_cm": (
            fighter_a_profile["reach_cm"]
            - fighter_b_profile["reach_cm"]
        )
    }

    # -------------------------
    # Build complete record
    # -------------------------

    fight_record = {
        "fight": {
            **fight_data["fight"],

            "event_day": event_day,
            "event_month": event_month,
            "event_year": event_year,

            "location": event["location"]
        },

        "fighter_a": fighter_a,
        "fighter_b": fighter_b,

        "matchup": matchup
    }

    # -------------------------
    # Save
    # -------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            fight_record,
            file,
            indent=4
        )

    print(
        f"Fight record saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()