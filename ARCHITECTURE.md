# High-Level Architecture — Airline Analytics Validation Platform

> **Purpose:** Replace ObservePoint (contract ending March 30) with a custom
> Playwright-based framework that validates GA4 events against `digitalData`
> (W3C CEDDL data layer) and `b2t` events (action-type events) across all
> four airline user journeys.

---

## Data Sources — What Changed from POC

```
POC (done)                        Production Target
──────────────────────────────    ──────────────────────────────────────
utag_data  ◀── compared ──▶ GA4   digitalData  ◀── compared ──▶ GA4
                                  b2t events   ◀── compared ──▶ GA4
                                  (per action type, per flow step)

Single flow (e-commerce demo)     Four airline flows:
                                  1. Normal Booking
                                  2. MMB Rebooking
                                  3. Check-in
                                  4. Upgrade
```

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       ANALYST / QA ENGINEER                              │
│              python run_flow.py --flow booking|mmb|checkin|upgrade       │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     Flow Runner  (flow_runner.py)                        │
│                                                                          │
│  Loads flow config YAML → selects journey steps → drives Playwright     │
│                                                                          │
│  ┌──────────────┐  ┌───────────────────┐  ┌─────────────────────────┐  │
│  │  Browser     │  │  Capture Layer    │  │  Validation Engine      │  │
│  │  (Playwright)│─▶│  GA4 + digitalData│─▶│  GA4 vs digitalData    │  │
│  │              │  │  + b2t events     │  │  GA4 vs b2t events     │  │
│  └──────────────┘  └───────────────────┘  └─────────────────────────┘  │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
               ┌───────────────────┼──────────────────┐
               ▼                   ▼                   ▼
  ┌─────────────────────┐  ┌────────────┐  ┌─────────────────────┐
  │  Excel Reports      │  │  JSON      │  │  Playwright         │
  │  per flow per step  │  │  last_run  │  │  Trace + Video      │
  └─────────────────────┘  └────────────┘  └─────────────────────┘
                                   │
                                   ▼
              ┌────────────────────────────────────────┐
              │        Dashboard (Dash + Plotly)        │
              │         http://127.0.0.1:8050/          │
              │   Breakdown by Flow / Step / Rule       │
              └────────────────────────────────────────┘
```

---

## Data Layer Definitions

### digitalData (W3C CEDDL)

The standard data layer object read from `window.digitalData`.
Airlines populate this at each page/step transition.

```
window.digitalData
├── page
│   ├── pageInfo
│   │   ├── pageName           e.g. "flight-search-results"
│   │   ├── pageID             e.g. "SERP"
│   │   └── language
│   └── category
│       └── primaryCategory    e.g. "booking"
│
├── user[]
│   └── profile
│       ├── profileInfo.profileID
│       └── attributes (loyalty tier, login status)
│
├── cart
│   ├── cartID
│   └── item[]
│       ├── productInfo.productID    flight number / fare code
│       ├── productInfo.sku
│       ├── quantity
│       └── price.basePrice
│
├── transaction
│   ├── transactionID          booking reference (PNR)
│   ├── total
│   │   ├── basePrice          fare total
│   │   ├── taxRate
│   │   └── transactionTotal   grand total
│   └── item[]
│       ├── productInfo.productID
│       ├── quantity
│       └── price.basePrice
│
└── event[]                    pushed on user interactions
    └── eventInfo
        ├── eventName
        └── actionType         maps to b2t action types
```

---

### b2t Events (Action-Type Events)

Custom analytics events pushed by the airline tagging layer.
Each event has an `actionType` property identifying the step.

```
b2t event structure (per step):
{
  actionType : "flightSearch" | "flightSelect" | "passengerDetails" |
               "seatSelect"   | "ancillaryAdd" | "paymentStep"      |
               "bookingConfirm" | "mmbLogin"   | "reBook"           |
               "checkInStart" | "checkInConfirm"| "upgradeSelect"   |
               "upgradeConfirm",

  // Booking data (present from flightSelect onwards)
  origin          : "LHR",
  destination     : "JFK",
  departDate      : "2026-04-01",
  returnDate      : "2026-04-08",    // if round trip
  paxCount        : "1",
  cabinClass      : "Economy",
  flightNumber    : "BA117",
  fareCode        : "YOWBP",
  bookingRef      : "ABC123",        // present on confirm step

  // Transaction data (present on confirm steps)
  totalAmount     : "450.00",
  currency        : "GBP",
  taxAmount       : "87.50",

  // Ancillary data (present on ancillary steps)
  ancillaryType   : "bag" | "meal" | "seat",
  ancillaryAmount : "35.00",

  // User data
  memberID        : "GOLD123456",    // if logged in
  loginStatus     : "logged-in" | "guest"
}
```

---

## Four Airline User Journeys

### Flow 1 — Normal Booking

```
STEP 1: Homepage / Search Entry
        User enters: origin, destination, dates, pax count, cabin class
        ├── b2t actionType: "flightSearch"
        ├── GA4 event:      "search" or "flight_search"
        └── digitalData:    page.pageInfo.pageName = "homepage"

