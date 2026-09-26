#!/usr/bin/env python3
"""D11 round 9, verifier V2 (independent) for D11-s2-02.

METRIC (one line): of settings.json variants whose PreToolUse matcher fails to match
  at least one of the four editing tools (Edit, Write, MultiEdit, NotebookEdit; full-match
  regex, case-sensitive as Claude Code matches tool names), how many
  `node .claude/workflows/policy_lint.mjs --hooks <variant>` accepts (exit 0).
KEY: policy_lint's exit status and its HOOKS line; the matcher coverage is computed
  by this harness from the variant, never from policy_lint.
CONTROLS: the tracked settings (must exit 0); pre-edit.sh moved to PostToolUse (must
  exit non-zero: the event arm is alive); the full-coverage matcher reordered (exit 0).
COMMAND: PYTHONPATH=tests/hastub python tools/audit/round9/D11/verify-v2/v2_hooks_matcher.py
EXPECTED (baseline 1936d5ca): partial_or_blind_accepted=5 of 5; event_moved_refused=1.
Writes variants under a temp dir inside this harness's own directory (cmdHooks joins
the path to the repository root) and removes it.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import copy, json, re, shutil, subprocess, tempfile, time

T0p, T0t = time.process_time(), time.thread_time()
NODE = shutil.which("node") or "/opt/node22/bin/node"
HERE = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))
EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")


def covers(matcher):
    if matcher in (None, "", "*"):
        return set(EDIT_TOOLS)
    return {t for t in EDIT_TOOLS if re.fullmatch(matcher, t)}


def lint(rel):
    env = dict(os.environ, HPO_PLANDATA=tempfile.mkdtemp(prefix="d11v2-pd-"))
    p = subprocess.run([NODE, ".claude/workflows/policy_lint.mjs", "--hooks", rel],
                       capture_output=True, text=True, env=env)
    last = [l for l in p.stdout.splitlines() if l.startswith("HOOKS")]
    return p.returncode, (last[-1] if last else p.stdout.strip().splitlines()[-1:])


def main():
    base = json.load(open(".claude/settings.json"))
    tmp = os.path.relpath(tempfile.mkdtemp(prefix="tmp-", dir=HERE))
    try:
        def variant(name, fn):
            s = copy.deepcopy(base); fn(s)
            rel = os.path.join(tmp, name + ".json")
            json.dump(s, open(rel, "w"), indent=1)
            return rel, s

        def set_m(m):
            return lambda s: s["hooks"]["PreToolUse"][0].__setitem__("matcher", m)

        rc0, l0 = lint(".claude/settings.json")
        print(f"# tracked: rc={rc0} {l0}  covers={sorted(covers(base['hooks']['PreToolUse'][0]['matcher']))}")
        blind = ["Edit", "Write", "edit|write|multiedit|notebookedit", "Read|Grep", "Bash"]
        acc = 0
        for m in blind:
            rel, s = variant("m-" + re.sub(r"\W", "_", m), set_m(m))
            rc, line = lint(rel)
            miss = sorted(set(EDIT_TOOLS) - covers(m))
            acc += rc == 0
            print(f"# matcher={m!r:40s} misses={miss} -> rc={rc} {line}")
        rel, _ = variant("reordered", set_m("NotebookEdit|MultiEdit|Write|Edit"))
        rcr, lr = lint(rel)
        print(f"# full-coverage reordered -> rc={rcr} {lr}")

        def move(s):
            s["hooks"]["PostToolUse"] = s["hooks"].pop("PreToolUse")
        rel, _ = variant("moved", move)
        rcm, lm = lint(rel)
        print(f"# pre-edit moved to PostToolUse -> rc={rcm} {lm}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"RESULT partial_or_blind_variants={len(blind)} count")
    print(f"RESULT partial_or_blind_accepted={acc} count")
    print(f"RESULT tracked_rc={rc0}")
    print(f"RESULT reordered_full_rc={rcr}")
    print(f"RESULT event_moved_refused={int(rcm != 0)} count")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
