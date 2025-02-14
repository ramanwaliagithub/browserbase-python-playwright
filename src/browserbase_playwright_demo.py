"""
  local:       playwright.chromium.launch(headless=True)
  browserbase: playwright.chromium.connect_over_cdp(session.connect_url)

Setup:
  1. pip install -r requirements.txt
  2. python src/browserbase_playwright_demo.py
"""

import os

from browserbase import Browserbase
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright

load_dotenv()

# --- Replace this
BROWSERBASE_API_KEY = os.environ.get("BROWSERBASE_API_KEY", "REPLACE_WITH_YOUR_API_KEY")
BROWSERBASE_PROJECT_ID = os.environ.get("BROWSERBASE_PROJECT_ID", "REPLACE_WITH_YOUR_PROJECT_ID")

TARGET_URL = "https://playwright.dev/"

bb = Browserbase(api_key=BROWSERBASE_API_KEY)


def run(playwright: Playwright) -> None:
    # Ask Browserbase to spin up a remote, managed browser session.
    session = bb.sessions.create(
        project_id=BROWSERBASE_PROJECT_ID,
        # proxies=True routes through Browserbase's proxy network but requires
        # a paid plan — leave it off on the Free plan, turn on if you upgrade.
        browser_settings={
            "blockAds": True,
            "recordSession": True,  # lets us replay this run afterwards
        },
    )
    print(f"Session live view / replay: https://browserbase.com/sessions/{session.id}")

    # Attach Playwright to that remote browser over the Chrome DevTools
    # Protocol instead of launching a local one.
    chromium = playwright.chromium
    browser = chromium.connect_over_cdp(session.connect_url)
    context = browser.contexts[0]
    page = context.pages[0]

    page.goto(TARGET_URL)

    title = page.title()
    heading = page.locator("h1").first.inner_text()
    nav_links = page.locator("nav a").count()

    print(f"Page title:   {title}")
    print(f"H1 heading:   {heading}")
    print(f"Nav links:    {nav_links}")

    page.screenshot(path="browserbase_screenshot.png")
    print("Saved screenshot to browserbase_screenshot.png")

    page.close()
    # Note: browser.close() ends the CDP connection; the remote session
    # itself then closes per your Browserbase session timeout settings.
    browser.close()
    print("Done!")


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
