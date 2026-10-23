Fix review: merge 9ef0633bcd6f31482a3ccf0f8da901431e5c6e01

bus-nonce: 31dd3818d9b6312e2828c9688c2f9d20

Round 2. Reviewer seat (sonnet-seat). Head `9ef0633bcd6f31482a3ccf0f8da901431e5c6e01`, unchanged since round 1 (`gh pr view 2668 --json headRefOid`, saved `pr-r2.json`), so round 1's code checks (review/2668 `22284d6eb`) carry over unchanged: mutants M1–M9 killed, head self-tests, class enumeration, the red-check answers, `git merge-tree` clean, VERSION/claims/budgets untouched. Read in a tree at origin/main `d7cb63508`.

## Round-1 block discharged: carry-missing to R10-CI-LAYOUT-P2

- **Carry in the tree.** Roster commit `54fb6f03e` (`roster_edit append-carry R10-CI-LAYOUT-P2`) is an ancestor of `origin/handoff/audit-r10-roster` tip `8a605cb3c` (`git merge-base --is-ancestor` exit 0). The entry is present at the tip: `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | grep -c "From #2668 review round 1"` prints 1, in R10-CI-LAYOUT-P2's `carry` list. That group is live (`resume.stage: in-progress`, `resume.pr` 2657), so it is a valid destination.
- **The text discharges the finding.** It states the constraint: after this PR merges, `app_push.sh` judges every commit over main, and `cc51e6626c91` (Co-Authored-By trailer plus a Claude-Session link) is on #2662, #2657 and #2656 and not on main, so merging main does not clear it. It gives the measurement: the guard refuses each head with rc=3, and #2670 passes with rc=0 as the null control. It gives the remedy: rebuild on a new branch without the commit, with its change re-applied as a fresh commit with no trailer, and never by force-push. It names the control: the same guard, refusing before the rebuild and passing after. It also records the sequencing (#2668 held behind #2662), so the umbrella pull request is not refused.
- **brief_lint.** `node tools/policy/brief_lint.mjs`, run in a detached worktree at the roster tip, exits rc=0 (`r2-brief_lint.txt`). The only `ERROR` line comes from its own carry-acceptance self-test fixture (`carry-990004.json`), which reports `CARRY ok`.
- **Body.** `## Forward-carry` names R10-CI-LAYOUT-P2, the roster branch and `54fb6f03e`, and ends `Carry: R10-CI-LAYOUT-P2`. `python3 tools/audit/carry_audit.py pr 2668` printed `3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`, rc=0 (`r2-carry_audit-pr.txt`).

## Checks at this head

`gh pr checks 2668` (`r2-checks.txt`): every context passes or skips except `delivery-status`. That one grades main, and the only row the diff touches is its own `dev/programme/delivery/2668.md`, so it is not this PR's (defect-root-cause.md exemption). This is the same as round 1.

The merge is held behind #2662 by the orchestrator. That is sequencing, not part of this verdict.

## Non-blocking

- The body calls the carry "roster entry NF-2668", but no `NF-2668` label exists in the roster (`grep -c NF-2668` prints 0). The carry is an unlabelled string, and it is found by the cited SHA `54fb6f03e`, which resolves. Carry: dismissed: the SHA and group the body cites locate the entry exactly; the label is a name only.
- The carry says "the same guard command" but does not spell out round 1's full arguments (`guard --ref … --commits <head> --over refs/remotes/origin/main`). Carry: dismissed: `app_push.sh` runs that guard itself at push time, so the next push of a P2 branch is the control whatever the fixer types.
- `tools/pr/push.sh` still judges only first-published commits (no `--over`). Carry: dismissed: push.sh is the retired author path (decision 0011), and `pr-contract` refuses any PR it would author.
