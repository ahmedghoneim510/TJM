"""Stage 2: Verify candidates and select the best match."""

import re
import json
from typing import List, Optional

import cv2
import PIL.Image
from google import genai
from google.genai import types

from .models import GroundingCandidate
from .json_repair import repair_truncated_json


def verify_and_rank_candidates(
    screenshot_path: str,
    candidates: List[GroundingCandidate],
    api_key: str,
    debug: bool = False,
) -> Optional[GroundingCandidate]:
    """
    Stage 2: Verify candidates and select the best match.
    Uses visual verification with cropped regions.
    """
    if not candidates:
        return None

    # If only one high-confidence candidate, return it directly
    if len(candidates) == 1 and candidates[0].confidence >= 0.85:
        if debug:
            print("\n=== Stage 2: Single high-confidence candidate ===")
            print(f"✓ Selected: {candidates[0]}")
        return candidates[0]

    client = genai.Client(api_key=api_key)
    screenshot = cv2.imread(screenshot_path)

    if debug:
        print("\n=== Stage 2: Verification & Ranking ===")
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
        cropped_pil = PIL.Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))

        verification_prompt = (
            "Is this the standard Windows Notepad icon? "
            "Analyze this cropped region carefully.\n\n"
            "Criteria:\n"
            "- Must be the standard Windows Notepad (paper/document icon)\n"
            "- NOT Notepad++ or other text editors\n"
            "- Must be a functional clickable icon\n\n"
            "Respond with JSON only:\n"
            '{"is_notepad": true, "confidence": 0.9, "reason": "brief explanation"}'
        )

        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[verification_prompt, cropped_pil],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=512,
                ),
            )

            # Parse response with repair fallback
            try:
                repaired_json = repair_truncated_json(response.text, debug=False)
                verify_result = json.loads(repaired_json)
            except Exception:
                json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
                if json_match:
                    verify_result = json.loads(json_match.group())
                else:
                    verify_result = json.loads(response.text)

            if verify_result.get("is_notepad"):
                combined_confidence = (
                    candidate.confidence + verify_result["confidence"]
                ) / 2
                candidate.confidence = combined_confidence
                verified_candidates.append(candidate)

                if debug:
                    reason = verify_result.get("reason", "")
                    print(
                        f"  ✓ Candidate {i}: VERIFIED "
                        f"(conf={combined_confidence:.2f}) - {reason}"
                    )
            else:
                if debug:
                    reason = verify_result.get("reason", "")
                    print(f"  ✗ Candidate {i}: REJECTED - {reason}")

        except Exception as e:
            if debug:
                print(f"  ⚠ Candidate {i}: Verification failed - {e}")
            candidate.confidence *= 0.8
            verified_candidates.append(candidate)

    # Select best candidate
    if verified_candidates:
        verified_candidates.sort(
            key=lambda c: (
                c.confidence,
                1 if c.source == "desktop" else 0,
                c.area,
            ),
            reverse=True,
        )

        best = verified_candidates[0]
        if debug:
            print(f"\n✓ Best candidate selected: {best}")
        return best

    return None
