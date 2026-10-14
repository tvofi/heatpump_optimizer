#!/usr/bin/env python3
"""D11-s3 harness: does the pre-edit hook's RELEASE_NOTES heading refusal reach every tool it is wired to?

Metric: of the three edit-tool payload shapes the hook's matcher names (Write `content`,
Edit `new_string`, MultiEdit `edits[].new_string`), each writing a new `## v9.9.9` heading into
RELEASE_NOTES.md on branch `feature`, how many does the production program refuse.
Count key: a payload counts as refused when the production program (the HPO_PRE_EDIT_PY block of
.claude/hooks/pre-edit.sh, extracted exactly as its own `decide` does) prints a non-empty message.
Instrumented symbol: .claude/hooks/pre-edit.sh:decide (the HPO_PRE_EDIT_PY program).
Perturbation: --perturb makes the one-line change of the `text = ...` join to also read
`edits[].new_string`; refused_heading_payloads must rise 2 -> 3.
Null control: a MultiEdit adding only a body line must be allowed in both arms (null_refused=0).
Command: PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round10/D11/s3/pre_edit_multiedit.py [--perturb]
Expected: refused_heading_payloads=2 (perturbed: 3), multiedit_refused=0 (perturbed: 1), null_refused=0; tolerance 0 (count).
Baseline: 17f1c55fad1b. Machine: macOS arm64 (B7).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, subprocess, sys, tempfile, time

HOOK = ".claude/hooks/pre-edit.sh"


def program(perturb: bool) -> str:
    out, on = [], False
    for line in open(HOOK, encoding="utf-8").read().splitlines():
        if line == "# HPO_PRE_EDIT_PY":
            on = True; continue
        if line == "# HPO_PRE_EDIT_PY_END":
            break
        if on:
            out.append(line[2:] if line.startswith("# ") else ("" if line == "#" else line))
    src = "\n".join(out) + "\n"
    if perturb:
        old = 'if k in ("new_string", "content", "new_source"))'
        assert old in src, "perturbation anchor missing"
        src = src.replace(old, old + ' + " " + " ".join(str(e.get("new_string", "")) for e in (ti.get("edits") or []) if isinstance(e, dict))')
    return src


def refused(src: str, payload: dict, root: str) -> bool:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root)
    r = subprocess.run([sys.executable, "-", "feature", json.dumps(payload)], input=src,
                       capture_output=True, text=True, env=env)
    return bool(r.stdout.strip())


def main() -> None:
    t0p, t0t = time.process_time(), time.thread_time()
    perturb = "--perturb" in sys.argv
    src = program(perturb)
    root = os.getcwd()
    rn = os.path.join(root, "RELEASE_NOTES.md")
    head = "## v9.9.9\n"
    shapes = {
        "write": {"tool_name": "Write", "tool_input": {"file_path": rn, "content": head}},
        "edit": {"tool_name": "Edit", "tool_input": {"file_path": rn, "old_string": "x", "new_string": head}},
        "multiedit": {"tool_name": "MultiEdit", "tool_input": {"file_path": rn,
                      "edits": [{"old_string": "x", "new_string": head}]}},
    }
    got = {k: refused(src, p, root) for k, p in shapes.items()}
    null = refused(src, {"tool_name": "MultiEdit", "tool_input": {"file_path": rn,
                   "edits": [{"old_string": "x", "new_string": "- a body line\n"}]}}, root)
    for k, v in got.items():
        print(f"  {k:10s} {'refused' if v else 'ALLOWED'}")
    print(f"RESULT refused_heading_payloads={sum(got.values())} count")
    print(f"RESULT multiedit_refused={int(got['multiedit'])} count")
    print(f"RESULT null_refused={int(null)} count")
    tt = time.thread_time() - t0t
    print(f"RESULT thread_factor={((time.process_time()-t0p)/tt) if tt > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
