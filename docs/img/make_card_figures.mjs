// Generates the docs/ figures that are pictures OF THE CARD, by running the
// shipped card through the same rig tests/card.mjs uses and annotating what it
// drew. Nothing here draws a chart: every coordinate a callout points at is
// read back out of the card's own output, so a series that moves takes its
// label with it and a series that stops being drawn takes its label away.
//
// Lives beside its output because `docs/` is INERT in tests/closure.py --
// nothing under tests/ reads it -- so the generator needs no closure entry and
// changing it selects no gate script. (A generator under tools/ would be an
// orphan until tests/closure.py named it, and closure.py is a GATE_FILE.)
//
//   python3 tests/plan_view.py                                   # 1-zone payload
//   HPO_PLAN_TWO_ZONE=1 HPO_PLANDATA=/tmp/plandata-twozone.json \
//     python3 tests/plan_view.py                                 # 2-zone payload
//   node docs/img/make_card_figures.mjs
//
// Run from the repository root.
import fs from "fs";
import path from "path";
import crypto from "crypto";
import { fileURLToPath } from "url";
import {
  CARD_PATH, DEFAULT_SPACE, DEFAULT_DHW,
  makeCardContext, loadCard, collect, planStates, frozenDateClass,
} from "../../tests/card_rig.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const OUT = path.join(ROOT, "docs/img");

// Same default-path derivation as tests/card.mjs and tests/plan_view.py, so a
// run here cannot be satisfied by another checkout's stale payload.
const defaultPlan = path.join(
  "/tmp",
  `plandata-${crypto
    .createHash("sha256")
    .update(path.join(ROOT, "tests"))
    .digest("hex")
    .slice(0, 12)}.json`
);
const ONE_ZONE = process.env.HPO_PLANDATA || defaultPlan;
const TWO_ZONE = process.env.HPO_PLANDATA_TWO_ZONE || "/tmp/plandata-twozone.json";

for (const p of [ONE_ZONE, TWO_ZONE]) {
  if (!fs.existsSync(p)) {
    console.error(`FAIL: no plan payload at ${p} -- run tests/plan_view.py first`);
    process.exit(1);
  }
}

const cardSrc = fs.readFileSync(path.join(ROOT, CARD_PATH), "utf8");

// --- Render ---------------------------------------------------------------

/** Render the card at a fixed instant and return its plan chart's SVG.
 *
 * The instant matters. The plotted window is `[now, now + horizon]`
 * (`defaultWindow`), so the now marker sits at the plot's left edge on every
 * real install -- the plan starts at now -- and it is drawn at all only while
 * the clock is inside the window. Freezing at the payload's first sample is
 * therefore both the faithful view and the one whose plot is full: any later
 * instant leaves the tail of the window empty, and any earlier one (the real
 * clock, months away) trips `defaultWindow`'s historical-data fallback and
 * draws no marker.
 */
function renderChart(planPath, extraConfig) {
  const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
  const { ctx } = makeCardContext();
  const firstT = Date.parse(plan.space_plan.forecast[0].t);
  ctx.Date = frozenDateClass(Date, firstT);
  const Card = loadCard(ctx, cardSrc);
  const card = new Card();
  card.setConfig({ type: "custom:heatpump-optimizer-card", ...(extraConfig || {}) });
  const states = planStates(plan);
  card.hass = { states };
  if (card.connectedCallback) card.connectedCallback();
  card.hass = { states };
  card._render();
  const html = collect(card.shadowRoot).join("\n");
  // The card emits several SVGs (the expand glyph among them); the chart is
  // the big one. Picked by size rather than by a class name the card is free
  // to rename.
  const svgs = html.match(/<svg[\s\S]*?<\/svg>/g) || [];
  const svg = svgs.sort((a, b) => b.length - a.length)[0] || "";
  if (!svg || svg.length < 5000) {
    console.error(`FAIL: no plan chart rendered from ${planPath}`);
    process.exit(1);
  }
  return svg;
}

