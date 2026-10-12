#!/usr/bin/env python3
"""
Static site builder for grizzlyanimation.com
Reads manifest.json (page content, in original order) + videos.json (Vimeo metadata)
and writes plain HTML. No dependencies beyond the stdlib + Pillow (favicon only).

    python build.py
"""
import json, os, html, re

HERE = os.path.dirname(os.path.abspath(__file__))   # tools/
ROOT = os.path.dirname(HERE)                        # site root (output)
MAN = json.load(open(os.path.join(HERE, "manifest.json"), encoding="utf-8"))
VID = json.load(open(os.path.join(HERE, "videos.json"), encoding="utf-8"))

SITE = "https://grizzlyanimation.com"
NAME = "Zach Grzymala"
EMAIL = "zach.grzymala@gmail.com"

SOCIALS = [
    ("LinkedIn", "https://www.linkedin.com/in/zach-grzymala-823ba3193/"),
    ("Vimeo",    "https://vimeo.com/user108112785"),
    ("YouTube",  "https://www.youtube.com/channel/UC7y2UBEq95aALXcrdFbunkw"),
    ("Instagram","https://www.instagram.com/zeegrizzly/"),
    ("Facebook", "https://www.facebook.com/zach.grzymala"),
]

PAGES = [
    ("rebound.html",  "Rebound",            "Thesis short film"),
    ("reel.html",     "Animation Reel",     "Demo reel & shorts"),
    ("modeling.html", "Character Modeling", "Models, turnarounds, wireframes"),
    ("disney.html",   "Disney",             "Creative Group sculpts"),
    ("story.html",    "Story",              "Boards & animatics"),
    ("about.html",    "About",              "Bio, experience, contact"),
]

LOGLINE = ("Personality,", "frame by frame.")   # hero headline — edit freely
ALDI_ID = "orVYWvH_Q9g"   # ALDI "Feast of Football" — the aired commercial
REEL_ID = "715394863"     # 3D Animation Demo Reel
FILM_ID = "826372166"     # Rebound

def e(s): return html.escape(str(s or ""), quote=True)

def mmss(sec):
    if not sec: return ""
    sec = int(sec)
    return "%d:%02d" % (sec // 60, sec % 60)

def vsrc(vid, auto=True):
    m = VID.get(vid, {})
    if m.get("kind") == "yt":
        return "https://www.youtube-nocookie.com/embed/%s?autoplay=1&rel=0" % vid
    h = m.get("h") or ""
    q = "autoplay=1&title=0&byline=0&portrait=0&dnt=1"
    if h: q = "h=%s&%s" % (h, q)
    return "https://player.vimeo.com/video/%s?%s" % (vid, q)

def poster(vid):
    p = "assets/img/poster_w/%s.webp" % vid
    return p if os.path.exists(os.path.join(ROOT, p)) else None

def vtitle(vid):
    t = (VID.get(vid, {}).get("title") or "").strip()
    t = re.sub(r"\s*\|\s*", " — ", t)
    return t or "Untitled"

# ---------------------------------------------------------------- components

def plate(vid, sub="", square=False, title=None, eager=False):
    """Video poster button -> opens lightbox player on click."""
    m = VID.get(vid, {})
    p = poster(vid)
    t = title if title is not None else vtitle(vid)
    dur = mmss(m.get("dur"))
    img = ('<img src="%s" alt="" loading="%s"%s decoding="async">' % (p, "eager" if eager else "lazy", ' fetchpriority="high"' if eager else "")) if p else \
          '<div style="width:100%;height:100%;background:var(--panel-2)"></div>'
    return """<button class="plate%s" type="button" data-video="%s" data-cap="%s" aria-label="Play %s">
  %s
  <span class="plate__btn" aria-hidden="true"></span>
  <span class="plate__meta">
    <span><span class="plate__title">%s</span>%s</span>
    %s
  </span>
</button>""" % (
        " plate--sq" if square else "", e(vsrc(vid)), e(t), e(t), img, e(t),
        ('<span class="plate__sub">%s</span>' % e(sub)) if sub else "",
        ('<span class="plate__dur">%s</span>' % e(dur)) if dur else "")

def tile(uid, cap="", sizes="(max-width:700px) 100vw, 33vw", eager=False):
    return """<button class="tile" type="button" data-full="assets/img/lg/%s.webp" data-cap="%s" aria-label="%s">
  <img src="assets/img/md/%s.webp" srcset="assets/img/sm/%s.webp 640w, assets/img/md/%s.webp 1400w"
       sizes="%s" alt="%s" loading="%s"%s decoding="async">
  %s
</button>""" % (uid, e(cap), e(cap or "View larger"), uid, uid, uid, sizes,
                e(cap), "eager" if eager else "lazy",
                ' fetchpriority="high"' if eager else "",
                ('<span class="tile__cap">%s</span>' % e(cap)) if cap else "")

def grid(uids_caps, cols=3, sizes=None, eager=False):
    """Image grid with no lightbox group of its own."""
    sizes = sizes or "(max-width:700px) 100vw, (max-width:1100px) 50vw, 33vw"
    items = "\n".join(tile(u, c, sizes, eager) for u, c in uids_caps)
    return '<div class="mgrid mgrid--%d">\n%s\n</div>' % (cols, items)

def gallery(uids_caps, cols=3, sizes=None, eager=False):
    """Image grid that is its own lightbox group."""
    return grid(uids_caps, cols, sizes, eager).replace('class="mgrid', 'data-gallery class="mgrid', 1)

def slate(rows):
    inner = "".join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(k), e(v)) for k, v in rows)
    return '<dl class="slate">%s</dl>' % inner

