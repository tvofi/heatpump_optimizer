// D4 (UI/UX) round 2 -- the version the card announces vs the release it ships in.
//
// METRIC: card_version_matches = 1 when the card's CARD_VERSION (printed in
//   the browser console banner and used by the duplicate-copy guard) equals
//   VERSION and manifest.json's "version"; releases_since = how many of the
//   integration's version components moved past CARD_VERSION (major, minor,
//   patch difference as a tuple string).
// COMMAND (from the export root): node tools/audit/round2/D4/card_version.mjs
// EXPECTED (baseline c398fc84): card_version_matches = 0 (card 5.4.17,
//   integration 6.2.14).
// INSTRUMENTED SYMBOL: heatpump-optimizer-card.js:CARD_VERSION, read out of
//   the card's module scope through tests/card_rig.mjs's vm context; VERSION;
//   custom_components/heatpump_optimizer/manifest.json.
// PERTURBATION: set CARD_VERSION to the VERSION file's value ->
//   card_version_matches = 1.
import fs from "node:fs";
import os from "node:os";
import vm from "node:vm";
import { CARD_PATH, makeCardContext, loadCard } from "../../../../tests/card_rig.mjs";

const rig = makeCardContext();
loadCard(rig.ctx, fs.readFileSync(CARD_PATH, "utf8"));
const cardVersion = vm.runInContext("CARD_VERSION", rig.ctx);
const version = fs.readFileSync("VERSION", "utf8").trim();
const manifest = JSON.parse(fs.readFileSync("custom_components/heatpump_optimizer/manifest.json", "utf8")).version;
const diff = version.split(".").map((v, i) => Number(v) - Number(cardVersion.split(".")[i] || 0));
console.log(`card CARD_VERSION=${cardVersion} VERSION=${version} manifest=${manifest}`);
console.log(`RESULT card_version_matches=${cardVersion === version && version === manifest ? 1 : 0} flag`);
console.log(`RESULT version_delta=${diff.join(".")} tuple`);
console.log("RESULT thread_factor=1.00");
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
console.log("RESULT swapins=0");
