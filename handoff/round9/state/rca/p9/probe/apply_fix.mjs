import fs from "node:fs";
const f = process.argv[2]; const skip = (process.argv[3] || "").split(",");
const { FIXES } = await import("./fixed.mjs");
let s = fs.readFileSync(f, "utf8");
for (const k of Object.keys(FIXES)) if (!skip.includes(k)) s = FIXES[k](s);
fs.writeFileSync(f, s); console.log("applied", Object.keys(FIXES).filter((k) => !skip.includes(k)).join(","));
