#!/usr/bin/env python3
"""VERIFIER-OWN harness for D11-03 (round 4, verifier seat 1).

METRIC (my own definition):
  claudemd_claims_enforced   -- 1 when CLAUDE.md carries a sentence asserting
                                the red-check trigger IS enforced.
  refusal_fires_with_red     -- rc of `policy_lint.mjs --pr-body <corpus's own
                                unnamed-red fixture> --red 'fast (3.14)'` ...
  refusal_with_ci_args       -- rc of the SAME body through the argument list
                                PARSED OUT OF governance.yml's `Check the body
                                against the contract` step (not hardcoded):
                                --pr-body/--head/--title/--paths-file only.
  ci_steps_passing_red       -- steps in .github/workflows/*.yml whose run line
                                invokes policy_lint.mjs with --red outside a
                                --self-test.
  executable_red_callers     -- non-doc files in the tree invoking policy_lint
                                with --red at all (grep), split self-test vs live.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/d11_own_D11-03.py

EXPECTED (tolerance: exact at tree head 0855277):
  claudemd_claims_enforced=1 refusal_fires_with_red_rc=1
  refusal_with_ci_args_rc=0 ci_steps_passing_red=0
MACHINE: verifier seat 1 worktree audit-r4-verify-D11-1, 2026-09-12; static +
two node invocations, no timing claim.

PERTURBATION. Append "--red does-not-exist-check" to the parsed CI argument
list and the same body must flip rc 0 -> 1; that is the control that the flip
is caused by --red and not by the fixture or the environment.
"""

import os
import re
import subprocess
import sys
import tempfile

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)[:400]


def main():
    # 1. the claim in CLAUDE.md
    cl = open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").read()
    claims = re.search(r"[Oo]nly the red-check trigger is enforced", cl)
    print(f"CLAUDE.md claims the red-check trigger is enforced: {bool(claims)}")

    # 2. the CI step's argument list, parsed from governance.yml
    gov = open(os.path.join(ROOT, ".github/workflows/governance.yml"),
               encoding="utf-8").read()
    m = re.search(
        r"run: \|\n\s+node \.claude/workflows/policy_lint\.mjs \\\n(.+?)\n\n", gov, re.S)
    step_body = m.group(0) if m else ""
    step_passes_red = "--red" in step_body
    print("governance.yml body-contract step (parsed):")
    print("  " + " ".join(step_body.split())[:200])
    print(f"  passes --red: {step_passes_red}")

    # every policy_lint invocation in workflows, flagged for --red
    wf_red_steps = []
    for name in sorted(os.listdir(os.path.join(ROOT, ".github/workflows"))):
        if not name.endswith((".yml", ".yaml")):
            continue
        t = open(os.path.join(ROOT, ".github/workflows", name), encoding="utf-8").read()
        for mm in re.finditer(r"node \.claude/workflows/policy_lint\.mjs[^\n]*", t):
            if "--red" in mm.group(0):
                wf_red_steps.append((name, mm.group(0)[:80]))
    print(f"workflow policy_lint invocations passing --red: {wf_red_steps or 'none'}")

    # 3. drive the refusal both ways, on the corpus's own fixture
    body = ".claude/workflows/fixtures/policy-rot/prepr/unnamed-red.md"
    paths = os.path.join(tempfile.gettempdir(), "d11-own-03-paths.txt")
    open(paths, "w").write("README.md\n")
    zero = "0" * 40
    base = ["node", ".claude/workflows/policy_lint.mjs", "--pr-body", body,
            "--head", zero, "--title", "t", "--paths-file", paths]
    rc_red, _ = run(base + ["--red", "fast (3.14)"])
    rc_ci, _ = run(base)
    print(f"same body, with --red 'fast (3.14)': rc={rc_red}")
    print(f"same body, CI's argument list:      rc={rc_ci}")

    # 4. perturbation: add --red to the CI list -> must flip
    rc_pert, _ = run(base + ["--red", "does-not-exist-check"])
    print(f"perturbed CI list (+ --red bogus):  rc={rc_pert} (must be 1)")

    # 5. every executable --red caller in the tree
    callers = []
    for dirpath, _dirs, files in os.walk(ROOT):
        if "/.git" in dirpath or "/tools/audit/round" in dirpath:
            continue
        for f in files:
            if not f.endswith((".sh", ".mjs", ".js", ".yml", ".yaml", ".py")):
                continue
            p = os.path.join(dirpath, f)
            try:
                txt = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if "policy_lint.mjs" in txt and "--red" in txt:
                rel = os.path.relpath(p, ROOT)
                for i, line in enumerate(txt.split("\n"), 1):
                    if "--red" in line and "policy_lint" not in line and "--pr-body" not in line:
                        callers.append((rel, i))
                break
    grep = subprocess.run(
        ["grep", "-rn", "--", "--red", "--include=*.sh", "--include=*.mjs",
         "--include=*.yml", os.path.join(ROOT, "tools"), os.path.join(ROOT, ".github"),
         os.path.join(ROOT, ".claude")],
        capture_output=True, text=True).stdout.split("\n")
    live_callers = [g for g in grep if "policy_lint" in g or "--pr-body" in g]
    print("tree callers passing --red to policy_lint:")
    for c in live_callers:
        print(f"  {c[:130]}")

    print()
    print(f"RESULT claudemd_claims_enforced={int(bool(claims))}")
    print(f"RESULT refusal_fires_with_red_rc={rc_red}")
    print(f"RESULT refusal_with_ci_args_rc={rc_ci}")
    print(f"RESULT ci_steps_passing_red={len(wf_red_steps)}")
    print(f"RESULT perturbed_ci_rc={rc_pert}")


if __name__ == "__main__":
    main()
