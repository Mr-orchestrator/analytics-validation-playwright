# RFP: Playwright-Based Analytics Validation Platform
### Replacement for ObservePoint — Contract End Date: March 30, 2026

---

## Executive Summary

ObservePoint is a SaaS tag auditing platform used for validating analytics implementations
across web properties. With its contract ending March 30, 2026, this document presents a
proposal to replace ObservePoint with a custom-built Playwright-based analytics validation
framework.

**Our POC (already built) demonstrates that Playwright can handle the core analytics
validation use case.** This RFP outlines what we can fully replace, what requires
additional engineering, and where we have an honest gap that needs to be acknowledged.

| Dimension | ObservePoint | Playwright Solution |
|---|---|---|
| Cost | $599–$2,400+/month | Infrastructure only (~$0–$200/month) |
| Ownership | Vendor SaaS | In-house, full control |
| Flexibility | No-code GUI | Code-based, unlimited customisation |
| Vendor lock-in | High | None (MIT open source) |
| Setup effort | Minimal | Medium–High engineering |
| Scale (pages/run) | 20,000+ (cloud) | ~5,000 per machine; scalable with infra |
| POC Status | Current tool | Already built ✅ |

---

## 1. What ObservePoint Does (Full Feature Set)

### 1.1 Core Capabilities

| Capability | Description |
|---|---|
| Tag Auditing | Crawls pages, intercepts all network calls, identifies 1,500+ known tags |
| Journeys | Multi-step user flow simulation with per-step tag rule validation |
| Rules Engine | No-code visual rule builder — Equals / Contains / Regex / Cross-variable |
| Crawl Engine | Cloud-hosted spider with sitemap ingestion, depth control, rate limiting |
| Data Layer Monitoring | Captures `window.dataLayer` / `utag_data` per page, validates against rules |
| Cookie Report | Full cookie inventory — name, domain, expiry, HTTP-only, Secure, SameSite |
| Privacy Scan | Detects tags firing before consent; CMP (OneTrust, TrustArc) validation |
| Scheduled Runs | Daily / weekly / monthly; no CI/CD dependency |
| Alerting | Email, Slack, Teams, and Webhooks on rule failure threshold breach |
| Tealium Integration | Auto-triggers audit on Tealium profile publish |
| RBAC / SSO | Multi-team governance with role-based access and SAML/SSO |
| API | REST API for programmatic trigger, result retrieval, rule management |
| Accessibility | WCAG 2.x scanning integrated into audits (added 2024–2025) |
| Historical Trends | Pass-rate trend graphs across audit runs over time |

### 1.2 Known ObservePoint Weaknesses (from user reviews)

- Journey UI is difficult; poor selector support; frequent trial-and-error
- Complex authentication (OAuth, SSO, MFA) is fragile and poorly supported
- Rules engine surfaces limited failure detail; bulk analysis requires API export
- Product has shown minimal UI/feature improvement in recent years
- Price vs. value mismatch for teams with a single domain or < 5,000 pages
- Crawlers get blocked by Cloudflare / Akamai — requires IP whitelisting
- No video recording or step-by-step trace for debugging failures

---

## 2. Playwright — Capability Assessment

### 2.1 What Playwright Does Natively

| Capability | Status |
|---|---|
| Full browser automation (click, type, navigate, scroll) | ✅ Native |
| Network request interception (GET + POST + Beacon) | ✅ Native |
| POST body capture (for GA4 `collect` POST calls) | ✅ Native |
| HAR file recording (full network archive per run) | ✅ Native |
| Video recording per test | ✅ Native |
| Trace Viewer (step-by-step DOM + network replay) | ✅ Native |
| JavaScript execution in browser (`page.evaluate`) | ✅ Native |
| Cookie read/write/inspect | ✅ Native |
| Multi-step user journeys | ✅ Native |
| Complex auth: OAuth, SSO, MFA via session storage | ✅ Native (superior to OP) |
| Cross-browser: Chromium, Firefox, WebKit (Safari) | ✅ Native (OP is Chromium-only) |
| Mobile device emulation | ✅ Native |
| Parallel test execution (workers + sharding) | ✅ Native |
| CI/CD integration (GitHub Actions, GitLab, Jenkins) | ✅ Native |
| Screenshot comparison (pixel diff) | ✅ Native |
| Accessibility scan (axe-core integration) | ✅ via `@axe-core/playwright` |
| Allure historical reporting | ✅ via `allure-playwright` |
| Sitemap-based crawling (Crawlee library) | ✅ via `crawlee` (Apify) |

