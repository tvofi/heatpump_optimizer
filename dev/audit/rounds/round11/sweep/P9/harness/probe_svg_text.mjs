// P9 sweep probe (round 11): rendered size of the setup diagram's SVG text.
// Metric: setup_text_under_floor = text runs in `.setup-svg` whose rendered font size
//   (computed font-size in viewBox units x the element's screen CTM scale) is under the
//   card's own SVG text floor, MIN_AXIS_FONT_PX = 8 px, which the chart applies through
//   chartFontUnits and the setup diagram does not apply by any rule. Measured at the grid's
//   viewports (375/768/1280; m1_browser.mjs has no narrower one): the setup text's minimum
//   is 8.56 px at 375 (under the card's 12 px HTML floor, over the 8 px SVG floor).
// Null control: the chart's SVG labels in the same renders, which ARE floored (chartFontUnits,
//   MIN_AXIS_FONT_PX = 8 px): chart_text_under_floor counts chart text under that 8 px floor.
// Perturbation PERTURB=1: the five setup text rules take 16px -> setup_text_under_floor down.
// Run: NODE_PATH=$(npm root -g) HPO_PLANDATA=<plan_view.py payload> node probe_svg_text.mjs [PERTURB=1]
// Exits 1 when setup_text_under_floor > 0.
import { execFileSync } from "node:child_process";
import { readFileSync, mkdtempSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
const FLOOR = 8; // the card's own SVG text floor, MIN_AXIS_FONT_PX (chart labels)
const HERE = path.dirname(fileURLToPath(import.meta.url));
const M1 = path.join(HERE, "..", "..", "D4", "s1", "m1_browser.mjs");
const OUT = mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "p9svg-"));
const PROBE = `(() => {
  const r = c.shadowRoot, out = [];
  const px = (el) => { const m = el.getScreenCTM(); if (!m) return null;
    const s = Math.hypot(m.a, m.b); const fs = parseFloat(getComputedStyle(el).fontSize);
    const b = el.getBBox ? el.getBBox() : { width: 0 }; if (!b.width) return null; return +(fs * s).toFixed(2); };
  for (const el of r.querySelectorAll(".setup-svg text")) { const v = px(el); if (v != null) out.push({ k: "setup", cls: el.getAttribute("class") || "text", px: v }); }
  for (const el of r.querySelectorAll("svg:not(.setup-svg) text")) { const v = px(el); const svg = el.ownerSVGElement; if (v != null) out.push({ k: "chart", cls: (svg && (svg.getAttribute("class") || svg.parentElement && svg.parentElement.className) || "svg") + " " + (el.getAttribute("class") || "text"), px: v }); }
  return out;
})()`;
const env = { ...process.env, OUT, LIGHT: "1", PROBE, STATES: process.env.STATES || "setup_two_tank,layout_editing,layout_editing_tidy", WORKERS: "4" };
if (process.argv.includes("PERTURB=1")) env.HPO_PERTURB = JSON.stringify([
  [".setup-slot.lead { font-size: 11px; }", ".setup-slot.lead { font-size: 16px; }"],
  ["font-size: 11px; font-weight: 600; fill: var(--hpo-accent", "font-size: 16px; font-weight: 600; fill: var(--hpo-accent"],
]);
execFileSync("node", [M1], { env, stdio: ["ignore", "ignore", "inherit"] });
const recs = readFileSync(path.join(OUT, "renders.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
let su = 0, cu = 0, sn = 0, cn = 0, renders = 0; const by = {};
for (const r of recs) {
  if (!Array.isArray(r.probe)) continue; renders++;
  for (const p of r.probe) {
    if (p.k === "setup") { sn++; if (p.px < FLOOR - 1e-6) { su++; const k = `${p.cls}@${r.vp}`; by[k] = Math.min(by[k] ?? 99, p.px); } }
    else { cn++; if (p.px < FLOOR - 1e-6) { cu++; const k = `chart:${p.cls}@${r.vp}`; by[k] = Math.min(by[k] ?? 99, p.px); } }
  }
}
for (const [k, v] of Object.entries(by).sort()) console.log(`  ${k}: min ${v} px`);
console.log(`RESULT renders=${renders}`);
console.log(`RESULT setup_text_runs=${sn}`);
console.log(`RESULT setup_text_under_floor=${su}`);
console.log(`RESULT chart_text_runs=${cn}`);
console.log(`RESULT chart_text_under_floor=${cu}`);
process.exit(su > 0 ? 1 : 0);
