# Proposal triage, session s10, batch 108 (P366)

The rolling batch after batch 107. Facts were read at origin/main `0166aefd7`, at the round's
roster branch `origin/handoff/audit-r10-roster` (`f2d9626b4`), at pull request #3147's verdict head
`5bb7710c1` and live head `dba968f8d`, at #3077's head `aa6148d4f`, and in the session's seat
ledger.

## P366: `review_carry` refuses a carry when main rewrote a context line of the branch's hunk

Verdict: REJECT, for code files. It re-files P325 (`s6-batch88.md#P325`), which ruled this exact
change REJECT for code files and named a re-open trigger that this filing does not meet. The
`*.md` arm stays the work of R10-FLY-CARRY-DOC-CONTEXT (P17), built in #3077.

Source: the orchestrator s10's queue line of 2026-11-01T22:49:17Z. It proposes comparing only the
`+`/`-` lines, and it calls the proposal "owner-ruled accept-class per deadlock rule".

Instances:
- **#3147, R10-DEPS-PIP-BUMP, a production pull request.** It touches
  `custom_components/heatpump_optimizer/learner_progress.py` and `snapshots.py`.
  - The merge verdict is at `5bb7710c1`. The live head `dba968f8d` is one merge of origin/main,
    with no commit of the branch's own.
  - `python3 tools/audit/seat/review_carry.py 5bb7710c1 dba968f8d --main origin/main` prints
    `why: the branch's own diff differs` and `review_carry: FRESH-REVIEW`.
  - The normalised diffs (`index` lines and `@@` headers dropped, as `carry()`'s `norm()` reads
    them) differ in exactly one line, a context line in `snapshots.py`:
    `if not snap.get("healthy"):` became `if not snap.get("healthy") or "before_reset" in snap:`.
  - Compared over `+`/`-` lines only (`-U0`), the two diffs are equal.
  - The line main wrote is #3047's (R10-FACTORY-RESET, `404117b99`, merged as `f04b25a00`). The
    branch's added lines are a type declaration on the loop variable that #3047's guard sits
    inside: two production changes, each reviewed alone, next to each other.
- **It is not a deadlock.** `tools/audit/seat/bus.sh` lines 503-516 refuse a second reviewer only
  when `review_carry.py` prints CARRY. On FRESH-REVIEW, dispatch mints a nonce.
  - The seat ledger at 22:51:54Z records exactly that: dispatch s10e rendered a sonnet delta
    reviewer for #3147 at `dba968f8d` (nonce `8123b36a`).
  - The 19:50Z owner rule makes "blocks a production merge" the condition for an ACCEPT. Here it
    holds only as a delay of one delta review, not as a block. P365 was a block, because no
    path existed short of an override.
- **P325 measured this class.** Over merged pull requests since 2026-10-17, 9 heads were
  context-only, all before 2026-10-24. #3014 (2026-10-31) was the tenth. #3147 is the eleventh, and
  the first in a production file.

Cost:
- As filed it is S: `norm()` in `tools/pr/app_approve.sh` reads `-U0` and keeps only the `diff`,
  `+` and `-` lines. The self-test arm `NO CARRY: a merge from main that changed a context line of
  the branch's hunk` flips. `review_carry.py`'s docstring, which names that case FRESH-REVIEW,
  changes with it.
- **The binding cost is the review coverage.** The context comparison is the one check that sends a
  reviewer to main's code written beside the branch's code. #3147 is that shape in production code:
  a merge git resolves automatically puts two separately reviewed changes in one loop.
- **The benefit is one delta review per instance, about 20 minutes on sonnet.** That is about one a
  week by P325's count; #3147 is the first since #3014.
- The relocation guards do not depend on context. A hand-resolved merge is refused as "not the
  automatic merge", and a `ci:` commit is refused outside the driver files (self-test arms at
  `app_approve.sh` lines 1568 and 1580). Neither the gain nor the loss above includes them.

Binding:
- **Why REJECT.** P325 stands: the owner's 19:50Z rule is not retroactive. Its re-open trigger is
  "delta reviews of context-only code heads that found no defect in the adjacent lines, across at
  least 5 such heads". This filing cites none. The trade is the one P325 found marginal, and
  #3147 makes the lost check concrete, because the adjacency is in production code.
- **What counts toward re-opening.** #3147's r2 delta review (nonce `8123b36a`), if it finds no
  defect in the adjacent lines, is the first head toward P325's five. #3014's delta review, if it
  found none, is a second. A later filing that lists five such verdicts re-opens P325 for code
  files on its merits.
- **No carry, no roster op.** The `*.md` relaxation (P17) is R10-FLY-CARRY-DOC-CONTEXT's, built in
  #3077 (`norm()` blanks a `*.md` file's context lines and keeps code context, citing P325).
