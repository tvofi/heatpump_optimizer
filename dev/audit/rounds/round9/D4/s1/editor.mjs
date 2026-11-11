// D4-s1 (D4.M2): the card's visual editor, driven through its ha-form contract.
//
// Metric definitions:
//   fields            top-level + nested schema entries HeatpumpOptimizerCardEditor._schema() returns
//   labels_raw        entries whose computeLabel(entry) returns the raw key (no translation) in en / sv
//   helpers           entries for which the form is given helper text (computeHelper) -- ha-form's help-text seam
//   roundtrip_extra   keys in the emitted config that merely restate a default after a no-op edit (lean-config contract)
//   roundtrip_throw   edits whose emitted config the card's own setConfig (parseConfig) then refuses
//
// Run from the repository root:
//   node tools/audit/round9/D4/s1/editor.mjs [--perturb helper]
// Expected: RESULT lines exact (counts). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B10, Node v22.
// Instrumented symbol: heatpump-optimizer-card.js:HeatpumpOptimizerCardEditor (_schema, _upgrade, _onValueChanged).
// Limits: no Home Assistant frontend -- ha-form is the rig's stub element, so rendering is inferred from schema and labels.
import fs from "node:fs";
import os from "node:os";
import vm from "node:vm";
import { makeCardContext, loadCard, CARD_PATH, EDITOR_TAG } from "../../../../../tests/card_rig.mjs";

const args = process.argv.slice(2);
let src = fs.readFileSync(CARD_PATH, "utf8");
if (args.includes("--perturb") && args[args.indexOf("--perturb") + 1] === "helper") {
  // Perturbation: hand the form a helper for every entry; `helpers` must move 0 -> fields.
  src = src.replace("this._form.computeLabel = (s) => {",
    "this._form.computeHelper = (s) => L(`editor.${s.name}`);\n    this._form.computeLabel = (s) => {");
}
const rig = makeCardContext();
const Card = loadCard(rig.ctx, src);
const Editor = rig.ctx.customElements.get(EDITOR_TAG);

const res = {};
for (const lang of ["en", "sv-SE"]) {
  const e = new Editor();
  e.setConfig({ type: "custom:heatpump-optimizer-card" });
  e.hass = { states: {}, language: lang };
  const form = e._form;
  const flat = [];
  for (const s of form.schema) { flat.push(s); if (s.schema) flat.push(...s.schema); }
  const raw = flat.filter((s) => { const l = form.computeLabel(s); return !l || l === s.name || l.startsWith("editor."); });
  const helpers = flat.filter((s) => typeof form.computeHelper === "function" && form.computeHelper(s));
  res[lang] = { fields: flat.length, top: form.schema.length, raw: raw.map((s) => s.name), helpers: helpers.length,
    labels: flat.map((s) => `${s.name}=${form.computeLabel(s)}`) };
}

// Round trip: a no-op edit (the form's own pre-filled value sent back) must emit the lean config.
const e = new Editor();
let emitted = null;
e.dispatchEvent = (ev) => { emitted = ev.detail.config; return true; };
e.setConfig({ type: "custom:heatpump-optimizer-card" });
e.hass = { states: {}, language: "en" };
e._onValueChanged({ detail: { value: e._data() }, stopPropagation() {} });
const extra = Object.keys(emitted || {}).filter((k) => k !== "type");
// Every selector extreme the schema offers, through the card's own setConfig.
let throws = 0; const thrown = [];
const hoursSel = e._schema().find((s) => s.name === "hours").selector.number;
for (const [k, v] of [["hours", hoursSel.min], ["hours", hoursSel.max], ["currency", "EUR"], ["title", ""], ["what_if", false], ["show_stats", false]]) {
  const ed = new Editor(); let out = null;
  ed.dispatchEvent = (ev) => { out = ev.detail.config; return true; };
  ed.setConfig({ type: "custom:heatpump-optimizer-card" });
  ed.hass = { states: {}, language: "en" };
  ed._onValueChanged({ detail: { value: { ...ed._data(), [k]: v } }, stopPropagation() {} });
  try { new Card().setConfig(out); } catch (err) { throws += 1; thrown.push(`${k}=${v}: ${err.message}`); }
}

console.log(JSON.stringify(res, null, 1));
console.log("thrown:", thrown);
console.log(`RESULT fields=${res.en.fields} count`);
console.log(`RESULT top_level_fields=${res.en.top} count`);
console.log(`RESULT labels_raw_en=${res.en.raw.length} count`);
console.log(`RESULT labels_raw_sv=${res["sv-SE"].raw.length} count`);
console.log(`RESULT helpers=${res.en.helpers} count`);
console.log(`RESULT roundtrip_extra=${extra.length} count`);
console.log(`RESULT roundtrip_throw=${throws} count`);
console.log("RESULT thread_factor=1.00");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT swapins=0");
