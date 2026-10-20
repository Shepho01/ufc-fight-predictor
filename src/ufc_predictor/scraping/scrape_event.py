from pathlib import Path

from playwright.sync_api import sync_playwright

import time

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

        response = page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        if response is None or not response.ok:
            browser.close()
            raise RuntimeError("The event page could not be downloaded.")

        page.wait_for_selector(
            ".b-fight-details__table",
            timeout=15000,
        )

        html = page.content()

        browser.close()

        return html


def main():
    urls_path = Path("data/event_urls.txt")
    output_dir = Path("data/raw/events")

    urls = urls_path.read_text(
        encoding="utf-8"
    ).splitlines()

    output_dir.mkdir(parents=True, exist_ok=True)

    for url in urls:
        url = url.strip()

        if not url:
            continue

        event_id = url.rstrip("/").split("/")[-1]
        output_path = output_dir / f"{event_id}.html"

        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"Skipped existing file: {output_path}")
            continue

        try:
            html = scrape_event(url)

            output_path.write_text(
                html,
                encoding="utf-8",
            )

            print(f"Saved: {output_path}")

        except Exception as error:
            print(f"Failed: {url}")
            print(f"Reason: {error}")

        time.sleep(2)


if __name__ == "__main__":
    main()