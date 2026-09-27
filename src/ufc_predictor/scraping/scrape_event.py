from pathlib import Path

from playwright.sync_api import sync_playwright

EVENT_URL = "http://ufcstats.com/event-details/6750e338922a099d"


def fetch_event_page(url: str) -> str:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)

        page = browser.new_page()

        page.goto(url, wait_until="domcontentloaded")

        # Give the browser check a chance to complete
        page.wait_for_timeout(3000)

        # Wait for the actual UFC event page to appear
        page.wait_for_selector(
            ".b-fight-details__table-row",
            timeout=15000
        )

        html = page.content()

        browser.close()

        return html


def save_html(html: str, file_path: str) -> None:
    path = Path(file_path)

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(html, encoding="utf-8")


def main():
    html = fetch_event_page(EVENT_URL)

    print("Successfully downloaded event page")
    print(f"HTML length: {len(html)} characters")

    save_html(html, "data/raw/events/ufc_300.html")

    print("Saved HTML to data/raw/events/ufc_300.html")


if __name__ == "__main__":
    main()