STEP 2: Search Results (SERP)
        Flights displayed
        ├── b2t actionType: "searchResults"
        ├── GA4 event:      "view_item_list"
        └── digitalData:    listing.items[] populated with flight options

STEP 3: Flight Selection
        User clicks a flight / fare
        ├── b2t actionType: "flightSelect"
        ├── GA4 event:      "select_item" or "add_to_cart"
        └── digitalData:    cart.item[0] populated
            Validate: GA4 item_id == digitalData.cart.item[0].productInfo.productID
            Validate: GA4 item_name == b2t.flightNumber
            Validate: GA4 price == digitalData.cart.item[0].price.basePrice

STEP 4: Passenger Details
        User fills pax form (name, DOB, passport etc.)
        ├── b2t actionType: "passengerDetails"
        ├── GA4 event:      "begin_checkout"
        └── digitalData:    cart.cartID set, user profile updated

STEP 5: Seat Selection (optional)
        User selects seats
        ├── b2t actionType: "seatSelect"
        ├── GA4 event:      "add_to_cart" (ancillary)
        └── digitalData:    cart.item[] updated with seat product

STEP 6: Ancillaries / Extras
        User adds bags, meals, etc.
        ├── b2t actionType: "ancillaryAdd"
        ├── GA4 event:      "add_to_cart"
        └── digitalData:    cart.item[] updated

STEP 7: Payment
        User enters payment details
        ├── b2t actionType: "paymentStep"
        ├── GA4 event:      "add_payment_info"
        └── digitalData:    transaction.total.transactionTotal visible

STEP 8: Booking Confirmation
        Order placed successfully
        ├── b2t actionType: "bookingConfirm"
        ├── GA4 event:      "purchase"
        └── digitalData:    transaction.transactionID = PNR (booking ref)
            Validate: GA4 transaction_id  == digitalData.transaction.transactionID
            Validate: GA4 transaction_id  == b2t.bookingRef
            Validate: GA4 value           == digitalData.transaction.total.transactionTotal
            Validate: GA4 value           == b2t.totalAmount
            Validate: GA4 tax             == digitalData.transaction.total.taxRate
            Validate: GA4 currency        == b2t.currency
            Validate: GA4 items[0].item_id == b2t.flightNumber
```

---

### Flow 2 — MMB Rebooking (Manage My Booking)

```
STEP 1: MMB Login / Retrieve Booking
        User enters booking ref + last name
        ├── b2t actionType: "mmbLogin"
        ├── GA4 event:      "login" or "mmb_retrieve"
        └── digitalData:    user.profile.profileInfo.profileID set

STEP 2: Booking Overview
        Existing booking displayed
        ├── b2t actionType: "mmbOverview"
        ├── GA4 event:      "view_item"
        └── digitalData:    transaction populated with existing booking

STEP 3: Change Flight / Select New Dates
        User initiates change, new search results shown
        ├── b2t actionType: "reBookSearch"
        ├── GA4 event:      "view_item_list"
        └── digitalData:    listing populated with new flight options

STEP 4: New Flight Selection
        User selects replacement flight
        ├── b2t actionType: "reBook"
        ├── GA4 event:      "select_item"
        └── digitalData:    cart updated with new flight
            Validate: GA4 item_id   == digitalData.cart.item[0].productInfo.productID
            Validate: GA4 item_name == b2t.flightNumber
            Validate: b2t.bookingRef == original PNR

STEP 5: Fare Difference / Payment (if applicable)
        User pays fare difference
        ├── b2t actionType: "reBookPayment"
        ├── GA4 event:      "purchase"
        └── digitalData:    transaction.total = fare difference amount
            Validate: GA4 transaction_id == b2t.bookingRef
            Validate: GA4 value          == digitalData.transaction.total.transactionTotal

STEP 6: Rebooking Confirmation
        Change confirmed
        ├── b2t actionType: "reBookConfirm"
        ├── GA4 event:      "purchase" or custom confirm event
        └── digitalData:    transaction.transactionID = new/modified PNR
