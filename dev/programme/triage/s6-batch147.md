# Proposal triage, session s14, batch 147 (P556, and an amendment to P554)

This batch amends batch 146's P554 on the orchestrator's measured correction, and rules
`s7/triage-queue-s7.txt` line 240. The bar and the denominators are batch 141's.

Sources: origin/main `d08ed31049`. Every carry it routes cites this file, at its roster record.

## P554: S14-PULSE-VERDICT-WHILE-TRAIN-LIVE, amendment (what the train holds)

Verdict: ACCEPT, narrowed. This amendment supersedes batch 146's P554 "Cost" and its count. The
batch 146 carry was voided in the queue before it drained (queue line 4271, `#replaced-below`);
it is not on the roster.

Source: the orchestrator's correction to batch 146 (2026-11-11, about 01:20Z).

Instances:
- **The spool.** The train's holdings include the spool, `<state>/queue-add.jsonl` (merge_train
  `QUEUE_SPOOL`).
  - At 01:10Z it held 3389, 3390, 3391 and 3392; the orchestrator measured this. `add` answered
    "ALREADY #3392: spooled for the live train's next batch" at 01:12Z.
  - At 02:11Z the spool holds `{"pr": 3392, ...}`.
- **The corrected count.** Of the 13 STOPPED verdicts, 9 were held: 5 pending and 4 spooled. Only
  #3379 and #3419 were in no queue, and both had repair fixers fired. Batch 146's "six owed" was
  wrong by four.
- **The instrument's rule.** It is `merge_train.already_held(pr, verdict, seen, spooled)` (main line
  1278), which `add` and the drain both apply. It also answers "held" for a PR this train skipped
  at the same verdict, or merged, or ran.
  - A skipped-at-this-verdict PR is one the train will not retry, so its verdict is owed to a seat.
    These are #3383 and #3386 at 01:10Z, the class batch 145's P553 repairs.

Cost: `pulse.py` reads the train's holdings through merge_train's own readers, `spool_read` and the
`QUEUE_SEEN` record, and its `already_held`, never through a path it names by hand.
- While `train.pid` is alive, a verdict reads `held by train` when `already_held` answers
  "spooled for the live train's next batch" or "still to run in this train".
- Its other answers (skipped at this verdict, merged, ran) and `None` stay counted as STOPPED.
- A dead train pid counts all.
- Self-test:
  - a spooled PR and a pending PR are held with a live pid;
  - both are STOPPED with a dead pid;
  - the null control: a PR skipped at its current verdict is STOPPED;
  - a mutant on the spool read, and a mutant on the answer filter.

Binding: one carry, R10-STANDING-CONTRACTS-P2 (`pulse.py`), replacing batch 146's. Carry file:
`b147-P554a.txt`.

## P556: S14-CARRY-FOLD-WRONG-CHECKOUT

Verdict: ACCEPT, narrowed. It repairs an observed wrong behaviour. The source's proposed fix is
already on main, so the carry is a reproduce-first repair.

Source: queue line 240 (2026-11-11T01:10:05Z, orchestrator friction).

Instances:
- **The refusal.** `tick.txt.relay.log` has `OWED carry-fold r10-plan-page-residue 9ec041dfb994
  body_push rc=1 after the fold: body_push: handoff/r10-plan-page-residue is at 428aa56b7cdc, this
  checkout at d08ed31049cd`.
  - `d08ed31049cd` is origin/main's tip.
  - `tick-loop.log` has the same refusal 18 times for `r10-process-slim-p2`, between
    2026-11-10T08:36Z and 19:18Z.
  - The source counts four handoffs that needed a hand seat, about 10 min each. That figure is the
    source's.
- **The proposed fix exists.** `carry_fold_arm` on main (`cloud_relay.sh` lines 836-840, since
  67a823c2e7 on 2026-11-08) runs `git fetch origin refs/heads/handoff/<topic>`, then
  `git worktree add --detach <wt> FETCH_HEAD`, then runs `body_push.sh` from inside that worktree.
  `body_push`'s `ROOT` is `git rev-parse --show-toplevel` of its cwd.
- **The reproduction.** In a seat worktree, the same two steps land HEAD at `428aa56b7cdc`, which is
  correct. So the relay's wrong head is not the arm's logic run alone.
  - The candidate cause is `FETCH_HEAD` overwritten in the relay's checkout between the fetch and
    the add. It is not proven, and 18 consecutive repeats argue against a millisecond race.

Cost:
- **(1) The reproduction.** It comes first: the fold arm's worktree head is logged at the failing
  pass.
- **(2) No FETCH_HEAD.** The arm fetches into a private ref
  (`+refs/heads/handoff/<topic>:refs/hpo-relay/fold/<topic>`), which nothing else writes. It adds
  the worktree at that ref.
- **(3) The assertion.** Before `body_push`, the worktree's HEAD must equal the `ls-remote` tip.
  On a mismatch it prints both shas as `OWED carry-fold ... worktree at <a>, handoff at <b>`.

Self-test:
- the fold with a planted concurrent fetch of main still pushes from the handoff tip;
- the null control: a sequential fold pushes as today;
- a mutant on the private ref, and a mutant on the assertion.

Binding: one carry, R10-REVIEW-DISPATCH-RESIDUE, which lists `tools/audit/seat/cloud_relay.sh`.
Carry file: `b147-P556.txt`.
