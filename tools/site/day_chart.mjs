#!/usr/bin/env node
// The product page's illustrative day (R10-PRODUCT-PAGE-REDESIGN).
//
// docs/index.html carries the chart as committed inline SVG, so it draws with
// no script and tests/doc_claims.py reads what a visitor sees. This file owns
// that markup: each layer sits between `<!-- chart:NAME -->` and
// `<!-- /chart:NAME -->`, and is never edited by hand.
//
//   node tools/site/day_chart.mjs --write      rewrite every marker pair in the page
//   node tools/site/day_chart.mjs --check      exit 1, naming the layer, where the page differs
//   node tools/site/day_chart.mjs --self-test  assert the toy planner's invariants
//   --page FILE                                a page other than docs/index.html
//
// --self-test and --check may be given together (tests/doc_claims.py does).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

/* The illustrative day and the toy planner behind every chart on this page.
   Not the integration's solver: a 24-step dynamic programme over a house that
   gains three units of stored heat in a heating hour and loses one in an idle
   hour, with one hot-water run owed before each of two demand windows and one
   compressor shared between the two. Prices are unitless. */
const HPO = (() => {
  const PRESETS = {
    peaks: [3.0, 2.6, 2.3, 2.1, 2.0, 2.5, 4.2, 6.6, 8.6, 8.0, 6.9, 5.9, 5.4, 5.1, 5.6, 6.7, 8.8, 9.6, 9.1, 7.6, 6.2, 5.0, 4.4, 3.8],
  };
  const CAP = 9, START = 3, GAIN = 3;
  const WINDOWS = [[6, 9], [18, 21]];          // hot-water demand windows, [from, to)
  const DHW_SPANS = [[2, 6], [14, 18]];        // hours a run may sit in, inclusive

  function baseline(p) {
    const space = Array(24).fill(false), dhw = Array(24).fill(false), temp = [START];
    let t = START;
    for (let h = 0; h < 24; h++) {
      if (h === 6 || h === 18) { dhw[h] = true; t -= 1; }
      else if (t <= 1) { space[h] = true; t += GAIN; }
      else t -= 1;
      temp.push(t);
    }
    return finish(p, space, dhw, temp);
  }

  function finish(p, space, dhw, temp) {
    let cost = 0, n = 0, cheap = 0;
    const mean = p.reduce((a, b) => a + b, 0) / 24;
    for (let h = 0; h < 24; h++) if (space[h] || dhw[h]) { cost += p[h]; n++; if (p[h] < mean - 1e-9) cheap++; }
    return { space, dhw, temp, cost, hours: n, cheap, mean };
  }

  function dp(p, dhwHours, endMin) {
    const INF = 1e9;
    let cur = Array(CAP + 1).fill(INF); cur[START] = 0;
    const back = [];
    for (let h = 0; h < 24; h++) {
      const nxt = Array(CAP + 1).fill(INF), from = Array(CAP + 1).fill(null);
      for (let t = 0; t <= CAP; t++) {
        if (cur[t] >= INF) continue;
        if (dhwHours.includes(h)) {
          if (t - 1 >= 0 && cur[t] + p[h] < nxt[t - 1]) { nxt[t - 1] = cur[t] + p[h]; from[t - 1] = [t, false]; }
          continue;
        }
        if (t - 1 >= 0 && cur[t] < nxt[t - 1] - 1e-9) { nxt[t - 1] = cur[t]; from[t - 1] = [t, false]; }
        if (t + GAIN <= CAP && cur[t] + p[h] < nxt[t + GAIN] - 1e-9) { nxt[t + GAIN] = cur[t] + p[h]; from[t + GAIN] = [t, true]; }
      }
      back.push(from); cur = nxt;
    }
    let best = -1;
    for (let t = endMin; t <= CAP; t++) if (cur[t] < INF && (best < 0 || cur[t] < cur[best] - 1e-9)) best = t;
    if (best < 0) return null;
    const space = Array(24).fill(false), temp = Array(25).fill(0);
    let t = best; temp[24] = t;
    for (let h = 23; h >= 0; h--) { const [pt, on] = back[h][t]; space[h] = on; t = pt; temp[h] = t; }
    return { cost: cur[best], space, temp };
  }

  function solve(p) {
    const base = baseline(p);
    const endMin = base.temp[24];
    let best = null;
    for (let a = DHW_SPANS[0][0]; a <= DHW_SPANS[0][1]; a++)
      for (let b = DHW_SPANS[1][0]; b <= DHW_SPANS[1][1]; b++) {
        const r = dp(p, [a, b], endMin);
        if (r && (!best || r.cost < best.r.cost - 1e-9)) best = { r, a, b };
      }
    const dhw = Array(24).fill(false); dhw[best.a] = dhw[best.b] = true;
    return { plan: finish(p, best.r.space, dhw, best.r.temp), base };
  }

  /* Geometry: a 720 x 380 drawing, no text in it. */
  const G = { W: 720, H: 380, L: 10, cw: 700 / 24, pTop: 22, pBase: 214, tFloor: 356, tStep: 9 };
  const x = h => +(G.L + h * G.cw).toFixed(2);
  const py = v => +(G.pBase - 62 - v * 13).toFixed(2);
  const ty = t => +(G.tFloor - 6 - t * G.tStep).toFixed(2);

  function grid() {
    let s = "";
    for (let h = 0; h <= 24; h++) s += `<line class="g${h % 6 ? "" : " g6"}" x1="${x(h)}" x2="${x(h)}" y1="${G.pTop}" y2="${G.pBase}"/>`;
    s += `<line class="g g6" x1="${x(0)}" x2="${x(24)}" y1="${G.pBase}" y2="${G.pBase}"/>`;
    return s;
  }
  function windows() {
    return WINDOWS.map(([a, b]) => `<rect class="c-win" x="${x(a)}" y="${G.pTop}" width="${+(x(b) - x(a)).toFixed(2)}" height="${G.pBase - G.pTop}"/>`).join("");
  }
  function price(p) {
    let d = `M${x(0)} ${py(p[0])}`;
    for (let h = 0; h < 24; h++) d += ` V${py(p[h])} H${x(h + 1)}`;
    return `<path class="c-price-fill" d="${d} V${G.pBase} H${x(0)} Z"/><path class="c-price" d="${d}"/>`;
  }
  function bars(s, cls) {
    let out = "", i = 0;
    for (let h = 0; h < 24; h++) {
      if (!s.space[h] && !s.dhw[h]) continue;
      const hh = s.space[h] ? 50 : 32;
      out += `<rect class="bar ${s.space[h] ? "c-heat" : "c-dhw"}${cls ? " " + cls : ""}" style="--i:${i++}" x="${+(x(h) + 4).toFixed(2)}" y="${G.pBase - 4 - hh}" width="${+(G.cw - 8).toFixed(2)}" height="${hh}" rx="4"/>`;
    }
    return out;
  }
  function comfort(s) {
    const pts = s.temp.map((t, h) => `${x(h)} ${ty(t)}`).join(" L");
    return `<path class="c-house" d="M${pts}"/>`;
  }
  function floor() {
    return `<line class="c-floor" x1="${x(0)}" x2="${x(24)}" y1="${G.tFloor}" y2="${G.tFloor}"/>`;
  }
  function outdoor() {
    let d = "";
    for (let h = 0; h <= 24; h++) { const v = 250 + 9 * Math.cos((h - 15) / 24 * 2 * Math.PI) * -1 + 9; d += (h ? " L" : "M") + x(h) + " " + v.toFixed(1); }
    return `<path class="c-out" d="${d}"/>`;
  }
  /* What the house then did: the prediction, a little off, as the learners see it. */
  function measured(s) {
    let out = "";
    const off = [0, 2, 3, 1, -2, -3, -1, 2, 3, 2, 0, -2, -3, -2, 1, 2, 3, 1, -1, -2, -3, -1, 1, 2, 1];
    for (let h = 1; h <= 24; h++) out += `<circle class="c-meas" style="--i:${h}" cx="${x(h)}" cy="${(ty(s.temp[h]) + off[h]).toFixed(1)}" r="3.2"/>`;
    return out;
  }
  function layers(p, s) {
    return { grid: grid(), windows: windows(), price: price(p), bars: bars(s), comfort: comfort(s), floor: floor(), outdoor: outdoor(), measured: measured(s) };
  }
  return { PRESETS, WINDOWS, G, solve, layers };
})();
if (typeof module !== "undefined") module.exports = HPO;