/** The chart's drawing, with theme variables resolved to their own fallbacks.
 *
 * A figure is viewed outside Home Assistant, where `var(--primary-text-color)`
 * resolves to nothing and the text disappears. The fallback the card itself
 * supplies is the honest substitute: it is what the card shows on a theme that
 * defines none.
 */
function chartBody(svg, ns) {
  const open = svg.indexOf(">");
  const body = svg
    .slice(open + 1, svg.lastIndexOf("</svg>"))
    .replace(/var\(--[a-z-]+,\s*([^)]+)\)/g, "$1")
    .replace(/var\(--primary-text-color\)/g, "#212121")
    .replace(/var\(--secondary-text-color\)/g, "#757575")
    .replace(/var\(--divider-color\)/g, "#e0e0e0");
  // The card's `<defs>` ids (the shared-compressor hatch) are unique inside one
  // card, not inside a figure that pastes two renders into one document, where
  // the second `url(#id)` would silently bind to the first render's pattern.
  return ns
    ? body.replace(/id="([^"]+)"/g, `id="${ns}-$1"`).replace(/url\(#([^)]+)\)/g, `url(#${ns}-$1)`)
    : body;
}

// --- Reading geometry back out of the render ------------------------------

/** On-curve vertices of an SVG path, for the M/L/C the card emits. */
function vertices(d) {
  const out = [];
  const tokens = d.match(/[MLCZmlcz]|-?\d*\.?\d+(?:e[-+]?\d+)?/gi) || [];
  let i = 0;
  let cmd = "M";
  const num = () => parseFloat(tokens[i++]);
  while (i < tokens.length) {
    if (/^[MLCZmlcz]$/.test(tokens[i])) cmd = tokens[i++];
    if (i >= tokens.length) break;
    if (cmd === "M" || cmd === "L") {
      out.push({ x: num(), y: num() });
    } else if (cmd === "C") {
      num(); num(); num(); num();      // the two control points
      out.push({ x: num(), y: num() }); // the endpoint is on the curve
    } else if (cmd === "Z" || cmd === "z") {
      // no coordinates
    } else {
      i++; // an unexpected command: skip a token rather than spin
    }
  }
  return out;
}

/** Every `<path class="series" data-key=K>` in the render, split by dashedness.
 *
 * `data-key` is the card's own handle on a series, and the extras (the house
 * zones, the hot-water band edges) come through it too -- they are dashed
 * because `line.primary` is false, which is exactly what tells them apart.
 */
function seriesPaths(svg) {
  const by = {};
  const re = /<path class="series" data-key="([^"]+)"[^>]*?d="([^"]+)"([^>]*)>/g;
  for (const m of svg.matchAll(re)) {
    const [, key, d, tail] = m;
    const stroke = /stroke="(#[0-9a-fA-F]{3,8})"/.exec(tail + m[0]);
    const entry = (by[key] = by[key] || { solid: [], dashed: [], color: null });
    if (stroke && !entry.color) entry.color = stroke[1];
    // The filled area under a stepped series carries no stroke; the line does.
    if (/fill-opacity/.test(m[0])) continue;
    (/stroke-dasharray/.test(m[0]) ? entry.dashed : entry.solid).push(vertices(d));
  }
  return by;
}

/** The vertex nearest a given fraction across the plot, for one path. */
function at(pts, frac) {
  if (!pts.length) return null;
  const xs = pts.map((p) => p.x);
  const target = Math.min(...xs) + frac * (Math.max(...xs) - Math.min(...xs));
  return pts.reduce((a, b) => (Math.abs(b.x - target) < Math.abs(a.x - target) ? b : a));
}

/** Only one series visible, as a real card config would ask for it.
 * `series: {key: false}` is the documented option, and hiding the rest makes
 * the card rescale the axes to what is left -- so each panel is the card's own
 * answer to "show me just this", not a crop with the neighbours painted out. */
function onlySeries(keep) {
  const series = {};
  for (const k of ["price", "solar", "dhw_slots", "space_slots", "outdoor", "dhw_temp", "house_temp"]) {
    if (k !== keep) series[k] = false;
  }
  return { series };
}

/** The plot frame the card draws, widened to take in the axis beside it. */
function plotBox(svg) {
  const m = /<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)" fill="none"/.exec(svg);
  if (!m) {
    console.error("FAIL: no plot frame in the render");
    process.exit(1);
  }
  const [x, y, w, h] = m.slice(1).map(Number);
  return { x0: x - 52, y0: y - 8, x1: x + w + 8, y1: y + h + 8 };
}

