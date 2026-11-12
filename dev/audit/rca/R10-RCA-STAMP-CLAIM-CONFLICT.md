# R10-RCA-STAMP-CLAIM-CONFLICT: a release stamp makes every branch that added a claim unmergeable

Root-cause seat `r10-rca-stamp-claim-conflict`, `root-cause.md`, 2026-11-08, from
`origin/main` `72940b795` (the stamp is `2a3c05644`, `v7.1.6`). Nothing was fixed,
no `custom_components/` file was touched, and the countermeasure in section 5 is a
proposal: it changes `claim-files.md`, so it waits for the owner's approving review.
Durations are estimates and are marked as such; counts come from the commands shown.

**Trigger.** The same shape, three times in one stamp (#3297, #3299, #3308), and
earlier stamps before it (section 2): the audit-class barrier rule applies, so a
barrier is owed or the owner is asked.

## 1. Named cause

`stamp.py` empties both claim files and moves `claims-for:` (`rewrite_claims`,
`stamp.py:686-728`: "every bare claim line is deleted"). A branch forked before the
stamp carries the old stamp and, as its base, the old claim lines. `claimnotes`
(`env_drift.py`, `merge_claim_decision`) calls a side "changed" when its parsed claim
map differs from the base's. The stamp's emptying is therefore a **change** whenever
the base held any claim line, and a branch that added a claim is a change too:

    both_changed = base_map not in (our_map, their_map) and our_map != their_map
    if both_changed and _parse_claims(ours)[0] != _parse_claims(theirs)[0]: return None, []

The second line is a blanket refusal that never reaches the per-scenario rule
(`_decide_per_key`), which would resolve this case correctly: a base line the branch
left alone takes main's deletion, a scenario only the branch added stays.

**A branch that only ADDED one claim line is refused**, reproduced at the stamp's
parent `2a3c05644^` with a one-line append to `claimed_drift.txt`:

    git merge-tree --write-tree 2a3c05644 <branch>
    MERGE-CLAIM: refused tests/golden/claimed_drift.txt
    CONFLICTING CLAIMS: both sides changed claims under different ...

The conditions are exactly two: the base held a claim line (merged PRs add them, the
stamp deletes them) and the branch added or edited a claim. Null controls, same
commands: a branch that touches no claim file merges clean; a branch forked at the tag
`v7.1.5`, whose base held no claim line, **resolves** (`MERGE-CLAIM: resolved`) although
8 commits touched the claim files between that tag and the stamp
(`git log --oneline v7.1.5..2a3c05644 -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt | wc -l`),
so the trigger is the base's content, not the version gap. A stamp that changes only the
header (`7.0.2`, `7.0.4`, `7.1.4`, `7.1.5`) cannot trigger it.

Who moved: the guard (`111d1f92c`, `76cd77cb0`, 2026-11-01) was written for two
branches' claims "from different releases"; the stamp's own design already says "the
next branch restates its own footprint" (`stamp.py:117-121`) and never gave the
branch an automatic way to do it. The driver treats the restatement as a conflict.

**Wider than the named cause.** Other files the stamp rewrites (`VERSION`, manifest,
`CARD_VERSION` in the card, `claims.md` row C42, the `RELEASE_NOTES.md` heading) are lines
a branch is forbidden to touch (`CLAUDE.md` rule 4), so they cannot conflict. The claim
files are the only stamp-rewritten file a branch is **required** to edit. `merge_main_bot`
relays the refusal (`skip-driver-refused`) and cannot repair it.

## 2. Process state: (a) the process did not exist

No step of the release path handles the stamp meeting an open branch's claims, and no
test combines the two:

- `tools/release/stamp.py` and `tools/` contain no code that re-stamps open branches'
  claims (searched for `claims-for`, `restamp`).
- The driver's refusal test, `tests/entities.py:23214-23226` ("claims both sides
  changed under different claims-for stamps are refused"), uses `_CM_BASE`
  (`entities.py:23051-23059`), which has no claim line, and a branch/main pair
  that both **add**; no test applies `rewrite_claims` output to a base with
  claims and merges a branch into it.
- It is not (b): the rules were obeyed (the driver refused as written). It is not (c): the
  refusal was the intended result for different-release claims; the stamp-emptied base
  is a case the guard's author did not model. It is not (d): the stamp emptied claims
  before the guard was written (the table below has the stamp conflict at `v6.7.13`,
  2026-10-01, a month before the guard of 2026-11-01), so no precondition changed.

Past occurrences (`git log --grep`, merge-commit bodies):

| stamp | evidence |
|---|---|
| v6.7.13 | `8f30964ff`: "The stamp emptied main's card claims ... restates this branch's 39 R9-UX-1 claims" |
| v6.7.17 | `45c04b7d6`: "the claimnotes driver refused it. Resolved as main's file ... plus this branch's six R9-UX-9 claims"; `f6d28bb76`; verdict `7f4dbaddb`: "claimed_drift.txt MERGE-CLAIM refused" |
| v7.1.0 | `7790838ea`; `7f181fef8`: "the claimnotes driver refused because both sides wrote bare claims" |
| v7.1.6 | `68b0735be` (#3297): "Took main's files byte-identical and re-appended only this branch's ... claims"; #3299 and #3308 refused the same way |

Which gate could have caught it: `D11` (governance mechanisms) and `D3` (test gaps)
audit the driver; neither has a finding on the stamp-versus-branch pairing, and the
shipping tests above do not exercise it. This is the first RCA on the shape.

## 3. How far the class reaches

Open pull-request heads at `origin/main` `72940b795`, tested with
`git merge-tree --write-tree origin/main <head>` for each of the 21 heads numbered 3240 or
above that are not merged: the claim files differ from their merge base in 4 (#3297,
#3299, #3308, #3315); #3297, #3299 and #3308 print the refusal (all carry
`claims-for: 7.1.5`); #3315 does not (it is already stamped 7.1.6) and #3305 touches no claim file. Branches without a pull-request ref (about 480 `fix/*` and
`handoff/*` heads) were not enumerated. The shape elsewhere (a file the stamp rewrites
and a branch must edit) found nothing else (section 1).

## 4. Cost test

Measured: 12 stamps from `v7.0.0` to `v7.1.6` in 25 days, 8 of which deleted claim
lines (`git show --stat <stamp> -- tests/golden/*claimed_drift.txt`: `v7.0.0`, `v7.0.1`,
`v7.0.3`, `v7.0.5`, `v7.1.0`, `v7.1.1`, `v7.1.3`, `v7.1.6`). Branches refused per stamp: 3 at
`v7.1.6`, at least 2 at `v7.1.0`, 3 at `v6.7.17`, at least 1 at `v6.7.13`; the other
stamps were not counted (no record), so the mean below is a floor over the counted four.

    cost(defect) = refused branches x (conflict-resolution fixer round + delta review)

A round is about 30 to 60 minutes of an opus fixer plus 20 to 30 of review: **estimate
about 1 h per branch**, not measured. At the counted mean of 2.25 branches per
claim-deleting stamp and 8 such stamps in 25 days: about 18 h of seat time per 25 days
(estimate, ~0.7 h per day), plus the branches' wait.

    cost(countermeasure, recurring) = 0 s on every run

The proposed rule runs only inside the merge driver, only when both sides changed claims
under different stamps; one tuple comparison. The standing complexity cost is about 15
lines in `env_drift.py`, one test and one mutant case (section 5).

Verdict: 0 < 18 h x P(recurrence), and P(recurrence) is 1 per claim-deleting stamp
(4 of 4 counted). **Build it**, behind the owner's approval of the `claim-files.md`
sentence.

## 5. Countermeasure (proposed, addresses state (a))

Narrow the blanket stamp refusal in `merge_claim_decision`: when the stamps differ and
**the side with the newer stamp carries no claim line** (a release stamp's shape), fall
through to `_decide_per_key` instead of refusing. That rule decides each scenario:
a base line the branch left alone takes the stamp's deletion, a scenario only the
branch added stays, a base line the branch **edited** against the stamp's deletion is
still refused, and the stamp key goes to the bumped side. If the newer side holds claims
(a claim merged after the stamp) the refusal stands. The prototype, applied to a scratch
worktree of `origin/main`, not landed:

```python
def _release_stamp_side(ours, theirs, our_map, their_map) -> bool:
    def key(text):
        stamp = _parse_claims(text)[0] or ""
        return tuple(int(p) for p in stamp.split(".") if p.isdigit())
    ours_key, theirs_key = key(ours), key(theirs)
    if not ours_key or not theirs_key or ours_key == theirs_key:
        return False
    return not (their_map if theirs_key > ours_key else our_map)
# in merge_claim_decision:
#   if both_changed and stamps differ and not _release_stamp_side(...): return None, []
```

**Demonstration, both runs.** `git merge-tree --write-tree origin/main <head>` with the
driver configured, unpatched then patched:

| head | unpatched | patched |
|---|---|---|
| #3299 `d7d4c511b` | `MERGE-CLAIM: refused` | `MERGE-CLAIM: resolved`; result is `claims-for: 7.1.6` plus the branch's one `config_flow` claim, the 7.1.5 lines gone |
| #3308 `fb5658f13` | refused | resolved |
| #3297 `2d010b091` | refused | still refused, correctly: the head is a hand-merge whose `coord_*` scenarios it deleted and main has since claimed again (a genuine per-scenario clash) |

Null controls, `merge_claim_file(base, ours, theirs)` on synthetic files: a branch that
edited a line the stamp deleted -> refused; the stamp side carrying a claim
(`c # R3: z`) while the branch added `b` -> refused; unpatched, the plain case ->
refused (`None`). So the patch does not go green by skipping: it relaxes one case.

**What it still owes before landing** (not done here): the test in `tests/entities.py`
with a base that holds claims and `rewrite_claims` output as main; a case in
`dev/audit/harnesses/claim_merge_mutants.py` (the 76cd77cb0 harness) killing the
newer-side-empty condition; the `claim-files.md` sentence "claims from different releases
refuse" narrowed to say a stamp-emptied side does not; the ratchet metrics and
`tests/closures.json` recorded. The owner decides the sentence. Rejected alternatives:
a stamp step that rewrites open branches (it would write to other seats' branches; CLAUDE.md names who authors pull requests and
this seat found no sanctioned path for the stamp to do so); a stamp-time `claims-for:` that stays at the old
release (breaks `STALE CLAIM FILE`, the check that exists to pin the claim to its release).

Carry: dismissed: proposal for the owner, no stage brief changes before approval.
