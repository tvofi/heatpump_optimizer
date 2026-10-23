## Unit
U9b + U9p, two ranges on top of ci-probe/all c09125327: `1e161e955` (U9b: tests/entities.py, required-contexts.json, policy_lint.mjs, codeowners_gap.py, body_patch.sh; +227/-136) and `ffe738c7c` (U9p: policy text, record; +98/-97). I did not touch U10's files or the follower pin. Workflow files: none edited.

## Interface
- Fixture: `contexts: ["gate"]`; `ruleset_objects` now `[{context: gate, integration_id: 15368}]` (ruleset_cutover.py's NEW_CHECKS); `gate_required` unchanged.
- entities.py: `_prw_reachable` (callee rule), `_prw_not_pr`, `_RC_UNITS` (= gate_required), `_RD_UNITS` (gate.py REQUIRED `pr` ∪ `no-pr`); `_rc_producer` accepts `<stem> / <job>`.
- policy_lint.mjs: `PR_CONTRACT_CHECK='pr-contract / pr-contract'`, `OWN_VERDICT_CHECKS` (+`gate`), `MAIN_STATE_REPORTERS={tests / nightly-status, governance / delivery-status}`, REPORTER_INPUTS + ci.yml.

## Static map
Not applicable (no workflow file changed).

## Controls
1. Lost guard (item 1). At c09125327 the two nulls read red: `refused jobs on the undone copy: []`, `refused: []`. Fixed reader, `/tmp/claude-0/scratch/prw_proof.py`: undone subjects = ci.yml:cancel-superseded, ci.yml:refresh, tests.yml:{claims,closures,mutation}-autofix; pulled = the three autofix jobs. Mutant (callee rule dropped): undone = only the two ci.yml jobs, pulled = [] — both nulls red again. New nulls: tests.yml alone is not read; codeql.yml's push-only D-5 step is exempt only by its `if:` (removed -> refused). The reader now also skips steps whose own `if:` excludes pull_request (needed for that D-5 step, `codeql.yml:analyze` otherwise read as a real finding).
   `ci.yml:refresh` joins the expected list (a write-grant job the old list could not see); `tests.yml:cancel-superseded` leaves it.
2. `_AF_DISPATCHED={"ci.yml"}`, three checks reworded; "codeql.yml accepts the autofix dispatch" was already absent.
3. B9 reads triggers through ci.yml; units are gate.py's `pr`∪`no-pr` classes (push-only ci-ratchet is not owed on a dispatch — using all of gate_required read it red). Nulls: old recheck-gate arm; umbrella without workflow_dispatch.
4. Six overrides in tests.yml. 5. Supersession check now drives `tools/pr/cancel_superseded.py` `candidates` and ci.yml's job (plant: older SHA cancelled; null: same-SHA run kept; bot and push senders skipped).
6. Fixture/readers: `contexts` pin now `["gate"]` with a "still the 17" plant; mq/B9/`_rc_producer` follow units; codeowners_gap `self_test_only_required` reads gate_required job ids; agreement pair needs no change (ci.yml is in neither side; `_GOV_FILES` still lists pr-contract-rerun.yml, see Wiring).
7. Red-history: fixture now holds `gate` and `pr-contract / pr-contract` reds that must not come out. Mutant (`gate` dropped from OWN_VERDICT_CHECKS): `policy_lint.mjs --self-test` prints two `FIXTURE VACUOUS` lines; restored: `FIXTURE ok: 92 error(s) hold 253 pins`.
8. body_patch.sh: filter is the N4 pair; the `gh` stub now runs the `--jq` program over a check_runs doc. New control `own` (gate and pr-contract / pr-contract red, only `lint` passed) and mutant `redf` (filter deleted, killed). `bash tools/audit/seat/body_patch.sh --self-test`: 64 checks, 0 failed.
9. Pins added by importing U5's harnesses: `stand_down_problems` (plus a planted skip `if:`), and `run_part.py` plain and `--mutant`.
Whole suite: `PYTHONPATH=tests/hastub python tests/entities.py` (python 3.14 venv): 2 of 2419 FAILED, both below. Also: `selftest_wiring --check` 90 self-testing, 90 wired, 0 unwired; `throwaway_git --check` clean; `tests/structure.py` PASSED; `rules_sync --check` ok; `fragments_sync --check` ok; `policy_lint.mjs --budgets` clean (all caps paid in the same files, none raised).

## Live checks owed
- The ruleset PUT (`ruleset_cutover.py`). Until it lands `policy_lint.mjs` (and the entities check "the template arm … real template keeps it green", which runs it) reads rc=1 on the live-vs-recorded required-contexts class only: the live set is still the 17.
- `pr-contract` on the first run: it must not ask the body for `gate` or itself.

## Wiring
- U10 must drop `pr-contract-rerun.yml` from `_GOV_FILES` and `rerun-stale-contract` from `GOV` with the file, and fix the follower pin (still red).
- Inherited from U6, not mine: `tools/audit/seat/tmp_paths.py --check` refuses `tests/entities.py:26932` (`"> /tmp/pr-alerts.txt"` pinned from pr-contract.yml); the same refusal reads at c09125327.
- `codeowners_gap.py --check` refuses 5 uncovered files `tools/ci/{gate,ghapi,prelude,sweep,sweep_selftest}.py`, identical at c09125327 (plan UNCERTAINTY 5). A CODEOWNERS edit is policy and the owner's call, so I did not make it.

## Red checks
- entities.py "a red that lands after pr-contract ran re-runs it …": U10's (follower pin).
- entities.py "the template arm …": live ruleset not yet cut over (above).
- tmp_paths and codeowners_gap: inherited, above. py-spy heartbeat checks: green on this machine.

## Policy changes
- `ci-autofix.md`: a seat waits on `tests / closures|fast|mutation` and knows autofix dispatches `ci.yml -f pr -f base` once; absence is of `gate` and units; approve steps stay until M-3.
- `orchestrator.md` §11: merge only when `gate` passed at the head, not "every lane ran".
- `defect-root-cause.md`: the main-state exemption names `tests / nightly-status` and `governance / delivery-status` and counts `ci.yml` among their inputs.
- `nudge.md`: stamp precondition is the latest `ci.yml` push run's `gate` on `origin/main`; red `gate` on main outranks the queue; `--ignore-red` takes the two `<caller> / <job>` names; `approve_held_runs.sh` step kept.
- `steward/SKILL.md`: the one required check is `gate`; answer the unit checks and each `code-scanning alert <n> (<rule id>)` pr-contract lists; pr-contract runs last in ci.yml.
- `web-fragments.md` (+ the four `web-*.js` copies, `fragments_sync --check` ok): wait on the `ci.yml` push run's `gate` job; `gh workflow run ci.yml -f pr -f base` mapping.
- `PULL_REQUEST_TEMPLATE.md`: `## Red checks` also answers each open code-scanning alert pr-contract lists (R-10); template check green.
- `HANDOVER.md`, `tests/README.md`, `coverage_tree.sh` comment: the umbrella, `gate`, `RUN_PART=fast|arch`.

## Head
`ffe738c7c` (code head of `handoff/r10-ci-layout-p2-u9bp`), measured on ci-probe/all `c09125327`.

## Mutation proof
Callee rule dropped (`python /tmp/claude-0/scratch/prw_proof.py mut`): the two D11-s1-03 nulls read `[ci.yml:cancel-superseded, ci.yml:refresh]` and `[]`, red. `gate` dropped from `OWN_VERDICT_CHECKS`: two `FIXTURE VACUOUS` lines. Red filter deleted in body_patch.sh: mutant `redf` killed. Details under Controls.

## Null control
The same nulls at c09125327 read `refused jobs on the undone copy: []` and `refused: []`; the unmodified tree is red there.

## Figures
- `PYTHONPATH=tests/hastub python tests/entities.py` -> 2 of 2419 ENTITY CHECKS FAILED (rule: the run's own last line).
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> 90 self-testing, 90 wired, 0 unwired.
- `bash tools/audit/seat/body_patch.sh --self-test` -> 64 checks, 0 failed.

## Forward-carry
`none` beyond Wiring: U10 owns the `_GOV_FILES`/`GOV` drop and the follower pin; the CODEOWNERS question for `tools/ci/` goes to the owner (plan UNCERTAINTY 5).

## Friction
none

## Approval
Policy files in this diff are approved by the orchestrator under mandate 6329234399 per the brief; the owner's review is still required at merge by the code-owner rule.
