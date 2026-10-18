Fix review: blocked 2d9f2000967579f577940a0eb4842d0a76867aec root-cause-unanswered: wave-script went red, unanswered

bus-nonce: d16dc004951182a5a3db7a02422a670b

**Round 6.** This is the sixth `Fix review:` verdict on #2406. Rounds 1 to 5 blocked at `a7d97f55b`, `89d2b9465`, `af391637b`, `b965c4ab9` and `d1becac2b`.

I reviewed from a detached worktree at `2d9f2000967579f577940a0eb4842d0a76867aec` (`ev/HEAD`). `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` was empty, so my copy of the contract is current. Origin/main is `07a09406a`, which is also the merge base. I judged the delta since round 5 (`d1becac2b`):
- the fix commits `8baa13e47` (the pin) and `cfd418c71` (the allow entry);
- the merges `c31f842d8`, `42a8c31a8`, `6b43b20f7` and `2d9f20009`.

## Why it is blocked: two reds on this head, and the body names neither (step 11)

Every workflow on the head has concluded (`ev/checkruns-final.tsv`, check-runs API, read at 21:39Z). Three runs are red:
- `wave-script`, concluded 20:31:48;
- `delivery-status`, concluded 20:31:34;
- `pr-contract`, twice.

The later `pr-contract` run, 117782745460, started at 20:34:17. That is after the other reds concluded, and it checked the body (`ev/pr-contract.log`, lines 1574-1580). It refuses with `PR-BODY: 2 error(s)`: `` check `wave-script` is red and `## Red checks` does not name it ``, and the same for `delivery-status`. So step 11's posting condition holds, and the body is silent on both.

Both reds are main's, not this PR's. The block is only on the missing answer:
- **`wave-script`** (job 117782075880) fails on `pair merge-subject-pr: ... 2 divergent`. The two divergent subjects are main's custom merge subjects for #2401 and #2379. This is exactly the main red from `5756f2b1` named in the dispatch, with the fix in flight as R10-MERGE-SUBJECT. This PR's diff does not touch the readers that disagree.
- **`delivery-status`** (job 117782075575) prints `DELIVERY STATUS OVERDUE`. The overdue rows are main's own autofix records: #2413 `be2d367`, #2412 `003c373` and #2407 `3126b86`. The step-11 exemption ("not this pull request's unless its diff reaches what they read") is arguable here, because `pr-contract` notes the diff touches `tests.yml`. On the measurement, though, the OVERDUE set holds nothing of this PR's.

**Remedy: a body edit, with no code change.** Add both checks to `## Red checks` as main's, each with its cause:
- `wave-script`: the `merge-subject-pr` divergence from `5756f2b1`, fixed by R10-MERGE-SUBJECT;
- `delivery-status`: OVERDUE on #2413, #2412 and #2407.

Then let `pr-contract` re-run on the body edit. The head does not move, so every measurement below carries.

## Round-5 blocker: fixed, and pinned

- **At the head** (`ev/entities-head.txt`, `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`, Python 3.14.7): `ALL 2349 ENTITY CHECKS PASSED`. In round 5 the same command gave `3 of 2347 FAILED`.
- **M1** (`ev/m1.diff`): I removed the planted repo's copy of `tests/closure.py` from `_pt_trigger`. Result (`ev/entities-m1.txt`): `2 of 2349 ENTITY CHECKS FAILED`. The failures are `and the arm's trigger fires on a restored path and only there` (`outputs=[]` on all three planted paths) and `and a trigger whose firing branch writes false is refused (null control)`. This matches the body's M1 and is round 5's failure, reproduced.
- **M3** (`ev/m3.diff`): I set `_PT_JOB_CANON`'s line back to `git diff --name-only "$BASE"..."$HEAD"`. Result (`ev/entities-m3.txt`): `2 of 2349`. The failures are `every pinned grader given a token runs its own copy ...` and `and any edit to the arm's job ... disarms it (null control)` (`mismatch at head: graders-head-copy.steps[2].run`). This matches the body's M3.
- **Head-copy sanity.** The other `FAIL` lines in those logs are the harness's own planted controls, which print at the head as well. The totals separate them.
- **CI agrees.** `graders-head-copy` concluded success, and `fast (3.14)` concluded success at 21:14:37 (it was red at `d1becac2b` in round 5).
- **The step it pins.** `tests.yml:1939` runs `python tests/closure.py changed ...` inside `graders-head-copy`. That job already runs the pull request's own copies by design (`pull_request` event, `HPO_JOB_GRADES: nothing`), so running head's `closure.py` there grants no new privilege. Under `set -euo pipefail`, a broken copy fails the job closed.
- **MS** (`ev/mutants-cheap.txt`): I changed `rename_sites`' stale list to `if False`. Result: `1 of 124 closure shrink pins FAILED` (`and reports every allow entry nothing matches as stale`). This matches the body.
- **MP, MB15, MB17 and MB19** I re-ran in rounds 4 and 5 on code this delta does not touch. I did not re-run them here.
- **M2** (no `python` on `PATH`): not re-run. The body discloses it as unpinned on any box with `python` on `PATH`, and that disclosure is accurate.

