# Browserbase MCP Server — Setup

This is the fourth way to drive a Browserbase browser, alongside the three
Python scripts in [src/](src/) — including [src/stagehand_demo.py](src/stagehand_demo.py),
which calls the exact same `act`/`extract`/`observe` primitives this server
exposes, just from your own code instead of from an LLM client. This is a
fundamentally different integration point, so read this before wiring it up.

## The four approaches, side by side

| | **Raw SDK** (`browserbase_playwright_demo.py`) | **Stagehand** (`stagehand_demo.py`) | **MCP server** |
|---|---|---|---|
| Who writes the automation | You, in Python (`page.goto`, `page.click`...) | You, in Python, but with AI-native calls | The LLM client itself, by calling tools |
| Where the logic lives | Your `.py` file | Your `.py` file | Not your code — a server process the agent talks to |
| How you invoke it | `python src/browserbase_playwright_demo.py` | `python src/stagehand_demo.py` | Claude (or any MCP client) calls tools like `navigate`, `act`, `extract` on its own |
| Selectors | CSS/text locators you write | None — natural language, resolved by AI | None — natural language, resolved by AI |
| Best for | Deterministic, repeatable scripts (tests, scheduled scrapers) | Agent-style automation you still author and control in code | Letting an agent (Claude Code, Claude Desktop, Cursor) browse the web on its own during a conversation |

The punchline on your second question: **the MCP server isn't a separate
technology from Stagehand — it's Stagehand wrapped in a server.** Under the
hood, the MCP server's `act`/`observe`/`extract` tools are Stagehand calls.
Stagehand is the library; the MCP server is that library exposed over MCP so
an LLM client can call it directly without you writing the calling code.

## What the MCP server exposes

Package: [`@browserbasehq/mcp`](https://www.npmjs.com/package/@browserbasehq/mcp) (Node/npx — no relation to this repo's Python venv)

| Tool | Does |
|---|---|
| `start` / `end` | Create / close a Browserbase session |
| `navigate` | Go to a URL |
| `act` | Perform an action described in natural language (e.g. "click the sign in button") |
| `observe` | List actionable elements currently on the page |
| `extract` | Pull structured data off the current page |

## Setup

### Option A — Hosted (recommended, no local process to manage)

Register it with Claude Code directly:

```powershell
claude mcp add --transport http browserbase "https://mcp.browserbase.com/mcp?browserbaseApiKey=YOUR_BROWSERBASE_API_KEY"
```

Or drop this repo's [.mcp.json.example](.mcp.json.example) in as `.mcp.json` (project-scoped, picked up automatically by Claude Code) and fill in your real key:

```powershell
copy .mcp.json.example .mcp.json
```

```json
{
  "mcpServers": {
    "browserbase": {
      "url": "https://mcp.browserbase.com/mcp?browserbaseApiKey=REPLACE_WITH_YOUR_API_KEY"
    }
  }
}
```

`.mcp.json` is gitignored — same reasoning as `.env`, it will hold a real key once filled in.

### Option B — Local STDIO (runs the server as a child process via npx)

```json
{
  "mcpServers": {
    "browserbase": {
      "command": "npx",
      "args": ["@browserbasehq/mcp"],
      "env": {
        "BROWSERBASE_API_KEY": "REPLACE_WITH_YOUR_API_KEY",
        "GEMINI_API_KEY": "REPLACE_WITH_YOUR_GEMINI_API_KEY"
      }
    }
  }
}
```

Requires Node.js + npx on your machine. `GEMINI_API_KEY` is needed here because
local STDIO mode runs Stagehand's `act`/`observe`/`extract` reasoning itself
(default model `google/gemini-2.5-flash-lite`) rather than delegating that to
Browserbase's hosted endpoint — override with `--modelName`/`--modelApiKey` to
use a different model.

## Trying it out

Once `.mcp.json` (or `claude mcp add`) is in place with a real API key, restart
Claude Code (or run `/mcp` to check connection status) and just ask in a
conversation, e.g.:

> "Use the browserbase MCP tools to go to playwright.dev and tell me what the
> hero heading says."

Claude will call `start` → `navigate` → `observe`/`extract` on its own — no
Python code runs for this path at all. You can still open the session replay
at `https://browserbase.com/sessions/{id}` the same as with the SDK scripts.

## Why this matters for agents specifically

The SDK scripts in this repo are automation *you* wrote for the agent to run
as a tool call. The MCP server flips that: the agent drives the browser
directly, deciding in real time what to click/extract based on what it sees —
useful when the task is open-ended ("find X and summarize it") rather than a
fixed, known sequence of steps. Use the SDK approach when you know the exact
flow in advance; reach for MCP/Stagehand when the agent needs to figure the
flow out itself.
