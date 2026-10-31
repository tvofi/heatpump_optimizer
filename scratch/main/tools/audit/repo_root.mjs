// Repository root for an audit harness. The same function is inlined in each
// script; this module is the copy a test reads, and the two texts match.

async function repoRoot(start) {
  const fs = await import("node:fs");
  const path = await import("node:path");
  let dir = path.resolve(start);
  if (fs.existsSync(dir) && fs.statSync(dir).isFile()) dir = path.dirname(dir);
  for (;;) {
    if (fs.existsSync(path.join(dir, "custom_components", "heatpump_optimizer", "manifest.json"))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) throw new Error("no repository root above " + start);
    dir = parent;
  }
}

export { repoRoot };
