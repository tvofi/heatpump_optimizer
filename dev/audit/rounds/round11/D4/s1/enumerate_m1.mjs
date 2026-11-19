// D4.M1 enumerator (round 11, seat D4-s1): the step's universe, one item per line,
// "<card_drift state>\t<language>" -- every state `node tests/card_drift.mjs --list`
// prints times every value on the `language` row of check_scopes.py --population.
// Each item is driven at 3 viewports x {light,dark} x {reduce,no-preference} x
// {fine,coarse} = 24 cells by m1_browser.mjs.
//
//   node dev/audit/rounds/round11/D4/s1/enumerate_m1.mjs
//
// The population needs a git repository holding the baseline: REPO (default ".")
// and the baseline ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
import { execFileSync } from "node:child_process";
const BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692";
const states = execFileSync("node", ["tests/card_drift.mjs", "--list"], { encoding: "utf8" }).split("\n").filter(Boolean);
const pop = execFileSync("python3", ["tools/audit/check_scopes.py", "--repo", process.env.REPO || ".", "--ref", BASE, "--population"],
  { encoding: "utf8" });
const row = pop.split("\n").find((l) => l.startsWith("language\t"));
if (!row) { console.error("no language row in the population"); process.exit(1); }
const langs = row.split("\t")[2].split(",");
for (const s of states) for (const l of langs) console.log(`${s}\t${l}`);
