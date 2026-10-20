"""Download one or more UFCStats fight pages, saving them by fight ID."""
import argparse
from pathlib import Path
import re
import time
from urllib.parse import urlsplit


def get_fight_id(url):
    parsed = urlsplit(url)

    if (
        parsed.scheme not in ("http", "https")
        or parsed.netloc.lower() not in (
            "ufcstats.com",
            "www.ufcstats.com",
        )
    ):
        raise ValueError(f"Expected a UFCStats URL: {url}")

    match = re.fullmatch(
        r"/fight-details/([0-9a-f]{16})/?",
        parsed.path,
    )

    if not match or parsed.query or parsed.fragment:
        raise ValueError(f"Invalid fight-details URL: {url}")

    return match.group(1)


def fetch_fight_page(page, url):
    response = page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    if response is None or not response.ok:
        status = (
            response.status
            if response is not None
            else "no response"
        )
        raise RuntimeError(
            f"Could not download {url}: {status}"
        )

    page.wait_for_selector(
        ".b-fight-details",
        timeout=15000,
    )

    return page.content()


def save_html(html, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    # Finish writing before replacing the destination file.
    temporary = path.with_suffix(".html.tmp")
    temporary.write_text(html, encoding="utf-8")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "urls",
        nargs="*",
        help="UFCStats fight-details URLs",
    )

    parser.add_argument(
        "--urls-file",
        type=Path,
        help="One URL per line; # comments allowed",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw/fights"),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Download existing files again",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Hide the browser window",
    )

    args = parser.parse_args()

    urls = list(args.urls)

    if args.urls_file:
        try:
            lines = args.urls_file.read_text(
                encoding="utf-8-sig"
            ).splitlines()

            urls.extend(
                line.strip()
                for line in lines
                if line.strip()
                and not line.lstrip().startswith("#")
            )
        except OSError as error:
            parser.error(str(error))

    if not urls:
        parser.error("Provide fight URLs or --urls-file")

    # Validate URLs and remove duplicate fight IDs.
    fights = {}

    for url in urls:
        try:
            fight_id = get_fight_id(url)
            fights[fight_id] = url
        except ValueError as error:
            parser.error(str(error))

    pending = []

    for fight_id, url in fights.items():
        path = args.output_dir / f"{fight_id}.html"

        if (
            path.exists()
            and path.stat().st_size > 0
            and not args.overwrite
        ):
            print(f"Skipped existing file: {path}")
        else:
            pending.append((url, path))

    if not pending:
        print("No pages to download.")
        return

    from playwright.sync_api import sync_playwright

    failures = []
    saved = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=args.headless
        )

        try:
            page = browser.new_page()

            for index, (url, path) in enumerate(pending):
                if index:
                    time.sleep(2)

                try:
                    html = fetch_fight_page(page, url)
                    save_html(html, path)

                    saved += 1
                    print(f"Saved: {path}")

                except Exception as error:
                    failures.append(url)
                    print(f"FAILED: {url}\n  {error}")

        finally:
            browser.close()

    print(f"Saved {saved}; failed {len(failures)}.")

    if failures:
        print("Retry these URLs:")

        for url in failures:
            print(url)

        raise SystemExit(1)


if __name__ == "__main__":
    main()