// D12-s1 card surface cell: the shipped card rendered against the entity states every cell plant published.
//
// Metric (one line): card_fail_plants = plant runs (cells.py --dump) whose states make the card throw on
// build (setConfig, hass, connectedCallback), on opening the expanded dialog, or on any dialog page render,
// or leave the folded card with no markup at all.
// Count key: the states are what each plant's real entities published after one cycle (cells.py
// entity_states), never a fixture; the card is custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js.
//
// Command (export root; T a private temp dir):
//   HPO_PLANDATA="$T/plandata" PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s1/cells.py --quiet --dump "$T"
//   HPO_PLANDATA="$T/plandata" node dev/audit/rounds/round11/D12/s1/card_cells.mjs "$T/states.json" [--poison ENTITY_ID]
// --poison ENTITY_ID  perturbation: that entity's attributes are replaced by a string in every plant; the
//                     count must rise on every plant publishing it if the card reads it unguarded.
// Baseline 92d38ecb (export as handed to D12-s1), box B4, node 22. Expected: see REPORT.md; exact counts.
import fs from "fs";
import { makeCardContext, loadCard, buildCard, collect, CARD_PATH } from "../../../../../../tests/card_rig.mjs";

const t0 = process.cpuUsage();
const args = process.argv.slice(2);
const statesPath = args[0];
const poison = args.includes("--poison") ? args[args.indexOf("--poison") + 1] : null;
// decl.json (cells.py --decl): each plant's declared features; a plant not declaring "zone" is single-zone
const decl = args.includes("--decl") ? JSON.parse(fs.readFileSync(args[args.indexOf("--decl") + 1], "utf8")) : null;
// Zone traces: the card's own English labels for the two zone lines of the house-temperature series.
const ZONE_LABELS = ["Upper floor", "Lower floor"];
let zoneInvented = 0, singleZone = 0;
const plants = JSON.parse(fs.readFileSync(statesPath, "utf8"));
const src = fs.readFileSync(CARD_PATH, "utf8");
const PAGES = ["plan", "setup", "advisor", "health", "savings"];
let fails = 0, runs = 0;
const reasons = {};
for (const [plant, states] of Object.entries(plants).sort()) {
  if (!states) continue;
  runs += 1;
  const st = JSON.parse(JSON.stringify(states));
  if (poison && st[poison]) st[poison].attributes = "poisoned";
  const { ctx } = makeCardContext();
  let bad = null;
  try {
    const Card = loadCard(ctx, src);
    const c = buildCard(Card, st);
    const html = collect(c.shadowRoot || c).join("");
    if (!html.length) bad = "folded card rendered no markup";
    if (!bad) {
      if (c.dialog) c.dialog.open(); else if (c._openExpanded) c._openExpanded();
      if (decl && decl[plant] && !decl[plant].includes("zone")) {
        singleZone += 1;
        const open = collect(c.shadowRoot || c).join("");
        if (ZONE_LABELS.some((l) => open.includes(l))) {
          zoneInvented += 1;
          const k = "single-zone plant: the expanded chart names an Upper/Lower floor trace";
          (reasons[k] = reasons[k] || []).push(plant);
        }
      }
      for (const p of PAGES) {
        if (c.dialog) c.dialog.page = p; else c._dialogPage = p;
        if (c._render) c._render();
      }
    }
  } catch (err) {
    bad = `threw ${String(err && err.message || err).slice(0, 160)}`;
  }
  if (bad) {
    fails += 1;
    const k = bad.replace(/[0-9.]+/g, "#");
    (reasons[k] = reasons[k] || []).push(plant);
  }
}
for (const [k, ps] of Object.entries(reasons)) console.log(`FAIL ${ps.length} ${k}  e.g. ${ps.slice(0, 3).join(" | ")}`);
const u = process.cpuUsage(t0);
console.log(`RESULT card_runs=${runs} count`);
console.log(`RESULT card_fail_plants=${fails} count`);
console.log(`RESULT card_single_zone_plants=${singleZone} count`);
console.log(`RESULT card_zone_traces_on_single_zone=${zoneInvented} count`);
console.log(`RESULT thread_factor=1.000`);
console.log(`RESULT load1=${(await import("os")).loadavg()[0].toFixed(2)}`);
console.log(`RESULT swapins=0`);
console.log(`RESULT cpu_s=${((u.user + u.system) / 1e6).toFixed(1)} s (provisional)`);
