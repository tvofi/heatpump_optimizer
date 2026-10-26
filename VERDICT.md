Fix review: blocked a2a7b9efae9ec2b96924a6ef38bad50f79a8c4e0 harness-nondeterministic: the in-tree mutation harness this delta adds, dev/audit/harnesses/r10_shape_grammar_mutants.py, exits 1 on its own documented invocation, reporting R11 SURVIVED from a stale env_drift .pyc; the body knows the one-token fix (-B in the child) and carries it to this PR's own group instead of landing it

bus-nonce: 1f5b62c082a77780fda0f4fa99816821

Round 2, a delta review of e380bebf..a2a7b9ef. I measured head `a2a7b9efae9ec2b96924a6ef38bad50f79a8c4e0` from a detached worktree. `git ls-remote origin refs/pull/2843/head` gave that SHA at 05:19Z, just before writing. `dev/governance/roles/` has no diff between the merge base and origin/main `df478d40b`, so the contract is current. I ran the finder's harness, the band census at blob `893c3957`, myself, and I used the round-1 reviewer's mutant instrument, not only the fixer's.

## Block

- **The committed instrument is nondeterministic, and the body carries that instead of fixing it.** `## Mutation proof` names `python3 dev/audit/harnesses/r10_shape_grammar_mutants.py` as "the instrument". This review ran it at the head, in-tree and unmodified (`ev/grammar_mutants_intree.txt`):
  - It printed `R11: RESULT pins=16 fails=0 SURVIVED` and `RESULT mutants=17 killed=15`, then `exit=1`.
  - `... R10 R11`, run three times (`ev/grammar_R10_R11_intree.txt`), gave R11 KILLED, KILLED, then SURVIVED. `R11` named alone was KILLED three times out of three.
  - The same file with `-B` in the child's argv (the body's own `sed`) gave `killed=16`, `exit=0` (`ev/grammar_mutants_child_B.txt`).
  - The body's cause is right. The child is a fresh `python3` with no `-B`, so R11 imports R10's same-size, same-second `tests/__pycache__/env_drift.*.pyc`.
- **Why this blocks and is not just a carry:**
  - The defect is in a file this delta adds. It is not a pre-existing problem.
  - Its documented invocation exits 1. The next seat that re-runs this proof as written will read a false SURVIVED.
  - The fix is one token, and the body names it: `-B`, or `sys.dont_write_bytecode` or `PYTHONDONTWRITEBYTECODE=1` in the child's `env=`.
  - "This seat may not change code" does not cover the fixer's own new harness. A `Carry: R10-996-RUNNER-CLAIMS` from this PR to its own group leaves nobody owning the fix once the PR merges.
- **What clears it:**
  - Make the child bytecode-free in `r10_shape_grammar_mutants.py`, plus `-B` or an equivalent if any other child shares the problem.
  - Re-run the in-tree command. It should give `killed=16` with exit 0, and `R10 R11` should kill R11 on repeated runs.
  - Drop the third `## Forward-carry` bullet and the matching `## Mutation proof` carry. Quote the in-tree run in `## Figures`.
  - Refresh `## Red checks` for the new head (see Findings).
  - The substance below carries unchanged to a head whose only change is that.

## Findings

- **`## Red checks` is stale for this head.** It reads the check runs of round 1's head `e380bebfa` and says "No run exists yet for this head". At `a2a7b9ef`, `arch-score / arch-score`, `tests / nightly-status`, `validate / validate-hacs`, `governance / env-matrix`, `gate`, `refresh` (twice) and the pr-contract run's `prelude` concluded red. Each log shows the GitHub API rate limit (HTTP 403 / `RATE-LIMITED reset_epoch=1792991224`, or `GitHubRatelimitException`), and each died before any test body. env-matrix's one failing arm reads "the GitHub API is unreachable". `pr-contract` was skipped behind the red prelude; a new `prelude` run started 05:09Z and was still in progress. Owed on the next head: name and answer the reds that head's runs actually show. Carry: R10-996-RUNNER-CLAIMS
- **Equivalent mutant R10** (the `path.startswith(prefix)` guard in `shaped_leaves`): SURVIVED again under both instruments, and still unreachable from `judge_drift`. Carry: dismissed: an equivalent mutant; `_diff_leaves` always prefixes the path with `<fixture>.`

## Evidence

