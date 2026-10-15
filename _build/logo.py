from PIL import Image
import numpy as np
src = Image.open("_build/logo-source.jpg").convert("RGB")
a = np.asarray(src).astype(np.float32)
# alpha from "distance to white": the darkest channel decides coverage
m = 255 - a.min(axis=2)
alpha = np.clip((m - 4) / (28 - 4), 0, 1)  # soft edge ramp
# un-blend from white where partially transparent
safe = np.maximum(alpha, 1e-3)[..., None]
rgb = np.clip((a - 255 * (1 - alpha[..., None])) / safe, 0, 255)
out = np.dstack([rgb, alpha * 255]).astype(np.uint8)
img = Image.fromarray(out, "RGBA")
img = img.crop(img.getbbox())
print("size", img.size)
w = 480
img.resize((w, round(img.height * w / img.width)), Image.LANCZOS).save("assets/img/logo.png", optimize=True)
big = 1400
img.resize((big, round(img.height * big / img.width)), Image.LANCZOS).save("_build/motif.png", optimize=True)
def square(n, pad=0.12, bg=None):
    c = Image.new("RGBA", (n, n), bg or (0, 0, 0, 0))
    s = int(n * (1 - 2 * pad))
    r = img.copy(); r.thumbnail((s, s), Image.LANCZOS)
    c.alpha_composite(r, ((n - r.width) // 2, (n - r.height) // 2))
    return c
square(32, .04).save("assets/img/favicon-32.png")
square(180, .16, (246, 244, 241, 255)).save("assets/img/apple-touch-icon.png")
square(512, .16, (246, 244, 241, 255)).save("assets/img/icon-512.png")
square(48, .04).save("favicon.ico", sizes=[(16,16),(32,32),(48,48)])
# sample colours
for name, (x, y) in {"mauve_light": (250, 520), "mauve_mid": (500, 1300), "plum_dark": (900, 1500), "teal_grey": (750, 600), "violet": (1350, 1200), "violet_dark": (1300, 1450)}.items():
    print(name, "#%02x%02x%02x" % tuple(int(v) for v in a[y, x]))
