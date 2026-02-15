# 🎯 GA4 vs utag.js Automation Testing Framework

## ✨ New Features Implemented

### 1. 📁 Excel File Naming with Timestamps
All Excel files now include:
- **utag.js prefix** for easy identification
- **Current date and time** (YYYYMMDD_HHMM format)
- Organized in `validation_results/` folder

**Example file names:**
```
ga4_calls_20251127_1545.xlsx
utag_data_20251127_1545.xlsx
ga4_vs_utag_comparison_20251127_1545.xlsx
playwright_trace_20251127_1545.zip
```

---

### 2. 🚀 Auto-Launch Dashboard
**Dashboard automatically opens after core.py completes!**

When you run:
```bash
python core.py
```

The script will:
1. ✅ Execute all tests
2. 📹 Record video with timestamp
3. 💾 Save results to Excel files
4. 🎯 Generate runtime_data/last_run.json
5. **🚀 Automatically launch dashboard**
6. 🌐 Open browser at http://127.0.0.1:8050/

---

### 3. 🔄 Latest Run Only Dashboard
**Dashboard shows ONLY the most recent test execution!**

Key features:
- ✅ Displays only current test run data
- ⏰ Shows exact test execution timestamp
- 🔄 Previous data overwritten on each new test
- 📋 Clear "Latest Run" labels throughout
- ℹ️ Info banner explaining no historical data

**Benefits:**
- No confusion about which data is shown
- Always displays current test results
- Timestamp visible at top of dashboard
- Auto-updates with new test runs

---

### 4. 🎨 Glassmorphism Dashboard Design

**Modern, Beautiful UI with:**
- 🌈 Gradient background (purple-pink theme)
- ✨ Semi-transparent glass cards with backdrop blur
- 💎 Frosted glass effect on all elements
- 🎭 Smooth hover animations
- 📊 Transparent charts with white text
- 🎯 Professional metrics cards
- 📈 Interactive visualizations
- 🖱️ Custom styled scrollbars

**Design Features:**
- Glassmorphism cards with rgba(255,255,255,0.15) background
- Backdrop blur of 12px for depth effect
- Soft shadows and borders
- Smooth transitions on hover
- White text with shadow for readability
- Transparent chart backgrounds

---

## 📂 File Structure

```
d:\automation\own\
├── core.py                           # Main test automation script
├── dashboard.py                      # Glassmorphism dashboard
├── runtime_data/
│   └── last_run.json                # Latest test results
├── validation_results/               # All test outputs organized by timestamp
│   ├── playwright_trace_YYYYMMDD_HHMM.zip           # Playwright trace
│   ├── ga4_calls_YYYYMMDD_HHMM.xlsx                 # GA4 analytics data
│   ├── utag_data_YYYYMMDD_HHMM.xlsx                 # Tealium utag data
│   └── ga4_vs_utag_comparison_YYYYMMDD_HHMM.xlsx    # Comparison results
└── videos/
    └── test_run_YYYYMMDD_HHMMSS.webm
```

---

## 🚀 Usage

### Quick Start (Recommended)
```bash
python core.py
```
**That's it!** The dashboard will automatically:
- Start after test completion
- Open in your default browser
- Display all results in beautiful glassmorphism UI

---

### Manual Dashboard Launch
If you want to view previous results:
```bash
python dashboard.py
```
Then open: http://127.0.0.1:8050/

---

## 📊 Dashboard Features

### 1. **Metrics Cards**
- 📋 Total Tests
- ✅ Passed (with count)
- ❌ Failed (with count)
- 📈 Pass Rate (with progress bar)

### 2. **Visualizations**
- 🥧 Pie Chart - Results distribution
- 📊 Bar Chart - Results over time
- 📋 Interactive Table - Detailed test results

### 3. **Interactive Features**
- 🔄 Refresh button to reload latest data
- 🔍 Table filtering and sorting
- 📥 Export to Excel
- 🎯 Hover tooltips
- 📱 Responsive design

---

## 🎨 Design Specifications

