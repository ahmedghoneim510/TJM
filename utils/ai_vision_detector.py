
import os
import json
import re
from pathlib import Path
import PIL.Image
from google import genai
from google.genai import types
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import time
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()


def extract_candidates_via_regex(text: str, debug: bool = False) -> dict:
    """
    Last-resort fallback: extract candidate objects from broken/truncated JSON 
    using regex to find individual {x, y, w, h} patterns.
    Works even when JSON is completely malformed.
    """
    # Find all objects that have at least x, y, w, h numeric values
    # Matches patterns like: "x": 124, "y": 662, "w": 48, "h": 68
    pattern = r'"x"\s*:\s*(\d+)\s*,\s*"y"\s*:\s*(\d+)\s*,\s*"w"\s*:\s*(\d+)\s*,\s*"h"\s*:\s*(\d+)'
    matches = re.findall(pattern, text)
    
    if not matches:
        # Try alternate field order
        pattern2 = r'"x"\s*:\s*(\d+).*?"y"\s*:\s*(\d+).*?"w"\s*:\s*(\d+).*?"h"\s*:\s*(\d+)'
        matches = re.findall(pattern2, text, re.DOTALL)
    
    if matches:
        candidates = []
        for m in matches:
            candidates.append({
                "x": int(m[0]), "y": int(m[1]),
                "w": int(m[2]), "h": int(m[3]),
                "c": 0.85  # Default confidence for regex-extracted candidates
            })
        
        # Try to extract confidence for each match
        conf_pattern = r'"(?:c|confidence)"\s*:\s*(0?\.\d+|1(?:\.0)?)'
        conf_matches = re.findall(conf_pattern, text)
        for i, conf in enumerate(conf_matches):
            if i < len(candidates):
                candidates[i]["c"] = float(conf)
        
        if debug:
            print(f"✓ Regex extraction found {len(candidates)} candidates from broken JSON")
        
        return {"found": True, "candidates": candidates}
    
    return {"found": False, "candidates": []}


def repair_truncated_json(text: str, debug: bool = False) -> str:
    """
    Attempt to repair truncated JSON responses from AI.
    Handles cases where JSON is cut off mid-way, including unterminated strings.
    """
    # First, try to extract JSON block from markdown code fence
    json_block_match = re.search(r'```json\s*([\s\S]*?)```', text)
    if json_block_match:
        text = json_block_match.group(1).strip()
    else:
        # Also match unclosed code fence (truncated response)
        json_block_match = re.search(r'```json\s*([\s\S]*)', text)
        if json_block_match:
            text = json_block_match.group(1).strip()
        else:
            # Try to find just the JSON object
            start = text.find('{')
            if start != -1:
                text = text[start:]
    
    # Remove trailing incomplete elements
    text = re.sub(r',\s*\.\.\.', '', text)  # Remove ", ..."
    text = re.sub(r'\.\.\.\s*$', '', text)  # Remove trailing "..."
    
    # Try parsing as-is first
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass
    
    # Handle unterminated strings by finding and removing incomplete trailing content
    # Remove the last incomplete key-value pair line(s) progressively
    lines = text.split('\n')
    for _ in range(min(5, len(lines))):  # Try removing up to 5 trailing lines
        # Remove trailing line
        removed_line = lines.pop().strip()
        text_attempt = '\n'.join(lines).rstrip().rstrip(',')
        
        # Count brackets and braces
        open_braces = text_attempt.count('{') - text_attempt.count('}')
        open_brackets = text_attempt.count('[') - text_attempt.count(']')
        
        # Add missing closers
        fixed = text_attempt + ']' * open_brackets + '}' * open_braces
        
        try:
            json.loads(fixed)
            if debug:
                print(f"✓ JSON repaired by removing {_ + 1} trailing line(s)")
            return fixed
        except json.JSONDecodeError:
            continue
    
    # If line-by-line removal didn't work, try aggressive regex cleanup on original  
    text_clean = text
    # Remove incomplete key-value pairs at end
    text_clean = re.sub(r',\s*"[^"]*$', '', text_clean)  # '"key (no closing quote)
    text_clean = re.sub(r',\s*"[^"]*"\s*:\s*"[^"]*$', '', text_clean)  # "key": "val (no closing quote)
    text_clean = re.sub(r',\s*"[^"]*"\s*:\s*"?[^"{}\[\],]*$', '', text_clean)
    text_clean = re.sub(r',\s*"[^"]*"\s*:\s*$', '', text_clean)
    text_clean = re.sub(r',\s*\{[^}]*$', '', text_clean)  # Remove incomplete object
    text_clean = re.sub(r',\s*$', '', text_clean.rstrip())
    
    open_braces = text_clean.count('{') - text_clean.count('}')
    open_brackets = text_clean.count('[') - text_clean.count(']')
    text_clean += ']' * open_brackets + '}' * open_braces
    
    try:
        json.loads(text_clean)
        if debug:
            print(f"✓ JSON repaired via regex cleanup")
        return text_clean
    except json.JSONDecodeError as e:
        if debug:
            print(f"⚠️ JSON repair failed: {e}")
        raise


