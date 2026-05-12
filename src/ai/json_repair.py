import json
import re


def extract_candidates_via_regex(text: str, debug: bool = False) -> dict:
    pattern = r'"x"\s*:\s*(\d+)\s*,\s*"y"\s*:\s*(\d+)\s*,\s*"w"\s*:\s*(\d+)\s*,\s*"h"\s*:\s*(\d+)'
    matches = re.findall(pattern, text)

    if not matches:
        pattern2 = r'"x"\s*:\s*(\d+).*?"y"\s*:\s*(\d+).*?"w"\s*:\s*(\d+).*?"h"\s*:\s*(\d+)'
        matches = re.findall(pattern2, text, re.DOTALL)

    if matches:
        candidates = [
            {"x": int(m[0]), "y": int(m[1]), "w": int(m[2]), "h": int(m[3]), "c": 0.85}
            for m in matches
        ]
        conf_matches = re.findall(r'"(?:c|confidence)"\s*:\s*(0?\.\d+|1(?:\.0)?)', text)
        for i, conf in enumerate(conf_matches):
            if i < len(candidates):
                candidates[i]["c"] = float(conf)

        if debug:
            print(f"Regex extraction found {len(candidates)} candidates from broken JSON")

        return {"found": True, "candidates": candidates}

    return {"found": False, "candidates": []}


def repair_truncated_json(text: str, debug: bool = False) -> str:
    json_block = re.search(r"```json\s*([\s\S]*?)```", text)
    if json_block:
        text = json_block.group(1).strip()
    else:
        json_block = re.search(r"```json\s*([\s\S]*)", text)
        if json_block:
            text = json_block.group(1).strip()
        else:
            start = text.find("{")
            if start != -1:
                text = text[start:]

    text = re.sub(r",\s*\.\.\.", "", text)
    text = re.sub(r"\.\.\.\s*$", "", text)

    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    lines = text.split("\n")
    for attempt in range(min(5, len(lines))):
        lines.pop()
        candidate = "\n".join(lines).rstrip().rstrip(",")
        open_braces = candidate.count("{") - candidate.count("}")
        open_brackets = candidate.count("[") - candidate.count("]")
        fixed = candidate + "]" * open_brackets + "}" * open_braces
        try:
            json.loads(fixed)
            if debug:
                print(f"JSON repaired by removing {attempt + 1} trailing line(s)")
            return fixed
        except json.JSONDecodeError:
            continue

    text_clean = text
    text_clean = re.sub(r',\s*"[^"]*$', "", text_clean)
    text_clean = re.sub(r',\s*"[^"]*"\s*:\s*"[^"]*$', "", text_clean)
    text_clean = re.sub(r',\s*"[^"]*"\s*:\s*"?[^"{}\[\],]*$', "", text_clean)
    text_clean = re.sub(r',\s*"[^"]*"\s*:\s*$', "", text_clean)
    text_clean = re.sub(r",\s*\{[^}]*$", "", text_clean)
    text_clean = re.sub(r",\s*$", "", text_clean.rstrip())

    open_braces = text_clean.count("{") - text_clean.count("}")
    open_brackets = text_clean.count("[") - text_clean.count("]")
    text_clean += "]" * open_brackets + "}" * open_braces

    try:
        json.loads(text_clean)
        if debug:
            print("JSON repaired via regex cleanup")
        return text_clean
    except json.JSONDecodeError as e:
        if debug:
            print(f"JSON repair failed: {e}")
        raise
