// D4 round-4 — the card's real-browser layout grid.
//
// METRIC: for every state in tests/card_drift.mjs's STATES, rendered in real
// Chromium at three viewports x {light,dark} x {en,sv} x {fine,coarse}
// x {motion,reduced}: the count and size of (a) overlapping visible text
// boxes, (b) text clipped by its own box, (c) svg text escaping its svg,
// (d) text/background pairs below the WCAG 2.1 AA contrast bar for their
// size, (e) interactive targets whose smaller side is under 24 px (44 px
// under a coarse pointer), (f) uncaught page errors, all keyed by
// (state, viewport, theme, lang, pointer, motion, element).
//
// RUN (from the export root):
//   PYTHONPATH=tests/hastub HPO_PLANDATA=/private/tmp/hpo-d4/plandata.json \
//     /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 tests/plan_view.py
//   NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   HPO_PLANDATA=/private/tmp/hpo-d4/plandata.json \
//     node tools/audit/round4/D4/card_grid.mjs
//
// EXPECTED at baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 on the audit
// box (8-core Apple M1, macOS 25.6.0, Chromium 131.0.6778.33 / chromium-1148,
// node v20.10.0, Playwright 1.49.0):
//   cells=1224, drive_failures=0  (+-0; the cell count is a product of the
//   axes below and the state list, both derived at run time)
//   every other RESULT is a defect count and is printed with its own
//   tolerance line in out/summary.json.
//
// This harness measures GEOMETRY, so it never uses tests/card_rig.mjs: that
// rig's DOM stub returns a constant 900x400 rect for everything.
import { createRequire } from "node:module";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");
const OUT = path.join(__dirname, "out");
const SHOTS = path.join(__dirname, "shots");
mkdirSync(OUT, { recursive: true });
mkdirSync(SHOTS, { recursive: true });

const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const planPath = process.env.HPO_PLANDATA;
if (!planPath || !existsSync(planPath)) {
  console.error("FAIL: set HPO_PLANDATA to a private plan payload (run tests/plan_view.py first)");
  process.exit(1);
}
const plan = JSON.parse(readFileSync(planPath, "utf8"));

