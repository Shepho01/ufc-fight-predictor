from pathlib import Path

from bs4 import BeautifulSoup

import json


FIGHT_URL = "http://ufcstats.com/fight-details/256894b49303537b"

HTML_PATH = Path(
    "data/raw/fights/makhachev_vs_volkanovski.html"
)


def parse_stat_table(table):
    headers = [
        th.get_text(" ", strip=True)
        for th in table.find("thead").find_all("th")
    ]

    fighter_a_stats = {}
    fighter_b_stats = {}

    tbody = table.find(
        "tbody",
        class_="b-fight-details__table-body"
    )

    if tbody is None:
        return fighter_a_stats, fighter_b_stats

    row = tbody.find(
        "tr",
        class_="b-fight-details__table-row"
    )

    if row is None:
        return fighter_a_stats, fighter_b_stats

    columns = row.find_all(
        "td",
        recursive=False
    )

    for header, column in zip(headers, columns):

        if header == "Fighter":
            continue

        values = column.find_all(
            "p",
            recursive=False
        )

        if len(values) >= 2:
            fighter_a_stats[header] = (
                values[0].get_text(
                    " ",
                    strip=True
                )
            )

            fighter_b_stats[header] = (
                values[1].get_text(
                    " ",
                    strip=True
                )
            )

    return fighter_a_stats, fighter_b_stats


def get_id_from_url(url):
    return url.rstrip("/").split("/")[-1]


def parse_fight_metadata(soup):
    event_link = soup.select_one(
        ".b-content__title a"
    )

    event_name = event_link.get_text(
        " ",
        strip=True
    )

    event_id = get_id_from_url(
        event_link["href"]
    )

    fight_title = soup.select_one(
        ".b-fight-details__fight-title"
    ).get_text(
        " ",
        strip=True
    )

    title_fight = "Title Bout" in fight_title

    weight_class = (
        fight_title
        .replace("UFC ", "")
        .replace(" Title Bout", "")
        .replace(" Bout", "")
        .strip()
    )

    detail_items = soup.select(
        ".b-fight-details__text-item, "
        ".b-fight-details__text-item_first"
    )

    details = {}

    for item in detail_items:
        label = item.select_one(
            ".b-fight-details__label"
        )

        if label is None:
            continue

        label_text = label.get_text(
            " ",
            strip=True
        ).replace(":", "")

        label.extract()

        value = item.get_text(
            " ",
            strip=True
        )

        details[label_text] = value

    time_format = details.get("Time format")

    scheduled_rounds = None

    if time_format:
        scheduled_rounds = int(
            time_format.split()[0]
        )

    return {
        "fight_id": get_id_from_url(FIGHT_URL),
        "event_id": event_id,
        "event_name": event_name,
        "weight_class": weight_class,
        "title_fight": title_fight,
        "scheduled_rounds": scheduled_rounds,
        "method": details.get("Method"),
        "finish_round": (
            int(details["Round"])
            if details.get("Round")
            else None
        ),
        "finish_time": details.get("Time"),
        "referee": details.get("Referee")
    }


def main():
    # -------------------------
    # Read HTML
    # -------------------------

    html = HTML_PATH.read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # -------------------------
    # Fighter information
    # -------------------------

    fighter_elements = soup.select(
        ".b-fight-details__person"
    )

    fighter_a_link = fighter_elements[0].select_one(
        ".b-fight-details__person-link"
    )

    fighter_b_link = fighter_elements[1].select_one(
        ".b-fight-details__person-link"
    )

    fighter_a = fighter_a_link.get_text(
        strip=True
    )

    fighter_b = fighter_b_link.get_text(
        strip=True
    )

    fighter_a_id = get_id_from_url(
        fighter_a_link["href"]
    )

    fighter_b_id = get_id_from_url(
        fighter_b_link["href"]
    )

    fighter_a_result = fighter_elements[0].select_one(
        ".b-fight-details__person-status"
    ).get_text(
        strip=True
    )

    fighter_b_result = fighter_elements[1].select_one(
        ".b-fight-details__person-status"
    ).get_text(
        strip=True
    )

    print(f"\n{fighter_a} vs {fighter_b}")

    # -------------------------
    # Determine winner
    # -------------------------

    winner_id = None

    if fighter_a_result == "W":
        winner_id = fighter_a_id

    elif fighter_b_result == "W":
        winner_id = fighter_b_id

    # -------------------------
    # Fight metadata
    # -------------------------

    fight_metadata = parse_fight_metadata(
        soup
    )

    fight_metadata["winner_id"] = winner_id

    # -------------------------
    # Full-fight stat tables
    # -------------------------

    table_headers = soup.find_all(
        "thead",
        class_="b-fight-details__table-head"
    )

    # First full-fight table = Totals
    totals_table = table_headers[0].find_parent(
        "table"
    )

    # Second full-fight table = Significant Strikes
    significant_strikes_table = (
        table_headers[1].find_parent("table")
    )

    # -------------------------
    # Parse Totals
    # -------------------------

    fighter_a_totals, fighter_b_totals = (
        parse_stat_table(totals_table)
    )

    # -------------------------
    # Parse Significant Strikes
    # -------------------------

    fighter_a_sig_strikes, fighter_b_sig_strikes = (
        parse_stat_table(
            significant_strikes_table
        )
    )

    # -------------------------
    # Build fighter dictionaries
    # -------------------------

    fighter_a_data = {
        "fighter_id": fighter_a_id,
        "name": fighter_a,
        "result": fighter_a_result,
        "totals": fighter_a_totals,
        "significant_strikes":
            fighter_a_sig_strikes
    }

    fighter_b_data = {
        "fighter_id": fighter_b_id,
        "name": fighter_b,
        "result": fighter_b_result,
        "totals": fighter_b_totals,
        "significant_strikes":
            fighter_b_sig_strikes
    }

    # -------------------------
    # Build fight dictionary
    # -------------------------

    fight_data = {
        "fight": fight_metadata,
        "fighter_a": fighter_a_data,
        "fighter_b": fighter_b_data
    }

    # -------------------------
    # Save JSON
    # -------------------------

    output_path = Path("data/processed/makhachev_vs_volkanovski_raw.json")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_text(
        json.dumps(
            fight_data,
            indent=4
        ),
        encoding="utf-8"
    )

    print(
        f"\nSaved parsed fight to {output_path}"
    )


if __name__ == "__main__":
    main()