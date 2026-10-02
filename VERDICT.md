Fix review: blocked f70cd730c60e1c6b9d505a26d27f0f2e0d14e31f root-cause-unanswered: nightly-status went red, unanswered (the diff touches tests.yml, so its exemption is void; pr-contract 110993238084 is red on exactly this)

bus-nonce: a39959b3ab4b114fb0d7085e45e7834e

Round 2. Reviewed from a detached worktree at f70cd730c, merge-base aa7a81192 (= origin/main). `tools/audit/briefs/` is unchanged between the merge-base and origin/main. Head re-read at posting time: still f70cd730c. f70cd730c's tree equals `git merge-tree 640ef43fa aa7a81192` (c3cdec29c), so it has no hand resolution. `git merge-tree --write-tree origin/main HEAD` exits 0. The `tests/closure.py` hunk is byte-identical to round 1's, so round 1's real-artifact demonstration carries (copied into this evidence directory).

Evidence: evidence-f70cd730c60e1c6b9d505a26d27f0f2e0d14e31f/. The mutants (`mut2.sh`, `mut2.out`) and `real.py`/`all.sh` are my own harness. numpy/scipy came from a pip `--target` of CI's pins on 3.14 macOS.

## The blocker: one line in `## Red checks`

- `nightly-status` failed at this head (job 110983235910): `NIGHTLY ABSENT: nothing failed, but mutation-ledger, mutation-ledger-push did not run in that scheduled run (last night)`.
- `pr-contract` (110993238084) refuses it: `check nightly-status is red and ## Red checks does not name it ... this diff touches what it reads (.github/workflows/tests.yml)`.
- By `defect-root-cause.md`, the exemption is void because the diff touches tests.yml, so the body owes an answer.
- The control says the red is main's, not this diff's. Every open PR head carries the same red: #1862, #1861, #1858, #1857, #1856 and #1852 are all `failure`. This PR's tests.yml change is confined to the closures check step, and the mutation-ledger jobs are untouched by this diff (#1859 changed them on main).
- The answer is one bullet. Name `nightly-status`, give the cause (main's scheduled run did not run mutation-ledger and mutation-ledger-push; not this diff), and name its owner (the orchestrator, on main). Then pr-contract re-runs.
- Everything else below passes. With that bullet added and no code change, I expect `merge`.

## The delta

- **`_af_case(..., inert=())`.** It wraps `_closure.is_inert` with the given set and restores it in `finally`. `inert_closure_violations` looks `is_inert` up as a module global at call time, so the wrap takes effect.
  - RESULT entities_head=ALL 2074 PASSED.
  - M11, dropping `inert={"DISCLAIMER.md"}`, brings back exactly round 1's two failures (`('changed', False)`). The fixture is now independent of main's live list, and that is what was killing it.
- **Pipefail placement check.** RESULT survivors=0/11 mutants (10 killed, 1 decoy correctly green):

  | Mutant | Result |
  |---|---|
  | M2a, this step's pipefail removed | killed |
  | M6, commented (round-1 P2) | killed |
  | M7, moved after `fi` (round-1 P3) | killed |
  | M10, moved inside the `then` arm (new, effective on one arm only) | killed |
  | M2b, one arm's tee removed | killed |
  | M2c decoy, the other three identical `set -o pipefail` lines removed (835/954/1007) | ALL PASSED (correct: the check is specific to this step) |
  | M1, guard deleted | killed |
  | M3, status made quiet | killed |
  | M8, `"UNDER" in l` | killed (by the null control) |
  | M9, always disagree | killed (null control + status roster) |
  | M11, fixture without inert | killed (2 checks) |

- **The body is re-taken.** It names f70cd730c, answers `fast (3.14)` and the round-1 `pr-contract` with a cheaper detector and its standing cost, and keeps the bootstrap note. It has two small staleness points, neither blocking:
  - `## Head` says "Merge base with origin/main: 5f87e25a1"; at f70cd730c the merge-base is aa7a81192.
  - The figures say 2065 checks, taken at 640ef43fa. The head has 2074 (main's additions), all passing, which I measured.

## Items 1-8 at this head

1. **tests.yml** is unchanged from round 1 (lines 1708/1710/1712).
2. **The closure.py logic** is unchanged and confirmed. The non-blocking rc==0 note from round 1 stands.
3. **Null controls** pass, both in entities.py and on the real artifacts.
4. **Real logs** carry from round 1, with an identical hunk:
   - unpatched pinned matches CI 5/5;
   - patched defects red 3/3;
   - nulls quiet 2/2;
   - no check.txt quiet 5/5.
5. **Wiring:** see the mutant table above.
6. **ci-autofix.md:** 92/96 lines and 1428/1428 tokens, no raise. `policy_lint` TOTAL 0 errors across 40 files, RULES-SYNC ok. tvofi's approval is owed (policy), and the body says so.
7. **Bootstrap:** true. closures-autofix is pinned to base.sha, and the body says so.
8. **CI:** waitci DONE, 35 runs.
   - `fast (3.14)` passed.
   - `closures` passed.
   - `mutation` passed.
   - NOTGREEN: `nightly-status` and `pr-contract` (see above). `budget-raise-gate` and the first `pr-contract` were cancelled, superseded.
