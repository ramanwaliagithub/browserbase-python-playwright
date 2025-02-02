from playwright.sync_api import Playwright, sync_playwright
from browserbase import Browserbase
import os

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])


def run(playwright: Playwright) -> None:
    session = bb.sessions.create()
    print("Session recording URL:", f"https://browserbase.com/sessions/{session.id}")

    chromium = playwright.chromium
    browser = chromium.connect_over_cdp(session.connect_url)
    context = browser.contexts[0]
    page = context.pages[0]

    page.goto("https://browserbase.com/")
    page_title = page.title()
    print(page_title)

    page.close()
    browser.close()
    print("Done!")


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)