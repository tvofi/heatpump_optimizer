R10-REVIEW-DISPATCH-RESIDUE part 6. Carry 25: the handoff's brief-carries check demands only the indexes the dispatch PROMPT's part line assigns. Carry 24: a later-round design reviewer is given the round, the last verdict and the diff range. Carry 10: review_strength reads a string roster model as the fixer model.

## Head

d81c7c9da4757917c2344c4d85417caf1f82f55c

## Mutation proof

Hand mutants, each applied to one file in place and restored, run against the file's own self-test at the head:

- Carry 25 drop part scope (`assigned or found or None` -> `found or None`): KILLED
- Carry 25 run end exclusive: KILLED
- Carry 25 run join (`+` runs not unioned): KILLED
- Carry 25 base text in the refusal dropped: KILLED
- Carry 25 NULL (replacement identical to the original): SURVIVED
- Carry 24 round context removed from the render: KILLED
- Carry 24 round count off by one: KILLED
- Carry 24 previous design sha read from the wrong token: KILLED
- Carry 24 verdict read narrowed back to the designer: KILLED
- Carry 10 string-model guard removed: KILLED
- Carry 10 dict key read broken: KILLED

## Round 2: the mutation-vacuous block

The first review (head 2e160c0c9b) blocked on `review_packet.py` `handoff()` lines 847-849 and 853, and on `cloud_dispatch.py` 681. Answers:

- `handoff()`'s brief-carries step is now one pure function, `brief_carries(prompt, live, body)`, returning the carries checked, the unnamed indexes and the refusal's base text; `handoff()` calls it once. The self-test drives it with a hand-spelling part line, a generated-spelling part line, each beside its null (no part line, no prompt). It also drives `handoff()` itself over stubbed edges (git, roster, dispatch prompt, hot PRs, structure): the hand-spelling prompt refuses the one unnamed assigned carry and names the part line, the generated-spelling prompt with its assigned carries named passes, and the no-prompt null falls to the live count with no base text.
- `cloud_dispatch.py` fetch: the fixture's third verdict commit is now published from a second clone, so it is absent from the dispatching clone (a `cat-file -e` check asserts that) until the fetch runs. Why the fetch target moved from the tip to the ref: a fetch by ref names an advertised ref, which every server serves and which brings the verdict commit's history for the round count (`rev-list --count`); a fetch by bare sha depends on the server allowing it. The fixture now observes the ref fetch.

Hand mutants (one text replacement per predicate, applied in a detached worktree and restored, each against the file's own `--self-test`), at head `d81c7c9da4757917c2344c4d85417caf1f82f55c`:

- c25 base predicate inverted (`if part_carries(prompt)` -> `if not ...`): was SURVIVED, now KILLED (4 failed)
- c25 base always empty: was SURVIVED, now KILLED (2 failed)
- c25 handoff ignores the prompt (`handoff_carries(None, live)`; now `brief_carries(None, ...)`): was SURVIVED, now KILLED (4 and 2 failed)
- c25 wiring of `base` into `handoff_refusals` dropped: was SURVIVED (line 853), now KILLED (1 failed)
- c25 `unnamed` dropped from the refusals call: now KILLED (2 failed)
- c24 `_git(repo_dir, "fetch", "-q", "origin", vref)` deleted (line 681): was SURVIVED, now KILLED (the absence check fails)
- NULL (identical replacement): SURVIVED, as expected

`mutant_run.py --diff <merge-base>...HEAD` per file against its own self-test (`--in-place` for review_packet, whose self-test needs a checkout): no production-line survivor remains; the survivors left are on self-test lines only (the twelve the reviewer excluded, plus the new self-test lines).

## Null control

Red at the merge base (the arms present, the fix lines reverted), then green at the head:

- `python3 tools/audit/seat/review_packet.py --self-test`: 3 `FAIL P593 brief-carries` lines without the fix; `133 checks, 0 failed` with it. Null arm: no part line demands the prompt's whole `Carry N:` set, no prompt demands the live count.
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test`: 2 FAIL (round 2 and round 3 arms) without the fix; `173 checks, 0 failed` with it. Null arm: a first round (no design-verdict ref) renders no `This is round` text and no verdict commit.
- `python3 tools/audit/seat/review_strength.py --self-test`: NameError on `fixer_of` without the fix; `117 checks, 0 failed` with it. Null arm: the dict shape reads its fixer key, an empty dict and no group read `none`.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none

## Design notes

Carry 25 extends `prompt_carries` (the existing seam) with `part_carries`, which reads both part-line spellings: the hand `This part: Carries <list> (0-based roster indexes` and the generated `Part k of N: build carries <runs>`. I did not build the roster-at-dispatch-time base (`rev-list -1 --before`): the dispatch PROMPT already holds the carries the part was dispatched with, so a carry appended later cannot be demanded; the refusal names its base as the dispatch PROMPT's part line.
Carry 24 widens the existing verdict read in `dispatch_group` to the design reviewer and adds `round_context`; no flag, no new git read beyond `rev-list --count`.
Carry 10 extracts `fixer_of` from `pr_facts` so the guard is testable.
No role or policy file is edited.
