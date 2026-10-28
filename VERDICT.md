Fix review: blocked 6e4d2b5cf5e9580e20198e2ea282bdb6ef597516 mutant-survives: gh_transient's classification branches are outside the sweep's rules; deleting the error-connecting-to alternative or widening the 403 grep to any rate limit passes all 218 checks

bus-nonce: 622da006e928932869d5115d27728d13

Round: second review (round 2), of fixer round fix2589z on the round-1 block at `e4b3e01a`. I reviewed from detached worktrees: `6e4d2b5cf5e9580e20198e2ea282bdb6ef597516` (the head), and `f84fa6b2e` (round 1's tests with main merged, the body's other end). The merge base is `3976515a08228598ea3863f4f36dc4c7c4846865`, which is also origin/main's tip. `dev/governance/roles/` on main is unchanged since the merge base (empty three-dot diff), so the contract I followed is current. The finder's harness is the group brief's null control (5) on `origin/handoff/audit-r10-roster` at `306a96d5f`.

## Block

1. **mutant-survives: the enumeration rule misses the classifier's own branches.** The brief requires every one-line mutant of the retry loop's bound, budget, classification branch and sleep/backoff to turn a test red. The body names `r10_gh_read_retry_mutants.py` as the rule that sweeps "a bound, budget or classification branch ... the day it lands". Its seven rules are num, rel, opnd, or, not, ret and del. None of them rewrites a `case` label, a sed/grep pattern or a grep flag. In `gh_transient`, those are exactly where the classification branches live. I hand-wrote one-line mutants of those tokens (`ev/my-mutants.txt`, runner `ev/my-mutants-runner.py`; the worktree was restored and `git status` is clean). Five survive with `218 checks, 0 failed`, rc=0:
   - **X7**: `'^Get "https?://[^"]*": |^error connecting to '` -> `'^Get "https?://[^"]*": '`. This drops gh's `error connecting to` transport shape, which the code comment and the body both name as retried. No fixture queues that shape: `grep -n 'error connecting'` hits only the comment and the pattern. With the mutant, a real `error connecting to api.github.com` refuses after one call, which is train 8's failure.
   - **X20**: `grep -qi 'secondary rate limit'` -> `grep -qi 'rate limit'`. This retries a primary-rate-limit 403 (`gh: API rate limit exceeded ... (HTTP 403)`). The body classifies that as "any other status", which refuses. No refusal arm queues a non-secondary rate-limit 403, so a retry would mask a refusal and nothing reds.
   - **X22**: dropping the `^` anchors of the transport grep. Any stderr that merely contains `Get "https://...": ` then classifies transient.
   - **X14**: `grep -qi` -> `grep -q`. GitHub's casing of `Secondary Rate Limit` is not pinned. The head classifies `gh: You have exceeded a Secondary Rate Limit (HTTP 403)` transient (`ev/classify-probe.txt`), and the mutant would refuse it.
   - **X4b**: `5??|429)` -> `50?|429)`. Only 500, 502, 503 and 504 are queued, so a 5xx outside 50x is unpinned.

   The production classifier is correct today on each probe line (`ev/classify-probe.txt`). Only the pins are missing, which is round 1's shape again, one level down: a census over the fixture lines cannot see a class of stderr no arm queues.

   Fix:
   - Add arms (or census lines) for `error connecting to ...` (transient), a primary-rate-limit 403 (refuse), a mixed-case secondary-limit 403 (transient), a non-50x 5xx such as 520 (transient), and an unanchored `... Get "https://x": ...` line (refuse).
   - Extend the sweep with a rule that mutates the classifier's alternatives: drop each `|` alternative of each `case` label and each grep/sed pattern, drop the `-i`, and drop each `^`. Then re-run it and my X4b, X7, X14, X20 and X22.

2. **carry-missing: not carried to R10-FLY-GH-READ-RETRY (PR 2 and PR 3).** The body's second `## Forward-carry` item (`bf68d2c0`, "PR 2 and PR 3 of this group owe the same proof": a spent-budget fixture with budget+1 transient lines, a census, and a rule-generated sweep) is a precondition on later stages of this group. It is not in the group's `brief` or `carry` on `origin/handoff/audit-r10-roster` at `306a96d5f`: `grep -c bf68d2c0` gives 0, `census` matches nothing in the group, and the group's two `carry` entries are the fourth-instance note and round 1's JWT/`git fetch` item. finding-propagation.md says the producing PR does not merge until the carry is in the tree, and that the body names the roster branch SHA. The body names neither. Append it with `roster_edit append-carry`, name the SHA in the body, and carry block 1's added rule with it, since PR 2 and PR 3's classifiers have the same shape.

Round 1's blocks are cleared at this head:
- **mutant-survives (budget unpinned)**: R11 (unbounded) and R1 (budget 5) are killed. As the sweep's M60 and M54, and as my X1 (`|| false`, 6 failed: 7 calls, sleeps `5 15 45 135 405`) and X2/X2b (`READ_TRIES` 5 and 3, 5 and 7 failed).
- **root-cause-unanswered**: `## Red checks` now names `pr-contract` with its cause and the cheaper detector.

## Findings

