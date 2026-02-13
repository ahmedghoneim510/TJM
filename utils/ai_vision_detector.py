
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
    
    # Stage 1 Prompt: Request bounding box proposals only
    proposal_prompt = f"""You are a visual grounding AI specialized in detecting UI elements.

Task: Identify ALL potential regions that could contain the standard Windows Notepad icon in this desktop screenshot (original size: {original_size[0]}x{original_size[1]}).

DETECTION RULES:
✓ INCLUDE:
  - Standard Windows Notepad icon (simple notepad/paper icon, often white/blue)
  - Desktop shortcuts with "Notepad" text label
  - Taskbar buttons (bottom bar, usually 40-50px tall)
  - Quick access icons
  - All icon sizes: 32x32, 48x48, 64x64, 96x96, 128x128 pixels

✗ EXCLUDE:
  - Notepad++ (has green/rainbow icon)
  - Other text editors
  - Background wallpaper elements
  - Blue empty space with no icons

IMPORTANT: 
- Look carefully at the ENTIRE image including desktop area and taskbar
- If you see ANY icon that looks like a notepad/paper/document, include it
- Only return coordinates that actually contain an icon, NOT empty blue areas
- Return bounding boxes large enough to capture the full icon + text label

Output JSON format (adjust x,y,w,h if image was resized to {img.size[0]}x{img.size[1]}):
{{
  "found": true/false,
  "candidates": [
    {{"x": 100, "y": 200, "w": 80, "h": 96, "confidence": 0.92, "location": "desktop"}},
    {{"x": 850, "y": 1030, "w": 48, "h": 48, "confidence": 0.78, "location": "taskbar"}}
  ]
}}

Return 1-5 candidates ranked by confidence. If NO Notepad icon visible, return empty candidates array."""

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

        # Extract JSON
        json_match = re.search(r'\{.*\}', full_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(full_text)

        if not result.get("found") or not result.get("candidates"):
            if debug:
                print("⚠️ No candidates found in Stage 1")
                print("💡 Possible reasons:")
                print("   - Notepad icon not visible on desktop or taskbar")
                print("   - Icon too small or obscured")
                print("   - Try adding Notepad shortcut to desktop")
            return []

        # Convert to GroundingCandidate objects
        candidates = []
        for c in result["candidates"]:
            # Scale coordinates back to original size if image was resized
            scale_x = original_size[0] / img.size[0]
            scale_y = original_size[1] / img.size[1]
            
            candidate = GroundingCandidate(
                x=int(c["x"] * scale_x),
                y=int(c["y"] * scale_y),
                w=int(c["w"] * scale_x),
                h=int(c["h"] * scale_y),
                confidence=float(c["confidence"]),
                source=c.get("location", "unknown")
            )
            candidates.append(candidate)
        
        if debug:
            print(f"✓ Generated {len(candidates)} proposals:")
            for i, c in enumerate(candidates, 1):
                print(f"  {i}. {c}")
        
        return candidates

    except json.JSONDecodeError as e:
        if debug:
            print(f"❌ JSON parsing error: {e}")
            print(f"   Response text: {full_text[:200]}...")
        raise Exception(f"Failed to parse AI response: {e}")
    except Exception as e:
        # Fallback to older model for 404 errors
        if "404" in str(e) or "not found" in str(e).lower():
            if debug:
                print("🔄 Falling back to gemini-1.5-flash...")
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=[proposal_prompt, img]
            )
            result = json.loads(re.search(r'\{.*\}', response.text, re.DOTALL).group())
            return [GroundingCandidate(int(c["x"]), int(c["y"]), int(c["w"]), int(c["h"]), float(c["confidence"])) 
                    for c in result.get("candidates", [])]
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
    api_key = "AIzaSyDKW_eUhMmu-4fkBF8JquhL7-J3a2Isnqk"
    
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
            print(f"  Confidence: {best_candidate.confidence:.2f}")
            print(f"  Source: {best_candidate.source}")
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