function bbox(lists) {
  const pts = lists.flat();
  return {
    x0: Math.min(...pts.map((p) => p.x)), x1: Math.max(...pts.map((p) => p.x)),
    y0: Math.min(...pts.map((p) => p.y)), y1: Math.max(...pts.map((p) => p.y)),
  };
}

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// The one font stack, matching the hero in README.md.
const FONT = `-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`;
const INK = "#1c1c1c";
const RULE = "#8a8a8a";

// --- B6: the anatomy figure ------------------------------------------------

const CHART_W = 900;
const CHART_H = 380;
const PAD_X = 22;
const PAD_T = 56;

/** A badge sitting on the feature it names. Leader lines were tried first and
 * are worse here: ten of them cross a plot that is already seven series deep,
 * and the key below reads in one pass instead. */
function badge(n, anchor, ox, oy) {
  const ax = anchor.x + ox;
  const ay = anchor.y + oy;
  return `
  <circle cx="${ax.toFixed(1)}" cy="${ay.toFixed(1)}" r="10" fill="#ffffff" fill-opacity="0.92"
          stroke="${INK}" stroke-width="1.5"/>
  <text x="${ax.toFixed(1)}" y="${(ay + 3.9).toFixed(1)}" font-size="11.5" font-weight="700"
        text-anchor="middle" fill="${INK}">${n}</text>`;
}

/** One row of the key under the drawing. */
function keyRow(n, label, x, y) {
  return `
  <circle cx="${x + 10}" cy="${y - 4}" r="10" fill="${INK}"/>
  <text x="${x + 10}" y="${y - 0.1}" font-size="11.5" font-weight="700" text-anchor="middle"
        fill="#ffffff">${n}</text>
  <text x="${x + 27}" y="${y}" font-size="12.5" fill="${INK}">${esc(label)}</text>`;
}

