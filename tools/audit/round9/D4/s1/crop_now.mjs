// Evidence screenshot for D4-s1-05 (not a RESULT harness): crop of the expanded chart top at a given width.
// node tools/audit/round9/D4/s1/crop_now.mjs 375 empty -10 <out.png>   (HPO_PLANDATA, NODE_PATH, PLAYWRIGHT_BROWSERS_PATH as in sweep.mjs)
// crop around a text run in a given state, 3x DPR
import fs from "node:fs"; import { createRequire } from "node:module";
import { planStates, withActuals, historyApi, realisticHistory } from "../../../../../tests/card_rig.mjs";
const require = createRequire(import.meta.url); const { chromium } = require("playwright");
const plan = JSON.parse(fs.readFileSync(process.env.HPO_PLANDATA, "utf8"));
const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * 3600000;
const [w, mode, pan, out] = [Number(process.argv[2]), process.argv[3], Number(process.argv[4]), process.argv[5]];
const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: w, height: 812 }, deviceScaleFactor: 3 });
await ctx.clock.setFixedTime(FROZEN);
await ctx.route("http://hpo.test/**", (r) => r.fulfill({ contentType: "text/html", body: "<!doctype html><html><body style='margin:0;padding:8px;font-family:Liberation Sans,Arial'></body></html>" }));
const p = await ctx.newPage(); await p.goto("http://hpo.test/");
const api = mode === "empty" ? historyApi({}, {}) : historyApi(realisticHistory(FROZEN));
await p.exposeFunction("__api", async (m, q) => api.callApi(m, q));
await p.addScriptTag({ path: "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js" });
await p.evaluate(async ([st, cw, pan]) => { const c = document.createElement("heatpump-optimizer-card"); c.style.display="block"; c.style.width=cw+"px"; c.setConfig({type:"x"}); c.hass={states:st,language:"en",callApi:(m,q)=>window.__api(m,q)}; document.body.appendChild(c); c._onCardClick({}); c.view.panBy(pan*3600000); await new Promise(r=>setTimeout(r,500)); }, [withActuals(planStates(plan)), w-16, pan]);
await p.waitForTimeout(300);
const r = await p.evaluate(() => { const s=[...document.querySelector("heatpump-optimizer-card").shadowRoot.querySelectorAll("dialog .chartwrap")].pop(); const b=s.getBoundingClientRect(); return {x:b.x,y:b.y,w:b.width,h:Math.min(b.height,160)}; });
await p.screenshot({ path: out, clip: { x: r.x, y: r.y, width: r.w, height: r.h } });
await b.close();
