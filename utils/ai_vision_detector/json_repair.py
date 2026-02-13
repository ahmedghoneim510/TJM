"""JSON repair utilities for handling truncated AI responses."""

import json
import re


def extract_candidates_via_regex(text: str, debug: bool = False) -> dict:
    """
    Last-resort fallback: extract candidate objects from broken/truncated JSON
    using regex to find individual {x, y, w, h} patterns.
    Works even when JSON is completely malformed.
    """
    pattern = r'"x"\s*:\s*(\d+)\s*,\s*"y"\s*:\s*(\d+)\s*,\s*"w"\s*:\s*(\d+)\s*,\s*"h"\s*:\s*(\d+)'
    matches = re.findall(pattern, text)

    if not matches:
        pattern2 = r'"x"\s*:\s*(\d+).*?"y"\s*:\s*(\d+).*?"w"\s*:\s*(\d+).*?"h"\s*:\s*(\d+)'
        matches = re.findall(pattern2, text, re.DOTALL)

    if matches:
        candidates = []
        for m in matches:
            candidates.append({
                "x": int(m[0]), "y": int(m[1]),
                "w": int(m[2]), "h": int(m[3]),
                "c": 0.85
            })

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
    # Extract JSON block from markdown code fence
    json_block_match = re.search(r'```json\s*([\s\S]*?)```', text)
    if json_block_match:
        text = json_block_match.group(1).strip()
    else:
        json_block_match = re.search(r'```json\s*([\s\S]*)', text)
        if json_block_match:
            text = json_block_match.group(1).strip()
        else:
            start = text.find('{')
            if start != -1:
                text = text[start:]

    # Remove trailing incomplete elements
    text = re.sub(r',\s*\.\.\.', '', text)
    text = re.sub(r'\.\.\.\s*$', '', text)

    # Try parsing as-is first
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # Handle unterminated strings by removing incomplete trailing lines
    lines = text.split('\n')
    for attempt in range(min(5, len(lines))):
        lines.pop()
        text_attempt = '\n'.join(lines).rstrip().rstrip(',')

        open_braces = text_attempt.count('{') - text_attempt.count('}')
        open_brackets = text_attempt.count('[') - text_attempt.count(']')

        fixed = text_attempt + ']' * open_brackets + '}' * open_braces

        try:
            json.loads(fixed)
            if debug:
                print(f"✓ JSON repaired by removing {attempt + 1} trailing line(s)")
            return fixed
        except json.JSONDecodeError:
            continue

    # Aggressive regex cleanup on original
    text_clean = text
    text_clean = re.sub(r',\s*"[^"]*$', '', text_clean)
    text_clean = re.sub(r',\s*"[^"]*"\s*:\s*"[^"]*$', '', text_clean)
    text_clean = re.sub(r',\s*"[^"]*"\s*:\s*"?[^"{}\[\],]*$', '', text_clean)
    text_clean = re.sub(r',\s*"[^"]*"\s*:\s*$', '', text_clean)
    text_clean = re.sub(r',\s*\{[^}]*$', '', text_clean)
    text_clean = re.sub(r',\s*$', '', text_clean.rstrip())

    open_braces = text_clean.count('{') - text_clean.count('}')
    open_brackets = text_clean.count('[') - text_clean.count(']')
    text_clean += ']' * open_brackets + '}' * open_braces

    try:
        json.loads(text_clean)
        if debug:
            print("✓ JSON repaired via regex cleanup")
        return text_clean
    except json.JSONDecodeError as e:
        if debug:
            print(f"⚠️ JSON repair failed: {e}")
        raise
