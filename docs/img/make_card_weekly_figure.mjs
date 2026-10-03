// Regenerates docs/img/card-dhw-band-weekly.png: the shipped card's enlarged
// Plan page across a Friday and a Saturday, with a per-weekday hot-water
// schedule (`weekdays 07:30-08:30, weekend 19:00-21:00`) in force, so the
// tank's dashed lower edge is held at the 45 degree minimum inside Friday's
// morning window and Saturday's evening window and runs free outside them.
//
// The card is the real one, in real Chromium (a picture OF the card, like
// card-plan-chart.png and docs/img/card/*; the older picture was taken from an
// earlier card design and nothing re-ran it). Only the payload is built here:
// the solved one-day payload tests/plan_view.py writes, repeated onto a
// second day shifted to start on a Friday, with the second day's prices
// marked estimated and its evening tank curve a few degrees under the
// minimum so the clamp is visible.
//
//   python3 tests/plan_view.py
//   node docs/img/make_card_weekly_figure.mjs      # from the repository root
//
// Needs `playwright` resolvable (NODE_PATH or a local node_modules) and its
// Chromium. docs/ is INERT in tests/closure.py, so this selects no gate script.
import { createRequire } from "node:module";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { CARD_PATH, DEFAULT_SPACE, DEFAULT_DHW, planStates } from "../../tests/card_rig.mjs";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const plan0 = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA ||
  path.join("/tmp", `plandata-${crypto.createHash("sha256").update(path.join(ROOT, "tests")).digest("hex").slice(0, 12)}.json`), "utf8"));
const OUT = process.env.HPO_WEEKLY_OUT || path.join(ROOT, "docs/img/card-dhw-band-weekly.png");

const DAY = 86400e3;
const iso = (ms) => new Date(ms).toISOString().slice(0, 19);
// Local wall-clock strings, as the payload writes them: read them as UTC and
// shift by whole days, so the Friday start is independent of the machine's zone.
const toMs = (t) => Date.parse(t + "Z");
const first = toMs(plan0.dhw_plan.forecast[0].t);
const friday = Date.UTC(2026, 0, 16); // 2026-01-16 is a Friday
const shift = friday - first;

function extend(rows, evening) {
  const day1 = rows.map((r) => ({ ...r, t: iso(toMs(r.t) + shift) }));
  const day2 = rows.map((r) => {
    const t = toMs(r.t) + shift + DAY;
    const h = new Date(t).getUTCHours() + new Date(t).getUTCMinutes() / 60;
    const o = { ...r, t: iso(t), price_known: false };
    if (evening && h >= 18.5 && h < 21.5) {
      for (const k of ["dhw_temp", "dhw_temp_lo", "dhw_temp_hi"]) if (k in o) o[k] = o[k] - 3.2;
    }
    return o;
  });
  return [...day1, ...day2];
}
const plan = JSON.parse(JSON.stringify(plan0));
plan.space_plan.forecast = extend(plan0.space_plan.forecast, false);
plan.dhw_plan.forecast = extend(plan0.dhw_plan.forecast, true);
const reslot = (slots) => [
  ...slots.map((s) => ({ ...s, start: iso(toMs(s.start) + shift), end: iso(toMs(s.end) + shift) })),
  ...slots.map((s) => ({ ...s, start: iso(toMs(s.start) + shift + DAY), end: iso(toMs(s.end) + shift + DAY) })),
];
plan.space_plan.slots = reslot(plan0.space_plan.slots);
plan.dhw_plan.slots = reslot(plan0.dhw_plan.slots);

const states = planStates(plan);
Object.assign(states[DEFAULT_DHW].attributes, {
  dhw_min_temperature: 45,
  dhw_windows_spec: "weekdays 07:30-08:30, weekend 19:00-21:00",
});

const browser = await chromium.launch();
try {
  const ctx = await browser.newContext({
    viewport: { width: 1230, height: 940 }, deviceScaleFactor: 2,
    colorScheme: "light", reducedMotion: "reduce", timezoneId: "UTC",
  });
  await ctx.clock.setFixedTime(friday);
  const page = await ctx.newPage();
  await page.goto("about:blank");
  await page.addScriptTag({ path: CARD_PATH });
  await page.evaluate((st) => {
    const style = document.createElement("style");
    style.textContent = `body{margin:0;font-family:"Liberation Sans",Arial,sans-serif}`;
    document.head.appendChild(style);
    const card = document.createElement("heatpump-optimizer-card");
    document.body.appendChild(card);
    card.setConfig({ type: "custom:heatpump-optimizer-card", hours: 48 });
    card.hass = { states: st, language: "en", themes: { darkMode: false } };
    card._onCardClick({});
    card.dialog.page = "plan";
    card._render();
    window.__card = card;
  }, states);
  await page.waitForTimeout(400);
  await page.evaluate(() => { const a = window.__card.shadowRoot.activeElement; if (a) a.blur(); });
  // The picture is the dialog down to the bottom of the chart; the slot editor under it is another figure.
  const box = await page.evaluate(() => {
    const d = window.__card.shadowRoot.querySelector("dialog[open]").getBoundingClientRect();
    const c = window.__card.shadowRoot.querySelector("dialog[open] .chartwrap").getBoundingClientRect();
    return { x: d.left, y: d.top, width: d.width, height: c.bottom - d.top + 2 };
  });
  const shot = await page.screenshot({ type: "png", clip: box });
  fs.writeFileSync(OUT, shot);
  console.log(`wrote ${OUT} (${shot.length} bytes)`);
} finally {
  await browser.close();
}
