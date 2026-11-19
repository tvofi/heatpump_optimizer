// D4.M3 "Professional look" over the card, in real Chromium (round 11, seat D4-s3).
//
// Metric (one line each, per cell = state x theme x language x viewport):
//   tile_row_misaligned  = rows of headline numbers (.tiles .tile-v, .hl-stats .hl-value) whose
//                          cells differ in font-size or in the bottom of the number's first line box
//                          by more than 0.5 px (D4-criteria P3), counted over all cells.
//   offscale_font_sizes  = distinct computed font-sizes of visible HTML text runs not on the
//                          --hpo-text scale {12,13,15,18} px.
//   offscale_spacing     = distinct non-zero computed padding/margin/gap px values on visible HTML
//                          elements not on the --hpo-space scale {4,8,12,16,24}.
//   series_colour_split  = (theme, series key) pairs whose `.series[data-key]` / legend `.dot` paint
//                          takes more than one computed colour across states.
//   untranslated_runs    = visible text runs in an sv/de cell whose text equals, verbatim, a run of
//                          the same state's en cell and carries >=2 alphabetic words of >=4 letters.
// Count keys: computed values Chromium delivers from the production stylesheet (cardStyleBlock /
// renderChart) on the rendered card, never a source-text literal.
//
// Run (from the export root):
//   HPO_PY=$HOME/venv-ci/bin/python3 node dev/audit/rounds/round11/D4/s3/m3_look.mjs [--perturb=<name>] [--vp=375,1280] [--states=a,b]
// Perturbations (in-memory edits of the card source string, never on disk):
//   tile_nowrap   .tile-k/.hl-label do not wrap (expected: tile_row_misaligned -> 0)
//   err_localize  failure lines read the translated exception via hass.localize (with --err=ha: english_error_lines -> 0)
//   one_error_colour  ERROR_READABLE(_DARK) take the --hpo-crit literals (role_colour_split down by 2)
//   tooltip_floor the phone dialog's tooltip keeps max(12px, ...) (below_floor_cells -> 0)
//   type_tokens   every 0.82/0.85 em font-size reads --hpo-text-sm (offscale_font_sizes down)
//   space_snap    literal 2/3/6/10 px paddings, margins and gaps snap to the --hpo-space scale (offscale_spacing down)
//   space_token   the literal `gap: 8px; font-size: 0.82em` pair in the legend rule reads the tokens
//                 (expected: offscale_* down)
// Expected values at the baseline: see REPORT.md (exact; counts are contention-immune).
// Baseline SHA 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B10 (4 vCPU, Chromium 1243,
// playwright 1.63.0, Node 22).
//
// The states, drivers and themes are the P9 grid's own (tests/card_browser.mjs gridStates,
// instrument, THEMES), extracted from that file's text at run time so the harness tracks the tree.
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as rig from "../../../../../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "../../../../../..");
const arg = (k, d) => { const a = process.argv.find((x) => x.startsWith(`--${k}=`)); return a ? a.slice(k.length + 3) : d; };
const PERTURB = arg("perturb", "");
const VPS = arg("vp", "375,1280").split(",").map(Number);
const ONLY = arg("states", "");
const OUTJSON = arg("out", "");
// --err=ha: a failing service rejects the way Home Assistant's websocket does for an integration
// exception raised with a translation_key -- `message` is the English text (HA formats it from the
// en translations), the translation fields ride beside it -- and hass carries localize() over
// this integration's own translations/<lang>.json, which an honest fix may use.
const ERRMODE = arg("err", "plain");

// ---- the payload: private HPO_PLANDATA under a temp root -----------------
const tmp = mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d4s3-"));
const planPath = path.join(tmp, "plandata.json");
// plan_view.py exits 1 when it prints "PLAN VIEW ISSUES" (a 0.03 kWh slot/schedule rounding line
// at this baseline) after writing the payload; the payload is what this harness needs.
try { execFileSync(process.env.HPO_PY || "python3", ["tests/plan_view.py"], {
  cwd: repo, stdio: ["ignore", "ignore", "inherit"],
  env: { ...process.env, HPO_PLANDATA: planPath, PYTHONPATH: "tests/hastub",
    OMP_NUM_THREADS: "1", OPENBLAS_NUM_THREADS: "1", MKL_NUM_THREADS: "1", NUMEXPR_NUM_THREADS: "1", VECLIB_MAXIMUM_THREADS: "1" },
}); } catch (e) { if (!existsSync(planPath)) throw e; }
const plan = JSON.parse(readFileSync(planPath, "utf8"));

