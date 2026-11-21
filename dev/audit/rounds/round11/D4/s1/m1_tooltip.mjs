// D4.M1 witness harness (round 11, seat D4-s1): the chart tooltip's height against its chart.
//
// Metric: tip_spill_px = max(0, tooltip.bottom - chartwrap.bottom, chartwrap.top - tooltip.top)
//   for the visible `.tooltip` after the hover step of card_drift's tooltip_hover and
//   shared_steps_hover states (every language, viewport, theme, motion and pointer arm).
//   Counted: renders whose spill exceeds 0.5 px (the lane's P9 pop-up rule, R9-UX-1 half,
//   without the viewport half, which moves with where the harness scrolled the chart).
//   Count key: the rendered tooltip box the production card placed, never the fixture.
// Instrumented symbol: heatpump-optimizer-card.js:fitWhy (called from the chart's
//   pointer-move handler with cap = chart height - 16) and tooltipHtml.
// Perturbation: PERTURB=1 makes fitWhy also drop the `.tt-reason` line when the box is
//   still too tall (`tt.querySelector(".tt-why")` -> `... || tt.querySelector(".tt-reason")`),
//   a one-line production edit in memory: tip_spill_renders must go down.
// Null control: tooltip_hover (no shared-step line) in the same run: tip_spill_renders_null.
//
// Run from the export root:
//   PW=$HOME/pwlane/node_modules/playwright PLAYWRIGHT_BROWSERS_PATH=$HOME/pw-browsers-lock \
//     HPO_PLANDATA=<plan_view.py payload> node dev/audit/rounds/round11/D4/s1/m1_tooltip.mjs [PERTURB=1]
// Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B9, Chromium 158.0.8127.18):
//   see REPORT.md (counts exact).
import { execFileSync } from "node:child_process";
import { readFileSync, mkdtempSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d4s1tip-"));
const PROBE = `(() => {
  const t = c.shadowRoot.querySelector(".tooltip:not([hidden])");
  if (!t) return { none: true };
  const b = t.getBoundingClientRect(), w = t.closest(".chartwrap").getBoundingClientRect();
  return { spill: +Math.max(0, b.bottom - w.bottom, w.top - b.top).toFixed(1), h: +b.height.toFixed(1), chartH: +w.height.toFixed(1),
    shared: !!t.querySelector(".tt-shared"), reason: !!t.querySelector(".tt-reason"), why: !!t.querySelector(".tt-why") };
})()`;
const env = { ...process.env, OUT, LIGHT: "1", PROBE, STATES: "tooltip_hover,shared_steps_hover", WORKERS: process.env.WORKERS || "4" };
if (process.argv.includes("PERTURB=1") || process.env.PERTURB === "1") {
  env.HPO_PERTURB = JSON.stringify([['  const why = tt.querySelector(".tt-why");', '  const why = tt.querySelector(".tt-why") || tt.querySelector(".tt-reason");']]);
}
execFileSync("node", [path.join(HERE, "m1_browser.mjs")], { env, stdio: ["ignore", "ignore", "inherit"] });
const recs = readFileSync(path.join(OUT, "renders.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const agg = {};
let none = 0;
for (const r of recs) {
  const p = r.probe;
  if (!p || p.none || typeof p !== "object") { none++; continue; }
  const k = r.state;
  agg[k] = agg[k] || { n: 0, spill: 0, max: 0, cells: {} };
  agg[k].n++;
  if (p.spill > 0.5) { agg[k].spill++; agg[k].max = Math.max(agg[k].max, p.spill); const c = `${r.vp}/${r.pointer}`; agg[k].cells[c] = Math.max(agg[k].cells[c] || 0, p.spill); }
}
for (const [k, a] of Object.entries(agg)) console.log(`  ${k}: renders ${a.n}, spilling ${a.spill}, max ${a.max} px, per vp/pointer ${JSON.stringify(a.cells)}`);
const R = (k, v, u = "") => console.log(`RESULT ${k}=${v}${u ? " " + u : ""}`);
R("renders", recs.length, "renders");
R("no_tooltip", none, "renders where no tooltip was shown");
R("tip_spill_renders", (agg.shared_steps_hover || { spill: 0 }).spill, "shared_steps_hover renders with the tooltip >0.5 px past its chart");
R("tip_spill_max_px", (agg.shared_steps_hover || { max: 0 }).max, "px");
R("tip_spill_renders_null", (agg.tooltip_hover || { spill: 0 }).spill, "tooltip_hover renders (null control)");
R("thread_factor", 1.0, "(no BLAS; node + chromium)");
R("load1", os.loadavg()[0].toFixed(2));
R("swapins", (readFileSync("/proc/vmstat", "utf8").match(/^pswpin (\d+)/m) || [0, "n/a"])[1]);