def head(title, desc, rel="", og=None, page_cls=""):
    og = og or "assets/img/md/3ead9fec-206a-4bc0-bce1-e22533f26d34.webp"
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s/%s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:image" content="%s/%s">
<meta property="og:url" content="%s/%s">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#08090B">
<link rel="icon" href="assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="assets/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Barlow:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<script>document.documentElement.className+=" js";</script>
<body%s>
<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"></div>
""" % (e(title), e(desc), SITE, rel, e(NAME), e(title), e(desc), SITE, og, SITE, rel,
       (' class="%s"' % page_cls) if page_cls else "")

def navbar(current=""):
    links = ""
    for href, label, _ in PAGES:
        cur = ' aria-current="page"' if href == current else ""
        links += '<a href="%s"%s>%s</a>' % (href, cur, e(label))
    return """<header class="nav">
  <a class="nav__brand" href="index.html" aria-label="%s — home">
    <span class="nav__name">Grizzly Animation</span>
    <span class="nav__role">%s</span>
  </a>
  <nav class="nav__links" aria-label="Main">
    %s
    <a class="nav__cta" href="mailto:%s">Hire me</a>
  </nav>
  <button class="nav__burger" type="button" aria-label="Menu" aria-expanded="false">
    <span></span><span></span><span></span>
  </button>
</header>
""" % (e(NAME), e(NAME), links, EMAIL)

def contact_section():
    socials = "".join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (u, e(n)) for n, u in SOCIALS)
    return """<section class="sec sec--panel" id="contact">
  <div class="wrap contact rv">
    <p class="eyebrow" style="justify-content:center">Available for feature &amp; episodic work</p>
    <h2 class="d2">Let's make something move</h2>
    <p class="lede" style="margin:0 auto 30px;text-align:center">Open to animation and character/asset roles. Reels, tests, and full breakdowns available on request.</p>
    <a class="contact__mail" href="mailto:%s">%s</a>
    <div class="socials">%s</div>
  </div>
</section>
""" % (EMAIL, EMAIL, socials)

def lightbox():
    return """<div class="lb" role="dialog" aria-modal="true" aria-label="Media viewer" aria-hidden="true">
  <button class="lb__x" type="button" aria-label="Close">×</button>
  <button class="lb__nav lb__nav--prev" type="button" aria-label="Previous">‹</button>
  <button class="lb__nav lb__nav--next" type="button" aria-label="Next">›</button>
  <div class="lb__stage"><p class="lb__cap"></p></div>
  <div class="lb__count"></div>
</div>
"""

def prevnext(cur):
    order = [p for p in PAGES if p[0] != "about.html"]
    idx = next((i for i, p in enumerate(order) if p[0] == cur), None)
    if idx is None: return ""
    prev = order[idx - 1]
    nxt = order[(idx + 1) % len(order)]
    return """<nav class="pn" aria-label="More work">
  <a href="%s"><span>Previous</span><strong>%s</strong></a>
  <a href="%s"><span>Next</span><strong>%s</strong></a>
</nav>
""" % (prev[0], e(prev[1]), nxt[0], e(nxt[1]))

def foot():
    return """<footer class="foot">
  <div class="wrap foot__in">
    <span>© <span data-year></span> Grizzly Animation Studios · %s — all assets my own</span>
    <span><a href="mailto:%s">%s</a></span>
  </div>
