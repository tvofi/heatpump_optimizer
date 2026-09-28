// D4 round-4 — the real keyboard tab order, and what a focus ring looks like.
//
// METRIC: for a named card state, the sequence of elements real Tab presses
// actually focus (read through the shadow root with activeElement chaining),
// how many presses it takes to traverse the state once, whether the sequence
// ever leaves the expanded dialog while it is open, whether every focused
// element has an accessible name, and the measured outline/box-shadow the
// focus ring draws (0 px = a focused control a sighted keyboard user cannot
// locate).
//
// RUN (from the export root):
//   NODE_PATH=/private/tmp/hpo-pw/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers \
//   HPO_PLANDATA=/private/tmp/hpo-d4/plandata.json \
//     node tools/audit/round4/D4/keyboard_tab.mjs
//
// EXPECTED at baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 on the audit
// box (Apple M1, Chromium 131.0.6778.33): counts, tolerance +-0.
import { createRequire } from "node:module";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");
const OUT = path.join(__dirname, "out");
mkdirSync(OUT, { recursive: true });
const plan = JSON.parse(readFileSync(process.env.HPO_PLANDATA, "utf8"));
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");

const THEME = { "--primary-text-color": "#212121", "--secondary-text-color": "#727272",
  "--primary-color": "#03a9f4", "--card-background-color": "#ffffff",
  "--primary-background-color": "#fafafa", "--secondary-background-color": "#e5e5e5",
  "--divider-color": "rgba(0,0,0,.12)", "--error-color": "#db4437",
  "--warning-color": "#ffa600", "--success-color": "#43a047", "--text-primary-color": "#ffffff" };
const HA_CARD = `if(!customElements.get("ha-card")){customElements.define("ha-card",class extends HTMLElement{constructor(){super();this.attachShadow({mode:"open"}).innerHTML="<style>:host{background:var(--card-background-color,white);box-sizing:border-box;border-radius:12px;border:1px solid var(--divider-color,#e0e0e0);color:var(--primary-text-color);display:block;position:relative}</style><slot></slot>"}})}`;

const CASES = [
  { state: "plan_inline", vp: [1280, 800], tile: 500, presses: 25 },
  { state: "expanded_plan", vp: [1280, 800], tile: 500, presses: 60 },
  { state: "setup_two_tank", vp: [1280, 800], tile: 500, presses: 60 },
  { state: "expanded_plan", vp: [375, 812], tile: 359, presses: 60 },
  { state: "picker_open_filtered", vp: [1280, 800], tile: 500, presses: 40 },
];

