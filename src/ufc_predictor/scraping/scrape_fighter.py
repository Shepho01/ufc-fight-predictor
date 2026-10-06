from pathlib import Path

from playwright.sync_api import sync_playwright


FIGHTER_URL = "http://ufcstats.com/fighter-details/e1248941344b3288"

OUTPUT_PATH = Path(
    "data/raw/fighters/alex_volkanovski.html"
)


def scrape_fighter(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page.goto(
            url,
            wait_until="networkidle"
        )

        html = page.content()

        browser.close()

        return html


def main():
    html = scrape_fighter(FIGHTER_URL)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        html,
        encoding="utf-8"
    )

    print(
        f"Saved fighter HTML to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()