// D12-s2 card surface driver (called by surfaces.py; not run alone).
// Usage: node dev/audit/rounds/round11/D12/s2/card_surface.mjs <card.js> <states.json>
// Loads the card source given, builds it the way Lovelace does with the states a real
// setup + cycle published (surfaces.py writes them), renders the inline card and each dialog
// page, and prints one JSON line: {pages: {name: {ok, error, html_len, lower_zone}}}.
// lower_zone counts the setup page's drawn "Lower floor" box (en label of places.lower_zone).
import fs from "fs";
import { makeCardContext, loadCard, collect, buildCard } from "../../../../../../tests/card_rig.mjs";

const [cardPath, statesPath] = process.argv.slice(2);
const states = JSON.parse(fs.readFileSync(statesPath, "utf8"));
const out = { pages: {} };
let Card;
try {
  const { ctx } = makeCardContext();
  Card = loadCard(ctx, fs.readFileSync(cardPath, "utf8"));
} catch (e) {
  out.load_error = String(e && e.message || e);
  console.log(JSON.stringify(out));
  process.exit(0);
}
const pages = ["inline", "plan", "savings", "advisor", "health", "setup"];
for (const page of pages) {
  const r = { ok: false, error: null, html_len: 0, lower_zone: 0 };
  try {
    const c = buildCard(Card, states, {});
    if (page !== "inline") {
      if (c.dialog) c.dialog.open(); else c._openExpanded();
      if (c.dialog) c.dialog.page = page; else c._dialogPage = page;
      c._render();
    }
    const html = collect(c.shadowRoot || c).join("\n");
    r.html_len = html.length;
    r.lower_zone = (html.match(/Lower floor/g) || []).length;
    r.ok = html.length > 0;
  } catch (e) {
    r.error = String(e && e.stack || e).slice(0, 400);
  }
  out.pages[page] = r;
}
console.log(JSON.stringify(out));
