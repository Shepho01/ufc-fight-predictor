from pathlib import Path
from bs4 import BeautifulSoup
import json


EVENT_URL = "http://ufcstats.com/event-details/01dd4cdc2446f665"

HTML_PATH = Path(
    "data/raw/events/ufc_284.html"
)

OUTPUT_PATH = Path(
    "data/processed/ufc_284_raw.json"
)


def get_id_from_url(url):
    return url.rstrip("/").split("/")[-1]


def main():
    html = HTML_PATH.read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # -------------------------
    # Event metadata
    # -------------------------

    event_name = soup.select_one(
        ".b-content__title-highlight"
    ).get_text(
        strip=True
    )

    info_items = soup.select(
        ".b-list__box-list-item"
    )

    event_date = (
        info_items[0]
        .get_text(" ", strip=True)
        .replace("Date:", "")
        .strip()
    )

    location = (
        info_items[1]
        .get_text(" ", strip=True)
        .replace("Location:", "")
        .strip()
    )

    event_data = {
        "event_id": get_id_from_url(
            EVENT_URL
        ),
        "event_name": event_name,
        "event_date": event_date,
        "location": location
    }

    # -------------------------
    # Fight rows
    # -------------------------

    fight_rows = soup.select(
        ".b-fight-details__table-body "
        ".b-fight-details__table-row"
    )

    fights = []

    for row in fight_rows:

        # -------------------------
        # Fighters
        # -------------------------

        fighters = row.select(
            "a.b-link_style_black"
        )

        fighter_a = fighters[0].get_text(
            strip=True
        )

        fighter_b = fighters[1].get_text(
            strip=True
        )

        # -------------------------
        # Fight URL
        # -------------------------

        fight_url = row["data-link"]

        fight_id = get_id_from_url(
            fight_url
        )

        # -------------------------
        # Table columns
        # -------------------------

        columns = row.select("td")

        # -------------------------
        # Result
        # -------------------------

        result_flag = columns[0].select_one(
            "i.b-flag__text"
        )

        if result_flag:
            result = result_flag.get_text(
                strip=True
            ).lower()
        else:
            result = None

        if result == "win":
            winner = fighter_a
        else:
            winner = None

        # -------------------------
        # Fight information
        # -------------------------

        weight_class = columns[6].get_text(
            " ",
            strip=True
        )

        method = columns[7].get_text(
            " ",
            strip=True
        )

        round_number = columns[8].get_text(
            strip=True
        )

        fight_time = columns[9].get_text(
            strip=True
        )

        fights.append({
            "fight_id": fight_id,
            "fighter_a": fighter_a,
            "fighter_b": fighter_b,
            "winner": winner,
            "weight_class": weight_class,
            "method": method,
            "round": round_number,
            "time": fight_time,
            "fight_url": fight_url
        })

    # -------------------------
    # Build event dictionary
    # -------------------------

    data = {
        "event": event_data,
        "fights": fights
    }

    # -------------------------
    # Save JSON
    # -------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            data,
            indent=4
        ),
        encoding="utf-8"
    )

    print(
        f"Saved parsed event to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()