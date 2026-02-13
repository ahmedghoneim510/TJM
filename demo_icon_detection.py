"""
Icon Detection Demo - Generate Annotated Screenshots

This script demonstrates icon detection at different screen positions:
- Top-left area
- Bottom-right area
- Center of screen

Each detection creates an annotated screenshot showing:
- Detected bounding boxes
- Confidence scores
- Icon center position (click target)
"""

import os
import time
from datetime import datetime
from typing import List, Tuple
import cv2
from PIL import ImageGrab
import numpy as np

from utils.ai_vision_detector.detector import detect_notepad_with_ai
from utils.ai_vision_detector.visualization import visualize_grounding
from utils.ai_vision_detector.proposal_generator import generate_proposals
from utils.screenshot_utils import capture_screenshot


def create_annotated_screenshot(
    screenshot_path: str,
    icon_position: Tuple[int, int],
    bbox: Tuple[int, int, int, int],
    location_label: str,
    output_path: str
) -> str:
    """
    Create an annotated screenshot showing icon detection.
    
    Args:
        screenshot_path: Path to original screenshot
        icon_position: (x, y) center position of detected icon
        bbox: (x, y, w, h) bounding box of detected icon
        location_label: Description of icon location (e.g., "Top-Left Area")
        output_path: Where to save the annotated image
    
    Returns:
        Path to saved annotated screenshot
    """
    # Read screenshot
    img = cv2.imread(screenshot_path)
    if img is None:
        raise ValueError(f"Could not read screenshot: {screenshot_path}")
    
    # Create overlay for transparency effect
    overlay = img.copy()
    
    # Unpack values
    x, y = icon_position
    bbox_x, bbox_y, bbox_w, bbox_h = bbox
    
    # Draw bounding box (green, thick)
    cv2.rectangle(
        overlay,
        (bbox_x, bbox_y),
        (bbox_x + bbox_w, bbox_y + bbox_h),
        (0, 255, 0),  # Green
        4
    )
    
    # Draw center point (red circle)
    cv2.circle(overlay, (x, y), 10, (0, 0, 255), -1)
    
    # Draw crosshair at center
    crosshair_size = 30
    cv2.line(
        overlay,
        (x - crosshair_size, y),
        (x + crosshair_size, y),
        (0, 0, 255),
        3
    )
    cv2.line(
        overlay,
        (x, y - crosshair_size),
        (x, y + crosshair_size),
        (0, 0, 255),
        3
    )
    
    # Add labels with background
    # Location label
    label_text = f"{location_label}"
    label_pos = (bbox_x, bbox_y - 60)
    _add_label_with_background(overlay, label_text, label_pos, (0, 255, 0), scale=1.0)
    
    # Position label
    pos_text = f"Position: ({x}, {y})"
    pos_pos = (bbox_x, bbox_y - 30)
    _add_label_with_background(overlay, pos_text, pos_pos, (0, 255, 0), scale=0.7)
    
    # Size label
    size_text = f"Size: {bbox_w}x{bbox_h}px"
    size_pos = (bbox_x, bbox_y + bbox_h + 30)
    _add_label_with_background(overlay, size_text, size_pos, (0, 255, 0), scale=0.6)
    
    # Add title banner at top
    title_text = f"Icon Detection Demo - {location_label}"
    title_height = 60
    cv2.rectangle(overlay, (0, 0), (img.shape[1], title_height), (0, 0, 0), -1)
    cv2.putText(
        overlay,
        title_text,
        (20, 40),
        cv2.FONT_HERSHEY_DUPLEX,
        1.2,
        (255, 255, 255),
        2
    )
    
    # Add timestamp at bottom
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer_text = f"Detected at: {timestamp}"
    img_height = img.shape[0]
    cv2.putText(
        overlay,
        footer_text,
        (20, img_height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )
    
    # Blend overlay with original (slight transparency)
    result = cv2.addWeighted(img, 0.3, overlay, 0.7, 0)
    
    # Save result
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, result)
    
    print(f"✓ Annotated screenshot saved: {output_path}")
    return output_path


def _add_label_with_background(
    img: np.ndarray,
    text: str,
    position: Tuple[int, int],
    color: Tuple[int, int, int],
    scale: float = 0.7
):
    """Add text label with semi-transparent background."""
    font = cv2.FONT_HERSHEY_DUPLEX
    thickness = 2
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thickness)
    
    # Draw background rectangle
    x, y = position
    padding = 5
    cv2.rectangle(
        img,
        (x - padding, y - text_height - padding),
        (x + text_width + padding, y + baseline + padding),
        (0, 0, 0),
        -1
    )
    
    # Draw text
    cv2.putText(img, text, position, font, scale, color, thickness)


def get_screen_region_label(x: int, y: int, screen_width: int, screen_height: int) -> str:
    """
    Determine which region of the screen the icon is in.
    
    Returns: Human-readable label like "Top-Left Area", "Center", etc.
    """
    # Define regions (thirds)
    third_width = screen_width // 3
    third_height = screen_height // 3
    
    # Determine horizontal position
    if x < third_width:
        h_pos = "Left"
    elif x < 2 * third_width:
        h_pos = "Center"
    else:
        h_pos = "Right"
    
    # Determine vertical position
    if y < third_height:
        v_pos = "Top"
    elif y < 2 * third_height:
        v_pos = "Middle"
    else:
        v_pos = "Bottom"
    
    # Combine positions
    if h_pos == "Center" and v_pos == "Middle":
        return "Center of Screen"
    elif x < third_width and y < third_height:
        return "Top-Left Area"
    elif x > 2 * third_width and y > 2 * third_height:
        return "Bottom-Right Area"
    else:
        return f"{v_pos}-{h_pos} Area"


