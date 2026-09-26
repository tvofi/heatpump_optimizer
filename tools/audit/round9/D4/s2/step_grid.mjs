// D4-s2 helper for step_grid.py (not run on its own): reads the rendered
// NumberSelector configs step_grid.py wrote, builds for each one a native
// <input type=number> with the selector's min/max/step and the rendered value,
// and reports Chromium's validity.stepMismatch and the value one stepUp() gives.
// Usage: NODE_PATH=<prefix>/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers \
//        node tools/audit/round9/D4/s2/step_grid.mjs <in.json> <out.json>
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const [, , inPath, outPath] = process.argv;
const fields = JSON.parse(readFileSync(inPath, "utf8"));
const browser = await chromium.launch();
const page = await browser.newPage();
await page.setContent("<!doctype html><html><body></body></html>");
const out = await page.evaluate((fields) => fields.map((f) => {
  const el = document.createElement("input");
  el.type = "number";
  el.min = String(f.min); el.max = String(f.max); el.step = String(f.step);
  el.value = String(f.value);
  document.body.appendChild(el);
  const mismatch = el.validity.stepMismatch;
  const message = el.validationMessage;
  let up = null;
  try { el.stepUp(); up = el.value; } catch (e) { up = "throws"; }
  el.remove();
  return { ...f, stepMismatch: mismatch, validationMessage: message, afterStepUp: up };
}), fields);
writeFileSync(outPath, JSON.stringify(out, null, 1));
await browser.close();