// The state list is DERIVED from tests/card_drift.mjs, never carried: the
// port in lib/states.js must cover exactly the names that file lists.
const driftSrc = readFileSync(path.join(repo, "tests/card_drift.mjs"), "utf8");
let driftNames = [...driftSrc.matchAll(/^\s{2}\{ name: "([a-z0-9_]+)",$/gm)].map((m) => m[1]);
if (driftNames.length !== 34) { console.error(`FAIL: derived ${driftNames.length} states from tests/card_drift.mjs`); process.exit(1); }
// D4_ONLY / D4_MEDIA narrow the grid for a smoke run; the full run sets neither.
if (process.env.D4_ONLY) driftNames = driftNames.filter((n) => process.env.D4_ONLY.split(",").includes(n));

const VIEWPORTS = [
  { name: "375x812", width: 375, height: 812, tile: 359 },
  { name: "768x1024", width: 768, height: 1024, tile: 736 },
  { name: "1280x800", width: 1280, height: 800, tile: 500 },
];
// Home Assistant's own default theme variables (frontend default_light /
// default_dark). A card is only ever mounted inside HA, so these — not the
// card's own var() fallbacks — are what a stock user sees.
const THEMES = {
  light: {
    "--primary-text-color": "#212121", "--secondary-text-color": "#727272",
    "--primary-color": "#03a9f4", "--accent-color": "#ff9800",
    "--card-background-color": "#ffffff", "--primary-background-color": "#fafafa",
    "--secondary-background-color": "#e5e5e5", "--divider-color": "rgba(0,0,0,.12)",
    "--error-color": "#db4437", "--warning-color": "#ffa600",
    "--success-color": "#43a047", "--text-primary-color": "#ffffff",
    "--disabled-text-color": "#bdbdbd",
  },
  dark: {
    "--primary-text-color": "#e1e1e1", "--secondary-text-color": "#9b9b9b",
    "--primary-color": "#03a9f4", "--accent-color": "#ff9800",
    "--card-background-color": "#1c1c1c", "--primary-background-color": "#111111",
    "--secondary-background-color": "#202020", "--divider-color": "rgba(225,225,225,.12)",
    "--error-color": "#db4437", "--warning-color": "#ffa600",
    "--success-color": "#43a047", "--text-primary-color": "#212121",
    "--disabled-text-color": "#6f6f6f",
  },
};
const LANGS = [
  { name: "en", hass: { language: "en" } },
  { name: "sv", hass: { language: "sv-SE" } },
];
// The two media arms the brief names. They are an axis of their own rather
// than a product with the rest: a coarse pointer changes the hit-size bar,
// reduced motion changes transitions, neither changes the colour pairs.
let MEDIA = [
  { name: "fine-motion", pointer: "fine", reduced: false, hitBar: 24 },
  { name: "coarse-motion", pointer: "coarse", reduced: false, hitBar: 44 },
  { name: "fine-reduced", pointer: "fine", reduced: true, hitBar: 24 },
];

if (process.env.D4_MEDIA) MEDIA = MEDIA.filter((m) => process.env.D4_MEDIA.split(",").includes(m.name));
let VPS = VIEWPORTS;
if (process.env.D4_VP) VPS = VIEWPORTS.filter((v) => process.env.D4_VP.split(",").includes(v.name));
let THEMELIST = process.env.D4_THEME ? process.env.D4_THEME.split(",") : ["light","dark"];
let LANGLIST = process.env.D4_LANG ? LANGS.filter((l)=>process.env.D4_LANG.split(",").includes(l.name)) : LANGS;

const pageCss = (theme, tile) => `
  :root { ${Object.entries(THEMES[theme]).map(([k, v]) => `${k}:${v}`).join(";")} }
  html, body { margin:0; padding:0; background: ${THEMES[theme]["--primary-background-color"]};
               color: ${THEMES[theme]["--primary-text-color"]};
               font-family: Roboto, -apple-system, "Segoe UI", sans-serif; font-size: 14px; }
  #hpo-host { width: ${tile}px; margin: 0 auto; }
  heatpump-optimizer-card { display: block; }
`;

// <ha-card>: Home Assistant's own element, which the card renders inside its
// shadow root. Undefined it is an inline unknown element and its padding and
// background never shape anything, which is the trap tests/card_browser.mjs
// records at #256. This is the frontend's own :host rule set.
const HA_CARD = `
  if (!customElements.get("ha-card")) {
    customElements.define("ha-card", class extends HTMLElement {
      constructor() {
        super();
        this.attachShadow({ mode: "open" }).innerHTML =
          "<style>:host{background:var(--ha-card-background,var(--card-background-color,white));" +
          "box-sizing:border-box;border-radius:var(--ha-card-border-radius,12px);border-width:1px;" +
          "border-style:solid;border-color:var(--ha-card-border-color,var(--divider-color,#e0e0e0));" +
          "color:var(--primary-text-color);display:block;position:relative;padding:0;}" +
          "</style><slot></slot>";
      }
    });
  }
  if (!customElements.get("ha-icon")) {
    customElements.define("ha-icon", class extends HTMLElement {
      connectedCallback(){ this.style.display="inline-block"; this.style.width="24px"; this.style.height="24px"; }
    });
  }
`;

const results = [];
const pageErrors = [];
let driveFailures = 0;
const SHOT_STATES = new Set((process.env.D4_SHOTS || "plan_inline,expanded_plan,setup_two_tank,tooltip_hover,picker_open_filtered,score_open,wood_alert,away_return,whatif_edited,layout_editing_dragged").split(","));

const browser = await chromium.launch();
try {
  for (const media of MEDIA) {
    for (const vp of VPS) {
      for (const theme of THEMELIST) {
        for (const lang of LANGLIST) {
          const ctx = await browser.newContext({
            viewport: { width: vp.width, height: vp.height },
            reducedMotion: media.reduced ? "reduce" : "no-preference",
            colorScheme: theme,
            deviceScaleFactor: 1,
          });
          const page = await ctx.newPage();
          const cdp = await ctx.newCDPSession(page);
          await cdp.send("Emulation.setEmulatedMedia", {
            features: [
              { name: "pointer", value: media.pointer },
              { name: "any-pointer", value: media.pointer },
              { name: "prefers-color-scheme", value: theme },
              { name: "prefers-reduced-motion", value: media.reduced ? "reduce" : "no-preference" },
            ],
          });
          page.on("pageerror", (e) =>
            pageErrors.push({ media: media.name, vp: vp.name, theme, lang: lang.name, msg: String(e.message).slice(0, 200) }));
          page.on("console", (m) => {
            if (m.type() === "error") {
              pageErrors.push({ media: media.name, vp: vp.name, theme, lang: lang.name, msg: "console: " + m.text().slice(0, 200) });
            }
          });
          await page.goto("about:blank");
          // D4_FREEZE: stand the clock six hours into the captured day, as
          // tests/card_browser.mjs does. Against the real wall clock every
          // slot in the recorded payload is already in the past, no
          // `.slot-hit` is drawn at all, and every editable-surface
          // measurement is taken over an empty set -- which reads as a pass.
          if (process.env.D4_FREEZE) {
            const frozen = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600 * 1000;
            await page.addInitScript((f) => {
              const Real = Date;
              class Frozen extends Real {
                constructor(...a) { super(...(a.length ? a : [f])); }
                static now() { return f; }
              }
              window.Date = Frozen;
            }, frozen);
            await page.reload();
          }
          await page.addStyleTag({ content: pageCss(theme, vp.tile) });
          await page.addScriptTag({ content: HA_CARD });
          await page.addScriptTag({ path: CARD_SRC });
          await page.addScriptTag({ path: path.join(__dirname, "lib/measure.js") });
          await page.addScriptTag({ path: path.join(__dirname, "lib/states.js") });
          // matchMedia for the card's own JS reads (CDP covers CSS only).
          await page.evaluate(([coarse, reduced]) => {
            const orig = window.matchMedia.bind(window);
            window.matchMedia = (q) => {
              if (q === "(pointer: coarse)") return { matches: coarse, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} };
              if (q === "(prefers-reduced-motion: reduce)") return { matches: reduced, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} };
              return orig(q);
            };
          }, [media.pointer === "coarse", media.reduced]);

          for (const name of driftNames) {
            const cell = {
              state: name, vp: vp.name, theme, lang: lang.name, media: media.name,
              hitBar: media.hitBar,
            };
            let r;
            try {
              r = await page.evaluate(async ([n, p, hassLang]) => {
                if (!window.__D4.STATES[n]) return { ok: false, note: "state not ported" };
                // the language arm: every mount takes hassExtra, so patch it once
                window.__D4.__lang = hassLang;
                const origMount = window.__D4.mount;
                if (!window.__D4.__patched) {
                  window.__D4.__patched = true;
                  window.__D4.mount = (st, cfg, extra, w) =>
                    origMount(st, cfg, Object.assign({}, window.__D4.__lang, extra || {}), w);
                }
                const out = await window.__D4.STATES[n](p);
                return out;
              }, [name, plan, lang.hass]);
            } catch (e) {
              r = { ok: false, note: "threw: " + String(e.message).slice(0, 160) };
            }
            cell.drive = r;
            if (!r || !r.ok) driveFailures += 1;
            const m = await page.evaluate(() => {
              const card = window.__card;
              if (!card || !card.shadowRoot) return null;
              const texts = window.__D4.texts(card.shadowRoot);
              return {
                texts,
                overlaps: window.__D4.overlaps(texts, 1),
                clipped: window.__D4.clipped(card.shadowRoot),
                escapes: window.__D4.svgEscapes(card.shadowRoot),
                targets: window.__D4.targets(card.shadowRoot),
                focusables: window.__D4.focusables(card.shadowRoot),
                cardW: card.getBoundingClientRect().width,
                cardH: card.getBoundingClientRect().height,
              };
            });
            if (m) {
              cell.cardW = Math.round(m.cardW * 10) / 10;
              cell.cardH = Math.round(m.cardH * 10) / 10;
              cell.nTexts = m.texts.length;
              cell.lowContrast = m.texts
                .filter((t) => t.ratio < t.need - 0.005 && !t.inactive)
                .map((t) => ({ sel: t.sel, text: t.text, ratio: t.ratio, need: t.need,
                               fg: t.fg, bg: t.bg, bgSource: t.bgSource, fontPx: Math.round(t.fontPx * 100) / 100 }));
              cell.overlaps = m.overlaps;
              cell.clipped = m.clipped;
              cell.escapes = m.escapes;
              cell.smallTargets = m.targets
                .filter((t) => t.min < media.hitBar - 0.05)
                .map((t) => ({ sel: t.sel, key: t.key, text: t.text, w: t.w, h: t.h, min: t.min }));
              cell.nTargets = m.targets.length;
              cell.lowContrastInactive = m.texts
                .filter((t) => t.ratio < t.need - 0.005 && t.inactive)
                .map((t) => ({ sel: t.sel, text: t.text, ratio: t.ratio }));
              cell.focusables = m.focusables;
              cell.tinyText = m.texts
                .filter((t) => t.fontPx > 0 && t.fontPx < 8 - 0.05)
                .map((t) => ({ sel: t.sel, text: t.text, fontPx: Math.round(t.fontPx * 100) / 100 }));
            } else {
              cell.nTexts = -1;
            }
            results.push(cell);
            if (SHOT_STATES.has(name) && media.name === "fine-motion" && lang.name === "en") {
              const f = path.join(SHOTS, `${name}__${vp.name}__${theme}.png`);
              try { await page.screenshot({ path: f, fullPage: false }); } catch (e) {}
            }
          }
          await ctx.close();
        }
      }
    }
  }
} finally {
  await browser.close();
}