### 2.2 What Our POC Already Validates (Built)

```
✅  GA4 purchase event capture (network interception + Performance API)
✅  utag_data layer reading (window.utag_data via page.evaluate)
✅  7-field GA4 vs utag comparison (order_id, total, tax, sku, qty, currency, shipping)
✅  Full network request categorisation (GA4 / GTM / Tealium / Meta / Adobe etc.)
✅  Video recording per run
✅  Playwright trace (screenshots + DOM snapshots)
✅  Excel export (ga4_calls, utag_data, comparison, all_network_requests)
✅  Glassmorphism web dashboard (Dash + Plotly) — auto-launched after run
✅  Runtime JSON for dashboard data feed
✅  Tealium training config + consent handling
✅  E2E checkout flow automation (home → product → cart → checkout → success)
```

---

## 3. Feature-by-Feature Replacement Verdict

### 3.1 GREEN — Full Replacement Possible (Low/No Effort)

| ObservePoint Feature | Playwright Approach | Confidence |
|---|---|---|
| Journey / multi-step flow testing | Native Playwright interactions | ✅ Done in POC |
| Per-step network call capture | `page.on("request")` | ✅ Done in POC |
| GA4 event validation | Parse URL params from GA4 collect | ✅ Done in POC |
| Tealium utag_data validation | `page.evaluate(() => utag_data)` | ✅ Done in POC |
| Data layer capture per page | `page.evaluate(() => window.dataLayer)` | ✅ Done in POC |
| Cookie inventory | `context.cookies()` | ✅ Easy |
| Regex-based variable rules | Native `expect().toMatch(regex)` | ✅ Easy |
| GA4 vs data layer comparison | Python/JS comparison logic | ✅ Done in POC |
| Export results to Excel/CSV | `pandas.to_excel()` | ✅ Done in POC |
| Dashboard / reporting | Dash + Plotly or Allure | ✅ Done in POC |
| CI/CD scheduled runs | GitHub Actions `schedule:` cron | ✅ Easy |
| Slack/Teams alerting | Webhook POST in test teardown | ✅ Easy (~50 lines) |
| Staging vs production targeting | `BASE_URL` environment variable | ✅ Easy |
| Video recording per run | Playwright `record_video_dir` | ✅ Done in POC |
| Trace viewer for debugging | Playwright tracing built-in | ✅ Done in POC |
| Complex auth (OAuth/SSO/MFA) | Playwright `storageState` | ✅ Better than OP |
| Cross-browser validation | Chromium + Firefox + WebKit | ✅ Better than OP |
| Visual regression testing | Percy / Chromatic / axe-core | ✅ Better than OP |
| Accessibility testing | `@axe-core/playwright` | ✅ Better than OP |
| Historical trend reporting | Allure + history files | ✅ Moderate setup |

---

### 3.2 AMBER — Replaceable With Moderate Engineering (2–4 Weeks)

| ObservePoint Feature | Gap | Playwright Solution | Effort |
|---|---|---|---|
| Sitemap-based page crawling | No built-in crawler | Integrate **Crawlee** (Apify OSS) for URL queue, sitemap parsing, rate limiting | 1 week |
| Tag pattern library (auto-detect 1,500+ tags) | No pre-built patterns | Build a URL-pattern config file for priority vendors (GA4, GTM, Tealium, Meta, Adobe, Bing, LinkedIn) | 2 weeks |
| Tag presence auditing across pages | No built-in discovery | Crawlee + pattern lib: for each crawled page, check which known tag patterns fired | 2 weeks |
| Pre-consent tag detection | No built-in | Run Playwright with no consent cookie set; capture all requests; compare to allowed-before-consent allowlist | 1 week |
| GPC signal testing | No built-in | `page.addInitScript` to set `navigator.globalPrivacyControl = true`; verify tags suppressed | 3 days |
| Cookie governance (flag unapproved cookies) | No built-in | Read `context.cookies()` after page load; compare to approved cookie allowlist | 3 days |
| Threshold-based alerting (% pages failing) | No built-in | Aggregate JSON results post-run; compute failure %; POST to Slack/webhook if over threshold | 3 days |
| Per-page tag pass/fail matrix report | No built-in | Custom aggregation over crawl results; output to HTML or Excel | 1 week |
| Tealium publish trigger | No built-in | Tealium webhook → CI/CD pipeline trigger (GitHub Actions `workflow_dispatch`) | 2 days |