</footer>
%s
<script src="assets/js/site.js"></script>
</body>
</html>
""" % (e(NAME), EMAIL, EMAIL, lightbox())

def write(fn, s):
    open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(s)
    print("  wrote", fn, "%.1f KB" % (len(s.encode()) / 1024))

# ---------------------------------------------------------------- data helpers

def blocks(page): return MAN[page]
def imgs(page):   return [(b["uid"], b["cap"]) for b in MAN[page] if b["t"] == "img"]
def vids(page):   return [b["id"] for b in MAN[page] if b["t"] in ("vimeo", "yt")]

REB = blocks("rebound")
REB_IMGS = [b["uid"] for b in REB if b["t"] == "img"]
ENVS = [
    ("The Stadium",     "828473681", REB_IMGS[0:4]),
    ("The Locker Room", "828469470", REB_IMGS[4:8]),
    ("The City",        "828481150", REB_IMGS[8:12]),
]
CONCEPT = REB_IMGS[12:]
PROPS = [v for v in vids("rebound")][8:]      # 14 prop turntables
TURNS = ["828854342", "828855781"]            # Malcolm Murphy, Coach Winston
PROCESS = ["828840388", "831098131", "832110624"]

MOD = blocks("modeling")
CAST = []
_names = ["Carlos", "Harvey", "Kahuna"]
_sets = ["Trolley Trouble Set", "Mining Mayhem Set", "Tipsy Tiki Set"]
_capmap = {b["cap"]: b["uid"] for b in MOD if b["t"] == "img" and b["cap"]}
for n in _names:
    trip = [_capmap.get("%s (%s)" % (n, s)) for s in ("Textured", "Shaded", "Wireframe")]
    if all(trip): CAST.append({"name": n, "imgs": ["assets/img/md/%s.webp" % u for u in trip]})
for s in _sets:
    trip = [_capmap.get("%s (%s)" % (s, k)) for k in ("Textured", "Shaded", "Wireframe")]
    if all(trip): CAST.append({"name": s.replace(" Set", ""), "imgs": ["assets/img/md/%s.webp" % u for u in trip]})

# ---------------------------------------------------------------- home

def scrubber(extra_cls=""):
    """The pipeline scrubber: Textured -> Shaded -> Wireframe across six real asset triplets."""
    cast_btns = "".join(
        '<button type="button" aria-pressed="%s">%s</button>' % ("true" if i == 0 else "false", e(c["name"]))
        for i, c in enumerate(CAST))
    return """<div class="scrub rv %s" data-scrub="%s">
      <div class="scrub__stage">
        <span class="scrub__label">Textured</span>
        <span class="scrub__hint">Drag ↔</span>
      </div>
      <div class="scrub__track">
        <input class="scrub__range" type="range" min="0" max="100" value="0" step="0.5"
               aria-label="Blend from textured through shaded to wireframe">
      </div>
      <div class="scrub__steps">
        <button type="button" aria-pressed="true">Textured</button>
        <button type="button" aria-pressed="false">Shaded</button>
        <button type="button" aria-pressed="false">Wireframe</button>
      </div>
      <div class="scrub__cast">%s</div>
    </div>""" % (extra_cls, e(json.dumps(CAST)), cast_btns)



def card(href, n, title, desc, img, alt):
    return """<a class="card rv" href="%s" data-rv="%d">
  <img src="%s" alt="%s" loading="lazy" decoding="async">
  <span class="card__body">
    <span class="card__n">%s</span>
    <h3 class="card__t">%s</h3>
    <span class="card__d">%s</span>
    <span class="card__go">Open</span>
  </span>
</a>""" % (href, n * 60, img, e(alt), e("%02d" % n), e(title), e(desc))

def build_index():
    hero_poster = poster(FILM_ID) or "assets/img/md/%s.webp" % REB_IMGS[0]
    bg = "https://player.vimeo.com/video/%s?h=f33d212a34&background=1&autoplay=1&loop=1&muted=1&dnt=1" % FILM_ID

    cast_json = e(json.dumps(CAST))
    cast_btns = "".join(
        '<button type="button" aria-pressed="%s">%s</button>' % ("true" if i == 0 else "false", e(c["name"]))
        for i, c in enumerate(CAST))

    cards = "\n".join([
        card("reel.html", 1, "Animation Reel",
             "Two minutes of character performance, plus the eight shorts it was cut from.",
             "assets/img/poster_w/%s.webp" % REEL_ID, "Demo reel"),
        card("modeling.html", 2, "Character Modeling",
             "Three characters and three environments, from blockout to final texture.",
             "assets/img/sm/73c914d3-f60a-4b06-9c69-d3ce7292e426.webp", "Carlos the bellhop, textured"),
        card("disney.html", 3, "Disney Creative Group",
             "Holiday ornament sculpts of Mickey, Pluto, and Goofy from my internship.",
             "assets/img/sm/7a94ecea-9252-4c92-8c13-789b708883c3.webp", "Disney ornament sculpt"),
        card("story.html", 4, "Story Development",
             "Boards for a national ALDI spot and five original animatics.",
             "assets/img/sm/586aac3e-7e1c-46fa-b6e0-3ac0d313da90.webp", "Storyboard panel"),
    ])

    s = head("Grizzly Animation Studios — " + NAME + ", 3D Animator",
             "3D character animator and modeler. Ringling BFA, Walt Disney Creative Group alum, "
             "Animator at Aristocrat Gaming. Reel, short films, character models and story work.",
             rel="", og="assets/img/poster_w/%s.webp" % FILM_ID)
    s += navbar("")
    s += """<main id="main">

<section class="hero">
  <div class="hero__bg" data-hero-video="%s">
    <img src="%s" alt="" fetchpriority="high" decoding="async">
  </div>
  <div class="hero__vp" aria-hidden="true"></div>
  <div class="wrap hero__inner">
    <h1 class="lockup">
      <span class="lockup__line d1">%s<br>%s</span>
      <span class="lockup__rule"></span>
      <span class="lockup__name">Zach Grzymala</span>
    </h1>
    <p class="hero__tag">Animator · Artist · Storyteller</p>
    <div class="hero__actions">
      <button class="btn btn--primary" type="button" data-video="%s" data-cap="3D Animation Demo Reel">
        <span class="btn__play" aria-hidden="true"></span> Watch the reel
      </button>
      <a class="btn" href="#work">See the work</a>
    </div>
    <div class="hero__credits">
      <span><b>BFA</b> Ringling College</span>
      <span><b>Sculpt</b> Walt Disney Creative Group</span>
      <span><b>Animator</b> Aristocrat Gaming</span>
      <span><b>Boards</b> PSYOP</span>
    </div>
  </div>
  <div class="scrollcue">Scroll</div>
