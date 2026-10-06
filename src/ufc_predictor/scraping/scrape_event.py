from pathlib import Path

from playwright.sync_api import sync_playwright


EVENT_URL = "http://ufcstats.com/event-details/00e11b5c8b7bfeeb"

OUTPUT_PATH = Path(
    "data/raw/events/ufc_324.html"
)


def scrape_event(url):
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
    html = scrape_event(
        EVENT_URL
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        html,
        encoding="utf-8"
    )

    print(
        f"Saved event HTML to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()