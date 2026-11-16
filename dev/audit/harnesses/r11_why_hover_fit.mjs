// R11-OWNER-GENERIC-CONTROL-TEXT carry (#3643): does the chart hover's
// explanation block (.tt-why) survive fitWhy once why.sub_dearer is reworded? Drives the
// card at one git ref in Chromium at 375 and 500 px, on the tile chart and the
// expanded dialog's chart, hovering the repository fixture's dearest idle space
// step (tests/plan_view.py's payload through tests/card_rig.mjs's planStates,
// its published reason idle_dearer). Per surface and width it prints the chart's
// fitWhy cap, the tooltip's height with fitWhy disabled (natural) and enabled
// (fitted), whether the explanation block is shown, and each line's rendered
// height (one line is the computed line-height).
//
//    node dev/audit/harnesses/r11_why_hover_fit.mjs <ref> [plan.json]
//
// WHY_SUB_DEARER="<text>" replaces the English why.sub_dearer string in the
// ref's card before it loads: the control arm, e.g. "this hour is more
// expensive than the hours the plan uses". The plan payload defaults to the
// per-checkout path tests/plan_view.py writes. Needs Playwright's Chromium.

import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const rig = await import(path.join(repo, "tests/card_rig.mjs"));
const ref = process.argv[2];
if (!ref) { console.error("usage: r11_why_hover_fit.mjs <ref> [plan.json]"); process.exit(2); }
const planPath = process.argv[3] || process.env.HPO_PLANDATA ||
  path.join("/tmp", `plandata-${createHash("sha256").update(path.join(repo, "tests")).digest("hex").slice(0, 12)}.json`);
let src = execFileSync("git", ["-C", repo, "show", `${ref}:${rig.CARD_PATH}`], { encoding: "utf8", maxBuffer: 64 << 20 });
if (process.env.WHY_SUB_DEARER) {
  const re = /("why\.sub_dearer": )"[^"]*"/;
  if (!re.test(src)) { console.error("why.sub_dearer not found in the card"); process.exit(2); }
  src = src.replace(re, `$1${JSON.stringify(process.env.WHY_SUB_DEARER)}`);
}
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "hpo-why-fit-"));
const cardSrc = path.join(tmp, "card.js");
fs.writeFileSync(cardSrc, src);
const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
const st = rig.planStates(plan);
const idle = st[rig.DEFAULT_SPACE].attributes.forecast.filter((p) => !(Number(p.space_power) > 0.05));
const maxP = Math.max(...idle.map((p) => p.price));
const step = idle.find((p) => p.price === maxP);
console.log(`ref=${ref} step=${step.t} reason=${step.reason}`);
const browser = await chromium.launch();
for (const dialog of [false, true]) for (const natural of [true, false]) for (const W of [375, 500]) {
  const ctx = await browser.newContext({ viewport: { width: W, height: 800 }, deviceScaleFactor: 1 });
  await ctx.clock.setFixedTime(Date.parse(plan.dhw_plan.forecast[0].t) + 6 * rig.HOUR);
  const page = await ctx.newPage();
  await page.setContent("<!doctype html><html><head></head><body></body></html>");
  await page.addScriptTag({ path: cardSrc });
  const r = await page.evaluate(async ([st, W, t, natural, dialog]) => {
    // The card is a classic script, so its top-level fitWhy is a global binding.
    if (natural) window.fitWhy = () => {};
    const frame = () => new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(res)));
    const s = document.createElement("style");
    s.textContent = `body{margin:0;padding:16px} heatpump-optimizer-card{display:block;width:${W}px}`;
    document.head.appendChild(s);
    const card = document.createElement("heatpump-optimizer-card");
    document.body.appendChild(card);
    card.setConfig({ type: "custom:heatpump-optimizer-card" });
    card.hass = { states: st, language: "en", themes: { darkMode: false } };
    await frame();
    if (dialog) { card._onCardClick({}); await frame(); }
    const root = card.shadowRoot, plot = card._plot;
    const svgs = [...root.querySelectorAll(".chartwrap svg")];
    const svg = svgs[svgs.length - 1];
    const rect = svg.getBoundingClientRect();
    const x = rect.left + (plot.scaleX(Date.parse(t) + 450000) / svg.viewBox.baseVal.width) * rect.width;
    card._onPointerMove({ clientX: x, clientY: rect.top + rect.height * 0.45, currentTarget: svg });
    const tt = svg.closest(".chartwrap").parentNode.querySelector(".tooltip") || root.querySelector(".tooltip");
    const why = tt.querySelector(".tt-why");
    const li = why ? [...why.querySelectorAll("li")] : [];
    const lh = li.length ? parseFloat(getComputedStyle(li[0]).lineHeight) : 0;
    return { cap: Math.round(rect.height - 16), h: tt.offsetHeight, shown: !!why,
      lines: li.map((l) => Math.round(l.getBoundingClientRect().height / (lh || 1))), first: li.length ? li[0].textContent : "" };
  }, [st, W, step.t, natural, dialog]);
  console.log(`${dialog ? "dialog" : "tile"} ${natural ? "natural" : "fitted"} W=${W} cap=${r.cap} height=${r.h} ` +
    `block=${r.shown} lines=${JSON.stringify(r.lines)} first="${r.first}"`);
  await ctx.close();
}
await browser.close();
fs.rmSync(tmp, { recursive: true, force: true });
