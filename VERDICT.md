Fix review: blocked 536080c084c3ea201db13860c29bcca577fac5db carry-missing: pr-contract (jobs 117965471342, 117968141018) refuses the body, carry_audit UNROUTED body item 6ff2bcdb (## Forward-carry): the dominated-rate-limit finding is "none." plus prose naming the orchestrator, not a Carry: to a stage; the fix itself measured sound

bus-nonce: 8e02943d67d0f4e609a64dd035800ed3

Round 1 (the PR has no earlier `Fix review:` comments). Measured head 536080c084c3ea201db13860c29bcca577fac5db (ev/HEAD); it was still the PR head when this verdict was written. Roles contract: `git diff 1bcc79884...origin/main -- dev/governance/roles/` is empty, so it is current.

## The block (body only, no code change needed)

pr-contract ran on the body twice at this head after the GitHub API rate limit cleared (08:36Z, 08:43Z). `PR-BODY: 0 error(s)`, then `carry_audit.py check` printed
`UNROUTED body item 6ff2bcdb (## Forward-carry) [section]: 'none. The two carried constraints are discharged above: ...'`, exit 1 (ev/pr-contract_117968141018.log).
carry_audit's NONE_ITEM accepts only a bare `none` or `n/a: <reason>`. Its own self-test L05 covers this case: "a Forward-carry that starts `none` and records an observation is a finding". The section names a finding for a later stage: `max_step_fraction` (`HOUSE_LOSS_MAX_STEP`) can no longer bind at the shipped constants. The body also says it "goes to the orchestrator as a finding to dispatch", and `## Red checks` says the cheaper pr-contract detector was "reported to the orchestrator for the root-cause seat". Neither is routed (`finding-propagation.md`). Fix: either carry the dominated-rate-limit finding to its stage with a `Carry:` line (and the root-cause one too, if it is meant to propagate), or reduce the section to a bare `none` and record the observation where carry_audit accepts it. This is a body edit, so the code head does not move. pr-contract then re-runs on the edited body.

## What measured sound (carries to a head that only edits the body)

- Mutation proof (step 1), in a scratch worktree at the head, `PYTHONPATH=tests/hastub python3 tests/features.py`:
  - `reach = trust_region` (the absolute bound restored): `3 of 4215 FEATURE CHECKS FAILED`, rc 1. The same three checks and values the body quotes (ev/mut_reach_absolute.txt).
  - My mutant `reach = max(current, 1.0) * trust_region`: 1 of 4215 failed (the #193 replay pin).
  - My mutant `reach = min(current, 1.0) * trust_region`: 2 of 4215 failed (saturation and split invariance) (ev/mut_reach_max.txt, ev/mut_reach_min.txt).
  - The tree was restored afterwards and `git status --porcelain` printed nothing.
  - CI's `mutation` at this head: `MUTATION TABLE PASSED`, `thermal_model.py:1938 CLAMP_DROP -- killed by tests/entities.py`.
- Finder's harness (step 2): `reseed_rolling.py` from study/r10-reseed `2c42ba4a0`, sha1 030df96abe88d7b12132798518bc92e466391d99, which matches the body. Run at merge base 1bcc79884 and at this head, defaults, every run rc 0 (ev/rolling.*.txt, ev/rolling_summary.txt). RESULT ratio_B_over_A.*_post:
  - Head: every metric on sz_157, sz_060, tz_157_192, sz_null and tz_null reads 1.0000. This is the finding closed, with house_step_rms 1.0000 as well.
  - Base:
    - sz_157 house_std 1.0458, rmse 1.0215, fc_mae 1.0617.
    - sz_060 0.5101 / 0.7874 / 0.8355.
    - tz_157_192 0.8667 / 0.8204 / 0.8272, lower 0.8831 / 0.8540. Identical to the body.
    - sz_null 0.9631 / 0.9628 / 0.9653.
    - tz_null 0.9980 / 0.9971 / 0.9993 / 1.0006.
  - Not re-derived exactly (step 8): the body's base-side sz_157 (1.0483 / 1.0227 / 1.0693) and sz_060 (0.5106 / 0.7799 / 0.8259). I re-ran sz_157 at the body's own base 768bfc0c3 and got 1.0458 / 1.0215 / 1.0617, the same as at 1bcc79884. No production or test-harness file differs between the two, so the gap is a machine floating-point difference in the closed-loop optimizer, not a tree difference. Direction and size hold. The finding's figures (head = 1.0000) reproduce exactly.
  - The sz_null and tz_null figures agree to within 0.0002 (tz_null rmse/fc_mae 0.9971/0.9993 against the body's 0.9972/0.9989).
- Perturbation and null control (step 3): `--trust-region 1e9` on sz_157 reads 1.0000 at both ends. The null plants read 1.0000 at the head.
- Bundle harness (dev/audit/harnesses/r10_trust_relative_bundle.py): the owner's bundles are not available to this seat, so the store figures (1.0900 and so on) are NOT verified. I ran the harness on a synthetic bundle (ev/synth_bundle.json: two-zone, learned 1.5667 / 1.9223, default config) at both trees (ev/bundle_synth.txt):
  - Base ratios: house 1.1548 / 1.1615 / 1.0011, lower 1.3540 / 1.3569 / 1.0013.
  - Head ratios: 1.0000 on every metric.
  - `--trust-region 1e9` and `--learned 1.0` read 1.0000 at both trees.
  - This is the fixer's harness, not the finder's. I used it only as a companion check.
- Class (step 6): the body's rule returns exactly the two seams it dispositions, `thermal_model.py:1938` and `:1944` (ev/class_rule.txt). The other `np.clip` sites in custom_components are fixed-range global bounds.
- Claim files, golden fixtures, VERSION, manifest and RELEASE_NOTES (steps 4 and 5): the three-dot diff touches none of them, and CI prints `no version edit`.
- Merge (step 13): `git merge-tree --write-tree origin/main(c35302773) 536080c08` gives tree b89b798d7c239300c78b9cab37415da453b8be1b, rc 0, no conflict.
- Score and structure (step 14): at the head, `archscore score.py --diff 1bcc79884` prints `dS +0.0000 NULL` and `structure.py` prints `STRUCTURE RATCHET PASSED`. The diff adds the closures.json entry and one mutation-ledger pin. The pin is earned: the CLAMP_DROP mutant is killed.
- Architecture (step 15): a one-line local change in the one shared step, with the constant's comment updated. No breach.

## CI on this head (ev/check_runs.tsv, commit check-runs API)

- Green: fast (3.14), mutation, closures, coverage, coverage-ratchet, typing, browser, hassfest, scope, closure-scope, briefs, policy-docs, instrument-self-tests, wave-script, delivery-status, budget-raise-gate, graders-head-copy.
- Rate-limited, then green on re-run: arch-score, validate-hacs and env-matrix first failed on the GitHub API rate limit (`API rate limit exceeded for installation` / `GitHub API is unreachable`) before measuring anything. Each re-run is green.
- Red: pr-contract. Its first two runs died on the same rate limit before reading the body. The two later runs failed on the UNROUTED item above.
- Red: nightly-status. Not this PR's (`defect-root-cause.md`); pr-contract lists it as the only red the body must answer, and `PR-BODY: 0 error(s)` accepts that.
- Pending at writing: Analyze (python) (CodeQL re-run).
- Red history: pr-contract printed `record red-history ... mutation, nightly-status`. The body answers mutation.