def detect_and_annotate_icon(screenshot_path: str, output_dir: str = "output/demo") -> dict:
    """
    Detect icon in screenshot and create annotated version.
    
    Returns:
        Dictionary with detection results and paths
    """
    print(f"\n{'='*70}")
    print(f"Processing: {os.path.basename(screenshot_path)}")
    print(f"{'='*70}")
    
    try:
        # Load API key
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        # Detect icon using AI vision grounding
        print("\n🔍 Stage 1: Generating candidate proposals...")
        candidates = generate_proposals(screenshot_path, api_key, debug=True)
        
        if not candidates:
            raise ValueError("No icon candidates detected")
        
        # Get best candidate
        from utils.ai_vision_detector.candidate_verifier import verify_and_rank_candidates
        print("\n✓ Stage 2: Verifying and ranking candidates...")
        best_candidate = verify_and_rank_candidates(screenshot_path, candidates, api_key, debug=True)
        
        if best_candidate is None:
            raise ValueError("No valid icon detected")
        
        # Get detection details
        x, y = best_candidate.center
        bbox = (best_candidate.x, best_candidate.y, best_candidate.w, best_candidate.h)
        
        # Determine screen region
        img = cv2.imread(screenshot_path)
        screen_height, screen_width = img.shape[:2]
        location_label = get_screen_region_label(x, y, screen_width, screen_height)
        
        print(f"\n✓ Icon detected at ({x}, {y}) - {location_label}")
        print(f"  Bounding box: {bbox}")
        print(f"  Confidence: {best_candidate.confidence:.2f}")
        
        # Create annotated screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"icon_detected_{location_label.lower().replace(' ', '_')}_{timestamp}.png"
        output_path = os.path.join(output_dir, output_filename)
        
        annotated_path = create_annotated_screenshot(
            screenshot_path,
            (x, y),
            bbox,
            location_label,
            output_path
        )
        
        result = {
            'success': True,
            'position': (x, y),
            'bbox': bbox,
            'location': location_label,
            'confidence': best_candidate.confidence,
            'annotated_screenshot': annotated_path,
            'original_screenshot': screenshot_path
        }
        
        print(f"\n{'='*70}")
        print(f"✓ SUCCESS - {location_label}")
        print(f"{'='*70}\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {
            'success': False,
            'error': str(e),
            'screenshot': screenshot_path
        }


def run_demo():
    """
    Run complete icon detection demo.
    
    Instructions:
    1. This script will prompt you to position an icon in different screen locations
    2. Take a screenshot for each position
    3. The script will detect and annotate each screenshot
    """
    print("\n" + "="*70)
    print("ICON DETECTION DEMO")
    print("="*70)
    print("\nThis demo will detect icons at different screen positions and")
    print("create annotated screenshots showing the detection results.\n")
    
    # Create output directory
    output_dir = "output/demo"
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    # Demo mode: Process existing screenshots or capture new ones
    print("\n" + "="*70)
    print("Demo Mode: We'll capture and analyze your current screen")
    print("="*70)
    
    print("\nPLEASE POSITION AN ICON (e.g., Notepad) in different screen areas")
    print("and press Enter after each position for detection:\n")
    
    positions_to_test = [
        ("TOP-LEFT area", "Move icon to top-left corner of screen"),
        ("BOTTOM-RIGHT area", "Move icon to bottom-right corner of screen"),
        ("CENTER of screen", "Move icon to center of screen"),
    ]
    
    for i, (position_name, instruction) in enumerate(positions_to_test, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}/3: {position_name}")
        print(f"{'─'*70}")
        print(f"📋 {instruction}")
        input(f"Press Enter when icon is positioned in {position_name}...")
        
        # Capture screenshot
        screenshot_path = capture_screenshot(save_dir="output/demo/screenshots")
        print(f"✓ Screenshot captured: {screenshot_path}")
        
        # Wait a moment for any window animations
        time.sleep(0.5)
        
        # Detect and annotate
        result = detect_and_annotate_icon(screenshot_path, output_dir)
        results.append(result)
        
        # Small pause between tests
        if i < len(positions_to_test):
            time.sleep(2)
    
    # Generate summary report
    print("\n" + "="*70)
    print("DEMO COMPLETE - SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r.get('success', False))
    print(f"\n✓ Successful detections: {successful}/{len(results)}")
    
    print("\n📁 Annotated Screenshots:")
    for i, result in enumerate(results, 1):
        if result.get('success'):
            print(f"  {i}. {result['location']}")
            print(f"     Position: {result['position']}")
            print(f"     File: {os.path.basename(result['annotated_screenshot'])}")
        else:
            print(f"  {i}. FAILED - {result.get('error', 'Unknown error')}")
    
    print(f"\n📂 All files saved to: {os.path.abspath(output_dir)}")
    print("\n" + "="*70 + "\n")
    
    return results


if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("❌ Error: .env file not found!")
        print("\nPlease create a .env file with your GEMINI_API_KEY:")
        print("  GEMINI_API_KEY=your_api_key_here")
        exit(1)
    
    # Run the demo
    results = run_demo()
    
    # Return exit code based on success
    successful = sum(1 for r in results if r.get('success', False))
    exit(0 if successful == len(results) else 1)
