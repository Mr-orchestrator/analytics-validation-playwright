# Flow Discovery Checklist
### What to confirm on the airline site BEFORE writing test code

Before building the four flow automation scripts, a 1-day discovery sprint is needed
to confirm the exact structure of `digitalData`, `b2t` events, and GA4 parameters
on the actual airline site. This checklist drives that sprint.

---

## How to Run Discovery

Open Chrome DevTools on the airline site during each flow step and run these
snippets in the Console. Record the results in the tables below.

---

## 1. Confirm digitalData Structure

Run in DevTools Console on each page:

```javascript
// Check if digitalData exists and show its top-level keys
console.log('digitalData keys:', Object.keys(window.digitalData || {}));
console.log(JSON.stringify(window.digitalData, null, 2));
```

| Page / Step | digitalData present? | transaction.transactionID path | cart.item[0].productInfo.productID path | total field path |
|---|---|---|---|---|
| Homepage | | | | |
| Search Results | | | | |
| Flight Selection | | | | |
| Passenger Details | | | | |
| Payment | | | | |
| Booking Confirm | | | | |
| MMB Overview | | | | |
| Check-in Confirm | | | | |
| Upgrade Confirm | | | | |

**Key questions to answer:**
- [ ] Is it `window.digitalData` or a differently named object?
- [ ] Is it a single object or an array `digitalData[0]`?
- [ ] Does it get reset on each page or does it accumulate?
- [ ] On SPA pages — does it update on route change or only on hard load?

---

## 2. Confirm b2t Event Structure

```javascript
// Option A: Check if b2t events live inside digitalData.event[]
console.log('digitalData.event[]:', JSON.stringify(window.digitalData?.event, null, 2));

// Option B: Check for a separate b2t events array
console.log('_b2tEvents:', window._b2tEvents);
console.log('b2tEvents:', window.b2tEvents);
console.log('dataLayer:', window.dataLayer);  // GTM dataLayer — may contain b2t events

// Option C: Listen for b2t events being pushed
const orig = Array.prototype.push;
window.digitalData = window.digitalData || {};
window.digitalData.event = window.digitalData.event || [];
window.digitalData.event.push = function(...args) {
  console.log('b2t event pushed:', JSON.stringify(args[0], null, 2));
  return orig.apply(this, args);
};
```

| Question | Answer |
|---|---|
| Where do b2t events live? (`digitalData.event[]` / `window._b2tEvents` / GTM dataLayer / custom) | |
| What is the exact property name for action type? (`actionType` / `action` / `eventAction` / `type`) | |
| What is the exact property name for booking ref? (`bookingRef` / `pnr` / `transactionID`) | |
| What is the exact property name for total amount? (`totalAmount` / `revenue` / `total`) | |
| What is the exact property name for flight number? (`flightNumber` / `flightNo` / `productID`) | |
| Are b2t events fired via `digitalData.event.push()` or custom JS event dispatch? | |
| Do b2t events accumulate or reset per page? | |

**Run this on the booking confirmation page to capture the actual b2t confirm event:**
```javascript
// Snapshot all events on success page
(window.digitalData?.event || []).forEach((e, i) => {
  console.log(`Event ${i}:`, JSON.stringify(e, null, 2));
});
```

---

## 3. Confirm GA4 Event Names per Step

Run in DevTools Network tab — filter by `collect?` — and note the `en` parameter value.

| Flow | Step | Expected GA4 Event | Actual GA4 `en` param | Notes |
|---|---|---|---|---|
| Booking | Search | `search` | | |
| Booking | Results | `view_item_list` | | |
| Booking | Flight Select | `select_item` | | |
| Booking | PAX Details | `begin_checkout` | | |
| Booking | Payment | `add_payment_info` | | |
| Booking | Confirm | `purchase` | | |
| MMB | Login | `login` | | |
| MMB | Overview | `view_item` | | |
| MMB | Rebook Confirm | `purchase` | | |
| Check-in | Start | ? | | |
| Check-in | Confirm | ? | | |
| Upgrade | Select | `select_item` | | |
| Upgrade | Confirm | `purchase` | | |

**Run this to capture all GA4 params on a page:**
```javascript
performance.getEntriesByType("resource")
  .filter(e => e.name.includes("google-analytics.com/g/collect"))
  .forEach((e, i) => {
    const params = Object.fromEntries(new URLSearchParams(e.name.split("?")[1]));
    console.log(`GA4 Hit ${i+1}:`, JSON.stringify(params, null, 2));
  });
```

---

## 4. Field Mapping Confirmation (Booking Confirmation Page)

Run this complete capture on the booking success/confirmation page and fill the table:

