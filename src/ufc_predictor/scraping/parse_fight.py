from pathlib import Path

from bs4 import BeautifulSoup

import json


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
    # Fighter names
    # -------------------------

    fighter_elements = soup.select(
        ".b-fight-details__person-name"
    )

    fighter_a = fighter_elements[0].get_text(
        strip=True
    )

    fighter_b = fighter_elements[1].get_text(
        strip=True
    )

    print(f"\n{fighter_a} vs {fighter_b}")

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
        "name": fighter_a,
        "totals": fighter_a_totals,
        "significant_strikes":
            fighter_a_sig_strikes
    }

    fighter_b_data = {
        "name": fighter_b,
        "totals": fighter_b_totals,
        "significant_strikes":
            fighter_b_sig_strikes
    }

    fight_data = {
        "fighter_a": fighter_a_data,
        "fighter_b": fighter_b_data
    }

    output_path = Path(
        "data/processed/"
        "makhachev_vs_volkanovski_raw.json"
    )

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