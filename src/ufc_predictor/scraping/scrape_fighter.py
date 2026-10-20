from pathlib import Path
import time

from playwright.sync_api import sync_playwright


def scrape_fighter(page, url):
    response = page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    if response is None or not response.ok:
        raise RuntimeError(
            "The fighter page could not be downloaded."
        )

    page.wait_for_selector(
        ".b-content__title-highlight",
        timeout=15000,
    )

    page.wait_for_selector(
        ".b-list__info-box",
        timeout=15000,
    )

    return page.content()


def main():
    urls_path = Path("data/fighter_urls.txt")
    output_dir = Path("data/raw/fighters")

    urls = urls_path.read_text(
        encoding="utf-8"
    ).splitlines()

    output_dir.mkdir(parents=True, exist_ok=True)

    saved = 0
    skipped = 0
    failures = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        try:
            page = browser.new_page()

            for url in urls:
                url = url.strip()

                if not url:
                    continue

                fighter_id = url.rstrip("/").split("/")[-1]
                output_path = output_dir / f"{fighter_id}.html"

                if (
                    output_path.exists()
                    and output_path.stat().st_size > 0
                ):
                    print(f"Skipped existing file: {output_path}")
                    skipped += 1
                    continue

                try:
                    html = scrape_fighter(page, url)

                    temporary_path = output_path.with_suffix(
                        ".html.tmp"
                    )

                    temporary_path.write_text(
                        html,
                        encoding="utf-8",
                    )

                    temporary_path.replace(output_path)

                    print(f"Saved: {output_path}")
                    saved += 1

                except Exception as error:
                    print(f"Failed: {url}")
                    print(f"Reason: {error}")
                    failures.append(url)

                time.sleep(2)

        finally:
            browser.close()

    print(
        f"\nSaved: {saved}; "
        f"skipped: {skipped}; "
        f"failed: {len(failures)}"
    )

    if failures:
        print("\nFailed URLs:")
        for url in failures:
            print(url)


if __name__ == "__main__":
    main()