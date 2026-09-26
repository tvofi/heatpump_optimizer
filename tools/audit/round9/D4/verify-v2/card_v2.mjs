// D4 round 9, verifier V2 (independent lens): the card findings D4-s1-01..05 measured with instruments
// written independently of tools/audit/round9/D4/s1 (own mount, real Playwright input, own metrics).
//
// Metric definitions (one line each; key of every count is the rendered DOM / pixels the production card delivers):
//   --check contrast (D4-s1-01)  status_runs_below_aa: (element, theme) pairs, reached by real clicks on the what-if Save
//                                button (arm, confirm-ok, confirm-fail), whose own text colour or own background resolves to
//                                --success/--error/--warning-color and whose WCAG 2.x ratio (own sRGB luminance formula,
//                                alpha-composited over the first opaque ancestor) is < 4.5 (text < 24 px, not bold >= 18.66 px).
//   --check menu (D4-s1-02)      menu_spill_px: max px the .slot-menu's right edge lies beyond min(viewport, .chartwrap right),
//                                menu opened by a REAL mouse click (tap) on the lane at fraction f of the plot width;
//                                menu_spill_cells: (viewport, lang, channel, f) cells with spill > 0.5 px.
//   --check picker (D4-s1-03)    identical_option_rows: pairs of options with different text in the open setup picker
//                                (<select size=8>, filter "vedpanna") whose screenshot crops are pixel-identical.
//   --check layout (D4-s1-04)    kbd_pipe_removals / kbd_box_moves: with the layout editor opened by a real click, Tab through
//                                every stop in the card; at each stop press Delete, Backspace, Enter, Space (pipe count =
//                                [data-edge] paths) and ArrowRight/ArrowDown (box rect moves); count stops that changed either.
//                                mouse_pipe_removals: pipes whose real mouse click at the path's midpoint removes one path.
//   --check now (D4-s1-05)       now_ink_overlap_px: pixels inked by BOTH text.now-label and text.now-temp (each rendered alone,
//                                screenshot diff against a blank of both), default view of withActuals(planStates) inline+expanded.
//
// Run from the repository root:
//   T=$(mktemp -d) && HPO_PLANDATA=$T/plandata.json PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
//     /home/claude/venv/bin/python tests/plan_view.py >/dev/null && \
//   HPO_PLANDATA=$T/plandata.json NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers \
//     node tools/audit/round9/D4/verify-v2/card_v2.mjs --check contrast|menu|picker|layout|now [--perturb]
// --perturb applies this harness's own in-memory one-line fix for the checked finding (see PERTURB below); every
// metric above must fall to 0 (layout: kbd_pipe_removals must rise).
// Expected (baseline, exact, counts/pixels contention-immune; first recorded 2026-09-26 on box G2-V2):
//   contrast status_runs_measured=8 status_runs_below_aa=6 (light 4, dark 2) min_status_ratio=1.96; --perturb -> 0
//   menu     menu_opened_by_real_tap=36 menu_spill_cells=4 menu_spill_px_max=54.3 menu_viewport_out_px_max=19.8 null_mid=0;
//            --perturb -> 0. (Arms: mid / last editable pixel / after two .vc-in zoom clicks at 97%; menu arm 'edge' at default
//            zoom never spills because the lane's last 25% is rect.lane-past, where a real tap opens no menu.)
//   picker   option_pairs_compared=18 identical_option_rows=4 (375/768 x en/sv) identical_option_rows_1280=0;
//            --perturb (id first) -> 2 (375 only); --perturb-css-wrap (the finder's CSS) -> 0
//   layout   pipes=12 boxes_seen=18 mouse_pipe_removals=10 tab_stops_in_canvas=18 kbd_pipe_removals=0 kbd_box_moves=0;
//            --perturb -> kbd_pipe_removals=12
//   now      now_cells_live=24 now_ink_overlap_cells=24 now_ink_overlap_px_max=88 null_no_actuals_ink_px=0; --perturb -> 0
// Debug: V2_DEBUG=1 prints per-row pixel differences (picker) and saves the select crop under the mkdtemp root.
// Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence). Machine: box G2-V2, 4-core Linux 6.18 container,
// Node v22.22.2, Playwright 1.56.1, Chromium (Playwright bundled), font Liberation Sans. Writes only under a mkdtemp root.
// Limits: no Home Assistant frontend; <ha-card> is a stand-in; HA default light/dark theme token values.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { planStates, setupSensorStates, qaTopologies, layoutCatalogTopo, withActuals, DEFAULT_SPACE, DEFAULT_DHW, HOUR }
  from "../../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const args = process.argv.slice(2);