### Color Scheme
- **Background Gradient**: Purple (#667eea) → Deep Purple (#764ba2) → Pink (#f093fb)
- **Cards**: rgba(255,255,255,0.15) with 12px blur
- **Text**: White with shadow
- **Success**: #4ade80 (Green)
- **Danger**: #f87171 (Red)
- **Info**: #60a5fa (Blue)

### Typography
- **Font**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Headers**: White with text-shadow
- **Body**: White on glass cards

### Effects
- **Backdrop Blur**: 10-12px
- **Border Radius**: 15px
- **Shadows**: rgba(31, 38, 135, 0.37)
- **Hover Transform**: translateY(-5px)
- **Transitions**: 0.3s ease

---

## 🔧 Technical Details

### Excel Files Format
```
Filename Patterns:
- ga4_calls_YYYYMMDD_HHMM.xlsx          # Google Analytics 4 data
- utag_data_YYYYMMDD_HHMM.xlsx          # Tealium utag_data
- ga4_vs_utag_comparison_YYYYMMDD_HHMM.xlsx  # Comparison results

Examples:
- ga4_calls_20251127_1545.xlsx
- utag_data_20251127_1545.xlsx
- ga4_vs_utag_comparison_20251127_1545.xlsx
```

### Playwright Trace Files Format
```
Filename Pattern: playwright_trace_YYYYMMDD_HHMM.zip
Example: playwright_trace_20251127_1545.zip

Location: validation_results/
Contains: Complete browser session recording
- Screenshots of every action
- Network requests/responses
- Console logs
- DOM snapshots
- Performance metrics

Usage: playwright show-trace validation_results/playwright_trace_20251127_1545.zip
```

### Video Files Format
```
Filename Pattern: test_run_YYYYMMDD_HHMMSS.webm
Example: test_run_20251127_154530.webm
Location: videos/
```

### Runtime Data
```json
{
  "parameter": "order_id / transaction_id",
  "utag_value": "12345",
  "ga4_value": "12345",
  "match": true,
  "hit_number": 1
}
```

---

## 🎯 Data Flow

```
1. Run core.py
   ↓
2. Execute test automation
   ↓
3. Save outputs (all with matching timestamps):
   - 📹 Video: videos/test_run_YYYYMMDD_HHMMSS.webm
   - 🎬 Trace: validation_results/utag.js_trace_YYYYMMDD_HHMM.zip
   - 📊 Excel: validation_results/utag.js_*_YYYYMMDD_HHMM.xlsx
   - 💾 JSON: runtime_data/last_run.json
   ↓
4. Auto-launch dashboard
   ↓
5. Dashboard reads last_run.json (latest run only)
   ↓
6. Display in glassmorphism UI at http://127.0.0.1:8050/
```

**Example Files from One Test Run (15:45):**
```
videos/test_run_20251127_154530.webm
validation_results/playwright_trace_20251127_1545.zip
validation_results/ga4_calls_20251127_1545.xlsx
validation_results/utag_data_20251127_1545.xlsx
validation_results/ga4_vs_utag_comparison_20251127_1545.xlsx
runtime_data/last_run.json
```

---

## ⚙️ Dependencies

Install required packages:
```bash
pip install -r requirements-dashboard.txt
```

**Required:**
- dash
- dash-bootstrap-components
- pandas
- plotly
- playwright

---

## 🎯 Key Improvements

| Feature | Before | After |
|---------|--------|-------|
| **Excel Names** | generic (ga4_calls.xlsx) | utag.js_ga4_calls_20251127_1545.xlsx |
| **Dashboard Launch** | Manual only | Auto-launch after core.py |
| **Design** | Basic Bootstrap | Beautiful Glassmorphism |
| **Video Names** | Hash (00bd3d.webm) | test_run_20251127_154530.webm |
| **User Experience** | Multi-step process | One command, auto-opens |

---

## 📝 Notes

- Dashboard auto-refreshes on button click
- All timestamps use 24-hour format
- Excel files include minutes for precise tracking
- Glassmorphism design works best on modern browsers
- Video recording captures full test execution
- Results persist across sessions

---

## 🐛 Troubleshooting

**Dashboard doesn't auto-launch?**
- Run manually: `python dashboard.py`
- Check if port 8050 is available

**Can't see test results?**
- Run `core.py` first to generate data
- Check `runtime_data/last_run.json` exists

**Glassmorphism effects not showing?**
- Use a modern browser (Chrome, Firefox, Edge)
- Ensure browser supports backdrop-filter

---

## 🎉 Enjoy Your Beautiful Testing Dashboard!

**Made with ❤️ for modern test automation**
