from pathlib import Path
import json


def main():
    input_dir = Path("data/processed/fighters/parsed")
    output_path = Path("data/history_fight_urls.txt")

    fight_urls = set()

    for path in sorted(input_dir.glob("*_raw.json")):
        fighter = json.loads(
            path.read_text(encoding="utf-8")
        )

        for fight in fighter.get("fight_history", []):
            fight_urls.add(fight["fight_url"])

    if not fight_urls:
        print("No fight-history URLs found.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        "\n".join(sorted(fight_urls)) + "\n",
        encoding="utf-8",
    )

    print(
        f"Saved {len(fight_urls)} unique fight URLs "
        f"to {output_path}"
    )


if __name__ == "__main__":
    main()