// ---------------------------------------------------------------------------
// The page writer. The drawn day is the first preset.
// ---------------------------------------------------------------------------

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const PAGE = path.join(ROOT, "docs", "index.html");
// How many marker pairs the page owes per layer: the story draws all eight, and
// the hero strip repeats the price and the bars. A page with fewer cannot pass
// the check by carrying nothing to compare.
const PAIRS = { grid: 1, windows: 1, price: 2, outdoor: 1, bars: 2, floor: 1, comfort: 1, measured: 1 };
const MARKER = /<!-- chart:([a-z]+) -->([\s\S]*?)<!-- \/chart:\1 -->/g;

function drawn(prices = Object.values(HPO.PRESETS)[0]) {
  return HPO.layers(prices, HPO.solve(prices).plan);
}

/** { text, problems }: the page with every pair rewritten, and what was wrong with the page as given. */
function render(src, want = drawn()) {
  const seen = {}, problems = [];
  const text = src.replace(MARKER, (whole, name, body) => {
    seen[name] = (seen[name] || 0) + 1;
    if (!(name in want)) { problems.push(`${name}: not a layer the generator draws`); return whole; }
    if (body !== want[name]) problems.push(`${name}: the page's markup is not the generator's`);
    return `<!-- chart:${name} -->${want[name]}<!-- /chart:${name} -->`;
  });
  for (const [name, n] of Object.entries(PAIRS)) {
    if ((seen[name] || 0) !== n) problems.push(`${name}: ${seen[name] || 0} marker pair(s) in the page, ${n} owed`);
  }
  return { text, problems };
}

