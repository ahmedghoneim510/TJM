"""
Quick Screenshot Generator for Interview
Generates multiple screenshots with Notepad icon in different positions.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.screenshot_utils import take_screenshot
from utils.ai_vision_detector import (
    generate_proposals,
    verify_and_rank_candidates,
    visualize_grounding
)


def generate_single_screenshot(position_name: str):
    """Generate a single annotated screenshot at current icon position."""
    api_key = "AIzaSyDKW_eUhMmu-4fkBF8JquhL7-J3a2Isnqk"
    
    print(f"\n{'='*70}")
    print(f"Capturing: {position_name}")
    print(f"{'='*70}")
    
    try:
        # Take screenshot
        screenshot_path = take_screenshot()
        print(f"✓ Screenshot captured")
        
        # Stage 1: Generate proposals
        print(f"\nStage 1: Generating proposals...")
        candidates = generate_proposals(screenshot_path, api_key, debug=False)
        
        if not candidates:
            print(f"✗ No candidates found")
            return False
        
        print(f"✓ Found {len(candidates)} candidate(s)")
        
        # Stage 2: Verify and rank
        print(f"\nStage 2: Verifying candidates...")
        best = verify_and_rank_candidates(screenshot_path, candidates, api_key, debug=False)
        
        if best is None:
            print(f"✗ No candidates verified")
            return False
        
        x, y = best.center
        print(f"✓ Icon detected at ({x}, {y}) - Confidence: {best.confidence:.2f}")
        
        # Save visualization
        output_path = os.path.join("output", f"interview_{position_name.lower().replace(' ', '_')}.png")
        visualize_grounding(screenshot_path, candidates, best, output_path)
        
        print(f"✓ Screenshot saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Interactive screenshot generation."""
    print("\n" + "="*70)
    print("INTERVIEW SCREENSHOT GENERATOR")
    print("="*70)
    print("\nThis will generate annotated screenshots showing icon detection")
    print("in different positions on your desktop.")
    print("\nInstructions:")
    print("1. Move the Notepad icon to the specified position")
    print("2. Press Enter to capture")
    print("3. Repeat for all positions")
    print("\n" + "="*70)
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    positions = [
        "TOP_LEFT",
        "BOTTOM_RIGHT",
        "CENTER",
        "CUSTOM"
    ]
    
    for i, position in enumerate(positions, 1):
        print(f"\n📍 Position {i}/4: {position}")
        print(f"Move the Notepad icon to the {position.replace('_', '-').lower()} area of your desktop")
        input(f"Press Enter when ready...")
        
        success = generate_single_screenshot(position)
        
        if not success:
            print(f"⚠️  Failed to capture {position}. Continue anyway? (y/n): ", end="")
            if input().lower() != 'y':
                break
    
    print("\n" + "="*70)
    print("✓ SCREENSHOT GENERATION COMPLETE")
    print("="*70)
    print(f"\nGenerated screenshots are in the 'output/' folder:")
    print("- interview_top_left.png")
    print("- interview_bottom_right.png")
    print("- interview_center.png")
    print("- interview_custom.png")
    print("\nThese images show:")
    print("  🟠 Orange boxes: Candidate proposals (Stage 1)")
    print("  🟢 Green box: Final selection (Stage 2)")
    print("  🔵 Blue dot: Click coordinates")
    print("  📊 Labels: Confidence scores")
    print("\nYou can now use these for your interview presentation!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