</section>

<section class="sec sec--panel">
  <div class="wrap">
    <div class="sec__head rv">
      <p class="eyebrow">Thesis film · Ringling College</p>
      <div class="feature">
        <div class="feature__media">%s</div>
        <div class="feature__body">
          <h2 class="d2">Rebound</h2>
          <p class="feature__logline">A 1980s-stylized basketball story, written and directed as my senior thesis. Two characters, three environments, fourteen hero props — every frame modeled, rigged, animated, lit, and composited by me.</p>
          %s
          <div class="feature__actions">
            <button class="btn btn--primary" type="button" data-video="%s" data-cap="Rebound — Animated Short Film">
              <span class="btn__play" aria-hidden="true"></span> Watch the film
            </button>
            <a class="btn" href="rebound.html">Full breakdown</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head rv">
      <p class="eyebrow">How a character gets built</p>
      <h2 class="d2">Every character, three ways</h2>
      <p class="lede">Texture, shading, topology. Drag across the frame to strip a finished character back to its wireframe — the same way it gets reviewed in a modeling dailies session.</p>
    </div>
    <div class="scrub rv" data-scrub="%s">
      <div class="scrub__stage">
        <span class="scrub__label">Textured</span>
        <span class="scrub__hint">Drag ↔</span>
      </div>
      <div class="scrub__track">
        <input class="scrub__range" type="range" min="0" max="100" value="0" step="0.5"
               aria-label="Blend from textured through shaded to wireframe">
      </div>
      <div class="scrub__steps">
        <button type="button" aria-pressed="true">Textured</button>
        <button type="button" aria-pressed="false">Shaded</button>
        <button type="button" aria-pressed="false">Wireframe</button>
      </div>
      <div class="scrub__cast">%s</div>
    </div>
  </div>
</section>

<section class="sec sec--panel" id="work">
  <div class="wrap">
    <div class="sec__head rv">
      <p class="eyebrow">Selected work</p>
      <h2 class="d2">The rest of the reel</h2>
    </div>
    <div class="cards">
%s
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap about">
    <div class="about__photo rv">
      <img src="assets/img/md/554390e5-d325-472e-96b4-87e18f8fe7d5.webp" alt="Zach Grzymala" loading="lazy" decoding="async">
    </div>
    <div class="about__body rv" data-rv="90">
      <p class="eyebrow">Who's behind it</p>
      <h2 class="d2" style="margin-bottom:20px">Hi, I'm Zach</h2>
      <p>It started with WALL·E — a small robot with no dialogue carrying a whole film on personality alone. That settled the argument for me in about ninety minutes.</p>
      <p>I earned my BFA in Computer Animation at Ringling College and learned every station of the pipeline: modeling, texturing, rigging, animation, lighting, comp. Since 2023 I've been an Animator at Aristocrat Gaming, building original character content end to end. Along the way I sculpted holiday merchandise characters for the Walt Disney Creative Group and boarded a national TV spot at PSYOP.</p>
      <p>What I care about is weight and intention — the pause before a character commits, the beat after they fail.</p>
      <a class="btn" href="about.html" style="margin-top:8px">Full background &amp; resume</a>
    </div>
  </div>
</section>

</main>
""" % (bg, hero_poster, e(LOGLINE[0]), e(LOGLINE[1]), e(vsrc(REEL_ID)),
       plate(FILM_ID, "Written & directed by Zach Grzymala"),
       slate([("Role", "Director / Animator"), ("Assets", "100% original"),
              ("Tools", "Maya · ZBrush · Substance"), ("Runtime", mmss(VID.get(FILM_ID, {}).get("dur")))]),
       e(vsrc(FILM_ID)), cast_json, cast_btns, cards)
    s += contact_section()
    s += foot()
    write("index.html", s)

# ---------------------------------------------------------------- interior pages

def phero(title, kicker, lede, media, aside="", back="index.html", cls=""):
    """Split hero: primary media on the left, identity + specs on the right.
    Puts the page's headline AND its main piece in one screen."""
    return """<section class="phero %s">
  <div class="wrap phero__grid">
    <div class="phero__media rv">%s</div>
    <div class="phero__body rv" data-rv="80">
      <a class="phero__back" href="%s">All work</a>
      <p class="eyebrow">%s</p>
      <h1 class="d2">%s</h1>
      <p class="lede">%s</p>
      %s
    </div>
  </div>
</section>
""" % (cls, media, back, e(kicker), e(title), lede, aside)


def secnav(items, count=""):
    """Sticky in-page jump bar. items = [(anchor_id, label), ...]"""
    links = "".join('<a href="#%s">%s</a>' % (i, e(l)) for i, l in items)
    tail = ('<span class="secnav__count">%s</span>' % e(count)) if count else ""
    return """<nav class="secnav" aria-label="Sections">
  <div class="secnav__in">%s%s</div>
</nav>
""" % (links, tail)


def subhead(t, note="", sid=None):
    idattr = (' id="%s" class="subhead jump rv"' % sid) if sid else ' class="subhead rv"'
    return '<h2%s>%s%s</h2>' % (idattr, t, ('<span>%s</span>' % note) if note else "")


