# Proposal triage, session s14, batch 162 (P575, P576)

This batch rules `s7/triage-queue-s7.txt` lines 257 and 258. The bar and the denominators are batch
141's.

Sources:
- origin/main `dbd1ab5b07`. Every line number below is at that commit.
- The refs named below, read with `git ls-remote` and fetched at 04:50Z.
- The roster at `origin/handoff/audit-r10-roster` (943eb224e8).
- Batch 142 (P546).
- No GitHub API calls.

## P575: DISPOSE-NEVER-CLEARS-BOARD

Verdict: ACCEPT for one new arm, (a2): an empty net diff counts as landed. The rest is ruled as
follows:
- (a1), "orphans honours a disposition", is already ACCEPTED as P546. Its carry is
  R10-REVIEW-DISPATCH-RESIDUE carry 13, not yet started.
- (b)'s "dispose accepts handoff-wip" is also already in that carry.
- (b)'s "blocked-stop clears when the handoff or PR head is newer" is REJECTED. Measured, it
  clears none of the three stops it names.

Source: queue line 257 (2026-11-11T04:40:52Z, orchestrator s14; the disposal seat's files are in
`s14/seat/dispose-0440/`).

Instances:
- **(a2) The empty-diff handoff.** `handoff/r10-body-contract-p3-bootstrap` is at cdad1183b2.
  - `git diff --name-only origin/main...origin/handoff/r10-body-contract-p3-bootstrap | wc -l`
    gives 0.
  - `git cherry origin/main <ref>` gives three `+` commits: 89eebbea23, 720eba4fe5 and 0f80f87095.
  - So no ancestry test can land it. Its commits are not on main, and the add-then-remove pair
    has no patch-id twin there.
  - The content arm should land it but does not. `ledger.py` `covered()` (line 383) diffs
    merge-base..tip and, at line 393, returns False when that diff is empty
    (`if rc or not names.strip(): return False`).
  - `reverse_applies` has no patch to apply either. So `landed()` (line 464) returns None, and
    `bus.sh orphans` (header lines 50-62: "the one classifier") prints the tip STRANDED on every
    pass.
  - The queue line says it has stood 30 h and has been disposed 5 times.
- **(a1) The dispositions are already ruled.** P546 (batch 142) ordered that the carry-fold arm and
  `bus.sh orphans` skip a tip disposed at that sha, and that `dispose()` accept `handoff-wip/`.
  - That is R10-REVIEW-DISPATCH-RESIDUE carry 13 (roster 943eb224e8). The group is not started,
    with 20 carries.
  - This queue line is a further instance of P546, not a new class.
- **(b) Would "head newer than BLOCKED" clear the three stops? No: 0 of 3.** For each topic,
  committer times are compared (`git log -1 --format=%cI`):

  | topic | handoff-wip (BLOCKED) | handoff/ | dispatch/fixer- | BLOCKED in handoff ancestry |
  |---|---|---|---|---|
  | r10-dependabot-3414-compat | 00:59:24Z | 00:40:06Z | 00:26:11Z | no |
  | r10-rca-dependabot-stale-hash | 01:58:18Z | 01:34:31Z | 01:23:37Z | no |
  | r10-hotfix-nonrequired-reds-2 | 11-10 11:38:28Z | 11-10 11:07:45Z | 11-10 11:01:46Z | no |

  - In all three, the BLOCKED commit came after the topic's handoff and dispatch.
  - `orchestrator_tick.py` `blocked_stops` (lines 955-972) already clears a stop on a newer
    dispatch or a disposition at its sha. A newer-head rule adds a third reader that would match
    nothing here.
  - Only P546's `handoff-wip` dispose clears them.

Cost:
- **(a2) `covered()` returns True on an empty merge-base..tip diff when the diff itself read
  cleanly (rc 0).**
  - A tip whose net change is nothing gives main nothing to receive.
  - `landed()` should name the reason, for example `empty`, as its own branch before `content`, so
    the level and orphans lines say why.
  - `rc != 0` stays False.
  - About 3 lines in `tools/audit/seat/ledger.py`.
  - Self-test arms:
    - the add-then-remove shape (two commits, net empty) lands as `empty`;
    - mutant: drop the branch, and it is STRANDED again;
    - null control: a tip with one real uncovered line stays None.
- `ledger.py` has no row in `tests/structure_budgets.json` (`grep -c 'seat/ledger.py'` gives 0).
- No new file or check.

