# Class sweep: N-move-stale-path (round 11, PLAN phase D)

Mechanism: a file move leaves a consumer importing, running or citing the old
path. Ledger status in `dev/audit/config/bugclasses.json`: `barriered` (tests/entities.py
check #2227, scoped to live-cited executables under a historical prefix).

## Enumerator

`python3 dev/audit/rounds/round11/D14/move_stale_path_enum.py` over `tools tests
dev/governance .claude CLAUDE.md dev/audit/harnesses dev/audit/README.md`.
Arm 1: `tools/audit/seat/moved_paths.py` STALE? hits (moves recorded in
tests/layout.json) whose old path is absent. Arm 2: any cited repo path
(`tools|tests|dev|docs|.claude/...ext`) absent from the tree, for moves
layout.json does not record. Each hit is classified by rule plus a hand-review
override table in the script. Raw output: `D14/move_stale_path_enum.out.json`.

Result: 693 seams -- 17 instance lines (5 seams), 99 guarded, 577 not applicable.

## Controls

- Null: a clean git fixture with layout.json and no stale path -> 0. PASS.
- Perturbation: one line `q = ROOT / ".claude/workflows/policy_lint.mjs"` added -> 1 instance. PASS.
- Positive: the enumerator lists the site of 15 of the 20 findings
  (D5-s10-04/05, D5-s5-02/03, D5-s6-03, D5-s8-01/02/03, D5-s9-01/02/03,
  D6-s2-02/03, D6-s5-03, D6-s5-06). It does not re-find five, all prose
  claims with no extension-bearing path token: D5-s10-01 (pre-edit.sh's
  generator direction), D6-s5-01 (relative `briefs/fix-review.md`), D6-s5-02
  (extensionless directory `tools/audit/round4/D6/`), D6-s5-04 ("under
  docs/"), D6-s5-08 (bare filename `event_hub_writes.py`). Those are
  judged sites already; the gap is recorded, not papered over.

## Dispositions

Instance (probe fails on each; all are finding sites, none beyond):
- tools/policy/policy_lint.mjs:41-52 usage lines (D5-s8-01): `test -e .claude/workflows/policy_lint.mjs` exits 1.
- tools/policy/friction_issues.mjs:53-55 usage lines (D5-s8-02): `test -e .claude/workflows/friction_issues.mjs` exits 1.
- dev/governance/roles/fixer.md:104 (D6-s2-02), orchestrator.md:73 (D6-s2-03): `test -e docs/decisions/...` exits 1.
- tools/audit/seat/row_position.py:4 usage (D5-s6-03): the command exits 2.

Guarded (99): `locate()`/`at()`/`load()` from tools/policy/counts.mjs map old
to new; `test -f`/`[ -f ]`/`is_file()` old-path-first fallbacks (prepr.sh,
stop-selfcheck.sh, app_comment.sh, merge_train.py:2548, agreement_py.py:472,
governance.yml's app_comment step pinned by entities.py:29781-29782);
retired-name/refusal lists (`BRIEF_LINT_OLD`, layout.json); rule `paths:`
globs naming a moved path beside its new home (defect-root-cause.md:4,
ratchet-budgets.md:8, both copies); web-decomp-stage.js:148 copies from a tag.

Not applicable (577): prose comments and history (decisions, `git show
<sha>:path`), self-test fixture strings (ci_predict.py, app_push.sh,
pr_args.sh, fold_ledger.py, merge_train.py:8026), mutation-ledger reasons,
and `.claude/rules/` references (the directory still exists as generated output).

## Beyond the findings

Zero. Every instance seam is a judged finding site; the remaining hits are
fallback-guarded or non-executable.

## Barrier

The existing #2227 barrier does not reach live-path usage lines or policy
citations. Proposed narrow barrier: the arm-2 check restricted to usage
docstrings/headers (`node|python3|bash <path>`) and `dev/governance/**`
citations, as a tests/ arm (one tree walk, est. under 1 s). Instrument
change, so it goes to round-end proposal triage, not a mid-round build.
