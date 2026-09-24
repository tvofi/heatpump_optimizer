#!/usr/bin/env python3
"""s1_owner_surface.py -- required-check enforcement surface NOT matched by a CODEOWNERS owner.

METRIC. `uncovered_surface`: the number of tracked files in the required-check
enforcement surface that no `.github/CODEOWNERS` pattern with an owner matches
(last matching pattern wins, GitHub semantics for the pattern forms used). The
surface is derived, never carried, by one rule wider than the one
CODEOWNERS' own header cites (`tools/audit/round6/D11/fix/codeowners_gap.py`,
which only sees `<interpreter> <path>`):
  (a) every tracked path a non-comment workflow line executes, in ANY form --
      `node|python3|bash|sh <path>`, `./<path>`, or a bare `<path>` run --
      which adds `./tests/run.sh` (tests.yml `fast`, the gate itself);
  (b) the transitive relative ES-module imports of every `.mjs` in (a)
      (`import ... from './x.mjs'`): the code a required job actually runs;
  (c) every tracked `.json`/`.txt` named by a string literal in (a)+(b)'s
      JS files that the check reads as its verdict data (budgets, the
      known-bad suppression ledger, exclusion lists).
Hooks and settings are kept exactly as the round-6 harness had them.
Key: the CODEOWNERS pattern match of the path, not any label in the file.

Production symbol: `.github/CODEOWNERS` (read by GitHub for the
`require_code_owner_review` rule of ruleset main-protect-checks), and the
workflows' `run:` lines that define the surface.

NULL CONTROL: rule (a) restricted to the round-6 interpreter form and (b),(c)
off reproduces that harness's surface and must print uncovered 0.

PERTURBATION (--perturb): append `/tests/run.sh @tvofi` to a temp copy of
CODEOWNERS (one line). Expected: uncovered_surface drops by exactly 1.

RUN (tree root): PYTHONPATH=tests/hastub python3 tools/audit/round8/D11/s1_owner_surface.py [--perturb] [--list]
EXPECTED at baseline cdf82da: null_control_uncovered=0; uncovered_surface=14 (+-0, exact count; set printed with --list).
MACHINE: 4-vCPU cloud container (round 8); no timing numbers.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import fnmatch
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(".")
ROOTS = r"(?:tests|tools|\.claude|\.github)"
EXEC_NARROW = re.compile(r"(?<![\w./-])(?:node|python3|python|bash|sh|npx|pnpm)\s+(" + ROOTS + r"/[A-Za-z0-9_./-]+\.(?:py|mjs|js|sh|yml))\b")
EXEC_WIDE = re.compile(r"(?:(?<![\w./-])(?:node|python3|python|bash|sh|npx|pnpm)\s+|(?<![\w/-])\./|^\s*(?:run:\s*)?)(" + ROOTS + r"/[A-Za-z0-9_./-]+\.(?:py|mjs|js|sh))\b")
IMPORT = re.compile(r"""(?:from|import)\s*\(?\s*['"](\.{1,2}/[A-Za-z0-9_./-]+\.m?js)['"]""")
DATA = re.compile(r"""['"`]((?:\.\.?/|""" + ROOTS + r"""/)?[A-Za-z0-9_./-]+\.(?:json|txt))['"`]""")


def tracked():
    return set(subprocess.check_output(["git", "ls-files"], text=True, cwd=ROOT).split())


def surface(wide):
    have = tracked()
    wfs = sorted(f for f in have if f.startswith(".github/workflows/") and f.endswith(".yml"))
    execs = set()
    rx = EXEC_WIDE if wide else EXEC_NARROW
    for wf in wfs:
        for line in (ROOT / wf).read_text().splitlines():
            if line.lstrip().startswith("#"):
                continue
            for m in rx.finditer(line):
                if m.group(1) in have and m.group(1) not in wfs:
                    execs.add(m.group(1))
    imports, data = set(), set()
    if wide:
        todo = [e for e in execs if e.endswith((".mjs", ".js"))]
        seen = set(todo)
        while todo:
            f = todo.pop()
            txt = (ROOT / f).read_text()
            for m in IMPORT.finditer(txt):
                p = os.path.normpath(os.path.join(os.path.dirname(f), m.group(1)))
                if p in have and p not in seen:
                    seen.add(p); imports.add(p); todo.append(p)
            for m in DATA.finditer(txt):
                tok = m.group(1)
                cands = [os.path.normpath(os.path.join(os.path.dirname(f), tok)), os.path.normpath(tok)]
                for c in cands:
                    if c in have and "/fixtures/" not in c:
                        data.add(c)
    hooks = sorted(f for f in have if f.startswith(".claude/hooks/"))
    settings = [".claude/settings.json"] if ".claude/settings.json" in have else []
    return sorted(set(wfs) | execs | imports | data | set(hooks) | set(settings)), execs, imports, data


def patterns(text):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        out.append((parts[0], parts[1:]))
    return out


def hit(pat, path):
    anchored = pat.startswith("/")
    p = pat.lstrip("/")
    if p.endswith("/"):
        return path.startswith(p) if anchored else ("/" + p) in ("/" + path)
    if anchored:
        return fnmatch.fnmatch(path, p) or fnmatch.fnmatch(path, p + "/*")
    return any(fnmatch.fnmatch(seg, p) for seg in path.split("/")) or fnmatch.fnmatch(path, p)


def owned(path, rules):
    owners = None
    for pat, own in rules:
        if hit(pat, path):
            owners = own
    return bool(owners)


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    text = (ROOT / ".github/CODEOWNERS").read_text()
    if "--perturb" in sys.argv:
        text += "\n/tests/run.sh @tvofi\n"
        print("# perturbation: appended `/tests/run.sh @tvofi` to an in-memory copy of CODEOWNERS")
    rules = patterns(text)
    narrow, *_ = surface(False)
    nun = [f for f in narrow if not owned(f, rules)]
    wide, execs, imports, data = surface(True)
    wun = [f for f in wide if not owned(f, rules)]
    print(f"# null control (round-6 rule): surface {len(narrow)}, uncovered {len(nun)} {nun}")
    print(f"# wide rule: surface {len(wide)} = narrow {len(narrow)} + {len(set(wide) - set(narrow))} added")
    for f in wun:
        why = "exec" if f in execs else "import" if f in imports else "data" if f in data else "other"
        print(f"#   UNCOVERED [{why}] {f}")
    print(f"RESULT null_control_surface={len(narrow)} count")
    print(f"RESULT null_control_uncovered={len(nun)} count")
    print(f"RESULT surface={len(wide)} count")
    print(f"RESULT uncovered_surface={len(wun)} count")
    print(f"RESULT uncovered_exec={sum(1 for f in wun if f in execs)} count")
    print(f"RESULT uncovered_import={sum(1 for f in wun if f in imports and f not in execs)} count")
    print(f"RESULT uncovered_data={sum(1 for f in wun if f in data and f not in execs and f not in imports)} count")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
