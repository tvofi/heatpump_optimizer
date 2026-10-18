// The card.mjs:10792-10812 pin's predicate, copied verbatim, driven against this checkout's
// tests/env_drift.py and tests/card_rig.mjs (run from the repo root).
import fs from "node:fs";
import { pathToFileURL } from "node:url";
const { threeDotFiles } = await import(pathToFileURL(process.cwd() + "/tests/card_rig.mjs").href + "?" + Date.now());
const asked = [];
const stub = (...a) => { asked.push(a.join(" ")); if (a[0] === "diff" && a[a.length - 1] === "REF...HEAD") return "dev/changed.md\n"; if (a[0] === "diff" && a[a.length - 1] === "HEAD") return " \ndev/changed.md\n"; return "notes.txt\n"; };
threeDotFiles(stub, "REF");
const pySrc = fs.readFileSync("tests/env_drift.py", "utf8");
const pyFn = pySrc.slice(pySrc.indexOf("def three_dot_files("));
const pyBody = pyFn.slice(0, pyFn.indexOf("\n    ):"));
const sibling = [...pyBody.matchAll(/^\s*\[("git",[^\]]*)\],\s*$/gm)].map((m) => JSON.parse(`[${m[1].replace(/f"\{ref\}/g, '"REF')}]`).slice(1).join(" "));
const ok = sibling.length === 3 && asked.length === 3 && asked.every((c, i) => c === sibling[i]) && sibling.slice(0, 2).every((c) => c.includes("--no-renames"));
console.log(ok ? "PIN PASS" : "PIN FAIL", "|", asked.join(" | "), "vs env_drift:", sibling.join(" | "));
