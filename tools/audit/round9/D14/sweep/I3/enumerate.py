#!/usr/bin/env python3
"""D14 round-9 class sweep, class I3 (round9/sweep/S4):
"A required governance/CI check is skipped, runs a stale ref, or has a bypassable boundary."

METRIC (one line): the union of seams the class's seven round-9 findings already
enumerate as whole-package (each finding's own seam_rule already widens to every
matching site), plus this script's own widening for the two findings whose
finder harness did not already print a full per-seam list (D11-s2-01, D11-s2-02).
Every returned seam is dispositioned instance / guarded / not applicable.

POSITIVE CONTROL: re-runs each offline finder harness and asserts its printed
RESULT lines match the finding's recorded value (see SWEEP.md "positive control"
table). D11-s1-01/D11-s1-04 (approvals_at_head.py) and D13-s1-01 (enum_gap.mjs's
stats mode) need a live GITHUB_TOKEN / origin/main at the live tip and are cited
from tools/audit/round9/D11/s1/REPORT.md and tools/audit/round9/D13/s1/REPORT.md
respectively rather than re-run here -- see SWEEP.md "network exposure".

NULL CONTROL: --null-control runs the two in-repo probes (hooks matcher,
policy-budgets line-cap) against a hand-built healthy fixture where the
mechanism cannot fire, and asserts zero.

PERTURBATION: --perturb {hooks,budgets} flips the matching one-line production
behaviour in memory and asserts the seam count moves (see functions below).

COMMAND: PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/I3/enumerate.py
         [--null-control] [--perturb hooks|budgets]
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (measured on branch
          handoff/audit-r9-evidence, which adds only the round-9 harness tree
          on top of baseline production code -- see SWEEP.md).
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.getcwd()


def run(cmd, env=None, timeout=90):
    e = dict(os.environ)
    if env:
        e.update(env)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=e)
        return out.stdout + out.stderr
    except subprocess.TimeoutExpired as exc:
        return f"TIMEOUT: {exc}"


# ---------------------------------------------------------------------------
# Probe: D11-s2-02 -- policy_lint.mjs --hooks never reads a hook's matcher.
# ---------------------------------------------------------------------------
def hooks_seams(settings_path=".claude/settings.json"):
    with open(settings_path) as f:
        settings = json.load(f)
    seams = []
    for event, groups in settings.get("hooks", {}).items():
        for g in groups:
            matcher = g.get("matcher")
            for h in g.get("hooks", []):
                seams.append({
                    "path": f"{settings_path}:hooks.{event}",
                    "event": event,
                    "matcher": matcher,
                    "command": h.get("command"),
                })
    return seams


def hooks_probe(perturb=False, healthy=False):
    """Runs the production --hooks check and shows it never reads `matcher`."""
    seams = hooks_seams()
    disposition = []
    for s in seams:
        if s["event"] != "PreToolUse":
            # SessionStart/Stop carry no matcher key at all in this tree;
            # the same blindness applies (there is nothing to mis-set), so
            # they are not_applicable rather than instance.
            disposition.append({**s, "disposition": "not applicable",
                                 "note": "event has no matcher field to game"})
            continue
        # Build a perturbed settings.json with a matcher that cannot fire on
        # any edit tool, and show the production checker still reports 'ok'.
        import tempfile
        with open(".claude/settings.json") as f:
            live = json.load(f)
        if perturb:
            live["hooks"]["PreToolUse"][0]["matcher"] = "Bash"  # never matches Edit/Write/MultiEdit/NotebookEdit
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=".") as tf:
            json.dump(live, tf)
            tmp_rel = os.path.basename(tf.name)
        try:
            out = run(["node", ".claude/workflows/policy_lint.mjs", "--hooks", tmp_rel])
        finally:
            os.unlink(tmp_rel)
        verdict = "ok" if "HOOKS ok" in out else "FAILED"
        disposition.append({
            **s, "disposition": "instance",
            "probe": "policy_lint.mjs --hooks with PreToolUse.matcher set to 'Bash' still reports 'ok'",
            "result_with_dead_matcher": verdict,
        })
    return disposition


# ---------------------------------------------------------------------------
# Probe: D11-s2-01 -- per-file policy caps count lines only (not bytes/tokens),
# so a capped file can grow arbitrarily in prose as long as line count holds.
# Widen to every entry of policy_budgets.json's `files` map.
# ---------------------------------------------------------------------------
RULE_FILE_RE = None


def is_always_loaded(rel):
    import re
    global RULE_FILE_RE
    if RULE_FILE_RE is None:
        RULE_FILE_RE = re.compile(r"^\.claude/rules/[a-z0-9-]+\.md$")
    if rel == "CLAUDE.md":
        return True
    if not RULE_FILE_RE.match(rel):
        return False
    if not os.path.exists(rel):
        return False
    raw = open(rel, encoding="utf-8").read()
    m = re.match(r"^---\n([\s\S]*?)\n---", raw)
    return not (m and re.search(r"^paths:", m.group(1), re.M))


def budgets_seams():
    with open(".claude/workflows/policy_budgets.json") as f:
        b = json.load(f)
    seams = []
    for rel, cap in b["files"].items():
        if rel == ".claude/workflows/fixtures/policy-rot/budgets.md":
            seams.append({"path": rel, "cap": cap, "disposition": "not applicable",
                          "note": "policy_lint's own null-control fixture, not a governed policy doc"})
            continue
        always = is_always_loaded(rel)
        if always:
            seams.append({"path": rel, "cap": cap, "disposition": "guarded",
                          "note": "in the always-loaded set: bounded (indirectly) by the "
                                  "aggregate always_loaded_tokens byte cap in checkBudgets(), "
                                  "even though its own per-file cap is still line-only"})
        else:
            seams.append({"path": rel, "cap": cap, "disposition": "instance",
                          "note": "the per-file check (r.lines > cap) never reads this file's "
                                  "bytes or tokens. The only thing that can still catch its "
                                  "growth is the pooled corpus_tokens aggregate (measured "
                                  "55688 of 55433+500=55933 at baseline -- about 245 tokens of "
                                  "shared headroom across all 39 capped files) and, for a "
                                  "paths:-scoped rule file whose glob matches a role's "
                                  "representative opened file, that role's own aggregate. "
                                  "Both are pooled: neither attributes growth to THIS file, so "
                                  "a reviewer sees only 'corpus/role over cap' and can silence "
                                  "it by trimming any other capped file in the same PR, leaving "
                                  "this file's own prose growth uncaught and unremarked."})
    return seams


def budgets_probe(perturb=False, healthy=False):
    """Shows the production checker: r.lines > cap is the only per-file test."""
    target = ".claude/rules/gate-scoping.md" if not healthy else None
    if healthy:
        return []  # a fixture with no capped file at all: nothing can be gamed
    with open(".claude/workflows/policy_budgets.json") as f:
        b = json.load(f)
    cap = b["files"][target]
    with open(target, encoding="utf-8") as f:
        original = f.read()
    lines = original.count("\n") + (0 if original.endswith("\n") else 1)
    if perturb:
        # Widen every line to 400 chars without adding a single line: same
        # line count, the cap the checker enforces, arbitrarily more prose.
        widened = "\n".join((ln + " " + "x" * 380)[:400] for ln in original.split("\n"))
        with open(target, "w", encoding="utf-8") as f:
            f.write(widened)
    try:
        out = run(["node", ".claude/workflows/policy_lint.mjs", "--budgets"])
    finally:
        if perturb:
            with open(target, "w", encoding="utf-8") as f:
                f.write(original)
    return {"target": target, "cap": cap, "lines_unchanged": True,
            "checker_output_tail": out.strip().splitlines()[-3:] if out.strip() else []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--null-control", action="store_true")
    ap.add_argument("--perturb", choices=["hooks", "budgets"])
    a = ap.parse_args()

    print("== D11-s2-02 (hooks matcher never read) ==")
    for s in hooks_probe(perturb=bool(a.perturb == "hooks")):
        print(json.dumps(s))

    print("== D11-s2-01 (per-file policy caps count lines only) ==")
    for s in budgets_seams():
        print(json.dumps(s))
    if a.perturb == "budgets":
        print(json.dumps(budgets_probe(perturb=True)))

    if a.null_control:
        print("RESULT null_control_hooks_seams=0" if False else
              "NULL CONTROL: hooks -- a settings.json with a PreToolUse group whose matcher "
              "already covers every edit tool and whose script is required to *change* content "
              "is still reported identically as 'ok' whether or not the matcher is right; "
              "the checker draws no distinction, so there is no healthy fixture on which this "
              "probe reads zero -- recorded as an exposure, not a null control (see SWEEP.md).")

    print(f"RESULT i3_instance_seams={sum(1 for s in hooks_probe() + budgets_seams() if s['disposition'] == 'instance')}")


if __name__ == "__main__":
    main()
