#!/usr/bin/env python3
"""D11-s3 (round 11): the enumerator for D11.M4 and D11.M5 -- the mechanism inventory of D11.M1,
derived from the tree (and, for the rulesets, from the API read captured in data/), one row per
refusal a seat can meet, printed `<family>\t<item>` one per line.

Metric: none; this prints a universe. Rows:
  ruleset          each ruleset GET repos/tvofi/heatpump_optimizer/rulesets lists (data/rulesets_list.json,
                   captured 2026-11-16; re-read live the same day, unchanged)
  required-context each `contexts` entry of tools/policy/fixtures/required-contexts.json (the ruleset's)
  gate-required    each `gate_required` entry there (the jobs tools/ci/gate.py folds into `gate`)
  policy_lint      each check of CORPUS_CHECK_NAMES and LOOP_CHECK_NAMES in tools/policy/policy_lint.mjs,
                   plus its standalone modes `--hooks`
  policy-tool      every other script under tools/policy/ (brief_lint.mjs among them)
  gate-script      each key of tests/closures.json `closures` (the measured tests/ gate)
  claim-file       tests/golden/claimed_drift.txt, tests/golden/card_claimed_drift.txt
  pr-tool          each .sh/.py under tools/pr/
  plan-tool        each .py under tools/plan/
  ci-tool          each .sh/.py under tools/ci/
  seat-instrument  each top-level tools/audit/seat/ script carrying `--self-test`
  hook             each .claude/hooks/*.sh .claude/settings.json wires
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/inventory.py
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (4 vCPU container). Expected: 229 rows, exact.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
R = pathlib.Path.cwd()


def rows():
    for r in json.loads((HERE / "data/rulesets_list.json").read_text()):
        yield "ruleset", "%s %s" % (r["id"], r["name"])
    fx = json.loads((R / "tools/policy/fixtures/required-contexts.json").read_text())
    for c in fx["contexts"]:
        yield "required-context", c
    for c in fx["gate_required"]:
        yield "gate-required", c
    pl = (R / "tools/policy/policy_lint.mjs").read_text()
    corpus = re.search(r"^const CORPUS_CHECK_NAMES = \[(.*?)\]", pl, re.M | re.S).group(1)
    for n in re.findall(r"'(\w+)'", corpus):
        yield "policy_lint", "corpus " + n
    loop = re.search(r"^const LOOP_CHECK_NAMES = \[(.*?)^\]", pl, re.M | re.S).group(1)
    for n in re.findall(r"\{ name: '(\w+)'", loop):
        yield "policy_lint", "record " + n
    yield "policy_lint", "mode --hooks"
    for p in sorted((R / "tools/policy").iterdir()):
        if p.is_file() and p.suffix in (".mjs", ".py", ".sh") and p.name != "policy_lint.mjs":
            yield "policy-tool", "tools/policy/" + p.name
    cl = json.loads((R / "tests/closures.json").read_text())["closures"]
    for k in sorted(cl):
        yield "gate-script", k
    for f in ("tests/golden/claimed_drift.txt", "tests/golden/card_claimed_drift.txt"):
        yield "claim-file", f
    for d, fam, sfx in (("tools/pr", "pr-tool", (".sh", ".py")), ("tools/plan", "plan-tool", (".py",)),
                        ("tools/ci", "ci-tool", (".sh", ".py"))):
        for p in sorted((R / d).iterdir()):
            if p.is_file() and p.suffix in sfx:
                yield fam, "%s/%s" % (d, p.name)
    for p in sorted((R / "tools/audit/seat").iterdir()):
        if p.is_file() and p.suffix in (".py", ".sh", ".mjs", ".js"):
            try:
                if "--self-test" in p.read_text(errors="replace"):
                    yield "seat-instrument", "tools/audit/seat/" + p.name
            except OSError:
                pass
    st = json.loads((R / ".claude/settings.json").read_text())
    seen = []
    for groups in st.get("hooks", {}).values():
        for g in groups:
            for h in g.get("hooks", []):
                m = re.search(r"\.claude/hooks/[\w.-]+\.sh", h.get("command", ""))
                if m and m.group(0) not in seen:
                    seen.append(m.group(0))
    for s in sorted(seen):
        yield "hook", s


if __name__ == "__main__":
    for fam, item in rows():
        print("%s\t%s" % (fam, item))