const check = args[args.indexOf("--check") + 1];
const perturb = args.includes("--perturb");
const TMP = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d4v2-"));
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
const CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js";
const rep = (s, a, b) => { if (!s.includes(a)) throw new Error("anchor missing: " + a.slice(0, 70)); return s.split(a).join(b); };
// This harness's own fixes, one per check (not the finder's edits).
const PERTURB = {
  // status tokens -> readable text; confirm fill -> a dark red that clears 4.5:1 with white
  contrast: (s) => rep(rep(rep(rep(rep(s,
    "color: var(--success-color, #2fae7a);", "color: var(--primary-text-color);"),
    "color: var(--error-color, #e0544e);\n      }\n      @media", "color: var(--primary-text-color);\n      }\n      @media"),
    "color: var(--warning-color, #d98e00);", "color: var(--primary-text-color);"),
    "border-color: var(--error-color, #e0544e);\n        background: var(--error-color, #e0544e);\n      }",
    "border-color: #b3261e;\n        background: #b3261e;\n      }"),
    "border-color: var(--error-color, #e0544e) !important;\n        background: var(--error-color, #e0544e);",
    "border-color: #b3261e !important;\n        background: #b3261e;"),
  // clamp by translating with the measured width, a different one-liner from the finder's
  menu: (s) => rep(s, "    host.appendChild(menu);\n",
    "    host.appendChild(menu);\n    { const over = menu.getBoundingClientRect().right - host.getBoundingClientRect().right; if (over > 0) menu.style.left = `${Math.max(0, parseFloat(menu.style.left) - over)}px`; }\n"),
  // show the entity id FIRST so truncation keeps the distinguishing part (a markup fix, not the finder's CSS wrap)
  picker: (s) => s, // set below after inspecting the option template
  layout: (s) => rep(rep(s, '<path class="setup-pipe${extra}" data-edge="${edge}"', '<path class="setup-pipe${extra}" data-edge="${edge}" tabindex="0"'),
    '    canvas.addEventListener("click", this.onClick);\n',
    '    canvas.addEventListener("click", this.onClick);\n    canvas.addEventListener("keydown", (ev) => { if (ev.key === "Delete") this.onClick(ev); });\n'),
  now: (s) => rep(s, '`<text class="now-temp" x="${plotL + 6}" y="${plotT + font}"', '`<text class="now-temp" x="${plotL + 6}" y="${plotT + 2.4 * font}"'),
};
let src = fs.readFileSync(CARD, "utf8");
if (check === "picker") {
  // SetupPage.pickerModel label `${friendly} — ${id}` -> `${id} — ${friendly}`: the distinguishing id first.
  PERTURB.picker = (s) => rep(s, "return friendly === id ? id : `${friendly} — ${id}`;", "return friendly === id ? id : `${id} — ${friendly}`;");
}
// --perturb-css-wrap: the finder's CSS fix for D4-s1-03 (options wrap), to test whether it changes PIXELS, not only a model.
if (args.includes("--perturb-css-wrap")) src = rep(src, "      .sp-filter {\n        box-sizing: border-box; margin-bottom: 0.4em;",
  "      .sp-select option { white-space: normal; overflow-wrap: anywhere; }\n      .sp-filter {\n        box-sizing: border-box; margin-bottom: 0.4em;");
if (perturb) { const b = src; src = PERTURB[check](src); if (b === src) throw new Error("perturbation changed nothing"); }

const THEME = {
  light: { "--primary-color": "#03a9f4", "--accent-color": "#ff9800", "--primary-text-color": "#212121", "--secondary-text-color": "#727272",
    "--text-primary-color": "#ffffff", "--disabled-text-color": "#bdbdbd", "--primary-background-color": "#fafafa",
    "--secondary-background-color": "#e5e5e5", "--card-background-color": "#ffffff", "--divider-color": "rgba(0,0,0,.12)",
    "--error-color": "#db4437", "--warning-color": "#ffa600", "--success-color": "#43a047" },
  dark: { "--primary-color": "#03a9f4", "--accent-color": "#ff9800", "--primary-text-color": "#e1e1e1", "--secondary-text-color": "#9b9b9b",
    "--text-primary-color": "#ffffff", "--disabled-text-color": "#6f6f6f", "--primary-background-color": "#111111",
    "--secondary-background-color": "#282828", "--card-background-color": "#1c1c1c", "--divider-color": "rgba(225,225,225,.12)",
    "--error-color": "#db4437", "--warning-color": "#ffa600", "--success-color": "#43a047" },
};