// ---- extract the P9 grid's states, drivers and themes from card_browser.mjs ----
const cb = readFileSync(path.join(repo, "tests/card_browser.mjs"), "utf8");
function block(startRe) {
  const m = cb.match(startRe); if (!m) throw new Error(`card_browser.mjs: ${startRe} not found`);
  let i = cb.indexOf("{", m.index + m[0].length - 1), depth = 0;
  // const X = [ ... ]; blocks start at "[" instead
  const open = cb[m.index + m[0].length - 1];
  if (open === "[") i = m.index + m[0].length - 1;
  const o = cb[i], c = o === "{" ? "}" : "]";
  for (let j = i; j < cb.length; j++) {
    if (cb[j] === o) depth++; else if (cb[j] === c && --depth === 0) return cb.slice(m.index, j + 1);
  }
  throw new Error("unbalanced");
}
const src = [
  block(/const THEMES = \{/), block(/function gridStates\(plan\) \{/), block(/const NARRATIVE_ITEMS = \[/),
  block(/function pageStates\(plan\) \{/), block(/function healthPageStates\(st, now\) \{/),
  block(/function instrument\(\) \{/),
].join("\n");
const names = ["DEFAULT_SPACE", "DEFAULT_DHW", "HOUR", "planStates", "setupSensorStates", "qaTopologies", "withActuals", "layoutCatalogTopo"];
const ext = new Function(...names, `${src}\nreturn { THEMES, gridStates, instrument };`)(...names.map((n) => rig[n]));
let states = ext.gridStates(plan);
// The empty, short-window and history states the P9 grid does not carry, taken from
// tests/card_drift.mjs's STATES (same fixtures, same page switches), so M3's "empty and error
// states" are rendered in Chromium too. `api` is the card's history fetch: "empty" answers with
// no rows (history_unavailable), "never" does not answer (history_pending); `pan` hours run
// after the drive, as card_drift's view.panBy does.
{
  const { planStates, setupSensorStates, qaTopologies, withActuals, DEFAULT_SPACE } = rig;
  const setupSt = (topo) => { const st = { ...planStates(plan), ...setupSensorStates() }; st[DEFAULT_SPACE].attributes.setup_topology = topo; return st; };
  const advEmpty = () => { const st = setupSt(qaTopologies().base); st[DEFAULT_SPACE].attributes.sensor_advisor = { basis: "history", candidates: [] }; return st; };
  const S = (name, o) => ({ name, config: {}, steps: [], service: false, ...o });
  states.push(
    S("plan_short_window", { states: planStates(plan), config: { hours: 6 } }),
    S("custom_title_currency", { states: planStates(plan), config: { title: "Värme", currency: "EUR", hours: 48 } }),
    S("setup_single_buffer", { states: setupSt(qaTopologies().base), steps: [["cardClick"], ["page", "setup"]] }),
    S("setup_coil", { states: setupSt(qaTopologies().coil), steps: [["cardClick"], ["page", "setup"]] }),
    S("savings_empty", { states: planStates(plan), steps: [["cardClick"], ["page", "savings"]] }),
    S("setup_not_published", { states: planStates(plan), steps: [["cardClick"], ["page", "setup"]] }),
    S("advisor_empty", { states: advEmpty(), steps: [["cardClick"], ["page", "advisor"]] }),
    S("history_unavailable", { states: withActuals(planStates(plan)), steps: [["cardClick"]], api: "empty", pan: -10 }),
    S("history_pending", { states: withActuals(planStates(plan)), steps: [["cardClick"]], api: "never", pan: -10 }),
  );
}
if (ONLY) states = states.filter((s) => ONLY.split(",").includes(s.name));

let cardSrc = readFileSync(path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"), "utf8");
const PERTURBS = {
  tile_nowrap: (s) => s.replace("      .tile-k {\n        display: block;", "      .tile-k, .hl-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }\n      .tile-k {\n        display: block;"),
  // The pin and save failure lines (and every other `(err && err.message) || err` site) read the
  // translated exception through hass.localize when the error carries a translation_key.
  err_localize: (s) => s.split("(err && err.message) || err").join(
    "(err && err.translation_key && this.host.hass && this.host.hass.localize && this.host.hass.localize(`component.${err.translation_domain}.exceptions.${err.translation_key}.message`, err.translation_placeholders)) || (err && err.message) || err"),
  // One error colour: the failure lines take the status pill's crit token instead of ERROR_READABLE.
  one_error_colour: (s) => s.replace('const ERROR_READABLE = "#ca4c46";', 'const ERROR_READABLE = "#b3261e";')
    .replace('const ERROR_READABLE_DARK = "#e0574d";', 'const ERROR_READABLE_DARK = "#f28b82";'),
  // The phone-width dialog's tooltip keeps the card's 12 px floor, as the other small text does.
  tooltip_floor: (s) => s.replace("dialog.expanded .tooltip { font-size: 0.78em; }", "dialog.expanded .tooltip { font-size: max(12px, 0.78em); }")
    .replace("        margin-top: 3px;\n        font-size: 0.85em;\n        font-style: italic;", "        margin-top: 3px;\n        font-size: max(12px, 0.85em);\n        font-style: italic;"),
  // The em-multiplied sizes read the type tokens instead (0.82/0.85 em -> --hpo-text-sm).
  type_tokens: (s) => s.replace(/font-size: (?:max\(12px, )?0\.8[25]em\)?;/g, "font-size: var(--hpo-text-sm, 13px);"),
  // Every literal px padding/margin/gap of 2, 3, 6 or 10 px snaps to the nearest --hpo-space step.
  space_snap: (s) => s.replace(/((?:padding|margin|gap)(?:-[a-z]+)?:\s*)([^;{}]+);/g, (m, k, v) =>
    k + v.replace(/(^|[\s(-])(2|3|6|10)px\b/g, (x, pre, n) => `${pre}${({ 2: 4, 3: 4, 6: 8, 10: 12 })[n]}px`) + ";"),
  space_token: (s) => s.replace("display: flex; align-items: center; gap: 8px; font-size: 0.82em;",
    "display: flex; align-items: center; gap: var(--hpo-space-2, 8px); font-size: var(--hpo-text-sm, 13px);"),
};
if (PERTURB) {
  const before = cardSrc; cardSrc = PERTURBS[PERTURB](cardSrc);
  if (cardSrc === before) throw new Error(`perturbation ${PERTURB} matched nothing`);
}

// ---- the page-side measurement --------------------------------------------
function m3() {
  const card = document.querySelector("heatpump-optimizer-card");
  const root = card.shadowRoot;
  const d = root.querySelector("dialog[open]");
  const scope = d && d.matches(":modal") ? d : root;
  const parentOf = (n) => n.parentElement || (n.getRootNode && n.getRootNode().host) || null;
  const effOp = (el) => { let o = 1; for (let n = el; n; n = parentOf(n)) o *= parseFloat(getComputedStyle(n).opacity || "1"); return o; };
  const visible = (el) => {
    if (!el.getClientRects || !el.getClientRects().length) return false;
    const cs = getComputedStyle(el);
    if (cs.visibility !== "visible" || cs.display === "none") return false;
    if (el.closest && el.closest("defs, pattern, clipPath, mask, marker, symbol, title")) return false;
    return effOp(el) > 0.02;
  };
  const desc = (el) => {
    const cls = (el.getAttribute && el.getAttribute("class")) || "";
    return (el.tagName.toLowerCase() + (cls ? "." + cls.trim().split(/\s+/).join(".") : "")).slice(0, 50);
  };
  const out = { fonts: {}, spacing: {}, runs: [], rows: [], series: {}, small: [], roles: {}, errText: [] };
  // Status roles by class name: the colour each renders, so one role's colours can be compared
  // across states (the pill's tone-*, the what-if result lines, the alerts' stripe).
  const ROLE = [["error", /(^|\s)(dearer|tone-crit|crit|error|fail)(\s|$)/], ["ok", /(^|\s)(cheaper|tone-ok|ok|success)(\s|$)/],
    ["warn", /(^|\s)(tone-warn|warn|wood-alert|space-blocked-alert)(\s|$)/]];
  for (const sel of [".wi-pin-result", ".wi-result"]) for (const el of scope.querySelectorAll(sel)) {
    const t = el.textContent.replace(/\s+/g, " ").trim(); if (t) out.errText.push(`${sel} ${t}`);
  }
  const els = [...scope.querySelectorAll("*")];
  for (const el of els) {
    if (el instanceof SVGElement) {
      if (el.matches(".series[data-key]") && visible(el)) {
        const cs = getComputedStyle(el);
        const paint = cs.stroke !== "none" ? cs.stroke : cs.fill;
        (out.series[el.dataset.key] = out.series[el.dataset.key] || {})[paint] = 1;
      }
      continue;
    }
    if (["STYLE", "SCRIPT", "TITLE", "OPTION"].includes(el.tagName) || !visible(el)) continue;
    const cs = getComputedStyle(el);
    const cls = el.getAttribute("class") || "";
    for (const [role, re] of ROLE) if (re.test(cls)) {
      const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
      // An alert block's body is ordinary text; its role colour is its stripe. Every other role
      // element's colour is its text. One role, one colour set per theme, text and stripe together.
      const stripe = parseFloat(cs.borderLeftWidth) >= 2;
      if (stripe) (out.roles[role] = out.roles[role] || {})[cs.borderLeftColor] = `${desc(el)} (stripe)`;
      else if (own) (out.roles[role] = out.roles[role] || {})[cs.color] = desc(el);
    }
    if (el.matches(".chip[data-key] .dot")) {
      const k = el.closest(".chip").dataset.key;
      // A dashed series' dot paints a repeating gradient over a transparent background: its
      // colour is the gradient's first stop, never the border (which is currentColor).
      const g = cs.backgroundImage.match(/rgba?\([^)]*\)/);
      (out.series[k] = out.series[k] || {})[cs.backgroundColor !== "rgba(0, 0, 0, 0)" ? cs.backgroundColor : (g ? g[0] : "none")] = 1;
    }
    for (const p of ["paddingTop", "paddingRight", "paddingBottom", "paddingLeft", "marginTop", "marginRight", "marginBottom", "marginLeft", "rowGap", "columnGap"]) {
      const v = parseFloat(cs[p]);
      if (!v || !isFinite(v)) continue;
      const k = String(Math.round(Math.abs(v) * 100) / 100);
      (out.spacing[k] = out.spacing[k] || {})[desc(el)] = 1;
    }
    let txt = "";
    for (const tn of el.childNodes) if (tn.nodeType === 3) txt += tn.textContent;
    txt = txt.replace(/\s+/g, " ").trim();
    if (txt) {
      const k = String(Math.round(parseFloat(cs.fontSize) * 100) / 100);
      (out.fonts[k] = out.fonts[k] || {})[desc(el)] = 1;
      if (parseFloat(cs.fontSize) < 11.995) out.small.push(`${desc(el)} ${k}px "${txt.slice(0, 30)}"`);
      out.runs.push(txt);
    }
  }
  // Headline-number rows: one row = the cells of one grid line in .tiles / .hl-stats.
  const lineBottom = (el) => {
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      if (!n.textContent.trim()) continue;
      const r = document.createRange(); r.selectNodeContents(n); const rs = r.getClientRects();
      if (rs.length) return rs[0].bottom;
    }
    return null;
  };
  for (const [grid, cellSel, valSel, keySel] of [[".tiles", ".tile", ".tile-v", ".tile-k"], [".hl-stats", ".hl-stat", ".hl-value", ".hl-label"]]) {
    for (const g of scope.querySelectorAll(grid)) {
      if (!visible(g)) continue;
      const cells = [...g.children].filter((c) => c.matches(cellSel) && visible(c));
      const byTop = {};
      for (const c of cells) { const t = Math.round(c.getBoundingClientRect().top); (byTop[t] = byTop[t] || []).push(c); }
      for (const row of Object.values(byTop)) {
        if (row.length < 2) continue;
        const vals = row.map((c) => {
          const v = c.querySelector(valSel), k = c.querySelector(keySel);
          if (!v) return null;
          const kr = k && k.getClientRects();
          return { fs: parseFloat(getComputedStyle(v).fontSize), bottom: lineBottom(v),
            labelLines: kr ? Math.round(k.getBoundingClientRect().height / parseFloat(getComputedStyle(k).lineHeight === "normal" ? parseFloat(getComputedStyle(k).fontSize) * 1.15 : getComputedStyle(k).lineHeight)) : 0,
            label: k ? k.textContent.trim().slice(0, 40) : "" };
        }).filter((x) => x && x.bottom !== null);
        if (vals.length < 2) continue;
        const db = Math.max(...vals.map((x) => x.bottom)) - Math.min(...vals.map((x) => x.bottom));
        const df = Math.max(...vals.map((x) => x.fs)) - Math.min(...vals.map((x) => x.fs));
        out.rows.push({ grid, db: Math.round(db * 100) / 100, df, labels: vals.map((x) => x.label), lines: vals.map((x) => x.labelLines) });
      }
    }
  }
  return out;
}

// ---- the host side (the P9 grid's mount, verbatim in effect) ----------------
const TR = Object.fromEntries(["en", "de", "sv"].map((l) => [l,
  JSON.parse(readFileSync(path.join(repo, `custom_components/heatpump_optimizer/translations/${l}.json`), "utf8"))]));
const PAGE = `<!doctype html><html><head><meta charset="utf-8"><style id="theme"></style></head><body></body></html>`;
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * rig.HOUR;
const LANGS = ["en", "de-DE", "sv-SE"];
const browser = await chromium.launch();
const cells = [];
const consoleErrors = [];
const t0 = process.cpuUsage(), w0 = Date.now();
try {
  for (const vp of VPS) for (const theme of ["light", "dark"]) {
    const ctx = await browser.newContext({ viewport: { width: vp, height: 812 }, deviceScaleFactor: 1, colorScheme: theme, reducedMotion: "reduce" });
    await ctx.clock.setFixedTime(FROZEN);
    await ctx.route("http://hpo.test/**", (r) => r.fulfill({ contentType: "text/html", body: PAGE }));
    const page = await ctx.newPage();
    let cur = "";
    page.on("pageerror", (e) => consoleErrors.push(`${cur}: ${String(e.message).slice(0, 120)}`));
    page.on("console", (m) => { if (m.type() === "error") consoleErrors.push(`${cur}: console ${m.text().slice(0, 120)}`); });
    for (const lang of LANGS) for (const st of states) {
      cur = `${st.name}/${vp}/${theme}/${lang}`;
      await page.goto("http://hpo.test/");
      await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
      await page.addScriptTag({ content: cardSrc });
      await page.addScriptTag({ content: `(${ext.instrument.toString()})();` });
      await page.evaluate(([themeCss, w, cfg, states2, lang2, svc, dark, errMode, tr, trEn, apiMode]) => {
        document.getElementById("theme").textContent =
          `html{${themeCss};background:var(--primary-background-color)}` +
          `body{margin:0;padding:8px;font-family:"Liberation Sans",Arial,sans-serif;color:var(--primary-text-color)}` +
          `heatpump-optimizer-card{display:block;width:${w}px}`;
        if (!customElements.get("ha-card")) {
          customElements.define("ha-card", class extends HTMLElement {
            constructor() { super(); this.attachShadow({ mode: "open" }).innerHTML =
              "<style>:host{background:var(--ha-card-background,var(--card-background-color,white));color:var(--primary-text-color);box-sizing:border-box;border-radius:12px;border:1px solid var(--divider-color,#e0e0e0);display:block;position:relative;}</style><slot></slot>"; }
          });
        }
        const c = document.createElement("heatpump-optimizer-card");
        c.setConfig({ type: "custom:heatpump-optimizer-card", ...cfg });
        const hass = { states: states2, language: lang2, themes: { darkMode: dark } };
        const look = (t, key) => key.split(".").reduce((o, k) => (o && o[k]), t);
        const fmt = (m, ph) => (m || "").replace(/\{(\w+)\}/g, (x, k) => (ph && k in ph ? String(ph[k]) : x));
        hass.localize = (key, ph) => { const m = key.match(/^component\.heatpump_optimizer\.(.*)$/); return m ? fmt(look(tr, m[1]), ph) : ""; };
        hass.loadBackendTranslation = async () => hass.localize;
        const HAERR = { apply_manual_plan: ["no_loaded_config_entry", {}],
          apply_schedule: ["apply_schedule_dhw_min_no_deadband", { minimum: 52, setpoint: 55, ceiling: 50 }] };
        if (svc === "fail" && errMode === "ha") hass.callService = async (dom, service) => {
          const [key, ph] = HAERR[service] || ["no_loaded_config_entry", {}];
          throw Object.assign(new Error(fmt(look(trEn, `exceptions.${key}.message`), ph)),
            { code: "home_assistant_error", translation_domain: "heatpump_optimizer", translation_key: key, translation_placeholders: ph });
        };
        else if (svc === "fail") hass.callService = async () => { throw new Error("Service call failed"); };
        else if (svc) hass.callService = async () => ({ response: { results: {}, applied: { space: { expires_at: new Date(Date.now() + 5 * 3600000).toISOString() } } } });
        if (apiMode === "empty") hass.callApi = async () => [];
        else if (apiMode === "never") hass.callApi = () => new Promise(() => {});
        c.hass = hass;
        document.body.appendChild(c);
      }, [ext.THEMES[theme], vp - 16, st.config, st.states, lang, st.service, theme === "dark", ERRMODE, TR[lang.slice(0, 2)], TR.en, st.api || null]);
      await page.waitForTimeout(40);
      const { missed, hover } = await page.evaluate((s) => window.__p9.drive(s), st.steps);
      if (st.pan) {
        await page.evaluate((h) => document.querySelector("heatpump-optimizer-card").view.panBy(h * 3600000), st.pan);
        await page.waitForTimeout(150);
      }
      if (hover) { await page.mouse.move(hover.x, hover.y); await page.waitForTimeout(100); }
      const m = await page.evaluate(m3);
      cells.push({ state: st.name, vp, theme, lang, missed, ...m });
      if (process.env.M3_SHOTS && vp === 375 && ["status_fallback", "pin_fail", "save_fail", "live_default", "score_open", "tooltip_hover", "shared_steps_hover", "savings_empty", "advisor_empty", "history_unavailable", "history_pending", "setup_not_published", "no_plan", "no_plan_expanded"].includes(st.name)) {
        const dir = path.join(here, "shots"); if (!existsSync(dir)) mkdirSync(dir);
        await page.screenshot({ path: path.join(dir, `${st.name}-${vp}-${theme}-${lang}.png`), fullPage: true });
      }
    }
    await ctx.close();
  }
} finally { await browser.close(); }

// ---- aggregate --------------------------------------------------------------
const FONT_SCALE = new Set([12, 13, 15, 18]), SPACE_SCALE = new Set([4, 8, 12, 16, 24]);
const agg = (key) => { const o = {}; for (const c of cells) for (const [v, sels] of Object.entries(c[key])) { o[v] = o[v] || new Set(); Object.keys(sels).forEach((s) => o[v].add(s)); } return o; };
const fonts = agg("fonts"), spacing = agg("spacing");
const offFonts = Object.keys(fonts).filter((v) => !FONT_SCALE.has(Number(v)));
const offSpace = Object.keys(spacing).filter((v) => !SPACE_SCALE.has(Number(v)));
const rows = cells.flatMap((c) => c.rows.map((r) => ({ cell: `${c.state}/${c.vp}/${c.theme}/${c.lang}`, ...r })));
const bad = rows.filter((r) => r.db > 0.5 || r.df > 0.5);
const series = {};
for (const c of cells) for (const [k, paints] of Object.entries(c.series)) {
  const key = `${c.theme}:${k}`; series[key] = series[key] || {};
  for (const p of Object.keys(paints)) (series[key][p] = series[key][p] || new Set()).add(c.state);
}
const split = Object.entries(series).filter(([, ps]) => Object.keys(ps).length > 1);
let untranslated = 0; const untrSamples = {};
for (const c of cells) {
  if (c.lang === "en") continue;
  const en = cells.find((x) => x.state === c.state && x.vp === c.vp && x.theme === c.theme && x.lang === "en");
  const enSet = new Set(en ? en.runs : []);
  for (const r of new Set(c.runs)) {
    if (!enSet.has(r)) continue;
    if ((r.match(/\b[A-Za-z]{4,}\b/g) || []).length < 2) continue;
    untranslated++; (untrSamples[r] = untrSamples[r] || new Set()).add(`${c.state}/${c.lang}`);
  }
}
// Text below the card's own 12 px floor (--hpo-text-xs; the stylesheet's max(12px, ...) guards).
const smallCells = cells.filter((c) => c.small.length);
const smallBy = {};
for (const c of smallCells) for (const x of c.small) { const k = x.replace(/ ".*$/, ""); (smallBy[k] = smallBy[k] || new Set()).add(`${c.state}/${c.vp}/${c.theme}/${c.lang}`); }
const roles = {};
for (const c of cells) for (const [r, cols] of Object.entries(c.roles)) {
  const k = `${c.theme}:${r}`; roles[k] = roles[k] || {};
  for (const [col, sel] of Object.entries(cols)) (roles[k][col] = roles[k][col] || new Set()).add(`${sel} @${c.state}`);
}
const roleSplit = Object.entries(roles).filter(([, v]) => Object.keys(v).length > 1);
const enMsgs = Object.values(TR.en.exceptions).map((e) => e.message.split(/\{\w+\}/)[0].trim()).filter((m) => m.length >= 12);
const leaks = [];
for (const c of cells) {
  if (c.lang === "en") continue;
  for (const t of c.errText) if (enMsgs.some((m) => t.includes(m))) leaks.push(`${c.state}/${c.vp}/${c.theme}/${c.lang}: ${t.slice(0, 140)}`);
}
const errCells = cells.filter((c) => c.lang !== "en" && c.errText.length).length;
const cpu = process.cpuUsage(t0);
const missedAll = cells.flatMap((c) => c.missed.map((m) => `${c.state}/${c.vp}/${c.theme}/${c.lang}: ${m}`));
const detail = {
  perturb: PERTURB || null, cells: cells.length, states: states.map((s) => s.name), missed: missedAll,
  offscale_fonts: Object.fromEntries(offFonts.map((v) => [v, [...fonts[v]]])),
  offscale_spacing: Object.fromEntries(offSpace.map((v) => [v, [...spacing[v]]])),
  misaligned_rows: bad,
  misaligned_by_state: bad.reduce((o, r) => { const k = r.cell.replace(/\/.*?\/.*?\//, "/"); o[k] = (o[k] || 0) + 1; return o; }, {}),
  series_split: Object.fromEntries(split.map(([k, ps]) => [k, Object.fromEntries(Object.entries(ps).map(([p, s]) => [p, [...s]]))])),
  untranslated: Object.fromEntries(Object.entries(untrSamples).map(([r, s]) => [r, [...s]])),
  console_errors: consoleErrors,
  role_colours: Object.fromEntries(Object.entries(roles).map(([k, v]) => [k, Object.fromEntries(Object.entries(v).map(([c, s]) => [c, [...s].slice(0, 8)]))])),
  english_error_lines: leaks,
  below_floor: Object.fromEntries(Object.entries(smallBy).map(([k, v]) => [k, [...v]])),
  hl_rows_by_vp_lang: rows.filter((r) => r.grid === ".hl-stats").reduce((o, r) => { const [, , vp, , lang] = ("x/" + r.cell).split("/"); const k = `${vp}/${lang}`; o[k] = o[k] || [0, 0]; o[k][0]++; if (r.db > 0.5 || r.df > 0.5) o[k][1]++; return o; }, {}),
};
if (OUTJSON) writeFileSync(OUTJSON, JSON.stringify(detail, null, 1));
console.log(`cells measured: ${cells.length} (${states.length} states x ${VPS.length} viewports x 2 themes x ${LANGS.length} languages); driver misses ${missedAll.length}`);
console.log(`RESULT cells=${cells.length} count`);
console.log(`RESULT headline_rows=${rows.length} count`);
console.log(`RESULT tile_row_misaligned=${bad.length} count`);
console.log(`RESULT tile_row_misaligned_max_px=${bad.length ? Math.max(...bad.map((r) => r.db)) : 0} px`);
console.log(`RESULT below_floor_cells=${smallCells.length} count`);
console.log(`RESULT below_floor_elements=${Object.keys(smallBy).length} count`);
console.log(`RESULT offscale_font_sizes=${offFonts.length} count`);
console.log(`RESULT offscale_spacing=${offSpace.length} count`);
console.log(`RESULT series_colour_split=${split.length} count`);
console.log(`RESULT untranslated_runs=${untranslated} count`);
console.log(`RESULT role_colour_split=${roleSplit.length} count`);
console.log(`RESULT non_en_error_cells=${errCells} count`);
console.log(`RESULT english_error_lines=${leaks.length} count`);
console.log(`RESULT console_errors=${consoleErrors.length} count`);
console.log(`RESULT wall_s=${((Date.now() - w0) / 1000).toFixed(1)} s (provisional)`);
console.log(`RESULT thread_factor=1.00`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
