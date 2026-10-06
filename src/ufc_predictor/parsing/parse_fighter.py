from pathlib import Path
from bs4 import BeautifulSoup
import json


HTML_PATH = Path(
    "data/raw/fighters/alex_volkanovski.html"
)

OUTPUT_PATH = Path(
    "data/processed/alex_volkanovski_raw.json"
)

FIGHTER_ID = "e1248941344b3288"


def parse_profile_stats(soup):
    profile = {}

    stat_items = soup.select(
        ".b-list__info-box_style_small-width "
        ".b-list__box-list-item"
    )

    for item in stat_items:
        label_element = item.find(
            "i",
            class_="b-list__box-item-title"
        )

        if label_element is None:
            continue

        label = label_element.get_text(
            " ",
            strip=True
        ).replace(":", "")

        label_element.extract()

        value = item.get_text(
            " ",
            strip=True
        )

        profile[label] = value

    return profile

def parse_career_stats(soup):
    career_stats = {}

    stat_items = soup.select(
        ".b-list__info-box_style_middle-width "
        ".b-list__box-list-item"
    )

    for item in stat_items:
        label_element = item.find(
            "i",
            class_="b-list__box-item-title"
        )

        if label_element is None:
            continue

        label = label_element.get_text(
            " ",
            strip=True
        ).replace(":", "")

        if not label:
            continue

        label_element.extract()

        value = item.get_text(
            " ",
            strip=True
        )

        career_stats[label] = value

    return career_stats

def main():
    html = HTML_PATH.read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # -------------------------
    # Name
    # -------------------------

    name = soup.select_one(
        ".b-content__title-highlight"
    ).get_text(strip=True)

    # -------------------------
    # Record
    # -------------------------

    record_text = soup.select_one(
        ".b-content__title-record"
    ).get_text(strip=True)

    record = record_text.replace(
        "Record:",
        ""
    ).strip()

    # -------------------------
    # Fighter profile stats
    # -------------------------

    profile = parse_profile_stats(soup)
    
    career_stats = parse_career_stats(soup)

    fighter_data = {
        "fighter_id": FIGHTER_ID,
        "name": name,
        "record": record,
        "height": profile.get("Height"),
        "weight": profile.get("Weight"),
        "reach": profile.get("Reach"),
        "stance": profile.get("STANCE"),
        "dob": profile.get("DOB"),
        "sig_strikes_landed_per_min": career_stats.get("SLpM"),
        "sig_striking_accuracy": career_stats.get("Str. Acc."),
        "sig_strikes_absorbed_per_min": career_stats.get("SApM"),
        "sig_strike_defense": career_stats.get("Str. Def"),
        "takedowns_landed_per_15_min": career_stats.get("TD Avg."),
        "takedown_accuracy": career_stats.get("TD Acc."),
        "takedown_defense": career_stats.get("TD Def."),
        "submission_attempts_per_15_min": career_stats.get("Sub. Avg.")
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            fighter_data,
            indent=4
        ),
        encoding="utf-8"
    )

    print(
        f"Saved parsed fighter to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()