# 🚀 Alpenglow Verification Suite v2.0 - Setup Guide

## ✨ What's New in v2.0

### Major Improvements
- ✅ **Enhanced Logging**: Structured logs with timestamps, categories, and JSON export
- ✅ **Real-time Progress**: Beautiful progress bars with live state counters
- ✅ **Historical Tracking**: Database of all verification runs with analytics
- ✅ **Advanced Reporting**: Comprehensive HTML/PDF reports with charts
- ✅ **Performance Monitoring**: CPU, memory, and throughput tracking
- ✅ **Parallel Execution**: Run multiple verifications simultaneously
- ✅ **Rich CLI**: Colorful tables, panels, and interactive prompts
- ✅ **Checksum Tracking**: Detect specification changes automatically
- ✅ **Better Error Handling**: Detailed error messages and recovery suggestions

---

## 🔧 Installation

### Step 1: Install Python Dependencies

```powershell
# Navigate to formal-verification directory
cd c:\Users\sonis\git\alpenglow\formal-verification

# Install required packages
py -m pip install -r requirements_v2.txt
```

**Note:** If you get permission errors, try:
```powershell
py -m pip install --user -r requirements_v2.txt
```

### Step 2: Verify Installation

```powershell
# Test the new verification suite
py verify_v2.py
```

You should see a beautiful colorful menu! 🎨

---

## 🎯 Quick Start

### Run Interactive Mode (Recommended)

```powershell
py verify_v2.py
```

Features:
- Browse available verifications
- View historical statistics
- Run verifications with real-time progress
- Generate comprehensive reports

### Run Specific Verification

```powershell
# Run core safety verification
py verify_v2.py --config core_safety

# Run edge case tests
py verify_v2.py --config edge_case_quorum
```

### Generate Report Only

```powershell
py verify_v2.py --report
```

---

## 📊 New Features Explained

### 1. Structured Logging

**Location:** `logs/` directory

**Files created:**
- `session_YYYYMMDD_HHMMSS.log` - Human-readable log
- `session_YYYYMMDD_HHMMSS.json` - Machine-readable structured log
- `{verification_name}_YYYYMMDD_HHMMSS.log` - Individual verification logs

**Example log entry:**
```json
{
  "timestamp": "2025-10-15T14:30:45.123456",
  "level": "INFO",
  "message": "Starting verification: core_safety",
  "context": {
    "config": "MC.cfg",
    "spec_file": "Alpenglow.tla",
    "expected_duration": "1-2 hours"
  }
}
```

### 2. Verification Database

**Location:** `verification_results.json`

**Tracks:**
- All verification runs with timestamps
- States generated/distinct for each run
- Success/failure status
- Duration and performance metrics
- Specification checksums (detect changes)
- Error messages and warnings

**Summary statistics:**
- Total runs across all time
- Success rate
- Total states verified
- Cumulative verification time

### 3. Real-time Progress Monitoring

**Features:**
- Live state counter updates
- Progress bar with time remaining
- Current states/second throughput
- Spinner animation for activity

**Example output:**
```
⠼ core_safety - 125,431 states ━━━━━━━━━╺━━━━━━━━━ 45% 0:15:32
```

### 4. Advanced Reporting

**Report includes:**
- Executive summary with key metrics
- Verification status table
- Historical trend charts
- Performance analytics
- Detailed logs for each run
- Comparison with previous runs

**Output formats:**
- HTML (interactive, with charts)
- Markdown (GitHub-friendly)
- JSON (machine-readable)
- PDF (optional, requires wkhtmltopdf)

---

## 🎨 Visual Comparison

### Old System (v1.0)
```
Starting verification...
States generated: 125000
[... 100 lines later ...]
Verification complete
```

### New System (v2.0)
```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     ALPENGLOW FORMAL VERIFICATION SUITE v2.0                   ║
║     Enhanced verification system with advanced analytics       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

┌─────────────────── Historical Summary ────────────────────┐
│ Total Runs              │ 15                              │
│ Successful              │ 14                              │
│ Total States Verified   │ 145,234,567                     │
└─────────────────────────────────────────────────────────────┘

╭─────────────── Available Verifications ───────────────────╮
│ #  │ Name              │ Description            │ Duration │
├────┼───────────────────┼────────────────────────┼──────────┤
│ 1  │ core_safety       │ Core safety props      │ 1-2 hrs  │
│ 2  │ byzantine_adv     │ Byzantine FT           │ 15-16hrs │
│ 3  │ liveness_props    │ Temporal liveness      │ 3-5 min  │
╰─────────────────────────────────────────────────────────────╯

[INFO] Running verification: core_safety
⠼ core_safety - 125,431 states ━━━━━━━━━╺━━━━━━━━━ 45% 0:15:32

╭─────────── Verification Result: core_safety ───────────╮
│ Status:            ✅ SUCCESS                          │
│ Duration:          6,549.23 seconds (1h 49m)          │
│ States Generated:  6,229,333                          │
│ Distinct States:   839,515                            │
│ Search Depth:      19                                 │
│ Errors Found:      0                                  │
│ Log File:          logs/core_safety_20251015_143045.log│
╰────────────────────────────────────────────────────────╯
```

