R10-CLOSEOUT-CLEANUP, instrument half (Part of #201; issues #2505, #2727, #2728). Lands the closeout instrument and folds in the two fly-ins: `prune_refs.py` (batched push arm, keep guards, `--topic`) and `worktree_gc.sh` (unpushed keep, `on-remote` class). The `--apply` run is the orchestrator's final act and was not run here; merging this sets the group carries-open, not done.

Carry dispositions, every carry of the group's roster entry (dev/programme/rosters/wave-r10-groups.json on handoff/audit-r10-roster), (numbered from 1, in roster order):
- Carry 1 (delete the probe refs for #2654 #2656 #2657): residue-no-pr in `prune_refs.py`'s plan, deleted by the final run; no new rule.
- Carry 2 (the `--apply` run is a separate, last step, the orchestrator's, with step 4 refusing until every open issue but the successor is dispositioned; roster-gated): `closeout.py` refuses while any other group is open, naming each; arms and mutants `closeout-1` and `closeout-2`.
- Carry 3 (folded R10-FLY-PRUNE-REFS, issue 2727): the batched push arm (0 gh calls, tags before deletes, null control 2N), the `claude/*`, open-group `design/` and age keeps; its inner carries (dispatch/`brief/` residue, stranded handoff refs) fall to the same plan as archive-delete residue.
- Carry 4 (folded R10-FLY-WORKTREE-GC, issue 2505): the `unpushed` keep on both the classify and apply paths, and the `on-remote` class with its cwd, fetch and lsof controls.
- Carry 5 (s9 script census, `prune_refs.py --topic <t>`): archive-then-delete, refused on a `+` cherry line or an open PR; mutants `prune_refs-5` and `prune_refs-6`.
- Carry 6 (plan-regain study, build the tooling now, run last): the instrument lands here; the `--apply` run is not made.
- Carry 7 (s9 local cleanup: worktree_gc "eligible 0, kept 131" at 7.8 GiB free): NOT built here, routed in `## Forward-carry`.

Design notes: `--topic`'s `git cherry` refusal covers `handoff/` code refs only, since body and dispatch refs are orphan commits that always carry a `+`; local branches holding commits no remote or tag has are never deleted.

## Head

`7f95f9084b42aa5bd651a9aa98cc5b4292adcaaa` merges the authored code head `e80cdedb0b5c1025dee4e84ffa38429740ffa8b1` and then merges origin/main `ea59e9a09` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

Handoff head e80cdedb0b5c1025dee4e84ffa38429740ffa8b1, which is code head fc47684e3577d7fdd34db78c48d9d173f8806c35 (the r3 repair for CodeQL alert 49 and self-test 69) with origin/main a568a2e128f8df25eb6a960838737c0bda277fac (merge of #3065) merged in; no other change. Measured at HEAD_SHA, origin/main unmoved since `tools/pr/prepr.sh` was run (2026-11-02).

## Mutation proof

Eleven mutants, each planted in a production predicate, run by `dev/audit/harnesses/r10_seat_selftests_mutants.py closeout-1 closeout-2 prune_refs-1 prune_refs-2 prune_refs-3 prune_refs-4 prune_refs-5 prune_refs-6 worktree_gc-1 worktree_gc-2 worktree_gc-3`: all KILLED, `RESULT survivors=0`. They drop the roster refusal, the step gate, the `claude/*` keep, the open-group `design/` keep, the age guard, the missing-tag refusal, the cherry `+` refusal, the dispatch topic match, the unpushed keep, the cwd test and the fetch gate.

## Null control

Every arm has one in its self-test: `--apply` with every other group done proceeds past the roster; the old gh-api arm on a 4-ref plan makes 8 writes (2N) against 0 for the push arm; a `claude/*` tip is kept while the same tip on a `fix/` ref is deleted; a done group's `design/` ref is still deleted; a topic fully on main is archived then deleted; main and the open-PR head survive; a clean seat worktree at a pushed head is removed beside the kept unpushed one; a clean detached worktree at a head no remote holds stays `unmerged-head`, and one at the origin/main tip stays kept.

## Figures

- `python3 -I tools/audit/seat/prune_refs.py --self-test` -> SELF-TEST PASS (69 checks).
- `python3 -I tools/audit/seat/closeout.py --self-test` -> 23 checks, 0 failed.
- `bash tools/audit/worktree_gc.sh --self-test` -> 91 checks, 0 failed.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> 0 index gaps.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py closeout-1 closeout-2 prune_refs-1 prune_refs-2 prune_refs-3 prune_refs-4 prune_refs-5 prune_refs-6 worktree_gc-1 worktree_gc-2 worktree_gc-3` -> RESULT survivors=0.

## Red checks

The whole check-run set of the PR head 1be96319 (55 check runs, one `get_check_runs` read, all pages), concluded red:
- `governance / instrument-self-tests` failure: self-test 69, the `prune_refs.py` gh stub test. Repaired in fc47684e (below). Cheaper detector: `prune_refs.py --self-test`, run locally and on every prepr.sh path that names the file.
- `CodeQL` failure and open `code-scanning alert 49 (py/overly-permissive-file)`: the self-test wrote its `gh` stub by `open()` then `os.chmod(…, 0o700)`, which the query flags as a permissive file. Answer: fc47684e creates the stub exclusively with mode 0o700 via `os.open(..., O_EXCL, mode)` (`_write_stub`), no chmod, and the self-test asserts the group/other bits are clear (`_wide_bits`), with a null control that reads 0o755 as wide. Cheaper detector: none that runs offline; CodeQL's `py/overly-permissive-file` is the only one, and a local `--self-test` assertion now covers the bits.
- `pr-contract / pr-contract` failure (twice) and `gate` failure (twice): pr-contract refused the stale body that named the old code head; `gate` failed on those required checks and on the self-test above. Both follow from this retake.

## Forward-carry

- From the s9 local cleanup (2026-11-01; ~/hpo-orch/cleanup-20261101.log). The disk was at 7.8 GiB free, under the sweep's 15 GiB floor, so the sweep ran tools/audit/worktree_gc.sh, which reported "eligible 0, kept 131" (roster carry 7). Not built in this group's PR: it needs (1) a seat-branch to PR-topic mapping (`work/*`, `scratch/*`, `seat/*` onto `fix/<topic>`) read from the live PR list, (2) a configurable seats root (`~/hpo-seats/<round>`), and (3) a new class for plain repo copies with no `.git`; that is three new classes in `worktree_gc.sh` on top of a PR already past the size contract, and the topic mapping needs gh data the offline self-test cannot plant without a new stub. Failing test first, when built: a fixture seat on a merged topic, eligible after the fix and kept today; null control: a seat with one unpushed commit, or a live process cwd in it, stays kept. Carry: #2505

## Friction

none
