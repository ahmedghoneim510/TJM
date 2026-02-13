"""
AI Vision Detector - Two-stage visual grounding system.

Modules:
    models              - GroundingCandidate data class
    json_repair         - JSON repair & regex extraction for truncated AI responses
    image_utils         - Image compression utilities
    proposal_generator  - Stage 1: Generate candidate proposals
    candidate_verifier  - Stage 2: Verify and rank candidates
    detector            - Main detection entry point
    visualization       - Debug visualization tools
"""

from dotenv import load_dotenv

load_dotenv()

# Public API - same exports as the old single-file module
from .models import GroundingCandidate
from .detector import detect_notepad_with_ai
from .proposal_generator import generate_proposals
from .candidate_verifier import verify_and_rank_candidates
from .visualization import visualize_grounding
from .json_repair import repair_truncated_json, extract_candidates_via_regex
from .image_utils import compress_image

__all__ = [
    "GroundingCandidate",
    "detect_notepad_with_ai",
    "generate_proposals",
    "verify_and_rank_candidates",
    "visualize_grounding",
    "repair_truncated_json",
    "extract_candidates_via_regex",
    "compress_image",
]
