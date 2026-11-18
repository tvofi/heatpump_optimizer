# Proposal triage, session s14, batch 170 (P585, P586)

This batch rules two process proposals filed by seat s14-12 on 2026-11-11, both about PR 3425.

Sources:
- origin/main `a7628041dc`. Every line number below is at that commit.
- The tick-loop log of the orchestrator's state directory (22183 lines at the time of ruling),
  its `cloud-relayed.refused` ledger, and the check-runs API for the heads named.

## P585: PENDING-CI-RED-TERMINAL

Verdict: ACCEPT, re-pointed, as a carry on R10-REVIEW-DISPATCH-RESIDUE (stage in-progress,
severity medium; it owns `tools/audit/seat/cloud_relay.sh` and `tools/audit/seat/review_carry.py`).
The fixer builds it with that group's P576 carry, which edits the same arm. The proposed arm
itself is REJECTED as a duplicate: P576 (batch 162) already carries it word for word.

Source: the proposal queue, s14-12, 2026-11-11 ("cloud_relay pending-ci draft is refused once a
main merge moves the head ... PR 3425").

Instances:
- **The proposed mechanism never fired.** `grep -c "head moved under a pending-ci"` over the
  tick-loop log, `cloud-relay.log` and `cloud-relayed.refused-why` gives 0 in each. The die that
  message belongs to is `cloud_relay.sh:268`. Had the claim been true, at least PR 3425's line
  would have matched.
- **What did fire is the RED arm, `cloud_relay.sh:273`.** `grep -n "pending-ci draft is not
  posted"` gives two refusals, and these are all of them:
  - **PR 3425.** At 04:39Z its draft (`probe/rev-3425-5c9958ba`, verdict `8e4b9d262c`,
    `Fix review: merge c6becb3175`) was HELD (classify WAIT). At 04:49Z it was REFUSED with
    "CI is red at c6becb3175 (classify RED)" (tick-loop line 21910). The failing check-runs at
    c6becb3175 were `gate`, `pr-contract / pr-contract` and `governance / instrument-self-tests`.
    The `gate` failures print only `FAIL pr-contract / pr-contract: failure`. The pr-contract job
    (130328018313) died in `carry_audit.py` with `AttributeError: module 'roster_lib' has no
    attribute 'carry_receivable'`. That is a version skew: main's `carry_audit.py` calls a
    function main added on 2026-11-10 (`e08425e904`), after the branch's merge base `d08ed31049`.
    The branch's diff (`git diff d08ed31049...c6becb3175 --stat`, 9 files) touches neither file.
    The third red is main's own (P584). The fixer's main merge at 05:54Z (`c93903f075`) cured the
    skew: `gate` and pr-contract are green there (06:54Z-07:05Z). `review_carry.py c6becb3175
    c93903f075 --verdict-only` answers `CARRY` (rc 0).
  - **PR 3430.** Its draft (`probe/rev-3430-6a421a63`, verdict `58b7ef6110`) was HELD at tick-loop
    line 22140, then REFUSED at line 22161 over a red at `ba0ed526cc`. Two check-runs were red
    there. `gate` (job 130351017244, 05:52Z) printed `run(s) [42968003278] at this head are still
    being judged; their gate decides`. `tests / nightly-status` is main's nightly and is not
    required. A later `gate` at the same head is green (06:41Z), with no new commit.
- **Both drafts are stranded.** `cloud_relay.sh:371` appends the refused pair to
  `cloud-relayed.refused`, and line 343 skips any pair already listed there. Both pairs are in
  the ledger (`grep -c 'rev-3425\|rev-3430'` gives 2). The log has no line for #3425 after line
  21910, and none for #3430 after line 22161. The refusal text says "the PR goes back to its
  fixer", but nothing sent it back. Both PRs are open with no review at the current head
  (`gh pr view 3425 --json reviews` is empty).
- **P576's fix as written would cure neither.** It keeps "RED at the live head still refuses".
  It also only acts on a moved head, and both drafts were refused before any head moved.

Cost:
- **Benefit.** 2 of 2 RED-arm refusals in the log (100%) were reds that cleared with no fixer
  work. Each costs a second reviewer turn (the group's opus reviewer) and leaves the PR waiting
  until someone notices, 2 h or more in both cases.
- **Fix.** One arm in `cloud_relay.sh` (about 10 lines), next to the lines P576 already edits,
  plus three self-test checks that reuse the classify stubs at lines 1183-1205. API cost is one
  extra classify per held draft per relay pass, the same as WAIT's today.
- **Gate.** No capped file is new, and no new file is added. The group's severity is medium, so
  the machinery bar does not apply.

Binding: a terminal refusal of a draft whose head still has the review's answer wastes a full
opus review each time. This is the arm that has fired, while the proposed one has not.

Rule per instance:
- **RED on a pending-ci draft holds the draft, like WAIT.** It returns 75 and prints one
  `HELD-PENDING-CI-RED #<pr> <head>: <red contexts> (classify RED)` line per pass. It refuses
  only on one of two conditions:
  - the PR's head moves to a head where `review_carry` does not answer CARRY (P576's arm);
  - the head has read RED with no check still running for 6 h since the first RED read.
    The first RED read is recorded in the state dir and keyed `<ref> <sha> <head>`.
- **On the final refusal, print an OWED line naming the PR.** It reads `cloud_relay: OWED
  re-dispatch #<pr> <head>` and replaces the claim that the PR goes back to its fixer, which no
  code carries out.
- **Run against the two instances, result beside each:**
  - PR 3425: RED at 04:49Z is held. At the next pass after 05:54Z the head has moved, and P576's
    arm runs `review_carry` (CARRY). After 06:56Z classify reads `c93903f075` with `gate` green.
    `instrument-self-tests` is red on main too, and `nightly-status` is not required. The draft
    posts, and no second review is needed.
  - PR 3430: RED at its refusal pass is held. At 06:41Z the same head reads `gate` green and the
    draft posts. It was held for under 1 h, inside the 6 h bound.
- **Self-test.** RED, then GREEN at the same head, posts. RED for longer than the bound refuses
  and prints the OWED line. As a null control, WAIT behaves as it does today. A mutant that
  restores the die at line 273 makes the first check fail.

## P586: CARRY-FOLD-PR-SPELLING

Verdict: REJECT. The claimed mechanism does not exist. The PR's spelling never changes the
answer, and the 1-versus-0 the proposer saw comes from two different inputs, not from the
spelling.

Source: the proposal queue, s14-12, 2026-11-11 ("carry_fold.py --pr 3425 (no #) reports 0 missing
while carry_audit landed --pr '#3425' reports 1 ... PR 3425").

Instances:
- **Replay on the roster from before the carry landed.** The carry is `From #3425, body item
  09380b99`, and it landed on the round roster at `d611071d86` (04:40Z). The replay ran against
  that commit's parent, with PR 3425's current body.
  - `carry_audit.py --roster-ref <it> landed` and `carry_fold.py --roster-ref <it>` were each run
    with `--pr '#3425'` and with `--pr 3425`, each with and without `--topic r10-tick-residue`.
  - All 8 runs agree between the two spellings. landed gives `CARRY-LANDED: 0 missing` every
    time, adding a `CARRY-STATUS` line when the topic is given. fold gives `0 item(s) folded`.
  - On the current roster, landed with `--roster-ref origin/main` and with the round roster gives
    `0 missing` for both spellings.
  - Had the claim been true, the bare-number runs would have differed from the `#` runs in at
    least one of these pairs.
- **The code agrees.** A bare number reaches `own_group` (`carry_audit.py:601-609`), which skips
  `#`-prefixed tokens and resolves bare ones through `pr_group_of`. `own_group(dests, ['3425'])`
  and `own_group(dests, ['#3425'])` both return `None`. Only the topic resolves
  (`R10-TICK-RESIDUE`). In the source-token match, a bare `3425` cannot equal the whole token
  `#3425`. So a bare number could only report more items missing, never fewer.
- **Where the 1 came from.** At 03:37Z the bus ran `carry_audit.py --roster-ref origin/main
  landed --pr "#3425"` with no `--topic` (`bus.sh:236-237`). It printed `CARRY-LANDED: 1 missing`
  (tick-loop lines 21767-21768). That was an hour before the carry landed at 04:40Z. A fold run
  after 04:40Z correctly finds nothing to write.

Cost: normalising or refusing the argument means code in two tools for a behaviour that measures
identical. It would buy nothing.

Binding: an unreproduced claim. 0 of 8 replays differ. If a later instance shows two runs at the
same roster ref and body, differing only in spelling, that reopens it.
