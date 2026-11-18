# Proposal triage, session s10, batch 111 (P369)

The rolling batch after batch 110. Facts were read at origin/main `8247a1ed1`, at pull requests
#3147 and #3149, and in the session's seat ledger. The ruling falls under the owner's LOG class
(tvofi, 2026-11-01 ~19:50Z): a proposal whose friction blocks no production merge and that proves
no improvement above 10% is recorded with its evidence, and no carry or group is built. The batch
grammar has no LOG verdict, so the ruling is written as DEFER, naming what would change it.

## P369: a nightly ledger commit moved main under a green batch proof, and four pull requests were re-proven

Verdict: DEFER (LOG, by the owner's 2026-11-01 ~19:50Z rule). No carry and no group. The answer
changes on a measured figure above 10% in CI time, completion time, right-first-time or tokens,
with a baseline and a null control. It also changes if a ledger push stops a train, past its
main-moved bound, on a pull request that touches `custom_components/`.

Source: the orchestrator s10's queue line of 2026-11-02T02:55:35Z. It proposes one of two
remedies. Either the merge train accepts a main move whose diff is confined to record paths
without a recarry, or bot record pushes wait while a batch proof is in flight.

Instances:
- **Train batch 3, 2026-11-02.** `git show --stat 8247a1ed` shows author `hpo-ledger[bot]` at
  02:34:55Z. Its subject is "ci: record nightly kills", and it touches only files under
  `tests/mutation_ledger/killed_by/`. It landed while the batch proof was green at `5334150c`, the
  head of #3149. The orchestrator's line puts the cost at a re-proof of 4 pull requests, about 1 h.
  - One of those four touches production. `gh pr view 3147 --json files` lists 2 files under
    `custom_components/` (R10-DEPS-PIP-BUMP). #3149, #3077 and #3153 list none.
  - The train recovered the batch itself. `merge_train.py`'s `--main-moved-tries` (default 3,
    `MAIN_MOVED_TRIES` at line 651) re-proves the remaining entries on the new main. So #3147 was
    delayed by one re-proof, not held.
- **A second instance, 2026-11-01.** Seat ledger line 3239: the merge seat recorded a post-merge
  SKIP after #3069 because main moved to `df66556f` under the same subject and author. It ended
  the train with TRAIN_RC=1, and the next train proceeded.
- **The rate is not measured.**
  - `git log origin/main --first-parent --author=hpo-ledger --since=2026-10-12` counts 28 such
    commits in round 10, one a night.
  - The seat ledger names 2 that landed under a live train. Nobody has counted the rest against
    the train's own logs, and the proposal asks for exactly that measure.
- **Remedy (a) is unsound for these files.** The records are not inert.
  - `tests/mutation_table.py`'s `dispositions()` reads every `killed_by` entry.
  - The ratchet counts unpinned sites against that ledger, and the completeness check refuses a
    ledger that disagrees with the inventory "in either direction".
  - So a batch pull request that edits a site the night's push just pinned can merge onto a main
    that the ledger then fails. Re-proving on the new main is what catches that.
- **Remedy (b) extends an existing guard.**
  - `nightly.yml`'s record beat already waits on `refs/heads/train-hold` (R10-TRAIN-HOLD; its
    `HOLD_MAX_AGE_S=3600` block).
  - The `mutation-ledger-push` job does not read that ref: it pushes to main inside a three-try
    fetch, apply and push loop, with a 10-minute timeout.
  - `merge_train.py`'s header gives the hold's scope as the record beat's auto-merge (#2302). The
    ledger push is outside that stated scope, so the gap is a design choice, not a defect.
  - A hold-aware ledger push must either wait out a train inside a 10-minute job or drop the
    night's slice. Dropping the slice slows the ledger's convergence, which R10-FLY-LEDGER-SAMPLE
    (batch 16, P85) paid to speed up.

Cost:
- Remedy (a): a path predicate in `merge_train.py`'s MAIN-MOVED arms, with self-test arms. It is
  refused above on soundness, whatever its size.
- Remedy (b): about 25 lines of workflow shell in the `mutation-ledger-push` job, reusing the
  record beat's hold read. It also needs a retry or carry-over of a skipped slice. That is a
  second design question with its own cost.
- No capped file is touched by this ruling.

Binding:
- **Why LOG.** The one production pull request in the instance, #3147, was delayed by one
  automatic re-proof, about 1 h, and not held. The train's bounded recovery did the work it was
  built for.
- **No figure reaches 10%.** Two recorded instances across 28 nightly pushes in the round give
  no measured share of CI time or completion time, let alone one above 10%.
- **What would re-open it.**
  - A count of train re-proofs and post-merge skips caused by `hpo-ledger[bot]` commits, over
    all train batches in a stated window, with the CI minutes each one cost. It must exceed 10%
    of train CI time or of programme completion time.
  - Or a ledger push that exhausts `--main-moved-tries` and stops a train holding a
    `custom_components/` pull request.
  - Either way, remedy (b) is the one to price; remedy (a) stays refused for ledger paths.
