Fix review: merge 4dc59c5991d238ff2fcccd16d81b91d7a1ea25c6

bus-nonce: 11be08f45b2306815564eebaee500cca

## Verdict

This is round 3 of the review of PR #3231, the seat re-author of outside contribution #3224 (contributor Bankaifan). Round 2 blocked the previous head `bd0ee867e49bf6f0af414efcf2aa29ae775ac926` as mutation-vacuous on mutant m4. I measured head `4dc59c5991d238ff2fcccd16d81b91d7a1ea25c6` against base `c679f4b692f483959769ec5b5147aa4d624c45f4` (= origin/main).

The repair is one test-only commit, f7ed411fc, which adds 20 lines to tests/features.py: a new check for a degF water_heater slot. It kills m4. The production code is unchanged since the reviewed bd0ee867. My round-2 verdict found no defect in inputs.py, config_flow.py or the strings, and that judgement stands. The mutants m1, m2, m3 and m6 are still killed. CI is GREEN on this head, and the PR merges cleanly with main and with the overlapping PRs.

## Findings

- Non-blocking body gap: `## Red checks` still says "The final head is not pushed to the pull request yet, so it has no check-runs". The head has now concluded all its runs. The only red is `tests / nightly-status` (main's scheduled `slow` lane, run 41943946464, head 499162c, not required). That red is already named in the same section with its cause and owner. Carry: dismissed: stale wording only; the red is named and answered, and merge_train classify reads GREEN with no required red at this head
- Non-blocking: the body's figures for the contributor's own head (4831) still come from the contributor and are disclosed as such. At this head the count re-derives as 4860, and main reads 4858. Carry: dismissed: contributor figure, disclosed; re-derived counts are in Evidence

## Evidence

- Round: 3. Head re-read before return: `git ls-remote origin refs/pull/3231/head` = 4dc59c5991d238ff2fcccd16d81b91d7a1ea25c6, the head I measured (`ev/HEAD.txt`).
- Contract check: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the role file is current.
- Patch identity: `git diff $(merge-base origin/main refs/pull/3224/head) refs/pull/3224/head | git patch-id --stable` = `9f2a529790894cb7c085bf59ae375e8521e0cbbe`, the same as `git diff d1153ae86~1 1fe34a84f`. The three commits are authored by Bankaifan (`ev/identity.txt`).
- `## Head`: the body names the fixer's handoff `b3bb708c05a3bfb54797cb62f0cedf6a48c8d763`.
  - The dispatch head 4dc59c59 is a merge with parents bd0ee867 and b3bb708c.
  - `git diff b3bb708c 4dc59c59` is empty, so its tree is identical to the handoff's.
  - Since bd0ee867, the code and test delta is `tests/features.py | 20 +` only (f7ed411fc, author hpo-fixer, no attribution trailers).
- RESULT features (`PYTHONPATH=tests/hastub python3 tests/features.py`): 4860 checks at head = main's 4858 + 2.
  - Head: `ALL 4860 FEATURE CHECKS PASSED` rc=0 (`ev/features-head.log`). This is the null control on the unmodified head.
  - Main: `ALL 4858 FEATURE CHECKS PASSED` rc=0 (`ev/features-main.log`).
- RESULT mutants, each applied in its own worktree at the head (diffs in `ev/mutant-m*.diff`, failing checks in `ev/mutants-summary.txt`):
  - m4 (`_ATTRIBUTE_TARGET_DOMAINS = ("climate",)`, inputs.py:467): `1 of 4860 FEATURE CHECKS FAILED` rc=1. The failing check is the new "a water_heater DHW set-point on a degF instance reads its range in degC and is clamped to it", which reads `{'range': (86.0, 149.0), 'clamp above max': 86.11…, 'clamp below min': 86.11…}`. **Killed.** Round 2 recorded 0 failed at bd0ee867.
  - m1 (drop water_heater from SETPOINT_SERVICES): 2 failed, the #1526 service-table check and the contributor's water_heater check.
  - m2 (drop it from _RANGE_KEYS): 2 failed, the contributor's check and the new degF check.
  - m3 (drop it from _STEP_KEYS): 1 failed, the contributor's check (step 1.0, write 52).
  - m6 (GUARD_OFF `if False:` at inputs.py:478): 4 failed, the three climate checks plus the new degF check. This now matches the pin reason's `failed=4` in setpoint_unit.GUARD_OFF.d9727610.json, which settles the count follow-up from round 2.
  - Every count above matches the body's mutation-proof section.
- RESULT `python3 tests/mutation_table.py --pin-killed --base origin/main` at the head:
  - Output: `PIN KILLED -- 0 new unpinned site(s) against c679f4b6… to drive`, `PIN KILLED: nothing to pin`, `3091 unpinned site(s) of 6799 candidate sites, 3091 at the ratchet base` rc=0.
  - The worktree was clean afterwards (`ev/pin-killed-head.log`).
- RESULT env_drift (`python3 tests/env_drift.py --all c679f4b6…` at head): `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)` rc=0 (`ev/env_drift-head.log`).
- Golden claim (a–e), re-verified three-dot against origin/main:
  - (d) Only tests/golden/claimed_drift.txt changed, with 5 insertions: the claim line `config_flow  # R10-EXT-3224: … gains water_heater (2 leaves, nothing else moves)` and a 4-line note. card_claimed_drift.txt is untouched.
  - (b) `claims-for: 7.1.1` = VERSION 7.1.1.
  - (c) config_flow is not may-drift, and env_drift accepts the pair (rc=0).
  - (e) config_flow.json changes 2 lines out and 2 in: the plain and seeded `dhw_setpoint_entity.config.filter`. No other fixture moves.
  - (a) The cause is the config_flow.py:1667 selector edit. Round 2's m5 showed this, and this round changed no production code.
  - config_flow is float-free and compared exactly at level 1, so the claim is #547's established practice rather than a value-bearing drift.
- VERSION, manifest.json and RELEASE_NOTES.md are untouched in the three-dot diff.
- RESULT structure: `STRUCTURE RATCHET PASSED` rc=0 at head and at main.
- RESULT entities: `ALL 2632 ENTITY CHECKS PASSED` rc=0 at head and at main.
- Merge simulation (`git merge-tree --write-tree`, claimnotes driver installed; `ev/merge-tree.txt`). Every simulation exits 0:
  - origin/main c679f4b6.
  - PR 3220 e70dfd64.
  - PR 3198 a96762c0, with `MERGE-CLAIM: resolved tests/golden/claimed_drift.txt`.
  - PR 3226 ba704972.
- CI on this head:
  - `python3 tools/audit/seat/merge_train.py classify 4dc59c59… --pr 3231` exit 0: `GREEN 4dc59c5991d238ff2fcccd16d81b91d7a1ea25c6 pending: none red: none` (`ev/ci-classify.txt`; it was WAIT on `gate` until 04:18 UTC).
  - All 39 check-runs fit on one page. The only concluded red is `tests / nightly-status`. Its log reads `NIGHTLY FAILED: slow failed 1 night ago`, scheduled run 41943946464 on main's head 499162c. It is not a required context, this diff does not reach it, and the body names it.
- Figures not re-derived: the contributor's 4831 (from their own head).
