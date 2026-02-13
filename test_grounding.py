"""
Visual Grounding Demo & Test Script

This script demonstrates the two-stage visual grounding system:
1. Stage 1: Generate candidate proposals (bounding boxes)
2. Stage 2: Verify and rank candidates, select best match

Run this to test icon detection and generate annotated screenshots for the interview.
"""

import os
import sys
from utils.screenshot_utils import take_screenshot
from utils.ai_vision_detector import (
    generate_proposals,
    verify_and_rank_candidates,
    visualize_grounding,
    detect_notepad_with_ai
)


def test_basic_grounding():
    """Test basic grounding without visualization."""
    print("\n" + "="*70)
    print("TEST 1: Basic Grounding (Simplified)")
    print("="*70)
    
    try:
        screenshot_path = take_screenshot()
        x, y = detect_notepad_with_ai(screenshot_path, debug=True)
        print(f"\n✓ SUCCESS: Notepad icon located at ({x}, {y})")
        print(f"You can double-click at these coordinates to launch Notepad.")
        return True
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        return False


def test_detailed_grounding_with_visualization():
    """Test detailed two-stage grounding with visual annotation."""
    print("\n" + "="*70)
    print("TEST 2: Detailed Two-Stage Grounding with Visualization")
    print("="*70)
    
    api_key = "AIzaSyDKW_eUhMmu-4fkBF8JquhL7-J3a2Isnqk"
    
    try:
        # Take screenshot
        screenshot_path = take_screenshot()
        print(f"\n📸 Screenshot captured: {screenshot_path}")
        
        # Stage 1: Generate proposals
        print("\n--- STAGE 1: Proposal Generation ---")
        candidates = generate_proposals(screenshot_path, api_key, debug=True)
        
        if not candidates:
            print("\n✗ No candidates generated")
            return False
        
        # Stage 2: Verify and rank
        print("\n--- STAGE 2: Verification & Ranking ---")
        best = verify_and_rank_candidates(screenshot_path, candidates, api_key, debug=True)
        
        if best is None:
            print("\n✗ No candidates verified")
            return False
        
        # Visualize results
        print("\n--- VISUALIZATION ---")
        viz_path = os.path.join("output", "grounding_test_detailed.png")
        visualize_grounding(screenshot_path, candidates, best, viz_path)
        
        x, y = best.center
        print(f"\n✓ SUCCESS: Notepad icon located at ({x}, {y})")
        print(f"   Confidence: {best.confidence:.2f}")
        print(f"   Source: {best.source}")
        print(f"   Bounding box: ({best.x}, {best.y}, {best.w}, {best.h})")
        print(f"\n📊 Annotated screenshot saved to: {viz_path}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_interview_screenshots():
    """
    Generate annotated screenshots for interview demonstration.
    Move the Notepad icon to different positions and run this.
    """
    print("\n" + "="*70)
    print("TEST 3: Generate Interview Demonstration Screenshots")
    print("="*70)
    print("\nInstructions:")
    print("1. Move Notepad icon to TOP-LEFT corner of desktop")
    print("2. Press Enter to capture...")
    
    positions = [
        ("top_left", "Move icon to TOP-LEFT corner"),
        ("bottom_right", "Move icon to BOTTOM-RIGHT corner"),
        ("center", "Move icon to CENTER of desktop"),
        ("custom", "Place icon at any custom position")
    ]
    
    results = []
    
    for position_name, instruction in positions:
        print(f"\n📍 Position: {position_name.upper()}")
        print(f"   {instruction}")
        input("   Press Enter when ready...")
        
        api_key = "AIzaSyDKW_eUhMmu-4fkBF8JquhL7-J3a2Isnqk"
        
        try:
            screenshot_path = take_screenshot()
            candidates = generate_proposals(screenshot_path, api_key, debug=False)
            best = verify_and_rank_candidates(screenshot_path, candidates, api_key, debug=False)
            
            if best:
                viz_path = os.path.join("output", f"interview_demo_{position_name}.png")
                visualize_grounding(screenshot_path, candidates, best, viz_path)
                
                x, y = best.center
                print(f"   ✓ Detected at ({x}, {y}) - Confidence: {best.confidence:.2f}")
                print(f"   📸 Saved: {viz_path}")
                results.append((position_name, x, y, best.confidence, viz_path))
            else:
                print(f"   ✗ Detection failed")
                results.append((position_name, None, None, 0.0, None))
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
            results.append((position_name, None, None, 0.0, None))
    
    # Summary
    print("\n" + "="*70)
    print("INTERVIEW DEMONSTRATION SUMMARY")
    print("="*70)
    print(f"\n{'Position':<15} {'Coordinates':<20} {'Confidence':<12} {'Status':<10}")
    print("-" * 70)
    
    for pos, x, y, conf, path in results:
        coord_str = f"({x}, {y})" if x and y else "N/A"
        conf_str = f"{conf:.2f}" if conf > 0 else "N/A"
        status = "✓ SUCCESS" if x and y else "✗ FAILED"
        print(f"{pos:<15} {coord_str:<20} {conf_str:<12} {status:<10}")
    
    print("\n" + "="*70)
    print(f"Screenshots saved in: {os.path.abspath('output')}")
    print("="*70)


def main():
    """Run all grounding tests."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "VISUAL GROUNDING SYSTEM TEST SUITE" + " "*19 + "║")
    print("╚" + "="*68 + "╝")
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    print("\nSelect test mode:")
    print("1. Quick test (basic grounding)")
    print("2. Detailed test (with visualization)")
    print("3. Generate interview demo screenshots")
    print("4. Run all tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        test_basic_grounding()
    elif choice == "2":
        test_detailed_grounding_with_visualization()
    elif choice == "3":
        generate_interview_screenshots()
    elif choice == "4":
        test_basic_grounding()
        print("\n" + "-"*70 + "\n")
        test_detailed_grounding_with_visualization()
        print("\n" + "-"*70 + "\n")
        response = input("Generate interview screenshots? (y/n): ")
        if response.lower() == 'y':
            generate_interview_screenshots()
    else:
        print("Invalid choice. Running basic test...")
        test_basic_grounding()


if __name__ == "__main__":
    main()
