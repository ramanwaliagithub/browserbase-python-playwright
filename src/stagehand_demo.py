"""
A third way to automate playwright.dev, alongside local_playwright_demo.py
(raw Playwright, local) and browserbase_playwright_demo.py (raw Playwright,
remote via CDP): Stagehand's AI-native API.

Where the other two scripts say "find this CSS selector and click it",
Stagehand lets you say "click the thing described in English" and it
resolves that to a real DOM action itself. The browser still runs on
Browserbase — this only changes how you *describe* actions, not where the
browser lives.

This is the same engine the Browserbase MCP server's act/observe/extract
tools use (see MCP_SETUP.md) — that server exposes these exact calls to an
MCP client. Here we call them directly from our own Python code instead,
which is the right choice when you want AI-driven actions but still want to
own the control flow (loops, branching, error handling) in your own script.

Setup:
  1. pip install -r requirements.txt        (installs the `stagehand` package)
  2. Copy .env.example to .env and fill in:
       BROWSERBASE_API_KEY=<your key>
       MODEL_API_KEY=<optional - only needed to pick a specific LLM for
                       act/extract/observe; Browserbase uses a default
                       model if this is omitted>
  3. python src/stagehand_demo.py
"""

import asyncio
import os

from dotenv import load_dotenv
from pydantic import BaseModel
from stagehand import Stagehand, browserbase

load_dotenv()

# --- Placeholders: replace via your .env file, not by editing this file ---
BROWSERBASE_API_KEY = os.environ.get("BROWSERBASE_API_KEY", "REPLACE_WITH_YOUR_API_KEY")
MODEL_API_KEY = os.environ.get("MODEL_API_KEY")  # optional — see setup notes above

TARGET_URL = "https://playwright.dev/"


class PageSummary(BaseModel):
    heading: str
    one_sentence_summary: str


async def main() -> None:
    # Same session creation as the raw SDK demo, just through Stagehand's
    # browserbase.launch() helper instead of bb.sessions.create().
    browser = await browserbase.launch(
        api_key=BROWSERBASE_API_KEY,
        browser_settings={
            "block_ads": True,
            "record_session": True,
        },
    )
    print(f"Session live view / replay: https://browserbase.com/sessions/{browser.session_id}")

    try:
        stagehand = await Stagehand.create(
            browser=browser,
            model_api_key=MODEL_API_KEY,
        )

        page = (await browser.context.pages())[0]
        await page.goto(TARGET_URL)

        # extract(): ask for structured data back — no selectors written by us.
        summary = await stagehand.extract(
            "Read the hero heading and summarize in one sentence what this "
            "project does.",
            PageSummary,
        )
        print(f"Heading:  {summary.data.heading}")
        print(f"Summary:  {summary.data.one_sentence_summary}")

        # observe(): ask what's clickable instead of guessing selectors ourselves.
        actions = await stagehand.observe("Find the links in the top navigation bar.")
        print(f"Found {len(actions.data)} nav action(s), first: {actions.data[0].description!r}")

        # act(): describe an action in English; Stagehand performs the DOM interaction.
        result = await stagehand.act("Click the 'Docs' link in the navigation bar.")
        print(f"Act result: success={result.data.success} — {result.data.message}")

        await stagehand.close()
    finally:
        browser.close()


if __name__ == "__main__":
    asyncio.run(main())
