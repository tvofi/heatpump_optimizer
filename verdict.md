Fix review: merge de1a371e2ed49c742ef690d605fbc8e605b853f3

bus-nonce: 1a35ee25dc97cd7c6b0640c34ac5c50f

## Round

This is round 3 of the fix review of #3241 (R10-CARRY-RESIDUE), by an opus reviewer in a cloud seat.

- Measured at PR head de1a371e2ed49c742ef690d605fbc8e605b853f3, a no-ff merge of code head bcbdcfb377d78433b122370bb21dc29b66371cfa. `git diff bcbdcfb de1a371e` is empty.
- Merge base: dc0a170b671814be196a54b1c71e29449f54d6d7. Null control: origin/main b36679ceaa65a08a67a84f0d934c93aa15f7c7f3.
- I used detached worktrees at the head, the base, origin/main, 9d16d843a and two separate mutant copies.
- `git diff <base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- Round 2 blocked at 95c7e604 as class-open: `review_owed` took a dispatched head as a prior even after a blocked verdict at that head. This round settles that block.

## Findings

- Residual: `governance / instrument-self-tests` (job 127922552146) concluded `cancelled` at this head when it hit `timeout-minutes: 30` (1814 s). Steps 1-101 were all success, and step 101 had printed `ci_predict self-test: 0 failed` before the cancel. The cause is not this diff:
  - origin/main's own run (job 127910411605 at b36679ce) was cancelled the same way at 1804 s;
  - this PR's steps 30, 39 and 70 take 0-3 s (`ev/instrument_job_compare.txt`, `ev/instrument_step_durations.txt`).

  The roster already carries this from the #3239 review. This head adds one more instance. Carry: R10-PROCESS-SLIM
- Residual: the body's `## Red checks` was written while bcbdcfb read WAIT. It does not name this head's concluded non-greens:
  - the cancellation above;
  - three deferral `gate` reds, `FAIL run(s) [...] at this head are still being judged; their gate decides` (jobs 127923462002, 127923310057 and 127940007490). Each was superseded within its own suite by a later gate run that passed.

  Under fix-review.md step 11, the evidence is the `pr-contract / pr-contract` run (job 127936796625), which started at 14:08:00 after the last real red concluded at 14:07:09 and passed. The later 14:14 deferral was re-run green by the gate sweep. So I do not re-derive the body's answer. Carry: dismissed: step 11's green pr-contract after the last concluded red is the evidence, and the red is main's (carried above)

## Evidence

- **Head.** `ev/HEAD.txt` names de1a371e2ed49c742ef690d605fbc8e605b853f3. Re-read before returning: the PR head is still de1a371e (`ev/head_at_post.txt`). The body's `## Head` names it.
- **Merge with main.** `git merge-tree --write-tree origin/main de1a371e...` exits 0 with tree 71feb7073, so there is no conflict (`ev/tree_checks.txt`).
- **CI.** `merge_train.py classify de1a371e... --pr 3241` printed `GREEN de1a371e2ed49c742ef690d605fbc8e605b853f3 pending: none red: none` (rc=0). The polling history is in `ev/classify.log`, and the final check-run list (68 runs, page 2 empty) is in `ev/check_runs_final.txt`.
  - Gate job 127937543894 (KIND code) printed PASS. Gate job 127940017942 (edit) printed PASS.
  - The packet's `required-red` refusal at render time was the 13:39 deferral gate. The live state supersedes it.
- **Three-dot diff.** 8 files, the delivery row dev/programme/delivery/3241.md among them. It touches no VERSION, manifest, RELEASE_NOTES, golden file or claim file.
- **Round-2 block settled.** ledger.py `review_owed` now keeps a dispatched head as a prior only when no verdict names it (`h not in newest`), and only a head whose newest verdict is a merge carries.
  - Failing test first: at 9d16d843a (test added, code as at 95c7e604), `ledger.py --self-test` gives 91 checks, 1 failed. At the head it gives 91 checks, 0 failed (`ev/failing_first_9d16d843a.txt`, `ev/selftests.txt`).
  - My round-2 reproducer now shows the right state: the blocked head is in `dispatched` and the result is REVIEW OWED, by the new fixture row "a blocked verdict's head in the dispatch record is no prior".
  - That row's null control, a dispatched head whose newest verdict is a merge, still carries.
