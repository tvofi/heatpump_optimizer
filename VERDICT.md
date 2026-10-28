Fix review: merge 7b071dbd73701ed8550ca9d31f0b0bdacc0a9f9a
bus-nonce: a15bc909ce63e81c8e0e6e53534e7a71

# Fix review -- PR #2883, R10-FLOW-BOARD, round 4

This is the fourth review round, dispatched `--past-three`. The round-3 review accepted the code and
blocked only on two CI findings: F1 `tests / closures` red, and F2 `tests / nightly-status` red with
no answer. This round I judge those two repairs. I also confirm that the code the round-3 review
accepted is unchanged.

Reviewed head: `7b071dbd73701ed8550ca9d31f0b0bdacc0a9f9a`. GitHub's `headRefOid` named it at
dispatch, again after CI concluded, and again before I posted. I worked in a detached worktree at
that head (`ev/head.txt`), with detached worktrees at `3bd284f74` and `71987ff1e` for the controls.

- Merge base: `9c9cd0d2d`, which is origin/main's tip.
- `git merge-tree --write-tree origin/main <head>` exits 0.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Code unchanged (the round-3 findings carry)

- RESULT `tools/audit/merge_throughput.py`: blob `bfafe4ae5` at the head and at `70928ca4e`.
- RESULT `tools/audit/seat/roster_lib.py`: blob `4b3f4ef3e` at the head and at `70928ca4e`.
- RESULT the three-dot file set is the same 8 files at `71987ff1e` and at this head. Every file other
  than `tests/closure.py` and `tests/closures.json` has the same blob at both heads.
- The delta since round 3 is `28b0fa0f3`: +11 lines in `tests/closure.py` (two `INERT_EXCEPT`
  entries and their comment) and +2 in `tests/closures.json`. The rest is main merges.

So round 3's harness results carry unchanged: 7 of 7 mutants killed, both self-tests green and the
class open closed.

## F1: `tests / closures`

**The cause, re-derived.** I re-ran the fixer's probe myself (`ev/probe_rec_rev.py`, my wrapper with
a wider print, `ev/probe_rec.txt`). It records `roster_lib.py --self-test` alone under
`closure._exec_record`.

- RESULT `3bd284f74`: no `dev/programme/rosters/` path in `files`, `inert_reads`, `spawned` or
  `argv`. Wall time 3.3 s.
- RESULT `71987ff1e`: `inert_reads` = `[critical-path.json, wave-r9-groups.json]`. These are exactly
  the two files CI named. Wall time 4.2 s.
- RESULT this head: the same two files are in `files`, and `inert_reads` is empty. They now count as
  ordinary reads.

How the read arises:
- The self-test calls `show_roster(..., "HEAD", f"{ROSTERS_DIR}/wave-r9-groups.json")` and
  `critical_path_read`. Both go through `blob_at`, which runs `git ls-tree -z --full-tree <ref> --
  <path>` (`roster_lib.py:177`).
- `closure.py:1242-1246` counts any argv token naming an existing repo path as a read.

So the "read" is the instrument's argv over-approximation. The self-test lists the trees of a temp
repo, not the working-tree file. Over-scoping in this direction is safe, and the rule documents it.

**Before and after.** I ran `python3 tests/closure.py check --in-dir <fixer's rec> --partial` on each
table (`ev/check_partial.txt`):

- RESULT on `71987ff1e`'s table: `INERT READS UNDER-APPROXIMATED` naming the same two files, rc 1.
- RESULT on this head's table: `committed closures cover every file this run touched`, rc 0.

The recording is the fixer's (`fix-2883-s8c/rec/entities.py.json`, 904.6 s). I did not re-derive it.
CI's full-scope closures run below is the independent measurement.

**The route.** INERT_EXCEPT is the sanctioned route, not `inert_reads`:

- The `--single` merge's own refusal reads: "files on the INERT list are actually read by tests ...
  remove them from INERT in tests/closure.py, or except them" (`fix-2883-s8c/ev/single.txt`).
