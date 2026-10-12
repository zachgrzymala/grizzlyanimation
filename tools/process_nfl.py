# -*- coding: utf-8 -*-
"""
Turn the raw NFL Super Grand Champions deliverables into web assets.

The source folder (assets/NFL Page) is 663 MB and holds three files over
GitHub's hard 100 MB limit, so it is gitignored. Only the derivatives this
script writes are committed.

    python tools/process_nfl.py
"""
import os, re, json, glob
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC  = os.path.join(ROOT, "assets", "NFL Page")
SIZES = {"sm": 640, "md": 1400, "lg": 1800}
PAD = 0.04          # breathing room around a trimmed character

for k in SIZES:
    os.makedirs(os.path.join(ROOT, "assets", "img", k), exist_ok=True)


def titleise(stem):
    """Ravens_RayLewis -> Ravens — Ray Lewis"""
    stem = stem.replace("_EmailSig", "").replace("_00000", "")
    parts = stem.split("_")
    out = []
    for p in parts:
        p = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", p)   # BaseGame -> Base Game
        out.append(p.strip())
    return " — ".join(x for x in out if x)


def trim_to_content(im, aspect=None):
    """Crop transparent padding, then pad back out to a uniform aspect."""
    if im.mode not in ("RGBA", "LA"):
        return im
    im = im.convert("RGBA")
    bbox = im.split()[-1].getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    mx, my = int(w * PAD), int(h * PAD)
    w2, h2 = w + mx * 2, h + my * 2
    if aspect:                      # widen or heighten to hit the target ratio
        if w2 / h2 > aspect: h2 = int(w2 / aspect)
        else:                w2 = int(h2 * aspect)
    canvas = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    canvas.paste(im, ((w2 - w) // 2, (h2 - h) // 2))
    return canvas


def emit(src, uid, caption, aspect=None, group=None):
    # resumable: skip anything already written, so a re-run costs nothing
    done = all(os.path.exists(os.path.join(ROOT, "assets", "img", k, uid + ".webp"))
               for k in SIZES)
    if done:
        return {"uid": uid, "cap": caption, "group": group, "w": 0, "h": 0, "alpha": True}
    im = Image.open(src)
    alpha = im.mode in ("RGBA", "LA")
    im = trim_to_content(im, aspect) if alpha else im.convert("RGB")
    w, h = im.size
    for k, mx in SIZES.items():
        nw = min(w, mx); nh = max(1, round(h * nw / w))
        out = os.path.join(ROOT, "assets", "img", k, uid + ".webp")
        im.resize((nw, nh), Image.LANCZOS).save(
            out, "WEBP", quality=82 if k != "sm" else 78, method=4)
    return {"uid": uid, "cap": caption, "group": group, "w": w, "h": h, "alpha": alpha}


def main():
    man = {"keyart": [], "characters": [], "cast": [], "badges": [], "pose": []}

    # key art — the G2E trade-show walls (full cast + logo), no alpha
    for f, uid, cap in [
        ("G2E_2025_BigWall.png", "nfl-keyart-wide", "NFL Super Grand Champions — G2E 2025 feature wall"),
        ("G2E_2025_MedWall.png", "nfl-keyart-med",  "NFL Super Grand Champions — G2E 2025 wall"),
    ]:
        p = os.path.join(SRC, f)
        if os.path.exists(p):
            man["keyart"].append(emit(p, uid, cap, group="keyart"))
            print("  keyart  ", uid)

    # named character poses — the strongest individual work
    for p in sorted(glob.glob(os.path.join(SRC, "JuneHeroes", "*.tif"))):
        stem = os.path.splitext(os.path.basename(p))[0]
        uid = "nfl-char-" + re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
        man["characters"].append(emit(p, uid, titleise(stem), aspect=1.0, group="characters"))
        print("  char    ", uid)

    # marketing pose
    for p in sorted(glob.glob(os.path.join(SRC, "MarketingPoses", "*.tif"))):
        stem = os.path.splitext(os.path.basename(p))[0]
        uid = "nfl-pose-" + re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
        man["pose"].append(emit(p, uid, titleise(re.sub(r"^\d+_", "", stem)), aspect=1.0, group="pose"))
        print("  pose    ", uid)

    # the full cast cutouts
    for p in sorted(glob.glob(os.path.join(SRC, "Heroes", "Hero_*.png"))):
        stem = os.path.splitext(os.path.basename(p))[0]
        num = re.search(r"Hero_(\d+)", stem)
        uid = "nfl-cast-" + (num.group(1) if num else stem.lower())
        man["cast"].append(emit(p, uid, "Character %s" % (num.group(1) if num else ""),
                                aspect=0.82, group="cast"))
        print("  cast    ", uid)

    # per-team badges
    for p in sorted(glob.glob(os.path.join(SRC, "Email Signatures", "*.png"))):
        stem = os.path.splitext(os.path.basename(p))[0]
        uid = "nfl-badge-" + re.sub(r"[^a-z0-9]+", "-", stem.replace("_EmailSig", "").lower()).strip("-")
        cap = titleise(stem)
        cap = {"ALL": "All teams", "Cabinet": "Cabinet", "Football": "Football"}.get(cap, cap)
        man["badges"].append(emit(p, uid, cap, aspect=1.0, group="badges"))
        print("  badge   ", uid)

    json.dump(man, open(os.path.join(HERE, "nfl.json"), "w"), indent=1)
    tot = sum(len(v) for v in man.values())
    print("\n%d images -> %s" % (tot, "tools/nfl.json"))
    for k, v in man.items():
        print("  %-11s %d" % (k, len(v)))


if __name__ == "__main__":
    main()