- **Self-tests** at base, head and main (`ev/selftests.txt`); base and main are identical:

  | self-test | base | head | main |
  |---|---|---|---|
  | ledger | 77 | 91 | 77 |
  | orchestrator_tick | 272 | 275 | 272 |
  | owed_unactioned | 46 | 47 | 46 |
  | beat_jobs | 107 | 107 | 107 |
  | r10_ledger_mutants | 135 | 180 | 135 |

  Every run reported 0 failed. Each count the body quotes reproduces.
- **Mutation proof, fixer's instrument.** A clean run in its own worktree (`ev/mutants_clean.txt`): `plants: 63, without a FAIL line: none`, rc=0.
  - C15_blocked_dispatched_prior rc=1 fails=1; C9 rc=1 fails=2; C14 rc=1 fails=1; T3 rc=1 fails=6.
  - The round-1 M3-M11 lineage (C1-C14) is all killed.
  - `--null` gives rc=0 fails=0 for all six owners (`ev/mutants_null_clean.txt`). These match the body's table.
  - An earlier sweep overlapped a timed-out run in one worktree, so I discarded it. It is kept in `ev/mutants_all.txt` and printed the same summary.
- **My own plants of the round-3 change** (`ev/my_mutants.txt`, restored afterwards, null 91/0):
  - R3a, newest = oldest verdict: killed, 2 fails.
  - R3b, any merge line is a prior: killed, 1 fail.
  - R3c, drop the newest exclusion: killed, 1 fail.
  - R3e, priors without recarry: killed, 5 fails.
  - R3d, exclude only blocked-newest heads, survives. It is an equivalent mutant: `VERDICT` matches only `merge|blocked`, so a head excluded under the head's rule and kept under R3d is a merge head, which is already a prior.
- **Class.** The newest-verdict rule covers both verdict kinds the `VERDICT` regex admits.
  - A dispatched head with no verdict is still a prior, which is intended. It is self-correcting: a later blocked verdict there removes it.
  - A code commit after any prior fails `git_recarry`'s first-parent walk, as the existing null rows and C12 show.
- **Gate scripts** (`ev/gate_wt-head.txt`, `ev/gate_wt-main.txt`):
  - Head: `MODE: SCOPED -- 4 script(s) run, 29 scoped out`, the same as the body. STRUCTURE RATCHET PASSED; ALL 2632 ENTITY CHECKS PASSED; ALL 162 DEBUG COLLECT; ALL 296 doc_claims; ALL 4876 FEATURE CHECKS PASSED.
  - origin/main: structure PASSED; ALL 2637 ENTITY CHECKS PASSED (main's own tree); 162 debug_collect; 296 doc_claims. Main's features run was still going when I returned this verdict.
- **The four earlier owed items** are on R10-CARRY-RESIDUE-2 at origin/handoff/audit-r10-roster: the #3241 CARRY line (standing-tick.md), the pr-token gap, the landing-barrier class and the bus round counter. `carry_audit.py landed --body <body>` gives `CARRY-LANDED: 0 missing` under `--pr 3241`, `--pr #3241` and `--topic r10-carry-residue` (`ev/carry_landed.txt`).
  - The standing-tick.md policy line goes to a round-10 group under the orchestrator's minimal re-cut ruling, not to round 11.
- **The six carries at the base**, unchanged since round 2's null control (verdict/3241):
  - Carry 1 is delivered by df9bfd301, carry 2 by 408644f7f and carry 3 by 82f333b9c.
  - Carry 4 is delivered at the base; this PR changes only the comment.
  - Carries 5 and 6 are absent at the base, and the body's `git grep` printed NONE.
- **Carry 4 figures.** I re-read the three CI readings round 2 had not read (`ev/carry4_rereads.txt`):
  - job 125160076828: `loop_cpu_ratio 0.1339`, ref_ms 30.4;
  - job 125097530406: 0.1418, ref_ms 46.3;
  - job 125316010511: 0.1433, ref_ms 46.7.

  All five readings in the tree comment are now re-derived: two in round 2 and three here. The margin 0.128 / 0.1245 = 1.028 re-derives.
- **Harness.** No finder harness is named. The instrument is the fixer's in-tree `r10_ledger_mutants.py`. My plants R3a-R3e are my own, out of tree, and disclosed here.
