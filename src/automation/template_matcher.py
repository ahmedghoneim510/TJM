import cv2


class IconNotFoundError(Exception):
    pass


def find_icon_by_template(
    screenshot_path: str,
    template_path: str,
    threshold: float = 0.8,
) -> tuple[int, int]:
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)

    if screenshot is None:
        raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")
    if template is None:
        raise FileNotFoundError(f"Template not found: {template_path}")

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        raise IconNotFoundError(f"Icon not found (best match: {max_val:.2f}, threshold: {threshold})")

    t_h, t_w = template.shape[:2]
    center_x = max_loc[0] + t_w // 2
    center_y = max_loc[1] + t_h // 2
    return center_x, center_y