```

---

### Flow 3 — Check-in

```
STEP 1: Check-in Entry
        User accesses online check-in
        ├── b2t actionType: "checkInStart"
        ├── GA4 event:      "checkin_start"
        └── digitalData:    page.pageInfo.pageName = "check-in-home"

STEP 2: Retrieve Booking for Check-in
        User enters booking ref + last name
        ├── b2t actionType: "checkInRetrieve"
        ├── GA4 event:      "checkin_retrieve"
        └── digitalData:    transaction populated (existing booking)
            Validate: b2t.bookingRef is present
            Validate: GA4 transaction_id == b2t.bookingRef

STEP 3: Passenger Selection
        User selects passengers to check in
        ├── b2t actionType: "checkInPaxSelect"
        ├── GA4 event:      "checkin_pax_select"
        └── digitalData:    user[] updated with pax being checked in

STEP 4: Seat Selection (check-in)
        User picks/confirms seats
        ├── b2t actionType: "checkInSeatSelect"
        ├── GA4 event:      "checkin_seat_select"
        └── digitalData:    cart.item[] updated with seat assignment

STEP 5: Extras at Check-in (bags etc.)
        User adds any last-minute ancillaries
        ├── b2t actionType: "checkInAncillary"
        ├── GA4 event:      "add_to_cart"
        └── digitalData:    cart updated

STEP 6: Check-in Confirmation / Boarding Pass
        Check-in completed; boarding pass issued
        ├── b2t actionType: "checkInConfirm"
        ├── GA4 event:      "checkin_complete"
        └── digitalData:    transaction.transactionID = booking ref
            Validate: GA4 transaction_id == b2t.bookingRef
            Validate: GA4 transaction_id == digitalData.transaction.transactionID
```

---

### Flow 4 — Upgrade

```
STEP 1: Upgrade Entry
        User accesses upgrade (from MMB or check-in)
        ├── b2t actionType: "upgradeEntry"
        ├── GA4 event:      "upgrade_start"
        └── digitalData:    transaction populated with existing booking
            Validate: b2t.bookingRef matches existing PNR

STEP 2: Upgrade Options Displayed
        Available cabin upgrades shown with prices
        ├── b2t actionType: "upgradeOptions"
        ├── GA4 event:      "view_item_list"
        └── digitalData:    listing[] populated with upgrade products

STEP 3: Upgrade Selection
        User picks an upgrade option
        ├── b2t actionType: "upgradeSelect"
        ├── GA4 event:      "select_item" or "add_to_cart"
        └── digitalData:    cart.item[0] = upgrade product
            Validate: GA4 item_id   == digitalData.cart.item[0].productInfo.productID
            Validate: GA4 price     == b2t.ancillaryAmount
            Validate: b2t.ancillaryType == "upgrade"

STEP 4: Upgrade Payment
        User pays for upgrade
        ├── b2t actionType: "upgradePayment"
        ├── GA4 event:      "add_payment_info"
        └── digitalData:    transaction.total updated with upgrade cost

STEP 5: Upgrade Confirmation
        Upgrade booked
        ├── b2t actionType: "upgradeConfirm"
        ├── GA4 event:      "purchase"
        └── digitalData:    transaction.transactionID = PNR
            Validate: GA4 transaction_id == b2t.bookingRef
            Validate: GA4 transaction_id == digitalData.transaction.transactionID
            Validate: GA4 value          == b2t.ancillaryAmount
            Validate: GA4 value          == digitalData.transaction.total.transactionTotal
            Validate: GA4 currency       == b2t.currency
```

---

## Capture Layer — Three Sources Running in Parallel

```
┌────────────────────────────────────────────────────────────────────────┐
│            THREE DATA SOURCES CAPTURED PER STEP                        │
│                                                                        │
│  SOURCE 1: GA4 Network Calls                                           │
│  ──────────────────────────────────────────────────────────────────    │
│  page.on("request") → filters google-analytics.com/g/collect          │
│  Captures: en (event name), ep.* params, items[], currency, value      │
│  Timing: fires on every outbound GA4 beacon                            │
│                                                                        │
│  SOURCE 2: digitalData (W3C CEDDL)                                     │
│  ──────────────────────────────────────────────────────────────────    │
│  page.evaluate(() => JSON.parse(JSON.stringify(window.digitalData)))   │
│  Called: after each step's page load or SPA update settles             │
│  Captures: page, user, cart, transaction, event[] objects              │
│                                                                        │
│  SOURCE 3: b2t Events                                                  │
│  ──────────────────────────────────────────────────────────────────    │
│  Two capture methods run together:                                     │
│                                                                        │
│  3a. Event listener injected before navigation:                        │
│      window.__b2tCapture = [];                                         │
│      // intercept push to digitalData.event[]                         │
│      // or intercept custom b2t dispatch / data layer push            │
│                                                                        │
│  3b. Read directly after step settles:                                 │
│      page.evaluate(() => window.digitalData.event                      │
│        .filter(e => e.eventInfo.eventName === 'b2t'))                  │
│      OR: page.evaluate(() => window._b2tEvents)  ← if separate obj    │
│                                                                        │
│  Note: exact capture method confirmed during flow discovery sprint     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Validation Engine — Cross-Source Comparison