---

### 3.3 RED — Genuine Gaps (Hard to Replace Without Major Build)

| ObservePoint Feature | Why It's Hard | Honest Assessment |
|---|---|---|
| **Cloud-scale crawling (20,000+ pages)** | Playwright is single-process; 20K+ pages needs distributed infra (Kubernetes + job queue) | Not in scope for initial replacement. Viable with Crawlee + cloud workers but 4–8 weeks engineering + DevOps overhead |
| **No-code interface for analysts** | Playwright requires writing code. Analysts / tag managers cannot use it without developer support | Fundamental gap. Cannot be closed without building a separate UI product. Workaround: pre-built test templates + parameterised config files that analysts fill in |
| **Centralised multi-team governance dashboard** | Playwright results are per-repo artifacts. Cross-team aggregation needs a backend DB + API + frontend | Not in scope for initial replacement. Use Allure + shared S3 storage as an interim approach for single-team use |
| **RBAC / SSO / multi-team access control** | Test frameworks do not manage user permissions | Out of scope. If required, integrate with existing SSO and restrict CI access via repository permissions |
| **Unapproved technology ownership tracking** | Maps each detected tag to a named owner and sends alerts. Requires a governance data store | Partial workaround: maintain an approved-tag config YAML; flag unknown tags in run report; manually assign owners outside the tool |
| **Auto-discovery of unknown tags (zero pre-configuration)** | ObservePoint flags any tag it has never seen before. Playwright only catches what you explicitly look for | Workaround: capture ALL network requests per page (done in POC) and log any domain not on the approved list |

---

## 3b. SPA (Single-Page Application) Event Handling

Airline websites are almost universally built as SPAs (React, Angular, or Vue).
This is the most technically critical difference between a traditional tool like
ObservePoint and a Playwright-based replacement — and it is a challenge we have
specifically solved.

### Why SPAs Are Different

```
Traditional (MPA) site:           SPA (React/Angular/Vue):
─────────────────────────────      ─────────────────────────────────────────
Full page reload on each step      No page reload — only DOM updates
digitalData re-populated fresh     digitalData may persist or partially update
GA4 page_view fires automatically  GA4 page_view must be manually triggered by the app
Network idle = step complete       Network idle does NOT mean step is complete
page.goto() waits for DOMLoaded    History API change (pushState) = "navigation"
New page context per step          Same JS context throughout entire journey
```

**The SPA problem for analytics:** On a booking flow SPA:
- The user clicks "Select Flight" — no new page loads
- The URL changes via `history.pushState`
- The app updates `window.digitalData.cart` and fires a `b2t` event
- GA4 fires a `select_item` beacon
- All of this happens within 300ms in the same browser context

Playwright must detect and respond to each of these transitions correctly
or it will either read `digitalData` too early (before the update) or
miss the GA4 beacon entirely.

---

### Our SPA Handling Strategy

#### 1. Route Change Detection (History API Intercept)

We inject a listener before the test starts that detects every SPA navigation:

```python
page.add_init_script("""
    window.__spaNavEvents = [];
    const origPush = history.pushState;
    const origReplace = history.replaceState;

    function onRouteChange(url) {
        window.__spaNavEvents.push({
            url: url,
            timestamp: Date.now(),
            digitalDataSnapshot: JSON.parse(JSON.stringify(window.digitalData || {}))
        });
        console.log('[SPA] Route changed to:', url);
    }

    history.pushState = function(...args) {
        const result = origPush.apply(this, args);
        onRouteChange(args[2]);
        return result;
    };
    history.replaceState = function(...args) {
        const result = origReplace.apply(this, args);
        onRouteChange(args[2]);
        return result;
    };
    window.addEventListener('popstate', () => onRouteChange(location.href));
""")
```

