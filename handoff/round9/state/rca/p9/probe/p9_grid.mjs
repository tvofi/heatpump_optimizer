// P9 class barrier (prototype): the rendered-property rules over a state grid.
//
// Every earlier P9 witness in tests/card_browser.mjs is keyed to the instance
// that produced it: a REQUIRED list of four contrast selectors, a unit regex
// that omits SEK/kWh, one hover row. Round 9 found five more instances at
// selectors and states none of them named. This block asserts the PROPERTY
// over every rendered node instead, in every cell of a grid, and a REACH rule
// that fails when the card styles a colour no cell renders -- so a new status
// class cannot ship unmeasured by being absent from the grid.
//
// Exported as one function so card_browser.mjs calls it with its browser and
// check(); run alone by probe/run_grid.mjs for the RCA's fail/pass/null runs.
import { readFileSync } from "node:fs";
import {
  DEFAULT_SPACE, DEFAULT_DHW, HOUR, planStates, setupSensorStates, qaTopologies, withActuals, layoutCatalogTopo,
} from "./card_rig.mjs";

// HA's default theme tokens, including the status colours the card reads.
const THEMES = {
  light: `--primary-color:#03a9f4;--accent-color:#ff9800;--primary-text-color:#212121;--secondary-text-color:#727272;
    --text-primary-color:#ffffff;--disabled-text-color:#bdbdbd;--primary-background-color:#fafafa;--secondary-background-color:#e5e5e5;
    --card-background-color:#ffffff;--divider-color:rgba(0,0,0,.12);--error-color:#db4437;--warning-color:#ffa600;--success-color:#43a047;--info-color:#039be5;`,
  dark: `--primary-color:#03a9f4;--accent-color:#ff9800;--primary-text-color:#e1e1e1;--secondary-text-color:#9b9b9b;
    --text-primary-color:#ffffff;--disabled-text-color:#6f6f6f;--primary-background-color:#111111;--secondary-background-color:#282828;
    --card-background-color:#1c1c1c;--divider-color:rgba(225,225,225,.12);--error-color:#db4437;--warning-color:#ffa600;--success-color:#43a047;--info-color:#039be5;`,
};
const VIEWPORTS = [[375, 812], [768, 1024], [1280, 800]];

