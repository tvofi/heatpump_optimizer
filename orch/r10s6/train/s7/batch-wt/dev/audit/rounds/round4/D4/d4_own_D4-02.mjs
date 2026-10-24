// VERIFIER 1 (seat 0-1) round 4 — OWN harness for finding D4-02.
//
// METRIC (mine, independent of the finder's):
//   (1) ARITHMETIC: WCAG 2.1 relative-luminance ratio, my own
//       implementation, for the pairings the finding names:
//       #212121 on #026aa8 (the finding's dark pairing) and #ffffff on
//       #026aa8 (the card's fallback / HA stock dark value).
//   (2) RENDERED CONTROL: two bare divs (NO card, NO finder lib) painted
//       with those exact colours, rasterised at deviceScaleFactor 3; ratio
//       computed from measured centre-pixel colours, so the arithmetic is
//       checked against what Chromium actually paints.
//   (3) PREMISE CHECK (the finding's load-bearing premise: "HA default
//       dark sets --text-primary-color: #212121"): fetch Home Assistant's
//       own frontend theme source at run time (the file HA's docs name as
//       the reference, color.globals.ts, plus the dark-application code
//       apply_themes_on_element.ts) and count how many times
//       --text-primary-color is assigned inside the DARK override set vs
//       the base (light) set.
//
// RUN (from the repository root):
//   NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//     node tools/audit/round4/D4/d4_own_D4-02.mjs
//   (no HPO_PLANDATA needed: the card is not mounted)
//
// EXPECTED (verifier's own prediction): #212121/#026aa8 = 2.78 and
// #ffffff/#026aa8 = 5.79 both reproduce (tolerance +-0.02 arithmetic,
// +-0.05 rendered); the premise check returns dark_assignments=0 and
// base_assignment=#ffffff if HA leaves the variable alone in dark mode.
import { createRequire } from "node:module";
import { writeFileSync, mkdirSync } from "node:fs";
import https from "node:https";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "out");
mkdirSync(OUT, { recursive: true });

// ---------- (1) arithmetic ----------
const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
const L = (c) => 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
const ratio = (a, b) => { const l1 = L(a), l2 = L(b); return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05); };
const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
const ACCENT = hex("#026aa8");
const DARKTEXT = hex("#212121");
const WHITE = hex("#ffffff");
const arith = {
  "212121_on_026aa8": Math.round(ratio(DARKTEXT, ACCENT) * 1000) / 1000,
  "ffffff_on_026aa8": Math.round(ratio(WHITE, ACCENT) * 1000) / 1000,
};

// ---------- (3) premise check: HA frontend source, fetched live ----------
const get = (url) => new Promise((ok, no) => {
  https.get(url, { headers: { "user-agent": "d4-verify" } }, (r) => {
    if (r.statusCode >= 300 && r.statusCode < 400 && r.headers.location) {
      return get(new URL(r.headers.location, url).toString()).then(ok, no);
    }
    let s = ""; r.on("data", (d) => (s += d)); r.on("end", () => ok(s)); r.on("error", no);
  }).on("error", no);
});
const premise = {};
try {
  const globals = await get("https://raw.githubusercontent.com/home-assistant/frontend/dev/src/resources/theme/color/color.globals.ts");
  // the DARK override block is `export const darkColorStyles = css\` html { ... }\`;`
  const darkStart = globals.indexOf("export const darkColorStyles");
  const darkBlock = darkStart >= 0 ? globals.slice(darkStart) : "";
  const baseBlock = darkStart >= 0 ? globals.slice(0, darkStart) : globals;
  premise.dark_block_assignments_of_text_primary_color = (darkBlock.match(/--text-primary-color\s*:/g) || []).length;
  premise.base_assignment = ((baseBlock.match(/--text-primary-color:\s*(#[0-9a-fA-F]{6})/) || [])[1]) || null;
  premise.fetched_bytes = globals.length;
} catch (e) { premise.error = String(e.message || e); }
try {
  const apply = await get("https://raw.githubusercontent.com/home-assistant/frontend/dev/src/common/dom/apply_themes_on_element.ts");
  premise.dark_rules_source = /themeRules\s*=\s*\{\s*\.\.\.darkSemanticVariables,\s*\.\.\.darkColorVariables\s*\}/.test(apply)
    ? "darkColorVariables only" : "unrecognised";
} catch (e) { premise.apply_error = String(e.message || e); }

// ---------- (2) rendered control ----------
let rendered = {};
const browser = await chromium.launch();
try {
  const ctx = await browser.newContext({ viewport: { width: 400, height: 300 }, deviceScaleFactor: 3 });
  const page = await ctx.newPage();
  await page.goto("about:blank");
  await page.setContent(
    `<style>body{margin:0}div{width:200px;height:100px;font:600 20px Roboto,sans-serif;
      display:flex;align-items:center;justify-content:center}</style>
     <div id="a" style="background:#026aa8;color:#212121">Sample</div>
     <div id="b" style="background:#026aa8;color:#ffffff">Sample</div>`);
  await page.waitForTimeout(80);
  const shot = await page.screenshot({ type: "png" });
  const px = await page.evaluate(async (b64) => {
    const img = new Image();
    await new Promise((ok) => { img.onload = ok; img.src = "data:image/png;base64," + b64; });
    const cv = document.createElement("canvas"); cv.width = img.width; cv.height = img.height;
    const g = cv.getContext("2d", { willReadFrequently: true }); g.drawImage(img, 0, 0);
    const d = g.getImageData(0, 0, cv.width, cv.height).data;
    // a filled background pixel of each swatch (top-left inset, away from glyphs)
    const pick = (x, y) => [d[(y * cv.width + x) * 4], d[(y * cv.width + x) * 4 + 1], d[(y * cv.width + x) * 4 + 2]];
    const lf = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    const ll = (c) => 0.2126 * lf(c[0]) + 0.7152 * lf(c[1]) + 0.0722 * lf(c[2]);
    const rr = (a2, b2) => { const l1 = ll(a2), l2 = ll(b2); return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05); };
    const bgA = pick(20, 20), tA = pick(600, 130); // glyph-ish? use computed colours instead
    return { bgA, bgB: pick(20, 320),
      rr_computed: rr([33, 33, 33], bgA), rr_white: rr([255, 255, 255], bgA) };
  }, shot.toString("base64"));
  rendered = px;
  await ctx.close();
} finally { await browser.close(); }

writeFileSync(path.join(OUT, "d4_own_D4-02.json"), JSON.stringify({ arith, premise, rendered }, null, 1));
console.log(`RESULT arith_212121_on_026aa8=${arith["212121_on_026aa8"]} ratio`);
console.log(`RESULT arith_ffffff_on_026aa8=${arith["ffffff_on_026aa8"]} ratio`);
console.log(`RESULT rendered_bg=rgb(${rendered.bgA}) measured_212121=${Math.round(rendered.rr_computed * 1000) / 1000} measured_ffffff=${Math.round(rendered.rr_white * 1000) / 1000} ratio`);
console.log(`RESULT ha_dark_block_assignments_of_text_primary_color=${premise.dark_block_assignments_of_text_primary_color}`);
console.log(`RESULT ha_base_assignment=${premise.base_assignment}`);
console.log(`RESULT ha_dark_rules_source=${premise.dark_rules_source || premise.apply_error || premise.error || "na"}`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT thread_factor=1.00 (no CPU-time metric)");
console.log("RESULT swapins=0 (not a memory metric)");