const rows = [];
const browser = await chromium.launch();
try {
  for (const c of CASES) {
    const ctx = await browser.newContext({ viewport: { width: c.vp[0], height: c.vp[1] }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    const errs = [];
    page.on("pageerror", (e) => errs.push(String(e.message).slice(0, 160)));
    await page.goto("about:blank");
    await page.addStyleTag({ content:
      `:root{${Object.entries(THEME).map(([k, v]) => `${k}:${v}`).join(";")}}` +
      `html,body{margin:0;background:#fafafa;font-family:Roboto,-apple-system,sans-serif;font-size:14px}` +
      `#hpo-host{width:${c.tile}px;margin:0 auto}heatpump-optimizer-card{display:block}` });
    await page.addScriptTag({ content: HA_CARD });
    await page.addScriptTag({ path: CARD_SRC });
    await page.addScriptTag({ path: path.join(__dirname, "lib/measure.js") });
    await page.addScriptTag({ path: path.join(__dirname, "lib/states.js") });
    await page.evaluate(async ([n, p]) => { await window.__D4.STATES[n](p); }, [c.state, plan]);

    // Focus the document body, then Tab. activeElement has to be chased
    // through every shadow root or every hit inside the card reads as the
    // card host itself.
    await page.evaluate(() => { document.body.focus(); if (document.activeElement && document.activeElement.blur) {} });
    const seq = [];
    for (let i = 0; i < c.presses; i++) {
      await page.keyboard.press("Tab");
      const f = await page.evaluate(() => {
        let el = document.activeElement;
        const chain = [];
        while (el && el.shadowRoot && el.shadowRoot.activeElement) {
          chain.push(el.tagName.toLowerCase());
          el = el.shadowRoot.activeElement;
        }
        if (!el) return null;
        const cls = (el.getAttribute && el.getAttribute("class")) || "";
        const st = getComputedStyle(el);
        const b = el.getBoundingClientRect();
        const dlg = window.__card && window.__card.shadowRoot
          && window.__card.shadowRoot.querySelector("dialog.expanded");
        const dlgOpen = !!(dlg && dlg.open);
        const inDialog = !!(dlg && dlg.contains(el));
        // the focus ring, as drawn
        const ow = parseFloat(st.outlineWidth) || 0;
        const ostyle = st.outlineStyle;
        const shadow = st.boxShadow && st.boxShadow !== "none" ? st.boxShadow : "";
        return {
          tag: el.tagName.toLowerCase() + (cls ? "." + String(cls).trim().split(/\s+/)[0] : ""),
          name: el.getAttribute("aria-label") || (el.textContent || "").trim().slice(0, 28)
                || el.getAttribute("title") || "",
          role: el.getAttribute("role") || "",
          x: Math.round(b.left), y: Math.round(b.top),
          w: Math.round(b.width * 10) / 10, h: Math.round(b.height * 10) / 10,
          outline: ostyle === "none" ? 0 : ow, ring: shadow.slice(0, 60),
          dlgOpen, inDialog, chain: chain.join(">"),
        };
      });
      seq.push(f);
      if (seq.length > 2 && f && seq[0] && f.tag === seq[0].tag && f.x === seq[0].x && f.y === seq[0].y) break;
    }
    const real = seq.filter(Boolean).filter((s) => !/^(body|html)$/.test(s.tag));

    // FOCUS VISIBLE, by pixels. A computed outline/box-shadow read misses
    // both directions: the UA ring on a native input reports outline-style
    // "auto" with no usable width, and .setup-hit deliberately rings itself
    // with a stroke and a fill instead of an outline. The only honest
    // question is whether ANYTHING on screen changes when the control takes
    // keyboard focus -- which is what WCAG 2.4.7 asks.
    //
    // One forward pass, full-viewport frames: an unfocused reference frame
    // first, then one frame per Tab. The box is re-read AT THAT MOMENT, so a
    // dialog that scrolls the focused control into view cannot leave the
    // comparison measuring a stale rectangle (which is what a coordinates-
    // from-the-first-pass version of this did, and it reported every ring as
    // invisible including ones a screenshot plainly shows).
    const ringPixels = [];
    {
      await page.evaluate(() => {
        let el = document.activeElement;
        while (el && el.shadowRoot && el.shadowRoot.activeElement) el = el.shadowRoot.activeElement;
        if (el && el.blur) el.blur();
      });
      const base = (await page.screenshot({ fullPage: false })).toString("base64");
      await page.evaluate(([b64]) => {
        window.__base = b64;
        window.__diffRegion = async (b64b, box) => {
          const load = (b) => new Promise((ok, no) => { const im = new Image(); im.onload = () => ok(im); im.onerror = no; im.src = "data:image/png;base64," + b; });
          const [A, B] = await Promise.all([load(window.__base), load(b64b)]);
          const cv = document.createElement("canvas");
          cv.width = A.width; cv.height = A.height;
          const g = cv.getContext("2d", { willReadFrequently: true });
          g.drawImage(A, 0, 0); const a = g.getImageData(0, 0, cv.width, cv.height).data;
          g.clearRect(0, 0, cv.width, cv.height);
          g.drawImage(B, 0, 0); const b2 = g.getImageData(0, 0, cv.width, cv.height).data;
          const dpr = A.width / innerWidth;
          const x0 = Math.max(0, Math.floor((box.x - 8) * dpr));
          const x1 = Math.min(cv.width - 1, Math.ceil((box.x + box.w + 8) * dpr));
          const y0 = Math.max(0, Math.floor((box.y - 8) * dpr));
          const y1 = Math.min(cv.height - 1, Math.ceil((box.y + box.h + 8) * dpr));
          let n = 0, tot = 0;
          for (let y = y0; y <= y1; y++) {
            for (let x = x0; x <= x1; x++) {
              const i = (y * cv.width + x) * 4;
              tot += 1;
              if (Math.abs(a[i] - b2[i]) + Math.abs(a[i + 1] - b2[i + 1]) + Math.abs(a[i + 2] - b2[i + 2]) > 24) n += 1;
            }
          }
          return { changed: n, total: tot };
        };
      }, [base]);
      for (let i = 0; i < c.presses; i++) {
        await page.keyboard.press("Tab");
        const cur = await page.evaluate(() => {
          let el = document.activeElement;
          while (el && el.shadowRoot && el.shadowRoot.activeElement) el = el.shadowRoot.activeElement;
          if (!el || /^(BODY|HTML)$/.test(el.tagName)) return null;
          const cls = (el.getAttribute && el.getAttribute("class")) || "";
          const b = el.getBoundingClientRect();
          return { tag: el.tagName.toLowerCase() + (cls ? "." + String(cls).trim().split(/\s+/)[0] : ""),
                   name: el.getAttribute("aria-label") || (el.textContent || "").trim().slice(0, 28) || "",
                   fv: el.matches(":focus-visible"),
                   box: { x: b.left, y: b.top, w: b.width, h: b.height } };
        });
        if (!cur) continue;
        if (ringPixels.some((r) => r.tag === cur.tag && r.name === cur.name && r.x === Math.round(cur.box.x) && r.y === Math.round(cur.box.y))) break;
        const shot = (await page.screenshot({ fullPage: false })).toString("base64");
        const d = await page.evaluate(([b64, box]) => window.__diffRegion(b64, box), [shot, cur.box]);
        ringPixels.push({ tag: cur.tag, name: cur.name, fv: cur.fv,
                          x: Math.round(cur.box.x), y: Math.round(cur.box.y), ...d });
      }
    }
    const invisibleFocus = ringPixels.filter((r) => r.changed === 0);
    const dlgOpen = real.some((s) => s.dlgOpen);
    const escaped = dlgOpen ? real.filter((s) => s.dlgOpen && !s.inDialog) : [];
    const unnamed = real.filter((s) => !s.name);
    const noRing = real.filter((s) => s.outline === 0 && !s.ring);
    // visual order vs tab order: a pair that tabs backwards up the page
    let backJumps = 0;
    for (let i = 1; i < real.length; i++) {
      const a = real[i - 1], b = real[i];
      if (b.y < a.y - 4) backJumps += 1;
    }
    rows.push({ ...c, ringPixels, invisibleFocus: invisibleFocus.length,
                invisibleFocusList: [...new Set(invisibleFocus.map((r) => r.tag))],
                presses_used: seq.length, focused: real.length,
                dialogOpen: dlgOpen, escapedDialog: escaped.length,
                unnamed: unnamed.length, unnamedList: unnamed.map((u) => u.tag),
                noFocusRing: noRing.length, noFocusRingList: [...new Set(noRing.map((u) => u.tag))],
                backJumps, pageErrors: errs.length, seq: real });
    await ctx.close();
  }
} finally { await browser.close(); }

writeFileSync(path.join(OUT, "keyboard_tab.json"), JSON.stringify(rows, null, 1));
for (const r of rows) {
  console.log(`RESULT ${r.state}@${r.vp.join("x")} focused=${r.focused} dialog_open=${r.dialogOpen} escaped_dialog=${r.escapedDialog} unnamed=${r.unnamed} css_no_ring=${r.noFocusRing} PIXEL_invisible_focus=${r.invisibleFocus} back_jumps=${r.backJumps} page_errors=${r.pageErrors}`);
  if (r.noFocusRingList.length) console.log("    css says no outline/shadow: " + r.noFocusRingList.join(", "));
  if (r.invisibleFocusList.length) console.log("    NOTHING CHANGES ON SCREEN when focused: " + r.invisibleFocusList.join(", "));
  const px = (r.ringPixels || []).filter((x) => x.changed != null).sort((a, b) => a.changed - b.changed).slice(0, 4);
  console.log("    weakest rings: " + px.map((x) => `${x.tag}=${x.changed}px`).join(", "));
  if (r.unnamedList.length) console.log("    unnamed: " + [...new Set(r.unnamedList)].join(", "));
}
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT thread_factor=1.00 (no CPU-time metric)");
console.log("RESULT swapins=0 (not a memory metric)");
