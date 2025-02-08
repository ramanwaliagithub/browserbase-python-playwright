from playwright.sync_api import Playwright, sync_playwright

TARGET_URL = "https://playwright.dev/"


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(TARGET_URL)

    title = page.title()
    heading = page.locator("h1").first.inner_text()
    nav_links = page.locator("nav a").count()

    print(f"Page title:   {title}")
    print(f"H1 heading:   {heading}")
    print(f"Nav links:    {nav_links}")

    page.screenshot(path="local_playwright_screenshot.png")
    print("Saved screenshot to local_playwright_screenshot.png")

    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)