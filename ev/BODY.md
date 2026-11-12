R10-REVIEW-DISPATCH-RESIDUE part 4: review_packet.py no longer refuses a finished body because the roster grew after dispatch, checks carries 0-based, accepts the round-roster landing shape, and defers a required-gate red to classify's WAIT/GREEN read.

## Head

95ad6344e2c5507975b6c154d04065be4ecce059

## Mutation proof

Reviewer-style mutants, each applied by hand to `tools/audit/seat/review_packet.py` at the head, `python3 tools/audit/seat/review_packet.py --self-test` run, file restored (output of that loop, /tmp/mut.out):

- Carry 15: `C15-range-1-based: KILLED (5 failing checks)`; `C15-live-roster-count: KILLED (1 failing checks)`
- Carry 16: `C16-round-scope-dropped: KILLED (1 failing checks)`; `C16-snapshot-not-ancestor-of-tip: KILLED (2 failing checks)`; `C16-snapshot-not-in-head: KILLED (1 failing checks)`
- Carries 18/19: `C19-wait-green-condition-dropped: KILLED (2 failing checks)`; `C19-required-scope-dropped: KILLED (1 failing checks)`
- Carry 4: `bash tools/audit/seat/body_patch.sh --self-test` prints `ok   MUTANT --commits-file dropped: the Dependabot arm no longer passes the list (the dep arm catches it)`.

## Null control

`NULL-docstring-edit: SURVIVED (0 failing checks)` (same loop, a docstring word changed). Self-test null cases: no dispatch PROMPT falls to the live count and a body missing a live carry is refused; a non-round topic with the 3377 shape is refused as today (#2887); `tests / fast` red beside a WAIT read still refuses red-unanswered; a RED or APPROVAL-OWED read keeps the refusal; `body_patch.sh` gives a non-Dependabot pull request no `--commits-file`.

## Figures

- `python3 tools/audit/seat/review_packet.py --self-test | tail -1` -> `review_packet self-test: 108 checks, 0 failed`
- `bash tools/audit/seat/body_patch.sh --self-test | tail -1` -> `body_patch self-test: 109 checks, 0 failed`
- `tools/pr/prepr.sh` at 95ad6344e2c5507975b6c154d04065be4ecce059: EXIT 0 (agreement lane first refused my sha regex as a duplicate of merge_throughput.py's grammar; respelled, commit "spell the snapshot-sha grammar apart", then clean).
- `git log --format=%B a7628041dc..HEAD | grep -ci 'claude\|co-authored\|session'` -> 0.

Carry 4: already built at the base by d0f91346bd (`body_patch.sh` reads the PR's commit list and passes `--commits-file` for a Dependabot PR, the first of the carry's two sufficient fixes, markers `mut:commitlist`/`mut:commitsarg`); no edit here, its self-test cases and mutant are quoted above. The review_packet head-note arm is not changed: once the body is patched the head-note check passes unchanged.

Carry 15: `unnamed_carries` counts 0-based (carry 0 checked, carry n never demanded); `handoff` takes the `Carry N:` indexes of `dispatch/fixer-<topic>`'s PROMPT.md (`dispatch_prompt`, `prompt_carries`, `handoff_carries`), else the live roster count. The "else a roster sha the dispatch records" middle arm is not built: the dispatch records none, so the live roster is the only fallback. Self-test: a body naming Carry 0..20 passes with a 21-carry PROMPT and 27 live; a body missing Carry 0 is refused.

Carry 16: `handoff_not_applied` returns (refusal, advisory); for the roster branch `roster_lib.round_ref` names only, a head holding a sha its `## Head` names that is an ancestor of the tip is accepted with the advisory `roster snapshot <sha>, N commits behind handoff/<t>; a later landing takes the rest`. Every other topic keeps today's rule.

Carry 18: dismissed as superseded by Carry 19 (the same change; built once, below). Carry: dismissed: superseded by carry 19.

Carry 19: built on the already gathered `required_read` (no second classify call): a `REQUIRED` red-unanswered entry is not refused when the read is WAIT or GREEN, its required-wait/green advisory names it; RED, APPROVAL-OWED, an absent read, and a red outside `REQUIRED` keep the refusal.

## Red checks

none

## Forward-carry

none

## Friction

none
