Triage batch 120 records two rulings on the orchestrator's queue lines of 2026-11-04, filed as P375 and P376 and numbered P384 and P385 because those numbers already name rulings on main.

- **P384: REJECT.** A tracked change to `train.sh`'s venv resolution costs a fly-in against a refusal that names its own path. The orchestrator's one local symlink answers it for every instrument.
- **P385: ACCEPT, narrowed.** One carry on R10-HANDOFF-PATH gives the relay a retry for an update refusal that clears without a ref moving. The filed key is refused: it would have blocked the 22 of 45 updates this retry got through.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. The carry is held for the orchestrator to route through `roster_edit.py` once this file is on the roster branch or main.

Repair of the block `citation-wrong` (verdict at 1570415e): P385 cited R10-HANDOFF-PATH carries by wrong number. Checked against `origin/handoff/audit-r10-roster` (11 carries): the key text and the "unrecoverable" count are carry 9 (carry 8 is the P362 `pr_tools_fresh` carry), and the driver `driver4.py` is carry 6 (carry 5 is the #3052 `max_class_loc` carry). Every occurrence, including the "Carry text for R10-HANDOFF-PATH" block, now reads 9 or 6. Carry 9 already says "Only content refusals (prepr REFUSE) stay recorded failed"; the carry text now states it narrows that sentence by splitting body-content from retryable steps, so a fixer does not read two rules.

## Head

`bf46fd683897a914814f98226a5c85abf6c7130f` is the authored code head; it adds one commit, the citation repair, to `03ed7434fb34145ab43649b91a2354fbc21f040e`. The delivery row `dev/programme/delivery/3210.md` is carried by the PR branch.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P385 `ACCEPT`, and its carry text is not refused.
- With that verdict flipped to DEFER, the citing text is refused: `is not an ACCEPT ruling (DEFER)`.
- P384 reads `REJECT`, and a text citing it is refused: `is not an ACCEPT ruling (REJECT)`.

## Null control

- P386 reads `None`: no such entry.
- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch120.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e...bf46fd683897a914814f98226a5c85abf6c7130f`: 1 file, 151 insertions.
- The rulings' figures are cited beside their sources in their `Instances:`.
- No capped file is touched; the diff is one markdown file.
- Toolchain: numpy 2.5.4 and scipy 1.18.1 match the lock; `tests/entities.py` could not run in this environment (venv-ha lacks scipy and paho), so CI is the authority.

## Red checks

Read at the previous PR head `1570415e`, not at the repaired head, which has no runs yet: `governance`, `governance / delivery-status`, `governance / instrument-self-tests`, `tests / record-autofix`, `tests / ci-ratchet`, `tests / closures-autofix`, `tests / fast (3.14)`, `tests / nightly-status` and `tests / replay`. At that head the runs listed were pending, skipped, cancelled by a newer run, or green (`fast (3.14)` succeeded; only `nightly-status` and the cancelled `gate` ended unsuccessful), and none reads this diff, which is one markdown file. Cheaper detector: none exists for a stale pending state, since the lint reads the head's checks before the new head has any; the answer is that these are the old head's states and the new head's CI is the authority. The citation fix itself was checked against the roster branch's JSON, not by a CI check.

## Forward-carry

none

## Friction

none
