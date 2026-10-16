D13-s3-01 (#2227, class N-move-stale-path): file moves had left programs that live text tells a seat to run unable to run.
- `dev/audit/rounds/round4/D11/dora_keys.py`, D13's standing instrument, imported a `d11lib` the move left under `tools/`, and opened `cfr_exclusions.json` at its pre-move home.
- `dev/audit/rounds/round5/D11/seat-b/corpus_churn.py`, which `carry-201.json` tells a seat to run, opened two moved files.
- `carry-201.json` spelled several commands at moved paths.

This pull request ships the countermeasure `dev/audit/rca/R10-N-move-stale-path.md` prices (form (ii), a narrow arm) and fixes every instance it finds.

What changes:
- `dora_keys.py` and `corpus_churn.py` resolve what moved through `tests/layout.py`'s `canon`/`locate`, the move map's own resolvers.
- `carry-201.json`: every `remeasure` path spelled at a moved location now names where the file lives. The other retired paths on those lines are re-pointed too, because `tests/layout.py --guard` reads a touched line as a new citation of each.
- `tests/entities.py`, the cited-program arm:
  - Sources: every executable a policy file cites (`policy_lint.mjs`'s `policyFiles()`, now exported), and every executable path in a carry's `remeasure`. Both are read from the git index, the way `tests/layout.py` reads INERT prose.
  - Probe: each source that lands under a `layout.json` `historical` prefix is loaded the way a seat runs it, and every repository path it opens must resolve. "Opens" means a literal given to `open`/`Path`/`join`/a subprocess or existence call, directly or through a name.
  - Spelling: any `remeasure` path spelled where the move map says no file lives is refused.
- `tests/closure.py`: `corpus_churn.py` joins `INERT_EXCEPT`, beside `dora_cfr.py`.
- `tests/closures.json`: `tests/entities.py` was re-recorded with `--single`. The three reads CI's Linux recording named were added by hand, and `corpus_churn.py` left both `inert_reads` lists.

Rejected alternatives:
- Moving `dora_keys.py` to the retired `tools/audit/round4/`.
- Hand-patching code paths. It breaks on the next move.
- Keying the probe on every literal. It over-fires on `codeowners_gap.py`'s classifier inputs.
- The whole-tree form (i). The RCA's cost test refuses it.

Part of #201.

Closes #2227.

## Head

`2e819456954548351ba8fd2d0c375fa3355d9543` merges the authored code head `69fc404530ad81e477de0562c8906619d147780e` and then merges origin/main `c42d7cea6` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`60c4b9b13e5a02bf54199b707c961e29bfe321a6`. Its merge base with `origin/main` is `d4c94f9a4`. Every figure below was re-taken in this pass, at this head, against a detached worktree at that base.

## Mutation proof

The arm block of `tests/entities.py` (between `# --- N-move-stale-path (#2227)` and `# --- D11-04 (#1194)`) was driven alone at this head. Each mutation was restored with `git checkout`.
- M1, `corpus_churn.py`'s budgets read made a bare literal: FAIL `every program live policy or a carry's remeasure tells a seat to run, under a historical prefix, loads and resolves the paths it opens (#2227)`.
- M4, `dora_keys.py`'s library import reverted to the sibling path: the same check FAILS.
- M5, `CFR_EXCLUSIONS` made a bare literal: the same check FAILS.
- M2, the probe keyed on every held literal: both arm checks FAIL.
- M9, carry-201's "run the D13 instrument (`tools/audit/round5/D13/seat-a/dora_cfr.py`)" restored and staged: the first check FAILS.

## Null control

At this head:
- `dev/audit/rounds/round4/D12/units.py` (cited by `COMMON.md`) loads and resolves.
- `codeowners_gap.py` holds more than 0 stale literals and opens none.

Both are asserted by the arm's second check, which also asserts:
- a planted `open(<retired>)` is refused;
- `open(locate(<retired>))` is accepted;
- a planted "run the D12 instrument (`<pre-move path>`)" is refused;
- the current spelling is accepted.

That check prints `ok`.

## Figures

- The arm at this head cites 5 programs, each `runs`:
  - `dora_keys.py` (`D13.md`, carry-201);
  - `units.py` (`COMMON.md`);
  - `corpus_churn.py`, `dora_cfr.py` and `codeowners_gap.py` (carry-201).

  Both checks print `ok`.
- `python3 dev/audit/rounds/round5/D11/seat-b/corpus_churn.py`: rc 1 at the base, rc 0 at the head.
- The finder's `dev/audit/rounds/round10/D13/s3/d13_s3.py` `dora_instrument_check()`, driven alone with `PYTHONPATH=tests/hastub`: `RESULT dora_keys_loads=0` at the base, `1` at the head.
- `python3 -I dev/audit/rounds/round10/D14/sweep-N-move-stale-path/enumerate.py .` reads `seams=2877 broken=368` at the base and `seams=2883 broken=367` at the head. The `diff` of the sorted outputs:
  - `dora_keys.py` 89 and 103: gone.
  - `dora_keys.py` 118 and `corpus_churn.py` 74/106/139: the same literals as `locate()`'s argument, which the enumerator does not read.
  - `tests/closure.py` 3844/3845 and six `tests/entities.py` lines: shifted only.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at both ends.
- CI at this head: 45 check-runs (`filter=all`), 0 pending, 0 not green. This includes `fast (3.14)` 116689033932, `closures` 116696579703 and `Analyze (python)` 116688917445.

## Red checks

- `closures` and `closures-autofix` went red on the branch's first pull-request head, `fc75984b2`.
  - Cause: `UNDER-SCOPED`. The Darwin `--single` recorder does not follow the probe's child process. `skip-classifier-disagrees` followed, because `corpus_churn.py` left INERT.
  - Answer: the three reads were added by hand.
  - Cheaper detector: none exists today. Checking every `inert_reads` list when a file joins `INERT_EXCEPT` would cost one `json` read. Whether to build it is the root-cause seat's question.
- `pr-contract` then refused the body for not naming them. It now does.
- `Analyze (python)` was cancelled once at `5014df139`. That is not from this diff: the re-run passed.

## Forward-carry

#2312, roster group R10-STALE-PATHS-2 in `dev/programme/rosters/wave-r10-groups.json`:
- F1: open shapes the arm does not follow.
- F2: citations are re-checked only on main's full run.
- F4.

`dev/programme/rosters/wave-r10-groups.json`, R10-BRIEFS-FOLD: the 35 evidence-only seams under D2.

## Friction

none