```
For each flow step that has a GA4 event:

  GA4 params (from network)
       │
       ├──── compared against ────▶  digitalData fields
       │                             (transaction, cart, page, user)
       │
       └──── compared against ────▶  b2t event fields
                                     (filtered by actionType for this step)

Validation fields per confirm step (booking / reBook / checkIn / upgrade):

  Validation Rule                GA4 Field         Digital Data Field     b2t Field
  ─────────────────────────────  ────────────────  ─────────────────────  ────────────────────
  Booking Reference / PNR        ep.transaction_id transaction.transactionID bookingRef
  Grand Total                    ep.value          transaction.total.transactionTotal totalAmount
  Base Fare                      ep.items[0].price cart.item[0].price.basePrice  —
  Tax Amount                     ep.tax            transaction.total.taxRate     taxAmount
  Currency                       ep.currency / cu  —                             currency
  Flight Number / Product ID     ep.items[0].item_id cart.item[0].productInfo.productID flightNumber
  Cabin Class                    ep.items[0].item_category —                    cabinClass
  Fare Code                      ep.items[0].item_variant  —                    fareCode
  Origin                         ep.items[0].index —                             origin
  Destination                    —                 —                             destination
  Pax Count                      ep.items[0].quantity —                         paxCount
  Action Type (b2t step)         ep.event_label    digitalData.event[].eventInfo.actionType actionType
  Login Status                   —                 user[0].profile.attributes   loginStatus
```

---

## Project File Structure (Target)

```
d:/automation/own/
│
├── flows/                          ← One file per airline journey
│   ├── booking_flow.py             Normal booking (Steps 1–8)
│   ├── mmb_flow.py                 MMB rebooking (Steps 1–6)
│   ├── checkin_flow.py             Check-in (Steps 1–6)
│   └── upgrade_flow.py             Upgrade (Steps 1–5)
│
├── capture/                        ← Data capture modules
│   ├── ga4_capture.py              Network interceptor for GA4
│   ├── digital_data_capture.py     window.digitalData reader
│   └── b2t_capture.py              b2t event capture + listener
│
├── validation/                     ← Comparison & assertion logic
│   ├── compare_engine.py           GA4 vs digitalData + b2t
│   ├── field_map.py                Field mapping per flow per step
│   └── rules.py                    Rule definitions (equals, regex, etc.)
│
├── config/
│   ├── flows.yml                   Flow config (URLs, test data, steps)
│   ├── field_mappings.yml          GA4 ↔ digitalData ↔ b2t field map
│   └── tag_patterns.yml            Known analytics vendor URL patterns
│
├── reporting/
│   ├── excel_exporter.py           Excel output per flow per run
│   └── json_runtime.py             last_run.json for dashboard
│
├── dashboard.py                    Dash web dashboard (updated for flows)
├── flow_runner.py                  Main entry point — runs any flow
├── core.py                         Original POC (keep as reference)
├── requirements.txt
│
└── validation_results/
    ├── booking/
    ├── mmb/
    ├── checkin/
    └── upgrade/
        └── YYYYMMDD_HHMM/
            ├── ga4_events.xlsx
            ├── digital_data_snapshots.xlsx
            ├── b2t_events.xlsx
            ├── comparison_report.xlsx
            ├── playwright_trace.zip
            └── test_run.webm
```

---

## Comparison Report Structure (per run)

