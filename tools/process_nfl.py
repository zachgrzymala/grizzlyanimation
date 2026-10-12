# -*- coding: utf-8 -*-
"""
Turn the raw NFL Super Grand Champions deliverables into web assets.

assets/NFL Page/ is gitignored — it is large and holds files over GitHub's
hard 100 MB per-file limit. Only what this script writes is committed.

    python tools/process_nfl.py

Resumable: anything already written is skipped, so re-runs are cheap.
"""
import os, re, json, glob
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC  = os.path.join(ROOT, "assets", "NFL Page")
SIZES = {"sm": 640, "md": 1400, "lg": 1800}
PAD = 0.04

for k in SIZES:
    os.makedirs(os.path.join(ROOT, "assets", "img", k), exist_ok=True)


def titleise(stem):
    stem = stem.replace("_EmailSig", "").replace("_00000", "")
    out = []
    for p in stem.split("_"):
        p = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", p).strip()
        p = re.sub(r"(\D)(\d)$", r"\1", p)        # Jaguars2 -> Jaguars
        if p: out.append(p)
    return " — ".join(out)


def trim_to_content(im, aspect=None, anchor="center"):
    """Crop transparent padding, then pad back out to a uniform aspect.

    anchor="bottom" seats the figure on the bottom edge, so a standing
    character meets the frame instead of floating in the middle of it.
    """
    if im.mode not in ("RGBA", "LA"):
        return im
    im = im.convert("RGBA")
    bbox = im.split()[-1].getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    mx = int(w * PAD)
    my = 0 if anchor == "bottom" else int(h * PAD)
    w2 = w + mx * 2
    h2 = h + my * (2 if anchor != "bottom" else 0) + (int(h * PAD) if anchor == "bottom" else 0)
    if aspect:
        if w2 / h2 > aspect: h2 = int(w2 / aspect)
        else:                w2 = int(h2 * aspect)
    canvas = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    y = h2 - h if anchor == "bottom" else (h2 - h) // 2
    canvas.paste(im, ((w2 - w) // 2, y))
    return canvas


def emit(src, uid, caption, aspect=None, anchor="center"):
    if all(os.path.exists(os.path.join(ROOT, "assets", "img", k, uid + ".webp")) for k in SIZES):
        return {"uid": uid, "cap": caption}
    im = Image.open(src)
    im = trim_to_content(im, aspect, anchor) if im.mode in ("RGBA", "LA") else im.convert("RGB")
    w, h = im.size
    for k, mx in SIZES.items():
        nw = min(w, mx); nh = max(1, round(h * nw / w))
        im.resize((nw, nh), Image.LANCZOS).save(
            os.path.join(ROOT, "assets", "img", k, uid + ".webp"),
            "WEBP", quality=82 if k != "sm" else 78, method=4)
    print("   ", uid)
    return {"uid": uid, "cap": caption}


def main():
    man = {"keyart": [], "heroes": [], "badges": [], "cabinet": []}

    # G2E 2025 trade-show walls (no alpha)
    for f, uid, cap in [
        ("G2E_2025_BigWall.png", "nfl-keyart-wide", "NFL Super Grand Champions — G2E 2025 feature wall"),
        ("G2E_2025_MedWall.png", "nfl-keyart-med",  "G2E 2025 wall"),
    ]:
        p = os.path.join(SRC, f)
        if os.path.exists(p):
            man["keyart"].append(emit(p, uid, cap))

    # the 32 team heroes — one per NFL club
    for p in sorted(glob.glob(os.path.join(SRC, "Heroes", "Hero_*.png"))):
        num = re.search(r"Hero_(\d+)", os.path.basename(p))
        n = num.group(1) if num else "00"
        man["heroes"].append(emit(p, "nfl-hero-" + n, "Hero %s" % n, aspect=0.82, anchor="bottom"))

    # the physical cabinet, and the Super Grand trophy
    for f, uid, cap, key in [
        ("Cabinet_EmailSig.png", "nfl-cabinet", "The cabinet on the floor", "cabinet"),
    ]:
        p = os.path.join(SRC, f)
        if os.path.exists(p):
            man[key].append(emit(p, uid, cap, aspect=1.0))

    # per-team badges
    for p in sorted(glob.glob(os.path.join(SRC, "Email Signatures", "*.png"))):
        stem = os.path.splitext(os.path.basename(p))[0]
        uid = "nfl-badge-" + re.sub(r"[^a-z0-9]+", "-", stem.replace("_EmailSig", "").lower()).strip("-")
        man["badges"].append(emit(p, uid, titleise(stem), aspect=1.0))

    json.dump(man, open(os.path.join(HERE, "nfl.json"), "w"), indent=1)
    print("\n%d images -> tools/nfl.json" % sum(len(v) for v in man.values()))
    for k, v in man.items():
        print("  %-9s %d" % (k, len(v)))

    # drop derivatives whose source is gone (removed duplicates, retired groups)
    keep = {i["uid"] for v in man.values() for i in v}
    killed = 0
    for k in SIZES:
        for f in glob.glob(os.path.join(ROOT, "assets", "img", k, "nfl-*.webp")):
            if os.path.splitext(os.path.basename(f))[0] not in keep:
                os.remove(f); killed += 1
    if killed:
        print("\nremoved %d stale derivatives (sources deleted upstream)" % killed)


if __name__ == "__main__":
    main()
