// D4 round 5 -- the card's own translation dictionaries: every en key a
// user reading the card in Swedish would see fall back to English.
//
// METRIC (one line): the number of leaf keys present in the card's `en`
// STRINGS dictionary and absent from its `sv` dictionary -- each one is a
// label a Swedish session renders in English, because `L()` falls back
// `dict[key]` -> `STRINGS.en[key]` -> the key itself.
//
// COMMAND (from the repository root):
//   node tools/audit/round5/D4/strings_parity.mjs
// No browser, no payload, no timing: the number is a set difference over a
// literal in the production source.
//
// EXPECTED: baseline 1 (stats.delta_detail_same); after the perturbation 0.
// Tolerance: exact.
//
// BASELINE SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main, round 5).
// MACHINE: 8-core Apple M1, 8 GB, macOS (Darwin 25.6.0).
//
// The instrumented symbol is heatpump-optimizer-card.js's `STRINGS` object
// literal -- read out of the production file and evaluated, not retyped.
// The perturbation adds the missing key to the `sv` block, in the block's
// own style: exactly the one-line production edit a fix would make.
import { readFileSync } from "node:fs";
import { execSync } from "node:child_process";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(__dirname, "../../../..");
const CARD_SRC = path.join(repo, "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js");

const SV_ANCHOR = '"stats.the_same": "oförändrad",';
const baselineSrc = readFileSync(CARD_SRC, "utf8");
if (baselineSrc.split(SV_ANCHOR).length - 1 !== 1) {
  throw new Error("anchor for the sv dictionary edit is not unique");
}
const perturbedSrc = baselineSrc.replace(
  SV_ANCHOR,
  '"stats.the_same": "oförändrad",\n' +
  '    "stats.delta_detail_same":\n' +
  '      "{verdict} jämfört med den sparade planen ({planned} → " +\n' +
  '      "{edited}&nbsp;{currency}, uppskattat)",'
);

/** Pull the `const STRINGS = {...}` literal out of the source and evaluate it. */
function readStrings(src) {
  const at = src.indexOf("const STRINGS = ");
  if (at < 0) throw new Error("no STRINGS literal");
  const first = src.indexOf("{", at);
  let d = 0, end = -1;
  for (let i = first; i < src.length; i++) {
    const c = src[i];
    if (c === "{") d++;
    else if (c === "}") { d--; if (d === 0) { end = i; break; } }
  }
  // eslint-disable-next-line no-eval
  return eval(`(${src.slice(first, end + 1)})`);
}

function flat(o, p = "") {
  const out = {};
  for (const [k, v] of Object.entries(o)) {
    const key = p ? `${p}.${k}` : k;
    if (v && typeof v === "object") Object.assign(out, flat(v, key));
    else out[key] = v;
  }
  return out;
}

function analyse(src) {
  const S = readStrings(src);
  const langs = Object.keys(S);
  const F = {};
  for (const l of langs) F[l] = flat(S[l]);
  const base = langs[0];
  const report = { langs, counts: {}, missing: {}, identical: {} };
  for (const l of langs) report.counts[l] = Object.keys(F[l]).length;
  for (const l of langs.slice(1)) {
    report.missing[l] = Object.keys(F[base]).filter((k) => !(k in F[l]));
    report.identical[l] = Object.keys(F[base]).filter((k) => (k in F[l]) && F[l][k] === F[base][k]);
  }
  return { F, base, ...report };
}

const base = analyse(baselineSrc);
const pert = analyse(perturbedSrc);

console.log(`languages: ${base.langs.join(", ")}`);
console.log(`keys: ${base.langs.map((l) => `${l}=${base.counts[l]}`).join("  ")}`);
for (const l of base.langs.slice(1)) {
  console.log(`\n${l} vs ${base.base}: missing=${base.missing[l].length} identical-string=${base.identical[l].length}`);
  for (const k of base.missing[l]) {
    console.log(`  MISSING   ${k} = ${JSON.stringify(base.F[base.base][k]).slice(0, 88)}`);
  }
  for (const k of base.identical[l]) {
    console.log(`  identical ${k} = ${JSON.stringify(base.F[base.base][k]).slice(0, 60)}`);
  }
}

const missingBase = base.langs.slice(1).reduce((a, l) => a + base.missing[l].length, 0);
const missingPert = pert.langs.slice(1).reduce((a, l) => a + pert.missing[l].length, 0);
const svKeys = base.counts.sv, svKeysPert = pert.counts.sv;
console.log("");
console.log(`RESULT card_lang_keys_en=${base.counts.en} count`);
console.log(`RESULT card_lang_keys_sv=${svKeys} count`);
console.log(`RESULT card_lang_missing_sv_baseline=${missingBase} count`);
console.log(`RESULT card_lang_missing_sv_perturbed=${missingPert} count`);
console.log(`RESULT card_lang_keys_sv_perturbed=${svKeysPert} count`);

let load1 = 0;
try { load1 = +os.loadavg()[0].toFixed(2); } catch { /* no loadavg here */ }
let swapins = -1;
try {
  const m = execSync("vm_stat", { encoding: "utf8" }).match(/Swapins:\s+(\d+)/);
  if (m) swapins = Number.parseInt(m[1], 10);
} catch { swapins = -1; }
console.log("RESULT thread_factor=1.000 ratio   # string set difference; no BLAS in this process");
console.log(`RESULT load1=${load1} load`);
console.log(`RESULT swapins=${swapins} count`);

const ok = base.counts.en === 261 && svKeys === 260 && missingBase === 1 && missingPert === 0;
console.log(ok ? "SELF-CHECK ok" : "SELF-CHECK FAIL");
if (!ok) process.exitCode = 1;