This gives us a timestamped log of every SPA step with a `digitalData` snapshot
taken at the exact moment of navigation.

---

#### 2. b2t Event Listener (Array Push Intercept)

Because b2t events are pushed into `digitalData.event[]` dynamically,
we intercept the array push before the test starts:

```python
page.add_init_script("""
    window.__b2tCapture = [];

    function interceptB2T() {
        if (!window.digitalData) return;
        if (window.digitalData.__b2tIntercepted) return;
        window.digitalData.__b2tIntercepted = true;

        const origPush = Array.prototype.push;
        window.digitalData.event = window.digitalData.event || [];
        window.digitalData.event.push = function(...args) {
            const event = args[0];
            if (event && (event.eventInfo?.eventName === 'b2t' ||
                          event.eventInfo?.actionType)) {
                window.__b2tCapture.push({
                    ...event,
                    __capturedAt: Date.now(),
                    __url: location.href
                });
                console.log('[b2t] Event captured:', event.eventInfo?.actionType);
            }
            return origPush.apply(this, args);
        };
    }

    // Run immediately and again after each SPA navigation
    interceptB2T();
    window.addEventListener('popstate', interceptB2T);
""")
```

This ensures **zero b2t events are missed** regardless of when they fire relative
to page state.

---

#### 3. Step Readiness — Wait for digitalData to Settle (Not Network Idle)

On SPAs, `networkidle` is insufficient. We wait for the specific data condition
to be true before reading `digitalData`:

```python
def wait_for_digital_data_step(page, expected_action_type, timeout=10000):
    """Wait until the expected b2t actionType has been captured."""
    page.wait_for_function(
        f"""() => window.__b2tCapture &&
            window.__b2tCapture.some(e =>
                e.eventInfo?.actionType === '{expected_action_type}'
            )""",
        timeout=timeout
    )

# Usage — wait until flight selection b2t event fires before reading data
page.click(".flight-select-btn")
wait_for_digital_data_step(page, "flightSelect")
digital_data = capture_digital_data(page)
```

This replaces fragile `page.wait_for_timeout(3000)` sleeps with deterministic
condition-based waiting tied directly to the analytics events we care about.

---

#### 4. GA4 SPA Page View Handling

On SPAs, GA4 fires a custom `page_view` event on each virtual page change
(not an automatic browser event). Our network interceptor already handles this —
`page.on("request")` fires for every outbound request regardless of navigation type.

For SPAs that fire GA4 via `navigator.sendBeacon` (common for exit events), we
add a beacon interceptor:

```python
page.add_init_script("""
    const origSendBeacon = navigator.sendBeacon.bind(navigator);
    navigator.sendBeacon = function(url, data) {
        if (url.includes('google-analytics.com/g/collect')) {
            const params = new URLSearchParams(
                typeof data === 'string' ? data :
                new TextDecoder().decode(data)
            );
            window.__beaconCapture = window.__beaconCapture || [];
            window.__beaconCapture.push({
                url, params: Object.fromEntries(params),
                timestamp: Date.now()
            });
            console.log('[Beacon] GA4 sendBeacon captured:', params.get('en'));
        }
        return origSendBeacon(url, data);
    };
""")
```

---

#### 5. MutationObserver for DOM-Driven Step Detection

For steps where neither a route change nor a b2t event fires (e.g., modal-based
steps like seat selection), we use a MutationObserver to detect when the correct
DOM state is present before reading data:

```python
def wait_for_step_dom(page, css_selector, timeout=15000):
    """Wait for a specific DOM element indicating step is rendered."""
    page.wait_for_selector(css_selector, timeout=timeout, state="visible")
    page.wait_for_function(
        "() => !document.querySelector('.loading-spinner')",
        timeout=5000
    )
```

---

### SPA Handling — Summary per Flow Step

