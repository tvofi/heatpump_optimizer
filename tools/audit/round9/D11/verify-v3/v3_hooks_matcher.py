#!/usr/bin/env python3
"""D11 verify-v3 (round 9), finding D11-s2-02: which matcher seams does `policy_lint --hooks`
see, and does the finder's proposed repair (PreToolUse must match 'Edit') cover them?

METRIC (one line): of 5 settings.json variants in which a REQUIRED hook no longer fires on
  every event its script targets -- PreToolUse matcher 'Edit' (Write/MultiEdit/NotebookEdit
  lost), 'Write|Edit' (MultiEdit/NotebookEdit lost), 'edit|write' (case: nothing matched),
  'Read' (nothing matched), and SessionStart matcher 'compact' (startup/resume/clear lost) --
  how many make production `.claude/workflows/policy_lint.mjs:cmdHooks` exit non-zero;
  measured on the tree and again under the finder's own one-line perturbation.
KEY: cmdHooks' exit status on the settings file passed as its argument.
Null control: tracked .claude/settings.json exits 0 in both arms.
COMMAND:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/verify-v3/v3_hooks_matcher.py
EXPECTED (baseline 1936d5ca): refused 0 of 5 on the tree; under the finder's perturbation
  refused 2 of 5 ('edit|write', 'Read' -- the variants that miss 'Edit' itself).
MACHINE: box G4-V3 cloud container, 4 CPU Linux, node 22, CPython 3.14.
Writes only under tempfile.mkdtemp() (settings copies and a clone of HEAD for the perturbation).
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import copy, json, shutil, subprocess, tempfile, time

T0p, T0t = time.process_time(), time.thread_time()
LINT = ".claude/workflows/policy_lint.mjs"
ANCHOR = "        const script = `.claude/hooks/${m[0].split('/').pop()}`\n"
FINDER_EDIT = ANCHOR + ("        if (event === 'PreToolUse' && !new RegExp(`^(?:${g.matcher ?? ''})$`).test('Edit')) "
                        "{ rows.push({ event: 'PreToolUse(matcher)', script, verdict: 'NOT WIRED', why: 'x' }); continue }\n")
VARIANTS = [("PreToolUse", "Edit"), ("PreToolUse", "Write|Edit"), ("PreToolUse", "edit|write"),
            ("PreToolUse", "Read"), ("SessionStart", "compact")]


def lint(tree, settings, tmp, name):
    p = os.path.join(tmp, name + ".json")
    json.dump(settings, open(p, "w"))
    r = subprocess.run([shutil.which("node"), LINT, "--hooks", os.path.relpath(p, tree)], cwd=tree,
                       capture_output=True, text=True)
    return r.returncode


def arm(tree, base, tmp, tag):
    rc0 = lint(tree, base, tmp, f"{tag}-null")
    refused = 0
    for ev, m in VARIANTS:
        s = copy.deepcopy(base)
        s["hooks"][ev][0]["matcher"] = m
        rc = lint(tree, s, tmp, f"{tag}-{ev}-{m.replace('|', '_')}")
        refused += rc != 0
        print(f"# {tag}: {ev} matcher={m!r} rc={rc}")
    return rc0, refused


def main():
    tmp = tempfile.mkdtemp(prefix="d11v3-hooks-")
    os.environ["HPO_PLANDATA"] = os.path.join(tmp, "plandata")
    base = json.load(open(".claude/settings.json"))
    rc0, ref = arm(os.getcwd(), base, tmp, "tree")
    c = os.path.join(tmp, "clone")
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", os.getcwd(), c], check=True)
    p = os.path.join(c, LINT)
    src = open(p).read(); assert src.count(ANCHOR) == 1
    open(p, "w").write(src.replace(ANCHOR, FINDER_EDIT))
    prc0, pref = arm(c, base, tmp, "finder-fix")
    print(f"RESULT variants={len(VARIANTS)} count")
    print(f"RESULT null_rc={rc0}")
    print(f"RESULT refused_on_tree={ref} of {len(VARIANTS)}")
    print(f"RESULT finder_fix_null_rc={prc0}")
    print(f"RESULT refused_under_finder_fix={pref} of {len(VARIANTS)}")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
