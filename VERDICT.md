Fix review: merge 9a0960559ed9e87c679e50f30bce43a599c63459

bus-nonce: a895cb8fefe1c35f3bae2c2a9b36fbb6

Round 2. Fix-review seat for #1848 (R9-F10.5). I reviewed head `9a096055`, which is round 1's head `4f594b42` plus the fixer's code `1fc1c6cc` plus `origin/main` `948671af`, merged automatically. I worked in a detached worktree and used my own harness throughout. Evidence is in the `evidence/` directory (`HEAD.txt` names the head).

**Resolution delta.** The head's tree is identical to `git merge-tree --write-tree 1fc1c6cc 948671af` (`git diff --stat` between them is empty). The main merge therefore carried no hand resolution, so what I judged is the fixer's delta `4f594b42..1fc1c6cc`.

## Round-1 blockers

### B1: closed (main-only reach)

- **What changed.** Both jobs now carry `github.ref == 'refs/heads/main'`. The push job also requires `schedule` or `workflow_dispatch` and a successful `mutation-ledger`.
- **Pinned by a reach check.** A new check evaluates each job's `if:` over every event, ref and recheck answer.
- **Mutants:**
  - `R_B1a` (guard removed from `mutation-ledger`): killed.
  - `R_B1b` (guard removed from the push job): killed.
  - `R_B1c` (`push` added to the push job's events): killed by two checks, the reach check and the reporter-lanes check.

### B3: closed (the commits sent are checked)

`drain_push_problems` reads `origin/main..HEAD`: exactly one commit, parent `origin/main`, subject `DRAIN_SUBJECT`, and its diff adds only new rows. `drain_changed` owns the returncode of the measured-head diff.

**Mutants (all against `tests/entities.py`, now 2069 checks):**

| Mutant | Change | Result |
|---|---|---|
| A2 | round 1's survivor: `ref: main` and the reset dropped | killed |
| A3 | round 1's survivor: token mask dropped | killed (a new mask-before-use check) |
| R_A7 | round 1's survivor: returncode ignored, now inside `drain_changed` | killed |
| R_P2 | `A` status not required | killed |
| R_P3 | subject check off | killed |
| R_P4 | count check off | killed |
| R_P5 | YAML call to `drain_push_problems` dropped | killed |

**Two of my mutants survive. Both are equivalent in effect, so neither blocks:**
- `R_P1`, parent check removed. Once `rev-list origin/main..HEAD` is exactly 1, HEAD's parent is reachable from `origin/main`. An older parent shows up in `diff origin/main HEAD` as M/D lines, which the name-status check refuses, and the push would also be non-fast-forward.
- `R_P6`, the `"\0"` failure sentinel turned into `""`. A failing `rev-list` then reads as 0 commits, which is still refused.

**Real git, scratch repos (`push_problems_harness.txt`).** `drain_push_problems` was run on eight shapes:

| Case | Shape | Result |
|---|---|---|
| S1 | one row commit (null control) | `[]` |
| S2 | branch commit under the row commit | 3 problems |
| S3 | modifies a row | refused |
| S4 | wrong subject | refused |
| S5 | row plus `src.py` in one commit | refused |
| S6 | no `origin/main` | refused |
| S7 | nothing committed | refused |
| S8 | deletes a row | refused |

`drain_changed` on real git:
- a real diff gives `['src.py']`;
- an unknown sha gives `None`;
- an empty measured head gives `None`;
- the same head gives `[]`.

### B2: code and amendment closed; owner state partial, and I accept the ordering

**Code.** The push job declares `environment: ledger`. `skip-no-writer` was removed from `DRAIN_QUIET`, so a missing credential now turns the job red.
- `R_B2a` (environment line removed): killed.
- `R_B2b` (`skip-no-writer` restored as quiet): killed.

**Amendment.** It now separates what the workflow does from what the credential can do. That is the distinction round 1 asked for. Its statements:
- The credential mints the App's full `contents: write` on any path and branch.
- Repository-level secrets reach every same-repository run on any branch, and environment jobs too, so only deleting the repository copies confines the credential.
- The 22628467 bypass buys only force-push and deletion of `main`, and should be removed unless a reason is recorded.

I confirmed all three: the first two against GitHub's documented secret scoping, the third against the live rulesets in `live-owner-state.txt`.

**Live owner state (read at posting):**
- Environment `ledger` exists with a branch policy of `main` only, and holds `HPO_LEDGER_APPID` and `HPO_LEDGER_PEM` (set 14:19–14:20Z).
- The repository-level copies still exist (13:12–13:13Z).
- 5094721 is still `always` on both rulesets.

**Ordering, which the orchestrator asked me to judge.** Deleting the repository copies after the merge is acceptable. Doing it before costs nothing and is better. Three reasons:
- The exposure lives in the repository secret store, not in this diff. Merging adds no reader: the head's only reader is the main-guarded environment job.
- Nothing on `main` reads them today. `git grep HPO_LEDGER origin/main -- .github/` finds nothing.
- The head's job gets the environment copies whether or not the repository copies exist.

So deleting the repository copies now breaks nothing and shortens the window by the time until merge. The amendment already says the job is "bounded by the `refs/heads/main` guard alone" until the copies are deleted, so the record is true in either order.

The 22628467 bypass stays tvofi's decision. The amendment records it honestly and recommends removal.

**Wording, not blocking:**
- The amendment's "Owed by the owner (#1848): create the `ledger` environment ..., store the two secrets there" is already done live. Only "delete the repository-level copies" and the 22628467 decision remain.
- The `docs/HANDOVER.md` bullet says "retire this on its merge", which is the orchestrator's job at merge.

## Reproduced at this head

**Entity checks:**
- Unmodified head: `ALL 2069 ENTITY CHECKS PASSED`, rc=0.
- M0, a comment-only change (the null control): `ALL 2069 ... PASSED`, rc=0.
- My re-derived forms of the fixer's M1–M8 each fail exactly their named check, with `1 of 2069 ... FAILED`.

**Cheap checks:**
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `node .claude/workflows/policy_lint.mjs`: `TOTAL: 0 error(s) across 40 policy file(s)`.
- `git merge-tree --write-tree origin/main HEAD`: exit 0 against main `5f87e25a`. Main moved again during the review; the PR head did not.

**Round 1's push-half figures** (stock, slice, single apply, second apply writes nothing) are untouched by this delta. The `--drain` code paths `drain_pool`, `apply_drained`, `stale_pins` and `write_drain` are byte-unchanged, so I carried those figures rather than re-taking them.

**Not run here:** the 40-site drive itself, which hits the BLAS baseline issue on this Mac. The fixer's demonstration figure is unverified by me. The first nightly is the measurement.

## Head CI (cited, not re-run)

Check-runs at `9a096055` (`checks-final-*.json`), all workflows completed:
- 24 success, 11 skipped, 2 cancelled, 0 failure.
- The two cancellations are superseded `budget-raise-gate` and `pr-contract` runs. Both have a success at this head.
- `fast (3.14)`, `mutation`, `closures` and `pr-contract` are all success.
- `mutation-ledger` and `mutation-ledger-push` are skipped on `pull_request`, as designed.

No red, so step 11 is not triggered.

## Head liveness

- Measured at `9a0960559ed9e87c679e50f30bce43a599c63459`.
- `gh pr view 1848` reads the same head at posting.

Code-owned paths still need tvofi's approving review at this head.