function gridStates(plan) {
  const scheduleStates = () => {
    const st = planStates(plan);
    st[DEFAULT_SPACE].attributes.day_start_hour = 7;
    st[DEFAULT_SPACE].attributes.day_end_hour = 22;
    st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30, 17:00-22:00";
    return st;
  };
  const setupStates = (topo, extra) => {
    const st = { ...planStates(plan), ...setupSensorStates(), ...(extra || {}) };
    st[DEFAULT_SPACE].attributes.setup_topology = topo;
    return st;
  };
  // Two sensors sharing a friendly name: the picker must tell them apart.
  const twins = () => {
    const st = {};
    for (let i = 0; i < 40; i++) {
      st[`sensor.zz_probe_${String(i).padStart(3, "0")}`] = { state: "20.0",
        attributes: { unit_of_measurement: "°C", friendly_name: `Probe ${String(i).padStart(3, "0")}` } };
    }
    for (const [id, v] of [["sensor.vedpanna_temperatur_temperature", "71.2"], ["sensor.vedpanna_temperatur_temperature_2", "48.9"]]) {
      st[id] = { state: v, attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
    }
    return st;
  };
  const clamped = () => {
    const st = scheduleStates();
    for (const id of [DEFAULT_SPACE, DEFAULT_DHW]) {
      st[id].attributes.dhw_min_temperature = 55; st[id].attributes.dhw_min_temperature_max = 60;
    }
    return st;
  };
  const wi = { what_if: true };
  const statStates = () => ({
    "sensor.heat_pump_optimizer_predicted_savings": { state: "12.34", attributes: { unit_of_measurement: "SEK" } },
    "sensor.heat_pump_optimizer_savings_percentage": { state: "8.2", attributes: {} },
    "sensor.heat_pump_optimizer_optimization_score": { state: "82", attributes: { envelope: 90, machine: 75 } },
    "sensor.heat_pump_optimizer_plan_narrative": { state: "cheap_price", attributes: {
      lines: ["Most heating is placed in the cheapest hours."], language: "en" } },
  });
  const shared = () => {
    const st = planStates(plan);
    const heating = new Set(st[DEFAULT_SPACE].attributes.forecast.filter((p) => Number(p.space_power) > 0.05).map((p) => p.t));
    st[DEFAULT_DHW].attributes.forecast = st[DEFAULT_DHW].attributes.forecast.map((p) => heating.has(p.t) ? { ...p, dhw_power: 1.5 } : p);
    return st;
  };
  const wood = (fuel) => { const st = planStates(plan); st[DEFAULT_SPACE].attributes.wood_fuel = fuel; return st; };
  const away = ({ sw = false, resolved = false } = {}) => {
    const st = planStates(plan);
    st["switch.heat_pump_optimizer_away"] = { state: sw ? "on" : "off", attributes: {} };
    st["datetime.heat_pump_optimizer_away_return"] = { state: "unknown", attributes: {} };
    st["binary_sensor.heat_pump_optimizer_away_mode"] = { state: resolved ? "on" : "off",
      attributes: { source: resolved && !sw ? "person.alice" : "none" } };
    return st;
  };
  const override = () => {
    const st = planStates(plan);
    const at = Date.parse(plan.dhw_plan.forecast[0].t) + 11 * HOUR;
    const info = { active: true, expires_at: new Date(at).toISOString(), space_slots: [], dhw_slots: [], released_space: [], released_dhw: [] };
    st[DEFAULT_SPACE].attributes.manual_override = info; st[DEFAULT_DHW].attributes.manual_override = info;
    return st;
  };
  const advisor = () => {
    const st = setupStates(qaTopologies().base);
    st[DEFAULT_SPACE].attributes.sensor_advisor = { basis: "history", candidates: [
      { key: "buffer_tank_temp_entity", label: "Buffer tank temperature", spread_c: 4.13, parameters: ["buffer_cooling_rate"], priced: true },
      { key: "dhw_temp_entity", label: "Hot water temperature", priced: false, reason: "no_clamped_parameter" },
    ] };
    return st;
  };
  const S = (name, o) => ({ name, config: {}, steps: [], service: false, ...o });
  return [
    S("live_default", { states: withActuals(planStates(plan)) }),
    S("live_default_expanded", { states: withActuals(planStates(plan)), steps: [["cardClick"]] }),
    S("draft_menu_open", { states: planStates(plan), config: wi, steps: [["cardClick"], ["dragDhw"], ["menuAt", "space", 0.1]] }),
    S("menu_right_edge", { states: planStates(plan), config: wi, steps: [["cardClick"], ["menuAt", "space", 0.97]] }),
    S("menu_right_edge_dhw", { states: planStates(plan), config: wi, steps: [["cardClick"], ["menuAt", "dhw", 0.97]] }),
    S("pin_ok", { states: planStates(plan), config: wi, service: "ok", steps: [["cardClick"], ["dragDhw"], ["clickSel", ".wi-pin"]] }),
    S("pin_fail", { states: planStates(plan), config: wi, service: "fail", steps: [["cardClick"], ["dragDhw"], ["clickSel", ".wi-pin"]] }),
    S("save_confirm", { states: scheduleStates(), config: wi, service: "ok", steps: [["cardClick"], ["clickSel", ".wi-save"]] }),
    S("save_ok", { states: scheduleStates(), config: wi, service: "ok", steps: [["cardClick"], ["clickSel", ".wi-save"], ["clickSel", ".wi-save"]] }),
    S("save_fail", { states: scheduleStates(), config: wi, service: "fail", steps: [["cardClick"], ["clickSel", ".wi-save"], ["clickSel", ".wi-save"]] }),
    S("dhw_clamped", { states: clamped(), config: wi, steps: [["cardClick"], ["lowerCeiling", 50]] }),
    S("no_plan", { states: {} }),
    S("no_plan_expanded", { states: {}, steps: [["open"]] }),
    S("score_open", { states: { ...planStates(plan), ...statStates() }, steps: [["stat", "score"]] }),
    S("savings_open", { states: { ...planStates(plan), ...statStates() }, steps: [["stat", "savings"]] }),
    S("hidden_series", { states: planStates(plan), config: { series: { outdoor: false, solar: false } }, steps: [["chip", "price"]] }),
    S("tooltip_hover", { states: planStates(plan), steps: [["cardClick"], ["hover", 5]] }),
    S("override_active", { states: override(), config: wi, steps: [["open"]] }),
    S("wood_alert", { states: wood({ cheaper: true, show_whatif: true, ready: true, slots: [] }) }),
    S("wood_lane", { states: wood({ cheaper: false, show_whatif: true, ready: true, slots: [{ start: plan.space_plan.forecast[0].t,
      end: plan.space_plan.forecast[Math.min(4, plan.space_plan.forecast.length - 1)].t, source: "detected" }] }) }),
    S("away_return", { states: away({ sw: true }), steps: [["cardClick"]] }),
    S("away_status", { states: away({ resolved: true }), steps: [["cardClick"]] }),
    S("setup_two_tank", { states: setupStates(qaTopologies().twoTank), steps: [["cardClick"], ["page", "setup"]] }),
    S("advisor_page", { states: advisor(), steps: [["cardClick"], ["page", "advisor"]] }),
    S("savings_page", { states: { ...planStates(plan), "sensor.heat_pump_optimizer_plan_monthly_savings": { state: "8.1",
      attributes: { unit_of_measurement: "SEK", savings_months: [
        { month: "2026-01", baseline_sek: 900, actual_sek: 820, savings_sek: 80, savings_pct: 8.9, estimated: true },
        { month: "2025-12", baseline_sek: 700, actual_sek: 712, savings_sek: -12, savings_pct: -1.7 }] } } },
      steps: [["cardClick"], ["page", "savings"]] }),
    S("estimated_price_hover", { states: (() => { const st = planStates(plan);
      for (const id of [DEFAULT_SPACE, DEFAULT_DHW]) st[id].attributes.forecast = st[id].attributes.forecast.map((p) => ({ ...p, price_known: false }));
      return st; })(), steps: [["cardClick"], ["hover", 3]] }),
    S("shared_steps_hover", { states: shared(), steps: [["cardClick"], ["hoverShared"]] }),
    S("view_limit", { states: planStates(plan), config: wi, steps: [["cardClick"], ["zoom", 0.25]] }),
    S("layout_editing", { states: setupStates(layoutCatalogTopo()), steps: [["cardClick"], ["page", "setup"], ["clickSel", ".layout-edit-toggle"]] }),
    S("setup_clear_armed", { states: setupStates(qaTopologies().base), steps: [["cardClick"], ["page", "setup"], ["armClear"]] }),
    S("picker_twins", { states: setupStates(qaTopologies().base, twins()), steps: [["cardClick"], ["page", "setup"], ["picker", "vedpanna"]] }),
  ];
}

// ---- the in-page instrument (serialised into the page) ---------------------
function instrument() {
  const H = {};
  window.__p9 = H;
  const parseColor = (s) => {
    if (!s || s === "none" || s === "transparent") return null;
    let m = s.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+%?))?\s*\)$/);
    if (m) return [+m[1], +m[2], +m[3], m[4] === undefined ? 1 : (m[4].endsWith("%") ? parseFloat(m[4]) / 100 : +m[4])];
    m = s.match(/^color\(srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\)$/);
    if (m) return [m[1] * 255, m[2] * 255, m[3] * 255, m[4] === undefined ? 1 : +m[4]];
    return undefined;
  };
  const over = (top, a, bottom) => [0, 1, 2].map((i) => top[i] * a + bottom[i] * (1 - a));
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
  };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const parentOf = (n) => n.parentElement || (n.getRootNode && n.getRootNode().host) || null;
  const effOpacity = (el) => { let o = 1; for (let n = el; n; n = parentOf(n)) o *= parseFloat(getComputedStyle(n).opacity || "1"); return o; };
  const visible = (el) => {
    if (!el.getClientRects || !el.getClientRects().length) return false;
    const cs = getComputedStyle(el);
    if (cs.visibility !== "visible" || cs.display === "none") return false;
    if (el.closest && el.closest("defs, pattern, clipPath, mask, marker, symbol, title")) return false;
    return effOpacity(el) > 0.02;
  };
  const desc = (el) => {
    const cls = (el.getAttribute && el.getAttribute("class")) || "";
    return (el.tagName.toLowerCase() + (cls ? "." + cls.trim().split(/\s+/).join(".") : "")).slice(0, 60);
  };
  const card = () => document.querySelector("heatpump-optimizer-card");
  const root = () => card().shadowRoot;
  const scope = () => { const d = root().querySelector("dialog[open]"); return d && d.matches(":modal") ? d : root(); };
  const allEls = () => [...scope().querySelectorAll("*")];

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
        rect = el.getBoundingClientRect();
      } else {
        const rs = [];
        txt = "";
        for (const tn of el.childNodes) {
          if (tn.nodeType !== 3 || !tn.textContent.trim()) continue;
          txt += tn.textContent;
          const r = document.createRange(); r.selectNodeContents(tn); rs.push(...r.getClientRects());
        }
        txt = txt.replace(/\s+/g, " ").trim();
        if (!rs.length) continue;
        const l = Math.min(...rs.map((r) => r.left)), t = Math.min(...rs.map((r) => r.top));
        const r = Math.max(...rs.map((r) => r.right)), b = Math.max(...rs.map((r) => r.bottom));
        rect = { left: l, top: t, right: r, bottom: b, width: r - l, height: b - t };
      }
      if (!txt || rect.width < 0.5 || rect.height < 0.5) continue;
      runs.push({ el, txt, rect, isSvg });
    }
    return runs;
  };
  // Ink a clipping ancestor hides and cannot scroll to.
  const unreachable = (run) => {
    let worst = 0;
    for (const axis of ["x", "y"]) {
      for (let n = parentOf(run.el); n && n !== document.documentElement; n = parentOf(n)) {
        const cs = getComputedStyle(n);
        const o = axis === "x" ? cs.overflowX : cs.overflowY;
        if (o === "visible") continue;
        const r = n.getBoundingClientRect();
        const scroll = o === "auto" || o === "scroll";
        const [a0, a1, c0, c1, eA, eB] = axis === "x"
          ? [run.rect.left, run.rect.right, r.left, r.right, scroll ? n.scrollLeft : 0, scroll ? n.scrollWidth - n.clientWidth - n.scrollLeft : 0]
          : [run.rect.top, run.rect.bottom, r.top, r.bottom, scroll ? n.scrollTop : 0, scroll ? n.scrollHeight - n.clientHeight - n.scrollTop : 0];
        worst = Math.max(worst, (c0 - eA) - a0, a1 - (c1 + eB));
        break;
      }
    }
    return worst;
  };
  const inShape = (sh, x, y) => {
    try { const m = sh.getScreenCTM(); if (m && sh.isPointInFill) return sh.isPointInFill(new DOMPoint(x, y).matrixTransform(m.inverse())); } catch (e) { /* fall through */ }
    const r = sh.getBoundingClientRect(); return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
  };
  const bgAt = (el, x, y) => {
    const chain = []; for (let n = el; n; n = parentOf(n)) chain.push(n); chain.reverse();
    let bg = [255, 255, 255];
    for (const n of chain) {
      if (n instanceof SVGElement) continue;
      const c = parseColor(getComputedStyle(n).backgroundColor);
      if (c && c[3] > 0) bg = over(c, c[3] * effOpacity(n), bg);
    }
    let svg = el instanceof SVGElement ? el.ownerSVGElement : null;
    while (svg && svg.ownerSVGElement) svg = svg.ownerSVGElement;
    if (svg) {
      for (const sh of svg.querySelectorAll("rect, path, circle, ellipse, polygon")) {
        if ((sh.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) === 0 || !visible(sh)) continue;
        const cs = getComputedStyle(sh);
        const c = parseColor(cs.fill);
        const a = parseFloat(cs.fillOpacity || "1") * effOpacity(sh);
        if (!c || a <= 0.01 || !inShape(sh, x, y)) continue;
        bg = over(c, c[3] * a, bg);
      }
    }
    return bg;
  };
  const contrastOf = (run) => {
    const cs = getComputedStyle(run.el);
    const fg = parseColor(run.isSvg ? cs.fill : cs.color);
    if (fg === null) return null;
    if (fg === undefined) return { unknown: true };
    const a = fg[3] * (run.isSvg ? parseFloat(cs.fillOpacity || "1") : 1) * effOpacity(run.el);
    const bg = bgAt(run.el, (run.rect.left + run.rect.right) / 2, (run.rect.top + run.rect.bottom) / 2);
    let px = parseFloat(cs.fontSize);
    if (run.isSvg) { const m = run.el.getScreenCTM(); if (m) px *= Math.hypot(m.a, m.b); }
    const large = px >= 24 || (parseInt(cs.fontWeight, 10) >= 700 && px >= 18.66);
    return { ratio: ratio(over(fg, a, bg), bg), need: large ? 3 : 4.5 };
  };
  const INTERACTIVE = "button, a[href], input:not([type=hidden]), select, textarea, summary, [role=button], [role=tab], [role=option], [role=menuitem], [tabindex]";
  const targets = () => allEls().filter((el) => {
    if (el.tagName === "HA-CARD" || el.tagName === "DIALOG" || !visible(el) || el.disabled) return false;
    if (getComputedStyle(el).pointerEvents === "none") return false;
    if (el.matches(INTERACTIVE) && !(el.getAttribute("tabindex") === "-1" && !el.matches("[role]"))) return true;
    if (getComputedStyle(el).cursor !== "pointer") return false;
    const p = parentOf(el); return !p || getComputedStyle(p).cursor !== "pointer";
  }).map((el) => { const r = el.getBoundingClientRect(); return { el, r, cx: (r.left + r.right) / 2, cy: (r.top + r.bottom) / 2 }; })
    .filter((t) => t.r.width >= 0.5 && t.r.height >= 0.5);

  H.measure = (coarse) => {
    const out = { runs: 0, contrast: [], unknownColour: 0, overflow: [], boxPairs: [], small: [], popups: [], options: [] };
    const runs = textRuns();
    out.runs = runs.length;
    runs.forEach((r, i) => r.el.setAttribute("data-p9run", String(i)));
    for (const run of runs) {
      const u = unreachable(run);
      if (u > 0.5) out.overflow.push(`${desc(run.el)} "${run.txt.slice(0, 30)}" ${u.toFixed(1)}px`);
      if (run.el.closest("[disabled], [aria-disabled='true']")) continue;
      const c = contrastOf(run);
      if (c && c.unknown) out.unknownColour += 1;
      else if (c && c.ratio + 1e-6 < c.need) out.contrast.push(`${desc(run.el)} "${run.txt.slice(0, 30)}" ${c.ratio.toFixed(2)}:1<${c.need}`);
    }
    // Candidate collisions: two text runs whose boxes intersect. Boxes are
    // line boxes; whether the GLYPHS touch is decided on pixels by the host.
    for (let i = 0; i < runs.length; i++) for (let j = i + 1; j < runs.length; j++) {
      const a = runs[i], b = runs[j];
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      if (a.el.closest(".tooltip, .slot-menu, .setup-picker") || b.el.closest(".tooltip, .slot-menu, .setup-picker")) continue;
      const ix = Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left);
      const iy = Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top);
      if (ix <= 0.5 || iy <= 0.5) continue;
      if (a.txt === b.txt && Math.abs(a.rect.left - b.rect.left) < 0.6 && Math.abs(a.rect.top - b.rect.top) < 0.6) continue;
      const u = { x: Math.min(a.rect.left, b.rect.left) - 1, y: Math.min(a.rect.top, b.rect.top) - 1 };
      out.boxPairs.push({ a: i, b: j, at: `${desc(a.el)} "${a.txt.slice(0, 20)}"`, bt: `${desc(b.el)} "${b.txt.slice(0, 20)}"`,
        clip: { x: u.x, y: u.y, width: Math.max(a.rect.right, b.rect.right) + 1 - u.x, height: Math.max(a.rect.bottom, b.rect.bottom) + 1 - u.y } });
    }
    const ts = targets(), floor = coarse ? 44 : 24;
    for (const t of ts) {
      if (Math.min(t.r.width, t.r.height) >= floor - 0.05) continue;
      // WCAG 2.5.8's spacing exception: a 24 px circle on the centre clears every other target.
      const clash = ts.some((u) => u !== t && !u.el.contains(t.el) && !t.el.contains(u.el) &&
        (Math.min(u.r.width, u.r.height) < 23.95 ? Math.hypot(u.cx - t.cx, u.cy - t.cy) - 12
          : Math.hypot(Math.max(u.r.left - t.cx, 0, t.cx - u.r.right), Math.max(u.r.top - t.cy, 0, t.cy - u.r.bottom))) < 12);
      // A slot the card could not grow because its neighbours abut it on both
      // sides is the lane's accepted "boxed in" case (card_browser.mjs), not a defect.
      const abuts = (side) => ts.some((u) => u !== t && Math.min(u.r.bottom, t.r.bottom) - Math.max(u.r.top, t.r.top) > 1 &&
        (side < 0 ? Math.abs(u.r.right - t.r.left) < 1 : Math.abs(u.r.left - t.r.right) < 1));
      if (clash && !(abuts(-1) && abuts(1))) out.small.push(`${desc(t.el)} ${t.r.width.toFixed(1)}x${t.r.height.toFixed(1)}`);
    }
    // Every pop-up sits inside the viewport and inside the chart it belongs to.
    for (const p of scope().querySelectorAll(".tooltip, .slot-menu")) {
      if (!visible(p)) continue;
      const r = p.getBoundingClientRect(), host = p.closest(".chartwrap"), hr = host && host.getBoundingClientRect();
      const out1 = Math.max(0, -r.left, r.right - innerWidth, -r.top, r.bottom - innerHeight, hr ? hr.left - r.left : 0, hr ? r.right - hr.right : 0);
      if (out1 > 0.5) out.popups.push(`${desc(p)} ${out1.toFixed(1)}px outside`);
    }
    // A listbox option shows only the prefix that fits; two options whose shown text is equal are one option to a reader.
    const cv = document.createElement("canvas").getContext("2d");
    for (const sel of scope().querySelectorAll("select")) {
      if (!visible(sel)) continue;
      const shown = [...sel.options].map((o) => {
        const cs = getComputedStyle(o);
        if (o.scrollWidth <= o.clientWidth + 1) return o.text;
        cv.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
        const avail = o.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
        let lo = 0, hi = o.text.length;
        while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (cv.measureText(o.text.slice(0, mid)).width <= avail) lo = mid; else hi = mid - 1; }
        return o.text.slice(0, lo);
      });
      const full = [...sel.options].map((o) => o.text);
      for (let i = 0; i < shown.length; i++) for (let j = i + 1; j < shown.length; j++) {
        if (full[i] !== full[j] && shown[i] === shown[j]) out.options.push(`${desc(sel)} "${shown[i]}"`);
        else if (full[i] === full[j]) out.options.push(`${desc(sel)} twice "${full[i]}"`);
      }
    }
    return out;
  };
  // REACH: every card rule that sets a colour, with its selector reduced to
  // what querySelectorAll can test, and whether a visible element matches it now.
  H.colourRules = () => {
    const sheets = [...root().querySelectorAll("style")].map((s) => s.sheet).filter(Boolean)
      .concat(root().adoptedStyleSheets || []);
    const out = {};
    const walk = (rules, media) => {
      for (const r of rules) {
        if (r.cssRules && !(r instanceof CSSStyleRule)) { walk(r.cssRules, r.conditionText || r.media && r.media.mediaText || media); continue; }
        if (!(r instanceof CSSStyleRule)) continue;
        const st = r.style;
        if (!["color", "background-color", "background", "fill"].some((p) => st.getPropertyValue(p) && !/^(inherit|currentcolor|transparent|none|initial|unset)$/i.test(st.getPropertyValue(p).trim()))) continue;
        for (const sel of r.selectorText.split(",")) {
          if (/::?(before|after|backdrop|placeholder|selection|-webkit-)/.test(sel)) continue;
          const base = sel.replace(/:(hover|focus-visible|focus-within|focus|active|visited|host)(\([^)]*\))?/g, "").trim();
          if (!base) continue;
          const key = media ? `@${media} ${sel.trim()}` : sel.trim();
          let hit = false;
          try { hit = [...root().querySelectorAll(base)].some(visible); } catch (e) { hit = false; }
          out[key] = hit;
        }
      }
    };
    for (const s of sheets) walk(s.cssRules, "");
    return out;
  };
  // Pixel ink of one text run: everything else hidden, the run forced black on white.
  H.inkMode = (i) => {
    let st = root().querySelector("style#p9ink");
    if (!st) { st = document.createElement("style"); st.id = "p9ink"; root().appendChild(st); }
    st.textContent = i === null ? "" :
      `*{visibility:hidden!important;background:transparent!important;border-color:transparent!important;box-shadow:none!important;outline:none!important}
       dialog::backdrop{background:transparent!important}
       [data-p9run="${i}"]{visibility:visible!important;color:#000!important;fill:#000!important;stroke:none!important;opacity:1!important}`;
    document.documentElement.style.background = i === null ? "" : "#fff";
  };
  H.inkShared = async (a, b) => {
    const load = (u) => new Promise((ok, no) => { const im = new Image(); im.onload = () => ok(im); im.onerror = no; im.src = u; });
    const px = (im) => { const c = document.createElement("canvas"); c.width = im.width; c.height = im.height; const x = c.getContext("2d"); x.drawImage(im, 0, 0); return x.getImageData(0, 0, im.width, im.height).data; };
    const da = px(await load(a)), db = px(await load(b));
    let n = 0;
    for (let q = 0; q < da.length; q += 4) if (da[q] + da[q + 1] + da[q + 2] < 384 && db[q] + db[q + 1] + db[q + 2] < 384) n++;
    return n;
  };

  // ---- drivers -----------------------------------------------------------
  const frame = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const click = (el) => el && el.dispatchEvent(new MouseEvent("click", { bubbles: true, composed: true, cancelable: true }));
  const charts = () => [...root().querySelectorAll(".chartwrap svg")];
  const svgPx = (svg, vbX) => { const r = svg.getBoundingClientRect(); return r.left + (vbX / svg.viewBox.baseVal.width) * r.width; };
  const pe = (type, x, y, target) => (target || window).dispatchEvent(new PointerEvent(type, { bubbles: true, composed: true,
    cancelable: true, clientX: x, clientY: y, pointerId: 1, isPrimary: true, button: 0, buttons: type === "pointerup" ? 0 : 1 }));
  // Returns the steps whose target was not found: a driver that silently
  // missed would measure a state the grid claims and never reached.
  H.drive = async (steps) => {
    const c = card(), missed = [];
    let hover = null;
    for (const [op, a1, a2] of steps) {
      if (op === "cardClick") c._onCardClick({});
      else if (op === "open") c.dialog.open();
      else if (op === "stat") { const el = root().querySelector(`[data-stat='${a1}']`); if (el) click(el); else missed.push(`${op} ${a1}`); }
      else if (op === "chip") { const el = root().querySelector(`.chip[data-key='${a1}']`); if (el) el.click(); else missed.push(`${op} ${a1}`); }
      else if (op === "hover") {
        await frame();
        const svgs = charts(), svg = svgs[svgs.length - 1], plot = c._plot;
        if (!svg || !plot) { missed.push(op); continue; }
        const r = svg.getBoundingClientRect();
        hover = { x: svgPx(svg, plot.scaleX(plot.windowStart + a1 * 3600000)), y: r.top + r.height * 0.45 };
      }
      else if (op === "zoom") c.view.zoom(a1);
      else if (op === "hoverShared") {
        await frame();
        const svgs = charts(), svg = svgs[svgs.length - 1], plot = c._plot;
        const sp = c.hass.states["sensor.heat_pump_optimizer_plan_space_heating"].attributes.forecast;
        const dh = new Set(c.hass.states["sensor.heat_pump_optimizer_plan_dhw_heating"].attributes.forecast.filter((p) => Number(p.dhw_power) > 0.05).map((p) => p.t));
        const f = sp.find((p) => Number(p.space_power) > 0.05 && dh.has(p.t) && Date.parse(p.t) >= Date.now());
        if (!svg || !plot || !f) { missed.push(op); continue; }
        const r = svg.getBoundingClientRect();
        hover = { x: svgPx(svg, plot.scaleX(Date.parse(f.t) + 900000)), y: r.top + r.height * 0.45 };
      } else if (op === "armClear") {
        const hit = [...root().querySelectorAll(".setup-hit")].find((h) => h.dataset.key === "indoor_temp_entity");
        if (!hit) { missed.push(op); continue; }
        click(hit); await frame();
        const sel = root().querySelector(".setup-picker select");
        const save = root().querySelector(".sp-save");
        if (!sel || !save || ![...sel.options].some((o) => o.value === "")) { missed.push(`${op} picker`); continue; }
        sel.value = ""; sel.dispatchEvent(new Event("change", { bubbles: true, composed: true }));
        save.click(); await frame();
        if (!save.classList.contains("confirm")) missed.push(`${op} not armed`);
      }
      else if (op === "page") { c.dialog.page = a1; c._render(); }
      else if (op === "clickSel") { const el = root().querySelector(a1); if (el) el.click(); else missed.push(`${op} ${a1}`); await sleep(60); }
      else if (op === "lowerCeiling") {
        const st = JSON.parse(JSON.stringify(c.hass.states));
        for (const e of Object.values(st)) if (e.attributes && "dhw_min_temperature_max" in e.attributes) e.attributes.dhw_min_temperature_max = a1;
        c.hass = { ...c.hass, states: st };
      } else if (op === "dragDhw") {
        await frame();
        const svgs = charts(), svg = svgs[svgs.length - 1];
        const runs = c.manual.draft().dhw, [lo] = c.manual.bounds();
        const i = runs.findIndex((r) => r.end > lo && r.start >= lo);
        const hit = svg && [...svg.querySelectorAll("[data-channel='dhw'][data-index]")].find((e) => e.dataset.index === String(i) && !e.dataset.edge);
        if (!hit) { missed.push(op); continue; }
        const g = c.geomAt(svgs.length - 1);
        const xOf = (t) => svgPx(svg, g.plotL + ((t - g.windowStart) / (g.windowEnd - g.windowStart)) * g.plotW);
        const hr = hit.getBoundingClientRect(), y = (hr.top + hr.bottom) / 2;
        const x0 = xOf(runs[i].start + 60000), x1 = xOf(runs[i].start + 60000 + 3600000);
        pe("pointerdown", x0, y, hit); pe("pointermove", x1, y, window); pe("pointerup", x1, y, window);
      } else if (op === "menuAt") {
        const svgs = charts(), svg = svgs[svgs.length - 1], g = c.geomAt(svgs.length - 1);
        const t = g.windowStart + a2 * (g.windowEnd - g.windowStart);
        const x = svgPx(svg, g.plotL + a2 * g.plotW);
        const lane = svg.querySelector(`rect.lane[data-channel='${a1}']`) || svg.querySelector(`[data-channel='${a1}']`);
        if (!lane) { missed.push(`${op} ${a1}`); continue; }
        const lr = lane.getBoundingClientRect();
        c.lanes.openMenu(a1, t, x, (lr.top + lr.bottom) / 2, svg, false);
      } else if (op === "picker") {
        const hit = [...root().querySelectorAll(".setup-hit")].find((h) => h.dataset.key === "wood_tank_top_entity");
        if (!hit) { missed.push(op); continue; }
        click(hit); await frame();
        const box = root().querySelector(".sp-filter");
        if (!box) { missed.push(`${op} filter`); continue; }
        box.value = a1; box.dispatchEvent(new Event("input", { bubbles: true, composed: true }));
      } else missed.push(`unknown ${op}`);
      await frame();
    }
    await sleep(120); await frame();
    return { missed, hover };
  };
}

