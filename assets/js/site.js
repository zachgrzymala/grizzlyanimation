/* Zach Grzymala — grizzlyanimation.com */
(function () {
  "use strict";
  var RM = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- nav ---------- */
  var nav = $(".nav");
  if (nav) {
    var burger = $(".nav__burger", nav);
    var last = 0;
    // Pages with a sticky section bar keep the nav pinned, so the jump bar
    // has a stable anchor instead of sliding around under it.
    var pinned = document.body.classList.contains("has-secnav");
    var setNavH = function () {
      document.documentElement.style.setProperty("--navh", nav.offsetHeight + "px");
    };
    setNavH();
    window.addEventListener("resize", setNavH);

    var onScroll = function () {
      var y = window.pageYOffset;
      nav.classList.toggle("is-stuck", y > 40);
      if (!pinned && !nav.classList.contains("is-open")) {
        nav.classList.toggle("is-hidden", y > 420 && y > last);
      }
      last = y;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    if (burger) {
      burger.addEventListener("click", function () {
        var open = nav.classList.toggle("is-open");
        burger.setAttribute("aria-expanded", open ? "true" : "false");
        document.body.classList.toggle("is-locked", open);
        if (open) nav.classList.remove("is-hidden");
      });
      $$(".nav__links a", nav).forEach(function (a) {
        a.addEventListener("click", function () {
          nav.classList.remove("is-open");
          burger.setAttribute("aria-expanded", "false");
          document.body.classList.remove("is-locked");
        });
      });
    }
  }

  /* ---------- scroll reveal ---------- */
  var rv = $$(".rv");
  var revealAll = function () { rv.forEach(function (el) { el.classList.add("is-in"); }); };
  if (rv.length) {
    // Failsafe: if the observer never revealed anything, it isn't working —
    // show everything. Guarded, because an unconditional timeout would reveal
    // the whole page after 2.5s and kill scroll reveals entirely.
    setTimeout(function () {
      if (!document.querySelector(".rv.is-in")) revealAll();
    }, 2500);
    if (RM || !("IntersectionObserver" in window)) {
      revealAll();
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var el = e.target;
          var d = parseInt(el.getAttribute("data-rv") || "0", 10);
          setTimeout(function () { el.classList.add("is-in"); }, d);
          io.unobserve(el);
        });
      }, { rootMargin: "0px 0px -9% 0px", threshold: 0.06 });
      rv.forEach(function (el) { io.observe(el); });
    }
  }

  /* ---------- hero ambient video (deferred) ---------- */
  var heroBg = $("[data-hero-video]");
  var conn = navigator.connection || {};
  if (heroBg && !RM && window.innerWidth > 760 && !conn.saveData) {
    var startHero = function () {
      if (heroBg.dataset.loaded) return;
      heroBg.dataset.loaded = "1";
      var url = heroBg.getAttribute("data-hero-video");
      var f;
      if (/\.mp4(\?|$)/i.test(url)) {
        // self-hosted loop — muted autoplay needs playsinline to start on iOS
        f = document.createElement("video");
        f.src = url;
        f.muted = true; f.defaultMuted = true;
        f.autoplay = true; f.loop = true; f.playsInline = true;
        f.setAttribute("muted", ""); f.setAttribute("playsinline", "");
        var go = f.play(); if (go && go.catch) go.catch(function () {});
      } else {
        f = document.createElement("iframe");
        f.src = url;
        f.setAttribute("frameborder", "0");
        f.allow = "autoplay; fullscreen";
      }
      f.setAttribute("title", "Ambient showreel loop");
      f.setAttribute("tabindex", "-1");
      f.setAttribute("aria-hidden", "true");
      heroBg.appendChild(f);
    };
    if ("requestIdleCallback" in window) requestIdleCallback(startHero, { timeout: 2600 });
    else setTimeout(startHero, 1500);
  }

  /* ---------- lightbox ---------- */
  var lb = $(".lb");
  if (lb) {
    var lbStage = $(".lb__stage", lb);
    var lbCap = $(".lb__cap", lb);
    var lbCount = $(".lb__count", lb);
    var prevBtn = $(".lb__nav--prev", lb);
    var nextBtn = $(".lb__nav--next", lb);
    var group = [];
    var idx = 0;
    var opener = null;

    function clearStage() {
      $$(".lb__img, .lb__frame, .lb__video", lbStage).forEach(function (n) {
        if (n.tagName === "VIDEO") { n.pause(); n.removeAttribute("src"); n.load(); }
        n.remove();
      });
    }

    function render() {
      clearStage();
      var it = group[idx];
      if (!it) return;
      var node;
      if (it.type === "video" && /\.mp4(\?|$)/i.test(it.src)) {
        // self-hosted clip — a real <video> rather than an embed
        node = document.createElement("video");
        node.className = "lb__video";
        node.src = it.src;
        node.controls = true;
        node.autoplay = true;
        node.playsInline = true;
        node.setAttribute("title", it.cap || "Video");
      } else if (it.type === "video") {
        node = document.createElement("iframe");
        node.className = "lb__frame";
        node.src = it.src;
        node.allow = "autoplay; fullscreen; picture-in-picture";
        node.setAttribute("allowfullscreen", "");
        node.setAttribute("title", it.cap || "Video");
      } else {
        node = document.createElement("img");
        node.className = "lb__img";
        node.src = it.src;
        node.alt = it.cap || "";
      }
      lbStage.insertBefore(node, lbCap);
      lbCap.textContent = it.cap || "";
      var many = group.length > 1;
      prevBtn.hidden = nextBtn.hidden = !many;
      lbCount.hidden = !many;
      if (many) lbCount.textContent = (idx + 1) + " / " + group.length;
    }

    function open(items, i, trigger) {
      group = items; idx = i; opener = trigger || null;
      lb.classList.add("is-on");
      lb.setAttribute("aria-hidden", "false");
      document.body.classList.add("is-locked");
      render();
      (group.length > 1 ? nextBtn : $(".lb__x", lb)).focus();
    }

    function close() {
      lb.classList.remove("is-on");
      lb.setAttribute("aria-hidden", "true");
      document.body.classList.remove("is-locked");
      clearStage();
      group = [];
      if (opener && opener.focus) opener.focus();
      opener = null;
    }

    function step(d) {
      if (group.length < 2) return;
      idx = (idx + d + group.length) % group.length;
      render();
    }

    $(".lb__x", lb).addEventListener("click", close);
    prevBtn.addEventListener("click", function () { step(-1); });
    nextBtn.addEventListener("click", function () { step(1); });
    lb.addEventListener("click", function (e) { if (e.target === lb || e.target === lbStage) close(); });

    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-on")) return;
      if (e.key === "Escape") close();
      else if (e.key === "ArrowRight") step(1);
      else if (e.key === "ArrowLeft") step(-1);
      else if (e.key === "Tab") {
        var f = $$("button:not([hidden])", lb);
        if (!f.length) return;
        var first = f[0], lastEl = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); lastEl.focus(); }
        else if (!e.shiftKey && document.activeElement === lastEl) { e.preventDefault(); first.focus(); }
      }
    });

    // swipe
    var sx = 0, sy = 0;
    lb.addEventListener("touchstart", function (e) { sx = e.changedTouches[0].clientX; sy = e.changedTouches[0].clientY; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      var dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
      if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy)) step(dx < 0 ? 1 : -1);
    }, { passive: true });

    /* videos */
    $$("[data-video]").forEach(function (el) {
      el.addEventListener("click", function () {
        open([{ type: "video", src: el.getAttribute("data-video"), cap: el.getAttribute("data-cap") || "" }], 0, el);
      });
    });

    /* image galleries */
    $$("[data-gallery]").forEach(function (wrap) {
      var tiles = $$("[data-full]", wrap);
      tiles.forEach(function (t, i) {
        t.addEventListener("click", function () {
          open(tiles.map(function (x) {
            return { type: "image", src: x.getAttribute("data-full"), cap: x.getAttribute("data-cap") || "" };
          }), i, t);
        });
      });
    });
  }

  /* ---------- pipeline scrubber ---------- */
  var scrub = $("[data-scrub]");
  if (scrub) {
    var CAST = JSON.parse(scrub.getAttribute("data-scrub"));
    var STATES = ["Textured", "Shaded", "Wireframe"];
    var stage = $(".scrub__stage", scrub);
    var range = $(".scrub__range", scrub);
    var label = $(".scrub__label", scrub);
    var steps = $$(".scrub__steps button", scrub);
    var castBtns = $$(".scrub__cast button", scrub);
    var cur = 0;
    var layers = [];

    function build(i) {
      cur = i;
      stage.innerHTML = "";
      layers = CAST[i].imgs.map(function (src, k) {
        var d = document.createElement("div");
        d.className = "scrub__layer";
        var im = document.createElement("img");
        im.src = src;
        im.alt = CAST[i].name + " — " + STATES[k];
        // all three eager: the crossfade must not stutter on first drag
        im.loading = "eager";
        im.decoding = "async";
        d.appendChild(im);
        stage.appendChild(d);
        return d;
      });
      stage.appendChild(label);
      var hint = $(".scrub__hint", scrub);
      if (hint) stage.appendChild(hint);
      paint(parseFloat(range.value));
      castBtns.forEach(function (b, k) { b.setAttribute("aria-pressed", k === i ? "true" : "false"); });
    }

    function paint(v) {
      // v: 0..100 across 3 states -> crossfade neighbours
      var p = (v / 100) * (STATES.length - 1);
      var lo = Math.floor(p), frac = p - lo;
      layers.forEach(function (l, k) {
        var o = 0;
        if (k === lo) o = 1 - frac;
        else if (k === lo + 1) o = frac;
        l.style.opacity = o;
      });
      var near = Math.round(p);
      label.textContent = STATES[near];
      steps.forEach(function (b, k) { b.setAttribute("aria-pressed", k === near ? "true" : "false"); });
    }

    range.addEventListener("input", function () {
      scrub.classList.add("is-touched");
      paint(parseFloat(range.value));
    });
    steps.forEach(function (b, k) {
      b.addEventListener("click", function () {
        scrub.classList.add("is-touched");
        var target = (k / (STATES.length - 1)) * 100;
        range.value = target;
        paint(target);
      });
    });
    castBtns.forEach(function (b, k) {
      b.addEventListener("click", function () { build(k); });
    });

    // drag across the stage itself
    var dragging = false;
    function fromX(clientX) {
      var r = stage.getBoundingClientRect();
      var v = Math.max(0, Math.min(100, ((clientX - r.left) / r.width) * 100));
      range.value = v; paint(v);
      scrub.classList.add("is-touched");
    }
    stage.addEventListener("pointerdown", function (e) { dragging = true; stage.setPointerCapture(e.pointerId); fromX(e.clientX); });
    stage.addEventListener("pointermove", function (e) { if (dragging) fromX(e.clientX); });
    stage.addEventListener("pointerup", function () { dragging = false; });
    stage.addEventListener("pointercancel", function () { dragging = false; });

    build(0);
  }

  /* ---------- year ---------- */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();

