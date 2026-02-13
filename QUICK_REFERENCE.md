# Icon Detection Demo - Quick Reference Guide

## 🎯 Meeting the Requirements

Your project needs:

1. ✅ Source code with clear structure on Github
2. ✅ UV configuration
3. ✅ At least 3 annotated screenshots showing:
   - Icon detected in top-left area
   - Icon detected in bottom-right area
   - Icon detected in center of screen

**All requirements are ready!** Just run the demo script.

---

## ⚡ 3-Minute Setup

### 1. Check UV Configuration

Your `pyproject.toml` is already configured:

```bash
# View configuration
cat pyproject.toml

# Should show:
# - name = "tjm-project-automation"
# - dependencies with opencv-python, google-genai, etc.
# - [tool.uv] section
```

✅ **UV config is complete!**

### 2. Install Dependencies

```bash
# Using UV (recommended)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# OR using pip
pip install -r requirements.txt
```

### 3. Set API Key

```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Get your key from: https://aistudio.google.com/app/apikey
```

### 4. Run Demo

```bash
python demo_icon_detection.py
```

---

## 📸 Using the Demo Script

The script will guide you through 3 tests:

### Test 1: Top-Left Detection

```
1. Move an icon (e.g., Notepad) to TOP-LEFT corner
2. Press Enter
3. Script captures screenshot and detects icon
4. Saves annotated image showing detection
```

### Test 2: Bottom-Right Detection

```
1. Move the same icon to BOTTOM-RIGHT corner
2. Press Enter
3. Script detects and annotates
```

### Test 3: Center Detection

```
1. Move icon to CENTER of screen
2. Press Enter
3. Script detects and annotates
```

**Total time: ~2-3 minutes**

---

## 📂 Finding Your Screenshots

After running the demo, find your deliverables in:

```
output/demo/
├── icon_detected_top-left_area_[timestamp].png      ← Deliverable 1
├── icon_detected_bottom-right_area_[timestamp].png  ← Deliverable 2
├── icon_detected_center_of_screen_[timestamp].png   ← Deliverable 3
└── screenshots/
    └── [original screenshots before annotation]
```

**These 3 annotated PNG files are your deliverables!**

---

## ✨ What the Annotations Show

Each screenshot displays:

✅ **Green bounding box** - Area containing the detected icon  
✅ **Red crosshair** - Exact click position (center point)  
✅ **Position label** - "Top-Left Area", "Bottom-Right Area", etc.  
✅ **Coordinates** - Exact (x, y) pixel position  
✅ **Size information** - Width x Height of detected icon  
✅ **Timestamp** - When detection occurred  
✅ **Title banner** - "Icon Detection Demo - [Location]"

---

## 🔍 How It Works (Simplified)

```
1. Capture screenshot
         ↓
2. AI analyzes entire screen
   (finds candidate regions)
         ↓
3. AI verifies each candidate
   (selects best match)
         ↓
4. Draw annotations
   (green box, red crosshair, labels)
         ↓
5. Save annotated screenshot
```

**Technology:** Two-stage visual grounding using Google Gemini AI

---

## 🚀 Uploading to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Icon detection system with demo"

# Create GitHub repository, then:
git remote add origin https://github.com/yourusername/tjm-project-automation.git
git branch -M main
git push -u origin main
```

**Include in your README:**

- Link to demo screenshots in `output/demo/`
- Reference to `ICON_DETECTION_DEMO.md` for detailed docs
- Mention UV configuration in `pyproject.toml`

---

## 📋 Submission Checklist

Before submitting, verify you have:

- [ ] ✅ GitHub repository with clear code structure
  - All files organized in logical folders
  - `utils/ai_vision_detector/` contains detection code
  - `demo_icon_detection.py` is the main demo script

- [ ] ✅ UV configuration in `pyproject.toml`
  - Dependencies listed
  - `[tool.uv]` section present
  - Can install with `uv pip install -e .`

- [ ] ✅ 3 annotated screenshots:
  - `icon_detected_top-left_area_*.png`
  - `icon_detected_bottom-right_area_*.png`
  - `icon_detected_center_of_screen_*.png`

- [ ] ✅ Documentation
  - `README.md` with project overview
  - `ICON_DETECTION_DEMO.md` with detailed guide
  - Comments in code explaining key functions

---

## 🎓 Code Structure Overview

### Main Demo Script

**File:** `demo_icon_detection.py`

```python
# User-facing demo script
# - Prompts user to position icon
# - Captures screenshots
# - Detects and annotates
# - Saves results
```

### Detection Engine

**Directory:** `utils/ai_vision_detector/`

```python
detector.py              # Main entry point
proposal_generator.py    # Stage 1: Find candidates
candidate_verifier.py    # Stage 2: Verify & rank
visualization.py         # Create annotations
models.py               # Data structures
```

### Key Function

```python
from utils.ai_vision_detector.detector import detect_notepad_with_ai

