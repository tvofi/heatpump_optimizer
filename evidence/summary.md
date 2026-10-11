# Evidence -- fix review of PR #2129, head 64f168d2cea942cdba6a79050116988b4b90c4c9
Reviewer worktree: /Users/timmalmstrom/hpo-seats/r9rev-2129/wt (detached at the head)
Merge base: 6be88834e8c4658b3e4832cd24c00aa97b3da2d3
Date: 2026-10-10

## (e) recording-set identity -- REPRODUCED
rec-target multiset (script + args), merge-base vs head, sorted: identical, 34 lines
each (reclines_base.txt / reclines_head.txt, dc_base.sh / dc_head.sh are the two
script texts). Full invocation lines (incl. `HASTUB_TZ=... rec tests/dst_checks.py`
and the parenthesised lane-1 line): identical multiset, 34 total. No lock, queue or
serialisation added (grep of the diff: only comment text). tests/closures.json not
in the diff. Lane arithmetic from tests/closures.json `recorded[*].seconds`:
boost 1489.6; lane1 stress 760.6; lane2 990.1; old lane3 (31 members) 2728.8;
new lane4 (30 members, old lane3 minus boost, order preserved) 1239.2 -- all four
body figures re-derived exactly.

## (a2) boundary measurements -- REPRODUCED (base worktree /Users/timmalmstrom/hpo-seats/r9rev-2129/base)
| file | base | head |
|---|---|---|
| dev/audit/rounds/round9/prestudy/nonesuch_probe.py (#2109 shape) | SKIP | SCOPED harness_headers |
| LICENSE | SKIP | SCOPED entities+harness_headers |
| docs/README.md, docs/new_page.md | SKIP | SCOPED doc_claims (8.6 s) |
| dev/governance/roles/fixer.md | SKIP | SKIP |
| handoff/r9-x/note.md | SKIP | SKIP |
| SECURITY.md, NOTICE | SKIP | SKIP |
| dev/programme/plan-x.md | SKIP | SCOPED harness_headers (stated cost) |
| custom_components/heatpump_optimizer/const.py | SCOPED 30 | SCOPED 30 (identical; no over-trigger) |
No probe answered FULL at head that answered scoped/skip at base: the rule only
moves skip->scoped, never toward skip or full.

## (a2) mutants (contract step 1) -- KILLED
A: consultation loop deleted from affected() -> #2109 probe SKIP, LICENSE SKIP
   (test not vacuous); restored -> SCOPED 2. Reproduces the fixer's proof output.
B: bound narrowed to own-dir only (dirs[-2] removed) -> round20 new-tree probe
   SKIP (pin _A_IR_NEWDIR catches); #2109 probe still SCOPED via own dir.
C: unbounded ancestors -> dev/governance probe SCOPED for entities+harness_headers
   (the over-trigger the pre-study refused; pin _A_IR_BOUND catches it).
Worktree restored clean after each.

## (a1) arms via the landed harness (HPO_A1_PYTHON=seat venv) -- REPRODUCED
inert-only=skip, closure-touching=scoped, diff-underivable=full; BASE arm:
closure-scope runs on workflow_dispatch: False -> FULL arm for every dispatch.
Independent fail-closed check: `affected --files-from <empty>` -> "CASE: FULL --
no changed files could be determined". Reviewed the decide-step shell: every
failure path (fetch fail, rev-parse fail, merge-base fail, diff fail) writes an
EMPTY changed.txt; no path writes a non-empty-but-wrong list.

## entities.py pins -- REPRODUCED
PYTHONPATH=tests/hastub <seat python> tests/entities.py at head: ALL 2260 PASSED
(2:14 min). The docs-only skip probe was re-cut to gate-scoping.md/SECURITY.md/
NOTICE (genuinely unreachable); the old probe files (register md, LICENSE) now
correctly scope.

## Untouched, verified by empty three-dot diff
VERSION, manifest.json, RELEASE_NOTES.md, tests/golden/claimed_drift.txt,
tests/golden/card_claimed_drift.txt, tests/closures.json.

## RED CHECKS AT THE MEASURED HEAD (the block)
check-runs API at 64f168d2c...:
  instrument-self-tests  failure  run 38086785285 / job 114314855120 (21:13:28Z)
    tests/throwaway_git.py --check: REFUSE tools/audit/seat/a1_dispatch_arms.sh:80
    `git init -q -b main . && git add -A`; REFUSE :82 `cd "$WORK" && git clone -q
    remote-tree repo && cd repo` -> exit 1.
  pr-contract            failure  run 38086785265 / job 114315311587 (21:15:53Z)
    "record red-history 2 commit(s) ... every failure conclusion across them:
    instrument-self-tests" -> "check `instrument-self-tests` is red and
    `## Red checks` does not name it."
PR body (## Red checks: "none at the head") does not name or answer it; PR
updated_at 21:13:22Z predates both failures. The failing sites are in this PR's
own new harness, lines 78-82: raw git init/git clone building the fixture repo
instead of the shared throwaway_git helper (tests/throwaway_git.py).
