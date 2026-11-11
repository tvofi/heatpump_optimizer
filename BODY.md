R10-WATER-SETPOINT-FEEDBACK residue: `Carry 8`, the contributor's answers in https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104, taken into account and cited where the merged loop rests on them. Carry 1-7 are delivered by #3405 and out of scope.

What each statement changes at the merged code, and what this diff does with it:

- **600 s watchdog and polling.** No behaviour change: the loop never re-writes to keep the watchdog armed, and `docs/configuration.md` already required polling within 10 minutes. The docs now say that any access re-arms the 600 s, a read included, that ha-luxtronik-shi polls every 30 s (10–300 s), and that a controller restart still drops written values unless its restore option is on, citing the comment.
- **Hysteresis 0.5 K, not 2 K.** `pump_arbiter.FEEDBACK_DOWN_K` already rests on the 0.5 K minimum, so no constant moves; its comment now cites the comment. `docs/configuration.md` stated "2 K on a Luxtronik's default" as the start condition: replaced by the hysteresis as a setting with a 0.5 K minimum, and input 10107 as the threshold in effect.
- **Inputs 10104 and 10103 (the clamp of 10001).** `_clamp_cut` infers both bounds from the readback; its docstring and the docs now name the two inputs, cite the comment, and say they are not read.
- **Found while pinning the section, own seam, built here:** the docs gave the loop's lower bound as 0.1 K below the inlet; `FEEDBACK_DOWN_K` is 0.3 K and the harness's simulation writes down to it. The docs now follow the constant, and `tests/doc_claims.py` reads all five documented loop figures from the `FEEDBACK_*` constants.

decision: owner — reading 10104, 10103 or 10107 is not built. Each needs an entity id of a third-party integration's sensor: `InputReader` reads configured keys only, so the read path is three new options (or a name derivation from the set-point entity id, the `modbus_prefill.package_prefix` shape, against ids this repository does not control). Reading the two clamp bounds would not remove `_clamp_cut`, which a controller without those sensors still needs; reading 10107 would let the first write of a run clear the start threshold, lifting the precondition "hysteresis at most the lift". Nothing here is marked implemented for those reads.

Alternatives (fixer.md step 17): citing in docs only lost because the code comments are where the 0.5 K and the clamp inference are assumed; a new entity read lost to the brief's bound (no new read path or option without the owner).

## Head

`06d092f436adacfc248a901d5ef68bab5204168f`

## Mutation proof

Each production file restored to its text at the failing-test commit `d84aa03dd7`, `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`, then restored (`ALL` checks pass, `git status --short` empty).

- `docs/configuration.md` restored: FAIL `the loop's lower bound is the constant's: 'no lower than 0.3 K below the inlet'`, `the polling precondition cites the contributor's answers`, `the start condition cites the contributor's answers`, `the start condition states 10107, 0.5 K`, `the loop's preconditions cites the contributor's answers`, `the loop's preconditions states 10104, 10103, 0.5 K`, `no start condition is stated as a 2 K Luxtronik default`.
- `custom_components/heatpump_optimizer/pump_arbiter.py` restored: FAIL `the assumed minimum hysteresis behind FEEDBACK_DOWN_K cites the contributor's answers`, `the inferred clamp bounds (_clamp_cut) cite the contributor's answers and name both inputs`.

The four start-hold, rate, window and deadband checks pass at both ends: they pin figures the docs already had right, and each fails if its `FEEDBACK_*` constant or its phrase moves.

## Null control

- The unmodified tree (`d84aa03dd7`, the test alone on base `dbd1ab5b07`): the new section fails the nine checks listed above and passes the other four.
- The group's harness `dev/audit/harnesses/r10_water_setpoint_feedback.py` (sha1 `874afca01e6a5928020471983c5d81273f77a816`) reads flat, base against head, compared by `diff ... && echo HARNESS-IDENTICAL`, which printed `HARNESS-IDENTICAL`: the diff changes comments and docs, no behaviour. The companion that reads the defect at the base and not at the head is the `tests/doc_claims.py` section above.
- The 0.1 K docs figure was false, not a rounding of the same bound: the harness's `sim(plan_kw=0.3)` writes down to the constant below the inlet; had 0.1 K held, the minimum of sent minus inlet would have been no lower than -0.1.

## Figures

- Loop writes relative to the inlet, K, minimum over the run after minute 10: `PYTHONPATH=tests/hastub:custom_components:tests:dev/audit/harnesses python3 -c "import r10_water_setpoint_feedback as h; r=h.sim(plan_kw=0.3); print(round(min(s-ret for m,s,ret in r['writes'] if m>10),2))"` printed `-0.3`.
- Files under `custom_components` and `docs` naming the comment id or one of the three inputs, rule `git grep -cE '6756915104|\b1010[347]\b' <ref> -- custom_components docs`: no line at `dbd1ab5b07` (empty output), two files at the head.
- The 2 K default, rule `git grep -c "2 K on a Luxtronik" <ref> -- docs`: `docs/configuration.md:1` at `dbd1ab5b07`, exit 1 with no output at the head.
- Harness at both ends: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_water_setpoint_feedback.py`, three lines, identical at `dbd1ab5b07` and the head.
- Structure ratchet: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.

## Unpinned sites

none: the `custom_components/` delta is comment and docstring lines.

## Red checks

none

## Forward-carry

none

## Friction

none
