# D13 verify, lens V3 (reach and class), round 9, group G1

Baseline 1936d5ca. Evidence tree 6f51db2c. The finder's snapshot is `tools/audit/round9/D13/s1/window.json.gz`. No GitHub access; git history is local. The "real HA" lens reads as "real in the live process": checked against git and the tree. The API rows come from the snapshot alone. Node v22; all RESULTs are counts. load1 was 1.1-3.3 during the runs, thread_factor 1.0.

**Harness defect (all three findings):** `enum_gap.mjs` reads `origin/main`, which in the shared worktree is db878b29, 18 commits past baseline. Run as committed it prints `stats_window_merges=0 subject_merges=256 gap_marked=1` (load1 0.39). All re-runs below used a `git clone --shared` with `refs/remotes/origin/main` pinned to 1936d5ca. `D13-s1-01_reach.mjs` makes that pin itself.

## D13-s1-01: API-mode enumerator drops 52 merges unmarked

- **Finder's harness:** base 201 / 253, gap 52, gap_marked 0 (load1 1.85). drop arm: 200 / gap 53 / 0. restore arm: 253 / gap 0. Exact.
- **Own harness:** `tools/audit/round9/D13/verify-v3/D13-s1-01_reach.mjs`.
  - Metric: the `TOTAL: e error(s) over N merged pull request(s)` line of production `--record --since v6.6.0`, run twice through a stub `curl`: as-is (replays the snapshot's `[]`) and restore (answers the subject's #N).
  - `record_enumerated` 201 → 253. `record_errors` 15 → 24. `unchecked_marker_asis` 0.
  - `dropped_undispositioned=9`: #1157-#1165 are merges with no disposition that `--record` never reports.
  - `dropped_with_delivery_row` 43 of 52.
- **Attacks:**
  - Phantom-PR: refuted. The 52 are real PRs of this repository (delivery rows, RELEASE_NOTES.md).
  - Range correction: #1097-#1165.
  - Contention: none (counts).
- **Reach:** the drop is real in both consumers driven (`--stats`, `--record`). The `[]` answers themselves rest on the snapshot.
- **Severity:** medium. It is an instrument; the workaround is the subject count, but the record gate is blind to 9 real gaps.
- **Seam rule:** enumerates all four callers of `mergedPRsFromWindow` (--record, --stats, --sunset, --record-known-bad). Two are demonstrated.
- **Class:** I4 confirmed (the API-map definition of a merged PR against the subject definition, with no marker).
- **Vote:** verify.

## D13-s1-02: 22 reverify rounds caught 0

- **Finder's harness:** `reverify_rounds=22 reverify_blocked=0`, merges-only 11, ci-only 1, content 10. `block_one_reverify` arm: 0 → 1. Exact.
- **Own harness:** `tools/audit/round9/D13/verify-v3/D13-s1-02_diffeq.mjs`.
  - Metric: reverify round = a verdict after a `merge` verdict on a different head. Identical = the same `git patch-id --stable` for `diff merge-base(H, M^1)..H` at both heads, where M is the PR's merge commit.
  - Blocked 0 of 22. Identical 3, changed 19. With `-U0` and the managed files excluded (both claim files, `tests/closures.json`): identical 9, changed 13.
  - Cross-tab by move class:
    - merges-only: 2 of 10 identical (5 of 10 relaxed)
    - ci-only: 0 of 1 (1 of 1 relaxed)
    - content: 1 of 11 (3 of 11 relaxed)
  - Base rate: first-verdict block rate 16/188 = 8.5%, so P(0 blocks in 19 changed rounds) = 0.185. Perturbation `flip`: 0 → 1.
- **Attacks:**
  - Diff-equivalence: most merges-only moves did change the branch's diff (the claimnotes driver, closures re-records, conflict resolutions). The proposed byte-identical carry would save 2-6 rounds, not 12.
  - Null control: 0/22 is consistent with chance (p 0.185 on the content-changed rounds).
- **Severity:** process cost, no user-visible defect. medium, not high.
- **Seam rule:** partial. It enumerates every reverify round but classes a move by commit type, not by the stated property.
- **Class:** new. An exact-head approval is re-bought in full on a diff-neutral move. Second instance, after round 8 D13-s1 (15 of 15 reverify rounds merge).
- **Vote:** weaken → medium.

## D13-s1-03: body-answer blocks (8) exceed every engineering class

- **Finder's harness:** blocked 21, body-answer 8, max engineering class 1, record-and-body 12, engineering 7. `rca_to_harness` arm: 7 / 11 / 8. Exact.
- **Own harness:** `tools/audit/round9/D13/verify-v3/D13-s1-03_blocks.mjs`.
  - 21 blocked verdicts, 16 distinct words.
  - root-cause-unanswered: 6 verdicts on 5 PRs. red-check: 2 on 2. Body-answer 8 verdicts on 6 PRs.
  - Perturbation `dup`: verdicts +1, PRs unchanged.
- **Attacks:**
  - (a) The mechanism is wrong. pr-contract already lists failure check-runs (#956), and `checkPrBody` refuses an unnamed red over every branch head since a07dd57d (2026-09-19, #1144). That predates all 8 blocks (2026-09-22, 2026-09-24). The finder's fix scope proposes a check that exists.
  - (b) Measured residual: order, not absence. At all 6 PRs' final heads, typing completed after the last pr-contract run (6/6), and mutation did too at 5/6. Window-wide, 346 of 738 mutation/typing runs completed after their head's last pr-contract. All 8 reds are typing, mutation or fast.
  - (c) Grid: 7 of 8 verdicts are from 2026-09-24, PRs #1559-#1563. Leave that wave out and 1 remains.
  - (d) Multi-reason: 3 of 8 also carry harness or regression blocks, so only 5 rounds were body-answer alone. Counting every reason, engineering is 10 against record-and-body 12.
- **Severity:** process cost. medium.
- **Seam rule:** demonstrated-only. It counts classes and does not enumerate check-run order at each branch head.
- **Class:** corrected from new to I3 (a required check runs before the state it enforces exists).
- **Vote:** weaken → medium. The corrected mechanism: re-run the body check when the slow jobs conclude.
