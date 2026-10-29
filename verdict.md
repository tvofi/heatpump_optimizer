Fix review: merge 2f8a97c83794d3b583e4456696463e3458f0c732

bus-nonce: 3c2b60104ad2ecc0c7b3a90494ed6546

## Round

This is round 3. Round 1 was `Fix review: blocked ad1ba9adb7341d31288d27648da09f0ce61def19` (review/2916 at 803820f94). Round 2 was `Fix review: blocked ca2dc27d74252606afb264c514585f9ea0e405b5 mutation-vacuous` (verdict commit 5f9b05586). I measured head 2f8a97c83794d3b583e4456696463e3458f0c732, and it was still the PR head (`refs/pull/2916/head`) when I wrote this. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the role contract is current. Between ca2dc27d7 and the head, the only authored change is 6fd9984a7. It touches the self-test half of `tools/audit/seat/beatd.py` alone: case (3)'s `graced()` bound and two `MUTANTS` entries. No production line changed. `git diff 6fd9984a7 2f8a97c83` over the PR's seven paths is empty, so the main merge carries none of this PR's lines.

## Findings

- The round-2 forward-carry is not yet written anywhere a later stage reads it. The beat's SIGTERM handler TERMs running groups and never escalates, so a TERM-ignoring descendant can outlive a stopped beat. That belongs in arm (b)'s brief as a precondition. The R10-ORCH-BEATD group on origin/main 0265f524e, and on roster ref 528413331, has no carry or brief text naming it (I searched the group's full JSON for `SIGTERM handler`, `escalat` and `surviv`: 0 hits). The body says the orchestrator owes the write through `roster_edit.py` before this PR merges, because the repair seat may push only its return refs. I return `merge` on that basis: no fixer push can settle it, and this bullet routes it. The merge train still owes the roster write before the merge, per finding-propagation.md. Carry: R10-ORCH-BEATD
- Seven of round 2's reviewer plants are deferred in the body, not pinned: y2 (`Lock.drop` ftruncate), y3 (`$S` substitution), y6 (shim retries `pull`), y7 (shim exports `HPO_REAL_GIT`), y9 (duplicate job names), y13 (idle hides a failed watch outcome) and y14 (shim skips `-c <value>`). No production line or case for them changed since ca2dc27d7, so they still survive by construction. I did not re-run them. Each is correct behaviour at this head and unpinned. Owed: a case arm and a `MUTANTS` entry each, in arm (b), whose brief reopens the self-test. Carry: R10-ORCH-BEATD

## Evidence

- **The block is answered.** RESULT lines come from round 2's harness, `ev/ymut.py`, unchanged (sha1 e6d3da28608e6f4feb916462aff6e320f8ba945f, which matches the body). The run was `ONLY=y1_kill_group_no_grace,y16_grace_half_second`, at the head, under /opt/hpo/venv-ci with no committer identity (`ev/ymut-y1-y16-head.txt`):
  - `BASELINE (3) 8 checks, not-true: []`
  - `RESULT y1_kill_group_no_grace: KILLED; red=['(3) a TERM-ignoring grandchild is killed after its leader exits']`
  - `RESULT y16_grace_half_second: KILLED; red=['(3) a TERM-ignoring grandchild is killed after its leader exits', '(3) null: a leader ignoring TERM too is killed at the grace, rc -9']`
  - Both results match the body's null-control figures exactly. The baseline row is the null: the unmutated grace passes the new bound.
- **The bound is sound.** Case (3) runs in-process from the unmutated module (`_run_case` calls `CASES[case](prog, w)`), and only the beat itself runs from the planted copy. So `graced()` reads the real `KILL_GRACE_S = 10.0`, and a plant on the constant cannot move the bound. `dur` is `int(time.time() - t0)`, taken at `run_one` after `supervise` returns and the job lock drops, with `kill_at = now + KILL_GRACE_S` set at `now >= t0 + 2`. A correct beat therefore reads `dur >= 12`, inside `[12, 17]`.
- **My own plants on the same seam** (`ev/zmut.py`). This is my instrument, not the finder's: round 2's harness with z1 to z5 added. Results are in `ev/zmut-head.txt`. All five KILLED, none crashed, with a clean baseline:
  - `z1_kill_group_now`: `kill_group(p.pid, kill_at)` becomes `kill_group(p.pid, time.time())`, so the grace drops at the call site and not in the poll. Red: the stubborn arm.
  - `z2_grace_twenty`: `KILL_GRACE_S = 20.0`, so the grace is too long. Red: both arms, through the upper bound.
  - `z3_live_kill_at_one`: `kill_at = now + 1` in `supervise`. Red: both arms.
  - `z4_live_early_kill`: the live-leader SIGKILL fires at `kill_at - 9`. Red: the null arm.
  - `z5_group_poll_skips_to_kill`: `kill_group`'s poll body becomes `break`. Red: the stubborn arm.
  - Together these show that both paths' grace is pinned from both sides, not only against the two named plants.
- **The self-test at the head.** The command was `HOME=<empty> GIT_CONFIG_GLOBAL=/dev/null /opt/hpo/venv-ci/bin/python -I tools/audit/seat/beatd.py --self-test` (Linux, Python 3.14.7). It printed `beatd self-test: 119 checks, 0 failed`, rc 0, 282 s wall (`ev/selftest-head.txt`). Under the body's rule the `grep -c` counts are 65 `ok   (`, 27 `ok   anchor` and 27 `ok   mutant`. That re-derives the body's 119 = 65 + 27 + 27 and its 27 plants, each `ok`, including `m3_kill_group_no_grace` and `m3_grace_half_second`. The body gives 278 s; this host gave 282 s.
- **Merge.** `git merge-tree --write-tree origin/main 2f8a97c83` against origin/main 0265f524e exited 0, tree cbeb41899 (`ev/merge-tree.txt`). Its stderr is `LEDGER-MERGE: resolved tests/closures.json` (`inert_reads.tests/entities.py` merged as a set). No `MERGE-CLAIM` line appeared, and no claim file is in the diff.
- **Cheap checks at the head** (`ev/cheap-checks.txt`):
  - `selftest_wiring.py --check`: `100 self-testing, 100 wired, 0 unwired`.
  - `throwaway_git.py --check`: `0 raw git init or clone site(s) refused, 0 stale allow entries`.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
  - `structure.py`: `STRUCTURE RATCHET PASSED`.
  - `closure.py select --diff 6493ea362`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`.
  - `archscore --diff 6493ea362 HEAD`: `Architecture score: dS +0.0000 NULL`.
  - `entities.py` (venv-ci 3.14.7): `ALL 2470 ENTITY CHECKS PASSED`.
  - `harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - Step 5: `git diff --stat 6493ea362...2f8a97c83 -- VERSION tests/golden custom_components RELEASE_NOTES.md` is empty.
- **CI on this head** (`ev/check-runs.txt`, check-runs API, re-read at about 01:15Z):
  - The one failure is `governance / delivery-status`. Its log reads `DELIVERY STATUS OVERDUE -- 18 rowed, 12 pending, 6 overdue`, and every overdue row is another PR's. This PR adds only its own row. The body names and answers it. It is not a required check and does not block.
  - closures, coverage, fast (3.14), mutation, policy-docs, env-matrix, arch-score and budget-raise-gate are green.
  - Still running at read: `governance / instrument-self-tests` and `codeql / Analyze (python)`. Queued: graders-head-copy, lane-proofs and coverage-ratchet.
  - No `pr-contract` or `gate` run is listed on this head. Step 11's red-check answer therefore rests on the body's `## Red checks` and not on a pr-contract run.
  - `tests / mutation` is green. This diff's head commit writes no production line, so the lane draws no mutant from it. The mutation evidence above is the self-test's and mine.
- **Step 6, the class.** The body enumerates `supervise`'s exits. Both grace paths are now pinned (above), and the SIGTERM-handler gap is carried under `## Findings`.
- **Figures I did not re-derive:** prepr's 29/9/0, the 688 s serial control, #2873's 16 min 32 s job, the macOS bash 3.2 run at f008c2b75, and the body's failing-test-first run on its working tree before 6fd9984a7.
- **Harnesses.** The packet names no finder harness. Round 2's `ymut.py` is the block's finder harness. It is reproduced in `ev/` unchanged and gives the body's figures. `ev/zmut.py` is my own instrument, disclosed as such.
