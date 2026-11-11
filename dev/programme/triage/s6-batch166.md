# Proposal triage, session s14, batch 166 (P580)

This batch rules `s7/triage-queue-s7.txt` line 262. The bar and the denominators are batch 141's.

Sources:
- origin/main `a7628041dc`. Every `cloud_relay.sh` line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster` `fc68214974`.
- `tick-loop.log` in the state dir, its `TICK-PASS` and `TICK-RELAY` lines for 2026-11-10 and
  2026-11-11. A `TICK-RELAY <end> relay=ok started=<start>` line gives one relay pass's length.
- The relay's last pass output `tick.txt.relay.log`, and the mtimes of the relay's fold files
  `cloud-fold-<topic>.md` (written just before `carry_fold.py`, `:827`) and `cloud-fold.out`
  (written by `body_push.sh`, `:840`) in the state dir.
- One timed replay of the arm's read loop (`:812-818`), run from a seat worktree at 06:00Z.
- No GitHub API calls.

## P580: CARRY-FOLD-ARM-REJUDGES-EVERY-PASS

Verdict: ACCEPT arm (3), corrected: a judged-outcome memo in `carry_fold_arm`. REJECT arms (1)
and (2), the `dispose` widening.

The cost is real, but the proposal names the cheaper part. Each pass re-fetches every
`handoff-wip/<topic>` ref and reads its `BLOCKED.md` (`:818`), about 30 s. The larger part
is a fold whose `body_push.sh` failed after `carry_fold.py` succeeded. Only `rc = 0` writes
`cloud-folded` (`:843`), so the arm runs the whole `carry_fold.py` and `body_push.sh` pair again
on every pass. That is about 3 minutes per pass for two topics today. The skip at `:821` never
fires for them.

Source: queue line 262, 2026-11-11T05:57:20Z, orchestrator s14.

Instances:
- **The read loop.** At 06:00Z, `git ls-remote origin 'refs/heads/handoff-wip/*'` lists 63
  refs: 46 topics pass the `:817` filter, and 15 have a `BLOCKED.md`. The arm's fetch-and-show
  loop over them took 33 s cold and 27 s warm.
- **The re-run folds.** The relay's last pass (`tick.txt.relay.log`) prints 12 `OWED carry-fold`
  lines. Two are `body_push rc=1 after the fold`, for `r10-sav-valuation-residue` and
  `r10-train-residue`. Both topics run `carry_fold.py` then `body_push.sh` again on every pass.
  - Fold-file mtimes in that pass: sav-valuation at 05:48:17Z, train-residue at 05:49:59Z, and
    `cloud-fold.out` at 05:51:18Z. That is about 102 s and 79 s, **about 181 s per pass**.
  - The refusal in `cloud-fold.out` is a body-lint error, `` `## Head` does not name 5e91c2c``,
    together with `RED UNANSWERED` ancestry reds. The first cannot change until the kept body
    changes. The second can clear without any ref moving.
- **The pass it sits in.** `TICK-RELAY` relay-pass medians per hour on 11-11, 01Z-05Z: 719,
  677, 832, 605 and 588 s; on 11-10, 14Z-20Z: 563-587 s. The carry-fold arm's measured
  ~211 s (30 s + 181 s) is **about 36%** of a 588-605 s pass today.
- **The proposal's symptom lines.** `relay=running` on a `TICK-PASS` line is the normal state.
  All 79 `TICK-PASS` lines from 11-10T13Z to 11-11T05Z carry it, so it does not single out
  this arm. The claim of a pass falling from ~10 min to under 2 min is not supported: the pass
  ran at ~570 s on 11-10 as well, and the arm accounts for about 211 s of it. The opener
  latency (`SKIP moved` x3) was not traced to this arm. It is not counted.
- **Rule applied per instance**, as a memo keyed on (topic, wip sha, kept-body sha):
  - the 44 of 46 topics whose judgement depends only on their two shas (10 BLOCKED.md not
    naming CARRY-LANDED alone, and the topics with no BLOCKED.md): skipped with no fetch, which saves
    ~27-33 s per pass;
  - the 2 failed folds: retried at most once an hour instead of every pass, which saves
    ~181 s on 5 of 6 passes, about 151 s per pass averaged;
  - together about 180 s of a ~600 s pass, **about 30%**.
- **Null control.** The 11-10 passes (median 563-590 s) bound what the rest of the relay costs.
  Removing the arm's 211 s from today's 600 s gives about 390 s, which is below them. So the
  saving is a ceiling for today's state, not a claim on every day. With no failed fold it falls
  to the 27-33 s read loop alone, about 5%.

Cost:
- `cloud_relay.sh`, 1,871 lines, a hot file. It has no row in `tests/structure_budgets.json` at
  `a7628041dc`, so no capped file is touched.
- The memo is about 20 production lines and one state file, `cloud-fold-judged`, with lines
  `<topic> <wip sha> <body sha> <outcome> <epoch>`.
- Self-test arms beside the `mut:foldonly` cases (`:1827-1850`), about 25 lines:
  - an unchanged nothing-folded ref is not fetched again, and its OWED level line still stands;
  - a moved wip ref or body ref is judged again;
  - a failed body push is retried after the TTL and not before.
- Owner R10-REVIEW-DISPATCH-RESIDUE (medium; not started; 22 carries), so P551's five-carry
  split applies at dispatch.

Binding:
- **Arm (3), corrected: ACCEPT**, carry to R10-REVIEW-DISPATCH-RESIDUE. The measure is about 30%
  of the relay pass today, above the 20% bar on CPU and wall-clock. Its terms:
  1. Read the shas from the `ls-remote` the arm already makes. A topic whose (wip sha, body sha)
     is in the memo is not fetched and not shown.
  2. Its stored OWED line is re-written into `cloud-level-fold.$$`, because `level_set`
     (`:849`) replaces the whole carry-fold level each pass. A memo that drops the line clears
     an owed item silently. This is the one way the arm can go wrong, and it needs a self-test
     arm.
  3. A failure after the fold (carry_fold rc != 0 or body_push rc != 0) is retried once its
     memo entry is 3600 s old, never every pass. An ancestry red can clear while no ref moves.
  4. Success still appends to `cloud-folded` as today.
- **Arms (1) and (2): REJECT.** Admitting `handoff-wip/` to `dispose` (`:322`) and checking
  `disposed` before the fetch puts a hand step on each wip ref to save what arm (3) saves with
  none. It also widens what `dispose` accepts, which is another surface to pin. Once (3) lands,
  the binding cost is all cost and no further benefit.
- The local workaround in force (stale wip refs archived as tags and deleted) stays the
  orchestrator's until the carry lands.
