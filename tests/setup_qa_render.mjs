// Visual-QA renderer: builds the card with the same DOM stub as card.mjs,
// renders the setup page for three topologies, and saves each page's
// setup <svg> as a self-contained .svg file (card CSS inlined, HA vars
// resolved to their light-mode fallbacks) for designer review.
import fs from "fs";
import path from "path";
import crypto from "crypto";
import { fileURLToPath } from "url";
import {
  CARD_PATH, DEFAULT_SPACE, makeCardContext, loadCard, collect, planStates,
  qaTopologies,
} from "./card_rig.mjs";

// Same plan-payload resolution as tests/card.mjs: argv, HPO_PLANDATA, then a
// default derived from this checkout's tests/ directory (what plan_view.py
// writes), so the render never silently uses another checkout's stale file.
const _testsDir = path.dirname(fileURLToPath(import.meta.url));
const _defaultPlan = path.join(
  "/tmp",
  `plandata-${crypto.createHash("sha256").update(_testsDir).digest("hex").slice(0, 12)}.json`
);
const _planPath = process.argv[2] || process.env.HPO_PLANDATA || _defaultPlan;
const plan = JSON.parse(fs.readFileSync(_planPath, "utf8"));

// --- The rig: shared with tests/card.mjs and tests/card_drift.mjs ----------
// This file once carried a verbatim copy of an EARLIER revision of card.mjs's
// DOM stub, silently drifting with every extension (#101). The stub, the vm
// context around it, the plan-sensor states and the three topologies below
// all live in tests/card_rig.mjs now; the renderer and the tests can no
// longer disagree about what the card was given.
const { ctx } = makeCardContext();
const cardSrc = fs.readFileSync(CARD_PATH, "utf8");
const Card = loadCard(ctx, cardSrc);

const mkStates = () => planStates(plan);

// --- The three topologies (tests/card_rig.mjs) ------------------------------
const { base, twoTank, coil } = qaTopologies();

// --- Extract the setup CSS from the card source and resolve HA vars ---------
const styleBlock = (cardSrc.match(/\.setup-page[\s\S]*?\.setup-pipe\.invalid \{[\s\S]*?\}/) || [""])[0];
const layoutCss = styleBlock
  .replace(/var\(--primary-text-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--secondary-text-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--primary-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--error-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--card-background-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--divider-color,\s*([^)]+)\)/g, "$1")
  .replace(/var\(--primary-text-color\)/g, "#212121")
  .replace(/var\(--secondary-text-color\)/g, "#757575");

const outDir = path.resolve(process.cwd(), "../setup-qa");
fs.mkdirSync(outDir, { recursive: true });

function renderTopo(name, topo) {
  const states = mkStates();
  states[DEFAULT_SPACE].attributes.setup_topology = topo;
  states["sensor.livingroom"] = { state: "21.3", attributes: { unit_of_measurement: "°C" } };
  states["sensor.tank"] = { state: "47.5", attributes: { unit_of_measurement: "°C" } };
  states["sensor.outside"] = { state: "unavailable", attributes: {} };
  const card = new Card();
  card.setConfig({ type: "custom:heatpump-optimizer-card" });
  card.hass = { states };
  if (card.connectedCallback) card.connectedCallback();
  card.hass = { states };
  card._onCardClick({});
  card.dialog.page = "setup";
  card._render();
  const page = collect(card.shadowRoot).join("\n");
  const svg = (page.match(/<svg class="setup-svg[\s\S]*?<\/svg>/) || [""])[0];
  if (!svg) { console.error(`FAIL: no setup svg for ${name}`); process.exit(1); }
  // Self-contained file: white ground + inlined card CSS with vars
  // resolved, spliced in right after the opening <svg ...> tag.
  const openEnd = svg.indexOf(">");
  const inject =
    `<style>svg { background: #fff; font-family: sans-serif; }\n${layoutCss}</style>` +
    `<rect x="0" y="0" width="100%" height="100%" fill="#ffffff" />`;
  const withStyle = openEnd < 0 ? svg : svg.slice(0, openEnd + 1) + inject + svg.slice(openEnd + 1);
  const file = path.join(outDir, `${name}.svg`);
  fs.writeFileSync(file, withStyle);
  console.log(`${name}: ${file}`);
  console.log(`  boxes: ${JSON.stringify(card.layout.boxes)}`);
  return { svg, boxes: card.layout.boxes };
}

renderTopo("coil", coil);
renderTopo("two-tank", twoTank);
renderTopo("single-buffer", base);
console.log("QA RENDERS WRITTEN");
