Fix review: blocked 0a459e607bd7de54e7a80233ee8f15e550256d77 class-open: tests/finite_boundary.py still fails host-zone checks at the head under America/New_York (1 of 108) and Asia/Kolkata (2 of 108), and passes under UTC

bus-nonce: 1da1bf49ae825a4da6b38bfe7c2c50c2

## Head

I measured 0a459e607bd7de54e7a80233ee8f15e550256d77, the head the dispatch names and the head `## Head` names. `git ls-remote origin refs/pull/3170/head` re-read the same head at the end of the review. This is round 2, a delta review of the round-1 block at b307f359. Merge base and origin/main are both 3905069f38a60559186fef916b0241e311cc81cd. I judged the change only through the three-dot diff. The PR's own round-2 commits are 332127330, 7108d8478, 8f2bcb30a and 4119c8982; ba8593ecf and b307f3599 are round 1's.

## Block

1. **class-open: tests/finite_boundary.py.** The brief's scope (1) asks for features.py "and the suite scripts that read host time" to pass under every listed zone. The PR body's class rule only enumerates features.py checks. At the head, features.py now passes everywhere. finite_boundary.py does not:
   - `HASTUB_TZ=TZ=America/New_York`: `1 of 108 FINITE BOUNDARY CHECKS FAILED`, on "no stored instant reaches a loader beyond the clock plus its store's lead". Escaped instants include `thermal_learning:updated_at` and the `__instant_probe` and `__instant_probe_aware` leaves of every store.
   - `HASTUB_TZ=TZ=Asia/Kolkata`: `2 of 108` failed, on "an honest payload comes back byte-identical (null control)" (12 stores rewritten) and "an instant inside its store's lead survives the load" (lead lost for manual_plan, boost, accuracy and snapshots).
   - UTC: `ALL 108 FINITE BOUNDARY CHECKS PASSED`.

   The merge base reads the same counts (New_York 1, Kolkata 2), so this predates the PR. It is the same shape as the four features seams fixed here. `_instant_arm` freezes a naive `t0 = datetime(2026, 6, 1, 12, 0, 0)` (tests/finite_boundary.py:1430), which the stub reads as configured-zone wall clock. The arm's own `_utc` (tests/finite_boundary.py:1363) then reads the naive probe leaves as UTC. America/New_York is one of the four zones the body itself claims to cover.

   The PR is titled "suite host determinism", and the brief requires all scripts to pass at the head. Either fix the arm by the PR's own pattern, or have the owner scope the class to features.py explicitly in the body and route finite_boundary as a named next part. If you fix it:
   - name `t0` in `DEFAULT_TIME_ZONE`, or make it aware, and have `_utc` adopt the configured zone for a naive leaf, whichever production's loader actually does;
   - settle per check whether production or the test is wrong;
   - add a mutant to `host_zone_features.py` or an equivalent harness that runs finite_boundary under the four zones plus a half-hour zone.

## Findings

- tests/finite_boundary.py fails under a non-UTC `HASTUB_TZ` at the head and at the base: New_York 1 of 108, Kolkata 2 of 108, UTC all passed. The cause is a naive frozen clock against a checker that reads naive leaves as UTC (Block 1). Carry: R10-SUITE-HOST-DETERMINISM
- No CI lane runs any suite script under a non-UTC `HASTUB_TZ`. `grep` over `.github` and `tests/run.sh` finds no assignment, so the zone fixes in this PR are guarded only by the out-of-gate harness `dev/audit/harnesses/host_zone_features.py`, which its docstring says is minutes per zone. A later edit can reintroduce a UTC-literal instant and stay green in CI. Consider a cheap one-zone lane (for example Asia/Kolkata, which is half-hour and far from UTC) on features.py and finite_boundary.py, or record the decision not to build one. Carry: R10-SUITE-HOST-DETERMINISM

## Evidence

