/* D4 round-4 browser-side measurement library.
 *
 * Loaded into the page with addScriptTag by tools/audit/round4/D4/card_grid.mjs.
 * Everything here runs in real Chromium against the real card element, so
 * every number is real layout: getBoundingClientRect / getComputedStyle /
 * getBBox. Nothing here reads the tests/card_rig.mjs DOM stub (whose
 * getBoundingClientRect is a constant 900x400 and has no geometry at all).
 */
(function () {
  const D4 = (window.__D4 = window.__D4 || {});

  // ---------- colour ----------
  function parseColor(s) {
    if (!s) return null;
    s = String(s).trim();
    if (s === "none" || s === "transparent") return { r: 0, g: 0, b: 0, a: 0 };
    let m = s.match(/^rgba?\(([^)]+)\)$/);
    if (m) {
      const p = m[1].split(/[,\s/]+/).filter((x) => x.length).map(Number);
      return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
    }
    m = s.match(/^#([0-9a-f]{3,8})$/i);
    if (m) {
      let h = m[1];
      if (h.length === 3) h = h.split("").map((c) => c + c).join("");
      if (h.length === 6) h += "ff";
      if (h.length !== 8) return null;
      return {
        r: parseInt(h.slice(0, 2), 16), g: parseInt(h.slice(2, 4), 16),
        b: parseInt(h.slice(4, 6), 16), a: parseInt(h.slice(6, 8), 16) / 255,
      };
    }
    return null;
  }
  const over = (fg, bg) => ({
    r: fg.r * fg.a + bg.r * (1 - fg.a),
    g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a),
    a: 1,
  });
  function lum(c) {
    const f = (v) => {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  }
  function contrast(a, b) {
    const l1 = lum(a), l2 = lum(b);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  }
  D4.contrastOf = (fg, bg) => contrast(fg, bg);

  // ---------- tree walking across shadow roots ----------
  function* walk(root) {
    const stack = [root];
    while (stack.length) {
      const n = stack.pop();
      if (!n) continue;
      if (n.nodeType === 1) yield n;
      if (n.shadowRoot) stack.push(n.shadowRoot);
      const kids = n.children ? [...n.children] : [];
      for (let i = kids.length - 1; i >= 0; i--) stack.push(kids[i]);
    }
  }
  D4.walk = walk;

  const visible = (el) => {
    const st = getComputedStyle(el);
    if (st.display === "none" || st.visibility === "hidden") return false;
    if (Number(st.opacity) === 0) return false;
    const b = el.getBoundingClientRect();
    return b.width > 0.01 && b.height > 0.01;
  };

  // Own text: text a node renders itself, not via element children.
  function ownText(el) {
    let s = "";
    for (const n of el.childNodes) if (n.nodeType === 3) s += n.nodeValue;
    return s.trim();
  }

  // ---------- background resolution ----------
  // What is ACTUALLY behind a run of text, composited the way the renderer
  // composites it: every covering layer in paint order, each at its own
  // effective alpha (fill-opacity x the opacity of itself and of every
  // ancestor group), alpha-over the HTML background underneath the svg.
  //
  // Reading `fill` alone is the trap this replaces: the card paints its lane
  // and series blocks at fill-opacity 0.07-0.35, so a raw `fill` read
  // reports a saturated series colour as the background and invents a
  // contrast failure that no pixel on screen has.
  function effAlpha(el, stopAt) {
    const st = getComputedStyle(el);
    let a = Number(st.fillOpacity === "" ? 1 : st.fillOpacity);
    if (!isFinite(a)) a = 1;
    let cur = el;
    while (cur && cur !== stopAt) {
      const o = Number(getComputedStyle(cur).opacity);
      if (isFinite(o)) a *= o;
      cur = cur.parentElement;
    }
    return a;
  }

  function htmlBgUnder(node) {
    let acc = null;
    let cur = node;
    const src = [];
    while (cur) {
      if (cur.nodeType === 1) {
        const st = getComputedStyle(cur);
        const c = parseColor(st.backgroundColor);
        if (c && c.a > 0) {
          src.push(describeShort(cur));
          acc = acc === null ? c : over(acc, c);
          if (acc.a >= 0.99 && c.a >= 0.99) return { c: acc, source: src.join("<") };
        }
      }
      cur = cur.parentElement || (cur.parentNode && cur.parentNode.host) || null;
    }
    const page = parseColor(getComputedStyle(document.body).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 };
    if (acc === null) return { c: page, source: "body" };
    return { c: over(acc, page), source: src.join("<") + "<body" };
  }
  function describeShort(el) {
    const cls = (el.getAttribute && el.getAttribute("class")) || "";
    return el.tagName.toLowerCase() + (cls ? "." + String(cls).trim().split(/\s+/)[0] : "");
  }

  /** Composited background at one client point, under `el`. */
  function bgAt(el, x, y) {
    const svgOwner = el.ownerSVGElement;
    if (!svgOwner) return htmlBgUnder(el);
    const base = htmlBgUnder(svgOwner);
    let acc = { r: base.c.r, g: base.c.g, b: base.c.b, a: 1 };
    const layers = [];
    for (const sh of svgOwner.querySelectorAll("rect,path,circle,polygon,ellipse")) {
      if (sh === el) continue;
      const st = getComputedStyle(sh);
      if (st.display === "none" || st.visibility === "hidden") continue;
      const f = parseColor(st.fill);
      if (!f || f.a === 0) continue;
      const b = sh.getBoundingClientRect();
      if (!(b.left <= x && b.right >= x && b.top <= y && b.bottom >= y)) continue;
      const a = f.a * effAlpha(sh, svgOwner);
      if (a <= 0.001) continue;
      acc = over({ r: f.r, g: f.g, b: f.b, a: Math.min(1, a) }, acc);
      layers.push(describeShort(sh) + "@" + a.toFixed(2));
    }
    return { c: acc, source: (base.source + (layers.length ? " + " + layers.join(" + ") : "")) };
  }

  /** The worst background under a text box: sampled across its width, since
   * a lane label can start over an empty lane and end over a slot block. */
  function bgBehind(el, box, fg) {
    const ys = [box.top + box.height * 0.5];
    const xs = [];
    const n = 5;
    for (let i = 0; i < n; i++) xs.push(box.left + (box.width * (i + 0.5)) / n);
    let worst = null;
    for (const x of xs) {
      for (const y of ys) {
        const b = bgAt(el, x, y);
        const fgOn = fg.a < 1 ? over(fg, b.c) : fg;
        const r = contrast(fgOn, b.c);
        if (!worst || r < worst.ratio) worst = { c: b.c, source: b.source, ratio: r, fgOn, x: Math.round(x) };
      }
    }
    return worst;
  }

  // ---------- the measurements ----------
  function describe(el) {
    const cls = (el.getAttribute && el.getAttribute("class")) || "";
    return el.tagName.toLowerCase() + (cls ? "." + String(cls).trim().split(/\s+/).slice(0, 2).join(".") : "");
  }
  D4.describe = describe;

  /** Every visible text-bearing node with its rect, colour and contrast. */
  D4.texts = function (root) {
    const out = [];
    for (const el of walk(root)) {
      const tag = el.tagName.toLowerCase();
      if (tag === "script" || tag === "style" || tag === "title") continue;
      const t = ownText(el);
      if (!t) continue;
      if (!visible(el)) continue;
      const st = getComputedStyle(el);
      const box = el.getBoundingClientRect();
      let fg;
      if (el.ownerSVGElement) fg = parseColor(st.fill) || parseColor(st.color);
      else fg = parseColor(st.color);
      if (!fg) continue;
      const fo = Number(st.fillOpacity === "" ? 1 : st.fillOpacity);
      const op = Number(st.opacity);
      const alpha = fg.a * (isFinite(fo) && el.ownerSVGElement ? fo : 1) * (isFinite(op) ? op : 1);
      const fgA = { r: fg.r, g: fg.g, b: fg.b, a: Math.min(1, alpha) };
      const w = bgBehind(el, box, fgA);
      let px = parseFloat(st.fontSize) || 0;
      const owner = el.ownerSVGElement;
      if (owner) {
        const vb = owner.viewBox && owner.viewBox.baseVal;
        const r = owner.getBoundingClientRect();
        let scale = 1;
        if (vb && vb.width > 0 && r.width > 0) scale = r.width / vb.width;
        const attr = Number(el.getAttribute("font-size"));
        if (attr) px = attr;
        px = px * scale;
      }
      const bold = Number(st.fontWeight) >= 700 || st.fontWeight === "bold";
      const large = px >= 24 || (px >= 18.66 && bold);
      const inactive = !!(el.closest && el.closest("[disabled],[aria-disabled='true']"));
      out.push({
        sel: describe(el), text: t.slice(0, 60),
        x: box.left, y: box.top, w: box.width, h: box.height,
        fontPx: px, bold, large, svg: !!owner, inactive,
        fg: [Math.round(w.fgOn.r), Math.round(w.fgOn.g), Math.round(w.fgOn.b)],
        bg: [Math.round(w.c.r), Math.round(w.c.g), Math.round(w.c.b)],
        bgSource: w.source, sampleX: w.x,
        ratio: Math.round(w.ratio * 100) / 100,
        need: large ? 3.0 : 4.5,
      });
    }
    return out;
  };

  /** Pairs of text boxes that overlap in both axes and are not nested. */
  D4.overlaps = function (texts, minPx) {
    const eps = minPx == null ? 1 : minPx;
    const out = [];
    for (let i = 0; i < texts.length; i++) {
      for (let j = i + 1; j < texts.length; j++) {
        const a = texts[i], b = texts[j];
        const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
        const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
        if (ox > eps && oy > eps) {
          out.push({
            a: a.sel, at: a.text, b: b.sel, bt: b.text,
            ox: Math.round(ox * 100) / 100, oy: Math.round(oy * 100) / 100,
          });
        }
      }
    }
    return out;
  };

  /** HTML text clipped by its own box (overflow hidden/clip and wider than it). */
  D4.clipped = function (root) {
    const out = [];
    for (const el of walk(root)) {
      if (el.ownerSVGElement || el.tagName === "svg") continue;
      if (!ownText(el)) continue;
      if (!visible(el)) continue;
      const st = getComputedStyle(el);
      const hidX = /hidden|clip/.test(st.overflowX);
      const hidY = /hidden|clip/.test(st.overflowY);
      const dx = el.scrollWidth - el.clientWidth;
      const dy = el.scrollHeight - el.clientHeight;
      if ((hidX && dx > 1) || (hidY && dy > 1)) {
        out.push({ sel: describe(el), text: ownText(el).slice(0, 50),
                   dx, dy, ellipsis: st.textOverflow });
      }
    }
    return out;
  };

  /** SVG text whose ink escapes its own svg viewport. */
  D4.svgEscapes = function (root) {
    const out = [];
    for (const el of walk(root)) {
      if (el.tagName !== "text" || !el.ownerSVGElement) continue;
      if (!ownText(el)) continue;
      if (!visible(el)) continue;
      const s = el.ownerSVGElement.getBoundingClientRect();
      const b = el.getBoundingClientRect();
      const l = s.left - b.left, r = b.right - s.right;
      const t = s.top - b.top, bo = b.bottom - s.bottom;
      const worst = Math.max(l, r, t, bo);
      if (worst > 0.5) {
        out.push({ sel: describe(el), text: ownText(el).slice(0, 40),
                   left: Math.round(l * 10) / 10, right: Math.round(r * 10) / 10,
                   top: Math.round(t * 10) / 10, bottom: Math.round(bo * 10) / 10 });
      }
    }
    return out;
  };

  const HIT_SEL = [
    "button", "a[href]", "input", "select", "textarea", "summary",
    "[role='button']", "[role='tab']", "[role='checkbox']", "[role='switch']",
    "[tabindex]", ".chip", ".setup-hit", ".dlg-tab", ".slot-hit", ".lane-hit",
  ].join(",");

  /** Every interactive target with its real on-screen size. */
  D4.targets = function (root) {
    const seen = new Set();
    const out = [];
    for (const el of walk(root)) {
      let match = false;
      try { match = el.matches && el.matches(HIT_SEL); } catch (e) { match = false; }
      if (!match) continue;
      if (seen.has(el)) continue;
      seen.add(el);
      const ti = el.getAttribute("tabindex");
      if (ti !== null && Number(ti) < 0 && !/button|input|select|a/.test(el.tagName.toLowerCase())) {
        // negative tabindex is not keyboard reachable but may still be a pointer target
      }
      if (el.disabled) continue;
      if (!visible(el)) continue;
      const b = el.getBoundingClientRect();
      out.push({
        sel: describe(el), key: el.getAttribute("data-key") || el.getAttribute("data-stat") || "",
        text: (el.textContent || "").trim().slice(0, 30),
        w: Math.round(b.width * 100) / 100, h: Math.round(b.height * 100) / 100,
        min: Math.round(Math.min(b.width, b.height) * 100) / 100,
        tabindex: ti,
      });
    }
    return out;
  };

  const FOCUS_SEL = [
    "a[href]", "button:not([disabled])", "input:not([disabled])",
    "select:not([disabled])", "textarea:not([disabled])",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");

  /** Focusables in DOM order, with tabindex and rect, for tab-order review. */
  D4.focusables = function (root) {
    const out = [];
    for (const el of walk(root)) {
      let match = false;
      try { match = el.matches && el.matches(FOCUS_SEL); } catch (e) { match = false; }
      if (!match) continue;
      if (!visible(el)) continue;
      const b = el.getBoundingClientRect();
      out.push({
        sel: describe(el), text: (el.textContent || "").trim().slice(0, 24),
        tabindex: el.getAttribute("tabindex"),
        x: Math.round(b.left), y: Math.round(b.top),
        w: Math.round(b.width), h: Math.round(b.height),
        label: el.getAttribute("aria-label") || el.getAttribute("title") || "",
        role: el.getAttribute("role") || "",
      });
    }
    return out;
  };

  /** A geometry fingerprint of every visible box, for layout-shift diffs. */
  D4.fingerprint = function (root) {
    const m = {};
    let i = 0;
    for (const el of walk(root)) {
      if (!visible(el)) continue;
      const b = el.getBoundingClientRect();
      m[describe(el) + "#" + i++] = [
        Math.round(b.left * 100) / 100, Math.round(b.top * 100) / 100,
        Math.round(b.width * 100) / 100, Math.round(b.height * 100) / 100,
      ];
    }
    return m;
  };
})();
