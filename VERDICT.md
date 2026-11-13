Fix review: merge f8d8a642a31a250b8ae297366c26f7858d51ef05

bus-nonce: e6b9209aea84bdbd2469c60779241814
pending-ci: gate

## Scope

Round 2. The previous round reviewed 3d1e538d90c240a2cc5009eea0582d3fcc95ca44 and blocked on the architecture score (coord_footprint 2506->2507). The rendered packet's `## Review scope` reads `full` because no verdict on verdict/3536 names that head, so I re-took the whole PR's claims; the delta 3d1e538d..f8d8a642 is one production edit (d710600251, merged into the head by f8d8a642, tree 3e9ef7e6 on both). It binds `ctx = getattr(self, "_ctx", self)` once in `coordinator._audit_comfort_band` and passes `ctx._config` and `ctx._thermal_params`. The behaviour is identical: one `getattr` instead of two, with the same arguments to the same calls. It puts no already-reviewed code at risk, so the scope is not widened.

## Block answered

- `python3 tools/audit/archscore/score.py --diff e4ca2d940efd1e87912d80cb3ebddf8240ba0729` at the head: `Architecture score: dS +0.0000 NULL` (ev/archscore-head.txt).
- Mechanism removed (the same command against HEAD~1 = 3d1e538d): `dS -0.0006 WORSENS (inadmissible: coord_footprint 2506->2507)` (ev/archscore-prevhead.txt). Both of the body's figures reproduce.
- Step 14, metric-gamed: the move is a respelling, and the scorer rewards it (code-equivalent HEAD and HEAD~1 differ by one coord_footprint statement). I judge the change sound and not gamed, for three reasons. The alias `ctx = getattr(self, "_ctx", self)` is the class's established form, bound the same way in about 15 other coordinator methods (for example `coordinator.py:3771`, `:4250`, `:5076`). The added coordinator statement is a pure forwarding call to `mixing_valve.audit_target`, which the metric's own intent counts as delegation. The rewrite also removes a duplicated `getattr`. The scorer's sensitivity to spelling is recorded below as an instrument finding.
- `tests/structure.py` at the head: STRUCTURE RATCHET PASSED; max_class_loc stays at its budget with zero headroom.

## Evidence

- Mutation proof, re-run with `PYTHONPATH=tests/hastub python3 tests/features.py`, one copy per mutant at the head:
  - Baseline: ALL 5365 FEATURE CHECKS PASSED, rc=0 (ev/features-head.txt).
  - A, `mixing_valve.audit_target(...)` call deleted from `_audit_comfort_band`: 1 of 5365 FAILED, "valve target: a configured target above the comfort ceiling raises one repair ...", rc=1 (ev/features-mut-A.txt). This matches the body's claim exactly.
  - B, CMP_BOUND `target >= comfort_ceiling`: 1 of 5365 FAILED, "valve target null control ..." [a plausible target raised a notice], rc=1 (ev/features-mut-B.txt). This confirms the body's prediction that the at-ceiling null control kills it, and agrees with the pinned ledger entry.
  - C, RETURN_DEL `pass`: 1 of 5365 FAILED, the repair check, rc=1 (ev/features-mut-C.txt). This agrees with the pinned ledger entry.
- Null control: "valve target null control" passes at the head, and the trap check ("a flow temperature typed as the target (30) moves the planned hot-water energy against 0; ... the same target replans identically") passes. Both are in ev/features-head.txt, lines 6839-6841.
- Claim files, golden fixtures, VERSION, manifest and RELEASE_NOTES are untouched in `git diff e4ca2d94...f8d8a642` (12 files: README, coordinator, mixing_valve, strings plus 3 translations, docs/configuration.md, delivery row, tests/features.py, 2 ledger pins).
- Merge: `git merge-tree --write-tree origin/main f8d8a642` exits 0 against origin/main 3b9749dac5 (ev/merge-tree.txt). The head merges cleanly.
- The PR head is still f8d8a642a31a250b8ae297366c26f7858d51ef05 at verdict time (`git ls-remote origin refs/pull/3536/head`). The body's `## Head` names it.
- Authorship: `git log --format='%an %ae' e4ca2d94..f8d8a642` shows only numbered users.noreply.github.com addresses (Bankaifan 476059+, tvofi/hpo-fixer 70032254+, github-actions[bot] 41898282+) (ev/branch-log.txt).
- Red checks: the arch-score red on 3d1e538d and the `tests / mutation` red are both answered in the body's `## Red checks` (cheaper detector `score.py --diff`, state (b); `prepr.sh` step 7d predictor). Both are in the `merge_train.py owed-reds` set. I checked that the trigger was answered, not the answer.
- CI: `merge_train.py classify f8d8a642... --pr 3536` read `WAIT ... pending: gate red: none` from 10:10 to 10:47 UTC (ev/classify-*.txt). I did not wait for green; see the `pending-ci:` line.
- `tests/entities.py` at the head (env -u BASH_ENV, PYTHONPATH=tests/hastub): ALL 2709 ENTITY CHECKS PASSED, rc=0 (ev/entities-head.txt).
- Finder's harness: none is named (an outside report on PR 3529, verified by reading). The committed features checks are the fixer's. The contributor's energy figure is not claimed, so there is no figure to re-derive.

## Findings

- Follow-up: the body's `## Null control` authorship control is stale. It says `git rev-parse HEAD^{tree}` equals the tree of 918f38cc, but at this head 918f38cc's tree is da2b9911 and HEAD's is 3e9ef7e6 (ev/tree-compare.txt). It held at the earlier head 3d3716aa. The authorship it was meant to show is re-verified above by `git log`, so this blocks nothing. Carry: dismissed: a stale figure in a body whose purpose is re-verified at this head by the git log control
- Follow-up: the body's `## Red checks` is spliced. The arch-score answer sits inside the `tests / mutation` bullet's backtick span, which also holds a stray `## Unpinned sites` heading, so a reader or parser keyed on bullets sees one bullet holding two answers. Both answers are present. Carry: dismissed: formatting of this PR's own body; pr-contract judges its parse at the head
- Follow-up: `tools/audit/archscore` footprint reads `f(..., getattr(self, "_ctx", self).x)` as one coordinator statement but `ctx = getattr(...); f(..., ctx.x)` as delegation. Measured: HEAD~1 and HEAD are code-equivalent and coord_footprint is 2507 against 2506. Respelling therefore moves the metric with nothing improved. Here the move corrects an over-count of a pure forwarding call into the class's established form, so it is not gaming in this diff. Carry: dismissed: an instrument reading the class's documented alias form; the movement here is an over-count corrected, not logic hidden