```javascript
// Full three-source capture on booking confirm page
const dd = window.digitalData || {};
const b2tEvents = (dd.event || []).filter(e =>
  e.eventInfo?.actionType === 'bookingConfirm' ||
  e.eventInfo?.eventName === 'b2t'
);
const ga4Calls = performance.getEntriesByType("resource")
  .filter(e => e.name.includes("google-analytics.com/g/collect"))
  .map(e => Object.fromEntries(new URLSearchParams(e.name.split("?")[1])));
const purchaseGA4 = ga4Calls.filter(p => p.en === 'purchase');

console.table({
  'PNR from digitalData': dd.transaction?.transactionID,
  'PNR from b2t':         b2tEvents[0]?.bookingRef,
  'PNR from GA4':         purchaseGA4[0]?.['ep.transaction_id'],
  'Total from digitalData': dd.transaction?.total?.transactionTotal,
  'Total from b2t':         b2tEvents[0]?.totalAmount,
  'Total from GA4':         purchaseGA4[0]?.['ep.value'],
  'Currency from b2t':      b2tEvents[0]?.currency,
  'Currency from GA4':      purchaseGA4[0]?.['cu'],
});
```

| Field | digitalData path | b2t property name | GA4 param name | Values match? |
|---|---|---|---|---|
| Booking Ref / PNR | | | | |
| Grand Total | | | | |
| Base Fare | | | | |
| Tax | | | | |
| Currency | | | | |
| Flight Number | | | | |
| Cabin Class | | | | |
| Fare Code | | | | |
| Origin | | | | |
| Destination | | | | |
| Pax Count | | | | |

---

## 5. SPA / Single-Page App Behaviour

Many airline sites are React/Angular SPAs. Confirm how data layer updates work.

| Question | Answer |
|---|---|
| Is the site a SPA (no full page reload between steps)? | |
| Does `digitalData` reset on each SPA route change? | |
| Does `digitalData` accumulate events or overwrite? | |
| Are b2t events fired on SPA navigation or on specific user actions? | |
| Do GA4 calls fire on `page_view` for each SPA step? | |
| Is there a `history.pushState` listener needed to detect step changes? | |

**Test for SPA routing:**
```javascript
// Monitor SPA route changes
const origPush = history.pushState;
history.pushState = function(...args) {
  console.log('SPA navigate to:', args[2]);
  console.log('digitalData at this point:', JSON.stringify(window.digitalData?.transaction, null, 2));
  return origPush.apply(this, args);
};
```

---

## 6. Authentication / Login State

For MMB and upgrade flows (which start with login):

| Question | Answer |
|---|---|
| What is the MMB login URL? | |
| What credentials are used for test accounts? | |
| Is there SSO / federated login involved? | |
| Can Playwright save session state (`storageState`) to skip re-login? | |
| Does `digitalData.user[0].profile.profileInfo.profileID` populate after login? | |
| What is the b2t `loginStatus` value for authenticated users? | |

---

## 7. Consent Handling

| Question | Answer |
|---|---|
| Is there a consent management platform (CMP)? (OneTrust, TrustArc, Cookiebot) | |
| What cookie/value accepts all tracking? | |
| Can Playwright set this cookie before page load to skip the banner? | |
| Does GA4 fire before or after consent? | |
| What b2t event fires on consent accept? | |

**Check for CMP:**
```javascript
// OneTrust
console.log('OneTrust:', typeof window.OneTrust !== 'undefined' ? 'present' : 'not found');
// Cookiebot
console.log('Cookiebot:', typeof window.Cookiebot !== 'undefined' ? 'present' : 'not found');
// Check consent cookie name
document.cookie.split(';').filter(c => c.toLowerCase().includes('consent'));
```

---

## 8. Environment URLs

| Flow | Staging URL | Production URL |
|---|---|---|
| Normal Booking entry | | |
| MMB entry | | |
| Check-in entry | | |
| Upgrade entry | | |
| Booking confirm success page | | |

---

## Discovery Sprint Output

After completing this checklist, the team will have:

1. **Confirmed `digitalData` structure** — exact key paths for all comparison fields
2. **Confirmed `b2t` event structure** — exact property names and event location
3. **Confirmed GA4 event names** — exact `en` param values per step per flow
4. **Completed field mapping table** — ready to put into `config/field_mappings.yml`
5. **Identified SPA vs MPA** — determines whether polling or event listeners are needed
6. **Test credentials** — for MMB and upgrade flows

**Estimated time for discovery sprint: 1 day**
**Owner: analytics engineer with DevTools access to the airline site**

---

*This checklist drives the `config/field_mappings.yml` which is the foundation
of the entire validation engine. Do not write automation code before this is complete.*
