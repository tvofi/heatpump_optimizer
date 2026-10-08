"""D11-s2 harness: `policy_lint --hooks` never reads a hook's `matcher`.

Metric: of M settings.json variants whose PreToolUse matcher no longer names any
  file-editing tool (so pre-edit.sh never runs on an edit), how many
  policy_lint.mjs:cmdHooks refuses (exit != 0) (count; want M, is 0).
Count key: cmdHooks' own exit status on a settings file passed as its argument.
Arms: the tracked settings (null: exit 0); M matcher variants ("Read", "Bash",
  "Glob", "NoSuchTool"); a live control (script path renamed -> MISSING, must
  refuse); and the same M variants under a one-line production edit to cmdHooks
  that marks a PreToolUse row NOT WIRED when its group's matcher does not match
  "Edit" (must refuse all M).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s2/hooks_matcher.py
Expected: RESULT variants_refused=0 of 4, control_refused=1, perturbed_refused=4 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B3, 4 CPUs, Linux.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import temp_root, clone, node, tail, ROOT  # noqa: E402
import json, copy

LINT = ".claude/workflows/policy_lint.mjs"
VARIANTS = ["Read", "Bash", "Glob", "NoSuchTool"]
ANCHOR = "        const script = `.claude/hooks/${m[0].split('/').pop()}`\n"
EDIT = ANCHOR + ("        if (event === 'PreToolUse' && !new RegExp(`^(?:${g.matcher ?? ''})$`).test('Edit')) "
                 "{ rows.push({ event: 'PreToolUse(matcher)', script, verdict: 'NOT WIRED', why: `matcher ${g.matcher} never matches Edit` }); continue }\n")


def run(tree, settings, tmp, name):
    p = os.path.join(tmp, name + ".json")
    json.dump(settings, open(p, "w"))
    rc, out = node(tree, LINT, "--hooks", os.path.relpath(p, tree))
    return rc, out.strip().splitlines()[-1] if out.strip() else ""


def main():
    tmp = temp_root("hooks")
    base = json.load(open(os.path.join(ROOT, ".claude/settings.json")))
    rc0, l0 = run(ROOT, base, tmp, "null")
    print(f"# null (tracked settings): rc={rc0} {l0}")
    refused = 0
    for v in VARIANTS:
        s = copy.deepcopy(base)
        s["hooks"]["PreToolUse"][0]["matcher"] = v
        rc, l = run(ROOT, s, tmp, f"v-{v}")
        refused += rc != 0
        print(f"# matcher={v!r}: rc={rc} {l}")
    s = copy.deepcopy(base)
    s["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = 'bash "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-edit-gone.sh"'
    rcc, lc = run(ROOT, s, tmp, "control")
    print(f"# control (script renamed): rc={rcc} {lc}")
    c = os.path.join(tmp, "clone")
    clone(c)
    p = os.path.join(c, LINT)
    src = open(p).read()
    assert src.count(ANCHOR) == 1, "perturbation anchor moved"
    open(p, "w").write(src.replace(ANCHOR, EDIT))
    rcp0, lp0 = run(c, base, tmp, "pnull")
    print(f"# perturbed, tracked settings: rc={rcp0} {lp0}")
    pref = 0
    for v in VARIANTS:
        s = copy.deepcopy(base)
        s["hooks"]["PreToolUse"][0]["matcher"] = v
        rc, l = run(c, s, tmp, f"p-{v}")
        pref += rc != 0
    print(f"RESULT variants={len(VARIANTS)} count")
    print(f"RESULT null_rc={rc0}")
    print(f"RESULT variants_refused={refused} count")
    print(f"RESULT control_refused={int(rcc != 0)} count")
    print(f"RESULT perturbed_null_rc={rcp0}")
    print(f"RESULT perturbed_refused={pref} count")
    tail()


if __name__ == "__main__":
    main()
