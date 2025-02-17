## 1. Code

Only one line conceptually changed — how the browser process comes into existence:

```python
# Traditional: Playwright launches and owns a local browser process
browser = playwright.chromium.launch(headless=True)

# Browserbase: Playwright attaches to a browser process running elsewhere
session = bb.sessions.create(project_id=BROWSERBASE_PROJECT_ID)
browser = playwright.chromium.connect_over_cdp(session.connect_url)
```

Everything downstream — `page.goto()`, locators, `page.screenshot()` — is identical
Playwright API. That's the whole trick: Browserbase doesn't replace Playwright, it
replaces *where the browser lives*. `connect_over_cdp` speaks the Chrome DevTools
Protocol (CDP), the same wire protocol Playwright already uses to control local
Chromium — so from Playwright's point of view, a remote Browserbase browser and a
local one are indistinguishable.

## 2. What happens when you call `bb.sessions.create()`

1. Your machine sends a request to the Browserbase API with your API key and
   project ID (plus optional settings: proxies, ad-blocking, captcha solving,
   recording, viewport, region).
2. Browserbase provisions an **isolated, real Chromium instance** in its own
   cloud infrastructure — not a shared/pooled browser, a dedicated one for this
   session — and returns a `connect_url` (a CDP WebSocket endpoint) plus a
   `session.id`.
3. Your Playwright process opens a WebSocket to that URL via `connect_over_cdp`.
   From that point on, every Playwright command (navigate, click, type, screenshot)
   is serialized as a CDP message and sent over that socket to the remote browser.
4. The remote browser executes the action and streams results/events back the
   same way. To your script, latency aside, it behaves like a local browser.
5. Browserbase also records the full session (DOM snapshots + network + console),
   viewable/replayable at `https://browserbase.com/sessions/{session.id}` — useful
   for debugging without adding any logging code yourself.
6. When you call `browser.close()`, the CDP connection ends; the underlying cloud
   session then terminates per your configured timeout/keep-alive settings.

## 3. Why this is better than the traditional approach

The "traditional approach" for automated browser workloads (scraping, testing,
web agents) is: install Chromium/Chrome yourself, run it headless on a VM/container
you manage, and scale it by running more VMs/containers. That sounds simple until
it needs to run in production. What breaks in practice:

| Problem with self-hosted headless Chrome | How Browserbase addresses it |
|---|---|
| **Bot detection / fingerprinting.** Headless Chrome has a distinct fingerprint (`navigator.webdriver`, missing plugins, timing signatures, etc.) that services like Cloudflare/DataDome/PerimeterX detect and block. | Sessions run with fingerprint-evasion and rotating residential/datacenter proxies baked in, so traffic looks like a real user's browser, not a bot farm. |
| **CAPTCHAs.** You hit a CAPTCHA and your automation just stalls or fails. | `browser_settings={"solveCaptchas": True}` handles CAPTCHA challenges automatically mid-session. |
| **Infra ops burden.** You own patching Chromium, matching driver versions, handling crashed/zombie processes, and provisioning enough compute for peak concurrency. | Browserbase runs and patches the browsers; you just request a session. Scaling to N concurrent sessions is an API call, not a fleet of VMs you manage. |
| **Memory/CPU cost of headless Chrome at scale.** Each Chrome instance is 150–300MB+ RAM; running hundreds concurrently means hundreds of GB and careful process lifecycle management. | The compute lives on Browserbase's infrastructure, not your app server/CI runner — your process only holds a lightweight WebSocket connection. |
| **No visibility when something goes wrong.** A failure in CI headless mode means digging through logs and maybe a screenshot you remembered to capture. | Every session is recorded automatically (DOM + network + console) and replayable from a URL — no extra instrumentation code needed. |
| **IP reputation.** Requests all originate from your own known datacenter/CI IP ranges, which get blocklisted quickly at any real scale. | Built-in proxy network spreads and rotates egress IPs. |
| **Cold start / environment drift.** "Works on my machine" issues from local Chrome version mismatches vs. CI vs. production. | One consistent, managed browser environment regardless of where your code runs (laptop, CI, serverless function). |

## 4. When the traditional approach is still fine

Browserbase adds most value when you're dealing with real-world websites that
actively resist automation (auth walls, bot detection, CAPTCHAs) or when you need
to scale concurrent sessions without managing infrastructure. For simple, trusted,
low-volume targets — like this repo's local demo hitting `playwright.dev` — a
locally launched browser is simpler and has zero external dependency.

## 5. Key takeaway

Browserbase is **infrastructure for the browser, not a replacement for Playwright**.
You keep writing Playwright automation exactly as you already know it; Browserbase
just gives that automation a production-grade, undetectable, observable place to run.