- `wave-r10-groups.json` and `tools/audit/merge_throughput.py` (this PR's round 1) took the same
  route.

I re-ran the fixer's selection probes (`probe_sel.py`, `probe_sel2.py`) at `71987ff1e` and at this
head:

- RESULT: adding the pair to `inert_reads` instead selects `tests/entities.py` for
  `dev/programme/delivery/9999.md` and for `wave-r10-groups.json`. Its match is by directory
  (`inert_reads (dir: dev/programme)`).
- RESULT at this head: `select()` picks `tests/entities.py` for `critical-path.json` and
  `wave-r9-groups.json` only. `delivery/9999.md`, `wave-r10-groups.json` and `wave-r1-groups.json`
  stay unselected.

So the body's selection-cost claim holds.

**The merged table.** `closures.json` at this head still holds both entries in `tests/entities.py`'s
closure after the main merge (three-dot diff), and `merge_throughput.py` from round 1.

**Step 14.** Remove the mechanism and the movement goes: at `3bd284f74`, before the `blob_at`
self-test arms, the probe files no roster path. The closure entries are earned by the change.

**CI.** RESULT `tests / closures` check-run 122633776323 concluded success at 05:07:29Z.
`closures-autofix` was skipped because there was nothing to repair.

## F2: `tests / nightly-status`

RESULT check-run 122633659574 is red at this head (`ev/nightly-status.log`): `NIGHTLY FAILED:
record-autofix failed in the last verification dispatch`, dispatched run 40595637258, head `802ba77`.

The body's account checks out:

- Run 40595637258 is a `workflow_dispatch` of `nightly.yml` on `main` at `802ba7756`.
- Its job 122510724454 raised `urllib.error.HTTPError: HTTP Error 403: Forbidden` from
  `record_row.enumerate_merges` (`ev/record-autofix-122510724454.log`, lines 4382-4406), and then
  failed "the record step did not run".
- The next run, 40620896832 at `b9e286254`, has `record-autofix` success.

What this diff touches:

- Its only file that `nightly-status` reads is `.github/workflows/governance.yml`. The change there
  is four comment lines.
- It touches no `nightly.yml`, no `record_row.py` and no nightly status script.

The body names the red, the cause (a GitHub API 403 on main's record lane), the owner (the
orchestrator) and the cheaper detector ("none: a live API read in a scheduled lane").

## Red checks at this head

All workflows had concluded by 05:14:27Z (`ev/check-runs-7b071dbd7....txt`): 37 success, 17
skipped, 1 failure. The one failure is `tests / nightly-status`, answered above.

- RESULT `pr-contract / pr-contract` succeeded twice: 122643444275 at 05:07:32Z and 122645218824 at
  05:13:21Z. Both started after the only red concluded (04:34:23Z). They checked the body and found
  every red answered.
- RESULT `gate` succeeded twice: 122643663115 and 122645455735.
- RESULT `tests / mutation` success. `mutation-autofix` and `mutation-pins` were skipped.

`## Red checks` covers every red on the range:
- at `71987ff1e`: closures, closures-autofix, nightly-status, pr-contract, gate;
- at `3bd284f7`: none;
- at `8f05b74d`: closures.

The `tests / closures` trigger is answered with a cheaper detector: recording the changed self-test
alone, 3.9 s against a 913 s `--single` derive. The process state (c) is named, and the RCA is
raised as owed to a separate root-cause seat. This is the second instance of this argv-read shape in
this PR. I check that the trigger was answered, not the answer.

## Other checks

- RESULT the three-dot diff touches no claim file, no `VERSION`, no manifest and no
  `RELEASE_NOTES.md`.
- The body's `## Head` names `7b071dbd7` and the code head `28b0fa0f3`.

## Findings

- F1 (round 3, blocking): repaired and verified at this head. Carry: dismissed: verified repaired
- F2 (round 3, blocking): answered in `## Red checks` and verified against the run's own log; the
  red is main's record lane. Carry: dismissed: verified answered
- F4 (non-blocking, instrument): `closure._exec_record`'s argv rule (`closure.py:1242-1246`) counts
  a path argument as a read even when the subprocess runs against a temp repo, as `blob_at`'s
  self-test does. The result is a safe over-approximation. However, `ci_predict.py` cannot see it
  ("a data-file read is not seen"), and it has now turned this PR's closures red twice. The body
  raises the RCA as owed to the root-cause seat; I add nothing to it. Carry: dismissed: owed to the
  root-cause seat the body names

Evidence: `ev/` (head.txt, check-runs, probe_rec, check_partial, nightly-status and record-autofix
logs). The probe wrapper is mine. `probe_sel.py` and `probe_sel2.py` are the fixer's, re-run by me.