function selfTest() {
  const fails = [];
  const ok = (cond, what) => { if (!cond) fails.push(what); };
  const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  const hours = flags => flags.flatMap((on, h) => (on ? [h] : []));
  const p = Object.values(HPO.PRESETS)[0];
  const { plan, base } = HPO.solve(p);

  ok(plan.temp.length === 25 && plan.temp.every(t => t >= 0), "stored heat is never below zero");
  const spans = [[2, 6], [14, 18]];
  HPO.WINDOWS.forEach(([opens], k) => {
    const runs = hours(plan.dhw).filter(h => h >= spans[k][0] && h <= spans[k][1]);
    ok(runs.length === 1, `exactly one hot-water run in span ${k}`);
    ok(runs.length === 1 && runs[0] + 1 <= opens, `the hot-water run of span ${k} ends before its demand window opens`);
  });
  ok(hours(plan.dhw).length === 2, "two hot-water runs in the day");
  ok(!plan.space.some((on, h) => on && plan.dhw[h]), "one compressor: no hour heats both");
  ok(plan.cost <= base.cost + 1e-9, "the plan costs no more than the unoptimized schedule on the drawn day");
  const flat = HPO.solve(Array(24).fill(5));
  ok(Math.abs(flat.plan.cost - flat.base.cost) < 1e-9, "a flat price gives equal cost for both");
  // The drawn day, as the design note states it for the reviewer.
  ok(eq(hours(plan.space), [3, 4, 5, 12, 13, 23]), "space heating sits in the hours the design note names");
  ok(eq(hours(plan.dhw), [2, 14]), "hot water sits in the hours the design note names");
  ok(eq(plan.temp, [3, 2, 1, 0, 3, 6, 9, 8, 7, 6, 5, 4, 3, 6, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 3]), "stored heat by hour is the design note's");

  const a = drawn(), b = drawn();
  ok(eq(a, b), "two runs give byte-identical output");
  ok(eq(Object.keys(a).sort(), Object.keys(PAIRS).sort()), "the layers drawn are the layers the page owes");
  const all = Object.values(a).join("");
  ok(!/<text|<tspan|<title|<desc/.test(all) && !/>[^<]+</.test(all), "no text in the drawing: nothing can be read off it");
  ok(!/<line[^>]*[^/]>/.test(all), "every line element is self-closed (the page parser closes nothing else)");

  // The check's own controls: a clean page passes, and each way of being wrong is named.
  const page = `<svg>${Object.entries(PAIRS).map(([n, k]) => `<!-- chart:${n} --><!-- /chart:${n} -->`.repeat(k)).join("")}</svg>`;
  const written = render(page).text;
  ok(written !== page && render(written).problems.length === 0, "a written page passes the check");
  ok(render(written).text === written, "writing a written page changes nothing");
  const moved = p.slice(); moved[7] += 0.5;
  const other = render(written, drawn(moved)).problems;
  ok(other.some(m => m.startsWith("price:")), "one changed price is refused, naming the price layer");
  ok(render(written.replace(/<!-- chart:grid -->[\s\S]*?<!-- \/chart:grid -->/, "")).problems.some(m => m.startsWith("grid: 0 marker")), "a missing marker pair is refused");
  ok(render(written.replace('r="3.2"', 'r="3.3"')).problems.some(m => m.startsWith("measured:")), "a hand edit inside a pair is refused");
  return fails;
}

function main(argv) {
  const flags = new Set(argv.filter(a => a.startsWith("--") && a !== "--page"));
  const at = argv.indexOf("--page");
  const page = at >= 0 ? path.resolve(argv[at + 1] || "") : PAGE;
  const known = ["--write", "--check", "--self-test"];
  if (!flags.size || [...flags].some(f => !known.includes(f)) || (flags.has("--write") && flags.has("--check"))) {
    console.error("usage: day_chart.mjs (--write | --check) [--self-test] [--page FILE]  |  day_chart.mjs --self-test");
    return 2;
  }
  let rc = 0;
  if (flags.has("--self-test")) {
    const fails = selfTest();
    for (const f of fails) console.log(`FAIL self-test: ${f}`);
    if (fails.length) rc = 1; else console.log("day_chart: self-test OK");
  }
  if (flags.has("--write") || flags.has("--check")) {
    let src;
    try { src = fs.readFileSync(page, "utf8"); } catch (e) {
      if (e.code !== "ENOENT") throw e;
      console.log(`FAIL ${page}: no such page`); return 1;
    }
    const { text, problems } = render(src);
    if (flags.has("--write")) {
      const structural = problems.filter(m => !m.endsWith("is not the generator's"));
      for (const m of structural) console.log(`FAIL ${m}`);
      if (structural.length) return 1;
      if (text !== src) fs.writeFileSync(page, text);
      console.log(`day_chart: ${text !== src ? "wrote" : "unchanged"} ${path.relative(ROOT, page)}`);
    } else {
      for (const m of problems) console.log(`FAIL ${m}`);
      if (problems.length) rc = 1; else console.log(`day_chart: ${path.relative(ROOT, page)} carries the generator's chart`);
    }
  }
  return rc;
}

process.exitCode = main(process.argv.slice(2));
