# Output Directory

This folder stores generated screenshots and visualizations.

## Files Generated Here:

- `grounding_test_detailed.png` - Detailed test with full annotations
- `interview_top_left.png` - Icon in top-left position
- `interview_bottom_right.png` - Icon in bottom-right position
- `interview_center.png` - Icon in center position
- `interview_custom.png` - Icon in custom position
- `grounding_attempt_*.png` - Retry attempts with visualization enabled

## Annotations:

All images contain:

- 🟠 **Orange boxes**: Candidate proposals (Stage 1)
- 🟢 **Green box**: Final selection (Stage 2)
- 🔵 **Blue dots**: Click coordinates
- 📊 **Labels**: Confidence scores and metadata

## Usage:

Generate screenshots by running:

```bash
python generate_screenshots.py
# or
python test_grounding.py  # option 2 or 3
```
