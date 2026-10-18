import { execFileSync } from "node:child_process";
const repo = process.argv[2];
const { threeDotFiles, claimsAreThisBranchs } = await import(repo + "/tests/card_rig.mjs");
const runGit = (...a) => execFileSync("git", a, { cwd: repo, encoding: "utf8" });
console.log("card_rig.threeDotFiles:", JSON.stringify(threeDotFiles(runGit, "HEAD~1")));
const src = execFileSync("sed", ["-n", "/^const GRID_SURFACE/,/^}$/p", repo + "/tests/card_browser.mjs"], { encoding: "utf8" });
const f = new Function("execFileSync", "repo", "process", src.replace(/^const /gm, "var ") + "\nreturn gridScope;")(execFileSync, repo, process);
console.log(f({ HPO_BROWSER_SCOPE: "auto", HPO_BROWSER_BASE: "HEAD~1", GITHUB_EVENT_NAME: "pull_request" }).line);
