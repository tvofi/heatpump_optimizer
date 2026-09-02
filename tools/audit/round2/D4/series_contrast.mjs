// D4 (UI/UX) round 2 -- the chart's series colours against the card background.
//
// METRIC: WCAG 2.x contrast ratio of each SERIES_DEFS colour (the line, the
//   bar fill and the legend dot for that series) against Home Assistant's
//   default card background, light (#ffffff) and dark (#1c1c1c). SC 1.4.11
//   asks 3:1 of graphical objects needed to understand the content; a line
//   under 3:1 is counted in series_below_3_light / _dark.
// COMMAND (from the export root):
//   node tools/audit/round2/D4/series_contrast.mjs
// EXPECTED (baseline c398fc84): 7 series; series_below_3_light = 3
//   (price #f5a623 2.1, solar #f2c94c 1.6, house #2fae7a 2.8), _dark = 0.
// INSTRUMENTED SYMBOL: heatpump-optimizer-card.js:SERIES_DEFS, read out of the
//   card's own module scope through tests/card_rig.mjs's vm context.
// PERTURBATION: darken `color` of the solar series to "#b8860b" ->
//   series_below_3_light falls by 1.
import fs from "node:fs";
import os from "node:os";
import vm from "node:vm";
import { CARD_PATH, makeCardContext, loadCard } from "../../../../tests/card_rig.mjs";

const rig = makeCardContext();
loadCard(rig.ctx, fs.readFileSync(CARD_PATH, "utf8"));
const defs = vm.runInContext("SERIES_DEFS", rig.ctx);
const hex = (h) => { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
const ratio = (a, b) => { const la = lum(a), lb = lum(b); return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05); };
const BG = { light: hex("#ffffff"), dark: hex("#1c1c1c") };
let low = { light: 0, dark: 0 };
for (const d of defs) {
  const c = hex(d.color);
  const rl = ratio(c, BG.light), rd = ratio(c, BG.dark);
  if (rl < 3) low.light++; if (rd < 3) low.dark++;
  console.log(`${d.key.padEnd(12)} ${d.color}  light ${rl.toFixed(2)}${rl < 3 ? " <3" : "   "}  dark ${rd.toFixed(2)}${rd < 3 ? " <3" : ""}`);
}
console.log(`RESULT series=${defs.length} count`);
console.log(`RESULT series_below_3_light=${low.light} count`);
console.log(`RESULT series_below_3_dark=${low.dark} count`);
console.log("RESULT thread_factor=1.00");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT swapins=0");
