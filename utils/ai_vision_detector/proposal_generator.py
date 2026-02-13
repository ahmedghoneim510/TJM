"""Stage 1: Generate candidate regions using AI vision grounding."""

import os
import json
import re
import time
from typing import List

import PIL.Image
from google import genai
from google.genai import types

from .models import GroundingCandidate
from .image_utils import compress_image
from .json_repair import repair_truncated_json, extract_candidates_via_regex


def generate_proposals(
    screenshot_path: str, api_key: str, debug: bool = False
) -> List[GroundingCandidate]:
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
    proposal_prompt = (
        f"Look at this {img.size[0]}x{img.size[1]} pixel screenshot. "
        f"Find the Windows Notepad icon.\n\n"
        f"Return PIXEL coordinates (not normalized). "
        f"x,y = top-left corner in pixels. w,h = size in pixels.\n"
        f"For example, on a {img.size[0]}x{img.size[1]} image, "
        f"x ranges 0-{img.size[0]}, y ranges 0-{img.size[1]}.\n\n"
        f"Output ONLY one line of JSON:\n"
        f'{{"found":true,"candidates":[{{"x":100,"y":500,"w":64,"h":64,"c":0.9}}]}}\n\n'
        f"No markdown. No explanation. No extra fields."
    )

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
                ),
            )
            break  # Success

        except Exception as e:
            error_msg = str(e)
            is_network_error = any(
                x in error_msg.lower()
                for x in ["ssl", "connection", "timeout", "network", "socket"]
            )

            if is_network_error and attempt < max_retries - 1:
                if debug:
                    print(f"⚠️ Network error: {e}")
                    print(f"   Waiting {retry_delay}s before retry...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                raise

    try:
        full_text = response.text
        if debug:
            print("\n=== Stage 1: Proposal Generation ===")
            if len(full_text) > 500:
                print(f"Raw AI Response:\n{full_text[:500]}...\n")
            else:
                print(f"Raw AI Response:\n{full_text}\n")

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
                json_match = re.search(r"\{.*\}", full_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Strategy 3: Extract candidates via regex from broken JSON
        if result is None:
            if debug:
                print("🔧 Using regex extraction fallback on broken JSON...")
            result = extract_candidates_via_regex(full_text, debug=debug)
            if not result.get("candidates"):
                raise Exception("Could not extract any candidates from AI response")

        if not result.get("found", True) and not result.get("candidates"):
            if debug:
                print("⚠️ No candidates found in Stage 1")
            return []

        # Convert to GroundingCandidate objects
        candidates = _parse_candidates(result, img.size, original_size, debug)

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
            except Exception:
                pass

        # Fallback to older model for 404 errors
        if "404" in error_msg or "not found" in error_msg.lower():
            return _fallback_generate(client, proposal_prompt, img, debug)

        raise Exception(f"Proposal generation failed: {e}")


def _parse_candidates(
    result: dict,
    img_size: tuple,
    original_size: tuple,
    debug: bool = False,
) -> List[GroundingCandidate]:
    """Parse raw JSON result into GroundingCandidate objects with coordinate fixing."""
    candidates = []
    img_w, img_h = img_size

    for c in result["candidates"]:
        raw_x, raw_y = int(c["x"]), int(c["y"])
        raw_w, raw_h = int(c["w"]), int(c["h"])

        # Detect if coordinates are in normalized 0-1000 range (Gemini default)
        max_coord = max(raw_x + raw_w, raw_y + raw_h)
        likely_normalized = (
            max_coord <= 1000
            and img_w > 1000
            and (raw_x + raw_w) <= 1000
            and (raw_y + raw_h) <= 1000
        )

        if likely_normalized:
            px_x = int(raw_x * img_w / 1000)
            px_y = int(raw_y * img_h / 1000)
            px_w = int(raw_w * img_w / 1000)
            px_h = int(raw_h * img_h / 1000)
            if debug:
                print(
                    f"  📐 Normalized coords detected: ({raw_x},{raw_y}) → pixel ({px_x},{px_y})"
                )
        else:
            px_x, px_y, px_w, px_h = raw_x, raw_y, raw_w, raw_h

        # Scale coordinates back to original size if image was resized
        scale_x = original_size[0] / img_w
        scale_y = original_size[1] / img_h

        conf = c.get("confidence", c.get("c", 0.5))

        candidate = GroundingCandidate(
            x=int(px_x * scale_x),
            y=int(px_y * scale_y),
            w=int(px_w * scale_x),
            h=int(px_h * scale_y),
            confidence=float(conf),
            source=c.get("location", "ai"),
        )
        candidates.append(candidate)

    return candidates


def _fallback_generate(client, prompt, img, debug: bool = False) -> List[GroundingCandidate]:
    """Fallback to older Gemini model when primary model returns 404."""
    if debug:
        print("🔄 Falling back to gemini-1.5-flash...")
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash", contents=[prompt, img]
        )
        fallback_text = response.text
        result = None
        try:
            repaired_json = repair_truncated_json(fallback_text, debug=debug)
            result = json.loads(repaired_json)
        except Exception:
            pass
        if result is None:
            result = extract_candidates_via_regex(fallback_text, debug=debug)

        return [
            GroundingCandidate(
                int(c["x"]),
                int(c["y"]),
                int(c["w"]),
                int(c["h"]),
                float(c.get("confidence", c.get("c", 0.5))),
            )
            for c in result.get("candidates", [])
        ]
    except Exception as fallback_err:
        if debug:
            print(f"   Fallback also failed: {fallback_err}")
        return []
