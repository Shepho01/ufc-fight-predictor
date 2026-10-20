from pathlib import Path
import json


def main():
    input_dir = Path("data/processed/fights/cleaned")
    output_path = Path("data/event_urls.txt")

    event_urls = set()

    for fight_path in sorted(input_dir.glob("*_clean.json")):
        fight_data = json.loads(
            fight_path.read_text(encoding="utf-8")
        )

        event_id = fight_data["fight"]["event_id"]

        event_urls.add(
            f"http://ufcstats.com/event-details/{event_id}"
        )

    if not event_urls:
        print("No events found. Check your cleaned fight folder.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        "\n".join(sorted(event_urls)) + "\n",
        encoding="utf-8",
    )

    print(f"Saved {len(event_urls)} event URLs to {output_path}")


if __name__ == "__main__":
    main()