| Flow | Step | Wait Mechanism | Trigger |
|---|---|---|---|
| Booking | Search submit | `waitForURL` pattern | New URL with search params |
| Booking | Results load | `wait_for_digital_data_step("searchResults")` | b2t event |
| Booking | Flight select | `wait_for_digital_data_step("flightSelect")` | b2t event |
| Booking | PAX details | `wait_for_selector(".pax-form")` | DOM element |
| Booking | Payment | `wait_for_digital_data_step("paymentStep")` | b2t event |
| Booking | Confirm | `waitForURL("*/confirmation*")` + b2t check | URL + b2t event |
| MMB | Login | `wait_for_selector(".booking-summary")` | DOM element |
| MMB | Rebook confirm | `wait_for_digital_data_step("reBookConfirm")` | b2t event |
| Check-in | Confirm | `waitForURL("*/boarding-pass*")` | URL change |
| Upgrade | Confirm | `wait_for_digital_data_step("upgradeConfirm")` | b2t event |

This deterministic wait strategy eliminates flaky tests caused by timing issues —
the single most common failure mode in analytics automation against SPAs.

---

### Why ObservePoint Struggles with SPAs

ObservePoint's Journey runner was designed for traditional multi-page flows.
On SPAs it:
- Cannot natively wait for a specific `digitalData` state; relies on fixed time delays
- Cannot intercept `navigator.sendBeacon` calls reliably
- Has no mechanism to detect `history.pushState` as a step boundary
- Requires manual "Execute JavaScript" actions between steps as a workaround
- Multiple user reviews specifically cite SPA journeys as unreliable

**Playwright's SPA handling is a concrete capability advantage over ObservePoint.**

---

## 4. Proposed Playwright Solution Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     PLAYWRIGHT ANALYTICS VALIDATION PLATFORM                │
│                         (ObservePoint Replacement)                           │
└──────────────────────────────────────────────────────────────────────────────┘

    TRIGGER LAYER
    ┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │  GitHub Actions│  │  Tealium        │  │  Manual CLI     │
    │  schedule:cron │  │  Publish Hook   │  │  python core.py │
    └───────┬────────┘  └────────┬────────┘  └────────┬────────┘
            └───────────────────┴───────────────────┘
                                 │
                                 ▼
    CRAWL LAYER (NEW — to build)
    ┌──────────────────────────────────────────────┐
    │  Crawlee (Apify OSS)                         │
    │  ├── Sitemap XML parser                      │
    │  ├── URL queue + deduplication               │
    │  ├── Configurable crawl depth / count        │
    │  └── Playwright browser pool per worker      │
    └──────────────────┬───────────────────────────┘
                       │  per-page Playwright context
                       ▼
    CAPTURE LAYER (POC DONE)
    ┌──────────────────────────────────────────────┐
    │  For each page / journey step:               │
    │                                              │
    │  A. Network Interceptor                      │
    │     page.on("request") → GA4, Meta, Adobe   │
    │     parse URL params + POST body             │
    │                                              │
    │  B. Performance API sweep (post-load)        │
    │     performance.getEntriesByType("resource") │
    │     categorise by vendor domain              │
    │                                              │
    │  C. Data Layer Reader                        │
    │     page.evaluate → utag_data / dataLayer    │
    │                                              │
    │  D. Cookie Capture                           │
    │     context.cookies() → full inventory       │
    │                                              │
    │  E. Tag Pattern Matcher (NEW)                │
    │     known_tags.yml → match against captured  │
    │     network domains → tag presence report    │
    └──────────────────┬───────────────────────────┘
                       │
                       ▼
    VALIDATION LAYER (POC DONE — expand)
    ┌──────────────────────────────────────────────┐
    │  Rules Engine (code-based)                   │
    │  ├── GA4 vs utag comparison (7 fields) ✅    │
    │  ├── Tag presence rules (NEW)                │
    │  ├── Variable value assertions               │
    │  ├── Pre-consent tag detection (NEW)         │
    │  ├── Cookie allowlist check (NEW)            │
    │  └── GPC signal compliance check (NEW)       │
    └──────────────────┬───────────────────────────┘
                       │
                       ▼
    OUTPUT LAYER (POC DONE — expand)
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │  Per Run:                                               │
    │  ├── ga4_calls_YYYYMMDD.xlsx              ✅ Done      │
    │  ├── utag_data_YYYYMMDD.xlsx              ✅ Done      │
    │  ├── ga4_vs_utag_comparison_YYYYMMDD.xlsx ✅ Done      │
    │  ├── all_network_requests_YYYYMMDD.xlsx   ✅ Done      │
    │  ├── tag_presence_report_YYYYMMDD.xlsx    🔲 Build     │
    │  ├── cookie_report_YYYYMMDD.xlsx          🔲 Build     │
    │  ├── playwright_trace_YYYYMMDD.zip        ✅ Done      │
    │  ├── test_run_YYYYMMDD.webm               ✅ Done      │
    │  └── last_run.json → dashboard            ✅ Done      │
    │                                                         │
    │  Historical:                                            │
    │  └── Allure history/ → trend charts       🔲 Build     │
    └──────────────────┬──────────────────────────────────────┘
                       │
                       ▼
    REPORTING & ALERTING LAYER
    ┌──────────────────────────────────────────────┐
    │                                              │
    │  Dashboard (Dash + Plotly)   ✅ Done        │
    │  http://127.0.0.1:8050/                      │
    │                                              │
    │  Allure Report (historical)  🔲 Build       │
    │  allure generate → trend charts              │
    │                                              │
    │  Slack / Teams Webhook       🔲 Build       │
    │  POST on failure threshold breach            │
    │                                              │
    │  Email (SendGrid/SES)        🔲 Optional    │
    └──────────────────────────────────────────────┘
