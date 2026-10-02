// Reviewer's own probe (not the finder's, not the fixer's): the shipped
// stylesheet painted under a dark Home Assistant theme with no `modes.dark`,
// for which HA's frontend reports hass.themes.darkMode === false.
import fs from "fs"; import vm from "vm"; import path from "path";
import { createRequire } from "module";
const require = createRequire("/tmp/claude-0/pwlane/");
const { chromium } = require("playwright");
const tree = process.argv[2];
const { makeCardContext } = await import(path.join(tree, "tests/card_rig.mjs"));
const { ctx } = makeCardContext();
vm.runInContext(fs.readFileSync(path.join(tree, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"), "utf8"), ctx);
const css = vm.runInContext("cardStyleBlock", ctx)(false);
const theme = process.argv[3] === "default"
  ? "--primary-text-color:#212121;--secondary-text-color:#727272;--card-background-color:#ffffff;--divider-color:rgba(0,0,0,.12)"
  : "--primary-text-color:#e1e1e1;--secondary-text-color:#9b9b9b;--card-background-color:#1c1c1c;--divider-color:rgba(225,225,225,.12)";
const markup = `<ha-card style="display:block;background:var(--card-background-color)">
 <div class="header"><div class="head-main"><span class="title">Heat pump</span>
 <span class="status-pill tone-idle" data-status="idle">Idle</span></div></div>
 <div class="tiles"><div class="tile" data-tile="energy"><span class="tile-k">Planned heating</span>
 <span class="tile-v"><span class="tile-n">12.3</span><span class="tile-u">kWh</span></span></div></div>
 <div class="headline"><div class="hl-stats"><span class="hl-stat"><span class="hl-label">Savings</span>
 <span class="hl-value">12.00 SEK</span></span></div></div></ha-card>`;
const b = await chromium.launch(); const p = await b.newPage();
await p.setContent(`<html style="${theme}"><body style="background:var(--card-background-color)"><div id=h></div></body></html>`);
const out = await p.evaluate(([css, markup]) => {
  const sr = document.getElementById("h").attachShadow({ mode: "open" });
  sr.innerHTML = css + markup;
  const rgb = (s) => s.match(/[\d.]+/g).slice(0, 4).map(Number);
  const lum = ([r, g, b]) => [r, g, b].map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; })
    .reduce((a, v, i) => a + v * [0.2126, 0.7152, 0.0722][i], 0);
  const bg = (el) => { for (; el; el = el.parentElement || el.getRootNode().host) {
    const c = rgb(getComputedStyle(el).backgroundColor); if (c.length < 4 || c[3] > 0) return c; } return [255,255,255]; };
  const res = [];
  for (const sel of [".title", ".status-pill", ".tile-k", ".tile-n", ".tile-u", ".hl-label", ".hl-value"]) {
    const el = sr.querySelector(sel); const fg = rgb(getComputedStyle(el).color); const bk = bg(el);
    const [l1, l2] = [lum(fg), lum(bk)].sort((a, b) => b - a);
    res.push(`${sel.padEnd(14)} fg rgb(${fg.slice(0,3)}) on rgb(${bk.slice(0,3)}) = ${((l1 + .05) / (l2 + .05)).toFixed(2)}:1`);
  }
  return res;
}, [css, markup]);
console.log(out.join("\n")); await b.close();
