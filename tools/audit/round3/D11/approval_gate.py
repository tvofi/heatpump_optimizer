#!/usr/bin/env python3
"""D11: the `## Approval` gate is keyed on the pull-request TITLE, not on the diff.

METRIC (one line): the fraction of first-parent commits on `main` in the window
that changed at least one file matched by `policy_lint.mjs`'s own POLICY_GLOBS
while carrying a subject that does not start with `policy:` -- i.e. that reached
`main` with `checkPrBody`'s `## Approval` requirement switched off, decided by
free text the author wrote.

INSTRUMENTED SYMBOL: .claude/workflows/policy_lint.mjs:checkPrBody (driven
through `node .claude/workflows/policy_lint.mjs --pr-body ... --title ...`), and
its `POLICY_H2` / `isPolicy` branch.

RUN (offline; git only, no GitHub, no network):
    cd <repo root> && PYTHONPATH=tests/hastub python3 tools/audit/round3/D11/approval_gate.py

PERTURBATION (run by this harness itself, arms A and B): one identical body with
no `## Approval` section, checked twice with only the --title prefix changed.
Arm A `policy: ...` must exit 1; arm B `docs: ...` must exit 0. If both arms
agree, the finding is void.

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
(window 2026-08-27T21:02:51Z..2026-09-10T21:02:51Z):
    RESULT arm_policy_title_exit=1 +/-0
    RESULT arm_docs_title_exit=0 +/-0
    RESULT policy_globs_in_production=10 +/-0
    RESULT policy_touching_commits=82 +/-0     (tree-derived, deterministic at this SHA)
    RESULT approval_not_required=64 +/-0
    RESULT approval_not_required_fraction=0.7805 +/-0.0001
    RESULT rule_text_commits=50 +/-0
    RESULT rule_text_approval_not_required=32 +/-0
    RESULT rule_text_approval_not_required_fraction=0.6400 +/-0.0001
MACHINE: 8-core Apple M1, 8 GB, node v20.10.0, python3 3.11.5.
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

BASELINE = "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1"
SINCE = "2026-08-27T21:02:51+00:00"
UNTIL = "2026-09-10T21:02:51+00:00"
ROOT = Path(__file__).resolve().parents[4]

# Transcribed from .claude/workflows/policy_lint.mjs POLICY_GLOBS. The harness
# refuses to run if the count of globs in that file has changed, so a widened
# corpus cannot be measured against a stale copy in silence.
POLICY_GLOBS = [
    r"^CLAUDE\.md$",
    r"^\.claude/rules/[a-z0-9-]+\.md$",
    r"^tools/audit/briefs/[A-Za-z0-9_.-]+\.md$",
    r"^tools/audit/README\.md$",
    r"^tools/audit/harnesses/README\.md$",
    r"^tests/README\.md$",
    r"^docs/HANDOVER\.md$",
    r"^\.claude/workflows/web-fragments\.md$",
    r"^\.claude/skills/[a-z0-9-]+/SKILL\.md$",
    r"^\.github/PULL_REQUEST_TEMPLATE\.md$",
]
POLICY_RE = [re.compile(g) for g in POLICY_GLOBS]

# The strict subset: files that are RULE TEXT binding a seat, as opposed to the
# records and READMEs the same glob list also covers. Reported separately so a
# reader can see the census is not carried by handover edits.
RULE_RE = [re.compile(g) for g in (
    r"^CLAUDE\.md$",
    r"^\.claude/rules/[a-z0-9-]+\.md$",
    r"^tools/audit/briefs/[A-Za-z0-9_.-]+\.md$",
    r"^\.claude/skills/[a-z0-9-]+/SKILL\.md$",
    r"^\.claude/workflows/web-fragments\.md$",
    r"^\.github/PULL_REQUEST_TEMPLATE\.md$",
)]

BODY = """Why this change, and what it measures.

## Head

{head}

## Mutation proof

