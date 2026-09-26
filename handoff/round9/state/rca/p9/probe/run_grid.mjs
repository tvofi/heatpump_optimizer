// Runs the P9 grid alone against the tree given as argv[2]; argv[3] optional
// perturbation module (default export: (src) => src). Exit 1 on any FAIL.
import fs from "node:fs"; import path from "node:path"; import { createRequire } from "node:module";
const require = createRequire(import.meta.url); const { chromium } = require("playwright");
const REPO = path.resolve(process.argv[2]);
fs.copyFileSync(new URL("./p9_grid.mjs", import.meta.url), path.join(REPO, "tests/p9_grid.mjs"));
const { p9Grid } = await import(path.join(REPO, "tests/p9_grid.mjs"));
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
let cardSrc = fs.readFileSync(path.join(REPO, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"), "utf8");
if (process.argv[3]) { const before = cardSrc; cardSrc = (await import(path.resolve(process.argv[3]))).default(cardSrc); if (cardSrc === before) { console.log("perturbation changed nothing"); process.exit(2); } }
let fails = 0;
const check = (name, ok, detail = "") => { console.log((ok ? "  ok  " : "  FAIL") + "  " + name); if (!ok) { fails++; if (detail) console.log("        " + detail); } };
const t0 = Date.now();
const browser = await chromium.launch();
try { const r = await p9Grid({ browser, check, plan, cardSrc, log: (s) => console.log(s) }); if (process.env.P9_DUMP) fs.writeFileSync(process.env.P9_DUMP, JSON.stringify(r, null, 1)); } finally { await browser.close(); fs.unlinkSync(path.join(REPO, "tests/p9_grid.mjs")); }
console.log(`wall ${((Date.now() - t0) / 1000).toFixed(1)} s; load1 ${fs.readFileSync("/proc/loadavg", "utf8").split(" ")[0]}; ${fails} FAIL`);
process.exit(fails ? 1 : 0);
