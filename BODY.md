Root-cause analysis `dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md`: why `open_pr.sh`'s full prepr ran 50 to 99+ minutes, or past its caller's 3000 s bound, on three opens on 2026-11-10. The named causes, process states, cost test with measured numbers and routed countermeasures are in the document. No production code and no policy land here: one new markdown file under `dev/audit/` (an INERT prefix in `tests/closure.py`).

- It is not a queue and not a hung step. Each prepr took its heavy slot 0.8 to 5.2 min after its open started, and the three were three of the four slot holders. Every tree's leaf process changed between samples taken a minute apart.
- C-A, state (c): no `Prepr:` receipt reached the open, so `app_push.sh --reuse` ran the full prepr. That is 82 of 142 code bodies since 11-06. In 29 of them `body_push.sh` dropped a receipt that `reuse_verdict` would have accepted: 5 were re-pushes from another checkout and 24 were clean merges of main past the receipted code. Carry: R10-PREPR-RESIDUE
- C-A, unestablished for the other 49: `body_push.sh` prints one undifferentiated no-receipt line. Carry: R10-PREPR-RESIDUE
- C-B, state (d): the full prepr is long and starved here. The 4-slot cap dates from when prepr.sh had 123 `st` sites; at this base it has 325. The host has 8 CPUs and 8 GiB with 3.2 to 4.5 GiB in swap, and a CPU-loop multiplier of 1.2x to 5.9x. Prepr's step lines carry no time. Carry: R10-PREPR-RESIDUE
- C-B, the one step that looks hung: step 6d's `--record-self-tests` ran 64+ min on slim-p2 and was still running at 04:05Z. It replays pinned graders' CI run lines, against a comment that prices the step in seconds. It is progressing, not hung. Carry: R10-PREPR-RESIDUE
- Lowering `HEAVY_SLOTS` or moving open-time prepr to the cloud is a recorded refusal for now. Without an idle per-step baseline, which C3 produces, the cost test has no number.
- Measured end times: arbiter-off-restore pushed after 53 min, record-issue-continuation was refused after 71 min, and slim-p2 was at 99+ min and still in 6d at 04:05Z.
- Found while measuring: r10-hotfix-record-issue-continuation's self-test refused at 509 passed and 6 failed. slim-p2 passed 515 at the same base, so that open fails on its own defect and goes back to its fixer.

## Head

6839549fb1e73a1bd1e318e8b5a006430058f0c3, two commits on origin/main b0762725099f. Live process readings were taken 03:16Z to 04:05Z.

## Mutation proof

n/a: no countermeasure is landed. C1, C3 and C4 are check-shaped. Each owes, in its fixer's PR, a failing-then-passing self-test arm on the cases in section 6 of the document.

## Null control

For C-B, the CPU-loop probe at nice 10 ran in the same seconds as the nice 0 probe. Wall/cpu was 1.19 to 1.52 against 1.41 to 1.83, so the multiplier is the host's and not the probe's priority. For C-A, the 60 tips carrying a trailer are the control for the reuse path: median open 1 min (n=59), against 17 min (n=63) for full runs.

## Figures

- 82 of 142, and the 5/24/4/49 split: `git for-each-ref refs/remotes/origin/handoff-body/` over tips committed 2026-11-06 to 2026-11-10, reading each tip's `Code:` and `Prepr:` trailers.
- 29 of 33: `git merge-tree --write-tree <receipted code> $(git merge-base <code> origin/main)` compared with `<code>^{tree}`.
- Medians 17 and 1 min: `stat -f %B` / `%m` of each `~/hpo-orch/r10s6/pr/*/p1.log` (a proxy, birth to last write, runs under 240 min).
- Slots: `python3 tests/gate_lock.py slot-status` at 03:16Z and 03:26Z, and each `slot-00N` file's `taken_at`.
- Host: `sysctl -n hw.ncpu hw.memsize vm.swapusage`, `uptime`, `vm_stat 5`, `iostat -d -w 2`, and a 1-CPU-second Python loop timed against `time.process_time()`.
- 2 734 / 123 and 4 682 / 325: `git show c09cf12010:tools/pr/prepr.sh | wc -l`, and `grep -c '^ *st '` at that commit and at the base.

## Red checks

none

## Forward-carry

- body_push.sh carries a receipt from the parent body tip or onto a descendant code head, and app_push.sh reuse_verdict re-proves it. Carry: R10-PREPR-RESIDUE
- body_push.sh's no-trailer line names which receipt condition failed. Carry: R10-PREPR-RESIDUE
- prepr.sh step lines and the PRE-PR line carry elapsed seconds. Carry: R10-PREPR-RESIDUE
- Step 6d: measure per-arm and per-grader wall time on 6671786843 and correct the seconds premise. Leave to CI the grader replays instrument-self-tests already runs, and keep SELF-TEST READS. Carry: R10-PREPR-RESIDUE

## Friction

none
