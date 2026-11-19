// D4.M1 witness harness (round 11, seat D4-s1): the plan editor's slot hit targets.
//
// Metric: slot_under_floor = `.slot-hit` rects (the target a slot's drag, tap and Tab land
//   on) whose rendered border box is under 24 px (44 px coarse) on either axis, D4-criteria F1
//   as written (no WCAG spacing exception). slot_wcag_fail = of those, the ones a 24 px
//   circle on their centre would also cut another slot-hit (WCAG 2.5.8's exception fails too).
//   Count key: the production card's rendered rect geometry.
// Instrumented symbol: heatpump-optimizer-card.js:slotHitExtents (via the lane renderer's
//   minTargetX = _targetMinPx() in viewBox units).
// Perturbation: PERTURB=1 skips slotHitExtents' final boxed-in resolution
//   (`if (t[p].r <= t[p + 1].l) continue;` -> `continue;`), so every target keeps the floor
//   it was grown to: slot_under_floor must go to (near) zero.
// Run from the export root (filters as m1_browser.mjs: STATES, LANGS, VPS, THEMES, MOTION, POINTER):
//   PW=$HOME/pwlane/node_modules/playwright PLAYWRIGHT_BROWSERS_PATH=$HOME/pw-browsers-lock \
//     HPO_PLANDATA=<plan_view.py payload> node dev/audit/rounds/round11/D4/s1/m1_slots.mjs [PERTURB=1]
// Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B9, Chromium 158.0.8127.18):
//   see REPORT.md (counts exact).
import { execFileSync } from "node:child_process";
import { readFileSync, mkdtempSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d4s1slot-"));
const PROBE = `(() => {
  const coarse = matchMedia("(pointer: coarse)").matches || (typeof window !== "undefined" && navigator.maxTouchPoints > 0);
  const out = [];
  for (const svg of c.shadowRoot.querySelectorAll(".chartwrap svg")) {
    const hs = [...svg.querySelectorAll(".slot-hit")].map((e) => ({ e, b: e.getBoundingClientRect() }));
    for (const h of hs) {
      const w = h.b.width, ht = h.b.height;
      if (Math.min(w, ht) >= 23.95) continue;
      const cx = (h.b.left + h.b.right) / 2, cy = (h.b.top + h.b.bottom) / 2;
      const cut = hs.some((u) => u !== h && Math.hypot(Math.max(u.b.left - cx, 0, cx - u.b.right), Math.max(u.b.top - cy, 0, cy - u.b.bottom)) < 12);
      out.push({ ch: h.e.dataset.channel, w: +w.toFixed(1), h: +ht.toFixed(1), cut });
    }
    for (const h of hs) if (Math.min(h.b.width, h.b.height) >= 23.95 && Math.min(h.b.width, h.b.height) < 43.95) out.push({ ch: h.e.dataset.channel, w: +h.b.width.toFixed(1), h: +h.b.height.toFixed(1), coarseOnly: true });
  }
  return { n: c.shadowRoot.querySelectorAll(".slot-hit").length, under: out };
})()`;
const env = { ...process.env, OUT, LIGHT: "1", PROBE, WORKERS: process.env.WORKERS || "4" };
if (process.argv.includes("PERTURB=1") || process.env.PERTURB === "1") {
  env.HPO_PERTURB = JSON.stringify([["    if (t[p].r <= t[p + 1].l) continue;", "    continue;"]]);
}
execFileSync("node", [path.join(HERE, "m1_browser.mjs")], { env, stdio: ["ignore", "ignore", "inherit"] });
const recs = readFileSync(path.join(OUT, "renders.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
let targets = 0, under = 0, wcag = 0, minW = Infinity;
const states = new Set(), cells = {};
for (const r of recs) {
  const p = r.probe;
  if (!p || typeof p !== "object" || !Array.isArray(p.under)) continue;
  targets += p.n;
  const coarse = r.pointer === "coarse" || r.state === "coarse_pointer";
  for (const u of p.under) {
    if (u.coarseOnly && !coarse) continue;
    under++; states.add(r.state); minW = Math.min(minW, u.w, u.h);
    if (u.cut) wcag++;
    const k = `${r.vp}/${r.pointer}`; cells[k] = (cells[k] || 0) + 1;
  }
}
console.log(`  per vp/pointer: ${JSON.stringify(cells)}`);
console.log(`  states: ${[...states].sort().join(",")}`);
const R = (k, v, u = "") => console.log(`RESULT ${k}=${v}${u ? " " + u : ""}`);
R("renders", recs.length, "renders");
R("slot_targets", targets, "slot-hit rects");
R("slot_under_floor", under, "slot-hit rects under 24 px (44 coarse)");
R("slot_wcag_fail", wcag, "of those, also failing WCAG 2.5.8's spacing exception (fine-pointer 24 px circle)");
R("slot_min_px", minW === Infinity ? "n/a" : minW, "px");
R("thread_factor", 1.0, "(no BLAS; node + chromium)");
R("load1", os.loadavg()[0].toFixed(2));
R("swapins", (readFileSync("/proc/vmstat", "utf8").match(/^pswpin (\d+)/m) || [0, "n/a"])[1]);
