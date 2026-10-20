from pathlib import Path
from urllib.parse import urljoin, urlsplit
import json
import re

from bs4 import BeautifulSoup


def parse_profile_stats(soup):
    profile = {}

    stat_items = soup.select(
        ".b-list__info-box_style_small-width "
        ".b-list__box-list-item"
    )

    for item in stat_items:
        label_element = item.find(
            "i",
            class_="b-list__box-item-title",
        )

        if label_element is None:
            continue

        label = label_element.get_text(
            " ", strip=True
        ).replace(":", "")

        label_element.extract()

        value = item.get_text(" ", strip=True)
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
            class_="b-list__box-item-title",
        )

        if label_element is None:
            continue

        label = label_element.get_text(
            " ", strip=True
        ).replace(":", "")

        if not label:
            continue

        label_element.extract()

        value = item.get_text(" ", strip=True)
        career_stats[label] = value

    return career_stats


def parse_fight_history(soup):
    history = {}

    links = soup.select(
        'table a[href*="/fight-details/"]'
    )

    for link in links:
        url = urljoin(
            "http://ufcstats.com",
            link["href"],
        )

        parsed = urlsplit(url)

        match = re.fullmatch(
            r"/fight-details/([0-9a-f]{16})/?",
            parsed.path,
        )

        if (
            parsed.hostname not in (
                "ufcstats.com",
                "www.ufcstats.com",
            )
            or not match
        ):
            continue

        fight_id = match.group(1)

        # Using the fight ID as a key removes duplicate links.
        history[fight_id] = {
            "fight_id": fight_id,
            "fight_url": (
                "http://ufcstats.com/fight-details/"
                f"{fight_id}"
            ),
        }

    return list(history.values())


def parse_fighter(html_path, fighter_id):
    """Read one fighter page and return its extracted data."""

    html = Path(html_path).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    name_element = soup.select_one(
        ".b-content__title-highlight"
    )

    record_element = soup.select_one(
        ".b-content__title-record"
    )

    if name_element is None or record_element is None:
        raise ValueError(
            f"Missing fighter name or record in {html_path}"
        )

    name = name_element.get_text(strip=True)

    record_text = record_element.get_text(strip=True)
    record = record_text.replace("Record:", "").strip()

    profile = parse_profile_stats(soup)
    career_stats = parse_career_stats(soup)
    fight_history = parse_fight_history(soup)

    fighter_data = {
        "fighter_id": fighter_id,
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
        "sig_strike_defense": career_stats.get(
            "Str. Def.",
            career_stats.get("Str. Def"),
        ),
        "takedowns_landed_per_15_min": career_stats.get("TD Avg."),
        "takedown_accuracy": career_stats.get("TD Acc."),
        "takedown_defense": career_stats.get("TD Def."),
        "submission_attempts_per_15_min": career_stats.get("Sub. Avg."),

        "fight_history": fight_history,
    }

    return fighter_data


def main():
    """Parse all fighter pages named with a fighter ID."""

    input_dir = Path("data/raw/fighters")
    output_dir = Path("data/processed/fighters/parsed")

    html_paths = [
        path
        for path in sorted(input_dir.glob("*.html"))
        if re.fullmatch(r"[0-9a-f]{16}", path.stem)
    ]

    if not html_paths:
        print(f"No ID-named fighter pages found in {input_dir}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    saved = 0
    failures = []

    for html_path in html_paths:
        fighter_id = html_path.stem

        try:
            fighter_data = parse_fighter(
                html_path,
                fighter_id,
            )

            output_path = output_dir / f"{fighter_id}_raw.json"

            output_path.write_text(
                json.dumps(fighter_data, indent=4) + "\n",
                encoding="utf-8",
            )

            print(f"Saved {fighter_data['name']}: {output_path}")
            saved += 1

        except Exception as error:
            print(f"Failed: {html_path}")
            print(f"Reason: {error}")
            failures.append(html_path)

    print(f"\nSaved: {saved}; failed: {len(failures)}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()