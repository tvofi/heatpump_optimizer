#!/usr/bin/env python3
"""D5-s10: does pre-edit.sh's "generated from .claude/rules/" comment and refusal send a seat to the real source?

Metric: edit_reaches_cursor = 1 when a line planted in the directory the hook's own refusal message names as
"the source" (Edit the <X> source and regenerate) survives `node tools/policy/rules_sync.mjs` (regenerate) and
reaches .cursor/rules/<rule>.mdc; 0 when regeneration discards it. Second number: unguarded_generated = how many
of rules_sync.mjs's generated output directories (.claude/rules, .cursor/rules) the hook lets an Edit through.
Count key: the directory parsed from the message .claude/hooks/pre-edit.sh actually prints (exit 2) for a
.cursor/rules path, and the exit status the hook returns for each generated directory.
Instrumented: .claude/hooks/pre-edit.sh:decide (its HPO_PRE_EDIT_PY block), driven end to end over stdin, and
tools/policy/rules_sync.mjs (SRC, CLAUDE_OUT, CURSOR_OUT), run for real in a scratch copy.

Command (from the export root; --repo is any git checkout holding --ref):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s10/pre_edit_source.py \
      --repo /home/user/heatpump_optimizer --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 [--perturb]
Expected at baseline 92d38ecb (box B12, round 11): RESULT named_source=.claude/rules/, edit_reaches_cursor=0,
unguarded_generated=1, exact.
Perturbation: --perturb rewrites `.claude/rules/` to `dev/governance/rules/` in the hook copy's refusal message
(the one-line production fix): edit_reaches_cursor goes 0 -> 1 (up).
Writes only under a mkdtemp root.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, json, re, shutil, subprocess, tempfile, time
from pathlib import Path

HOOK = ".claude/hooks/pre-edit.sh"
RULE = "gate-scoping"
PLANT = "PLANTED-BY-D5-S10: a hand edit made where the hook said the source is."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    c0, h0 = time.process_time(), time.thread_time()
    root = Path(tempfile.mkdtemp(prefix="d5s10_preedit_"))
    try:
        t = root / "tree"
        # a scratch tree at --ref holding exactly what the hook and rules_sync read
        arch = subprocess.run(["git", "-C", a.repo, "archive", a.ref, ".claude/hooks", ".claude/rules", ".cursor/rules",
                               "dev/governance/rules", "tools/policy"], capture_output=True, check=True).stdout
        t.mkdir()
        subprocess.run(["tar", "-x", "-C", str(t)], input=arch, check=True)
        hook = (t / HOOK).read_text()
        if a.perturb:
            start, end = hook.index("# if rel.startswith(\".cursor/rules/\"):"), hook.index("# HPO_PRE_EDIT_PY_END")
            hook = hook[:start] + hook[start:end].replace(".claude/rules/", "dev/governance/rules/") + hook[end:]
            (t / HOOK).write_text(hook)
        g = lambda *x: subprocess.run(["git", "-C", str(t), *x], capture_output=True, text=True)
        g("init", "-q", "-b", "feature")
        g("add", "-A")
        g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed")

        def hook_on(rel):
            p = subprocess.run(["bash", str(t / HOOK)], input=json.dumps({"tool_input": {"file_path": str(t / rel)}}),
                               cwd=t, text=True, capture_output=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=str(t)))
            return p.returncode, p.stderr

        rc_cursor, msg = hook_on(f".cursor/rules/{RULE}.mdc")
        m = re.search(r"Edit the (\S+) source", msg)
        named = m.group(1) if m else ""
        print(f"RESULT cursor_refused_rc={rc_cursor} exit")
        print(f"RESULT named_source={named}")
        # follow the refusal: edit the named source, regenerate, and look where the edit went
        src = t / named / f"{RULE}.md"
        before_cursor = (t / f".cursor/rules/{RULE}.mdc").read_text()
        rc_src, _ = hook_on(f"{named}{RULE}.md")
        src.write_text(src.read_text() + "\n" + PLANT + "\n")
        regen = subprocess.run(["node", "tools/policy/rules_sync.mjs"], cwd=t, capture_output=True, text=True)
        after_cursor = (t / f".cursor/rules/{RULE}.mdc").read_text()
        survives = PLANT in src.read_text()
        reaches = PLANT in after_cursor and PLANT not in before_cursor
        print(f"RESULT hook_rc_on_named_source={rc_src} exit")
        print(f"RESULT regenerate_rc={regen.returncode} exit")
        print(f"RESULT edit_survives_regeneration={int(survives)} bool")
        print(f"RESULT edit_reaches_cursor={int(reaches)} bool")
        # rules_sync.mjs's own outputs: which does the hook let an Edit through?
        sync = (t / "tools/policy/rules_sync.mjs").read_text()
        outs = re.findall(r"const (?:CLAUDE|CURSOR)_OUT = path\.join\(ROOT, '([^']+)', '([^']+)'\)", sync)
        unguarded = []
        for d1, d2 in outs:
            rc, _ = hook_on(f"{d1}/{d2}/{RULE}.{'mdc' if d1 == '.cursor' else 'md'}")
            if rc == 0:
                unguarded.append(f"{d1}/{d2}")
        print(f"RESULT generated_dirs={len(outs)} count")
        print(f"RESULT unguarded_generated={len(unguarded)} count")
        for d in unguarded:
            print(f"   unguarded {d}")
        # null control: production code is allowed either way
        print(f"RESULT null_prod_rc={hook_on('custom_components/heatpump_optimizer/const.py')[0]} exit")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    pc = time.process_time() - c0
    print(f"RESULT thread_factor={pc / max(time.thread_time() - h0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
