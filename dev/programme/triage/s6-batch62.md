# Proposal triage, session s7, batch 62 (P290)

The rolling batch (V182) after batch 61 (#2970, merge verdict at `2a25229f9`, not yet merged).
Facts were read at origin/main `2fde526340bdb1da17fa7a5cd8bff283cff2757c`.

## P290: a merge verdict never carries across a claim-file merge

Verdict: ACCEPT, option (a) only, as a new fly-in, R10-FLY-CARRY-CLAIM-DRIVER. Option (b), a
train hold at the batch boundary, is REJECTED. URGENT: critical-path #2917 is blocked by this
right now, so this seat asks the orchestrator to open this batch at once rather than wait for 8
rulings.

Source: the orchestrator's triage-queue line of 2026-10-29T22:30Z (a slip class with 3 or more
instances). Critical-path #2917's carry check refused it after every main move, and
`review_carry` returns FRESH-REVIEW each time. The heads were `2fda9547` -> `c861c0e7` ->
`2a5bd4dd` -> `a361e454`. The cost so far is about 4 h of critical-path delay and 3 delta
reviews. The line asks for the count of carry refusals caused by claim-file resolutions in the
train log over round 10.

Instances:
- **The count.** `grep 'resolves tests/golden/'` over the live `merge_train/train.log` finds 5
  refusals, all #2917: 4 `SKIP #2917 carry` lines and 1 `ADD REFUSED #2917`. The log's only
  other `CARRY: no` line is #2876, which has a different cause (a merge that is not on main).
- **The check.** `tools/pr/app_approve.sh`'s carry walk requires each `merge=claimnotes` file in
  a merge commit to equal "the union of its parents" (the `got`/`want` comparison and its "resolves
  ... to something other than the union of its parents" refusal). `review_carry.py` asks
  `app_approve.sh --carry` for this predicate (commit `c1a5cd91c`), so the two tools share one rule.
- **The driver does not union.** `tests/env_drift.py`'s `merge_claim_file` takes the claim list
  from whichever side changed it, because "Union a branch's list with main's and a claim the
  branch deliberately deleted comes back". So a driver resolution in which one side cleared a claim
  is never the union, and the carry refuses git's own automatic output.
- **The driver's output, replayed.** For each refused merge, the driver was run on (merge base,
  first parent, second parent) of `tests/golden/claimed_drift.txt`. The runs were `--merge-claim-file`
  on copies taken with `git show`, and each exited 0:

  | Merge | Driver output vs head | Union of parents vs head |
  |---|---|---|
  | `f53ac2a39` | EQUAL | DIFF |
  | `2fda9547e` | EQUAL | DIFF |
  | `c861c0e7b` | EQUAL | DIFF |
  | `2a5bd4dd2` | EQUAL | DIFF |

  All four heads hold exactly the driver's deterministic resolution, and none is the union.

The rule run on each instance: all 4 merges carry under (a), and none carries under today's
union rule.

Accepted, as fly-in R10-FLY-CARRY-CLAIM-DRIVER:
1. In `app_approve.sh`'s merge-commit arm, a claim file also passes when it equals the driver's
   own output. That output is `tests/env_drift.py --merge-claim-file` run on the file at the
   merge base of the two parents, the first parent and the second parent.
2. The driver is read at main, as the `.gitattributes` list already is (`git show
   "$main:tests/env_drift.py"`), so a branch cannot supply its own driver.
3. When the driver refuses (both sides changed the claim list), the existing union rule decides,
   unchanged.
4. Self-test: a fixture merge where main cleared a claim the branch kept, resolved by the driver,
   carries. The same merge with one extra claim line added by hand does not. Mutation: dropping
   the driver arm fails the first arm. Null control: today's pure-union fixture
   (`app_approve.sh` "refused as a claim resolution that is not the union") still refuses a
   non-union hand resolution.

Rejected, (b): a batch-boundary hold in `train.sh` so a claim-touching critical-path entry runs
with nothing merged ahead. It adds a train state and a new hold for a defect that (a) removes at
its source. The record-step ordering is P289's.

Cost: one S fly-in on the sonnet fixer with an opus review. It edits `tools/pr/app_approve.sh`
and `tools/audit/seat/instruments/app_approve.sh.md`, plus one driver call per claim file per
merge commit in a carry walk (milliseconds). Neither file has a `policy_lint.mjs --budgets` row.
Benefit, measured: 5 refusals on the critical path, about 4 h and 3 delta reviews to date. The
refusals recur on every main move until #2917 merges.

Binding: the triage gate. The fly-in's roster op cannot land until this file is on main, so the
critical path waits on this batch's own merge.
