// R10-CARD-VOICE (#2506): the setup page's properties the owner's chosen design
// states (prototype 1, probe/card-symbols-design 2cc4d5eb, its NOTES.md), read
// on the card rig's own `coil` and `twoTank` fixtures in the coil's three
// states -- active, configured but not modelled, none.
//
//    python3 tests/plan_view.py                     # writes the plan payload
//    node dev/audit/harnesses/r10_card_voice_states.mjs <plandata.json>
//
// Run from a worktree root: that tree's card and rig are the ones loaded, so
// the same file measures a base and a head. One JSON line per state:
//   boxes               cards drawn;
//   badge_types         distinct type discs (0 before the design);
//   wood_badge          the wood tank's disc, "coil", "coil off" or "store";
//   coil_pipes_accent   pipes in the coil's accent class;
//   configure_buttons   Configure controls, and buttons_naming_page those whose
//                       own ink names the options page;
//   dhw_coil_lines      the hot water box's coil wording;
//   dest_caption        the line above the drawing that says where pages are.
// Counts only; no timing, no network.

import fs from "fs";
import path from "path";
const root = process.cwd();
const rig = await import(path.join(root, "tests/card_rig.mjs"));
const { CARD_PATH, DEFAULT_SPACE, makeCardContext, loadCard, planStates, qaTopologies, collect } = rig;
const plan = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const { ctx } = makeCardContext();
const Card = loadCard(ctx, fs.readFileSync(CARD_PATH, "utf8"));
const { coil, twoTank } = qaTopologies();
const page = (topo) => {
  const s = planStates(plan);
  s[DEFAULT_SPACE].attributes.setup_topology = JSON.parse(JSON.stringify(topo));
  const c = new Card();
  c.setConfig({ type: "custom:heatpump-optimizer-card" });
  c.hass = { states: s, callService: async () => {}, callWS: async () => { throw new Error("no"); } };
  c._onCardClick({}); c.dialog.page = "setup"; c._render();
  return { html: collect(c.shadowRoot).join("\n"), boxes: c.layoutEditor.boxes.length };
};
// Fixed markup is counted by string search, not by a regex literal: tests/card.mjs
// spells the same three as regexes, and this file must also run on a base tree.
const count = (s, lit) => s.split(lit).length - 1;
const states = {
  active: { ...coil, dhw_wood_coil_configured: true },
  off: { ...twoTank, dhw_wood_coil_configured: true },
  none: twoTank,
};
for (const [k, t] of Object.entries(states)) {
  const { html, boxes } = page(t);
  const dhw = html.split("<g>").find((g) => /setup-title[^>]*>Hot water tank</.test(g)) || "";
  console.log(JSON.stringify({
    state: k,
    boxes,
    badge_types: [...new Set([...html.matchAll(/data-type="([a-z_]+)"/g)].map((m) => m[1]))].length,
    wood_badge: ((html.split("<g>").find((g) => g.includes("Wood furnace tank")) || "")
      .match(/class="type-badge( off)?" data-type="([a-z_]+)"/) || ["", "", "none"])
      .slice(1).reverse().filter(Boolean).map((x) => x.trim()).join(" "),
    coil_pipes_accent: (html.match(/class="setup-pipe coil-pipe/g) || []).length,
    configure_buttons: count(html, 'class="setup-chip-hit"'),
    buttons_naming_page: (html.match(/class="setup-chip-page"/g) || []).length,
    dhw_coil_lines: [...dhw.matchAll(/<text class="setup-slot extra[^"]*"[^>]*>([^<]*)</g)].map((m) => m[1]),
    dest_caption: count(html, 'class="setup-dest"'),
  }));
}
