Triage batch 120 records two rulings on the orchestrator's queue lines of 2026-11-04, filed as P375 and P376 and numbered P384 and P385 because those numbers already name rulings on main.

- **P384: REJECT.** A tracked change to `train.sh`'s venv resolution costs a fly-in against a refusal that names its own path. The orchestrator's one local symlink answers it for every instrument.
- **P385: ACCEPT, narrowed.** One carry on R10-HANDOFF-PATH gives the relay a retry for an update refusal that clears without a ref moving. The filed key is refused: it would have blocked the 22 of 45 updates this retry got through.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. The carry is held for the orchestrator to route through `roster_edit.py` once this file is on the roster branch or main.

## Head

`03ed7434fb34145ab43649b91a2354fbc21f040e`; the one file is the whole diff against `2a9cd3476`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P385 `ACCEPT`, and its carry text is not refused.
- With that verdict flipped to DEFER, the citing text is refused: `is not an ACCEPT ruling (DEFER)`.
- P384 reads `REJECT`, and a text citing it is refused: `is not an ACCEPT ruling (REJECT)`.

## Null control

- P386 reads `None`: no such entry.
- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch120.md is not on the roster branch or origin/main`.

## Figures

- `git diff --stat 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e...03ed7434fb34145ab43649b91a2354fbc21f040e`: 1 file, 149 insertions.
- The rulings' figures are cited beside their sources in their `Instances:`.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