def plates(ids, cols=3, square=False, subs=None):
    subs = subs or {}
    items = "\n".join(plate(v, subs.get(v, ""), square=square) for v in ids)
    return '<div class="mgrid mgrid--%d">\n%s\n</div>' % (cols, items)


def build_rebound():
    s = head("Rebound - " + NAME,
             "Rebound: a 1980s-stylized animated short film written, directed, modeled, animated, lit and composited by Zach Grzymala at Ringling College.",
             rel="rebound.html", og="assets/img/poster_w/%s.webp" % FILM_ID, page_cls="has-secnav")
    s += navbar("rebound.html")
    s += '<main id="main">'
    s += phero("Rebound", "Thesis film · Ringling College · 2023",
               "A 1980s-stylized basketball story built end to end — two characters, three "
               "environments, fourteen hero props. Every asset is my own.",
               plate(FILM_ID, "Written & directed by Zach Grzymala", eager=True),
               slate([("Role", "Director / Animator"),
                      ("Runtime", mmss(VID.get(FILM_ID, {}).get("dur"))),
                      ("Assets", "100% original"),
                      ("Tools", "Maya · ZBrush · Arnold")]))
    s += secnav([("s-char", "Characters"), ("s-env", "Environments"), ("s-concept", "Concept art"),
                 ("s-props", "Props"), ("s-process", "Process")],
                "%d pieces" % (len(TURNS) + len(ENVS) + len(CONCEPT) + len(PROPS) + len(PROCESS)))
    s += '<section class="sec"><div class="wrap">'

    s += subhead("Character designs", "2 turnarounds", "s-char")
    s += '<div class="rv">%s</div>' % plates(TURNS, cols=2)

    s += subhead("Environment designs", "3 sets", "s-env")
    for name, vid, uids in ENVS:
        s += '<div class="rv" style="margin-bottom:22px">'
        s += '<div class="mgrid mgrid--2" style="align-items:start">%s%s</div>' % (
            plate(vid, name),
            '<div data-gallery>%s</div>' % grid([(u, name + " — design") for u in uids], 2,
                                                "(max-width:700px) 50vw, 25vw"))
        s += '</div>'

    s += subhead("Concept art", "%d boards" % len(CONCEPT), "s-concept")
    s += '<div class="rv">%s</div>' % gallery([(u, "Rebound — concept art") for u in CONCEPT], cols=4)

    s += subhead("Prop designs", "%d turntables · 1980s stylized" % len(PROPS), "s-props")
    s += '<div class="rv">%s</div>' % plates(PROPS, cols=4, square=True)

    s += subhead("Story &amp; process", "3 pieces", "s-process")
    s += '<div class="rv">%s</div>' % plates(PROCESS, cols=3)
    s += '<p class="note">© 2023 Zach Grzymala — responsible for all assets</p>'
    s += '</div></section></main>'
    s += prevnext("rebound.html")
    s += contact_section() + foot()
    write("rebound.html", s)


def build_reel():
    ids = vids("reel")
    main, shorts = ids[0], ids[1:]
    s = head("Animation Reel - " + NAME,
             "3D animation demo reel by Zach Grzymala, plus the original animated shorts and character performance tests it was cut from.",
             rel="reel.html", og="assets/img/poster_w/%s.webp" % REEL_ID)
    s += navbar("reel.html")
    s += '<main id="main">'
    s += phero("Animation Reel", "Character performance",
               "Two minutes of character animation, and the eight original shorts and "
               "performance tests it was cut from.",
               plate(main, "Demo reel", eager=True),
               slate([("Runtime", mmss(VID.get(main, {}).get("dur"))),
                      ("Pieces", "%d shorts" % len(shorts)),
                      ("Assets", "100% original"),
                      ("Tools", "Maya · Arnold · ZBrush")]))
    s += '<section class="sec"><div class="wrap">'
    s += subhead("The shorts", "%d pieces" % len(shorts), "s-shorts")
    s += '<div class="rv">%s</div>' % plates(shorts, cols=3)
    s += '<p class="note">Autodesk Maya / Arnold / ZBrush / Substance Painter / Photoshop / Nuke / Premiere Pro — responsible for all assets</p>'
    s += '</div></section></main>'
    s += prevnext("reel.html")
    s += contact_section() + foot()
    write("reel.html", s)


