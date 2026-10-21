Fix review: merge 90bab078d19dd6aebba140fa360576b7780a560a

bus-nonce: 43ea241b40ae10814cc74e8b5440c87c

Round 1 cloud review of PR #2547 (R10-TICK-OWED-LEVEL). I measured head 90bab078d19dd6aebba140fa360576b7780a560a and it was still the branch head right before I returned this (ev/HEAD.txt). I worked from detached worktrees at the head, at the code's measured base df6ca4bc6 and at the current merge base 6961f0663. `git diff <mb>...origin/main -- dev/governance/roles/` was empty, so my contract copy is current.

Harness: the brief names no finder harness, and the finding (orchestrator, 2026-10-21) never committed one. That is itself a finding under step 9, and the fixer disclosed it. The only committed harness is the fixer's `dev/audit/harnesses/r10_tick_owed_level.py`. I re-ran it, and I also built an instrument of my own, disclosed here as the reviewer's (ev/probe_deleted_ref.sh): a ref deleted from origin must leave the level after one pass.

RESULT lines (ev/harness.txt, ev/mine-deleted-ref.txt):
- baseline df6ca4bc6: `passes=3 refs=5 disposed=1 log_lines=24 printed=22 distinct=7 match=no`. Merge base 6961f0663 gives the same.
- head 90bab078d: `passes=3 refs=5 disposed=1 log_lines=5 printed=7 distinct=7 match=yes`
- null control `--passes 1 --no-dispose`: the baseline prints `printed=8 distinct=8 match=yes` and the head prints the same. It is flat at both ends, as claimed.
- other configuration `--passes 10 --refs 20`: the baseline prints `printed=233 distinct=23 match=no` and the head prints `printed=23 distinct=23 match=yes`.
- my probe (deleted refs): the baseline prints `owed_after_delete=7 want=1 match=no` and the head prints `owed_after_delete=1 want=1 match=yes`.

Mutation proof (ev/mutants.txt). Every mutant was killed and restored, and the tree was left clean.
- M1 to M4 reproduce the body exactly (2, 2, 2 and 1 named FAILs; 81 and 154 checks).
- My own mutants:
  - M5 drops the handoff `level_set`: cloud_relay prints 8 FAIL.
  - M6 makes the reader ignore `.level`: tick prints 1 FAIL.
  - M7 makes a failed probe listing clear the level: 1 FAIL.
  - M8 makes the `dispose --log` CLI ignore `--log`: 1 FAIL.
  - M9 appends the level to the log again: 1 FAIL ("the event log carries no level line").

Self-tests (ev/selftests.txt):
- head: tick `154 checks, 0 failed`; relay `81 checks, 0 failed`
- base: tick 150/0; relay 74/0

These match the body.

Class (step 6). I ran the body's two enumeration rules at the head (ev/seams-*.txt):
- There is one writer, cloud_relay.sh. The level kinds `probe-ref` and `handoff-no-pr` both move to level_line/level_set.
- The events are owed(), handoff-update, approve-held-runs, dispatch (x2) and reviewer-fire. Each has its PR as the first all-digit field in f[1:4].
- There is one reader, orchestrator_tick.py. Its hermetic default is os.devnull, which makes `.level` not-found, which is harmless.
- governance.yml only runs the self-test, and tick_loop.sh does not read the log.
- No seam is outside the diff.

Figures:
- The figures for fixture, null, self-tests, structure (`STRUCTURE RATCHET PASSED`) and archscore (`dS +0.0000 NULL`) are re-derived (ev/cheap-checks.txt).
- I could NOT re-derive the recorded-log figure (35214 lines -> printed=15; 34757/13/442/2 split). Its archive lives on the orchestrator's machine, so it is unverified here.
- `harness_headers.py` could not run locally (no voluptuous). CI covers it.

Other checks:
- VERSION, the manifest and RELEASE_NOTES are untouched.
- No claim files or golden files were touched (diff stat).
- The `closures.json` change is one INERT read for the new harness file. The new file earns it.
- Merge: `git merge-tree --write-tree origin/main(03b49e152) 90bab078d` exits 0 with no conflict and no claim driver involved (ev/merge-tree.txt).

CI (ev/check-runs.txt, from the check-runs API at the head): 49 runs. Every run is success, skipped or neutral except `nightly-status` (failure). That check reports main's last scheduled run, through the pinned base copy of tests/nightly_status.py. The diff touches neither that file nor tests.yml, so the failure is not this PR's. `pr-contract` is green, and it ran after the last red concluded. Earlier heads in the range: b38c6431 has no red, and 12dfce128 has only nightly-status (ev/check-runs-range.txt). So the body's "Red checks: none" holds.

Forward-carry: the body's "none" holds for this PR's own findings. The roster carries one item INTO this group (from #2545): "its grammar must agree with the ledger's when that lands." No such ledger is on main (03b49e152), so that agreement binds whichever lands second. The body does not mention the carry. This note is advisory and does not block.

Architecture (step 15): there is one owner of the grammar (cloud_relay.sh writes, the tick reads), and writes go through temp+mv. The reader-side skip of PR-less OWED lines is a transitional compat arm, and the body says so. I found no breach.
