Fix review: blocked a942da87b28a2ec60cf29717754c6a663c9f4efe ci-cancelled: code run 42533669919 cancelled before tests/fast, mutation, coverage, closures, replay concluded; gate red, classify RED

bus-nonce: 7361c1f3ba9eb3d64b0c982abfafadc5

## Block

`merge_train.py classify a942da87b28a2ec60cf29717754c6a663c9f4efe --pr 3347` exits 1: `RED a942da87b28a2ec60cf29717754c6a663c9f4efe pending: none red: gate` (ev/ci-classify-final.txt). This head has two CI runs. In the edit run 42533670001, `gate` concluded failure at 23:14 with `FAIL run(s) [42533669919] at this head are still being judged; their gate decides`. Then the code run 42533669919 was cancelled at 23:21:03-05. No job in it failed. `tests / fast (3.14)`, `tests / mutation`, `tests / coverage`, `tests / closures`, `tests / replay`, `tests / browser`, `governance / instrument-self-tests` and `codeql / Analyze (python)` were all cancelled together, and so were its `gate`, `mutation-autofix`, `claims-autofix` and `closures-autofix`. The branch and `refs/pull/3347/head` both still read a942da87b, and no newer run exists on this head. So the gate's suite (features, golden, env_drift and the mutation ratchet are all in the closure) has no conclusion at this head, and a red CI never yields `merge`. Nothing in the authored work is defective, as far as this review can see (below). A re-run of the CI code run on this head, then a re-dispatch, is what is owed; the patch is unchanged, so the review below stands for it.

## Findings

- Out of scope: the space solve's seed is the thermostat reference, and it is capped only at `max_electrical_power`. Where `h.power_caps` bounds a step below the pump (space-blocked and off steps, `_build_space_power_caps`), `seed_power` still lies outside that step's bound. That holds at main too: `np.clip(seed_power, 0.0, p_max)` never read `power_caps`, so this diff neither causes nor changes it. Neither the new code comment ("inside the bounds: the reference never passes the pump") nor the check name ("the reference seeds the space solve only inside its bounds") says that it holds only where no power cap binds. L-BFGS-B clips x0 itself, so the cost is in the candidate scoring, which scores an out-of-bound point. Read from code, not measured. Carry: R10-SAV-COMFORT
- Follow-up: the review packet names no finder's harness for items 0497bde5 / fc24128d. The 1.226x figure is reproduced in-tree by the new check: under mutant M2 (main's uncapped line restored at this head), the check reads `reference peak 3.678331746510925 kW against 3.0`, so the measurement is committed. Carry: dismissed: the committed features check reproduces the finder's 3.678 kW / 3.0 kW at main's line

## Evidence

- Head measured: a942da87b28a2ec60cf29717754c6a663c9f4efe, still the head at ls-remote after the CI wait. Its tree is byte-identical to the authored code head 682edb35c (`git diff --stat` is empty), as the body's `## Head` says. Merge base 661d26a5d. Round: first review of this head.
- Roles current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main a942da87b` exits 0 against origin/main 425b85849 (ev/merge-tree.txt). No claim file is touched, so no driver ran.
- VERSION, the manifest version and the notes heading are untouched. The diff is optimizer.py, features.py, the delivery row and 6 ledger files.
- Mutation proof, run through `tools/audit/seat/features_block.py` with the body's preludes, `PYTHONPATH=tests/hastub`, each mutant restored after (ev/mutants.txt, ev/mut-*.txt):
  - RESULT M0 as committed: rc=0, 14 checks pass in the valve block and 14 in the settlement-wiring block.
  - RESULT M1 `~held & (spread >= cap)`: rc=1. Fails `a step spread exactly to the pump keeps the spread`, reading [1.5, 1.5, 1.5, 1.5], as the body says.
  - RESULT M2 main's uncapped spread restored: rc=1, 3 checks red (bounds, cap/energy, held-step share), peak 3.678 kW on the 3.0 kW pump.
  - RESULT M3 clamp after the spread (the body's rejected alternative): rc=1, 2 checks red.
  - RESULT M5 no subtraction of the held energy: rc=1. RESULT M6 the all-held fallback returns the pump: rc=1. RESULT M9 the steady-demand floor at 0 dropped: rc=1.
  - RESULT M7 `zone = lowers` to `zone = rooms` (carry 11, item 435eb685): rc=1. Both new two-zone checks are red, so the surviving mutant is now killed.
  - Null controls: RESULT M4 (an equivalent rewrite of `held |= over`) rc=0. RESULT M8 (the seed clip re-added) rc=0, so the clip is dead code once the reference is capped, as the body says.
- Termination and sign, reviewer's own argument: each pass returns or holds at least one new step, so there are at most n passes. Any step over the cap means the unheld remainder E - cap*(k+m) is greater than 0, so no step is spread negative.
- Harnesses re-run by this seat at the head and at the base 661d26a5d, identical at both ends (ev/harness-wt.txt, ev/harness-wtb.txt). `r10_sav_wood_reference.py valve-flat` gives residual -3.90 %, SOUND. `r10_sav_null_settled.py` gives const +0.28 % and vary +14.28 %, both SOUND. These match the body. The printed `rc=` lines there are `tail`'s; read the SOUND lines.
- Structure: `python3 tests/structure.py` passes at the head (STRUCTURE RATCHET PASSED; ev/structure.txt). Gate scope at the head: SCOPED, 27 scripts run and 6 scoped out, as the body says.
- Not re-derived: the unpinned-site count (2755 against 2755), `ALL 4984 FEATURE CHECKS PASSED`, `r10_sav_baseline.py null`, `r10_sav_null_terms.py`, `r10_partload_pricing.py`, and env_drift/golden drift. These are CI's heavy runs, and the run that would carry them at this head was cancelled.
- Forward-carry: the body says none. Its open carries (6, 9, 20) stay on the roster. Items 476710bb and 0497bde5 are in `dev/programme/rosters/wave-r10-groups.json` at the head. Item 213e8a10 is on `handoff/audit-r10-roster` (8cf8f9ae7).
- Red checks at earlier heads (mutation at e329c7a, pr-contract and gate at 06a9e764c) are named and answered under the body's `## Red checks`. The gate red at this head has no cause of its own beyond the cancelled code run.
- Self-audit: `carry_audit.py check` rc=0, 2 routed, 0 unrouted (ev/carry-audit.txt). It was run against this verdict and a body file holding the PR body's `## Forward-carry` and `## Friction` sections (both `none`). The packet's carry_audit of the full body at the head reads 0 finding items.