def build_modeling():
    groups = [
        ("Carlos", "the Hotel Lobby Bellhop", "660767360", "e86988fa-3ce2-4d7a-8ed9-7c1c71b9f412", "Carlos", "Trolley Trouble Set", "s-carlos"),
        ("Harvey", "the Gold Mine Prospector", "660478038", "222f9048-e511-4808-9a47-790311a122f2", "Harvey", "Mining Mayhem Set", "s-harvey"),
        ("Kahuna", "the Tipsy Tiki Cup", "660767173", "7243a867-8718-4646-80eb-a05136fae0b8", "Kahuna", "Tipsy Tiki Set", "s-kahuna"),
    ]
    s = head("Character Modeling - " + NAME,
             "Character models, turnarounds and wireframes by Zach Grzymala: Carlos, Harvey and Kahuna, plus three fully dressed environment sets.",
             rel="modeling.html", og="assets/img/md/73c914d3-f60a-4b06-9c69-d3ce7292e426.webp",
             page_cls="has-secnav")
    s += navbar("modeling.html")
    s += '<main id="main">'
    s += phero("Character Modeling", "Models · turnarounds · wireframes",
               "Three characters and the sets they live in, each shown textured, shaded, and in wireframe.",
               scrubber(),
               slate([("Characters", "3"), ("Sets", "3"), ("Renders", "21"),
                      ("Tools", "Maya · ZBrush · Substance")]))
    s += secnav([(g[6], g[0]) for g in groups], "3 characters · 21 renders")
    s += '<section class="sec"><div class="wrap">'
    for nm, tag, vid, hero, ckey, skey, sid in groups:
        s += subhead(nm, tag, sid)
        trip_c = [(_capmap[k2], k2) for k2 in ["%s (%s)" % (ckey, k) for k in ("Textured", "Shaded", "Wireframe")] if k2 in _capmap]
        trip_s = [(_capmap[k2], k2) for k2 in ["%s (%s)" % (skey, k) for k in ("Textured", "Shaded", "Wireframe")] if k2 in _capmap]
        # showcase video beside the beauty render, then both triplets
        rows = "".join([
            '<div class="mgrid mgrid--2" style="align-items:start">%s%s</div>' % (
                plate(vid, nm + " — model showcase"),
                grid([(hero, nm + " — beauty render")], 2, "(max-width:700px) 100vw, 50vw")),
            '<div style="margin-top:12px">%s</div>' % grid(trip_c, 3),
            '<div style="margin-top:12px">%s</div>' % grid(trip_s, 3),
        ])
        s += '<div class="rv" data-gallery>%s</div>' % rows
    s += '<p class="note">Autodesk Maya / ZBrush / Substance Painter / Arnold — responsible for all assets</p>'
    s += '</div></section></main>'
    s += prevnext("modeling.html")
    s += contact_section() + foot()
    write("modeling.html", s)


def build_disney():
    ic = imgs("disney")
    vid = vids("disney")[0]
    s = head("Disney Creative Group - " + NAME,
             "Holiday ornament character sculpts of Mickey, Pluto and Goofy, created by Zach Grzymala during an internship with the Walt Disney Creative Group Workshop.",
             rel="disney.html", og="assets/img/md/7a94ecea-9252-4c92-8c13-789b708883c3.webp")
    s += navbar("disney.html")
    s += '<main id="main">'
    s += phero("Disney Creative Group", "Internship · Orlando, FL · 2022–23",
               "“Bells Ringing and Lots of Singing!” — a Christmas merchandise ornament "
               "featuring Mickey, Pluto and Goofy, sculpted from Disney-supplied model sheets.",
               plate(vid, "Holiday ornament — 3D model / sculpt", eager=True),
               slate([("Role", "3D Character Artist"), ("Client", "Disney Creative Group"),
                      ("Reference", "Disney model sheets"), ("Tools", "ZBrush · Maya · Nuke")]))
    s += '<section class="sec"><div class="wrap">'
    s += subhead("The sculpt", "%d views" % len(ic), "s-sculpt")
    s += '<div class="rv">%s</div>' % gallery([(u, c or "Ornament sculpt") for u, c in ic], cols=4)
    s += '<p class="note">Model sheets provided by Disney Creative Group · sculpting and lookdev by Zach Grzymala</p>'
    s += '</div></section></main>'
    s += prevnext("disney.html")
    s += contact_section() + foot()
    write("disney.html", s)


def build_story():
    ic = imgs("story")
    vs = [v for v in vids("story") if VID.get(v, {}).get("kind") != "yt"]
    boards = [(u, "ALDI Christmas 2022 — storyboard") for u, c in ic]
    s = head("Story Development - " + NAME,
             "The ALDI Christmas 2022 Feast of Football TV spot, storyboarded by Zach Grzymala at PSYOP, "
             "with the 100+ panels behind it and five original story animatics.",
             rel="story.html", og="assets/img/md/586aac3e-7e1c-46fa-b6e0-3ac0d313da90.webp",
             page_cls="has-secnav")
    s += navbar("story.html")
    s += '<main id="main">'
    s += phero("Story Development", "Boards & animatics",
               "A national Christmas TV spot I boarded at PSYOP, and five original animatics "
               "from pitch to parallel-edit exercise.",
               plate(ALDI_ID, "ALDI Christmas 2022 — the aired spot", eager=True),
               slate([("Client", "ALDI via PSYOP"), ("My role", "Storyboards"),
                      ("Panels", "100+"), ("Animatics", "%d" % len(vs))]))
    s += secnav([("s-aldi", "ALDI spot"), ("s-animatics", "Original animatics")],
                "%d boards · %d animatics" % (len(boards), len(vs)))
    s += '<section class="sec"><div class="wrap">'
    s += subhead("ALDI Christmas 2022", "Feast of Football · PSYOP Studios", "s-aldi")
    s += ('<p class="lede rv">Contract storyboarder at PSYOP Studios, Los Angeles. Boarded 100+ panels '
          'of 3D characters over three weeks for the World Cup Christmas spot, working to director '
          'notes. <strong>Storyboards only</strong> — the finished film belongs to PSYOP and ALDI.</p>')
    # the spot itself is the page hero; this section carries the boards behind it
    s += '<div class="rv" style="margin-top:18px">%s</div>' % gallery(boards, cols=4)
    s += '<p class="note">100+ panels boarded over three weeks · %d shown</p>' % len(boards)
    s += subhead("Original animatics", "%d pieces" % len(vs), "s-animatics")
    s += '<div class="rv">%s</div>' % plates(vs, cols=3)
    s += '<p class="note">Adobe Photoshop / Adobe Premiere Pro</p>'
    s += '</div></section></main>'
    s += prevnext("story.html")
    s += contact_section() + foot()
    write("story.html", s)