```
Sheet 1 — Summary
  Flow        | Steps Run | GA4 Events | b2t Events | digitalData Captures | Pass | Fail | Pass%
  ─────────────────────────────────────────────────────────────────────────────────────────────
  Booking     |    8      |     12     |     8      |         8            |  18  |   2  |  90%
  MMB Rebook  |    6      |      8     |     6      |         6            |  14  |   1  |  93%
  Check-in    |    6      |      7     |     6      |         6            |  12  |   2  |  86%
  Upgrade     |    5      |      6     |     5      |         5            |  10  |   0  | 100%

Sheet 2 — Detail (one row per validation rule per step)
  Flow | Step | Step Name      | Rule                    | GA4 Value | digitalData Value | b2t Value | Match
  ─────────────────────────────────────────────────────────────────────────────────────────────────────────
  Booking | 8 | Confirm        | transaction_id / PNR    | ABC123    | ABC123            | ABC123    | ✅
  Booking | 8 | Confirm        | total / transactionTotal| 450.00    | 450.00            | 450.00    | ✅
  Booking | 3 | FlightSelect   | item_id / productID     | BA117     | BA117             | BA117     | ✅
  Booking | 7 | Payment        | currency                | GBP       | N/A               | GBP       | ✅
  MMB    | 5 | reBookPayment   | value / totalAmount     | 85.00     | 85.00             | 85.00     | ✅
  ...

Sheet 3 — b2t Event Log (all b2t events captured, all steps)
  Flow | Step | actionType       | bookingRef | totalAmount | currency | flightNumber | cabinClass
  ──────────────────────────────────────────────────────────────────────────────────────────────
  Booking | 1 | flightSearch    | —          | —           | —        | —            | Economy
  Booking | 3 | flightSelect    | —          | —           | GBP      | BA117        | Economy
  Booking | 8 | bookingConfirm  | ABC123     | 450.00      | GBP      | BA117        | Economy

Sheet 4 — GA4 Event Log (all GA4 hits captured)
Sheet 5 — digitalData Snapshots (all page captures)
Sheet 6 — Network Request Log (all vendor calls)
```

---

## Dashboard — Updated for Airline Flows

```
http://127.0.0.1:8050/

Tab: Overview
  ┌──────────────┬──────────────┬──────────────┬──────────────┐
  │  Booking     │  MMB         │  Check-in    │  Upgrade     │
  │  Pass: 90%   │  Pass: 93%   │  Pass: 86%   │  Pass: 100%  │
  │  18/20 rules │  14/15 rules │  12/14 rules │  10/10 rules │
  └──────────────┴──────────────┴──────────────┴──────────────┘
  [Bar Chart — Pass/Fail per flow]
  [Pie Chart — Overall pass rate across all flows]

Tab: Booking Flow
  Step-by-step pass/fail per rule
  b2t actionType sequence timeline
  GA4 event sequence timeline
  Failures highlighted with Expected vs Actual

Tab: MMB Rebooking
  [same structure]

Tab: Check-in
  [same structure]

Tab: Upgrade
  [same structure]

Tab: b2t Event Inspector
  Full b2t event log filterable by flow, step, actionType

Tab: digitalData Inspector
  Full digitalData snapshot per page per step

Tab: Network Log
  All analytics vendor requests categorised
```

---

## Technology Stack

```
Layer               Technology              Purpose
──────────────────  ──────────────────────  ──────────────────────────────────────
Browser Automation  Playwright (sync_api)   Browser control, network intercept
Language            Python 3.x              Flow logic, capture, validation
Data Layer Read     page.evaluate()         window.digitalData + b2t events
GA4 Capture         page.on("request")      Network interceptor
b2t Capture         JS injection + eval     Event listener + direct read
Data Processing     pandas 2.1.3            Comparison, aggregation
Excel Export        openpyxl 3.1.2          Multi-sheet comparison report
Dashboard           Dash 2.14.1             Multi-tab web dashboard
Charts              Plotly 5.18.0           Pass/fail charts per flow
Test Framework      pytest (next phase)     Parallel flow execution
CI/CD               GitHub Actions          Scheduled runs + alerts
Reporting (history) Allure Report           Historical trend tracking
```

---

## What Changed from POC vs This Target

```
POC (ecommerce.tealiumdemo.com)    Airline Production Target
────────────────────────────────   ─────────────────────────────────────────
Single flow (checkout)             4 flows: booking, mmb, checkin, upgrade
utag_data (Tealium)                digitalData (W3C CEDDL)
No b2t events                      b2t events with actionType per step
7 comparison fields                15+ comparison fields per confirm step
Single comparison sheet (Excel)    6-sheet Excel report per flow per run
Single-tab dashboard               Multi-tab dashboard (one tab per flow)
Fixed test data                    Config YAML for test data per flow
Single entry point (core.py)       flow_runner.py --flow <name>
```

---

*Last updated: 2026-02-15*
*Flows: Booking | MMB Rebooking | Check-in | Upgrade*
*Data sources: GA4 network calls | window.digitalData | b2t events*
*ObservePoint contract ends: 2026-03-30*
