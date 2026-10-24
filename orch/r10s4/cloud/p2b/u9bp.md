# P2b units U9b + U9p, pins, agreement and policy text (sonnet). Topic r10-ci-layout-p2-u9bp

Shared rules: `git fetch origin brief/r10-ci-layout-p2 && git show FETCH_HEAD:COMMON.md`. They bind; read them first. Set PREPR_SKIP_CLOSURES=1. Plan: `git show 1011d6b2f:plans/ci-layout/EXECUTION.md`.

Input refs: stacked on the ASSEMBLED tree `refs/heads/ci-probe/all` = `c09125327c9fd5a011268d6dcd7cc50a709e3484`. That is current main (with #2629 and #2638) plus every unit except U10, plus the integration glue. Fetch it with `git fetch origin ci-probe/all`. Each unit's body is at `origin/handoff-body/r10-ci-layout-p2-<unit>:BODY.md` (u0c u1u2u7 u3 u4 u5 u6 u8 u11 u9a u9d). U10 (`pr-contract-rerun.yml` and `contract_rerun.py` deleted, `merge-main.yml`) is running in parallel: do NOT touch its files or the follower pin (`_PR_WORKFLOW_NAMES`/`_crr_defects`). Return: `handoff/r10-ci-layout-p2-u9bp` + body via body_push.sh. Your commits sit on top of c09125327: two ranges, U9b first, then U9p.

## Scope, verbatim from plan §1
| **U9b+U9d+U9p** (one seat, after names are final): pins and agreement | `entities.py` (all section 9 rows not taken by U0c); `required-contexts.json` `contexts: ["gate"]`; `agreement_py.py`/`agreement.mjs`; `policy_lint.mjs` (`PR_CONTRACT_CHECK`, `MAIN_STATE_REPORTERS`, REPORTER_INPUTS); `codeowners_gap.py` | 350 / 100 | U0c, U1-U11 names | cloud, sonnet | P2b |
| **U9p** policy text | `ci-autofix.md`, `orchestrator.md` §11, `defect-root-cause.md:143`, `nudge.md:85,93`, `steward/SKILL.md:106`, `web-fragments.md`, `PULL_REQUEST_TEMPLATE.md:23`, `rules_sync.mjs` + `--check`; record: `HANDOVER.md` and `tests/README.md` | 100 / 0 | all names final; M-3 outcome | cloud, sonnet; **policy caps sit at zero headroom**, so it pays in the same files first | P2b |
(U9d is done; the rows' U9d files are not yours.)

## U9b: what the assembled tree still owes
`PYTHONPATH=tests/hastub python3 tests/entities.py` at c09125327 reads `13 of 2413 ENTITY CHECKS FAILED`. Four of them are the py-spy heartbeat-control checks, which also read red on main on the seat machine: environmental, not yours. Leave them. Nine are yours. The tenth cut-over red, "a red that lands after pr-contract ran re-runs it", is U10's.

1. **FIRST, the lost guard (finding-propagation from U5; the orchestrator requires it here).** The D11-s1-03 write-grant reader `_prw_defects` inspects a workflow only when its own `on:` lists `pull_request`. `tests.yml` is now a `workflow_call` callee, so the main check ("no job holding a write grant on pull_request runs the pull request's own program…") reads green VACUOUSLY. Its two nulls are red:
   - "…restores and token hygiene undone is refused on each of the three autofix jobs and the cancel-superseded job" (`refused jobs on the undone copy: []`);
   - "…a report run from the working tree after the push step's pull…" (`refused: []`).

   Fix the reader so that a `workflow_call` callee of a workflow that runs on `pull_request` (`ci.yml` lists it and `uses:` the file) counts as pull_request-reachable. The nulls must go green again by REFUSING the undone copy, not by being edited to expect `[]`. `tests.yml:cancel-superseded` leaves the expected list (it is `ci.yml`'s now). Failing test first: show the nulls red at c09125327, then green. A mutant that drops the callee rule must turn them red again.
2. `_AF_DISPATCHED` becomes `{"ci.yml"}`. This covers the three "closures-/claims-/mutation-autofix dispatches every workflow owning a required context but Governance" checks; reword them to the one umbrella dispatch. "codeql.yml accepts the autofix jobs' dispatch" retires, if it is still present.
3. "every required context tests.yml produces runs on an autofix or batch-proof dispatch (B9)": read the triggers through `ci.yml`, which lists `workflow_dispatch` and calls `tests.yml`, the same way `_mq_problems` reads callees.
4. "exactly seven jobs override the workflow's read-only floor…" becomes six in `tests.yml`; `cancel-superseded` is `ci.yml`'s.
5. "tests.yml cancels a superseded older SHA" moves to `ci.yml`'s `cancel-superseded` job. Keep its plant and null.
6. `tools/policy/fixtures/required-contexts.json` `contexts: ["gate"]`, with `gate_required` unchanged. Then follow every reader of `contexts` (`agreement_py.py`/`agreement.mjs`, `policy_lint.mjs` `PR_CONTRACT_CHECK`/`MAIN_STATE_REPORTERS`/REPORTER_INPUTS, `codeowners_gap.py`, the entities pins of the 17) to the new layout, per DESIGN-P2 §9. The ruleset PUT (`ruleset_cutover.py`) moves the live ruleset at the same merge.
7. `policy_lint.mjs`'s red-history arm (#1144) must not ask a body to answer `gate` or `pr-contract / pr-contract` (U6's forward-carry). Plant and null.
8. `tools/audit/seat/body_patch.sh:92` `contract()` excludes only `pr-contract`. It needs the N4 pair `.name != "pr-contract / pr-contract" and .name != "gate"`. Its self-test's `gh` stub returns pre-filtered names (line ~233), so give it a stub that applies the jq program first. Otherwise the edit has no check that moves.
9. Optional pins from U5, which CI should guard:
   - no `tests / *` job that `gate.py` requires carries a job-level skip `if:` (U5's `dev/audit/harnesses/r10_ci_layout_u5/unitcheck.py` `stand_down_problems`);
   - `RUN_PART=fast` skips the arch pair by name, and `RUN_PART=arch` runs only it (`run_part.py`). Import or drive those harnesses; do not re-implement them.

Do not edit any workflow file except to fix a pin's subject that the units left wrong; say so if you do. Run `python3 -I tools/audit/seat/selftest_wiring.py --check` and expect 90/90/0. Run `tests/structure.py`.

## U9p: policy text
These files are policy: the orchestrator approves them under mandate 6329234399. Caps sit at zero headroom (`ratchet-budgets.md`, `policy_budgets.json`), so pay in the same files first; never raise. Never touch VERSION or RELEASE_NOTES.
- `.claude/rules/` are generated: edit `dev/governance/rules/*.md`, then run `node tools/policy/rules_sync.mjs` and `--check`.
- `ci-autofix.md`: the autofix jobs now dispatch `ci.yml -f pr -f base` once, not four workflows (U5).
- `orchestrator.md` §11, `defect-root-cause.md:143`, `nudge.md:85,93`. nudge.md:93's stamp precondition becomes "the latest `ci.yml` push run's `gate` on current `origin/main` is green" (U9a). M-3 is open (default keep): the approve steps and `approve_held_runs.sh` stay, so do NOT delete `nudge.md:85`'s held-run step.
- `steward/SKILL.md:106`, `web-fragments.md`: the one required check is `gate`.
- `PULL_REQUEST_TEMPLATE.md:23` (owner ruling R-10, U6): `## Red checks` also answers each `code-scanning alert <n> (<rule id>)` that pr-contract lists. Make the matching steward/SKILL.md pr-contract line say the same. The template and `checkPrBody` are one contract (CLAUDE.md), so keep `policy_lint.mjs`'s template check green.
- Record: `dev/programme/HANDOVER.md` and `tests/README.md`. Cover the umbrella, `gate`, `RUN_PART=fast|arch` (U5), and `tools/coverage/coverage_tree.sh:25`'s comment ("`tests / arch-instrument`, where run.sh runs them (RUN_PART=arch)").
- The approved design cites: DESIGN-P2 at tag `archive/probe/design-ci-rev4` (1371a0a6) and the review at `archive/probe/design-ci-review5` (afc00bfe).

Body: the common headings, plus `## Policy changes`, one line per file stating what a seat must now do differently.
