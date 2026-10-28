Fix review: merge e1adaa79ce167dfc0fd022280a44e3e38b565d54
bus-nonce: ac991a7d38881129260f9e98ae7e9988

# Fix review -- PR #2890, triage batch 41 (P212-P215)

Round 3, the second re-cut. The batch says round 1 blocked on `claim-false`, and batch 44
(#2898, P219) says round 2 blocked on the V-number offset. Reviewed head:
e1adaa79ce167dfc0fd022280a44e3e38b565d54, in a detached worktree at that head, against
origin/main 07295d4ea. `dev/governance/roles/` has no diff between the merge base and
origin/main.

## Results

- Headings: all four have the contract form `## P<n>: <title>`. P212-P215 are new, and main
  ends at P211. Each heading's id matches its `Source:` line, and each resolves in the
  orchestrator's `proposals.md` to the same title and stamp: `## V125` to `## V128`,
  `orchestrator s7, 2026-10-27T20:20Z`. The +7 offset batch 44 measured is gone from this
  branch.
- Verdicts, through `roster_edit.ruling_verdict` at the head: P212 REJECT, P213 ACCEPT,
  P214 ACCEPT, P215 ACCEPT. Changing P214 to DEFER reads DEFER, so the gate reads this file's
  entries (`ev/ruling-verdicts.txt`).
- P212's citations hold. `bus.sh:479` writes `<pr> <head> <reviewer> <nonce> <date> <model>`,
  and `dispatched_to`'s match at line 313 keys on `pr hsha`, which supports the argument that a digest
  of in-head files cannot see the instance. The three tips and both spans are exact:
  18:31:07Z to 20:23:46Z is 1 h 52 m 39 s, and 32b938f3e to d61e2834c is 1 h 45 m 06 s. The
  count is finding F1.
- P213's citations hold. `review_packet.py:289` is the head-note string. `:411` is its
  self-test arm. `head_note.py` defines only `head_offset` (20) and `prefix` (39), besides
  `self_test` and `main`. The `update_pr.sh` usage block is as quoted.
- P214's citations hold. `tests/env_drift.py` `merge_claim_refusal` starts at 1844, and the
  quoted message is verbatim at 1851-1857. `merge_main_bot.py:139` is the
  `skip-driver-refused` join.
- P215's citations hold. `roster_edit.py:703-705` lists the nine ops. `sweep_template.md:63`,
  `nudge.md:89` (set-stage) and `nudge.md:105` (append-group) are quoted correctly.
  `set-resume` appears in no role and in no sweep template. `roster_queue.py:94-102` builds
  the child `env`.
- Roster facts at `d61e2834c` and at `9aed78e0e` (`ev/roster-facts.txt`): 212 groups.
  R10-ORCH-REVIEW-PACKET is `done` with 10 carries and owns `review_packet.py`.
  R10-996-RUNNER-CLAIMS is `carries-open` with 2 carries and owns `env_drift.py` and
  `claimed_drift.txt`. R10-ROSTER-OPS is `done` with 6 carries and owns `roster_edit.py` and
  `r10_roster_ops_mutants.py`. R10-RCA-FRICTION-RESIDUE `fixes` is `[2410, 2593]` at
  `d61e2834c`. No group owns `tools/pr/merge_main_bot.py` or `tools/pr/head_note.py` in
  `files` or `hot_files`.
- `git merge-tree --write-tree origin/main <head>` exits 0 (tree `d9d867c84`). Live
  check-runs at the head: 55 runs, 38 success, 17 skipped, 0 failure, 0 pending. There is no
  red to answer. `VERSION`, the manifest and the notes heading are untouched.

## Findings

- F1 (non-blocking, a figure re-derived under my own definition): P212 says "twelve commits"
  between 18:31:07Z and 20:23:46Z, measured by `git log --format='%cI'
  origin/handoff/audit-r10-roster`. That command, as cited, prints 34 commits in the window,
  because it walks the merged-in main history. Twelve reproduces only with `--first-parent`.
  Restricting the walk to `-- dev/programme/rosters/` gives 13 (`ev/roster-window.txt`). Under
  every definition the churn is at least the stated rate, so the REJECT holds and is
  understated. The ruling's command is missing the flag its figure needs. Carry: dismissed: conclusion holds under all three definitions; this verdict records the flag
- F2 (non-blocking): the ACCEPT destinations for P213 (R10-ORCH-REVIEW-PACKET) and P215
  (R10-ROSTER-OPS) are both `done`. Each ruling says "the roster op reopens it", so the carry
  is only live once the orchestrator runs `set-stage` before `append-carry`. A done group is
  not a destination under `finding-propagation.md`. Carry: dismissed: the reopen is stated in the ruling and is the orchestrator's routing step under proposal-triage.md
