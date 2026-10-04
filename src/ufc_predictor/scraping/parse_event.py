from pathlib import Path

from bs4 import BeautifulSoup


HTML_PATH = Path("data/raw/events/ufc_284.html")


def main():
    # Read the saved UFC event HTML
    html = HTML_PATH.read_text(encoding="utf-8")

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # -------------------------
    # Event metadata
    # -------------------------

    event_name = soup.select_one(
        ".b-content__title-highlight"
    ).get_text(strip=True)

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

    print(f"Event: {event_name}")
    print(f"Date: {event_date}")
    print(f"Location: {location}")

    # -------------------------
    # Fight rows
    # -------------------------

    fight_rows = soup.select(
        ".b-fight-details__table-body .b-fight-details__table-row"
    )

    print(f"\nNumber of fights: {len(fight_rows)}")

    for row in fight_rows:

        # -------------------------
        # Fighters
        # -------------------------

        fighters = row.select("a.b-link_style_black")

        fighter_a = fighters[0].get_text(strip=True)
        fighter_b = fighters[1].get_text(strip=True)

        # -------------------------
        # Fight URL
        # -------------------------

        fight_url = row["data-link"]

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
            result = result_flag.get_text(strip=True).lower()
        else:
            result = None

        # UFC 300 lists the winner first when a "win"
        # flag is present.
        #
        # We will revisit this logic when we encounter
        # draws / no contests in other events.
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

        # -------------------------
        # Print fight
        # -------------------------

        print()
        print(f"{fighter_a} vs {fighter_b}")
        print(f"Winner: {winner}")
        print(f"Weight class: {weight_class}")
        print(f"Method: {method}")
        print(f"Round: {round_number}")
        print(f"Time: {fight_time}")
        print(f"Fight URL: {fight_url}")


if __name__ == "__main__":
    main()