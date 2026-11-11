// R10-CARD-VOICE (#2506): the harmony study's own harness
// (probe/card-harmony-design 6aea0d10, docs/design/harmony/harness) driven in
// Chromium at 375 / 768 / 1280 px over the card at one git ref, light and dark,
// on every page -- the measurement the roster's H1-H4 carries name as control.
//
//    node dev/audit/harnesses/r10_card_harmony.mjs <ref> > <out.json>
//
// The ref's card and the study's harness are written to a fresh temporary
// tree with `git show` (the harness loads the card by relative path), so a base
// and a head are measured by the same driver. Per page and width it prints the
// dialog's base px, the HTML text nodes under the ramp's 12 px step, each named
// caption role's px, the setup drawing's disc px and glyph / box / pipe strokes,
// the savings replay's rendered label px, the health / advisor row's contrast
// (with and without a theme's --secondary-background-color), the health
// heading's weight, and on the card face every text node's px (the null arm).
// Needs Playwright's Chromium; no network.

import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const ref = process.argv[2];
if (!ref) { console.error("usage: r10_card_harmony.mjs <ref>"); process.exit(2); }
const HARNESS_REF = "6aea0d10b8f2e618d64c684755db9aaa0c624588";
const show = (spec) => execFileSync("git", ["show", spec], { maxBuffer: 1 << 26 });
const root = fs.mkdtempSync(path.join(os.tmpdir(), "r10-card-harmony-"));
const hx = path.join(root, "docs/design/harmony/harness");
const cardDir = path.join(root, "custom_components/heatpump_optimizer/www");
fs.mkdirSync(hx, { recursive: true });
fs.mkdirSync(cardDir, { recursive: true });
for (const f of ["harness.html", "states.js"]) {
  fs.writeFileSync(path.join(hx, f), show(`${HARNESS_REF}:docs/design/harmony/harness/${f}`));
}
fs.writeFileSync(path.join(cardDir, "heatpump-optimizer-card.js"),
  show(`${ref}:custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`));

const url = (q) => `file://${root}/docs/design/harmony/harness/harness.html?${q}`;
const ROLES = [".legend-note", ".hl-caveat", ".viewctl button", ".whatif .wi-hint",
  ".whatif .wi-group-title", ".setup-hint", ".setup-dest", ".adv-sub", ".adv-note", ".adv-basis",
  ".health-mark", ".layout-bar button", ".chip"];
(async () => {
  const b = await chromium.launch();
  const out = {};
  for (const w of [375, 768, 1280]) {
    for (const theme of ["light", "dark"]) {
      for (const page of ["tile", "plan", "setup", "savings", "advisor", "health"]) {
        for (const themed of theme === "dark" && (page === "health" || page === "advisor") ? [false, true] : [false]) {
          const p = await b.newPage({ viewport: { width: w, height: 900 } });
          await p.goto(url(`page=${page}&theme=${theme}`));
          if (themed) await p.evaluate(() => document.body.style.setProperty("--secondary-background-color", "#111111"));
          await p.waitForTimeout(250);
          const r = await p.evaluate((ROLES) => {
            const card = window.HPO_CARD; const sr = card.shadowRoot;
            const px = (el) => parseFloat(getComputedStyle(el).fontSize);
            const dlg = sr.querySelector("dialog[open]");
            const scope = dlg || sr;
            const html = [...scope.querySelectorAll("*")].filter((el) => !(el instanceof SVGElement) &&
              !["STYLE", "SCRIPT"].includes(el.tagName) && el.getClientRects().length &&
              [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()));
            const face = !dlg ? html.map((el) => `${el.tagName.toLowerCase()}.${[...el.classList].join(".")}=${px(el).toFixed(2)}`) : null;
            const roles = {};
            for (const sel of ROLES) {
              const els = [...scope.querySelectorAll(sel)].filter((e) => e.getClientRects().length);
              if (els.length) roles[sel] = [...new Set(els.map((e) => px(e).toFixed(2)))];
            }
            const res = { base: dlg ? px(dlg) : px(sr.host), below12: html.filter((e) => px(e) < 12 - 1e-6).length,
              htmlNodes: html.length, roles, face };
            const svg = scope.querySelector(".setup-svg");
            if (svg) {
              const vb = svg.viewBox.baseVal.width; const scale = svg.getBoundingClientRect().width / vb;
              const disc = svg.querySelector(".badge-disc");
              res.setup = { scale: +scale.toFixed(4),
                disc_px: disc ? +disc.getBoundingClientRect().width.toFixed(1) : null,
                glyph_stroke: (() => { const g = svg.querySelector(".type-badge path"); return g ? getComputedStyle(g).strokeWidth : null; })(),
                box_stroke: getComputedStyle(svg.querySelector(".setup-box")).strokeWidth,
                pipe_stroke: (() => { const q = svg.querySelector(".setup-pipe:not(.coil-pipe)"); return q ? getComputedStyle(q).strokeWidth : null; })(),
                chip_label_px: (() => { const t = svg.querySelector(".setup-chip-label"); return t ? +(parseFloat(getComputedStyle(t).fontSize) * scale).toFixed(2) : null; })(),
              };
            }
            const rep = scope.querySelector(".replay > svg");
            if (rep) {
              const vb = rep.viewBox.baseVal.width; const scale = rep.getBoundingClientRect().width / vb;
              const sizes = [...rep.querySelectorAll("text")].map((t) => parseFloat(getComputedStyle(t).fontSize) * scale);
              res.replay_label_px = sizes.length ? [+Math.min(...sizes).toFixed(2), +Math.max(...sizes).toFixed(2)] : null;
            }
            const row = scope.querySelector(".health-row, .adv-inbox-row");
            if (row) {
              const cs = getComputedStyle(row);
              const lum = (c) => { const m = c.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number).map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]; };
              const L1 = lum(cs.backgroundColor), L2 = lum(cs.color);
              res.row = { bg: cs.backgroundColor, ink: cs.color, contrast: +((Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05)).toFixed(2) };
            }
            const hh = scope.querySelector(".health-h");
            if (hh) res.health_h_weight = getComputedStyle(hh).fontWeight;
            return res;
          }, ROLES);
          out[`${w}/${theme}/${page}${themed ? "/themed" : ""}`] = r;
          await p.close();
        }
      }
    }
  }
  await b.close();
  fs.rmSync(root, { recursive: true, force: true });
  console.log(JSON.stringify(out, null, 1));
})();
