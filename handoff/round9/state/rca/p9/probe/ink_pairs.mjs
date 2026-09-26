// Probe: for every pair of chart <text> runs whose layout boxes intersect,
// is the INK shared? Isolates each run by hiding every other text, screenshots
// the pair's union box at DSF 2 and intersects the two ink masks.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const { PNG } = (() => { try { return require("pngjs"); } catch { return {}; } })();
const REPO = process.argv[2];
const rig = await import(path.join(REPO, "tests/card_rig.mjs"));
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const CARD = path.join(REPO, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");
const browser = await chromium.launch();
const out = [];
for (const [vw, expand, live] of [[1280, true, false], [375, true, false], [1280, false, true], [375, false, true]]) {
  const ctx = await browser.newContext({ viewport: { width: vw, height: 800 }, deviceScaleFactor: 2 });
  await ctx.clock.setFixedTime(Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600000);
  const page = await ctx.newPage();
  await page.goto("about:blank");
  await page.addScriptTag({ path: CARD });
  await page.evaluate(() => { if (!customElements.get("ha-card")) customElements.define("ha-card", class extends HTMLElement {
    constructor() { super(); this.attachShadow({ mode: "open" }).innerHTML = "<style>:host{display:block;background:#fff}</style><slot></slot>"; } }); });
  const st = live ? rig.withActuals(rig.planStates(plan)) : rig.planStates(plan);
  await page.evaluate(async ([st, w, expand]) => {
    const s = document.createElement("style");
    s.textContent = `body{margin:0 8px;font-family:"Liberation Sans",sans-serif}heatpump-optimizer-card{display:block;width:${w}px}`;
    document.head.appendChild(s);
    const c = document.createElement("heatpump-optimizer-card");
    c.setConfig({ type: "custom:heatpump-optimizer-card", what_if: true });
    c.hass = { states: st, language: "en" };
    document.body.appendChild(c); window.__c = c;
    await new Promise((r) => setTimeout(r, 100));
    if (expand) c._onCardClick({});
    await new Promise((r) => setTimeout(r, 150));
  }, [st, vw - 16, expand]);
  const pairs = await page.evaluate(() => {
    const root = window.__c.shadowRoot;
    const svg = [...root.querySelectorAll(".chartwrap svg")].pop();
    const ts = [...svg.querySelectorAll("text")].filter((t) => t.textContent.trim() && t.getBoundingClientRect().width > 0);
    ts.forEach((t, i) => t.setAttribute("data-probe", i));
    const res = [];
    for (let i = 0; i < ts.length; i++) for (let j = i + 1; j < ts.length; j++) {
      const a = ts[i].getBoundingClientRect(), b = ts[j].getBoundingClientRect();
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 2 && oy > 2) res.push({ i, j, a: ts[i].textContent.trim(), b: ts[j].textContent.trim(), ox: +ox.toFixed(1), oy: +oy.toFixed(1),
        clip: { x: Math.min(a.left, b.left) - 2, y: Math.min(a.top, b.top) - 2, width: Math.max(a.right, b.right) - Math.min(a.left, b.left) + 4, height: Math.max(a.bottom, b.bottom) - Math.min(a.top, b.top) + 4 } });
    }
    return res;
  });
  for (const p of pairs) {
    const masks = [];
    for (const k of [p.i, p.j]) {
      await page.evaluate((k) => {
        const svg = [...window.__c.shadowRoot.querySelectorAll(".chartwrap svg")].pop();
        for (const el of svg.querySelectorAll("*")) if (el.tagName !== "svg" && el.tagName !== "text" && !el.closest("text")) el.style.visibility = "hidden";
        for (const t of svg.querySelectorAll("text")) t.style.visibility = t.getAttribute("data-probe") === String(k) ? "visible" : "hidden";
      }, k);
      const buf = await page.screenshot({ clip: p.clip });
      masks.push(buf);
    }
    await page.evaluate(() => { for (const el of window.__c.shadowRoot.querySelectorAll(".chartwrap svg *")) el.style.visibility = ""; });
    // decode via the browser: draw both PNGs to canvas and intersect dark pixels
    const shared = await page.evaluate(async ([a, b]) => {
      const load = (u) => new Promise((ok) => { const im = new Image(); im.onload = () => ok(im); im.src = u; });
      const [ia, ib] = [await load(a), await load(b)];
      const px = (im) => { const c = document.createElement("canvas"); c.width = im.width; c.height = im.height; const x = c.getContext("2d"); x.drawImage(im, 0, 0); return x.getImageData(0, 0, im.width, im.height).data; };
      const da = px(ia), db = px(ib); let n = 0, na = 0, nb = 0;
      for (let q = 0; q < da.length; q += 4) {
        const inkA = da[q] + da[q + 1] + da[q + 2] < 600, inkB = db[q] + db[q + 1] + db[q + 2] < 600;
        na += inkA; nb += inkB; if (inkA && inkB) n++;
      }
      return { shared: n, inkA: na, inkB: nb };
    }, ["data:image/png;base64," + masks[0].toString("base64"), "data:image/png;base64," + masks[1].toString("base64")]);
    out.push({ vw, expand, live, a: p.a, b: p.b, box: `${p.ox}x${p.oy}`, ...shared });
  }
  await ctx.close();
}
await browser.close();
for (const r of out) console.log(JSON.stringify(r));
