# 🎬 Playwright Trace Files - Individual Run Storage

## ✅ What Changed

Playwright trace files are now stored in `validation_results` folder with timestamps for **each individual test run**.

---

## 📂 File Location & Naming

### **Location:**
```
validation_results/
└── playwright_trace_YYYYMMDD_HHMM.zip
```

### **Naming Format:**
```
playwright_trace_20251127_1545.zip
playwright_trace_20251127_1602.zip
playwright_trace_20251127_1635.zip
```

**Pattern:** `playwright_trace_[DATE]_[TIME].zip`
- `YYYYMMDD` - Date (Year, Month, Day)
- `HHMM` - Time (24-hour format with minutes)

---

## 🎯 Key Features

### 1. **Individual Run Storage**
- ✅ Each test run creates its own trace file
- ✅ Timestamped for easy identification
- ✅ No overwriting of previous traces
- ✅ Historical trace files preserved

### 2. **Organized with Test Data**
All test outputs in one location:
```
validation_results/
├── playwright_trace_20251127_1545.zip       ← Playwright trace
├── ga4_calls_20251127_1545.xlsx             ← Google Analytics 4 data
├── utag_data_20251127_1545.xlsx             ← Tealium utag_data
└── ga4_vs_utag_comparison_20251127_1545.xlsx ← Comparison results
```

**Same timestamp = Same test run!**

### 3. **Easy Debugging**
- Match trace file to test results by timestamp
- Replay exact browser interactions
- View network requests, console logs, DOM snapshots
- Debug failures with full context

---

## 📊 Storage Details

### **What's in a Trace File?**
Each `playwright_trace_*.zip` contains:
- 🎬 **Screenshots** of every action
- 🌐 **Network requests** and responses
- 📝 **Console logs** from browser
- 🖱️ **User interactions** (clicks, typing, etc.)
- 📄 **DOM snapshots** at each step
- ⏱️ **Timing information**

### **File Size:**
- Typical size: 5-15 MB per trace
- Depends on test length and complexity
- Compressed .zip format

---

## 🔍 How to Use Trace Files

### **1. View Trace in Playwright Inspector**
```bash
playwright show-trace validation_results/playwright_trace_20251127_1545.zip
```

### **2. Open in Browser**
- Go to: https://trace.playwright.dev/
- Drag and drop the trace.zip file
- Navigate through the recorded actions

### **What You'll See:**
- Timeline of all actions
- Network requests and responses
- Screenshots at each step
- Console logs
- DOM snapshots
- Performance metrics

---

## 📁 File Organization

### **Complete Test Run Files:**
```
validation_results/
│
├── Run 1 (15:45)
│   ├── playwright_trace_20251127_1545.zip
│   ├── ga4_calls_20251127_1545.xlsx
│   ├── utag_data_20251127_1545.xlsx
│   └── ga4_vs_utag_comparison_20251127_1545.xlsx
│
├── Run 2 (16:02)
│   ├── playwright_trace_20251127_1602.zip
│   ├── ga4_calls_20251127_1602.xlsx
│   ├── utag_data_20251127_1602.xlsx
│   └── ga4_vs_utag_comparison_20251127_1602.xlsx
│
└── Run 3 (16:35)
    ├── playwright_trace_20251127_1635.zip
    ├── ga4_calls_20251127_1635.xlsx
    ├── utag_data_20251127_1635.xlsx
    └── ga4_vs_utag_comparison_20251127_1635.xlsx
```

**Each run = 4 files with matching timestamps**

---

## 🔄 Workflow

### **1. Run Test**
```bash
python core.py
```

### **2. Files Created**
```
✅ Video: videos/test_run_20251127_154530.webm
✅ Trace: validation_results/playwright_trace_20251127_1545.zip
✅ Excel: validation_results/*_20251127_1545.xlsx
✅ JSON: runtime_data/last_run.json
```

### **3. Debugging**
If test fails:
1. Check timestamp of failed test
2. Open corresponding trace file: `utag.js_trace_[timestamp].zip`
3. Replay the exact browser session
4. Identify where it failed
5. View network requests, console errors, DOM state

---

## 💡 Use Cases

### **1. Debugging Failed Tests**
```bash
# Test failed at 15:45
playwright show-trace validation_results/playwright_trace_20251127_1545.zip
```
- See exactly what happened
- View error messages
- Check network failures

### **2. Comparing Test Runs**
```bash
# Compare two different runs
playwright show-trace validation_results/playwright_trace_20251127_1545.zip
playwright show-trace validation_results/playwright_trace_20251127_1602.zip
```
- Compare different executions
- Identify timing differences
- Spot inconsistencies

### **3. Documentation**
- Share trace file with team
- Reproduce issues exactly
- Visual proof of test execution

### **4. Performance Analysis**
- View request timing
- Identify slow operations
- Optimize test flow

---

## 📊 Benefits

| Benefit | Description |
|---------|-------------|
| **Individual Storage** | Each run has its own trace file |
| **Timestamped** | Easy to match with test results |
| **No Overwriting** | All historical traces preserved |
| **Complete Debug Info** | Full browser session recorded |
| **Easy Sharing** | Single zip file contains everything |
| **Organized** | All test outputs in one folder |

---

## 🗑️ Cleanup

### **Old trace.zip in Root**
If you have an old `trace.zip` file in the root directory, you can delete it:
```bash
Remove-Item trace.zip
```

All new traces are saved in `validation_results/` folder.

### **Managing Storage**
To clean up old trace files:
```bash
# Delete traces older than 30 days
Get-ChildItem validation_results/playwright_trace_*.zip | 
  Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
  Remove-Item
```

---

## 🎯 Quick Reference

### **Run Test & Create Trace**
```bash
python core.py
# Creates: validation_results/playwright_trace_[timestamp].zip
```

### **View Latest Trace**
```bash
# PowerShell
$latest = Get-ChildItem validation_results/playwright_trace_*.zip | 
          Sort-Object LastWriteTime -Descending | 
          Select-Object -First 1
playwright show-trace $latest.FullName
```

### **View Specific Trace**
```bash
playwright show-trace validation_results/playwright_trace_20251127_1545.zip
```

### **Open in Browser**
Visit: https://trace.playwright.dev/
Drag and drop trace.zip file

---

## 📝 Summary

✅ **Each test run creates individual trace file**
✅ **Stored in validation_results folder**
✅ **Timestamped naming: playwright_trace_YYYYMMDD_HHMM.zip**
✅ **Matches Excel file timestamps**
✅ **Complete debugging information**
✅ **No overwriting - all runs preserved**
✅ **Easy to identify and replay specific runs**

**Perfect for debugging, documentation, and performance analysis!** 🎬