class GroundingCandidate:
    """Represents a grounding proposal with bounding box and confidence."""
    def __init__(self, x: int, y: int, w: int, h: int, confidence: float, source: str = "ai"):
        self.x = x  # Top-left x
        self.y = y  # Top-left y
        self.w = w  # Width
        self.h = h  # Height
        self.confidence = confidence
        self.source = source
        
    @property
    def center(self) -> Tuple[int, int]:
        """Return center coordinates for clicking."""
        return (self.x + self.w // 2, self.y + self.h // 2)
    
    @property
    def area(self) -> int:
        return self.w * self.h
    
    def __repr__(self):
        return f"GroundingCandidate(center={self.center}, bbox=({self.x},{self.y},{self.w},{self.h}), conf={self.confidence:.2f})"


def compress_image(img: PIL.Image.Image, max_size: int = 1920) -> PIL.Image.Image:
    """
    Compress image to reduce upload size and prevent network timeouts.
    """
    # Resize if larger than max_size
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, PIL.Image.Resampling.LANCZOS)
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Compress to JPEG with quality reduction
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85, optimize=True)
    buffer.seek(0)
    return PIL.Image.open(buffer)


def generate_proposals(screenshot_path: str, api_key: str, debug: bool = False) -> List[GroundingCandidate]:
    """
    Stage 1: Generate candidate regions using AI vision grounding.
    Returns multiple bounding box proposals with confidence scores.
    """
    client = genai.Client(api_key=api_key)
    
    if not os.path.exists(screenshot_path):
        raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")

    # Load and compress image to prevent network timeouts
    img = PIL.Image.open(screenshot_path)
    original_size = img.size
    img = compress_image(img)
    
    if debug and img.size != original_size:
        print(f"📦 Image compressed: {original_size} → {img.size}")
    
    # Stage 1 Prompt: Ultra-compact, explicit about PIXEL coordinates
    proposal_prompt = f"""Look at this {img.size[0]}x{img.size[1]} pixel screenshot. Find the Windows Notepad icon.

Return PIXEL coordinates (not normalized). x,y = top-left corner in pixels. w,h = size in pixels.
For example, on a {img.size[0]}x{img.size[1]} image, x ranges 0-{img.size[0]}, y ranges 0-{img.size[1]}.

Output ONLY one line of JSON:
{{"found":true,"candidates":[{{"x":100,"y":500,"w":64,"h":64,"c":0.9}}]}}

No markdown. No explanation. No extra fields."""

    # Retry logic for network errors
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            if debug and attempt > 0:
                print(f"🔄 Retry attempt {attempt + 1}/{max_retries}...")
            
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[proposal_prompt, img],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=2048,
                )
            )
            break  # Success, exit retry loop
            
        except Exception as e:
            error_msg = str(e)
            is_network_error = any(x in error_msg.lower() for x in ['ssl', 'connection', 'timeout', 'network', 'socket'])
            
            if is_network_error and attempt < max_retries - 1:
                if debug:
                    print(f"⚠️ Network error: {e}")
                    print(f"   Waiting {retry_delay}s before retry...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                # Non-network error or final attempt
                raise
    
    try:
        full_text = response.text
        if debug:
            print(f"\n=== Stage 1: Proposal Generation ===")
            print(f"Raw AI Response:\n{full_text[:500]}...\n" if len(full_text) > 500 else f"Raw AI Response:\n{full_text}\n")

        result = None
        
        # Strategy 1: Try repair_truncated_json
        try:
            repaired_json = repair_truncated_json(full_text, debug=debug)
            result = json.loads(repaired_json)
        except Exception:
            pass
        
        # Strategy 2: Greedy regex for outermost JSON object
        if result is None:
            try:
                json_match = re.search(r'\{.*\}', full_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Extract candidates via regex from broken JSON (last resort)
        if result is None:
            if debug:
                print("🔧 Using regex extraction fallback on broken JSON...")
            result = extract_candidates_via_regex(full_text, debug=debug)
            if not result.get("candidates"):
                raise Exception(f"Could not extract any candidates from AI response")

        if not result.get("found", True) and not result.get("candidates"):
            if debug:
                print("⚠️ No candidates found in Stage 1")
            return []

        # Convert to GroundingCandidate objects
        candidates = []
        for c in result["candidates"]:
            raw_x, raw_y = int(c["x"]), int(c["y"])
            raw_w, raw_h = int(c["w"]), int(c["h"])
            
            # Detect if coordinates are in normalized 0-1000 range (Gemini default)
            # Heuristic: if all coords suggest they're in 0-1000 range relative to image size
            img_w, img_h = img.size
            max_coord = max(raw_x + raw_w, raw_y + raw_h)
            likely_normalized = (
                max_coord <= 1000 and 
                img_w > 1000 and
                (raw_x + raw_w) <= 1000 and 
                (raw_y + raw_h) <= 1000
            )
            
            if likely_normalized:
                # Convert from 0-1000 normalized to actual pixels
                px_x = int(raw_x * img_w / 1000)
                px_y = int(raw_y * img_h / 1000)
                px_w = int(raw_w * img_w / 1000)
                px_h = int(raw_h * img_h / 1000)
                if debug:
                    print(f"  📐 Normalized coords detected: ({raw_x},{raw_y}) → pixel ({px_x},{px_y})")
            else:
                # Already pixel coordinates
                px_x, px_y, px_w, px_h = raw_x, raw_y, raw_w, raw_h
            
            # Scale coordinates back to original size if image was resized
            scale_x = original_size[0] / img_w
            scale_y = original_size[1] / img_h
            
            # Support both "confidence" and "c" field names
            conf = c.get("confidence", c.get("c", 0.5))
            
            candidate = GroundingCandidate(
                x=int(px_x * scale_x),
                y=int(px_y * scale_y),
                w=int(px_w * scale_x),
                h=int(px_h * scale_y),
                confidence=float(conf),
                source=c.get("location", "ai")
            )
            candidates.append(candidate)
        
        if debug:
            print(f"✓ Generated {len(candidates)} proposals:")
            for i, c in enumerate(candidates, 1):
                print(f"  {i}. {c}")
        
        return candidates

    except Exception as e:
        error_msg = str(e)
        if debug:
            print(f"❌ Parsing error: {error_msg}")
            try:
                print(f"   Response (first 300): {full_text[:300]}")
            except:
                pass
        
        # Fallback to older model for 404 errors
        if "404" in error_msg or "not found" in error_msg.lower():
            if debug:
                print("🔄 Falling back to gemini-1.5-flash...")
            try:
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=[proposal_prompt, img]
                )
                fallback_text = response.text
                result = None
                try:
                    repaired_json = repair_truncated_json(fallback_text, debug=debug)
                    result = json.loads(repaired_json)
                except:
                    pass
                if result is None:
                    result = extract_candidates_via_regex(fallback_text, debug=debug)
                
                return [GroundingCandidate(int(c["x"]), int(c["y"]), int(c["w"]), int(c["h"]), 
                        float(c.get("confidence", c.get("c", 0.5)))) 
                        for c in result.get("candidates", [])]
            except Exception as fallback_err:
                if debug:
                    print(f"   Fallback also failed: {fallback_err}")
        
        raise Exception(f"Proposal generation failed: {e}")


def verify_and_rank_candidates(
    screenshot_path: str,
    candidates: List[GroundingCandidate],
    api_key: str,
    debug: bool = False
) -> Optional[GroundingCandidate]:
    """
    Stage 2: Verify candidates and select the best match.
    Uses visual verification with cropped regions.
    """
    if not candidates:
        return None
    
    # If only one high-confidence candidate, return it
    if len(candidates) == 1 and candidates[0].confidence >= 0.85:
        if debug:
            print(f"\n=== Stage 2: Single high-confidence candidate ===")
            print(f"✓ Selected: {candidates[0]}")
        return candidates[0]
    
    client = genai.Client(api_key=api_key)
    screenshot = cv2.imread(screenshot_path)
    
    if debug:
        print(f"\n=== Stage 2: Verification & Ranking ===")
        print(f"Verifying {len(candidates)} candidates...")
    
    verified_candidates = []
    
    for i, candidate in enumerate(candidates, 1):
        # Crop region with padding
        pad = 20
        x1 = max(0, candidate.x - pad)
        y1 = max(0, candidate.y - pad)
        x2 = min(screenshot.shape[1], candidate.x + candidate.w + pad)
        y2 = min(screenshot.shape[0], candidate.y + candidate.h + pad)
        
        cropped = screenshot[y1:y2, x1:x2]
        
        # Convert to PIL for AI
        cropped_pil = PIL.Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        
        verification_prompt = f"""Is this the standard Windows Notepad icon? Analyze this cropped region carefully.

Criteria:
- Must be the standard Windows Notepad (paper/document icon)
- NOT Notepad++ or other text editors
- Must be a functional clickable icon

Respond with JSON only:
{{
  "is_notepad": true/false,
  "confidence": 0.0-1.0,
  "reason": "brief explanation"
}}"""
        
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[verification_prompt, cropped_pil],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=512,
                )
            )
            
            # Use repair function for truncated responses
            try:
                repaired_json = repair_truncated_json(response.text, debug=False)
                verify_result = json.loads(repaired_json)
            except:
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    verify_result = json.loads(json_match.group())
                else:
                    verify_result = json.loads(response.text)
            
            if verify_result.get("is_notepad"):
                # Combine original and verification confidence
                combined_confidence = (candidate.confidence + verify_result["confidence"]) / 2
                candidate.confidence = combined_confidence
                verified_candidates.append(candidate)
                
                if debug:
                    print(f"  ✓ Candidate {i}: VERIFIED (conf={combined_confidence:.2f}) - {verify_result.get('reason', '')}")
            else:
                if debug:
                    print(f"  ✗ Candidate {i}: REJECTED - {verify_result.get('reason', '')}")
        
        except Exception as e:
            if debug:
                print(f"  ⚠ Candidate {i}: Verification failed - {e}")
            # Keep candidate with reduced confidence
            candidate.confidence *= 0.8
            verified_candidates.append(candidate)
    
    # Select best candidate
    if verified_candidates:
        # Sort by confidence, then by area (prefer larger icons), then by desktop location
        verified_candidates.sort(
            key=lambda c: (
                c.confidence,
                1 if c.source == "desktop" else 0,
                c.area
            ),
            reverse=True
        )
        
        best = verified_candidates[0]
        if debug:
            print(f"\n✓ Best candidate selected: {best}")
        return best
    
    return None