## Body figures re-taken at this head

The body took its figures at `42a8c31a8`. I re-took them at `2d9f20009` (`ev/cheap-head.txt`, `ev/cheap-head2.txt`), and each matches:

| check | result at the head |
|---|---|
| closure selftest | `ALL 124 closure shrink pins PASSED` |
| `closure.rename_sites()` | `([], [])` |
| lane_skip | `54/54 pins passed` |
| codeql_scope `-I` | `47 checks, 0 failed` |
| roster_lib | `18 checks, 0 failed` |
| orchestrator_tick | `104 checks, 0 failed` |
| state_docs | `all checks passed` |
| stamp | `RESULT stamp_self_test=pass` |
| policy_lint | `TOTAL: 0 error(s) across 41 policy file(s)`, no `VACUOUS` |
| structure | `STRUCTURE RATCHET PASSED` |
| env_drift `--claims-only` at the merge base | `claims hygiene: ... ok` |
| layout `--guard` | `GUARD: 0 refusal(s)` |
| throwaway_git | `0 ... refused` |
| tmp_paths | `0 refused` |
| codeowners_gap | `uncovered_files=0` |
| harness_headers | `ALL 109 HARNESS HEADER CHECKS PASSED` |
| archscore `--diff` at the merge base | `dS +0.0000 NULL` |

## Other steps

- **Merges** (`ev/merges.txt`): `c31f842d8`, `42a8c31a8`, `6b43b20f7` and `2d9f20009` each have a tree equal to `git merge-tree --write-tree` of their parents, so none was resolved by hand. `git merge-tree --write-tree origin/main(07a09406a) 2d9f20009` returns rc 0 with no conflict, because the head already contains main.
- **Head** (steps 7, 12): the body's `## Head` matches the commit graph:
  - `2d9f20009` has parents `6b43b20f7` and `07a09406a`;
  - `6b43b20f7` has parents `d1becac2b` and `42a8c31a8`;
  - `42a8c31a8` has parents `cfd418c71` and `5756f2b15`.
  - The PR head was `2d9f2000967579f577940a0eb4842d0a76867aec` when I wrote this.
- **Version, claims and budgets** (steps 4, 5, 14): `VERSION`, the manifest, `RELEASE_NOTES.md`, the claim files, the goldens and every `*_budgets.json` are untouched. `tests/closures.json` moved only through the `closures-autofix` bot commit, as round 5 found.
- **Class** (step 6): the census (`rename_sites`) returns nothing at the head. The deleted `RENAME_ALLOW` entry is gone because its line is gone, and the stale-entry pin now plants `tools/policy/policy_lint.mjs` (MS kills it).
- **Forward-carry** (step 10; `ev/carry.txt`, `origin/handoff/audit-r10-roster`): `R10-TICK-DRIVERS.carry` holds the beat restart with its control (two SHAs in the memo, plus a roster-only regenerate within one beat). It also still holds the CodeQL-delegation item. This PR has done that work (MB17), so the orchestrator should drop the item from the roster at merge.
- **Earlier reds in the range** (step 11): `fast (3.14)`, `closures` and `nightly-ha (stable)` are named and answered in the body's `## Red checks`.
- **Rounds:** this is the sixth. The product and its pins hold. What remains is the body edit above.