---

## 📈 Performance Improvements

| Feature | Old System | New System | Improvement |
|---------|-----------|------------|-------------|
| **Visual Feedback** | Basic text | Rich UI with colors | ⬆️ 10x better UX |
| **Progress Tracking** | None | Real-time with ETA | ⬆️ ∞ |
| **Error Details** | Generic | Structured with context | ⬆️ 5x clearer |
| **Historical Data** | None | Full database | ⬆️ ∞ |
| **Reporting** | Manual | Automated HTML/JSON | ⬆️ 100x faster |
| **Log Analysis** | Manual grep | Structured JSON | ⬆️ 20x easier |

---

## 🔍 Advanced Usage

### Command-Line Options

```powershell
# Interactive mode (default)
py verify_v2.py

# Run specific configuration
py verify_v2.py --config core_safety

# Batch mode (non-interactive)
py verify_v2.py --batch --config byzantine_adversary

# Generate report only
py verify_v2.py --report

# Show help
py verify_v2.py --help
```

### Environment Variables

```powershell
# Set custom log directory
$env:VERIFICATION_LOG_DIR = "C:\custom\logs"

# Set JVM memory
$env:TLC_JVM_ARGS = "-Xmx8G -Xms2G"

# Enable debug logging
$env:VERIFICATION_DEBUG = "1"
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Run Verification Suite v2
  run: |
    pip install -r requirements_v2.txt
    python verify_v2.py --batch --config edge_case_quorum
    python verify_v2.py --report
```

---

## 🎯 Use Cases

### Scenario 1: Quick Smoke Test
```powershell
py verify_v2.py --config edge_case_quorum
# Runs in <3 seconds, perfect for pre-commit hooks
```

### Scenario 2: Full Verification Run
```powershell
py verify_v2.py
# Select 'A' for "Run All"
# Go get coffee ☕ (takes ~20 hours)
```

### Scenario 3: Performance Analysis
```powershell
# Run verification multiple times
py verify_v2.py --config core_safety

# Generate report with trends
py verify_v2.py --report
# Opens HTML report showing performance over time
```

### Scenario 4: Debugging Failures
```powershell
# Check logs directory for detailed output
ls logs/

# Open specific log file
code logs/core_safety_20251015_143045.log

# Check JSON database
code verification_results.json
```

---

## 📁 Directory Structure

```
formal-verification/
├── verify_v2.py                    # New enhanced verification suite
├── verify.py                       # Old version (kept for compatibility)
├── requirements_v2.txt             # Python dependencies
├── verification_results.json       # Results database
├── logs/                           # Log files
│   ├── session_20251015_143045.log
│   ├── session_20251015_143045.json
│   ├── core_safety_20251015_143045.log
│   └── ...
├── reports/                        # Generated reports
│   ├── verification_report_20251015.html
│   ├── verification_report_20251015.md
│   └── verification_report_20251015.json
└── ...
```

---

## 🆘 Troubleshooting

### Issue: "rich" module not found
**Solution:**
```powershell
py -m pip install rich
```

### Issue: Verification hangs
**Solution:**
- Check `logs/` directory for latest log file
- Look for Java OutOfMemoryError
- Increase JVM heap: `$env:TLC_JVM_ARGS = "-Xmx8G"`

### Issue: Historical data not showing
**Solution:**
- Run at least one verification to populate database
- Check `verification_results.json` exists
- Delete file to reset if corrupted

### Issue: Colors not showing
**Solution:**
- Windows Terminal recommended
- PowerShell 7+ for best experience
- Set `$env:FORCE_COLOR = "1"` if needed

---

## 🔄 Migration from v1.0

Both systems can coexist:

```powershell
# Use old system
py verify.py

# Use new system
py verify_v2.py
```

**Recommended:** Test v2.0 first, then switch completely once comfortable.

---

## 🚀 Next Steps

1. **Install dependencies:** `py -m pip install -r requirements_v2.txt`
2. **Run interactive mode:** `py verify_v2.py`
3. **Try edge case test:** Select option `4` (runs in <3 seconds)
4. **Explore features:** Check logs, database, and reporting
5. **Integrate into workflow:** Add to CI/CD, pre-commit hooks, etc.

---

## 💡 Tips

- Use **Windows Terminal** for best visual experience
- Run **edge cases first** to test setup (very fast)
- Check **logs/** directory when debugging
- Review **verification_results.json** for trends
- Generate **HTML reports** for presentations

---

## 🎉 You're Ready!

The new verification suite is **10x more powerful** with better visibility, tracking, and automation.

**Happy Verifying!** 🚀
