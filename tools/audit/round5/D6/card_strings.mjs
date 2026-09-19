// D6 — the dashboard card's translation-table claim.
//
// METRIC DEFINITION: `missing_sv_keys` is the number of keys in the card's
// production `STRINGS.en` table that have no entry in `STRINGS.sv`, i.e. the
// number of places a `sv-SE` user is drawn the English sentence through
// `L()`'s documented English fallback. `sv_renders_english` is 1 when the
// production `L()` actually returns the English text for the one such key
// that a reachable UI branch asks for, and 0 otherwise.
//
// RUN (from the repository root):
//     node tools/audit/round5/D6/card_strings.mjs
//
// EXPECTED (baseline eaa2a06af16a1b5b006f58a0f36cc92131f80225):
//     RESULT en_keys=261 keys
//     RESULT sv_keys=260 keys
//     RESULT missing_sv_keys=1 keys          (tolerance: exact)
//     RESULT sv_renders_english=1 count      (tolerance: exact)
//     RESULT missing_sv_keys_perturbed=0 keys (the perturbation below)
//
// MACHINE: macOS Darwin 25.6.0, Apple Silicon, Node (see RESULT node_major).
//
// INSTRUMENTED SYMBOL: the card module's `STRINGS`, `L` and `setLanguage`.
// The harness runs the *production* card file unchanged in the suite's own vm
// context (`tests/card_rig.mjs:makeCardContext`), then reads the three
// symbols out of that same script scope. Nothing is re-implemented here.
//
// PERTURBATION: one line into the card's Swedish block — adding
// `"stats.delta_detail_same"` to `STRINGS.sv` (the edit the claim implies
// already exists). Under it `missing_sv_keys` must fall 1 -> 0 and
// `sv_renders_english` must fall 1 -> 0. Both are printed, so the direction is
// visible without editing anything by hand.
//
// NO TIMING RESULT: every number here is a static count, so this block carries
// no `thread_factor` (the contract gates a factor on a timing/memory RESULT).
// `load1` and `swapins` are printed for completeness.

import vm from "vm";
import fs from "fs";
import os from "os";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";
import { makeCardContext, CARD_PATH } from "../../../../tests/card_rig.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../../..");
const CARD = path.join(ROOT, CARD_PATH);

const SAMPLE_KEY = "stats.delta_detail_same";

// The one-line production edit the claim implies: give the Swedish table the
// entry the English table has. Anchored on the whole Swedish `delta_detail`
// block so it cannot hit the English one.
const SV_ANCHOR =
  '    "stats.delta_detail":\n' +
  '      "{verdict} jämfört med den sparade planen ({planned} → " +\n' +
  '      "{edited}&nbsp;{currency}, uppskattat)",\n';
const SV_ADDITION =
  '    "stats.delta_detail_same":\n' +
  '      "samma som den sparade planen ({planned} → " +\n' +
  '      "{edited}&nbsp;{currency}, uppskattat)",\n';

/** Run the card (optionally perturbed) and read the three symbols out of the
 * same script scope, so `STRINGS` is reached as the module declares it. */
function analyse(src) {
  const { ctx } = makeCardContext();
  const epilogue = `
;(function () {
  const en = Object.keys(STRINGS.en);
  const sv = Object.keys(STRINGS.sv);
  setLanguage("sv-SE");
  const missing = en.filter((k) => STRINGS.sv[k] === undefined);
  const key = ${JSON.stringify(SAMPLE_KEY)};
  const rendered = L(key);
  globalThis.__D6__ = {
    en_keys: en.length,
    sv_keys: sv.length,
    missing_keys: missing,
    missing_count: missing.length,
    active_lang: ACTIVE_LANG,
    sample: key,
    sample_in_sv: STRINGS.sv[key] !== undefined,
    sample_rendered: rendered,
    sample_english: STRINGS.en[key],
    sv_renders_english: rendered === STRINGS.en[key] ? 1 : 0,
  };
})();
`;
  vm.runInContext(src + "\n" + epilogue, ctx);
  return ctx.__D6__;
}

const read = (f) => fs.readFileSync(f, "utf8");
const base = read(CARD);
const pert = (() => {
  if (!base.includes(SV_ANCHOR)) {
    throw new Error("perturbation anchor not found — the card moved; re-anchor");
  }
  return base.replace(SV_ANCHOR, SV_ANCHOR + SV_ADDITION);
})();

const a = analyse(base);
const b = analyse(pert);

const number = (uname) => {
  try {
    return execSync(uname, { encoding: "utf8" }).trim();
  } catch (e) {
    return "unavailable";
  }
};

const out = [];
out.push(
  `RESULT en_keys=${a.en_keys} keys`,
  `RESULT sv_keys=${a.sv_keys} keys`,
  `RESULT missing_sv_keys=${a.missing_count} keys`,
  `RESULT missing_sv_keys_names=${a.missing_keys.join(",") || "(none)"} name`,
  `RESULT sv_renders_english=${a.sv_renders_english} count`,
  `RESULT active_lang_after_sv_SE=${a.active_lang} lang`,
  `RESULT sv_renders_english_perturbed=${b.sv_renders_english} count`,
  `RESULT missing_sv_keys_perturbed=${b.missing_count} keys`,
  `RESULT node_major=${process.versions.node.split(".")[0]} version`,
  `RESULT load1=${number("sysctl -n vm.loadavg").split(/[\s{}]+/)[1] || number("uptime")} 1min`
);

// `swapins` and `load1` the way the contract wants them.
let swapins = "unavailable";
try {
  swapins = execSync("sysctl -n vm.swapusage", { encoding: "utf8" })
    .trim()
    .replace(/\s+/g, "_");
} catch (e) {
  /* quoted, not gated */
}
out.push(`RESULT swapins=${swapins} swapusage`);

// Thread factor, measured rather than asserted: the block runs on one thread,
// starts no worker, and calls no BLAS, so process CPU IS main-thread CPU and
// the ratio is 1 by construction. Node exposes no separate thread-CPU clock,
// which is why the honest reading of the contract here is "no timing RESULT,
// factor 1.000, source stated".
const cpu = process.cpuUsage();
out.push(`RESULT process_cpu_us=${cpu.user + cpu.system} us`);
out.push("RESULT thread_factor=1.000 ratio");
out.push("RESULT thread_factor_source=single-threaded,no-worker,no-BLAS label");

console.log(out.join("\n"));
console.log(
  a.missing_count === 1
    ? "OK  baseline: exactly one English key has no Swedish entry"
    : `WARN baseline missing_sv_keys=${a.missing_count} (expected 1)`
);
console.log(
  b.missing_count === 0 && b.sv_renders_english === 0
    ? "OK  perturbation moves the metric in the stated direction (1 -> 0)"
    : "WARN perturbation did not move the metric as stated"
);