Binding:
- One wrong classifier keeps a dead OWED line on the board indefinitely. Each sweep must act on
  it, and each disposal seat re-disposes it: 5 times so far.
- The fix is three lines in the one shared classifier, which `bus.sh orphans` and the relay's level
  both read. Both are corrected at once.
- **The newer-head arm is REJECTED.** It would add a rule that matches 0 of the 3 instances it was
  proposed for.

Routing:
- (a2) is one carry to R10-REVIEW-DISPATCH-RESIDUE, to build with its P546 carry 13, which changes
  the same orphan arm.
  - `ledger.py` is not in that group's files. No open group owns it: R10-LEDGER-RESIDUE and
    R10-TICK-LEVELS are done.
  - The carry names `tools/audit/seat/ledger.py`. The group is not started, so P551's five-carry
    split applies at dispatch.
- Interim, the orchestrator's call: deleting the three `handoff-wip/` refs clears the three
  blocked-stop lines today, as the queue line notes.

## P576: PENDING-CI-RED-DEADLOCK

Verdict: ACCEPT. A pending-ci draft whose head moved is posted when `review_carry.py` answers
CARRY for drafted-head..live-head and classify then reads the live head GREEN. The RED refusal is
unchanged.

Source: queue line 258 (2026-11-11T04:43:53Z, orchestrator s14; PR 3419, comment 6787235865).

Instances:
- **The two refusals.** In `cloud_relay.sh`'s pending-ci block (lines 259-275):
  - line 268 dies when the live head differs from the drafted head ("the head moved under a
    pending-ci draft");
  - line 273 dies on classify RED ("the PR goes back to its fixer").
  - A red that the branch did not cause, and that only a main merge cures, hits 273 before the
    cure and 268 after it. No path posts the verdict without re-dispatching a reviewer.
- **The relay already has the rule for a moved head**, on the other path.
  - Line 405 calls `review_carry.py <handoff-head> <pr-head> --verdict-only` and relays a verdict
    across a range it answers CARRY.
  - `review_carry.py`'s header holds the owner's ruling (tvofi, 2026-10-27): "if there are no code
    changes, the previous review can be carried". A git automatic merge of main is in its CARRY
    set.
  - The pending-ci path alone ignores it.
- **Count.** One measured: PR 3419, where the P572 grader skew was cured by merging main, and the
  relay was overridden once with `HPO_RELAY_CLASSIFY`. One imminent: PR 3425 at c6becb31, a
  pending-ci merge verdict, red on main's own instrument-self-tests.

Cost:
- **At line 268, before dying on a moved head, ask `review_carry.py <drafted head> <live head>
  --verdict-only`**, with the same `HPO_RELAY_CARRY` hook line 405 uses.
  - On CARRY, continue with classify at the **live** head and post on GREEN, saying in the relay's
    line that the verdict was carried.
  - On FRESH-REVIEW or CANNOT DECIDE, keep today's refusal and re-dispatch.
  - RED at the live head still refuses (line 273).
- About 8 lines in `tools/audit/seat/cloud_relay.sh`. Its self-test's pending-ci arms (lines
  1183-1190) gain three stubs, reusing the carry-ok, carry-no and carry-un stubs at lines
  1161-1163:
  - moved head plus carry-ok plus GREEN: posted;
  - moved head plus carry-no: refused;
  - null control: same head plus GREEN, posted as today.
  - Mutant: skip the carry call, and the moved-head plus carry-ok arm is refused.
- The verdict names the drafted head, which is an ancestor of the live head (a merge of main into
  it), so the merge train's reviewed-head rule is met.
- `cloud_relay.sh` has no row in `tests/structure_budgets.json`.

Binding:
- Without it, every pending-ci verdict on a head that has to take main in, the cure for any red
  main caused, costs one full reviewer re-dispatch, or a hand override of the relay's classifier.
  The override is the riskier of the two, because it bypasses the RED check.
- The fix uses the relay's own existing rule and instrument, and makes no new judgement.
  `review_carry` refuses any range with branch-authored change, so nothing unreviewed is carried.

Routing:
- One carry to R10-REVIEW-DISPATCH-RESIDUE. It owns `cloud_relay.sh`, is not started, and P551's
  split applies.
- Interim: the `HPO_RELAY_CLASSIFY` override with the cause commented first, as on 3419, remains
  the orchestrator's call per instance. Check `review_carry.py <drafted> <live>` answers CARRY
  before using it.