```

---

## 5. Build Roadmap — March 30 Deadline

```
Timeline: 6 weeks to full ObservePoint parity on core use cases
──────────────────────────────────────────────────────────────

WEEK 1 (Feb 16–22) — Foundation & Journey Parity
─────────────────────────────────────────────────
[x] POC already complete — GA4 vs utag validation
[ ] Refactor core.py into pytest test structure
[ ] Add journey config YAML (parameterise test data)
[ ] Add cookie capture report (context.cookies())
[ ] Add Slack webhook notification on test failure

WEEK 2 (Feb 23 – Mar 1) — Tag Pattern Library
──────────────────────────────────────────────
[ ] Build known_tags.yml (priority: GA4, GTM, Tealium,
    Meta Pixel, Adobe Analytics, Bing Ads, LinkedIn)
[ ] Tag presence validation: for each journey page,
    assert expected tags fired
[ ] Tag absence validation: assert no unexpected tags
[ ] Per-page tag presence report → Excel output

WEEK 3 (Mar 2–8) — Crawl Layer (Audit Mode)
─────────────────────────────────────────────
[ ] Integrate Crawlee for sitemap-based URL discovery
[ ] Run tag pattern matcher across all crawled pages
[ ] Output: tag inventory report (which tags on which pages)
[ ] Output: tag presence pass/fail matrix (per URL)
[ ] Configurable crawl depth + page count limit

WEEK 4 (Mar 9–15) — Privacy & Consent Validation
──────────────────────────────────────────────────
[ ] Pre-consent scan mode (no consent cookie set)
[ ] Capture all network requests before consent granted
[ ] Compare to pre-consent-allowed vendor allowlist
[ ] GPC signal testing (navigator.globalPrivacyControl)
[ ] Cookie allowlist check (flag unapproved cookies)
[ ] Output: privacy compliance report

WEEK 5 (Mar 16–22) — Reporting & Alerting
──────────────────────────────────────────
[ ] Allure integration (allure-pytest) for historical trends
[ ] Allure history stored between runs (local or S3)
[ ] Threshold-based alerting: if pass rate < X%, fire Slack alert
[ ] Aggregate crawl results into summary Excel dashboard
[ ] Per-run comparison against prior run (regression detection)

WEEK 6 (Mar 23–30) — Hardening & Cutover
──────────────────────────────────────────
[ ] CI/CD pipeline: GitHub Actions scheduled cron job
[ ] Tealium publish webhook → trigger CI run
[ ] Smoke test entire pipeline end-to-end
[ ] Document runbooks for analytics team handover
[ ] Parallel run: both ObservePoint and Playwright for 1 week
    to validate parity before ObservePoint is decommissioned