- **The finder's harness, re-run by me.** `dev/audit/harnesses/r10_band_census.py`, blob `893c39573714a99fb151ec76cbdf0ec40b878675`, in a worktree at the parked arm `996b54cf1`, Linux x86_64, `PYTHONPATH=tests/hastub`. It printed `RESULT scenarios=50 susceptible=15 failures=0`, `SUSCEPTIBLE away_setback direct_flow_carnot everything_on fuse_guard shoulder_two_zone tariff_plus_two_zone valve_storage valve_storage_low_target valve_storage_small_tank valve_storage_smart_write valve_upper_direct_slab winter_two_zone_dhw wood_coil wood_two_tank wood_two_tank_smart_write`, `exit=0`. That is identical to round 1's run and to the figure the body quotes. File: `ev/finder_band_census_at_996b54cf1.txt`.
- **The citation is correct.**
  - `git cat-file -e` succeeds for blob `893c3957…`, commit `648f88d9e67bc756ed3f647f5b1ffd042b14a883` and the arm and base `996b54cf1` / `a1d56b66f`.
  - `git rev-parse origin/fix/r10-arch-shapes-pr:dev/audit/harnesses/r10_band_census.py` gives `893c3957…`.
  - At `648f88d9e` itself the blob is `87585ad4…`. `94a4ea904` changed it later, which matches the body's "its blob after `94a4ea904`".
  - `git branch -r --contains 648f88d9e` lists `origin/fix/r10-arch-shapes-pr` and `origin/handoff/r10-arch-shapes`.
  - The false "no sha1 can be cited" bullet and the R10-ARCH-SHAPES carry it rested on are gone from the body. Round 1's block is cleared.
- **The three new pins, under the round-1 reviewer's instrument** (`ev/mutate.py` and `ev/sc_pins.py`, copied from `review/2843:evidence/`, not the fixer's harness). Each mutant goes in a temp-file copy of the head's `tests/env_drift.py`, so no `.pyc` is shared (`ev/r1_instrument_mutants_at_head.txt`).
  - Null control (the unmutated head file): `RESULT pins=16 fails=0`.
  - R13: `fails=2 KILLED`. R14: `fails=1 KILLED`. R17: `fails=1 KILLED`. Round 1 recorded all three SURVIVED.
  - Every other mutant was KILLED, except R10 (equivalent): 16 of 17 killed.
- **The fixer's harness.** It matches the body's `## Figures` both ways: 15 of 17 with exit 1 in-tree, and 16 of 17 with exit 0 under `-B`. The body's own `## Figures` reports both the same way.
- **What changed since round 1.**
  - `tests/env_drift.py`, `dev/governance/rules/claim-files.md`, `.claude/rules/claim-files.md`, `.cursor/rules/claim-files.mdc` and `r10_shape_claim_controls.sh` have the same blobs at `e380bebf` and at the head.
  - The authored delta is `1f57b9a76` (three pins plus the mutant harness) and `d1a6a98e5` (one `closures.json` line). The rest of e380bebf..head is two main merges.
  - Round 1's mutation and real-capture controls therefore carry unchanged.
- **Policy.**
  - `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
  - `claim-files.md` at the head is 53 lines and 2385 bytes. The change is the one the body describes and has not moved since round 1. The owner's approving review is still owed.
- **Classification.** Both new harnesses sit in `tests/closures.json` under `inert_reads` / `tests/harness_headers.py` (`ev/classification.txt`). `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED`. `tests/entities.py` at the head prints `2 of 2461 ENTITY CHECKS FAILED`. The two FAILs are the `gate-sweep.yml` check and the `graders-head-copy` delivery_status check, the same two the body's merge-base control fails. No check fails with "force the FULL suite". The body's 2460 was taken at `d1a6a98e`; the extra check comes from main (`ev/entities_head.txt`).
- **Cheap checks** (`ev/cheap_checks.txt`, origin/main `df478d40b`, 05:06Z):
  - `git merge-tree --write-tree origin/main a2a7b9ef` exits 0 (`ada27f4d6`).
  - The claim files, `VERSION`, `RELEASE_NOTES.md` and the manifest have no three-dot diff (exit 0).
  - `env_drift.py --claims-only`: `claims hygiene: origin/main ok`.
  - `STRUCTURE RATCHET PASSED`.
  - `ALL 117 closure shrink pins PASSED`.
  - `dev/programme/delivery/2843.md` is in the three-dot diff and reads `**open**`.
- **Body check.** `tools/pr/prepr.sh --body-check` on the live body (`ev/body.md`, fetched about 05:05Z, head `a2a7b9ef`) printed no REFUSE: `PR-BODY: 0 error(s)`, `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted`, `preflight ok`. `python3 -I tools/audit/carry_audit.py pr 2843` printed `4 routed, 0 unrouted, 0 bad destination(s)`. `## Class seams` is present and lists the three seams round 1 asked for.
- **CI at the head** (`ev/check_runs_at_head.txt`, 05:19Z):
  - Concluded green: `tests / typing`, `tests / mutation`, `tests / arch-instrument`, `tests / closure-scope`, `tests / briefs`, `governance / delivery-status`, `governance / policy-docs`, `governance / wave-script`, `budget-raise-gate`, `hassfest` and `codeql` (javascript, actions).
  - Still in progress: `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `codeql / Analyze (python)` and a re-run `prelude`.
  - Every red concluded on the API rate limit (Findings). `tests / nightly-status` and `validate / validate-hacs` are not required checks and do not block. I did not re-run the gate or the mutation table.
- **Not re-derived by me:** the scoped-gate mode line (`MODE: SCOPED -- 6 script(s) run`), the architecture score, and the 03:39Z real-capture controls. They are unchanged inputs since round 1, which re-derived the controls.
