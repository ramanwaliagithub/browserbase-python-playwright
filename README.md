# Browserbase + Playwright Python POC

A minimal, side-by-side comparison of running Playwright locally vs. running it
through [Browserbase](https://www.browserbase.com/).

```
BrowserbasePOC/
├── src/
│   ├── local_playwright_demo.py       # baseline: local headless Chromium
│   ├── browserbase_playwright_demo.py # same script, browser runs on Browserbase
│   └── stagehand_demo.py              # same target site, driven with AI act/extract/observe
├── requirements.txt
├── .env.example                       # copy to .env and fill in real values
├── .mcp.json.example                  # copy to .mcp.json for the MCP server approach (Step 7)
├── BROWSERBASE_EXPLAINED.md           # how it works + why it beats self-hosted Chrome
├── MCP_SETUP.md                       # MCP server approach: setup + how it differs from the SDK/Stagehand
└── src_old/bb.py                      # earlier scratch script (kept as-is)
```

## Step 1 — Install dependencies

A `.venv` already exists in this repo with `playwright` and `browserbase` installed.
If you need to (re)install everything:

```powershell
.venv\Scripts\pip.exe install -r requirements.txt
.venv\Scripts\playwright.exe install chromium
```

## Step 2 — Run the local baseline (no Browserbase needed)

```powershell
.venv\Scripts\python.exe src\local_playwright_demo.py
```

This launches Chromium on your machine, visits `playwright.dev`, prints the
title/heading, and saves `local_playwright_screenshot.png`. Confirms your
Playwright install works before adding Browserbase.

## Step 3 — Get your Browserbase credentials

1. Sign up / log in at https://www.browserbase.com/
2. Go to **Overview** in the dashboard.
3. Copy your **API Key** and **Project ID**.

## Step 4 — Configure credentials

```powershell
copy .env.example .env
```

Then edit `.env`:

```
BROWSERBASE_API_KEY=<paste your real key here>
BROWSERBASE_PROJECT_ID=<paste your real project id here>
```

> `.env` is gitignored — never commit real keys. The scripts fall back to
> obvious placeholder strings (`REPLACE_WITH_YOUR_API_KEY`) if `.env` is missing,
> so it's clear at a glance when credentials haven't been set yet.

## Step 5 — Run the Browserbase-integrated version

```powershell
.venv\Scripts\python.exe src\browserbase_playwright_demo.py
```

This creates a remote session on Browserbase, attaches Playwright to it over
CDP, runs the exact same navigation/scrape as Step 2, and prints a session
replay URL (`https://browserbase.com/sessions/<id>`) where you can watch a
recording of the run.

## Step 6 — Run the Stagehand version (AI-driven actions, still your code)

```powershell
.venv\Scripts\python.exe src\stagehand_demo.py
```

Same target site, same Browserbase session underneath, but instead of CSS
locators it calls `stagehand.act("Click the 'Docs' link...")`,
`stagehand.extract(...)`, and `stagehand.observe(...)` — natural-language
actions resolved to real DOM interactions for you. Useful when a page's
structure is unknown or changes often. Optionally set `MODEL_API_KEY` in
`.env` to pick a specific LLM; omit it and Browserbase uses a default.

## Step 7 — Read the explainer

Open [BROWSERBASE_EXPLAINED.md](BROWSERBASE_EXPLAINED.md) for a breakdown of
what `bb.sessions.create()` + `connect_over_cdp()` actually do under the hood,
and why that beats self-managing headless Chrome (bot detection, CAPTCHAs,
infra ops, IP reputation, observability).

## Step 8 — Try the MCP server approach (agent-driven, no Python at all)

The three scripts above are automation *you* wrote in Python. There's a
fourth option: the [Browserbase MCP server](MCP_SETUP.md), which lets an MCP
client like Claude Code drive the browser directly via natural-language tool
calls (`navigate`, `act`, `observe`, `extract`) — no script to run at all.
It's the same engine as `stagehand_demo.py`, just called by the LLM client
instead of by your code. See [MCP_SETUP.md](MCP_SETUP.md) for setup and the
full comparison.

## Next steps / options worth exploring

- `browser_settings={"solveCaptchas": True}` — automatic CAPTCHA solving
- `proxies=True` (or a specific proxy config) — route through Browserbase's proxy network
- `keep_alive` — keep a session warm across multiple script runs
- Browserbase **Contexts** — persist cookies/localStorage across sessions (e.g. stay logged in)
- Browserbase **Live View** — watch/interact with a session in real time while it runs