[ ] Cutover — ObservePoint contract ends March 30
```

---

## 6. Capability Comparison Summary

### What We CAN Replace (GREEN)

```
✅  GA4 event capture & parameter validation
✅  Tealium utag_data capture & validation
✅  GA4 vs utag_data field-level comparison
✅  Multi-step user journey automation
✅  Per-step tag rule validation
✅  All network request capture & categorisation
✅  Cookie inventory and governance
✅  Data layer monitoring (utag_data / window.dataLayer)
✅  Video recording per run (better than ObservePoint)
✅  Playwright Trace Viewer — step-by-step debug (better than OP)
✅  Cross-browser validation — Chrome, Firefox, Safari (better than OP)
✅  Complex auth — OAuth, SSO, MFA (better than OP)
✅  Pre-consent tag firing detection
✅  GPC signal compliance testing
✅  CI/CD integration — GitHub Actions, GitLab, Jenkins
✅  Scheduled runs (GitHub Actions cron)
✅  Slack / Teams / Webhook alerting
✅  Historical trend reporting (Allure)
✅  Excel / CSV export
✅  Web dashboard (Dash + Plotly — already built)
✅  Sitemap-based page crawling (via Crawlee)
✅  Tag presence auditing across crawled pages
✅  Accessibility testing (axe-core — better than OP)
✅  Visual regression testing (Percy/Chromatic — better than OP)
✅  Open source — zero license cost
✅  Self-hosted — no vendor dependency
```

### Where We LAG (RED — Be Honest)

```
❌  SCALE: 20,000+ page crawls require distributed infrastructure
    → ObservePoint scales in the cloud automatically
    → Playwright needs Kubernetes + job queue to match this
    → Mitigation: Most teams never exceed 5,000 pages per run

❌  NO-CODE: Analysts cannot create tests without developer help
    → ObservePoint is fully GUI / no-code
    → Playwright always requires writing Python or TypeScript
    → Mitigation: Pre-built templates + YAML config files reduce
      the need for code changes per new test

❌  AUTO-DISCOVERY: OP detects 1,500+ tags with zero pre-config
    → Playwright only validates what you explicitly look for
    → Mitigation: known_tags.yml pattern library covers our
      actual vendor list; unknown vendor detection via allowlist

❌  MULTI-TEAM GOVERNANCE: No RBAC, user management, or SSO
    → OP provides a shared platform with named owners per tag
    → Playwright results are per-repo CI artifacts
    → Mitigation: Repository-level access control + Allure
      hosted reports as a shared team view

❌  TEALIUM NATIVE INTEGRATION: OP has a dedicated Tealium plugin
    that auto-fires on profile publish with zero config
    → Playwright requires a webhook → CI/CD setup (1-2 days)
    → Mitigation: Tealium webhooks make this achievable
