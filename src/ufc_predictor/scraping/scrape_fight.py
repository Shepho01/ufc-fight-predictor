from pathlib import Path

from playwright.sync_api import sync_playwright


FIGHT_URL = "http://ufcstats.com/fight-details/256894b49303537b"


def fetch_fight_page(url: str) -> str:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)

        page = browser.new_page()

        page.goto(
            url,
            wait_until="domcontentloaded"
        )

        page.wait_for_selector(
            ".b-fight-details",
            timeout=15000
        )

        html = page.content()

        browser.close()

        return html


def save_html(html: str, file_path: str) -> None:
    path = Path(file_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        html,
        encoding="utf-8"
    )


def main():
    html = fetch_fight_page(FIGHT_URL)

    print("Successfully downloaded fight page")
    print(f"HTML length: {len(html)} characters")

    save_html(
        html,
        "data/raw/fights/makhachev_vs_volkanovski.html"
    )

    print(
        "Saved HTML to "
        "data/raw/fights/makhachev_vs_volkanovski.html"
    )


if __name__ == "__main__":
    main()