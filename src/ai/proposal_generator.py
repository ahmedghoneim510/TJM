import json
import os
import re
import time
from typing import List

import PIL.Image
from google.genai import types

import config
from .gemini_client import get_client
from .image_utils import compress_image
from .json_repair import extract_candidates_via_regex, repair_truncated_json
from .models import GroundingCandidate


def generate_proposals(screenshot_path: str, debug: bool = False) -> List[GroundingCandidate]:
    """Stage 1: ask Gemini for bounding-box proposals for the Notepad icon."""
    if not os.path.exists(screenshot_path):
        raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")

    img = PIL.Image.open(screenshot_path)
    original_size = img.size
    img = compress_image(img)

    if debug and img.size != original_size:
        print(f"  Image compressed: {original_size} → {img.size}")

    prompt = (
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

    response = _call_with_retry(prompt, img, config.GEMINI_PRIMARY_MODEL, debug)
    if response is None:
        return []

    try:
        return _parse_response(response.text, img.size, original_size, debug)
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            return _fallback_generate(prompt, img, debug)
        raise


def _call_with_retry(prompt: str, img, model: str, debug: bool):
    client = get_client()
    delay = 2
    for attempt in range(3):
        try:
            if debug and attempt > 0:
                print(f"  Retry attempt {attempt + 1}/3...")
            return client.models.generate_content(
                model=model,
                contents=[prompt, img],
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=2048),
            )
        except Exception as e:
            is_network = any(
                x in str(e).lower() for x in ["ssl", "connection", "timeout", "network", "socket"]
            )
            if is_network and attempt < 2:
                if debug:
                    print(f"  Network error: {e} — retrying in {delay}s")
                time.sleep(delay)
                delay *= 2
            else:
                raise
    return None


def _parse_response(
    text: str,
    img_size: tuple,
    original_size: tuple,
    debug: bool,
) -> List[GroundingCandidate]:
    if debug:
        print("\n=== Stage 1: Proposal Generation ===")
        print(f"Raw AI response:\n{text[:500]}{'...' if len(text) > 500 else ''}\n")

    result = None

    for strategy in (_try_repair, _try_regex_extract, _try_regex_fallback):
        result = strategy(text, debug)
        if result is not None:
            break

    if result is None or (not result.get("found", True) and not result.get("candidates")):
        return []

    candidates = _convert_to_candidates(result["candidates"], img_size, original_size, debug)

    if debug:
        print(f"  Generated {len(candidates)} proposals:")
        for i, c in enumerate(candidates, 1):
            print(f"    {i}. {c}")

    return candidates


def _try_repair(text: str, debug: bool) -> dict | None:
    try:
        return json.loads(repair_truncated_json(text, debug=debug))
    except Exception:
        return None


def _try_regex_extract(text: str, debug: bool) -> dict | None:
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    return None


def _try_regex_fallback(text: str, debug: bool) -> dict | None:
    if debug:
        print("  Using regex extraction fallback on broken JSON...")
    result = extract_candidates_via_regex(text, debug=debug)
    return result if result.get("candidates") else None


def _convert_to_candidates(
    raw: list,
    img_size: tuple,
    original_size: tuple,
    debug: bool,
) -> List[GroundingCandidate]:
    img_w, img_h = img_size
    scale_x = original_size[0] / img_w
    scale_y = original_size[1] / img_h
    candidates = []

    for c in raw:
        rx, ry, rw, rh = int(c["x"]), int(c["y"]), int(c["w"]), int(c["h"])

        # Gemini sometimes returns normalised 0-1000 coords even when asked for pixels
        if max(rx + rw, ry + rh) <= 1000 and img_w > 1000:
            if debug:
                print(f"  Normalised coords detected: ({rx},{ry}) → pixel space")
            rx = int(rx * img_w / 1000)
            ry = int(ry * img_h / 1000)
            rw = int(rw * img_w / 1000)
            rh = int(rh * img_h / 1000)

        candidates.append(
            GroundingCandidate(
                x=int(rx * scale_x),
                y=int(ry * scale_y),
                w=int(rw * scale_x),
                h=int(rh * scale_y),
                confidence=float(c.get("confidence", c.get("c", 0.5))),
                source=c.get("location", "ai"),
            )
        )

    return candidates


def _fallback_generate(prompt: str, img, debug: bool) -> List[GroundingCandidate]:
    if debug:
        print(f"  Falling back to {config.GEMINI_FALLBACK_MODEL}...")
    try:
        response = _call_with_retry(prompt, img, config.GEMINI_FALLBACK_MODEL, debug)
        if response is None:
            return []
        result = _try_repair(response.text, debug) or extract_candidates_via_regex(
            response.text, debug=debug
        )
        return _convert_to_candidates(result.get("candidates", []), img.size, img.size, debug)
    except Exception as e:
        if debug:
            print(f"  Fallback also failed: {e}")
        return []