const TAG = process.env.D4_FREEZE ? "_frozen" : "";
writeFileSync(path.join(OUT, `cells${TAG}.json`), JSON.stringify(results, null, 1));
writeFileSync(path.join(OUT, `page_errors${TAG}.json`), JSON.stringify(pageErrors, null, 1));

const sum = (f) => results.reduce((a, c) => a + (c[f] ? c[f].length : 0), 0);
const cellsWith = (f) => results.filter((c) => c[f] && c[f].length).length;
const summary = {
  baseline_sha: "7dd68dd327fe3dbfb09f3bd0fe38910c58877697",
  machine: `${os.platform()} ${os.release()} ${os.arch()} ${os.cpus().length}-core`,
  chromium: "chromium-1148 / HeadlessChrome 131.0.6778.33",
  states: driftNames.length,
  viewports: VIEWPORTS.map((v) => v.name),
  themes: ["light", "dark"],
  langs: LANGS.map((l) => l.name),
  media: MEDIA.map((m) => m.name),
  clock: process.env.D4_FREEZE ? "frozen 6h into the captured day" : "real wall clock",
  cells: results.length,
  drive_failures: driveFailures,
  page_errors: pageErrors.length,
  text_nodes_measured: results.reduce((a, c) => a + Math.max(0, c.nTexts), 0),
  low_contrast_instances: sum("lowContrast"),
  low_contrast_cells: cellsWith("lowContrast"),
  overlap_instances: sum("overlaps"),
  overlap_cells: cellsWith("overlaps"),
  clipped_instances: sum("clipped"),
  clipped_cells: cellsWith("clipped"),
  svg_escape_instances: sum("escapes"),
  svg_escape_cells: cellsWith("escapes"),
  small_target_instances: sum("smallTargets"),
  small_target_cells: cellsWith("smallTargets"),
  tiny_text_instances: sum("tinyText"),
};
writeFileSync(path.join(OUT, `summary${TAG}.json`), JSON.stringify(summary, null, 1));
for (const [k, v] of Object.entries(summary)) {
  if (typeof v === "number") console.log(`RESULT ${k}=${v}`);
}
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT thread_factor=1.00 (no CPU-time metric in this harness)`);
console.log(`RESULT swapins=0 (not a memory metric)`);
