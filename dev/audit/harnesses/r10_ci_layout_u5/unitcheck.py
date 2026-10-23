#!/usr/bin/env python3
"""R10-CI-LAYOUT P2b, unit U5: tests.yml's static null control and its interface.

    python3 dev/audit/harnesses/r10_ci_layout_u5/unitcheck.py [BASE]   (BASE default: origin/main)

1. STATIC: the design's instrument (measure/rev/unitcheck2.py, read from the
   archived ref, never copied) over BASE's tests.yml against this tree's,
   under tests_map.json. Want rc 0.
2. STAND-DOWN (DESIGN-P2 4.2, no required job ever skips): no job whose
   `tests / <job>` name tools/ci/gate.py requires carries a job-level `if:`
   that reads a closure-scope skip decision. The static half is blind here:
   the job row is a mapped change, so it prints and passes.
3. INTERFACE (U0c's): ci.yml's `tests` caller passes exactly the inputs
   tests.yml declares, and only secrets it declares; GitHub refuses a run
   whose caller passes an undeclared input.
Then three plants, each of which one half must refuse, and the instrument's
blind line on the third, measured.
Prints one line per check; exit 0 only when the head passes 1-3 and every
plant reads as stated.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

TAG = "archive/probe/design-ci-rev4"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TESTS = ROOT / ".github" / "workflows" / "tests.yml"
CI = ROOT / ".github" / "workflows" / "ci.yml"
sys.path.insert(0, str(ROOT / "tools" / "ci"))
import gate  # noqa: E402


def git_show(spec: str) -> str:
    return subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def static(d: Path, before: Path, after: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-I", str(d / "unitcheck2.py"), "static", str(before), str(after),
                        "--map", str(HERE / "tests_map.json")], capture_output=True, text=True)
    lines = (p.stdout + p.stderr).strip().splitlines()
    return p.returncode, lines[-1] if lines else "(no output)"


def required_tests_jobs() -> set[str]:
    """tests.yml job ids behind every `tests / <name>` gate.py can require (matrix names cut)."""
    names = {n.split(" / ", 1)[1] for ns in gate.REQUIRED.values() for n in ns if n.startswith("tests / ")}
    return {n.split(" (", 1)[0] for n in names}


def stand_down_problems(doc: dict) -> list[str]:
    jobs = doc.get("jobs") or {}
    out = []
    for jid in sorted(required_tests_jobs()):
        if jid not in jobs:
            out.append(f"{jid}: required by gate.py, absent from tests.yml")
            continue
        cond = str(jobs[jid].get("if") or "")
        if jid != "coverage" and "closure-scope.outputs." in cond:
            out.append(f"{jid}: a job-level `if:` reads a skip decision ({' '.join(cond.split())[:90]}...)")
    return out


def interface_problems(tests_doc: dict, ci_doc: dict) -> list[str]:
    call = (tests_doc.get("on", tests_doc.get(True)) or {}).get("workflow_call") or {}
    declared = set(call.get("inputs") or {})
    declared_secrets = set(call.get("secrets") or {})
    caller = (ci_doc.get("jobs") or {}).get("tests") or {}
    passed, secrets = set(caller.get("with") or {}), set(caller.get("secrets") or {})
    out = []
    if passed != declared:
        out.append(f"caller passes {sorted(passed)}, tests.yml declares {sorted(declared)}")
    if not secrets <= declared_secrets:
        out.append(f"caller passes undeclared secrets {sorted(secrets - declared_secrets)}")
    if any((call["inputs"][k] or {}).get("type") != "string" or (call["inputs"][k] or {}).get("default") != ""
           for k in declared):
        out.append("an input is not `type: string, default: \"\"`")
    return out


def main(argv: list[str]) -> int:
    base = argv[0] if argv else "origin/main"
    fails = 0

    def say(label: str, ok: bool, detail: str) -> None:
        nonlocal fails
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {label}: {detail}")

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "unitcheck2.py").write_text(git_show(f"{TAG}:measure/rev/unitcheck2.py"))
        before = d / "before.yml"
        before.write_text(git_show(f"{base}:.github/workflows/tests.yml"))
        head_text = TESTS.read_text()
        head = yaml.safe_load(head_text)
        ci = yaml.safe_load(CI.read_text())

        rc, line = static(d, before, TESTS)
        say("static, the head (want rc 0)", rc == 0, line)
        probs = stand_down_problems(head)
        say("stand-down, the head (want none)", not probs, "; ".join(probs) or "none")
        probs = stand_down_problems(yaml.safe_load(before.read_text()))
        say("stand-down, BASE's tests.yml (want browser and typing refused)",
            [p.split(":")[0] for p in probs] == ["browser", "typing"], "; ".join(p[:60] for p in probs) or "none")
        probs = interface_problems(head, ci)
        say("interface, the head (want none)", not probs, "; ".join(probs) or "none")

        # Plant 1: an unmapped job. The static half refuses it.
        p1 = d / "p1.yml"
        p1.write_text(head_text.replace("\n  fast:\n", "\n  extra:\n    runs-on: ubuntu-latest\n"
                                        "    steps:\n      - run: \"true\"\n\n  fast:\n", 1))
        rc, line = static(d, before, p1)
        say("plant 1, an unmapped job added (want rc 1)", rc == 1, line)

        # Plant 2: browser's gained first step moved past the checkout. MISPLACED.
        doc = copy.deepcopy(head)
        st = doc["jobs"]["browser"]["steps"]
        st.insert(1, st.pop(0))
        p2 = d / "p2.yml"
        p2.write_text(yaml.safe_dump(doc, sort_keys=False))
        rc, line = static(d, before, p2)
        say("plant 2, browser's decision step moved after its checkout (want rc 1)", rc == 1, line)

        # Plant 3: browser's job-level skip restored. Static is blind (a mapped
        # change); the stand-down check refuses it.
        doc = copy.deepcopy(head)
        doc["jobs"]["browser"]["if"] = (doc["jobs"]["browser"]["if"].rstrip()
                                        + " && needs.closure-scope.outputs.browser_skip != 'skip'")
        p3 = d / "p3.yml"
        p3.write_text(yaml.safe_dump(doc, sort_keys=False))
        rc, line = static(d, before, p3)
        say("plant 3, browser's job-level skip restored: static (blind, reads rc 0)", rc == 0, line)
        probs = stand_down_problems(doc)
        say("plant 3: stand-down (want browser refused)", [p.split(":")[0] for p in probs] == ["browser"],
            "; ".join(probs) or "none")

        # Plant 4: the caller passes an input tests.yml does not declare.
        ci4 = copy.deepcopy(ci)
        ci4["jobs"]["tests"]["with"]["legs"] = "{}"
        probs = interface_problems(head, ci4)
        say("plant 4, an undeclared input passed (want refused)", bool(probs), "; ".join(probs) or "none")

    print(f"RESULT {'PASS' if not fails else 'FAIL'} ({fails} failed)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