- `pr-contract` is red on this head (both runs, jobs 119605965880 and 119606114810), with `BAD-DEST` for the two `Carry: R10-FLY-GH-READ-RETRY` items. Group R10-FLY-GH-READ-RETRY is absent from main's roster and present only on `handoff/audit-r10-roster`. The body routes both under `## Forward-carry` and answers the red under `## Red checks`, so per the brief this is a finding, not a block. It clears when #2588 merges. Carry: R10-FLOW-ROSTER-FREEZE
- `## Red checks` still says "The commits after `e4b3e01a` are on `handoff/r10-fly-gh-read-retry`, not on the pull request, so CI has not run on them". At `6e4d2b5c` they are on the PR and CI ran: `pr-contract` and `nightly-status` are red, the rest green or skipped, and `closures` was still in progress at 02:56Z. The section should be re-taken at the next head. Carry: R10-FLY-GH-READ-RETRY
- `gh_transient` classifies only the last `gh: ... (HTTP NNN)` line (`tail -1`), and `gh_read` classifies the file rather than `GH_ERR`. My X13 (`tail -1` -> `head -1`) and X17 (classify `$GH_ERR`) survive because every fixture is a single line. They are equivalent only while gh's stderr is one line. A two-line fixture, such as a status line followed by gh's hint line, would pin both. Carry: R10-FLY-GH-READ-RETRY

## Evidence

- RESULT head self-test `6e4d2b5c`: `app_approve self-test: 218 checks, 0 failed`, rc=0 (`ev/selftest-head.txt`). Re-derived; matches the body's `1063eb3a` figure.
- RESULT other-end self-test `f84fa6b2e`: `206 checks, 0 failed`, rc=0 (`ev/selftest-base-f84fa6b2e.txt`). Re-derived.
- RESULT sweep at head: `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py` gives `RESULT mutants=89 killed=78 equivalent=11 survivors=0`, with M0 `NULL-OK` (`ev/sweep-head.txt`, list in `ev/sweep-list.txt`). Re-derived, matching the body's `0f2fa660` row.
  - I checked each of the 11 equivalents' reasons against the code and they hold.
  - The `f84fa6b2e` row (68 / 11 / 10) was not re-run: not re-derived here.
- RESULT my mutants (`ev/my-mutants.txt`). X0 null: 0 failed.
  - Killed: X1 6, X2 5, X2b 7, X3 3, X4 11, X5 3, X6 3, X8 7, X9 7, X10 1, X11 1, X12 3, X15 5, X16 3, X18 2, X19 11, X21 31.
  - Survived: X4b, X7, X13, X14, X17, X20, X22 (Block 1, and Findings for X13 and X17).
- The census null control (the review's fourth line planted, `218 checks, 2 failed`): not re-run, so not re-derived. The census assertions are present at the head, and the census holds both classes in the green run.
- Figures at this head (`ev/figures.txt`):
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc=0. Re-derived.
  - `score.py --diff 3976515a0 HEAD`: `Architecture score: dS +0.0000 NULL`. Re-derived.
  - `closure.py select --diff <merge base>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` Re-derived.
  - `policy_lint.mjs --budgets`: rc=0. Re-derived.
  - `tmp_paths.py --check`: `0 refused`. Re-derived.
  - `harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`. Re-derived.
  - The seam rule `awk ...` gives 10 lines (`ev/seams.txt`). Re-derived, and each is dispositioned in the body's table.
  - `entities.py` (2382), `ci_predict.py`, `env_drift.py --claims-only`, `layout.py` and `closure.py selftest`: not re-run, so not re-derived. CI's `closures` job was still in progress at 02:56Z.
  - The 2667 s / train 8 figures come from train logs not in this container: not re-derivable.
- Merge: `git merge-tree --write-tree origin/main 6e4d2b5c` gives clean tree `944e6bc9ec`, rc=0 (`ev/merge-tree.txt`).
  - No claim file and none of VERSION, the manifest version or the notes heading is touched. CI's `no version edit` line agrees.
- Carry audit (`ev/carry-audit-roster-ref.txt`, `ev/carry-audit-main.txt`):
  - `--roster-ref origin/handoff/audit-r10-roster` gives `3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`, rc=0.
  - Without `--roster-ref` it gives `1 routed, 0 unrouted, 2 bad destination(s)`, rc=1, naming R10-FLY-GH-READ-RETRY.
  - Round 1's JWT/`git fetch` carry is in the roster group's `carry` list (`ev/roster-group.json`).
- CI on this head, check-runs API, at 02:56Z (`ev/checkruns-head.tsv`): 28 success, 14 skipped, 3 failure, 1 in progress (`closures`).
  - `instrument-self-tests` (which runs this self-test), `fast (3.14)`, `coverage`, `typing`, `mutation`, `arch-score`, `budget-raise-gate`, `policy-docs`, `browser` and CodeQL all passed.
  - Red: `pr-contract` ×2 (Findings), and `nightly-status`. `nightly-status` grades main's nightly lanes, and the diff reaches nothing it reads.
  - `0f2fa660`, `1063eb3a` and `14eda530` have no check runs (`ev/checkruns-intermediate.txt`).
- Head: `6e4d2b5cf5e9580e20198e2ea282bdb6ef597516` is the PR head (re-read at 02:56Z) and the head the body's `## Head` names (`ev/HEAD.txt`).
