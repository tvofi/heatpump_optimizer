#!/usr/bin/env python3
"""R10-RCA-HOTFIX-BATCH-ERREXIT: a workflow step reads `$?` after a bare call that errexit ends first.

    python3 -I dev/audit/harnesses/r10_errexit_capture.py [--root DIR]
    python3 -I dev/audit/harnesses/r10_errexit_capture.py --selftest

Every `run:` block in .github/workflows/*.yml and .github/actions/*/action.yml
runs under errexit: GitHub's default Linux shell is `bash -e {0}`, `shell:
bash` is `bash --noprofile --norc -eo pipefail {0}`, `shell: sh` is `sh -e
{0}`; a `set -uo pipefail` line does not clear `-e`. In such a block a `$?`
read (`rc=$?`, `case $?`, `[ $? ...`) whose producer is a bare simple command
is dead code for every nonzero exit: errexit ends the STEP with that exit
before the read. A producer that is a condition (`if cmd`, `cmd || rc=$?`,
`... else rc=$?`), or a read under `set +e`, is exempt.

It prints one HIT line per such read and, last, RESULT lines; it refuses
(exit 2) when it scanned no run block or no `$?` read, so it cannot go green by
reading nothing. Exit 1 on any hit.

Recorded at main d181d014a (frozen evidence, not a live header): the one hit
is nightly.yml's `--batch-due` gate; with the hotfix line it prints hits=0.
EXPECTED RESULT blocks=260
EXPECTED RESULT reads=5
EXPECTED RESULT hits=1
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

import yaml

ERREXIT_SHELLS = {None, "bash", "sh"}
READ = re.compile(r"\$\?")
SAFE_PRODUCER = re.compile(
    r"^(if|elif|while|until)\b|^!|\|\||&&|"
    r"(^|\s)(then|do|else|\{|\()$|^(fi|done|esac|\}|\))\b|^(else|then|do)\b")


def run_blocks(root: Path):
    """(file, job, step name, shell, run text) for every run block."""
    files = sorted((root / ".github" / "workflows").glob("*.yml")) + sorted(
        (root / ".github" / "actions").glob("*/action.yml"))
    for f in files:
        doc = yaml.safe_load(f.read_text()) or {}
        wdef = ((doc.get("defaults") or {}).get("run") or {}).get("shell")
        jobs = doc.get("jobs") or {}
        if "runs" in doc:  # composite action
            jobs = {"(composite)": {"steps": (doc["runs"] or {}).get("steps") or []}}
        for jname, job in jobs.items():
            jdef = (((job or {}).get("defaults") or {}).get("run") or {}).get("shell", wdef)
            for i, step in enumerate((job or {}).get("steps") or []):
                if "run" in step:
                    yield (f.relative_to(root).as_posix(), jname,
                           step.get("name") or f"step {i}", step.get("shell", jdef), step["run"])


def logical_lines(text: str) -> list[str]:
    """Comment lines dropped, backslash continuations joined."""
    out, cur = [], ""
    for raw in text.split("\n"):
        s = raw.strip()
        if not cur and (not s or s.startswith("#")):
            continue
        if s.endswith("\\"):
            cur += s[:-1] + " "
            continue
        out.append((cur + s).strip())
        cur = ""
    if cur:
        out.append(cur.strip())
    return out


def hazards(text: str) -> tuple[int, list[tuple[str, str]]]:
    """(reads examined, [(producer, read line)]) for one errexit run block."""
    reads, hits, errexit, prev = 0, [], True, ""
    for line in logical_lines(text):
        if re.match(r"^set\s+\+e\b", line) or re.match(r"^set\s+\+o\s+errexit\b", line):
            errexit = False
        elif re.match(r"^set\s+-[a-z]*e", line) or re.match(r"^set\s+-o\s+errexit\b", line):
            errexit = True
        for m in READ.finditer(line):
            reads += 1
            head = line[:m.start()]
            if not errexit:
                continue
            # The producer: the statement before the read on this line, else the previous line.
            cut = head.rfind(";")
            producer = head[:cut].strip() if cut >= 0 else prev
            stmt = head[cut + 1:].strip()
            if SAFE_PRODUCER.search(stmt) or (stmt and not re.match(
                    r"^(\w+=|case\b|\[|\[\[|test\b|echo\b|printf\b|exit\b|return\b|local\b)", stmt)):
                continue  # the read sits inside a condition or a command's own arguments
            if not producer or SAFE_PRODUCER.search(producer.split(";")[-1].strip()):
                continue
            hits.append((producer.split(";")[-1].strip(), line))
        prev = line
    return reads, hits


def scan(root: Path) -> tuple[int, int, list[str]]:
    blocks = reads = 0
    out = []
    for f, job, name, shell, run in run_blocks(root):
        if shell not in ERREXIT_SHELLS:
            continue
        blocks += 1
        n, hs = hazards(run)
        reads += n
        for producer, line in hs:
            out.append(f"HIT {f} job={job} step={name!r}: `{producer[:90]}` then `{line[:60]}`")
    return blocks, reads, out


def selftest() -> int:
    cases = {
        # (run text, hits expected)
        "bare then capture": ("set -uo pipefail\ncmd --batch-due\nbatch=$?\n", 1),
        "same line": ("guard --require-green; rc=$?\ncase $rc in 0) ;; esac\n", 1),
        "case on $?": ("cmd\ncase $? in 4) exit 0 ;; esac\n", 1),
        "or-capture": ("batch=0\ncmd --batch-due || batch=$?\n", 0),
        "if/else": ("if guard --require-green; then rc=0; else rc=$?; fi\n", 0),
        "else line": ("if cmd; then\n  :\nelse\n  pitch=$?\nfi\n", 0),
        "set +e": ("set +e\ncmd\nrc=$?\nset -e\n", 0),
        "comment between": ("cmd \\\n  --flag\n# why\nrc=$?\n", 1),
    }
    bad = [k for k, (t, want) in cases.items() if len(hazards(t)[1]) != want]
    # The shell arm: a `shell: python` block is not errexit bash; a `shell: bash` one is.
    with tempfile.TemporaryDirectory() as td:
        wf = Path(td) / ".github" / "workflows"
        wf.mkdir(parents=True)
        wf.joinpath("a.yml").write_text(yaml.safe_dump({"jobs": {"j": {"steps": [
            {"name": "py", "shell": "python", "run": "x\nrc=$?\n"},
            {"name": "bash", "shell": "bash", "run": "x\nrc=$?\n"},
            {"name": "default", "run": "x\nrc=$?\n"}]}}}))
        blocks, _, hits = scan(Path(td))
        if (blocks, len(hits)) != (2, 2):
            bad.append(f"shell arm blocks={blocks} hits={len(hits)}")
    print(f"selftest: {len(cases) + 1} checks, {len(bad)} failed{' ' + str(bad) if bad else ''}")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[3]))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    blocks, reads, hits = scan(Path(a.root))
    for h in hits:
        print(h)
    print(f"RESULT blocks={blocks}")
    print(f"RESULT reads={reads}")
    print(f"RESULT hits={len(hits)}")
    if not blocks or not reads:
        print("REFUSED: no errexit run block or no $? read scanned", file=sys.stderr)
        return 2
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
