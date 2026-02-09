
import os
import json
import re
from pathlib import Path
import PIL.Image
from google import genai
from google.genai import types

def detect_notepad_with_ai(screenshot_path: str, debug: bool = True) -> tuple:
    # المفتاح بتاعك
    api_key = "AIzaSyDKW_eUhMmu-4fkBF8JquhL7-J3a2Isnqk"
    #api_key="AIzaSyCZ7aQdm-_mzop_bUzPaN1Kib8QOm6WRL0"
    # تعريف الكلاينت مع تحديد الإصدار المستقر v1
    client = genai.Client(
        api_key=api_key,
    )
    
    if not os.path.exists(screenshot_path):
        raise FileNotFoundError(f"الصورة مش موجودة هنا: {screenshot_path}")

    img = PIL.Image.open(screenshot_path)
    
    prompt = """As a high-precision Vision AI, your task is to perform robust visual grounding on a provided Windows desktop screenshot (1920x1080).

Your objective is to locate the exact center pixel coordinates (x, y) of the clickable graphic area of the standard Windows Notepad application, ensuring the coordinates are accurate and safe for direct mouse double-click automation. The Notepad application may appear either as a desktop shortcut icon or as a Taskbar icon (pinned or running). Desktop detection must be attempted first, and Taskbar detection must be used only as a fallback.

The icon must be identified visually, independent of its position, size, theme, background, or surrounding noise.

Identification rules: Identify ONLY the standard Windows Notepad icon. The expected appearance is a paper or document-style icon with a blue or light-colored header typical of Windows 10/11. If both Notepad and Notepad++ are present, select ONLY the standard Windows Notepad and explicitly reject Notepad++ (green chameleon icon) and any third-party text editors.

Search priority: First search the desktop area for the Notepad icon. If the desktop icon is not confidently found, search the Windows Taskbar region only. Do not search the Start menu. If neither desktop nor Taskbar detection succeeds with sufficient confidence, return a failure result.

Desktop detection rules: The icon may appear anywhere on the desktop, including corners, edges, center, or arbitrary locations. Do not assume grid alignment, fixed spacing, or default desktop ordering. Ignore wallpaper patterns, illustrations, and non-interactive background elements, and focus exclusively on functional desktop shortcut icons.

Taskbar detection rules (fallback): Handle pinned and running Taskbar icons, including cases where text labels are hidden. Do not assume a fixed Taskbar position (bottom, top, left, or right). Identify the Notepad icon using visual structure and Windows UI context only.

Scaling, resolution, and themes: Handle all Windows icon sizes (Small, Medium, Large) and both Light and Dark themes. Do not rely on color alone; use icon shape, structure, and UI semantics.

Occlusion handling: If the icon is partially obscured by windows, pop-ups, or notifications, identify only the visible portion and compute the center of the remaining visible clickable area. Do not hallucinate hidden or fully covered regions.

Multiple matches and ambiguity: If multiple icons visually resemble Notepad, select the one with the highest visual confidence based on clarity, structure, and consistency with Windows UI conventions. If uncertainty exists, return the best candidate and lower the confidence score accordingly.

Coordinate validation: Ensure the returned (x, y) lies inside the icon graphic itself, not on the text label and not between multiple icons. The coordinates must represent the true clickable center suitable for automation.

Failure handling: If the Notepad icon cannot be confidently identified on both the desktop and the Taskbar due to absence, extreme occlusion, or ambiguity, set "found" to false, set "x" and "y" to null, and provide a brief failure reason in "description".

Output specification: Return ONLY a valid JSON object. Do not include markdown, explanations, or any text outside the JSON.

JSON format:
{
"found": true/false,
"x": <integer_center_x>,
"y": <integer_center_y>,
"confidence": <float_between_0_and_1>,
"description": "<desktop or taskbar location and visibility note>",
"visual_verification": "<concise description of the icon appearance>"
}

Confidence scoring guidance: 0.90–1.00 indicates a fully visible and unambiguous icon, 0.70–0.89 indicates minor ambiguity or partial occlusion, 0.50–0.69 indicates heavy occlusion or strong visual similarity, and below 0.50 indicates that returning "found": false is preferred."""

    try:
        # # هنستخدم gemini-2.0-flash لأنه الأحدث ودقيق جداً في الصور
        # response = client.models.generate_content(
        #   model='gemini-1.5-flash',
        #     contents=[prompt, img]
        # )
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",  contents=[prompt, img]
        )
        
        full_text = response.text
        if debug:
            print(f"--- Raw AI Response ---\n{full_text}\n-----------------------")

        # استخراج JSON بحرص
        json_match = re.search(r'\{.*\}', full_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(full_text)

        if not result.get("found"):
            print(f"⚠️ الموديل مش شايف نوت باد: {result.get('description')}")
            return None, None

        return int(result["x"]), int(result["y"])

        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents="what is sum of 5+5"
        )
        

    except Exception as e:
        # لو 2.0 لسه مش متاح للكي بتاعك، هينزل أوتوماتيك لـ 1.5 المستقر
        if "404" in str(e) or "not found" in str(e).lower():
            if debug: print("Trying fallback to gemini-1.5-flash...")
            response = client.models.generate_content(
                model='gemini-1.5-flash-8b',
                contents=[prompt, img]
            )
            result = json.loads(re.search(r'\{.*\}', response.text, re.DOTALL).group())
            return int(result["x"]), int(result["y"])
        
        raise Exception(f"فشل الاتصال: {e}")