# ---------------------------------------------------------------- about

TIMELINE = [
    ("2023 — Present", "Animator", "Aristocrat Gaming · Las Vegas, NV",
     "3D model, texture, rig, animate and composite original slot game modules end to end. "
     "Establish visual wealth through symbol hierarchy and prop design, working alongside artists "
     "and game designers to keep a cohesive look across titles."),
    ("Nov 2022 — Feb 2023", "3D Character Artist", "Walt Disney Creative Group Workshop · Orlando, FL",
     "Translated supplied 2D illustrations of Mickey, Pluto and Goofy into appealing 3D models for "
     "holiday merchandise, sculpting in ZBrush and Maya to Disney's model sheets and notes."),
    ("Oct 2022 — Apr 2023", "CG Generalist", "MAKE Visual Studios · Minneapolis, MN",
     "Built a 15-second 3D animated commercial for Bubly Sparkling Beverages with a small team, "
     "from story ideas through character design to final assets."),
    ("Jun — Jul 2022", "Contract Storyboarder", "PSYOP Studios · Los Angeles, CA",
     "Boarded 100+ panels of 3D characters in three weeks for the ALDI Christmas 2022 World Cup TV spot, "
     "building camera compositions and revising to director notes."),
    ("Jul — Aug 2022", "3D Animation Teaching Assistant", "Ringling College of Art and Design",
     "Taught high-school students the basics of computer animation in the Ringling Precollege Program, "
     "giving critique and shepherding complete shorts inside a two-week class."),
    ("May — Aug 2021", "3D Animation Intern", "Riley Animation Studios · Tampa, FL",
     "Modeled assets to the animation supervisor's designs for studio pitches, built functional rigs for "
     "humans, creatures and props, and animated four characters for a 30-second teaser trailer."),
    ("Sep 2021 — May 2023", "Render Farm Manager", "Ringling College of Art and Design",
     "Ran the college render farm eight hours a week, triaging student render failures and queue issues."),
    ("2019 — 2023", "BFA, Computer Animation", "Ringling College of Art and Design · Sarasota, FL",
     "3.68 GPA. Dean's and Horizon's Scholarships. Student Ambassador."),
]

SKILLS = [
    ("Advanced proficiency", ["Autodesk Maya", "ZBrush", "Substance Painter", "Photoshop", "Premiere Pro", "Arnold"]),
    ("Working knowledge", ["Nuke", "After Effects", "Simplify3D", "Lightroom", "Graphic design", "Photography"]),
    ("Disciplines", ["Character animation", "Modeling", "Texturing", "Rigging", "Lighting", "Lookdev", "Storyboarding"]),
]

