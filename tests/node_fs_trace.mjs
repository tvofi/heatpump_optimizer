// Preload for tests/closure.py _record_node when strace is missing.
// --import this file: wrap fs + register an ESM resolve hook, write
// CLOSURE_NODE_TRACE (JSON list of repo-relative paths) on exit.
import fs from "node:fs";
import child_process from "node:child_process";
import path from "node:path";
import { register } from "node:module";
import { fileURLToPath } from "node:url";

const root = process.env.CLOSURE_ROOT || "";
const sink = process.env.CLOSURE_NODE_TRACE || "";
const opened = new Set();

function note(p) {
  if (!root || p == null) return;
  let raw = null;
  if (typeof p === "string") raw = p;
  else if (typeof p === "object" && typeof p.href === "string") {
    try { raw = fileURLToPath(p); } catch { return; }
  } else if (Buffer.isBuffer(p)) raw = p.toString();
  if (!raw) return;
  let abs;
  try {
    abs = path.isAbsolute(raw) ? path.normalize(raw) : path.resolve(raw);
  } catch {
    return;
  }
  const prefix = root.endsWith(path.sep) ? root : root + path.sep;
  if (abs === root || abs.startsWith(prefix)) {
    opened.add(abs.slice(prefix.length).split(path.sep).join("/"));
  }
}

function wrap(obj, name) {
  const orig = obj[name];
  if (typeof orig !== "function") return;
  obj[name] = function (...args) {
    const a = args[0];
    if (typeof a === "string" || Buffer.isBuffer(a) || (a && a.href)) note(a);
    return orig.apply(this, args);
  };
}

for (const n of [
  "readFileSync", "readFile", "openSync", "open", "createReadStream",
  "existsSync", "statSync", "lstatSync", "accessSync", "access",
  "realpathSync", "realpath",
]) wrap(fs, n);
if (fs.promises) {
  for (const n of ["readFile", "open", "stat", "lstat", "access", "realpath"]) {
    wrap(fs.promises, n);
  }
}

function noteArgv(args) {
  for (const a of args) {
    if (typeof a === "string") note(a);
    else if (Array.isArray(a)) {
      for (const x of a) if (typeof x === "string") note(x);
    }
  }
}
for (const n of [
  "execFile", "execFileSync", "spawn", "spawnSync", "exec", "execSync", "fork",
]) {
  const orig = child_process[n];
  if (typeof orig !== "function") continue;
  child_process[n] = function (...args) {
    noteArgv(args);
    return orig.apply(this, args);
  };
}

const hook = `data:text/javascript,${encodeURIComponent(`
import { fileURLToPath } from "node:url";
import fs from "node:fs";
import path from "node:path";
let root = "";
let sink = "";
export function initialize(data) {
  root = data.root || "";
  sink = data.sink || "";
}
export async function resolve(specifier, context, nextResolve) {
  const r = await nextResolve(specifier, context);
  if (r.url && r.url.startsWith("file:") && root && sink) {
    try {
      const abs = fileURLToPath(r.url);
      const prefix = root.endsWith(path.sep) ? root : root + path.sep;
      if (abs === root || abs.startsWith(prefix)) {
        const rel = abs.slice(prefix.length).split(path.sep).join("/");
        fs.appendFileSync(sink + ".mod", rel + "\\n");
      }
    } catch {}
  }
  return r;
}
`)}`;
register(hook, import.meta.url, { data: { root, sink } });

function flush() {
  if (!sink) return;
  try {
    if (fs.existsSync(sink + ".mod")) {
      for (const line of fs.readFileSync(sink + ".mod", "utf8").split("\n")) {
        if (line) opened.add(line);
      }
      fs.rmSync(sink + ".mod", { force: true });
    }
    fs.writeFileSync(sink, JSON.stringify([...opened].sort()));
  } catch {}
}
process.on("exit", flush);
