// Reviewer-built harness (not the finder's: none committed): render healthModelHtml
// for a stub plan and print the heat_loss bar width.
import fs from "fs"; import vm from "vm"; import path from "path";
const root = process.argv[2];
const { makeCardContext } = await import(path.join(root, "tests/card_rig.mjs"));
const made = makeCardContext();
const ctx = made.ctx || made;
vm.runInContext(fs.readFileSync(path.join(root, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"), "utf8"), ctx);
const H = vm.runInContext("healthModelHtml", ctx);
const SFX = vm.runInContext("HEALTH_MODEL_SUFFIX", ctx);
const mk = ({ meter, learned, phase, progress, ages }) => ({
  statEntity: (s) => s === SFX ? { state: "learned", attributes: {
    heat_loss_w_per_k: 142, heat_loss: { scale: 1.08, samples: learned ? 21 : 3, learned },
    learner_progress: { house: { phase, progress, samples: 10 } } } } : null,
  attrRaw: (k, d) => k === "setup_topology" ? { slots: [{ key: "heat_pump_power_entity", entity: meter ? "sensor.p" : null }] } : d,
  resolveEntity: () => ages ? "sensor.hpo_space_plan" : null,
  stateOf: () => ages ? { attributes: { input_ages_minutes: ages } } : null,
});
const bar = (p) => { const h = H(p); const m = /data-model-row="heat_loss"[\s\S]*?model-bar[^>]*><span style="width:(\d+)%"/.exec(h); const d = /data-model-row="heat_loss"[\s\S]*?adv-sub">([^<]*)</.exec(h); return `${m ? m[1] : "none"}% | ${d ? d[1] : "-"}`; };
const cases = {
  "nometer-converged": { meter: false, learned: true, phase: "settled", progress: 1 },
  "metered-converged": { meter: true, learned: true, phase: "settled", progress: 1 },
  "nometer-unconverged": { meter: false, learned: false, phase: "counting", progress: 0.4 },
  "metered-unconverged": { meter: true, learned: false, phase: "counting", progress: 0.4 },
  "nometer-zero-share": { meter: false, learned: false, phase: "waiting", progress: 0 },
  "metered-zero-share": { meter: true, learned: false, phase: "waiting", progress: 0 },
};
for (const [k, c] of Object.entries(cases)) console.log(`RESULT ${process.argv[3]} ${k}: bar ${bar(mk(c))}`);