// ---- the host side -----------------------------------------------------------
export async function p9Grid({ browser, check, plan, cardSrc, log = () => {} }) {
  const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
  const states = gridStates(plan).filter((st) => !(process.env.P9_DROP || "").split(",").includes(st.name));
  // Contrast varies with theme, geometry with width and language: 7 cells per
  // state cover both axes (375 px light/dark in English; 3 widths x 2
  // languages in light), where the full product is 12.
  const cells = [];
  for (const vp of VIEWPORTS) for (const lang of ["en", "sv-SE"]) cells.push({ vp, lang, theme: "light" });
  cells.push({ vp: VIEWPORTS[0], lang: "en", theme: "dark" });
  if (process.env.P9_ONE) cells.splice(1);
  const PAGE = `<!doctype html><html><head><meta charset="utf-8"><style id="theme"></style></head><body></body></html>`;
  const bad = { contrast: [], overflow: [], overlap: [], small: [], popups: [], options: [], missed: [], threw: [] };
  const reach = {};
  let measuredRuns = 0, candidates = 0, unknown = 0, n = 0;
  const t0 = Date.now();
  for (const cell of cells) {
    const ctx = await browser.newContext({ viewport: { width: cell.vp[0], height: cell.vp[1] }, deviceScaleFactor: 2,
      // Reduced motion: the card drops its transitions, so every cell measures
      // an end state -- a fade caught half-way would be a flake, not a finding.
      colorScheme: cell.theme, reducedMotion: "reduce" });
    await ctx.clock.setFixedTime(FROZEN);
    await ctx.route("http://hpo.test/**", (r) => r.fulfill({ contentType: "text/html", body: PAGE }));
    const page = await ctx.newPage();
    for (const st of states) {
      const tag = `${st.name}/${cell.vp[0]}/${cell.theme}/${cell.lang}`;
      try {
        await page.goto("http://hpo.test/");
        await page.addScriptTag({ content: cardSrc });
        await page.addScriptTag({ content: `(${instrument.toString()})();` });
        await page.evaluate(([themeCss, w, cfg, states2, lang, svc]) => {
          document.getElementById("theme").textContent =
            `html{${themeCss};background:var(--primary-background-color)}` +
            `body{margin:0;padding:8px;font-family:"Liberation Sans",Arial,sans-serif;color:var(--primary-text-color)}` +
            `heatpump-optimizer-card{display:block;width:${w}px}`;
          if (!customElements.get("ha-card")) {
            customElements.define("ha-card", class extends HTMLElement {
              constructor() {
                super();
                this.attachShadow({ mode: "open" }).innerHTML =
                  "<style>:host{background:var(--ha-card-background,var(--card-background-color,white));" +
                  "color:var(--primary-text-color);box-sizing:border-box;border-radius:12px;" +
                  "border:1px solid var(--divider-color,#e0e0e0);display:block;position:relative;}</style><slot></slot>";
              }
            });
          }
          const c = document.createElement("heatpump-optimizer-card");
          c.setConfig({ type: "custom:heatpump-optimizer-card", ...cfg });
          const hass = { states: states2, language: lang };
          if (svc === "fail") hass.callService = async () => { throw new Error("Service call failed"); };
          else if (svc) hass.callService = async () => ({ response: { results: {}, applied: { space: { expires_at: new Date(Date.now() + 5 * 3600000).toISOString() } } } });
          c.hass = hass;
          document.body.appendChild(c);
        }, [THEMES[cell.theme], cell.vp[0] - 16, st.config, st.states, cell.lang, st.service]);
        await page.waitForTimeout(60);
        const { missed, hover } = await page.evaluate((s) => window.__p9.drive(s), st.steps);
        if (hover) { await page.mouse.move(hover.x, hover.y); await page.waitForTimeout(120); }
        for (const m of missed) bad.missed.push(`${tag}: ${m}`);
        if (process.env.P9_SHOT && process.env.P9_SHOT.split(",").includes(st.name)) await page.screenshot({ path: `${process.env.P9_SHOTDIR}/${st.name}.png` });
        const m = await page.evaluate((co) => window.__p9.measure(co), false);
        n += 1; measuredRuns += m.runs; unknown += m.unknownColour; candidates += m.boxPairs.length;
        for (const k of ["contrast", "overflow", "small", "popups", "options"]) for (const x of m[k]) bad[k].push(`${tag}: ${x}`.replace(/^([^/]*)\/[^:]*: /, process.env.P9_ONE ? "$1: " : "$&"));
        for (const [k, v] of Object.entries(await page.evaluate(() => window.__p9.colourRules()))) { if (v && !reach[k] && process.env.P9_ONE) log(`reach ${k} <- ${st.name}`); reach[k] = reach[k] || v; }
        for (const p of m.boxPairs) {
          const shots = [];
          for (const i of [p.a, p.b]) {
            await page.evaluate((k) => window.__p9.inkMode(k), i);
            shots.push("data:image/png;base64," + (await page.screenshot({ clip: p.clip })).toString("base64"));
          }
          await page.evaluate(() => window.__p9.inkMode(null));
          const shared = await page.evaluate(([a, b]) => window.__p9.inkShared(a, b), shots);
          if (shared > 0) bad.overlap.push(`${tag}: ${p.at} x ${p.bt} ${shared} px of shared ink`);
        }
      } catch (e) {
        bad.threw.push(`${tag}: ${String(e && e.message || e).slice(0, 160)}`);
      }
    }
    await ctx.close();
  }
  const unreached = Object.entries(reach).filter(([, v]) => !v).map(([k]) => k);
  const show = (xs) => `${xs.length}${xs.length ? ": " + [...new Set(xs.map((x) => x.replace(/^[^:]*: /, "")))].slice(0, process.env.P9_ONE ? 99 : 6).join(" | ") : ""}`;
  log(`P9 grid: ${n} cells, ${measuredRuns} text runs, ${candidates} box-intersecting pairs inked, ${Object.keys(reach).length} colour rules, ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  check("P9 grid: every cell mounted and every driver step found its target (the grid measured what it names)",
    bad.threw.length === 0 && bad.missed.length === 0 && n === cells.length * states.length && measuredRuns > 0,
    `threw ${show(bad.threw)}; missed ${show(bad.missed)}; cells ${n}/${cells.length * states.length}`);
  check("P9 grid: every card rule that sets a colour is rendered in some cell (no unmeasured colour)",
    unreached.length === 0 && Object.keys(reach).length > 0, `${unreached.length} unreached: ${unreached.join(" | ")}`);
  check("P9 grid: every visible text run clears WCAG AA against what is under it", bad.contrast.length === 0 && unknown === 0,
    `${show(bad.contrast)}; unparsed colours ${unknown}`);
  check("P9 grid: no two text runs share ink", bad.overlap.length === 0, show(bad.overlap));
  check("P9 grid: no pop-up leaves the viewport or its chart", bad.popups.length === 0, show(bad.popups));
  check("P9 grid: every listbox option reads differently from its siblings as shown", bad.options.length === 0, show(bad.options));
  check("P9 grid: no text is clipped where its ancestor cannot scroll to it", bad.overflow.length === 0, show(bad.overflow));
  check("P9 grid: every target clears 24 px or the 2.5.8 spacing exception", bad.small.length === 0, show(bad.small));
  return { bad, unreached, n };
}