/* ================= interaction pass ================= */
(function () {
  "use strict";
  var RM = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var FINE = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- scroll progress ---------- */
  var bar = $(".progress");
  if (bar) {
    var tick = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      var p = h > 0 ? window.pageYOffset / h : 0;
      bar.style.transform = "scaleX(" + Math.min(1, Math.max(0, p)) + ")";
    };
    window.addEventListener("scroll", tick, { passive: true });
    window.addEventListener("resize", tick);
    tick();
  }

  /* ---------- section jump bar ---------- */
  var sn = $(".secnav");
  if (sn) {
    var snLinks = $$("a", sn);
    var targets = snLinks
      .map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); })
      .filter(Boolean);

    // click -> smooth scroll allowing for both sticky bars
    snLinks.forEach(function (a) {
      a.addEventListener("click", function (ev) {
        var t = document.getElementById(a.getAttribute("href").slice(1));
        if (!t) return;
        ev.preventDefault();
        var navH = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--navh"), 10) || 64;
        var y = t.getBoundingClientRect().top + window.pageYOffset - navH - sn.offsetHeight - 14;
        window.scrollTo({ top: y, behavior: RM ? "auto" : "smooth" });
        history.replaceState(null, "", a.getAttribute("href"));
      });
    });

    // active state follows the section currently under the bars
    var mark = function () {
      var navH = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--navh"), 10) || 64;
      var line = navH + sn.offsetHeight + 24;
      var active = 0;
      targets.forEach(function (t, i) {
        if (t.getBoundingClientRect().top <= line) active = i;
      });
      snLinks.forEach(function (a, i) { a.classList.toggle("is-active", i === active); });
    };
    window.addEventListener("scroll", mark, { passive: true });
    window.addEventListener("resize", mark);
    mark();
  }

  /* Hover feedback is pure CSS now (viewport selection brackets + wireframe
     overlays). No cursor-tracking or magnetic transforms — they read as wiggle. */

  /* ---------- keyboard: / focuses nothing destructive, g+key jumps ---------- */
  var GO = { h: "index.html", r: "reel.html", b: "rebound.html", m: "modeling.html",
             d: "disney.html", s: "story.html", a: "about.html" };
  var armed = false, armTimer;
  document.addEventListener("keydown", function (ev) {
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    var t = ev.target.tagName;
    if (t === "INPUT" || t === "TEXTAREA" || ev.target.isContentEditable) return;
    if ($(".lb.is-on")) return;
    if (ev.key === "g") {
      armed = true;
      clearTimeout(armTimer);
      armTimer = setTimeout(function () { armed = false; }, 1200);
      return;
    }
    if (armed && GO[ev.key]) {
      armed = false;
      location.href = GO[ev.key];
    }
  });
})();
