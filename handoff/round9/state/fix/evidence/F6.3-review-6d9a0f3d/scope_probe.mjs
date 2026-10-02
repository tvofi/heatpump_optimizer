// Reviewer's own probe (not the finder's): extract gridScope from tests/card_browser.mjs and call it.
import { readFileSync } from "node:fs"; import { execFileSync } from "node:child_process";
const repo = process.argv[2];
const src = readFileSync(`${repo}/tests/card_browser.mjs`, "utf8");
const a = src.indexOf("const GRID_SURFACE"), b = src.indexOf("// ---- the host side");
const f = new Function("execFileSync", "repo", src.slice(a, b) + "\nreturn gridScope;")(execFileSync, repo);
console.log(f({ HPO_BROWSER_SCOPE: "auto", HPO_BROWSER_BASE: process.argv[3] }).line);
