
import cv2
import numpy as np
import os

class IconNotFoundError(Exception):
    pass

def find_icon_by_template(screenshot_path, template_path, threshold=0.8, debug=True):
    """
    Locate a desktop icon using template matching.

    :param screenshot_path: path to desktop screenshot
    :param template_path: path to icon template image
    :param threshold: matching confidence threshold (0-1)
    :param debug: if True, show image with detected box
    :return: (center_x, center_y) of detected icon
    :raises IconNotFoundError: if icon not found
    """
    # Load images
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)

    if screenshot is None:
        raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")
    if template is None:
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Template matching
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        raise IconNotFoundError(f"Icon not found. Best match: {max_val:.2f}")

    # Bounding box
    t_h, t_w = template.shape[:2]
    top_left = max_loc
    center_x = top_left[0] + t_w // 2
    center_y = top_left[1] + t_h // 2

    if debug:
        cv2.rectangle(screenshot, top_left, (top_left[0]+t_w, top_left[1]+t_h), (0,0,255), 2)
        display_img = cv2.resize(screenshot, (0,0), fx=0.5, fy=0.5)
        cv2.imshow("Template Match", display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return (center_x, center_y)
