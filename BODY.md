Triage batch 80 rules the orchestrator s8's slip proposal of 2026-10-31. PR #3024 published a body with a home-directory path. The first check of a body's text for host paths is `review_packet.py:427`, at dispatch, after the PR is already public. This is the next rolling batch under V182, after batch 79. It holds one ruling and one held roster op.

- **P317: ACCEPT, a carry on R10-FLY-NO-FOOTERS**, the group that already owns body-hygiene refusals at prepr.
  - `prepr.sh --body-check` applies `ref_privacy.body_refusal` to the body text and refuses. That is the step `body_push.sh:45` runs before publishing and `open_pr.sh`'s prepr step 7 runs.
  - The dispatch check at `review_packet.py:427` stays as the backstop.
  - Narrowed to that one call site: a second copy in `body_push.sh` would duplicate the check.
  - Instances: #3024 (patched live, body ref re-pushed clean at `c15dfa5a`) and #2958 (`seat-ledger.md:2325`). Two public leaks in round 10, each caught only at dispatch. The fixer measured the detector returning the home-directory refusal on the old body and None on the clean one.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`99825fff449b1a13580c8e7d5f85ac67b654d5d4`; the file is the whole diff against `18b788ac2`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P317 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch80.md#P317`: it returns None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same carry is refused: `dev/programme/triage/s6-batch80.md#P317 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.
- `ref_privacy.body_refusal` on this batch file's own text returns None.

## Figures

- `git grep -n 'body_refusal' origin/main -- tools` lists `review_packet.py:427`, `gh_comment.py:141`, `ci_probe.py:255`, `ci_probe.py:278` and the definition at `ref_privacy.py:300`. There is no call in `prepr.sh` or `body_push.sh`.
- `prepr.sh:1586` at `18b788ac2` is `vline=$(privacy_line); vr=$?`, the only privacy arm of `--body-check`.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