def detect_notepad_with_ai(screenshot_path: str, debug: bool = True) -> tuple:
    """
    Two-stage visual grounding system for robust Notepad icon detection.
    
    Stage 1: Generate candidate regions (proposals) with bounding boxes
    Stage 2: Verify and rank candidates, select best match
    
    Returns: (x, y) center coordinates for clicking
    Raises: ValueError if icon not found
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    
    if debug:
        print("\n" + "="*60)
        print("TWO-STAGE VISUAL GROUNDING SYSTEM")
        print("="*60)
    
    # STAGE 1: Generate candidate proposals
    try:
        candidates = generate_proposals(screenshot_path, api_key, debug)
        
        if not candidates:
            if debug:
                print("\n❌ No candidates generated in Stage 1")
            raise ValueError("Notepad icon not detected - no proposals generated")
        
        # STAGE 2: Verify and select best candidate
        best_candidate = verify_and_rank_candidates(
            screenshot_path, 
            candidates, 
            api_key, 
            debug
        )
        
        if best_candidate is None:
            if debug:
                print("\n❌ No candidates verified in Stage 2")
            raise ValueError("Notepad icon not verified - all candidates rejected")
        
        # Return center coordinates for clicking
        x, y = best_candidate.center
        
        if debug:
            print("\n" + "="*60)
            print(f"✓ GROUNDING COMPLETE: Click at ({x}, {y})")
            print(f"  BBox: top-left=({best_candidate.x},{best_candidate.y}), size=({best_candidate.w}x{best_candidate.h})")
            print(f"  Confidence: {best_candidate.confidence:.2f}")
            print(f"  Source: {best_candidate.source}")
            
            # Save a quick debug marker on screenshot
            try:
                debug_img = cv2.imread(screenshot_path)
                if debug_img is not None:
                    # Draw crosshair at click point
                    cv2.drawMarker(debug_img, (x, y), (0, 0, 255), cv2.MARKER_CROSS, 40, 3)
                    # Draw bounding box
                    cv2.rectangle(debug_img, 
                        (best_candidate.x, best_candidate.y),
                        (best_candidate.x + best_candidate.w, best_candidate.y + best_candidate.h),
                        (0, 255, 0), 2)
                    debug_path = screenshot_path.replace('.png', '_debug_click.png')
                    cv2.imwrite(debug_path, debug_img)
                    print(f"  📸 Debug click preview saved: {debug_path}")
            except Exception:
                pass
            
            print("="*60 + "\n")
        
        return x, y
        
    except Exception as e:
        if debug:
            print(f"\n❌ Grounding failed: {e}")
        raise ValueError(f"Visual grounding failed: {e}")


def visualize_grounding(
    screenshot_path: str, 
    candidates: List[GroundingCandidate], 
    selected: Optional[GroundingCandidate],
    output_path: str = None
) -> str:
    """
    Create annotated screenshot showing grounding proposals and final selection.
    Useful for debugging and demonstration.
    
    Returns: path to saved visualization
    """
    import cv2
    import datetime
    
    screenshot = cv2.imread(screenshot_path)
    overlay = screenshot.copy()
    
    # Draw all candidates
    for i, candidate in enumerate(candidates, 1):
        color = (0, 165, 255)  # Orange for proposals
        thickness = 2
        
        # Draw bounding box
        cv2.rectangle(
            overlay,
            (candidate.x, candidate.y),
            (candidate.x + candidate.w, candidate.y + candidate.h),
            color,
            thickness
        )
        
        # Draw center point
        cx, cy = candidate.center
        cv2.circle(overlay, (cx, cy), 5, color, -1)
        
        # Draw label
        label = f"#{i} {candidate.confidence:.2f}"
        label_pos = (candidate.x, candidate.y - 10)
        cv2.putText(
            overlay, 
            label, 
            label_pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )
    
    # Highlight selected candidate
    if selected:
        color = (0, 255, 0)  # Green for selection
        thickness = 4
        
        cv2.rectangle(
            overlay,
            (selected.x, selected.y),
            (selected.x + selected.w, selected.y + selected.h),
            color,
            thickness
        )
        
        cx, cy = selected.center
        cv2.circle(overlay, (cx, cy), 8, color, -1)
        
        # Draw "SELECTED" label
        label = f"SELECTED: ({cx},{cy})"
        label_pos = (selected.x, selected.y - 30)
        cv2.putText(
            overlay, 
            label, 
            label_pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )
    
    # Blend overlay
    result = cv2.addWeighted(screenshot, 0.7, overlay, 0.3, 0)
    
    # Save visualization
    if output_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/grounding_viz_{timestamp}.png"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, result)
    
    print(f"📸 Grounding visualization saved to: {output_path}")
    return output_path