# Detect icon in screenshot
x, y = detect_notepad_with_ai("screenshot.png", debug=True)
# Returns: Center coordinates for clicking
```

---

## ❓ Quick Troubleshooting

### "GEMINI_API_KEY not found"

```bash
# Create .env file with your key
echo "GEMINI_API_KEY=your_actual_key_here" > .env
```

### "No icon detected"

- Make sure icon is visible and not obscured
- Icon should be at least 30x30 pixels
- Try with a clearer icon (Notepad works best)

### "Detection took too long"

- Normal detection: 3-5 seconds
- Check internet connection (API requires network)
- Large screenshots (>1920x1080) take longer

### Need help?

Check detailed docs: [ICON_DETECTION_DEMO.md](ICON_DETECTION_DEMO.md)

---

## 🎯 One-Command Demo

If you just want to test quickly:

```bash
# Setup and run in one go
uv venv && source .venv/bin/activate && uv pip install -e . && python demo_icon_detection.py
```

_(Windows PowerShell:)_

```powershell
uv venv; .\.venv\Scripts\activate; uv pip install -e .; python demo_icon_detection.py
```

---

## 📊 Expected Output

```
==================================================================
ICON DETECTION DEMO
==================================================================

This demo will detect icons at different screen positions and
create annotated screenshots showing the detection results.

==================================================================
Demo Mode: We'll capture and analyze your current screen
==================================================================

PLEASE POSITION AN ICON (e.g., Notepad) in different screen areas
and press Enter after each position for detection:

──────────────────────────────────────────────────────────────────
Test 1/3: TOP-LEFT area
──────────────────────────────────────────────────────────────────
📋 Move icon to top-left corner of screen
Press Enter when icon is positioned in TOP-LEFT area...

✓ Screenshot captured: output/demo/screenshots/screenshot_20260213_143052.png

==================================================================
Processing: screenshot_20260213_143052.png
==================================================================

🔍 Stage 1: Generating candidate proposals...
[AI processing...]

✓ Stage 2: Verifying and ranking candidates...
[AI verification...]

✓ Icon detected at (150, 120) - Top-Left Area
  Bounding box: (130, 100, 40, 40)
  Confidence: 0.95

✓ Annotated screenshot saved: output/demo/icon_detected_top-left_area_20260213_143052.png

==================================================================
✓ SUCCESS - Top-Left Area
==================================================================

[... continues for Test 2 and Test 3 ...]

==================================================================
DEMO COMPLETE - SUMMARY
==================================================================

✓ Successful detections: 3/3

📁 Annotated Screenshots:
  1. Top-Left Area
     Position: (150, 120)
     File: icon_detected_top-left_area_20260213_143052.png
  2. Bottom-Right Area
     Position: (1850, 1000)
     File: icon_detected_bottom-right_area_20260213_143115.png
  3. Center of Screen
     Position: (960, 540)
     File: icon_detected_center_of_screen_20260213_143138.png

📂 All files saved to: D:\tjm-project-automation\output\demo

==================================================================
```

---

## 🎁 Bonus: Custom Detection

Want to detect other icons? Modify the detection query:

**File:** `utils/ai_vision_detector/proposal_generator.py`

```python
# Current (Notepad icon)
prompt = "Find the Notepad icon on this desktop screenshot..."

# Change to detect other icons
prompt = "Find the Chrome browser icon on this desktop..."
prompt = "Find the Visual Studio Code icon on this desktop..."
prompt = "Find the Recycle Bin icon on this desktop..."
```

Then run the demo again!

---

## 📚 Learn More

- **Full documentation:** [ICON_DETECTION_DEMO.md](ICON_DETECTION_DEMO.md)
- **Technical details:** [GROUNDING_DOCUMENTATION.md](GROUNDING_DOCUMENTATION.md)
- **Project overview:** [README.md](README.md)
- **Setup guide:** [SETUP_SUMMARY.md](SETUP_SUMMARY.md)

---

**Ready to generate your screenshots?**

```bash
python demo_icon_detection.py
```

**Good luck! 🚀**