const browser = await chromium.launch();
async function mount({ vp = [375, 812], theme = "light", lang = "en", states, config = {}, svc = null }) {
  const ctx = await browser.newContext({ viewport: { width: vp[0], height: vp[1] }, colorScheme: theme });
  await ctx.clock.setFixedTime(FROZEN);
  await ctx.route("http://v2.test/**", (r) => r.fulfill({ contentType: "text/html",
    body: `<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;padding:8px;font-family:'Liberation Sans'"></body></html>` }));
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e.message)));
  await page.goto("http://v2.test/");
  await page.addScriptTag({ content: src });
  await page.evaluate(({ vars, w, states, config, lang, svc }) => {
    for (const [k, v] of Object.entries(vars)) document.documentElement.style.setProperty(k, v);
    document.documentElement.style.background = "var(--primary-background-color)";
    document.body.style.color = "var(--primary-text-color)";
    customElements.define("ha-card", class extends HTMLElement { constructor() { super();
      this.attachShadow({ mode: "open" }).innerHTML = "<style>:host{display:block;background:var(--card-background-color);color:var(--primary-text-color);border-radius:12px}</style><slot></slot>"; } });
    const c = document.createElement("heatpump-optimizer-card");
    c.style.display = "block"; c.style.width = w + "px";
    c.setConfig({ type: "custom:heatpump-optimizer-card", ...config });
    const hass = { states, language: lang };
    if (svc === "ok") hass.callService = async () => ({ response: {} });
    if (svc === "fail") hass.callService = async () => { throw new Error("boom"); };
    c.hass = hass;
    document.body.appendChild(c);
    c.hass = hass;
  }, { vars: THEME[theme], w: vp[0] - 16, states, config, lang, svc });
  await page.waitForTimeout(150);
  return { ctx, page, errors };
}
const expand = async (page) => { await page.locator("heatpump-optimizer-card ha-card").first().click({ position: { x: 20, y: 12 } }); await page.waitForTimeout(250); };

// ---------- own WCAG computation, in page ----------
const CONTRAST_FN = `(() => {
  const parse = (s) => { const m = s.match(/rgba?\\(([^)]+)\\)/); if (!m) return null; const p = m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const over = (f, b) => ({ r: f.r * f.a + b.r * (1 - f.a), g: f.g * f.a + b.g * (1 - f.a), b: f.b * f.a + b.b * (1 - f.a), a: 1 });
  const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const L = (c) => 0.2126 * lin(c.r) + 0.7152 * lin(c.g) + 0.0722 * lin(c.b);
  const up = (el) => el.parentElement || (el.getRootNode() && el.getRootNode().host) || null;
  const bgOf = (el) => { const stack = []; for (let e = el; e; e = up(e)) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c.a > 0) { stack.push(c); if (c.a >= 1) break; } }
    let acc = parse(getComputedStyle(document.documentElement).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 }; if (acc.a < 1) acc = over(acc, { r: 255, g: 255, b: 255, a: 1 });
    for (let i = stack.length - 1; i >= 0; i--) acc = over(stack[i], acc); return acc; };
  return (el) => { const cs = getComputedStyle(el); const bg = bgOf(el); const fg = over(parse(cs.color), bg); const a = L(fg), b = L(bg);
    return { ratio: (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05), fg: cs.color, bg: \`rgb(\${Math.round(bg.r)},\${Math.round(bg.g)},\${Math.round(bg.b)})\`, px: parseFloat(cs.fontSize), w: +cs.fontWeight, ownBg: cs.backgroundColor }; };
})()`;

const out = [];
const R = (k, v, u = "count") => out.push(`RESULT ${k}=${v} ${u}`);