- Contract currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, because the merge base equals origin/main.
- RESULT features.py at the head (`PYTHONPATH=tests/hastub python3 tests/features.py`, my own runner ev/runz.sh, not the fixer's harness). Each row is in ev/features_*.summary.txt:

  | zone | result |
  |---|---|
  | UTC | ALL 4770 passed |
  | America/New_York | ALL 4770 passed |
  | Asia/Tokyo | ALL 4770 passed |
  | Europe/Stockholm (TZ set too) | ALL 4770 passed |
  | Asia/Kolkata (half-hour) | ALL 4770 passed |
  | Australia/Sydney (DST in force at the January and February instants) | ALL 4770 passed |

  Round 1 read New_York 3 of 4770 and Tokyo 3 of 4770 at b307f359. The round-1 block on features.py is settled.
- RESULT mutation proof, my own worktrees at the head, each with one fixed site restored to its host-zone read. Each mutant failed exactly its own check, 1 of 4770, and nothing else:
  - nometer_month (`zone = _BO_TZ`) under New_York: KILLED.
  - sysid_night_t0 (`tzinfo=UTC`) under Tokyo: KILLED.
  - outage_naive_tick (naive UTC wall clock) under New_York: KILLED.
  - humidity_now (naive `_T6_HUM_NOW`) under Tokyo: KILLED.

  The unmutated head runs above are the null control. The body's mutation figures agree.
- RESULT root cause, not a pin: the three-dot diff adds no `TZ` or `HASTUB_TZ` assignment in the suite or the runner. The only assignment is in the harness's own subprocess env (host_zone_features.py:80), by design. Each fix names the instant in `DEFAULT_TIME_ZONE` or makes it aware.
- RESULT other host-time scripts at the head under New_York and Kolkata (ev/other_scripts.txt):
  - block_duty, config_flow_steps, rolling, manual_plan, solar_alignment and open_meteo pass in both zones.
  - entities passes under Tokyo and Kolkata (ALL 2593).
  - ha_contract reads 4 of 96 failed whenever `HASTUB_TZ` is present, UTC included. Its default-case contracts assert that the variable is unset (tests/ha_contract.py:2349), and with it unset it reads ALL 96 passed. That is by design, not a zone defect.
  - finite_boundary fails: see Block 1.
- RESULT coordinator.py: the 4-line change is still in the three-dot diff and is explained in the body. With docstrings blanked, the AST hashes match at base and head (ev/coordinator_ast.txt). The function returns `dt_util.as_local(ts).replace(tzinfo=None)`, so the new docstring matches the code.
- RESULT harness commits, read line by line:
  - 8f2bcb30a replaces the `git archive` copy with a detached worktree and removes it in `finally`.
  - 4119c8982 replaces `parents[3]` with the manifest-walk `repo_root`. The redundant inner `from pathlib import Path` is cosmetic.
  - 7108d8478 adds the harness to `tests/closures.json` under `inert_reads["tests/harness_headers.py"]` (verified by walking the JSON).
  - The three-dot diff touches neither `tests/harness_headers.py` nor `tests/closure.py`, and adds no allowlist entry. CI `tests / closures` is green at this head.
- RESULT standing checks (ev/standing.txt):
  - `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to origin/main.
  - VERSION, manifest.json and RELEASE_NOTES.md are byte-identical.
  - The three-dot diff contains no `*_budgets.json`.
  - No host path appears in the added lines.
  - The delivery row dev/programme/delivery/3170.md is in the three-dot diff.
  - `git merge-tree --write-tree origin/main 0a459e60` exits 0, with no conflict.
- RESULT CI at this head: `merge_train.py classify 0a459e607bd7de54e7a80233ee8f15e550256d77 --pr 3170` printed `GREEN 0a459e607bd7de54e7a80233ee8f15e550256d77 pending: none red: none` (rc=0; ev/ci_classify.final). No check is red at this head, so `## Red checks` owes nothing new here. Its answers for b307f359's replay, pr-contract and gate reds are present.
- The gate-lease `_free_slot` TOCTOU from round 1 is routed in the body's `## Forward-carry` to this group's Carry 2 on handoff/audit-r10-roster. I did not re-measure it, because round 2 does not touch tests/gate_lock.py.
- Figures I did not re-derive: the fixer's harness runs at 8f2bcb30a, and the round-1 coverage and gate-lease figures the body carries. My own runs above supersede the features figures.
- Disclosure: ev/runz.sh and ev/runs.sh are my own runners. The four mutants were built by hand at the same sites the fixer's MUTANTS table names.
