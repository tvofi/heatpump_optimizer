// Browser-side instrument for tools/audit/round9/D4/s1/sweep.mjs (not run on
// its own). Injected into the page after the card; defines window.__hpo with
// the drivers that reproduce tests/card_drift.mjs's STATES against the REAL
// DOM, and the geometry/contrast/target/keyboard measurements.
//
// Every measurement reads the rendered shadow root of the production element
// `heatpump-optimizer-card` (custom_components/heatpump_optimizer/www/
// heatpump-optimizer-card.js:HeatpumpOptimizerCard) through
// getBoundingClientRect / getComputedStyle / Range rects.
(() => {
  const H = {};
  window.__hpo = H;
  const HOUR = 3600000;

  // ---- colour ----------------------------------------------------------
  const parseColor = (s) => {
    if (!s || s === "none" || s === "transparent") return null;
    let m = s.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+%?))?\s*\)$/);
    if (m) {
      let a = m[4] === undefined ? 1 : (m[4].endsWith("%") ? parseFloat(m[4]) / 100 : +m[4]);
      return [+m[1], +m[2], +m[3], a];
    }
    m = s.match(/^color\(srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\)$/);
    if (m) return [m[1] * 255, m[2] * 255, m[3] * 255, m[4] === undefined ? 1 : +m[4]];
    if (s.startsWith("#")) {
      let h = s.slice(1);
      if (h.length === 3) h = h.split("").map((c) => c + c).join("");
      const n = parseInt(h.slice(0, 6), 16);
      return [(n >> 16) & 255, (n >> 8) & 255, n & 255, h.length === 8 ? parseInt(h.slice(6), 16) / 255 : 1];
    }
    return undefined; // url(), currentcolor oddities: unknown
  };
  const over = (top, a, bottom) => [0, 1, 2].map((i) => top[i] * a + bottom[i] * (1 - a));
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
  };
  const ratio = (a, b) => {
    const la = lum(a), lb = lum(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  };
  H.ratio = ratio;

  // ---- tree walking -----------------------------------------------------
  const parentOf = (n) => n.parentElement || (n.getRootNode && n.getRootNode().host) || null;
  const effOpacity = (el) => {
    let o = 1;
    for (let n = el; n; n = parentOf(n)) {
      const cs = getComputedStyle(n);
      o *= parseFloat(cs.opacity || "1");
      if (n instanceof SVGElement) {
        const ao = n.getAttribute && n.getAttribute("opacity");
        // computed opacity already covers the attribute in Chromium
      }
    }
    return o;
  };
  const visible = (el) => {
    if (!el.getClientRects || !el.getClientRects().length) return false;
    const cs = getComputedStyle(el);
    if (cs.visibility === "hidden" || cs.visibility === "collapse" || cs.display === "none") return false;
    if (el.closest && el.closest("defs, pattern, clipPath, mask, marker, symbol, title")) return false;
    return effOpacity(el) > 0.02;
  };
  const desc = (el) => {
    const cls = (el.getAttribute && el.getAttribute("class")) || "";
    let s = el.tagName.toLowerCase() + (cls ? "." + cls.trim().split(/\s+/).join(".") : "");
    const k = el.getAttribute && (el.getAttribute("data-key") || el.getAttribute("data-page") || el.getAttribute("data-stat"));
    if (k) s += `[${k}]`;
    return s.slice(0, 80);
  };
  const path = (el) => {
    const out = [];
    for (let n = el; n && out.length < 4; n = parentOf(n)) {
      if (n.tagName === "HEATPUMP-OPTIMIZER-CARD") break;
      out.push(desc(n));
    }
    return out.reverse().join(" > ");
  };
  const card = () => document.querySelector("heatpump-optimizer-card");
  const root = () => card().shadowRoot;
  const modalDialog = () => {
    const d = root().querySelector("dialog[open]");
    return d && d.matches(":modal") ? d : null;
  };
  const scope = () => modalDialog() || root();
  const allEls = () => [...scope().querySelectorAll("*")];

  // ---- text runs ----------------------------------------------------------
  const directText = (el) => [...el.childNodes].filter((x) => x.nodeType === 3)
    .map((x) => x.textContent).join("").replace(/\s+/g, " ").trim();
  const textRuns = () => {
    const runs = [];
    for (const el of allEls()) {
      const isSvg = el instanceof SVGElement;
      if (isSvg && el.tagName.toLowerCase() !== "text") continue;
      if (!isSvg && ["STYLE", "SCRIPT", "TITLE", "OPTION"].includes(el.tagName)) continue;
      if (!visible(el)) continue;
      let txt, rect;
      if (isSvg) {
        txt = (el.textContent || "").replace(/\s+/g, " ").trim();
        if (!txt) continue;
        rect = el.getBoundingClientRect();
      } else {
        txt = directText(el);
        if (!txt) continue;
        const rg = document.createRange();
        rg.selectNodeContents(el);
        // Only the direct text nodes: a child element's run is its own.
        const rs = [];
        for (const tn of el.childNodes) {
          if (tn.nodeType !== 3 || !tn.textContent.trim()) continue;
          const r2 = document.createRange();
          r2.selectNodeContents(tn);
          rs.push(...r2.getClientRects());
        }
        if (!rs.length) continue;
        const l = Math.min(...rs.map((r) => r.left)), t = Math.min(...rs.map((r) => r.top));
        const r = Math.max(...rs.map((r) => r.right)), b = Math.max(...rs.map((r) => r.bottom));
        rect = { left: l, top: t, right: r, bottom: b, width: r - l, height: b - t };
      }
      if (rect.width < 0.5 || rect.height < 0.5) continue;
      runs.push({ el, txt, rect, isSvg });
    }
    return runs;
  };

  // ---- clipping -------------------------------------------------------
  const clipOf = (el, axis) => {
    for (let n = parentOf(el); n; n = parentOf(n)) {
      if (n === document.documentElement) break;
      const cs = getComputedStyle(n);
      const o = axis === "x" ? cs.overflowX : cs.overflowY;
      if (o === "hidden" || o === "clip") return { n, rect: n.getBoundingClientRect(), extraA: 0, extraB: 0 };
      if (o === "auto" || o === "scroll") {
        const r = n.getBoundingClientRect();
        if (axis === "x") return { n, rect: r, extraA: n.scrollLeft, extraB: n.scrollWidth - n.clientWidth - n.scrollLeft };
        return { n, rect: r, extraA: n.scrollTop, extraB: n.scrollHeight - n.clientHeight - n.scrollTop };
      }
    }
    return null;
  };
  const unreachable = (run) => {
    let worst = 0, side = "", clip = "";
    for (const axis of ["x", "y"]) {
      const c = clipOf(run.el, axis);
      if (!c) continue;
      const [a0, a1, c0, c1] = axis === "x"
        ? [run.rect.left, run.rect.right, c.rect.left, c.rect.right]
        : [run.rect.top, run.rect.bottom, c.rect.top, c.rect.bottom];
      const lo = (c0 - c.extraA) - a0;
      const hi = a1 - (c1 + c.extraB);
      if (lo > worst) { worst = lo; side = axis === "x" ? "left" : "top"; clip = desc(c.n); }
      if (hi > worst) { worst = hi; side = axis === "x" ? "right" : "bottom"; clip = desc(c.n); }
    }
    return { px: worst, side, clip };
  };

  // ---- background under a point ---------------------------------------
  const pointInShape = (shape, x, y) => {
    try {
      const m = shape.getScreenCTM();
      if (!m) return false;
      const p = new DOMPoint(x, y).matrixTransform(m.inverse());
      if (typeof shape.isPointInFill === "function") return shape.isPointInFill(p);
    } catch (e) { /* ignore */ }
    const r = shape.getBoundingClientRect();
    return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
  };
  const SHAPES = "rect, path, circle, ellipse, polygon";
  const bgAt = (el, x, y) => {
    const chain = [];
    for (let n = el; n; n = parentOf(n)) chain.push(n);
    chain.reverse();
    let bg = [255, 255, 255];
    let unknown = false;
    for (const n of chain) {
      if (n instanceof SVGElement) continue;
      const cs = getComputedStyle(n);
      const c = parseColor(cs.backgroundColor);
      if (c === undefined) { unknown = true; continue; }
      if (c && c[3] > 0) bg = over(c, c[3] * effOpacity(n), bg);
    }
    // SVG shapes painted before the text in the same outermost svg.
    const svg = el instanceof SVGElement ? el.ownerSVGElement && (() => {
      let s = el.ownerSVGElement; while (s.ownerSVGElement) s = s.ownerSVGElement; return s;
    })() : null;
    if (svg) {
      const shapes = [...svg.querySelectorAll(SHAPES)];
      for (const sh of shapes) {
        if (sh === el || (sh.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) === 0) continue;
        if (sh.contains(el)) continue;
        if (!visible(sh)) continue;
        const cs = getComputedStyle(sh);
        if (cs.fill === "none") continue;
        const c = parseColor(cs.fill);
        const a = parseFloat(cs.fillOpacity || "1") * effOpacity(sh);
        if (a <= 0.01) continue;
        if (!pointInShape(sh, x, y)) continue;
        if (c === undefined || c === null) { unknown = true; continue; }
        bg = over(c, c[3] * a, bg);
      }
    }
    return { bg, unknown };
  };
  const textContrast = (run) => {
    const el = run.el;
    const cs = getComputedStyle(el);
    let fg, a;
    if (run.isSvg) {
      if (cs.fill === "none") return null;
      fg = parseColor(cs.fill);
      if (!fg) return { unknown: true };
      a = fg[3] * parseFloat(cs.fillOpacity || "1") * effOpacity(el);
    } else {
      fg = parseColor(cs.color);
      if (!fg) return { unknown: true };
      a = fg[3] * effOpacity(el);
    }
    const x = (run.rect.left + run.rect.right) / 2, y = (run.rect.top + run.rect.bottom) / 2;
    const { bg, unknown } = bgAt(el, x, y);
    const fgc = over(fg, a, bg);
    let px = parseFloat(cs.fontSize);
    if (run.isSvg) {
      const m = el.getScreenCTM();
      if (m) px *= Math.hypot(m.a, m.b);
    }
    const bold = parseInt(cs.fontWeight, 10) >= 700;
    const large = px >= 24 || (bold && px >= 18.66);
    const disabled = !!el.closest("[disabled], [aria-disabled='true']");
    return {
      ratio: ratio(fgc, bg), need: large ? 3 : 4.5, px, unknown, disabled,
      fg: fgc.map((v) => Math.round(v)), bg: bg.map((v) => Math.round(v)),
    };
  };

  // ---- targets ----------------------------------------------------------
  const INTERACTIVE = [
    "button", "a[href]", "input:not([type=hidden])", "select", "textarea", "summary",
    "[role=button]", "[role=tab]", "[role=link]", "[role=checkbox]", "[role=switch]",
    "[role=slider]", "[role=menuitem]", "[role=option]", "[tabindex]",
  ].join(",");
  const isInteractive = (el) => {
    if (el.matches(INTERACTIVE) && !(el.getAttribute("tabindex") === "-1" && !el.matches("[role]"))) return true;
    const cs = getComputedStyle(el);
    if (cs.cursor !== "pointer") return false;
    const p = parentOf(el);
    return !p || getComputedStyle(p).cursor !== "pointer";
  };
  const targets = () => {
    const out = [];
    for (const el of allEls()) {
      if (el.tagName === "HA-CARD") continue;
      if (el.tagName === "DIALOG") continue;
      if (!isInteractive(el) || !visible(el)) continue;
      if (el.disabled || el.getAttribute("aria-disabled") === "true") continue;
      if (getComputedStyle(el).pointerEvents === "none") continue;
      const r = el.getBoundingClientRect();
      if (r.width < 0.5 || r.height < 0.5) continue;
      out.push({ el, r, cx: (r.left + r.right) / 2, cy: (r.top + r.bottom) / 2 });
    }
    return out;
  };
  const distToRect = (x, y, r) => Math.hypot(Math.max(r.left - x, 0, x - r.right), Math.max(r.top - y, 0, y - r.bottom));

  // ---- the main measurement ---------------------------------------------
  H.measure = (opts) => {
    const floor = opts.coarse ? 44 : 24;
    const runs = textRuns();
    const out = { runs: runs.length, overflow: [], overlap: [], contrast: [], contrastUnknown: 0,
      ellipsized: [], targets: 0, small: [], small24: [], nameless: [], pointerOnly: [],
      hscroll: 0, texts: [] };
    for (const run of runs) {
      const u = unreachable(run);
      if (u.px > 0.5) out.overflow.push({ px: +u.px.toFixed(1), side: u.side, clip: u.clip, el: path(run.el), txt: run.txt.slice(0, 40) });
      const c = textContrast(run);
      out.texts.push({ t: run.txt.slice(0, 80), el: path(run.el), svg: run.isSvg, px: c && c.px ? +c.px.toFixed(2) : null,
        h: +run.rect.height.toFixed(1) });
      if (c && c.unknown && c.ratio === undefined) out.contrastUnknown += 1;
      else if (c && !c.disabled && c.ratio + 1e-6 < c.need) {
        out.contrast.push({ ratio: +c.ratio.toFixed(2), need: c.need, px: +c.px.toFixed(1), fg: c.fg, bg: c.bg,
          el: path(run.el), txt: run.txt.slice(0, 40), bgUnknown: c.unknown });
      }
      if (!run.isSvg) {
        const cs = getComputedStyle(run.el);
        if (cs.textOverflow === "ellipsis" && run.el.scrollWidth > run.el.clientWidth + 1) {
          const full = run.el.getAttribute("title") || run.el.getAttribute("aria-label") || "";
          out.ellipsized.push({ el: path(run.el), txt: run.txt.slice(0, 40), hidden: run.el.scrollWidth - run.el.clientWidth, hasTitle: !!full });
        }
      }
    }
    for (let i = 0; i < runs.length; i++) {
      for (let j = i + 1; j < runs.length; j++) {
        const a = runs[i], b = runs[j];
        if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
        // Pop-ups (hover tooltip, slot menu) are drawn over the chart on purpose.
        if (a.el.closest(".tooltip, .slot-menu, .setup-picker") || b.el.closest(".tooltip, .slot-menu, .setup-picker")) continue;
        const ix = Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left);
        const iy = Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top);
        if (ix <= 3 || iy <= 3) continue;
        // A halo copy (same text, same box) is one label drawn twice.
        if (a.txt === b.txt && Math.abs(a.rect.left - b.rect.left) < 0.6 && Math.abs(a.rect.top - b.rect.top) < 0.6) continue;
        out.overlap.push({ ix: +ix.toFixed(1), iy: +iy.toFixed(1), a: path(a.el), at: a.txt.slice(0, 30), b: path(b.el), bt: b.txt.slice(0, 30) });
      }
    }
    const ts = targets();
    out.targets = ts.length;
    for (const t of ts) {
      const m = Math.min(t.r.width, t.r.height);
      const name = accName(t.el);
      if (!name) out.nameless.push({ el: path(t.el) });
      const focusable = t.el.tabIndex >= 0 || t.el.matches("button, a[href], input, select, textarea, summary");
      let focusAnc = false;
      for (let n = parentOf(t.el); n && n !== card(); n = parentOf(n)) {
        if (n.tagName !== "HA-CARD" && n.tabIndex >= 0 && n.tagName !== "DIALOG") { focusAnc = true; break; }
      }
      if (!focusable && !focusAnc) out.pointerOnly.push({ el: path(t.el), w: +t.r.width.toFixed(1), h: +t.r.height.toFixed(1) });
      if (m < floor - 0.05) {
        out.small.push({ el: path(t.el), w: +t.r.width.toFixed(1), h: +t.r.height.toFixed(1) });
      }
      if (m < 24 - 0.05) {
        // WCAG 2.5.8 spacing exception: a 24 px circle on the target's centre
        // must not intersect another target, or another undersized target's circle.
        let clash = null;
        for (const u of ts) {
          if (u === t) continue;
          if (u.el.contains(t.el) || t.el.contains(u.el)) continue;
          const um = Math.min(u.r.width, u.r.height);
          const d = um < 24 - 0.05 ? Math.hypot(u.cx - t.cx, u.cy - t.cy) - 12 : distToRect(t.cx, t.cy, u.r);
          if (d < 12) { clash = desc(u.el); break; }
        }
        if (clash) out.small24.push({ el: path(t.el), w: +t.r.width.toFixed(1), h: +t.r.height.toFixed(1), clash });
      }
    }
    // Pop-ups must sit inside the viewport and inside their chart's box.
    out.popups = [];
    for (const p of scope().querySelectorAll(".tooltip, .slot-menu")) {
      if (!visible(p)) continue;
      const r = p.getBoundingClientRect();
      const host = p.closest(".chartwrap");
      const hr = host ? host.getBoundingClientRect() : null;
      const vwOut = Math.max(0, -r.left, r.right - innerWidth, -r.top, r.bottom - innerHeight);
      const hostOut = hr ? Math.max(0, hr.left - r.left, r.right - hr.right) : 0;
      out.popups.push({ el: desc(p), w: +r.width.toFixed(1), left: +r.left.toFixed(1), right: +r.right.toFixed(1),
        vwOut: +vwOut.toFixed(1), hostOut: +hostOut.toFixed(1) });
    }
    // Listbox options: a <select size=N> neither wraps nor scrolls sideways, so
    // an option wider than the box shows only the prefix that fits. Two options
    // whose visible prefixes are identical cannot be told apart.
    out.options = [];
    const cv = document.createElement("canvas").getContext("2d");
    for (const sel of scope().querySelectorAll("select")) {
      if (!visible(sel)) continue;
      const opts = [...sel.options];
      const vis = opts.map((o) => {
        const cs = getComputedStyle(o);
        cv.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
        const avail = o.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
        const full = o.text;
        if (o.scrollWidth <= o.clientWidth + 1) return { full, shown: full, cut: false };
        let lo = 0, hi = full.length;
        while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (cv.measureText(full.slice(0, mid)).width <= avail) lo = mid; else hi = mid - 1; }
        return { full, shown: full.slice(0, lo), cut: true, scroll: o.scrollWidth, client: o.clientWidth };
      });
      const pairs = [];
      for (let i = 0; i < vis.length; i++) for (let j = i + 1; j < vis.length; j++) {
        if (vis[i].full !== vis[j].full && vis[i].shown === vis[j].shown) pairs.push([vis[i].full, vis[j].full, vis[i].shown]);
      }
      out.options.push({ el: path(sel), n: opts.length, cut: vis.filter((v) => v.cut).length, indistinct: pairs.length,
        pairs: pairs.slice(0, 3), widest: Math.max(...vis.map((v) => v.scroll || 0)), box: sel.clientWidth });
    }
    // Motion: elements with a running transition or animation duration.
    out.motion = allEls().filter((el) => {
      const cs = getComputedStyle(el);
      const d = (v) => (v || "0s").split(",").some((x) => parseFloat(x) > 0);
      return d(cs.transitionDuration) || (cs.animationName && cs.animationName !== "none" && d(cs.animationDuration));
    }).map((el) => desc(el));
    const de = document.documentElement;
    out.hscroll = de.scrollWidth - de.clientWidth;
    return out;
  };

  const accName = (el) => {
    const lab = el.getAttribute("aria-label");
    if (lab && lab.trim()) return lab.trim();
    const lb = el.getAttribute("aria-labelledby");
    if (lb) {
      const r = el.getRootNode();
      const t = lb.split(/\s+/).map((id) => (r.getElementById ? r.getElementById(id) : null)).filter(Boolean)
        .map((n) => n.textContent.trim()).join(" ");
      if (t) return t;
    }
    if (el.labels && el.labels.length) {
      const t = [...el.labels].map((l) => l.textContent.trim()).join(" ");
      if (t) return t;
    }
    if (el.closest && el.closest("label") && el.closest("label").textContent.trim()) return el.closest("label").textContent.trim();
    const tt = el.getAttribute("title");
    if (tt && tt.trim()) return tt.trim();
    if (el instanceof SVGElement) {
      const t = el.querySelector(":scope > title");
      if (t && t.textContent.trim()) return t.textContent.trim();
    }
    if (el.tagName === "INPUT" && el.placeholder) return el.placeholder;
    const txt = (el.textContent || "").trim();
    return txt;
  };

  // ---- keyboard -----------------------------------------------------------
  let seq = 0;
  H.tagIds = () => {
    for (const el of root().querySelectorAll("*")) if (!el.dataset || !el.dataset.hpoId) { if (el.dataset) el.dataset.hpoId = String(++seq); }
  };
  H.focusables = () => allEls().filter((el) => el.tabIndex >= 0 && visible(el) && !el.disabled
    && !(el.closest && el.closest("[inert]"))).map((el) => ({ id: el.dataset.hpoId, el: path(el),
    x: el.getBoundingClientRect().left, y: el.getBoundingClientRect().top, name: accName(el).slice(0, 40) }));
  H.active = () => {
    let a = document.activeElement;
    while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement;
    return a && a.dataset ? { id: a.dataset.hpoId || null, el: path(a) } : { id: null, el: a ? a.tagName : "none" };
  };
  const SNAP = ["outlineStyle", "outlineWidth", "outlineColor", "boxShadow", "backgroundColor", "color",
    "borderTopColor", "stroke", "strokeWidth", "fill", "textDecorationLine", "opacity"];
  const snap = (el) => { const cs = getComputedStyle(el); return SNAP.map((k) => cs[k]).join("|"); };
  H.focusIndicator = (id) => {
    const el = root().querySelector(`[data-hpo-id="${id}"]`);
    if (!el) return { id, missing: true };
    el.blur();
    const off = snap(el);
    el.focus();
    const cs = getComputedStyle(el);
    const on = snap(el);
    const outline = cs.outlineStyle !== "none" && parseFloat(cs.outlineWidth) > 0 && (parseColor(cs.outlineColor) || [0, 0, 0, 0])[3] > 0;
    return { id, el: path(el), outline, changed: on !== off, visible: outline || on !== off };
  };

  // ---- drivers (tests/card_drift.mjs STATES, against the real DOM) --------
  const frame = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const click = (el) => el && el.dispatchEvent(new MouseEvent("click", { bubbles: true, composed: true, cancelable: true }));
  const chartSvgsAll = () => [...root().querySelectorAll(".chartwrap svg")];
  const svgPx = (svg, vbX) => {
    const r = svg.getBoundingClientRect();
    return r.left + (vbX / VIEW_W) * r.width;
  };
  const pe = (type, x, y, target) => {
    const ev = new PointerEvent(type, { bubbles: true, composed: true, cancelable: true, clientX: x, clientY: y, pointerId: 1, isPrimary: true, button: 0, buttons: type === "pointerup" ? 0 : 1 });
    (target || window).dispatchEvent(ev);
  };
  H.drive = async (steps) => {
    const c = card();
    const req = {};
    for (const s of steps) {
      const [op, a1, a2] = s;
      if (op === "cardClick") c._onCardClick({});
      else if (op === "open") c.dialog.open();
      else if (op === "page") { c.dialog.page = a1; c._render(); }
      else if (op === "chip") { const el = root().querySelector(`.chip[data-key='${a1}']`); if (el) el.click(); }
      else if (op === "clickSel") { const el = root().querySelector(a1); if (el) el.click(); req[a1] = !!el; await sleep(60); }
      else if (op === "lowerCeiling") {
        // The setpoint moved after the draft was seeded: the next hass carries a lower ceiling.
        const st = JSON.parse(JSON.stringify(c.hass.states));
        for (const e of Object.values(st)) if (e.attributes && "dhw_min_temperature_max" in e.attributes) e.attributes.dhw_min_temperature_max = a1;
        c.hass = { ...c.hass, states: st };
      }
      else if (op === "stat") click(root().querySelector(`[data-stat='${a1}']`));
      else if (op === "zoom") c.view.zoom(a1);
      else if (op === "pan") { c.view.panBy(a1 * HOUR); await sleep(400); }
      else if (op === "dragDhw") {
        await frame();
        const svgs = chartSvgsAll(); const svg = svgs[svgs.length - 1];
        const runs = c.manual.draft().dhw; const [lo] = c.manual.bounds();
        const i = runs.findIndex((r) => r.end > lo && r.start >= lo);
        const hit = svg && [...svg.querySelectorAll("[data-channel='dhw'][data-index]")].find((e) => e.dataset.index === String(i) && !e.dataset.edge);
        if (hit) {
          const geom = c.geomAt(svgs.length - 1);
          const xOf = (t) => svgPx(svg, geom.plotL + ((t - geom.windowStart) / (geom.windowEnd - geom.windowStart)) * geom.plotW);
          const hr = hit.getBoundingClientRect(); const y = (hr.top + hr.bottom) / 2;
          const x0 = xOf(runs[i].start + 60000), x1 = xOf(runs[i].start + 60000 + HOUR);
          pe("pointerdown", x0, y, hit); pe("pointermove", x1, y, window);
          if (a1) pe("pointerup", x1, y, window);
          req.dragged = true;
        } else req.dragged = false;
      } else if (op === "menu" || op === "menuAt") {
        // A tap on the channel's lane opens the menu at the tap point
        // (LaneEditor.onUp -> openMenu(channel, at, ev.clientX, ev.clientY)).
        const svgs = chartSvgsAll(); const svg = svgs[svgs.length - 1];
        const geom = c.geomAt(svgs.length - 1);
        const t = op === "menu" ? geom.windowStart + a2 * HOUR
          : geom.windowStart + a2 * (geom.windowEnd - geom.windowStart);
        const x = svgPx(svg, geom.plotL + ((t - geom.windowStart) / (geom.windowEnd - geom.windowStart)) * geom.plotW);
        const lane = svg.querySelector(`rect.lane[data-channel='${a1}']`) || svg.querySelector(`[data-channel='${a1}']`);
        const lr = lane ? lane.getBoundingClientRect() : svg.getBoundingClientRect();
        c.lanes.openMenu(a1, t, x, (lr.top + lr.bottom) / 2, svg, false);
        req.menuAt = { x, y: (lr.top + lr.bottom) / 2 };
      } else if (op === "whatifInput") {
        c.whatIf.onInput({ stopPropagation() {}, preventDefault() {}, target: { value: "42", classList: { contains: (x) => x === "wi-dhw-min" } } });
        clearTimeout(c.whatIf.timer); c.whatIf.timer = null;
      } else if (op === "addWindow") c.whatIf.onAddWindow({ stopPropagation() {}, preventDefault() {} });
      else if (op === "hover") {
        await frame();
        const svgs = chartSvgsAll(); const svg = svgs[svgs.length - 1];
        const plot = c._plot;
        const t = a1 === "firstShared" ? a2 : plot.windowStart + a1 * HOUR;
        const r = svg.getBoundingClientRect();
        req.hover = { x: svgPx(svg, plot.scaleX(t)), y: r.top + r.height * 0.45 };
      } else if (op === "layoutToggle") click(root().querySelector(".layout-edit-toggle"));
      else if (op === "layoutDrag") {
        await frame();
        const le = c.layoutEditor;
        const box = (le.boxes || []).find((b) => b.place === "buffer_tank");
        const p0 = le.point({ clientX: 0, clientY: 0 }), p1 = le.point({ clientX: 100, clientY: 100 });
        if (box && p0 && p1) {
          const sx = (p1.x - p0.x) / 100, sy = (p1.y - p0.y) / 100;
          const toPx = (u) => ({ x: (u.x - p0.x) / sx, y: (u.y - p0.y) / sy });
          const from = { x: box.x + box.w / 2, y: box.y + box.h / 2 }, to = { x: from.x + 40, y: from.y + 30 };
          const mid = { x: (from.x + to.x) / 2, y: (from.y + to.y) / 2 };
          const ev = (u) => ({ ...toPx(u), stopPropagation() {}, preventDefault() {} });
          const e0 = ev(from); le.onDown({ clientX: e0.x, clientY: e0.y, target: { dataset: {} }, stopPropagation() {}, preventDefault() {} });
          const e1 = ev(mid); le.onMove({ clientX: e1.x, clientY: e1.y, target: {}, stopPropagation() {}, preventDefault() {} });
          const e2 = ev(to); le.onUp({ clientX: e2.x, clientY: e2.y, target: {}, stopPropagation() {}, preventDefault() {} });
          req.layoutDragged = true;
        }
        if (a1) click(root().querySelector(".layout-tidy"));
      } else if (op === "picker") {
        const hit = [...root().querySelectorAll(".setup-hit")].find((h) => h.dataset.key === "wood_tank_top_entity");
        click(hit);
        await frame();
        const box = root().querySelector(".sp-filter");
        if (box) { box.value = "vedpanna"; box.dispatchEvent(new Event("input", { bubbles: true, composed: true })); }
      }
      await frame();
    }
    await sleep(120);
    await frame();
    return req;
  };
  H.shot = () => {
    const d = modalDialog();
    return d ? "dialog" : "card";
  };
})();
