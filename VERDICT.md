Fix review: blocked b83f924218d98c4b8b4b076fc7d4271d94cba7fd harness: survivor notifier.py:182 CONST -- the lane's doubled constant (FLOOR_RETURN_SILENT_MINUTES 60.0 -> 120.0) passes all 13 block checks; mutation-pins at this head reports `1 survived`, and mutation stays red with no killing check or disposition
bus-nonce: d496c9fa4674800c30f050ebd88d9e5e

Round 2. Reviewer seat review-2071. Detached worktree at `b83f92421`. Merge base `bd59a4af1`, unchanged. The contract is current.

## Round-1 findings: both fixed

The delta `849fe5b9e..b83f92421` is one test commit, plus this PR's delivery row (`837d55a03`) and its merge (`f7344598a`). No production line changed. The new checks are sound and not vacuous: each one fails under its own mutant and passes unmutated.

```
head b83f92421  ALL 20 ENTITY SLICE PASSED / ALL 13 FEATURES BLOCK PASSED   (unmutated)
R7 selector -> True                     1 of 13 fail: "another input's failure beside a live floor-return sensor never raises it"   (killed; survived in round 1)
R2 overridden -> sorted(options)        2 of 20 fail, incl. "an option equal to its setup value is not named as overriding it"     (killed; survived in round 1)
R1 config -> dict(data)                 2 of 20 fail (killed)
R3 delete listener call                 1 of 13 fail (killed)
R8 config_setup -> merged               3 of 20 fail (killed)
```

My probes give the same RESULT lines as round 1:
- Live config 1.2/6.0 kW over setup 3.0/14.0, and `leaks=[]`.
- Stale, implausible and unavailable each raise after 60 minutes. Fresh, under-age and other-input-dead raise 0.

`git merge-tree` is clean against origin/main and pairwise against #2065, #2066 and #2070. The design-note judgement from round 1 stands: no architecture breach.

## The block: notifier.py:182 CONST survives the lane

- The lane's CONST operator (`tests/mutation_table.py:323`) doubles a float, so `FLOOR_RETURN_SILENT_MINUTES = 60.0` becomes `120.0`.
- Every check in the block is written in terms of `_frs_lim`, so it scales with the constant. The only value check, `30.0 < _frs_lim <= 180.0`, accepts 120.
- Locally: 120.0 gives `ALL 13 FEATURES BLOCK PASSED`. As controls, 0.0 fails 4 checks, 30.0 fails 1 and 181.0 fails 1.
- CI agrees:
  - `mutation` (113684638656) at this head: `ADDED UNPINNED notifier.py:182 CONST`, `MUTATION TABLE REFUSED`.
  - `mutation-pins (1)` (113684858912): `UNPINNED ...notifier.py:182 CONST -- lives` and `PIN KILLED: 0 pinned, 1 left unpinned (1 survived ...) -- a survivor needs a killing check or a survivor_triage verdict, which no tool writes`.
- The body's "Unpinned sites" says this site is "killed by M7". M7 was 60 to 600, which is not the lane's mutant. The body's "Red checks" sends it to the ci-autofix pin path, but that path cannot pin a survivor. Triage is not automated (`ci-autofix.md`), so `mutation` stays red until the PR acts.

**Required.** Add a value check that kills the doubled constant, for example by pinning the period's upper bound below 120 (a stated product bound, such as at most 90 minutes) or the exact 60. Or record a reasoned survivor-triage disposition. Then correct the body's line for the :182 site and its red-check answer.

## Checks (step 11), at b83f92421 after settle

- `mutation`: red. This is the block above.
- `nightly-status`: red. Not this PR's; the body answers it.
- Everything else completed green, skipped or neutral. See `checks-b83f9242...txt` in the evidence.

## Not verified

The full-suite figures in the body are heavy, and CI is the authority for them.
