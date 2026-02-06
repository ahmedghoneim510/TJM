import cv2
import os

class IconNotFoundError(Exception):
    pass

def find_icon_by_template(screenshot_path, template_path, threshold=0.8, debug=True):
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)

    if screenshot is None:
        raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")
    if template is None:
        raise FileNotFoundError(f"Template not found: {template_path}")

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        raise IconNotFoundError(f"Icon not found. Best match: {max_val:.2f}")

    t_h, t_w = template.shape[:2]
    top_left = max_loc
    center_x = top_left[0] + t_w // 2
    center_y = top_left[1] + t_h // 2

    # if debug:
    #     cv2.rectangle(screenshot, top_left, (top_left[0]+t_w, top_left[1]+t_h), (0,0,255), 2)
    #     display_img = cv2.resize(screenshot, (0,0), fx=0.5, fy=0.5)
    #     cv2.imshow("Template Match", display_img)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()

    return (center_x, center_y)
