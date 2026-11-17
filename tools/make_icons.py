"""
Draw the app's icons from the logo.

    python3 tools/make_icons.py

Writes deb/icons/secretspace-<size>.png, which the .deb installs into the
desktop's icon theme (hicolor) at every size, and sourceFiles/SecretSpace-icon.png,
which the app gives its windows. The logo is cropped to its shield (plus a
margin), so at 16-24 px the shield fills the icon instead of a few pixels
of it, and given rounded corners, like an app tile - the same icon as the
Windows app's. Each size is drawn from the full-size logo. Run it again
after the logo changes, and commit the pictures; the build only reads them.
"""

import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sourceFiles")
ICONS = os.path.join(ROOT, "deb", "icons")

#: The sizes desktops look for in hicolor (menus, docks, the app grid).
SIZES = (16, 24, 32, 48, 64, 128, 256, 512)
#: What the app's own windows get (gui.py picks from it).
WINDOW_ICON = os.path.join(SRC, "SecretSpace-icon.png")
WINDOW_SIZE = 256
MARGIN = 0.2         # room around the shield, as a share of its size
CORNER = 0.22        # corner radius, as a share of the side


def tight_logo():
    """The logo cropped to a square around its shield (the bright pixels)."""
    image = Image.open(os.path.join(SRC, "SecretSpace-logo.png")).convert("RGBA")
    left, top, right, bottom = image.convert("L").point(
        lambda v: 255 if v > 40 else 0).getbbox()
    side = round(max(right - left, bottom - top) * (1 + MARGIN))
    x = (left + right) // 2 - side // 2
    y = (top + bottom) // 2 - side // 2
    return image.crop((x, y, x + side, y + side))


def icon(logo, size):
    image = logo.resize((size, size), Image.LANCZOS)
    big = size * 4                      # the mask drawn large, then reduced: smooth
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, big - 1, big - 1),
                                           radius=round(big * CORNER), fill=255)
    image.putalpha(mask.resize((size, size), Image.LANCZOS))
    return image


def main():
    logo = tight_logo()
    os.makedirs(ICONS, exist_ok=True)
    for size in SIZES:
        icon(logo, size).save(os.path.join(ICONS, f"secretspace-{size}.png"),
                              optimize=True)
    icon(logo, WINDOW_SIZE).save(WINDOW_ICON, optimize=True)
    print("wrote", len(SIZES), "icons to", ICONS, "and", WINDOW_ICON)


if __name__ == "__main__":
    main()
