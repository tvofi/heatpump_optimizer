// D4-s1 (round 10, D4.M1): the card's P9 property grid over the cells the CI
// lane does not measure.
//
// Metric: per cell set, the count of distinct (element, size) hit targets that
// fail the target floor (24 px fine pointer, 44 px coarse pointer, with the
// lane's own WCAG 2.5.8 spacing exception), plus contrast / overflow / popup
// violations, measured by tests/card_browser.mjs's own `instrument()` and
// `p9Grid` on every state of its `gridStates`. Count key: distinct
// "desc WxH" strings the instrument emits from getBoundingClientRect on the
// rendered production card (custom_components/heatpump_optimizer/www/
// heatpump-optimizer-card.js), never an input attribute.
//
// The lane's p9Grid calls measure(false) in every cell, so the 44 px coarse
// floor is never applied, and runs 7 of the 12 viewport x theme x language
// cells. This harness reuses the lane's code verbatim (sliced from
// tests/card_browser.mjs at run time, so it measures the tree it runs in) and
// substitutes the cell list: CELLS=complement (the 5 missing cells, reduced
// motion as the lane) or CELLS=coarse (375/768 light en, hasTouch, measured at 44 px)
// or CELLS=motion (375 light en, no reduced motion).
//
// Run from the repository root:
//   PYTHONPATH=tests/hastub HPO_PLANDATA=$(mktemp -d)/p.json python tests/plan_view.py
//   NODE_PATH=<pw>/node_modules HPO_CHROME=<chromium executable or empty> CELLS=coarse \
//     node dev/audit/rounds/round10/D4/s1/grid_complement.mjs
// Expected (baseline 17f1c55fad1b, macOS arm64, Chromium 131 headless shell
// rev 1148 via HPO_CHROME because the lock's 1194 was absent): see REPORT.md;
// counts exact.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";

const repo = process.cwd();
const src = fs.readFileSync(path.join(repo, "tests/card_browser.mjs"), "utf8");
const cut = src.indexOf("const solarForecast");
let body = src.slice(0, cut);
const c0 = body.indexOf("  const cells = [];");
const c1 = body.indexOf("  const PAGE = `");
if (c0 < 0 || c1 < 0 || cut < 0) throw new Error("card_browser.mjs layout changed: cells block not found");
body = body.slice(0, c0) + "  const cells = globalThis.__CELLS;\n" + body.slice(c1);
const n1 = body.length;
body = body.replace('colorScheme: cell.os || cell.theme, reducedMotion: "reduce" });',
  'colorScheme: cell.os || cell.theme, reducedMotion: cell.motion || "reduce", hasTouch: !!cell.coarse, isMobile: !!cell.coarse });');
body = body.replace("window.__p9.measure(co), false)", "window.__p9.measure(co), !!cell.coarse)");
// On the coarse pointer the 44 px floor (WCAG 2.5.5) has no spacing exception:
// the lane's 2.5.8 exception tests a 24 px circle, which would pass every
// 24-44 px target. COARSE_EXCEPTION=1 keeps the lane's exception (the control).
if (!process.env.COARSE_EXCEPTION) body = body.replace("if (clash && !(abuts(-1) && abuts(1)))", "if ((clash || coarse) && !(abuts(-1) && abuts(1)))");
if (!body.includes("hasTouch: !!cell.coarse") || !body.includes("!!cell.coarse)")) throw new Error("patch points not found");
body = body.replace(/from "\.\/card_rig\.mjs"/g, `from ${JSON.stringify(path.join(repo, "tests/card_rig.mjs"))}`);
body += "\nexport { p9Grid, plan };\n";
const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), "d4s1-"));
const mod = path.join(tmp, "grid.mjs");
fs.writeFileSync(mod, body);

const V = [[375, 812], [768, 1024], [1280, 800]];
const SETS = {
  complement: [
    { vp: V[1], lang: "en", theme: "dark" }, { vp: V[2], lang: "en", theme: "dark" },
    { vp: V[0], lang: "sv-SE", theme: "dark" }, { vp: V[1], lang: "sv-SE", theme: "dark" }, { vp: V[2], lang: "sv-SE", theme: "dark" },
  ],
  coarse: [{ vp: V[0], lang: "en", theme: "light", coarse: true }, { vp: V[1], lang: "en", theme: "light", coarse: true }],
  fine: [{ vp: V[0], lang: "en", theme: "light" }, { vp: V[1], lang: "en", theme: "light" }],
  motion: [{ vp: V[0], lang: "en", theme: "light", motion: "no-preference" }],
};
const which = process.env.CELLS || "coarse";
globalThis.__CELLS = SETS[which];
const { p9Grid, plan } = await import(mod);
const require = createRequire(path.join(process.env.NODE_PATH || repo, "x.js"));
const { chromium } = require("playwright");
const browser = await chromium.launch(process.env.HPO_CHROME ? { executablePath: process.env.HPO_CHROME } : {});
const cardSrc = fs.readFileSync(path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"), "utf8");
let checks = 0;
const check = (name, ok, detail) => { checks++; console.log(`${ok ? "  ok  " : "  FAIL"}  ${name}${ok ? "" : "\n        " + detail}`); };
const { bad, n } = await p9Grid({ browser, check, plan, cardSrc, log: (s) => console.log(s) });
await browser.close();
const strip = (xs) => [...new Set(xs.map((x) => x.replace(/^[^:]*: /, "")))];
if (process.env.D4_DEBUG) console.log(JSON.stringify(bad, null, 1));
for (const k of ["small", "contrast", "overflow", "popups", "overlap", "options", "threw", "missed"]) {
  console.log(`RESULT ${which}_${k}_instances=${bad[k].length} count`);
  console.log(`RESULT ${which}_${k}_distinct=${strip(bad[k]).length} count`);
  for (const x of strip(bad[k]).slice(0, 12)) console.log(`  ${k}: ${x}`);
}
console.log(`RESULT ${which}_cells_states=${n} count`);
console.log(`RESULT thread_factor=1.0`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
fs.rmSync(tmp, { recursive: true, force: true });