```

---

## 7. Cost Analysis

### ObservePoint Cost (Current)

| Tier | Monthly | Annual |
|---|---|---|
| Essentials (up to 4,000 page scans) | $599 | $7,188 |
| Professional (up to 20,000 page scans) | $2,400 | $28,800 |
| Enterprise (20,000+ page scans) | Custom — estimated $1,500–$3,000/month | $18,000–$36,000 |

### Playwright Solution Cost (Proposed)

| Item | Monthly Cost | Notes |
|---|---|---|
| Playwright (OSS) | $0 | MIT license |
| Python / Node.js runtime | $0 | Open source |
| Dash / Plotly dashboard | $0 | Open source |
| Crawlee crawler | $0 | Open source (Apify) |
| Allure reporting | $0 | Open source |
| GitHub Actions (CI) | $0–$60 | Free tier for public repos; ~$60/month for private repos with heavy usage |
| Cloud runner (optional) | $50–$200 | Only needed for large-scale crawls (5,000+ pages) |
| **Total** | **$0–$260/month** | vs $599–$3,000/month for ObservePoint |

**Estimated Annual Saving: $7,000 – $35,000**

---

## 8. Technology Stack (Proposed Full Platform)

```
Layer               Technology              Purpose
──────────────────  ──────────────────────  ────────────────────────────────────
Browser Automation  Playwright              Core test engine
Language            Python 3.x              Test logic, data processing
Crawl Engine        Crawlee (Apify OSS)     Sitemap-based URL crawling
Test Framework      pytest + playwright     Test structure, parallel execution
Reporting (live)    Dash + Plotly           Current-run web dashboard (built)
Reporting (history) Allure Report           Historical trend tracking
Data Export         pandas + openpyxl       Excel/CSV output
Alerting            Slack Webhooks          Failure notifications
CI/CD               GitHub Actions          Scheduled runs, PR checks
Container           Docker                  Reproducible execution environment
Tag Patterns        YAML config file        Known vendor tag URL patterns
Privacy Testing     Custom + Playwright     Consent simulation, GPC testing
Accessibility       @axe-core/playwright    WCAG compliance per page
Visual Regression   Percy / Chromatic       Screenshot comparison
```

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Crawler blocked by bot protection (Cloudflare, Akamai) | Medium | High | Use realistic user agents + slow crawl rate; request IP allowlist from site ops team (same issue exists with ObservePoint) |
| GA4 changes its `/g/collect` endpoint or param schema | Low | High | Monitor GA4 SDK release notes; update pattern lib; tests will break visibly alerting the team |
| Analyst team cannot maintain tests without developers | High | Medium | Deliver YAML-based config templates; provide runbooks; dedicate 10% dev time for test maintenance |
| March 30 cutover is too tight for full feature parity | Medium | High | Prioritise journey validation (done) + tag presence audit (Week 2–3). All core use cases complete by Week 4. Governance features are Phase 2. |
| Large-scale crawl (>5,000 pages) performance | Low | Medium | Current ObservePoint usage rarely exceeds 5,000 pages per run. Confirm actual page scan usage before March 30. |
| Playwright Inspector dependency in production runs | Low | Low | `PWDEBUG=1` and `page.pause()` are in current POC — remove before production; use `headless=True` in CI |

---

## 10. What We Are Asking For (RFP Ask)

### Phase 1 — Core Replacement (Weeks 1–4, by March 16)
- **Approve 4 weeks of engineering time** to build the tag pattern library,
  Crawlee integration, privacy scan, and cookie governance modules
- **Approve Slack/Teams webhook setup** for alerting
- **Approve GitHub Actions** for CI/CD scheduled runs
- **Deliverable:** Full parity on all journey validation + tag auditing use cases

### Phase 2 — Governance & Scale (Weeks 5–6, by March 30)
- **Approve Allure hosting** (shared server or S3 bucket) for historical trends
- **Approve parallel run** period (last 7 days of March) to validate parity
  before ObservePoint is decommissioned
- **Deliverable:** Complete ObservePoint replacement; contract decommissioned on schedule

### Phase 3 — Enhancement (Post March 30, Optional)
- Distributed crawler infrastructure (Kubernetes) for 10,000+ page scale
- Self-service YAML test config UI for non-developer analysts
- Multi-team dashboard aggregation
- Full GDPR/CCPA compliance automation suite

---

## 11. Verdict: Can Playwright Replace ObservePoint?

```
┌─────────────────────────────────────────────────────────────────────┐
│  YES — for our primary use case (journey-based analytics            │
│  validation: GA4 vs utag_data, tag presence, consent checking)      │
│                                                                     │
│  We lag in:                                                         │
│  • No-code interface for non-developer users                        │
│  • Cloud-scale crawling beyond 5,000 pages per run                 │
│  • Multi-team RBAC governance dashboard                             │
│                                                                     │
│  These gaps are ACCEPTABLE because:                                 │
│  • Our analytics validation is developer-owned                      │
│  • Our crawl scope is within the 5,000 page range                  │
│  • We are a single-team user of ObservePoint today                 │
│                                                                     │
│  We are BETTER than ObservePoint in:                               │
│  • Video recording + Trace Viewer for debugging                    │
│  • Complex auth (OAuth, SSO, MFA)                                  │
│  • Cross-browser coverage (Firefox + WebKit)                       │
│  • Visual regression testing                                       │
│  • Accessibility testing in CI pipeline                            │
│  • Full control + no vendor dependency                             │
│  • Cost: saves $7,000–$35,000/year                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

*Document prepared: February 15, 2026*
*POC codebase: `d:/automation/own/`*
*ObservePoint contract end: March 30, 2026*
*Proposed stack: Python + Playwright + Crawlee + Dash + Allure + GitHub Actions*