function anatomy(svg) {
  const S = seriesPaths(svg);
  const need = (k) => {
    if (!S[k] || !S[k].solid.length) {
      console.error(`FAIL: the chart drew no "${k}" series; the anatomy figure would label nothing`);
      process.exit(1);
    }
    return S[k].solid[0];
  };
  // The now marker: the one full-height line the card draws that is neither a
  // gridline nor the hidden crosshair. Its x is where "now" is.
  const nowM = [...svg.matchAll(/<line(?![^>]*class="crosshair")[^>]*x1="([\d.]+)"[^>]*y1="16"[^>]*y2="346"[^>]*>/g)]
    .map((m) => ({ raw: m[0], x: parseFloat(m[1]) }))
    .filter((l) => !/#eee/.test(l.raw));
  if (!nowM.length) {
    console.error("FAIL: no now marker in the render; freeze the clock inside the plotted window");
    process.exit(1);
  }
  const nowX = nowM[0].x;

  // The editable slot lanes under the plot, and the time-axis labels.
  const laneRect = /<rect class="lane"[^>]*y="([\d.]+)"[^>]*height="([\d.]+)"/.exec(svg);
  const axisText = /<text x="([\d.]+)" y="(3\d\d)"[^>]*>([^<]*)<\/text>/.exec(svg);

  const ox = PAD_X;
  const oy = PAD_T;

  // Highest point of a series, which is where a power band is worth pointing
  // at: a stepped band spends most of the day on its own baseline, and a badge
  // parked there names the axis rather than the series.
  const peakIn = (pts, lo, hi) => {
    const xs = pts.map((q) => q.x);
    const x0 = Math.min(...xs), span = Math.max(...xs) - x0;
    const win = pts.filter((q) => q.x >= x0 + lo * span && q.x <= x0 + hi * span);
    return (win.length ? win : pts).reduce((a, b) => (b.y < a.y ? b : a));
  };

  const dhwDashed = S.dhw_temp && S.dhw_temp.dashed.length ? S.dhw_temp.dashed[0] : null;

  const items = [
    [1, at(need("price"), 0.62), "Electricity price, stepped — right axis"],
    [2, peakIn(need("space_slots"), 0.15, 0.45), "Space heating power — left kW axis"],
    [3, peakIn(need("dhw_slots"), 0.0, 1.0), "Hot-water heating power, the same kW axis"],
    [4, at(need("outdoor"), 0.24), "Outdoor temperature — left °C axis"],
    [5, at(need("house_temp"), 0.46), "House temperature: the curve the plan holds"],
    [6, at(need("dhw_temp"), 0.78), "Hot-water tank temperature"],
    [7, dhwDashed ? at(dhwDashed, 0.9) : at(need("dhw_temp"), 0.9),
      "…and the model’s own expected error, dashed"],
    [8, peakIn(need("solar"), 0.0, 1.0), "Solar irradiance — its own inner right axis"],
    [9, { x: nowX + 3, y: 30 }, "The “now” marker: the plan starts here"],
  ];
  if (laneRect) {
    items.push([10, { x: 300, y: parseFloat(laneRect[1]) + parseFloat(laneRect[2]) / 2 },
      "Editable slot lanes — drag a slot to move it"]);
  }
  if (axisText) {
    // Below the tick labels, not on top of them: the badge is 20 px across and
    // the labels are 10 px tall, so anything level with them hides one.
    items.push([items.length + 1, { x: parseFloat(axisText[1]) + 118, y: parseFloat(axisText[2]) + 12 },
      "One shared time axis, in your language"]);
  }

  // Key: two columns under the drawing, filled down then across.
  const perCol = Math.ceil(items.length / 2);
  const keyTop = PAD_T + CHART_H + 30;
  const key = items
    .map(([n, , label], i) =>
      keyRow(n, label, PAD_X + (i < perCol ? 0 : CHART_W / 2), keyTop + (i % perCol) * 21)
    )
    .join("");

  const W = CHART_W + PAD_X * 2;
  const H = keyTop + perCol * 21 + 6;

  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="The plan chart with each of its seven series, the now marker, the editable slot lanes and the shared time axis numbered, and a key naming them">
<style>text { font-family: ${FONT}; }</style>
<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>
<text x="${PAD_X}" y="28" font-size="16" font-weight="700" fill="${INK}">Anatomy of the plan chart</text>
<text x="${PAD_X}" y="45" font-size="12" fill="#5a5a5a">Seven series on one shared time axis, four units on four axes. Every chip in the legend toggles one series and rescales the axes to what is left.</text>
<g transform="translate(${ox},${oy})">${chartBody(svg, "an")}</g>
<line x1="${PAD_X}" y1="${keyTop - 18}" x2="${W - PAD_X}" y2="${keyTop - 18}" stroke="#d8d8d8"/>
${items.map(([n, a]) => badge(n, a, ox, oy)).join("")}
${key}
</svg>
`;
}

// --- B7: the two kinds of dashed line --------------------------------------

/** A cropped view of one render, as a nested viewport that clips to a box. */
function panel(svg, box, x, y, w, h, ns) {
  const pad = 16;
  const vb = [box.x0 - pad, box.y0 - pad, (box.x1 - box.x0) + 2 * pad, (box.y1 - box.y0) + 2 * pad];
  return `<svg x="${x}" y="${y}" width="${w}" height="${h}"
      viewBox="${vb.map((v) => v.toFixed(1)).join(" ")}" preserveAspectRatio="xMidYMid meet">
    <rect x="${vb[0]}" y="${vb[1]}" width="${vb[2]}" height="${vb[3]}" fill="#ffffff"/>
    ${chartBody(svg, ns)}
  </svg>`;
}

function dashedPair(house, band) {
  const A = seriesPaths(house);
  const B = seriesPaths(band);
  if (!A.house_temp || !A.house_temp.dashed.length) {
    console.error("FAIL: the two-zone render drew no house zone dashes -- is the payload two-zone?");
    process.exit(1);
  }
  if (!B.dhw_temp || B.dhw_temp.dashed.length !== 2) {
    console.error(
      `FAIL: expected two dashed hot-water band edges, got ${(B.dhw_temp || { dashed: [] }).dashed.length}`
    );
    process.exit(1);
  }

  const PW = 520, PH = 250, GAP = 36, M = 22;
  const W = M * 2 + PW * 2 + GAP;
  const TOP = 104;
  const H = TOP + PH + 84;
  const x2 = M + PW + GAP;

  const cap = (x, title, sub) => `
  <text x="${x}" y="70" font-size="14.5" font-weight="700" fill="${INK}">${esc(title)}</text>
  <text x="${x}" y="88" font-size="12" fill="#5a5a5a">${esc(sub)}</text>`;
  const note = (x, lines) =>
    lines
      .map((t, i) => `<text x="${x}" y="${TOP + PH + 26 + i * 17}" font-size="12" fill="${INK}">${esc(t)}</text>`)
      .join("");

  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Two chart details side by side. Left: the house temperature series, whose dashed pair is the upper and lower floor, two real predicted temperatures with the whole-house curve between them. Right: the hot-water tank series, whose dashed pair is one symmetric expected-error band that widens with lead time.">
<style>text { font-family: ${FONT}; }</style>
<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>
<text x="${M}" y="28" font-size="16" font-weight="700" fill="${INK}">The two kinds of dashed line</text>
<text x="${M}" y="45" font-size="12" fill="#5a5a5a">Each panel is the card with every other series toggled off, so the axis is rescaled to the one that is left.</text>
${cap(M, "Two real temperatures", "House temperature, two-zone house")}
${cap(x2, "One symmetric band", "Hot-water tank temperature")}
${panel(house, plotBox(house), M, TOP, PW, PH, "hz")}
${panel(band, plotBox(band), x2, TOP, PW, PH, "bd")}
<rect x="${M}" y="${TOP}" width="${PW}" height="${PH}" fill="none" stroke="#d4d4d4"/>
<rect x="${x2}" y="${TOP}" width="${PW}" height="${PH}" fill="none" stroke="#d4d4d4"/>
${note(M, [
  "Upper floor and lower floor: two predicted temperatures, one",
  "per zone, drawn only when the house is configured as two-zone.",
  "The solid line between them is the whole house. Two tooltip rows,",
  "two absolute values. They are not error bars.",
])}
${note(x2, [
  "One thing, drawn as two edges: dhw_temp \u2213 the error the model",
  "has actually made for a promise that far ahead, so it widens the",
  "further into the plan you look. One tooltip row, one \u00b1 figure.",
  "Absent entirely until there is history to draw it from.",
])}
</svg>
`;
}

// --- Run -------------------------------------------------------------------

const oneZone = renderChart(ONE_ZONE);
const houseOnly = renderChart(TWO_ZONE, onlySeries("house_temp"));
const bandOnly = renderChart(ONE_ZONE, onlySeries("dhw_temp"));

const figures = [
  ["chart-anatomy.svg", anatomy(oneZone)],
  ["chart-dashed-lines.svg", dashedPair(houseOnly, bandOnly)],
];
for (const [name, content] of figures) {
  fs.writeFileSync(path.join(OUT, name), content);
  console.log(`${name}: ${content.length} bytes`);
}
console.log("CARD FIGURES WRITTEN");
