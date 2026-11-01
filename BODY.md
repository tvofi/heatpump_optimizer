Triage batch 108 records one ruling, P366, from the orchestrator s10's queue line of 2026-11-01T22:49:17Z. The proposal: `review_carry.py` and `app_approve.sh --carry` should compare only the `+`/`-` lines of the branch's diff, so that main rewriting a context line beside the branch's hunk no longer forces a fresh review (#3147, `5bb7710c1` to `dba968f8d`). It is the rolling batch after batch 107.

- **P366: REJECT, for code files.** No carry and no roster op.
  - **It re-files P325** (`s6-batch88.md#P325`), which ruled this exact change REJECT for code files. P325's re-open trigger is at least five delta reviews of context-only code heads that found no defect in the adjacent lines. This filing cites none, and the owner's 19:50Z rule is not retroactive.
  - **It is not a deadlock.** `bus.sh dispatch` refuses a second reviewer only on CARRY. On #3147's FRESH-REVIEW it minted a nonce, and a sonnet delta reviewer was rendered at 22:51:54Z (nonce `8123b36a`). The friction is one delta review, not a blocked production merge.
  - **#3147 is the case the check exists for.** The one differing line is #3047's new guard, `or "before_reset" in snap`, in `custom_components/heatpump_optimizer/snapshots.py`. It sits in the loop whose variable the branch declares: two separately reviewed production changes, joined by a merge git resolved automatically.
  - **The `*.md` arm (P17) is unaffected.** It is R10-FLY-CARRY-DOC-CONTEXT's, built in #3077.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`6b76486514d041ec8daec7518d1788bd97ae304e`; the file is the whole diff against `0166aefd7`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P366 as `REJECT`, and a text citing `s6-batch108.md#P366` is refused: `is not an ACCEPT ruling (REJECT)`.
- With the verdict flipped to ACCEPT, it reads `ACCEPT`.
- P367 reads `None`: no such entry.

## Null control

- With the file absent, the citing text is refused: `the triage ruling dev/programme/triage/s6-batch108.md is not on the roster branch or origin/main`.

## Figures

- `python3 tools/audit/seat/review_carry.py 5bb7710c1 dba968f8d --main origin/main`: `review_carry: FRESH-REVIEW`, branch-only commits 1, the merge.
- The normalised diffs differ in 1 line, and the `-U0` `+`/`-` comparison is equal.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