def build_about():
    tl = ""
    for when, role, org, note in TIMELINE:
        tl += """<div class="tl rv">
  <div class="tl__when">%s</div>
  <div>
    <h3 class="tl__role">%s</h3>
    <p class="tl__org">%s</p>
    <p class="tl__note">%s</p>
  </div>
</div>
""" % (when, role, org, note)

    sk = ""
    for h, items in SKILLS:
        sk += '<section><h3>%s</h3><ul>%s</ul></section>' % (
            h, "".join("<li>%s</li>" % e(i) for i in items))

    photo = """<div class="about__photo">
  <img src="assets/img/md/554390e5-d325-472e-96b4-87e18f8fe7d5.webp"
       srcset="assets/img/sm/554390e5-d325-472e-96b4-87e18f8fe7d5.webp 640w, assets/img/md/554390e5-d325-472e-96b4-87e18f8fe7d5.webp 1400w"
       sizes="(max-width:980px) 100vw, 46vw" alt="Zach Grzymala" loading="eager" decoding="async">
</div>"""

    actions = slate([("Based in", "Las Vegas, NV"), ("Currently", "Aristocrat Gaming"),
                     ("Education", "Ringling BFA"), ("Focus", "Character performance")]) + """
      <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:18px">
        <a class="btn btn--primary" href="mailto:%s">Get in touch</a>
        <a class="btn" href="assets/docs/zach-grzymala-resume.png" download>Resume</a>
      </div>""" % EMAIL

    s = head("About - " + NAME,
             "Zach Grzymala is a 3D animator and character artist in Las Vegas. Ringling BFA, Walt Disney "
             "Creative Group alum, currently Animator at Aristocrat Gaming.",
             rel="about.html", og="assets/img/md/554390e5-d325-472e-96b4-87e18f8fe7d5.webp",
             page_cls="has-secnav")
    s += navbar("about.html")
    s += '<main id="main">'
    s += phero("Zach Grzymala", "3D animator & character artist",
               "I like being the person who can take a character from a sketch to a lit, "
               "rendered shot without handing it off.",
               photo, actions, cls="phero--portrait")
    s += secnav([("s-story", "Story"), ("s-exp", "Experience"),
                 ("s-tools", "Toolset"), ("s-resume", "Resume")], "Ringling BFA · 3 yrs pro")

    s += """<section class="sec"><div class="wrap">
  <h2 class="subhead jump rv" id="s-story">How I got here<span>Bio</span></h2>
  <div class="prose2 rv">
    <p>It started with WALL·E. I was a kid in Bel Air, Maryland who had already cycled through
    basketball, dance and acting, and then I watched a small robot with no dialogue carry an entire
    film on personality alone. That settled the argument in about ninety minutes.</p>

    <p>I studied art and animation through high school and found my way to Ringling College of Art
    and Design, which turned into less a school than a sanctuary for the work. I graduated with a BFA
    in Computer Animation having learned every station of the pipeline — modeling, texturing,
    rigging, animation, lighting and comp — and directed my thesis short,
    <a href="rebound.html">Rebound</a>, start to finish.</p>

    <p>Since 2023 I have been an Animator at Aristocrat Gaming in Las Vegas, building original
    character content end to end for titles that ship to casino floors worldwide. Before that I
    sculpted holiday merchandise characters for the Walt Disney Creative Group, boarded a national
    TV spot at PSYOP, and built a commercial spot at MAKE Visual Studios.</p>

    <p>What I care about is weight and intention — the pause before a character commits, the
    beat after they fail. I work primarily in Maya, ZBrush and Substance Painter, and the thing I
    most want to do next is character performance on a feature crew.</p>
  </div>
</div></section>

<section class="sec sec--panel"><div class="wrap">
  <h2 class="subhead jump rv" id="s-exp">Where I have worked<span>%d roles</span></h2>
  <div class="timeline">%s</div>
</div></section>

<section class="sec"><div class="wrap">
  <h2 class="subhead jump rv" id="s-tools">What I work in<span>Toolset</span></h2>
  <div class="skills rv">%s</div>
</div></section>

<section class="sec sec--panel"><div class="wrap">
  <h2 class="subhead jump rv" id="s-resume">The one-pager<span>Click to enlarge</span></h2>
  <div class="rv" style="max-width:820px" data-gallery>%s</div>
</div></section>
</main>
""" % (len(TIMELINE), tl, sk,
       tile("c6f0054c-5b89-4128-88e0-ac348a527f59", "Zach Grzymala — resume", "(max-width:840px) 100vw, 820px"))

    s += contact_section() + foot()
    write("about.html", s)


def build_404():
    s = head("Page not found - " + NAME, "That page doesn't exist.", rel="404.html")
    s += navbar("")
    s += """<main id="main">
<section class="sec" style="padding-top:clamp(150px,22vh,240px);min-height:70svh">
  <div class="wrap">
    <p class="eyebrow">Error 404</p>
    <h1 class="d1" style="font-size:clamp(3rem,9vw,7rem)">Dropped<br>the ball</h1>
    <p class="lede" style="margin-top:22px">That page isn't here. The reel, though, definitely is.</p>
    <div style="display:flex;flex-wrap:wrap;gap:11px;margin-top:30px">
      <a class="btn btn--primary" href="index.html">Back to the start</a>
      <a class="btn" href="reel.html">Watch the reel</a>
    </div>
  </div>
</section>
</main>
"""
    s += foot()
    write("404.html", s)


def build_extras():
    # favicon from the logo mark
    try:
        from PIL import Image
        src = os.path.join(ROOT, "_masters/3ead9fec-206a-4bc0-bce1-e22533f26d34.png")
        if os.path.exists(src):
            im = Image.open(src).convert("RGB")
            w, h = im.size
            # crop the "Z" at the start of the wordmark
            box = (int(w * 0.115), int(h * 0.24), int(w * 0.115) + int(h * 0.34), int(h * 0.24) + int(h * 0.34))
            im.crop(box).resize((256, 256), Image.LANCZOS).save(os.path.join(ROOT, "assets/img/favicon.png"))
            print("  wrote assets/img/favicon.png")
    except Exception as ex:
        print("  favicon skipped:", ex)

    # downloadable resume copy
    import shutil
    rsrc = os.path.join(ROOT, "_masters/c6f0054c-5b89-4128-88e0-ac348a527f59.png")
    rdst = os.path.join(ROOT, "assets/docs/zach-grzymala-resume.png")
    os.makedirs(os.path.dirname(rdst), exist_ok=True)
    if os.path.exists(rsrc):
        shutil.copyfile(rsrc, rdst)
        print("  wrote assets/docs/zach-grzymala-resume.png")

    write("CNAME", "grizzlyanimation.com\n")
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    print("  wrote .nojekyll")
    write("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)

    urls = ["", "rebound.html", "reel.html", "modeling.html", "disney.html", "story.html", "about.html"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        sm += "  <url><loc>%s/%s</loc><priority>%s</priority></url>\n" % (SITE, u, "1.0" if u == "" else "0.8")
    sm += "</urlset>\n"
    write("sitemap.xml", sm)


if __name__ == "__main__":
    print("Building grizzlyanimation.com ...")
    build_index()
    build_rebound()
    build_reel()
    build_modeling()
    build_disney()
    build_story()
    build_about()
    build_404()
    build_extras()
    print("Done.")
