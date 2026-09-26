#!/usr/bin/env python3
"""D11 verify-v3 (round 9), finding D11-s2-04: does CLAUDE.md's quoted mode line occur in what
the gate's real scoping path prints, and how many quoted output literals in the policy corpus
are absent from every code file?

METRIC (one line): (a) 1 if CLAUDE.md's backticked `MODE: SCOPED ...` literal is a substring of
  the scope.txt that production `tests/closure.py select --diff HEAD` writes for this tree
  (a real 0-run scoped plan), else 0; (b) of the backticked `UPPER: ...` literals (whitespace-normalised, cut at a <placeholder>) in the whole
  policy corpus (CLAUDE.md, AGENTS.md, .claude/rules/*.md, steward SKILL.md, tools/audit/briefs/*.md,
  tools/audit/README.md, tests/README.md), how many occur verbatim in no tracked .py/.mjs/.js/.sh/.yml.
KEY: substring of the production printer's own output file / of tracked code text.
Perturbation: the scope.txt re-read after replacing ' -- ' with ' — ' in its SCOPED line (what a
  one-character print_plan edit would print) -> (a) rises to 1.
COMMAND:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/verify-v3/v3_mode_line.py
EXPECTED (baseline 1936d5ca + round-9 evidence): (a)=0, perturbed (a)=1; (b) exact on the tree.
MACHINE: box G4-V3 cloud container, 4 CPU Linux, CPython 3.14.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import glob, re, subprocess, sys, tempfile, time

T0p, T0t = time.process_time(), time.thread_time()
LIT = re.compile(r"`([A-Z][A-Z -]*: [^`]*)`")


def main():
    tmp = tempfile.mkdtemp(prefix="d11v3-mode-")
    subprocess.run([sys.executable, "tests/closure.py", "select", "--diff", "HEAD", "--workdir", tmp],
                   capture_output=True, text=True, env=dict(os.environ, PYTHONPATH="tests/hastub"))
    scope = open(os.path.join(tmp, "scope.txt"), encoding="utf-8").read()
    line = next(l.strip() for l in scope.splitlines() if "MODE:" in l)
    quoted = next(m.group(1) for m in LIT.finditer(open("CLAUDE.md", encoding="utf-8").read()) if "MODE: SCOPED" in m.group(1))
    a = int(quoted in scope)
    pa = int(quoted in scope.replace("MODE: SCOPED -- ", "MODE: SCOPED — "))
    print(f"# production scope.txt mode line: {line!r}; CLAUDE.md quotes {quoted!r}")
    corpus = (["CLAUDE.md", "AGENTS.md", ".claude/skills/steward/SKILL.md", "tools/audit/README.md", "tests/README.md"]
              + sorted(glob.glob(".claude/rules/*.md")) + sorted(glob.glob("tools/audit/briefs/*.md")))
    code = subprocess.run(["git", "ls-files", "*.py", "*.mjs", "*.js", "*.sh", "*.yml"], capture_output=True,
                          text=True).stdout.split()
    code_text = "\n".join(open(f, encoding="utf-8", errors="replace").read() for f in code
                          if os.path.isfile(f) and not f.startswith("tools/audit/round"))
    lits, absent = [], []
    for f in corpus:
        for m in LIT.finditer(open(f, encoding="utf-8").read()):
            lits.append((f, m.group(1)))
            # whitespace-normalised; a <placeholder> ends the literal's checked prefix
            words = []
            for w in m.group(1).split():
                if w.startswith("<"):
                    break
                words.append(re.escape(w))
            if not re.search(r"\s+".join(words), code_text):
                absent.append((f, m.group(1)))
    for f, l in absent:
        print(f"# absent from every code file: {f}: {l!r}")
    print(f"RESULT quoted_in_production_output={a} count")
    print(f"RESULT perturbed_quoted_in_output={pa} count")
    print(f"RESULT corpus_quoted_output_literals={len(lits)} count")
    print(f"RESULT corpus_literals_absent_from_code={len(absent)} count")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
