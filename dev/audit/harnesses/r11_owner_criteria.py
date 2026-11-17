#!/usr/bin/env python3
"""R11-PRE-OWNER-CRITERIA: the round-11 unset gaps, and each criteria file
applied to one planted finding that meets it and one that does not.

Written by the R11-PRE-OWNER-CRITERIA fixer. Run from a worktree root:

    python3 dev/audit/harnesses/r11_owner_criteria.py gaps <eval-ref> <head-ref>
    python3 dev/audit/harnesses/r11_owner_criteria.py plants

``gaps``: for each ref, a scratch commit (never a branch) whose
``dev/audit/yardstick/round11/EVALUATION.json`` marks every ``E11-T-*`` and
``E11-K-*`` card accepted, then ``tools/audit/check_scopes.py --round 11``
at it; prints each "still leaves unset" and "unset and no card" gap. Pass
``<eval-ref>`` as eval/r11's tip and ``<head-ref>`` as a merge of the head
with it: the eval ref is the null control, printing the gaps the head's
``objective.json`` must close.

``plants``: one met and one unmet plant per criteria file under
``dev/governance/dimensions/criteria/``, each applying the statement's own
rule (D10 Q1's command over a planted copy of ``quality_scale.yaml``, D4
P2's WCAG ratio, D5 C5's word count, D9 B1's 60 s budget times F = 5).
Each line prints the plant, the measured value and FAILS or PASSES; a met
plant must print FAILS and an unmet one PASSES, else the run exits 1.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile

EVAL = "dev/audit/yardstick/round11/EVALUATION.json"
YAML = "custom_components/heatpump_optimizer/quality_scale.yaml"
CRIT = "dev/governance/dimensions/criteria/"


def git(*args, **kw):
    return subprocess.check_output(["git", *args], text=True, **kw).strip()


def overlay(ref):
    ev = json.loads(git("show", f"{ref}:{EVAL}"))
    n = 0
    for cid, card in ev["cards"].items():
        if cid.startswith(("E11-T-", "E11-K-")):
            card.update(decision="accepted", ruling="scratch overlay")
            n += 1
    blob = git("hash-object", "-w", "--stdin", input=json.dumps(ev, indent=1))
    fd, index = tempfile.mkstemp()
    os.close(fd)
    env = dict(os.environ, GIT_INDEX_FILE=index)
    try:
        subprocess.check_call(["git", "read-tree", ref], env=env)
        subprocess.check_call(["git", "update-index", "--cacheinfo", f"100644,{blob},{EVAL}"], env=env)
        tree = git("write-tree", env=env)
    finally:
        os.unlink(index)
    return git("commit-tree", tree, "-p", ref, "-m", "scratch overlay"), n


def gaps(refs):
    for ref in refs:
        sha, n = overlay(ref)
        out = subprocess.run([sys.executable, "tools/audit/check_scopes.py", "--repo", ".", "--ref", sha, "--round", "11"],
                             capture_output=True, text=True).stdout.splitlines()
        hit = [ln.strip() for ln in out if "still leaves unset" in ln or "is unset and no card" in ln]
        print(f"== {ref} (overlay {sha[:10]}, {n} cards accepted): {len(hit)} unset gap(s)")
        for ln in hit:
            print("  " + ln.split(" card ", 1)[-1])


def q1_rows(text):
    import yaml
    rules = yaml.safe_load(text)["rules"]
    st = lambda v: v if isinstance(v, str) else v["status"]
    return [k for k, v in rules.items() if st(v) not in ("done", "exempt")
            or (st(v) == "exempt" and (isinstance(v, str) or not str(v.get("comment", "")).strip()))]


def luminance(hexrgb):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hexrgb[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(fg, bg):
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def plants():
    for f in ("D4", "D5", "D9", "D10"):
        if not os.path.isfile(f"{CRIT}{f}-criteria.md"):
            sys.exit(f"{CRIT}{f}-criteria.md is not in this tree")
    live = open(YAML).read()
    rows = []
    todo = live.replace("\n  has-entity-name: done\n", "\n  has-entity-name: todo\n", 1)
    bare = live.replace("\n  async-dependency: done\n", "\n  async-dependency: exempt\n", 1)
    assert todo != live and bare != live, "a plant matched nothing"
    rows += [("D10 Q1", "met: has-entity-name: todo", q1_rows(todo), True),
             ("D10 Q1", "met: async-dependency exempt, no comment", q1_rows(bare), True),
             ("D10 Q1", "unmet: the live register", q1_rows(live), False)]
    for fg, met in (("#777777", True), ("#767676", False)):
        r = contrast(fg, "#ffffff")
        rows.append(("D4 P2", f"{'met' if met else 'unmet'}: body text {fg} on #ffffff", round(r, 3), r < 4.5))
    long = " ".join(["word"] * 41) + "."
    short = "The cap keeps a slow plan from starving the event loop."
    for txt, met in ((long, True), (short, False)):
        n = max(len(s.split()) for s in re.split(r"(?<=[.!?])\s+", txt) if s)
        rows.append(("D5 C5", f"{'met' if met else 'unmet'}: a comment's longest sentence", n, n > 40))
    for host_s, met in ((13.0, True), (3.6, False)):
        pi = host_s * 5
        rows.append(("D9 B1", f"{'met' if met else 'unmet'}: {host_s} s host solver CPU per cycle, x F=5", pi, pi > 60))
    bad = 0
    for crit, plant, value, fails in rows:
        verdict = bool(value) if isinstance(value, list) else fails
        want = plant.startswith("met")
        bad += verdict != want
        print(f"{crit}\t{plant}\t{value}\t{'FAILS' if verdict else 'PASSES'}{'' if verdict == want else '  <-- WRONG'}")
    print(f"plants: {len(rows)}, wrong: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    if sys.argv[1:2] == ["gaps"] and len(sys.argv) == 4:
        gaps(sys.argv[2:])
    elif sys.argv[1:] == ["plants"]:
        plants()
    else:
        sys.exit(__doc__)