n/a: prose only, no executable behaviour changes.

## Null control

n/a: no cost, gain or timing claim is made here.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
"""


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=True).stdout


def main():
    # Guard: the transcribed glob list must still have the same cardinality as
    # production's, or this harness is measuring a corpus that has moved.
    src = (ROOT / ".claude/workflows/policy_lint.mjs").read_text()
    block = src.split("const POLICY_GLOBS = [", 1)[1].split("\n]", 1)[0]
    live = len(re.findall(r"^\s*/\^", block, re.M))
    print(f"RESULT policy_globs_in_production={live} globs")
    print(f"RESULT policy_globs_transcribed={len(POLICY_GLOBS)} globs")
    if live != len(POLICY_GLOBS):
        print("REFUSED: POLICY_GLOBS moved; re-transcribe before trusting the census")
        return 2

    # --- the perturbation, both arms -------------------------------------
    head = "deadbeef" * 5
    exits = {}
    with tempfile.TemporaryDirectory() as td:
        bp = Path(td) / "body.md"
        bp.write_text(BODY.format(head=head))
        for arm, title in (("policy", "policy: rewrite a rule"),
                           ("docs", "docs: rewrite a rule")):
            p = subprocess.run(
                ["node", ".claude/workflows/policy_lint.mjs", "--pr-body", str(bp),
                 "--head", head, "--title", title],
                cwd=str(ROOT), capture_output=True, text=True)
            exits[arm] = p.returncode
            saw = "no `## Approval` section" in p.stdout
            print(f"  arm {arm:6s} title={title!r} exit={p.returncode} "
                  f"approval_error={'yes' if saw else 'no'}")
    print(f"RESULT arm_policy_title_exit={exits['policy']} exit_code")
    print(f"RESULT arm_docs_title_exit={exits['docs']} exit_code")

    # --- the census over merged history ----------------------------------
    log = git("log", "--first-parent", "--format=%H\x09%s", BASELINE,
              f"--since={SINCE}", f"--until={UNTIL}")
    touching, not_required, examples = 0, 0, []
    r_touching, r_not_required, r_examples = 0, 0, []
    for line in log.splitlines():
        sha, subject = line.split("\t", 1)
        files = git("show", "--first-parent", "--name-only", "--format=", sha).split()
        hit = sorted({f for f in files if any(r.match(f) for r in POLICY_RE)})
        rhit = sorted({f for f in files if any(r.match(f) for r in RULE_RE)})
        if not hit:
            continue
        touching += 1
        r_touching += 1 if rhit else 0
        # The title `checkPrBody` sees is the pull request's; a squash merge
        # writes it as the commit subject with a ` (#N)` suffix.
        title = re.sub(r"\s*\(#\d+\)$", "", subject)
        if not title.startswith("policy:"):
            not_required += 1
            if len(examples) < 8:
                examples.append((sha[:7], title[:64], hit[0]))
            if rhit:
                r_not_required += 1
                if len(r_examples) < 8:
                    r_examples.append((sha[:7], title[:64], rhit[0]))
    print(f"RESULT policy_touching_commits={touching} commits")
    print(f"RESULT approval_not_required={not_required} commits")
    frac = (not_required / touching) if touching else 0.0
    print(f"RESULT approval_not_required_fraction={frac:.4f} fraction")
    print("  examples (sha, title, one policy file it changed):")
    for e in examples:
        print(f"    {e[0]}  {e[1]!r}  {e[2]}")
    print(f"RESULT rule_text_commits={r_touching} commits")
    print(f"RESULT rule_text_approval_not_required={r_not_required} commits")
    rfrac = (r_not_required / r_touching) if r_touching else 0.0
    print(f"RESULT rule_text_approval_not_required_fraction={rfrac:.4f} fraction")
    print("  examples over the rule-text subset:")
    for e in r_examples:
        print(f"    {e[0]}  {e[1]!r}  {e[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
