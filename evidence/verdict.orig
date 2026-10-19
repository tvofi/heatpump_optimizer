Fix review: blocked 22803f99bd8be29012a668ef22140dd12ae3aa5e carry-missing: the body still names done R10-TICK-DRIVERS as the beat-restart destination: a spliced stale second ## Forward-carry (after a broken "## Friction`." heading) contradicts the R10-STAMP one, and carry_audit refuses it BAD-DEST

bus-nonce: b99f1763a7e81901bc62b855d9db353c

**Round 8.** This is the eighth `Fix review:` verdict on #2406. Rounds 1 to 7 blocked at `a7d97f55b`, `89d2b9465`, `af391637b`, `b965c4ab9`, `d1becac2b`, `2d9f20009` and `22803f99b`. The head has not moved since round 7. From the fourth round on, `fix-review.md` says `fixer.md` owes a re-cut rather than a repair. What is left here is a body edit, so I name the rule and leave it to the orchestrator.

I measured head `22803f99bd8be29012a668ef22140dd12ae3aa5e` (`ev/HEAD`). `pulls/2406` reported the same head when I wrote this. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so my copy of the contract is current. The merge base is origin/main `06c6f3cf2`.

## What the repair got right (the roster)

On `origin/handoff/audit-r10-roster` at `73bb15fe8f5bf05ec3568927118a8d678dd8b99f` (`ev/carry.txt`):
- `R10-STAMP` has `resume.stage: "not-started"` and `next_step` "after the wave-1 drain, run the stamp". So it is a live group that runs after this PR merges.
- Its `carry` ends with the beat restart, worded the same as the copy on R10-TICK-DRIVERS:
  - "after #2406 merges, restart the state-docs beat (tools/audit/seat/state_docs.py) on main's code with no --roster-ref and no --watch-ref refs/heads/main";
  - the control: "Check: the beat's memo file holds two SHAs (main's and the roster branch's), and a roster-only commit regenerates the plan within one beat."
- `73bb15fe` changes one file, adding that one line.
- The body's first `## Forward-carry` names R10-STAMP at `73bb15fe` correctly.
- The two stale copies remain on the done R10-TICK-DRIVERS. Nothing dispatches or lints a done group, and the body discloses them.

## Why it is blocked: the body names two destinations, and one is the done group

The repair was spliced into the body rather than replacing the old section. The tail of the body (`ev/body-tail.txt`, `ev/body-headings.txt`) contain:
- a broken heading, `## Friction`.` (with a stray backtick and full stop);
- a duplicate copy of the `closures` and `nightly-ha (stable)` red-check entries;
- **a second `## Forward-carry`** that still reads "Carry: R10-TICK-DRIVERS ... The CodeQL delegation carry is done in this PR, so the orchestrator drops it from that group";
- the real `## Friction` after that.

So the body now names two destinations for the same carry, and one of them is a group at `resume.stage: done`. `finding-propagation.md` says "A group at `resume.stage: done` is not a destination", and "a reader who finds two versions trusts neither". Step 10 opens the destination the body names, and this body names both.

The instrument agrees. I ran `carry_audit.py`, which is not in the tree on main: it comes from PR #2404's head `b419463b1`, self-test `144 checks, 0 failed`. Against `--roster-ref origin/handoff/audit-r10-roster` (`ev/carry_audit.txt`):

```
BAD-DEST body item 441668ce: R10-TICK-DRIVERS: R10-TICK-DRIVERS is done (resume.stage done)
CARRY-AUDIT: 4 finding item(s): 1 routed, 2 unrouted, 1 bad destination(s)   rc=1
```

So the dispatch's precondition, "carry_audit check passes against the roster ref", does not hold.

**Remedy: a body-only edit, no push.** Delete the block from `## Friction`.` through the second `## Forward-carry` bullet, and keep the first `## Forward-carry` section (the one naming R10-STAMP) and the real `## Friction`. Then run `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` again.

`carry_audit` lists two other UNROUTED body items. I do not block on them, because the `Carry:` marker rule carry_audit enforces is still in unmerged #2404, not on main's `finding-propagation.md`. They will still fail the check named in the dispatch:
- `ba1bccf9`: the CodeQL "done in this PR" bullet. Writing `Carry: dismissed: done in this PR (MB17 pins it)` would route it.
- `832ebf74`: the `## Friction` item `fixer-step-5: unenforced`. It needs a `Carry:` naming its owner, or `dismissed: <reason>`.

The PR-level sweep (`carry_audit pr 2406`) also lists four non-blocking notes from earlier verdicts (items `3af316e4`, `bc6c94b6`, `d714141d` and `8694f912`) as unrouted. `d714141d` is the beat restart, which R10-STAMP now holds, but no marker in the body names that item id.

## Checks that pass, and an instrument note

- **pr-contract.** It passed this body three times, the last run starting at 02:48:48Z, after the edit. So `checkPrBody` accepts duplicate `## Forward-carry` headings and a malformed heading. Nothing in the tree catches this splice. This is an instrument observation for D11, not a finding of this PR.
- **Merge.** `git merge-tree --write-tree origin/main 22803f99b` returns rc 0, tree `b33c4358a` (`ev/merge-tree.txt`).
- **Census.** `closure.rename_sites()` at the head returns `([], [])`.
- **Code.** Round 7's verification of the code stands. The head is unchanged, and the roster edit touches nothing the diff reads. I did not re-run the mutation proof or the figures.
- **CI** (check-runs API, `ev/checkruns.tsv`):
  - Nothing at this head has concluded `failure`.
  - `fast (3.14)` and `closures` were still `in_progress` at 02:50Z. They started at 02:10Z and 02:27Z.
  - Round 7's local `ALL 2349 ENTITY CHECKS PASSED` predicts `fast` green. Read its conclusion before any `merge` verdict.
- **Version, claims and budgets** (steps 4, 5, 14): untouched, as round 7 found.
- **Stage form** (not blocking): `finding-propagation.md` says a stage's brief lives in the group's `brief` string. This carry sits in R10-STAMP's `carry` list, as earlier rounds accepted, and the group's `brief` does not mention it.

RESULT carry_destination=R10-STAMP live=not-started text=present control=present
RESULT body_forward_carry_sections=2 stale_dest=R10-TICK-DRIVERS(done)
RESULT carry_audit_check rc=1 routed=1 unrouted=2 bad_dest=1
RESULT merge_tree rc=0
RESULT rename_sites=([], [])
RESULT ci_failure_at_head=0 in_progress=fast(3.14),closures
