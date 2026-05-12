import json
import re
from typing import List, Optional

import cv2
import PIL.Image
from google.genai import types

import config
from .gemini_client import get_client
from .json_repair import repair_truncated_json
from .models import GroundingCandidate


def verify_and_rank_candidates(
    screenshot_path: str,
    candidates: List[GroundingCandidate],
    debug: bool = False,
) -> Optional[GroundingCandidate]:
    """Stage 2: verify each candidate with a cropped-region prompt, return the best."""
    if not candidates:
        return None

    if len(candidates) == 1 and candidates[0].confidence >= 0.85:
        if debug:
            print("\n=== Stage 2: Single high-confidence candidate — skipping verification ===")
            print(f"  Selected: {candidates[0]}")
        return candidates[0]

    client = get_client()
    screenshot = cv2.imread(screenshot_path)

    if debug:
        print(f"\n=== Stage 2: Verification & Ranking ({len(candidates)} candidates) ===")

    prompt = (
        "Is this the standard Windows Notepad icon? "
        "Analyze this cropped region carefully.\n\n"
        "Criteria:\n"
        "- Must be the standard Windows Notepad (paper/document icon)\n"
        "- NOT Notepad++ or other text editors\n"
        "- Must be a functional clickable icon\n\n"
        'Respond with JSON only:\n{"is_notepad": true, "confidence": 0.9, "reason": "brief"}'
    )

    verified: List[GroundingCandidate] = []

    for i, candidate in enumerate(candidates, 1):
        pad = 20
        x1 = max(0, candidate.x - pad)
        y1 = max(0, candidate.y - pad)
        x2 = min(screenshot.shape[1], candidate.x + candidate.w + pad)
        y2 = min(screenshot.shape[0], candidate.y + candidate.h + pad)
        cropped = PIL.Image.fromarray(cv2.cvtColor(screenshot[y1:y2, x1:x2], cv2.COLOR_BGR2RGB))

        try:
            response = client.models.generate_content(
                model=config.GEMINI_PRIMARY_MODEL,
                contents=[prompt, cropped],
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=512),
            )
            verify_result = _parse_verify_response(response.text)

            if verify_result.get("is_notepad"):
                candidate.confidence = (candidate.confidence + verify_result["confidence"]) / 2
                verified.append(candidate)
                if debug:
                    print(
                        f"  Candidate {i}: VERIFIED "
                        f"(conf={candidate.confidence:.2f}) — {verify_result.get('reason', '')}"
                    )
            else:
                if debug:
                    print(f"  Candidate {i}: REJECTED — {verify_result.get('reason', '')}")

        except Exception as e:
            if debug:
                print(f"  Candidate {i}: verification error — {e}")
            candidate.confidence *= 0.8
            verified.append(candidate)

    if not verified:
        return None

    verified.sort(
        key=lambda c: (c.confidence, 1 if c.source == "desktop" else 0, c.area),
        reverse=True,
    )

    best = verified[0]
    if debug:
        print(f"\n  Best candidate: {best}")
    return best


def _parse_verify_response(text: str) -> dict:
    try:
        return json.loads(repair_truncated_json(text))
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"is_notepad": False, "confidence": 0.0, "reason": "parse error"}
