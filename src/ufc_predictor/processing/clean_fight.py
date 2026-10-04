import json
from pathlib import Path


RAW_PATH = Path("data/processed/makhachev_vs_volkanovski_raw.json")

CLEAN_PATH = Path("data/processed/makhachev_vs_volkanovski_clean.json")


def load_raw_fight():
    with open(RAW_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def parse_landed_attempted(value: str):
    parts = value.split(" of ")

    landed = int(parts[0])
    attempted = int(parts[1])

    return landed, attempted


def parse_percentage(value: str):
    if value == "---":
        return None
    
    number = value.replace("%", "")
    percentage = int(number) / 100
    return percentage


def parse_control_time(value: str):
    parts = value.split(":")

    minutes = int(parts[0])
    seconds = int(parts[1])

    total_seconds = (minutes * 60) + seconds

    return total_seconds

def calculate_accuracy(landed, attempted):
    if attempted == 0:
        return None

    return landed / attempted



def clean_fighter(fighter):
    sig_landed, sig_attempted = parse_landed_attempted(
        fighter["totals"]["Sig. str."]
    )

    total_landed, total_attempted = parse_landed_attempted(
        fighter["totals"]["Total str."]
    )

    td_landed, td_attempted = parse_landed_attempted(
        fighter["totals"]["Td"]
    )

    head_landed, head_attempted = parse_landed_attempted(
        fighter["significant_strikes"]["Head"]
    )

    body_landed, body_attempted = parse_landed_attempted(
        fighter["significant_strikes"]["Body"]
    )

    leg_landed, leg_attempted = parse_landed_attempted(
        fighter["significant_strikes"]["Leg"]
    )

    distance_landed, distance_attempted = parse_landed_attempted(
        fighter["significant_strikes"]["Distance"]
    )

    clinch_landed, clinch_attempted = parse_landed_attempted(
        fighter["significant_strikes"]["Clinch"]
    )

    ground_landed, ground_attempted = parse_landed_attempted(
        fighter["significant_strikes"]["Ground"]
    )

    return {
        "name": fighter["name"],
        "kd": int(fighter["totals"]["KD"]),

        "sig_str_landed": sig_landed,
        "sig_str_attempted": sig_attempted,
        "sig_str_pct": parse_percentage(
            fighter["totals"]["Sig. str. %"]
        ),

        "total_str_landed": total_landed,
        "total_str_attempted": total_attempted,

        "td_landed": td_landed,
        "td_attempted": td_attempted,
        "td_pct": parse_percentage(
            fighter["totals"]["Td %"]
        ),

        "head_landed": head_landed,
        "head_attempted": head_attempted,
        "head_accuracy": calculate_accuracy(
            head_landed, head_attempted
        ),

        "body_landed": body_landed,
        "body_attempted": body_attempted,
        "body_accuracy": calculate_accuracy(
            body_landed, body_attempted
        ),

        "leg_landed": leg_landed,
        "leg_attempted": leg_attempted,
        "leg_accuracy": calculate_accuracy(
            leg_landed, leg_attempted
        ),

        "distance_landed": distance_landed,
        "distance_attempted": distance_attempted,
        "distance_accuracy": calculate_accuracy(
            distance_landed, distance_attempted
        ),

        "clinch_landed": clinch_landed,
        "clinch_attempted": clinch_attempted,
        "clinch_accuracy": calculate_accuracy(
            clinch_landed, clinch_attempted
        ),

        "ground_landed": ground_landed,
        "ground_attempted": ground_attempted,
        "ground_accuracy": calculate_accuracy(
            ground_landed, ground_attempted
        ),

        "sub_att": int(fighter["totals"]["Sub. att"]),
        "rev": int(fighter["totals"]["Rev."]),

        "ctrl_seconds": parse_control_time(
            fighter["totals"]["Ctrl"]
        ),
    }

def save_clean_fight(cleaned_fight):
    with open(CLEAN_PATH, "w", encoding="utf-8") as file:
        json.dump(cleaned_fight, file, indent=4)
    
def main():
    fight_data = load_raw_fight()

    fighter_a = clean_fighter(fight_data["fighter_a"])
    fighter_b = clean_fighter(fight_data["fighter_b"])

    cleaned_fight = {
        "fighter_a": fighter_a,
        "fighter_b": fighter_b
    }

    save_clean_fight(cleaned_fight)


if __name__ == "__main__":
    main()