async function runContrast() {
  const st = planStates(plan);
  st[DEFAULT_SPACE].attributes.day_start_hour = 7; st[DEFAULT_SPACE].attributes.day_end_hour = 22;
  st[DEFAULT_DHW].attributes.dhw_windows = "06:00-08:30, 17:00-22:00";
  for (const id of [DEFAULT_SPACE, DEFAULT_DHW]) { st[id].attributes.dhw_min_temperature = 55; st[id].attributes.dhw_min_temperature_max = 60; }
  const rows = [];
  for (const theme of ["light", "dark"]) {
    const tok = THEME[theme];
    const hex = (h) => { const n = parseInt(h.slice(1), 16); return `rgb(${n >> 16}, ${(n >> 8) & 255}, ${n & 255})`; };
    const status = new Set([hex(tok["--error-color"]), hex(tok["--success-color"]), hex(tok["--warning-color"])]);
    for (const [label, svc, clicks] of [["confirm_armed", "ok", 1], ["saved_ok", "ok", 2], ["save_failed", "fail", 2], ["dhw_clamped", "ok", 0]]) {
      const { ctx, page, errors } = await mount({ vp: [1280, 800], theme, states: st, config: { what_if: true }, svc });
      await expand(page);
      const save = page.locator("heatpump-optimizer-card .wi-save").first();
      if (!(await save.count())) { rows.push({ theme, label, missing: true }); await ctx.close(); continue; }
      for (let i = 0; i < clicks; i++) { await save.click(); await page.waitForTimeout(120); }
      if (label === "dhw_clamped") {
        // a hass push lowering the DHW-minimum ceiling below the stored 55 degC (the clamped-warning path)
        await page.evaluate(() => { const c = document.querySelector("heatpump-optimizer-card"); const st = JSON.parse(JSON.stringify(c.hass.states));
          for (const e of Object.values(st)) if (e.attributes && "dhw_min_temperature_max" in e.attributes) e.attributes.dhw_min_temperature_max = 50;
          c.hass = { ...c.hass, states: st }; });
        await page.waitForTimeout(150);
      }
      const found = await page.evaluate(({ fn, status }) => {
        const ratio = eval(fn); const status2 = new Set(status); const res = [];
        const root = document.querySelector("heatpump-optimizer-card").shadowRoot;
        // every run of the four status classes, whatever its colour (so a fix that recolours them is still measured)
        for (const el of root.querySelectorAll(".wi-save.confirm, .wi-result.cheaper, .wi-result.dearer, .wi-warn, b.cheaper, b.dearer")) {
          const txt = (el.textContent || "").trim(); const r = el.getBoundingClientRect();
          if (!txt || r.width < 1 || r.height < 1) continue;
          const cs = getComputedStyle(el);
          const m = ratio(el); const large = m.px >= 24 || (m.w >= 700 && m.px >= 18.66);
          res.push({ statusToken: status2.has(cs.color) || status2.has(cs.backgroundColor), el: el.tagName.toLowerCase() + "." + el.className.replace(/\s+/g, "."), txt: txt.slice(0, 40), ratio: +m.ratio.toFixed(2), need: large ? 3 : 4.5, fg: m.fg, bg: m.bg });
        }
        return res;
      }, { fn: CONTRAST_FN, status: [...status] });
      for (const f of found) rows.push({ theme, label, ...f });
      if (errors.length) rows.push({ theme, label, pageerror: errors[0] });
      await ctx.close();
    }
  }
  for (const r of rows) console.log(JSON.stringify(r));
  const below = rows.filter((r) => r.ratio !== undefined && r.ratio < r.need);
  R("status_runs_measured", rows.filter((r) => r.ratio !== undefined).length);
  R("status_runs_below_aa", below.length);
  R("status_runs_below_aa_light", below.filter((r) => r.theme === "light").length);
  R("status_runs_below_aa_dark", below.filter((r) => r.theme === "dark").length);
  R("min_status_ratio", Math.min(...below.map((r) => r.ratio), 99), "ratio");
}

