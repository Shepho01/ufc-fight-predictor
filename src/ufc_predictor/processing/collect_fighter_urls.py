from pathlib import Path
import json


def main():
    input_dir = Path("data/processed/fights/cleaned")
    output_path = Path("data/fighter_urls.txt")

    fighter_urls = set()

    for fight_path in sorted(input_dir.glob("*_clean.json")):
        fight_data = json.loads(
            fight_path.read_text(encoding="utf-8")
        )

        for side in ("fighter_a", "fighter_b"):
            fighter_id = fight_data[side]["fighter_id"]

            fighter_urls.add(
                f"http://ufcstats.com/fighter-details/{fighter_id}"
            )

    if not fighter_urls:
        print("No fighters found. Check your cleaned fight folder.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        "\n".join(sorted(fighter_urls)) + "\n",
        encoding="utf-8",
    )

    print(
        f"Saved {len(fighter_urls)} fighter URLs "
        f"to {output_path}"
    )


if __name__ == "__main__":
    main()