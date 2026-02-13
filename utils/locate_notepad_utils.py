from utils.screenshot_utils import take_screenshot
from utils.ai_vision_detector import (
    detect_notepad_with_ai, 
    generate_proposals, 
    verify_and_rank_candidates,
    visualize_grounding
)
from utils.icon_detection import find_icon_by_template, IconNotFoundError
from time import sleep
import os
from dotenv import load_dotenv

load_dotenv()

def locate_notepad_icon(max_attempts=3, wait_time=1, debug=True, save_visualization=False, use_fallback=True):
    """
    Locate the Notepad icon using two-stage visual grounding with retry logic.
    
    Args:
        max_attempts: Number of retry attempts
        wait_time: Seconds to wait between attempts
        debug: Print detailed grounding information
        save_visualization: Save annotated screenshots showing grounding process
        use_fallback: Use template matching as fallback if AI grounding fails
    
    Returns: 
        (x, y) center coordinates if found
    
    Raises: 
        Exception if not found after retries
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    
    for attempt in range(1, max_attempts + 1):
        screenshot_path = None
        try:
            screenshot_path = take_screenshot()
            
            if save_visualization:
                # Use detailed grounding with visualization
                candidates = generate_proposals(screenshot_path, api_key, debug)
                best = verify_and_rank_candidates(screenshot_path, candidates, api_key, debug)
                
                if best is None:
                    raise ValueError("No valid candidates found")
                
                # Save annotated screenshot
                viz_path = os.path.join("output", f"grounding_attempt_{attempt}.png")
                visualize_grounding(screenshot_path, candidates, best, viz_path)
                
                x, y = best.center
            else:
                # Use simplified detection
                x, y = detect_notepad_with_ai(screenshot_path, debug=debug)
            
            print(f"✓ Notepad icon found at ({x}, {y}) on attempt {attempt}")
            return x, y
            
        except (ValueError, Exception) as e:
            error_msg = str(e)
            print(f"❌ Attempt {attempt}/{max_attempts}: AI grounding failed - {error_msg}")
            
            # Try fallback template matching if enabled
            if use_fallback and screenshot_path and attempt == max_attempts:
                if debug:
                    print("\n🔄 Attempting fallback: Template matching...")
                
                # Look for template files in assets folder
                template_paths = [
                    "assets/notepad_icon.png",
                    "assets/notepad_template.png",
                    "assets/notepad.png"
                ]
                
                for template_path in template_paths:
                    if os.path.exists(template_path):
                        try:
                            x, y = find_icon_by_template(screenshot_path, template_path, threshold=0.7, debug=debug)
                            print(f"✓ Notepad found via template matching at ({x}, {y})")
                            return x, y
                        except IconNotFoundError as icon_err:
                            if debug:
                                print(f"   Template {template_path}: {icon_err}")
                            continue
                        except Exception as tmpl_err:
                            if debug:
                                print(f"   Template matching error: {tmpl_err}")
                            continue
                
                if debug:
                    print("⚠️  Template matching failed - no matching templates found")
                    print("\n💡 Troubleshooting tips:")
                    print("   1. Ensure Notepad icon is visible on desktop or taskbar")
                    print("   2. Check network connection (API requires internet)")
                    print("   3. Try creating a Notepad desktop shortcut")
                    print("   4. Add a Notepad icon template to assets/ folder")
            
            if attempt < max_attempts:
                if debug:
                    print(f"⏳ Waiting {wait_time}s before retry...\\n")
                sleep(wait_time)
            else:
                raise Exception(
                    f"Notepad icon could not be located after {max_attempts} attempts. "
                    f"Please ensure Notepad is visible on your desktop or taskbar."
                )
                
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            break

    raise Exception("Notepad icon could not be located after multiple attempts.")