async function runMenu() {
  // Arms per (viewport, lang, channel): "mid" = tap at 50% of the lane (null control); "edge" = tap on the last editable
  // pixel of the lane (2 px left of rect.lane-past, the non-editable tail); "zoomed" = after two real clicks on the
  // zoom-in control (.vc-in), tap at 97% of the lane if that pixel is editable. All taps are real mouse down/up.
  let cells = 0, spillCells = 0, maxSpill = 0, vpSpillMax = 0, opened = 0, nullSpill = 0;
  for (const vp of [[375, 812], [768, 1024], [1280, 800]]) for (const lang of ["en", "sv-SE"]) for (const ch of ["space", "dhw"]) for (const arm of ["mid", "edge", "zoomed"]) {
    const { ctx, page } = await mount({ vp, lang, states: planStates(plan), config: { what_if: true } });
    await expand(page);
    if (arm === "zoomed") for (let i = 0; i < 2; i++) { const z = page.locator("heatpump-optimizer-card dialog[open] .vc-in").first(); if (await z.count()) { await z.click(); await page.waitForTimeout(150); } }
    const box = await page.evaluate(({ ch }) => {
      const root = document.querySelector("heatpump-optimizer-card").shadowRoot;
      const svgs = [...root.querySelectorAll("dialog[open] .chartwrap svg")]; const svg = svgs[svgs.length - 1]; if (!svg) return null;
      const lane = svg.querySelector(`rect.lane[data-channel='${ch}']`); if (!lane) return null;
      const r = lane.getBoundingClientRect();
      const past = [...svg.querySelectorAll("rect.lane-past")].map((p) => p.getBoundingClientRect()).filter((p) => p.top < r.bottom && p.bottom > r.top && p.left > r.left + 1);
      return { l: r.left, r: r.right, t: r.top, b: r.bottom, pastL: past.length ? Math.min(...past.map((p) => p.left)) : null };
    }, { ch });
    cells++;
    if (!box) { console.log(`no lane ${vp[0]} ${lang} ${ch} ${arm}`); await ctx.close(); continue; }
    const x = arm === "mid" ? box.l + 0.5 * (box.r - box.l) : arm === "edge" ? (box.pastL !== null ? box.pastL - 2 : box.r - 2) : box.l + 0.97 * (box.r - box.l);
    const y = (box.t + box.b) / 2;
    await page.mouse.move(x, y); await page.mouse.down(); await page.mouse.up(); await page.waitForTimeout(150);
    const m = await page.evaluate(() => {
      const root = document.querySelector("heatpump-optimizer-card").shadowRoot;
      const menu = root.querySelector(".slot-menu"); if (!menu) return null;
      const r = menu.getBoundingClientRect(); const wrap = menu.closest(".chartwrap") || menu.parentElement; const w = wrap.getBoundingClientRect();
      const b = menu.querySelector("button");
      return { right: r.right, width: r.width, wrapRight: w.right, vw: document.documentElement.clientWidth, txt: b ? b.textContent : "", btnH: b ? b.getBoundingClientRect().height : 0 };
    });
    if (!m) {
      const hitEl = await page.evaluate(({ x, y }) => { const e = document.querySelector("heatpump-optimizer-card").shadowRoot.elementFromPoint(x, y);
        return e ? e.tagName + "." + (e.getAttribute("class") || "") : "none"; }, { x, y });
      console.log(`no menu ${vp[0]} ${lang} ${ch} ${arm} x=${x.toFixed(0)}: topmost=${hitEl} lane=${box.l.toFixed(0)}..${box.r.toFixed(0)} pastL=${box.pastL}`);
    }
    await ctx.close();
    if (!m) continue;
    opened++;
    const spill = Math.max(0, m.right - Math.min(m.vw, m.wrapRight));
    const vpOut = Math.max(0, m.right - m.vw);
    console.log(`menu ${vp[0]} ${lang} ${ch} ${arm} x=${x.toFixed(0)}: menuW=${m.width.toFixed(1)} btnH=${m.btnH.toFixed(1)} chartOut=${(m.right - m.wrapRight).toFixed(1)} vpOut=${vpOut.toFixed(1)} "${m.txt}"`);
    if (arm === "mid") { nullSpill += spill > 0.5 ? 1 : 0; continue; }
    if (spill > 0.5) spillCells++;
    maxSpill = Math.max(maxSpill, spill); vpSpillMax = Math.max(vpSpillMax, vpOut);
  }
  R("menu_cells", cells); R("menu_opened_by_real_tap", opened); R("menu_spill_cells", spillCells);
  R("menu_spill_px_max", maxSpill.toFixed(1), "px"); R("menu_viewport_out_px_max", vpSpillMax.toFixed(1), "px");
  R("null_mid_spill_cells", nullSpill);
}

