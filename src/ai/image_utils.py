from io import BytesIO
import PIL.Image


def compress_image(img: PIL.Image.Image, max_size: int = 1920) -> PIL.Image.Image:
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, PIL.Image.Resampling.LANCZOS)

    if img.mode != "RGB":
        img = img.convert("RGB")

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    buf.seek(0)
    return PIL.Image.open(buf)
