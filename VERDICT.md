Fix review: merge 95bf04a83cf16aab992410968deea3aaa3ca58e1

bus-nonce: 2e036a43562ae0d8ab779753f7588082

## Evidence

- Round 1, handoff review: no pull request exists yet, so there is no review packet and no CI run to read; no check has run at this head, so no red is owed an answer (owed-reds set in `ev/owed-reds.txt`).
- Head measured: 95bf04a83cf16aab992410968deea3aaa3ca58e1, the body's `## Head` (`ev/HEAD.txt`). Merge base 14f227c5bd0eb80855b21055cc668857a5f820b4; roles diff merge-base...origin/main empty (contract current).
- Merge: `git merge-tree --write-tree origin/main <head>` rc 0 at origin/main fc2a7edcf2be (tree ea61f62bd5d1), no conflict; head is behind main but merges cleanly (`ev/merge-tree.txt`).
- Diff touches only `tools/audit/seat/open_pr.sh`, `tools/audit/seat/pr_args.sh`, `tools/audit/seat/instruments/open_pr.sh.md` (`ev/diff-names.txt`): no new tracked file, `VERSION`, manifest, notes heading, claim files and budgets untouched.
- RESULT selftest-head: `pr_args.sh --self-test` at the head: 205 checks, 0 failed, rc 0, 4m19s (`ev/selftest-head.log`). The six new arms pass: figure body opens with both pushes; mut:opfig2 refused at the row push naming another head, PR closed; mut:opfig1 refused at the code push with nothing pushed; null control (no block) opens and its row push prints `ROW-ONLY: prepr SKIPPED`; re-run after a p2 close clears leftovers and opens; mut:opclear fails the re-run (`ev/selftest-head-figure-arms.txt`). The body's three named mutants are thus re-run and fail as claimed.
- RESULT real-instrument repro (reviewer-built, not the fixer's stub): with the real `tools/pr/figure_block.py` and the base registry's `merge-base` instrument in a scratch repo, a block rendered at the code head verifies rc 0 there; after main moves and is merged, the same body is refused (`names head=41dc1fd62bde ... this run is head=c3b49a04127c`, rc 1) — the without-fix state; `refresh --base origin/main --head HEAD` then verifies rc 0 — the with-fix state. A body with no block is skipped by op_figures' guard and is byte-identical even after a direct refresh (`ev/real-figure-block-repro.log`).
- Real pusher read: with a refreshed block the p2 body is no longer `prefix(live, note)`, so the real `app_push.sh --row-only` falls to a full prepr (row_only_verdict (d)); the stub models that (`prepr RUNS: the body changed`). Correct, at prepr's cost, for figure-block bodies only.
- Figures: the body quotes none (`## Figures: none`); every count it states (three mutants, one null control) re-derived from the self-test log above.
- Forward-carry: body names none; the stub limitations are disclosed in its opening paragraph.
- RESULT targeted mutants (reviewer's own, `ev/mutant-headC.diff`, `ev/mutant-noguard.diff`): both survive, 205/0 each (`ev/selftest-mutant-headC.log`, `ev/selftest-mutant-noguard.log`); carried under Findings. Not a mutation-vacuous block: every line the body names fails its arm when deleted, and the real-instrument repro pins the head the refresh must use.

## Findings

- Surviving mutant headC: op_figures rendering at `--head $C` instead of `--head HEAD` passes the self-test, because the stub figure_block.py ignores `--head` and reads `git rev-parse HEAD`; with the real figure_block.py that mutant re-creates exactly the stale block this PR fixes. The arm should let the stub honour `--head`, so the predicate the fix rests on is pinned. Carry: dismissed: tooling test gap in a disclosed stub; the predicate is correct at this head and pinned by this review's real-instrument repro (ev/real-figure-block-repro.log); the owner may re-open it as a pr_args.sh arm
- Surviving mutant noguard: replacing both ancestry checks in op_clear_leftover with `true` (so a local branch or worktree holding commits origin lacks is force-deleted) passes the self-test; no arm exercises the refuse path that protects unpushed work. Carry: dismissed: the guard reads correct by inspection at this head and only the deletion-of-unpushed-work path is unpinned; an arm with an extra local commit on fix/<topic>-pr would pin it