async function runPicker() {
  const big = {};
  for (let i = 0; i < 40; i++) big[`sensor.zz_probe_${i}`] = { state: "20", attributes: { unit_of_measurement: "°C", friendly_name: `Probe ${i}` } };
  big["sensor.vedpanna_temperatur_temperature"] = { state: "71.2", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  big["sensor.vedpanna_temperatur_temperature_2"] = { state: "48.9", attributes: { unit_of_measurement: "°C", friendly_name: "Vedpanna temperatur" } };
  let identical = 0, pairs = 0; const perVp = {};
  for (const vp of [[375, 812], [768, 1024], [1280, 800]]) for (const lang of ["en", "sv-SE"]) {
    const st = { ...planStates(plan), ...setupSensorStates(), ...big };
    st[DEFAULT_SPACE].attributes.setup_topology = qaTopologies().base;
    const { ctx, page } = await mount({ vp, lang, states: st });
    await expand(page);
    await page.locator("heatpump-optimizer-card [role=tab][data-page=setup]").first().click();
    await page.waitForTimeout(200);
    const hit = page.locator("heatpump-optimizer-card .setup-hit[data-key=wood_tank_top_entity]").first();
    if (!(await hit.count())) { console.log(`no wood_tank_top hit at ${vp[0]} ${lang}`); await ctx.close(); continue; }
    await hit.click({ force: true }); await page.waitForTimeout(150);
    await page.locator("heatpump-optimizer-card .sp-filter").first().fill("vedpanna"); await page.waitForTimeout(250);
    const sel = page.locator("heatpump-optimizer-card .sp-select").first();
    await sel.evaluate((s) => { s.selectedIndex = -1; s.blur(); });
    const opts = await sel.evaluate((s) => [...s.options].map((o, i) => { const r = o.getBoundingClientRect(); return { i, t: o.textContent, x: r.left, y: r.top, w: r.width, h: r.height }; }));
    const sr = await sel.boundingBox();
    const shot = await page.screenshot({ clip: sr });
    // crop rows from the element screenshot by decoding via the browser (no extra npm deps)
    // rows cropped from the select's screenshot (whole select width), 1 px padded; compared with a +-1 px vertical search
    // because the option boxes sit at fractional y. "identical" = fewer than 8 pixels differ by > 40 (sum |dRGB|) at the best shift (one glyph is >= 20 such pixels).
    const rows = await page.evaluate(async ({ b64, opts, sr }) => {
      const img = new Image(); img.src = "data:image/png;base64," + b64; await img.decode();
      const cv = document.createElement("canvas"); cv.width = img.width; cv.height = img.height; const g = cv.getContext("2d"); g.drawImage(img, 0, 0);
      return opts.map((o) => { const y = Math.floor(o.y - sr.y) - 1, h = Math.ceil(o.h) + 2; if (y < 0 || y + h > img.height) return null;
        return { w: img.width, h, d: Array.from(g.getImageData(0, y, img.width, h).data) }; });
    }, { b64: shot.toString("base64"), opts, sr });
    const diffPx = (A, B) => { let best = 1e9;
      for (const dy of [-1, 0, 1]) { let bad = 0, n = 0;
        for (let y = 1; y < A.h - 1; y++) for (let x = 0; x < A.w; x++) { const yb = y + dy; if (yb < 0 || yb >= B.h) continue; const i = (y * A.w + x) * 4, j = (yb * B.w + x) * 4;
          n++; if (Math.abs(A.d[i] - B.d[j]) + Math.abs(A.d[i + 1] - B.d[j + 1]) + Math.abs(A.d[i + 2] - B.d[j + 2]) > 40) bad++; }
        best = Math.min(best, bad); }
      return best; };
    const same = (A, B) => !!A && !!B && diffPx(A, B) < 8;
    let id = 0, pr = 0;
    for (let a = 0; a < opts.length; a++) for (let b = a + 1; b < opts.length; b++) {
      if (opts[a].t === opts[b].t || !rows[a] || !rows[b]) continue;
      pr++; if (process.env.V2_DEBUG) console.log(`diffPx ${vp[0]} ${lang} ${a}-${b}: ${diffPx(rows[a], rows[b])}`); if (same(rows[a], rows[b])) { id++; console.log(`identical rows ${vp[0]} ${lang}: "${opts[a].t}" | "${opts[b].t}" selectW=${sr.width.toFixed(0)}`); }
    }
    perVp[`${vp[0]}_${lang}`] = `${id}/${pr} opts=${opts.length}`;
    if (process.env.V2_DEBUG) { console.log(vp[0], lang, JSON.stringify(opts), 'rows', JSON.stringify(sr)); fs.writeFileSync(path.join(TMP, `sel_${vp[0]}_${lang}.png`), shot); console.log(TMP); }
    identical += id; pairs += pr;
    await ctx.close();
  }
  console.log(JSON.stringify(perVp));
  R("option_pairs_compared", pairs); R("identical_option_rows", identical);
  R("identical_option_rows_1280", Object.entries(perVp).filter(([k]) => k.startsWith("1280")).reduce((a, [, v]) => a + +v.split("/")[0], 0));
}

async function runLayout() {
  let boxesSeen = 0, kbdPipe = 0, kbdBox = 0, mousePipe = 0, pipesTotal = 0, stopsTotal = 0, canvasStops = 0;
  for (const vp of [[375, 812], [768, 1024], [1280, 800]]) {
    const st = { ...planStates(plan), ...setupSensorStates() };
    st[DEFAULT_SPACE].attributes.setup_topology = layoutCatalogTopo();
    const open = async () => {
      const m = await mount({ vp, states: st });
      await expand(m.page);
      await m.page.locator("heatpump-optimizer-card [role=tab][data-page=setup]").first().click(); await m.page.waitForTimeout(150);
      await m.page.locator("heatpump-optimizer-card .layout-edit-toggle").first().click(); await m.page.waitForTimeout(150);
      return m;
    };
    const snap = (page) => page.evaluate(() => {
      const root = document.querySelector("heatpump-optimizer-card").shadowRoot; const cv = root.querySelector(".setup-canvas");
      if (!cv) return null;
      // box positions in the canvas's own SVG units (x/y attributes of rect.setup-box): scroll-invariant
      const boxes = [...cv.querySelectorAll("rect.setup-box")].map((b) => `${b.getAttribute("x")},${b.getAttribute("y")}`).join("|");
      return { pipes: cv.querySelectorAll("[data-edge]").length, boxes };
    });
    // mouse control: click each pipe midpoint on a fresh mount
    let m = await open();
    const s0 = await snap(m.page); if (!s0) { console.log("no .setup-canvas at", vp[0]); await m.ctx.close(); continue; }
    pipesTotal += s0.pipes; boxesSeen += s0.boxes ? s0.boxes.split("|").length : 0;
    const mids = await m.page.evaluate(() => [...document.querySelector("heatpump-optimizer-card").shadowRoot.querySelectorAll(".setup-canvas [data-edge]")].map((p) => {
      const L = p.getTotalLength(); const q = p.getPointAtLength(L / 2); const pt = new DOMPoint(q.x, q.y).matrixTransform(p.getScreenCTM()); return { e: p.dataset.edge, x: pt.x, y: pt.y }; }));
    await m.ctx.close();
    for (const mid of mids) {
      m = await open();
      await m.page.mouse.click(mid.x, mid.y); await m.page.waitForTimeout(120);
      const s1 = await snap(m.page); if (s1 && s1.pipes < s0.pipes) mousePipe++;
      await m.ctx.close();
    }
    // keyboard: every Tab stop inside the card, try keys
    m = await open();
    const stops = [];
    for (let i = 0; i < 120; i++) {
      await m.page.keyboard.press("Tab");
      const a = await m.page.evaluate(() => { const c = document.querySelector("heatpump-optimizer-card"); let a = c.shadowRoot.activeElement; if (!a) return null;
        return { sig: a.tagName + "." + (a.getAttribute("class") || "") + "#" + (a.dataset.edge || a.dataset.key || a.textContent.slice(0, 20)), inCanvas: !!a.closest(".setup-canvas") }; });
      if (!a) continue; if (stops.length && a.sig === stops[0].sig) break; if (!stops.some((s) => s.sig === a.sig)) stops.push({ ...a, idx: i });
    }
    await m.ctx.close();
    stopsTotal += stops.length; canvasStops += stops.filter((s) => s.inCanvas).length;
    for (const s of stops) {
      for (const keys of [["Delete", "Backspace", "Enter", "Space"], ["ArrowRight", "ArrowDown"]]) {
        m = await open();
        let reached = false;
        for (let i = 0; i <= s.idx + 1; i++) { await m.page.keyboard.press("Tab");
          const sig = await m.page.evaluate(() => { const a = document.querySelector("heatpump-optimizer-card").shadowRoot.activeElement; return a ? a.tagName + "." + (a.getAttribute("class") || "") + "#" + (a.dataset.edge || a.dataset.key || a.textContent.slice(0, 20)) : null; });
          if (sig === s.sig) { reached = true; break; } }
        if (!reached) { await m.ctx.close(); continue; }
        const b = await snap(m.page);
        // do not press Enter/Space on Save/Undo/Tidy/toggle: they are the editor's own buttons, not a pipe/box route
        if (/layout-(save|undo|tidy|edit-toggle)|BUTTON/.test(s.sig) && !s.inCanvas) { await m.ctx.close(); continue; }
        for (const k of keys) { await m.page.keyboard.press(k); await m.page.waitForTimeout(60); }
        const a2 = await snap(m.page);
        if (b && a2 && keys[0] === "Delete" && a2.pipes < b.pipes) kbdPipe++;
        if (b && a2 && keys[0] === "ArrowRight" && a2.boxes !== b.boxes) { kbdBox++; console.log(`box moved from stop ${s.sig}`); }
        if (b && a2 && keys[0] === "Delete" && a2.pipes < b.pipes) console.log(`pipe removed from stop ${s.sig}`);
        await m.ctx.close();
      }
    }
    console.log(`vp ${vp[0]}: pipes=${s0.pipes} stops=${stops.length} canvasStops=${stops.filter((x) => x.inCanvas).length} seq=${stops.map((x) => x.sig).join(" > ").slice(0, 400)}`);
  }
  R("boxes_seen", boxesSeen); R("pipes", pipesTotal); R("mouse_pipe_removals", mousePipe); R("tab_stops", stopsTotal); R("tab_stops_in_canvas", canvasStops);
  R("kbd_pipe_removals", kbdPipe); R("kbd_box_moves", kbdBox);
}

async function runNow() {
  let cells = 0, overlapCells = 0, maxInk = 0, nullInk = 0;
  for (const vp of [[375, 812], [768, 1024], [1280, 800]]) for (const theme of ["light", "dark"]) for (const lang of ["en", "sv-SE"]) for (const [mode, sts] of [["live", withActuals(planStates(plan))], ["null_no_actuals", planStates(plan)]]) for (const exp of [false, true]) {
    const { ctx, page } = await mount({ vp, theme, lang, states: sts });
    if (exp) await expand(page);
    const svgSel = exp ? "dialog[open] .chartwrap svg" : ".chartwrap svg";
    const info = await page.evaluate((sel) => {
      const root = document.querySelector("heatpump-optimizer-card").shadowRoot; const svg = [...root.querySelectorAll(sel)].pop(); if (!svg) return null;
      const a = svg.querySelector("text.now-label"), b = svg.querySelector("text.now-temp");
      const rr = (e) => { if (!e) return null; const r = e.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; };
      return { a: rr(a), b: rr(b), bt: b ? b.textContent : null };
    }, svgSel);
    cells++;
    if (!info || !info.a || !info.b) { if (mode !== "live") { /* null arm: no now-temp drawn */ } await ctx.close(); continue; }
    const x0 = Math.floor(Math.min(info.a.x, info.b.x)) - 2, y0 = Math.floor(Math.min(info.a.y, info.b.y)) - 2;
    const x1 = Math.ceil(Math.max(info.a.x + info.a.w, info.b.x + info.b.w)) + 2, y1 = Math.ceil(Math.max(info.a.y + info.a.h, info.b.y + info.b.h)) + 2;
    const clip = { x: x0, y: y0, width: x1 - x0, height: y1 - y0 };
    const vis = (which) => page.evaluate(({ sel, which }) => { const svg = [...document.querySelector("heatpump-optimizer-card").shadowRoot.querySelectorAll(sel)].pop();
      svg.querySelector("text.now-label").style.visibility = which.includes("a") ? "visible" : "hidden"; svg.querySelector("text.now-temp").style.visibility = which.includes("b") ? "visible" : "hidden"; }, { sel: svgSel, which });
    const grab = async () => page.evaluate(async (b64) => { const img = new Image(); img.src = "data:image/png;base64," + b64; await img.decode();
      const cv = document.createElement("canvas"); cv.width = img.width; cv.height = img.height; const g = cv.getContext("2d"); g.drawImage(img, 0, 0); return Array.from(g.getImageData(0, 0, img.width, img.height).data); }, (await page.screenshot({ clip })).toString("base64"));
    await vis(""); const none = await grab(); await vis("a"); const onlyA = await grab(); await vis("b"); const onlyB = await grab(); await vis("ab");
    let both = 0;
    for (let i = 0; i < none.length; i += 4) {
      const dA = Math.abs(onlyA[i] - none[i]) + Math.abs(onlyA[i + 1] - none[i + 1]) + Math.abs(onlyA[i + 2] - none[i + 2]);
      const dB = Math.abs(onlyB[i] - none[i]) + Math.abs(onlyB[i + 1] - none[i + 1]) + Math.abs(onlyB[i + 2] - none[i + 2]);
      if (dA > 60 && dB > 60) both++;
    }
    if (mode === "live") { if (both > 0) overlapCells++; maxInk = Math.max(maxInk, both); }
    else nullInk += both;
    if (mode === "live" && vp[0] === 375 && theme === "light" && lang === "en") console.log(`375 light en expanded=${exp}: label@${info.a.x.toFixed(1)},${info.a.y.toFixed(1)} ${info.a.w.toFixed(1)}x${info.a.h.toFixed(1)} temp@${info.b.x.toFixed(1)},${info.b.y.toFixed(1)} ${info.b.w.toFixed(1)}x${info.b.h.toFixed(1)} "${info.bt}" ink_both=${both}`);
    await ctx.close();
  }
  R("now_cells_live", cells / 2); R("now_ink_overlap_cells", overlapCells); R("now_ink_overlap_px_max", maxInk, "px"); R("null_no_actuals_ink_px", nullInk, "px");
}

try {
  if (check === "contrast") await runContrast();
  else if (check === "menu") await runMenu();
  else if (check === "picker") await runPicker();
  else if (check === "layout") await runLayout();
  else if (check === "now") await runNow();
  else throw new Error("--check contrast|menu|picker|layout|now");
} finally { await browser.close(); }
console.log(`perturb=${perturb}`);
for (const l of out) console.log(l);
console.log("RESULT thread_factor=1.00");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
const vm = fs.readFileSync("/proc/vmstat", "utf8").match(/pswpin (\d+)/);
console.log(`RESULT swapins=${vm ? vm[1] : 0}`);
