# 📝 File Naming Convention

## ✅ Accurate Content-Based File Names

All output files now use **descriptive names that accurately reflect their contents**.

---

## 📂 File Names & Contents

### **1. Playwright Trace**
```
playwright_trace_20251127_1545.zip
```
**Contains:** Complete Playwright browser session recording
- Screenshots of every action
- Network requests and responses
- Console logs
- DOM snapshots
- Performance metrics

**Why this name:** It's a Playwright trace of the entire test session, not specific to utag.js.

---

### **2. Google Analytics 4 Data**
```
ga4_calls_20251127_1545.xlsx
```
**Contains:** Google Analytics 4 tracking calls
- GA4 event names
- Parameters
- Transaction IDs
- Values
- Currency

**Why this name:** This file contains Google Analytics 4 data, not utag.js data.

---

### **3. Tealium utag_data**
```
utag_data_20251127_1545.xlsx
```
**Contains:** Tealium utag_data object
- Data layer variables
- Page information
- User data
- Product information
- Transaction details

**Why this name:** This file contains Tealium's utag_data object specifically.

---

### **4. Comparison Results**
```
ga4_vs_utag_comparison_20251127_1545.xlsx
```
**Contains:** Comparison between GA4 and utag_data
- Parameter matching
- Value validation
- Pass/Fail results
- Discrepancies

**Why this name:** Clearly describes it's comparing GA4 data with utag data.

---

### **5. Video Recording**
```
test_run_20251127_154530.webm
```
**Contains:** Video recording of test execution
- Full browser session
- All interactions
- Visual playback

**Why this name:** Generic test run video, includes seconds for uniqueness.

---

### **6. Runtime Data**
```
last_run.json
```
**Contains:** Latest test results for dashboard
- Test case results
- Timestamps
- Pass/Fail status
- Comparison data

**Why this name:** Always the "last run" - gets overwritten.

---

## 🎯 Naming Rules

### **1. Be Descriptive**
✅ `ga4_calls_` - Clear it's GA4 data
✅ `utag_data_` - Clear it's utag data
✅ `playwright_trace_` - Clear it's a Playwright trace
✅ `ga4_vs_utag_comparison_` - Clear what's being compared

❌ `utag.js_trace_` - Confusing, trace isn't utag.js specific
❌ `utag.js_ga4_calls_` - Confusing, GA4 isn't part of utag.js

### **2. Reflect Actual Content**
Each file name should accurately describe what's inside:
- If it contains GA4 data → name it `ga4_`
- If it contains utag data → name it `utag_data_`
- If it's a Playwright trace → name it `playwright_trace_`
- If it compares two things → name it `x_vs_y_comparison_`

### **3. Use Timestamps**
Format: `YYYYMMDD_HHMM`
- `20251127` - Date (2025-11-27)
- `1545` - Time (15:45 / 3:45 PM)

**Why:** Easy to identify when the test was run.

---

## 📊 Complete Example (One Test Run)

**Test executed on: November 27, 2025 at 3:45 PM**

### Files Created:
```
videos/
└── test_run_20251127_154530.webm

validation_results/
├── playwright_trace_20251127_1545.zip
├── ga4_calls_20251127_1545.xlsx
├── utag_data_20251127_1545.xlsx
└── ga4_vs_utag_comparison_20251127_1545.xlsx

runtime_data/
└── last_run.json
```

### File Purposes:
| File | Purpose | Content Type |
|------|---------|--------------|
| `playwright_trace_*.zip` | Debug browser session | Playwright trace |
| `ga4_calls_*.xlsx` | GA4 analytics data | Google Analytics 4 |
| `utag_data_*.xlsx` | Tealium data layer | Tealium utag_data |
| `ga4_vs_utag_comparison_*.xlsx` | Validate data accuracy | Comparison results |
| `test_run_*.webm` | Visual recording | Video |
| `last_run.json` | Dashboard display | Latest results |

---

## 🔍 Why We Changed the Naming

### **Old (Confusing):**
```
utag.js_trace_20251127_1545.zip           ← Not utag.js specific
utag.js_ga4_calls_20251127_1545.xlsx      ← GA4 isn't part of utag.js
utag.js_utag_data_20251127_1545.xlsx      ← Redundant .js
utag.js_comparison_results_20251127_1545.xlsx ← Doesn't say what's compared
```

### **New (Clear):**
```
playwright_trace_20251127_1545.zip        ← Playwright session trace
ga4_calls_20251127_1545.xlsx              ← Google Analytics 4 data
utag_data_20251127_1545.xlsx              ← Tealium utag_data
ga4_vs_utag_comparison_20251127_1545.xlsx ← GA4 vs utag comparison
```

---

## ✅ Benefits

| Benefit | Description |
|---------|-------------|
| **Clarity** | File names instantly tell you what's inside |
| **Accuracy** | Names reflect actual content, not project name |
| **Professional** | Standard naming convention |
| **Searchable** | Easy to find specific data types |
| **Self-documenting** | No need to open files to know contents |

---

## 📝 Summary

**File Naming Principle:**
> Name files based on their actual content, not the project name.

**Examples:**
- ✅ `ga4_calls_` - Contains GA4 data
- ✅ `utag_data_` - Contains utag data
- ✅ `playwright_trace_` - Contains Playwright trace
- ✅ `ga4_vs_utag_comparison_` - Compares GA4 and utag

**Avoid:**
- ❌ Using project name for all files
- ❌ Generic names like `data_`, `results_`
- ❌ Ambiguous names that don't describe content

---

## 🎯 Quick Reference

```
playwright_trace_YYYYMMDD_HHMM.zip      → Playwright browser trace
ga4_calls_YYYYMMDD_HHMM.xlsx            → Google Analytics 4 data
utag_data_YYYYMMDD_HHMM.xlsx            → Tealium utag_data
ga4_vs_utag_comparison_YYYYMMDD_HHMM.xlsx → Comparison results
test_run_YYYYMMDD_HHMMSS.webm           → Video recording
last_run.json                            → Latest results (dashboard)
```

**Clear, accurate, and professional!** 📂✨
