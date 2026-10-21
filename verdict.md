Fix review: blocked 59c5b20ef0d7beef377fe2580bd87f9fdb783ff7 mutation-survivor: the model-record refusal, the violating-plan refusal and the link-caption fix each survive deletion while the body says each new predicate is pinned

bus-nonce: e98d4b97318b505ab007e725b74e5c4d

## Round

First review of PR #2558 (R10-PLAN-ARTIFACT), measured at head `59c5b20ef0d7beef377fe2580bd87f9fdb783ff7`. The PR's base is `5006687576713535518634a154f7de1824432219`, and origin/main was `1ebc737e7e187a1d45c62069ae8ab69c465db928` when I measured. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so my contract is current.

## Block

1. **Step 1 (mutation proof): four mutants survive.** I applied each one in place at the head, ran `python3 -I tools/audit/seat/plan_page.py --self-test` and `python3 tools/plan/replan.py --self-test`, then restored the file. The driver is `ev/reviewer_mutants.txt`, and the M0 null control passes both suites (rc 0/0). Survivors:
   - **B**: `if "model" not in plan["generated"]:` -> `if False:` in `plan_page.main`. Both suites stay at 0 failed. The body states "A plan without that record is refused with a replan instruction", and no arm feeds main a plan without `generated.model`.
   - **C**: `bad = replan.check_plan(plan)` -> `bad = []` in `plan_page.main`. Both suites stay at 0 failed. The forward-carry states the page "refuses a stale or violating plan with exit 1 and writes nothing". Only the stale arm is pinned.
   - **D**: the caption's `{drawn} of` -> `{max(0, len(chain) - 1) - drawn} of`, which re-introduces the bug the body says this PR fixed ("The link caption printed the *skipped* count as the drawn count"). Both suites stay at 0 failed.
   - **E**: in `replan.stale_reason`, `ref = ref or gen.get("roster_ref")` -> `ref = gen.get("roster_ref") or ref`, so an explicit `--roster-ref` is ignored in favour of the plan's own ref. Both suites stay at 0 failed.

   The body's `## Unpinned sites` says "The predicates `plan_page.py` adds are each pinned by a self-test arm, shown killed under `## Mutation proof`". B, C and D contradict that at this head. The fixer's own driver (`dev/audit/harnesses/r10_plan_page_mutants.py`) re-ran `RESULT survived=0` here, but its 14 rows do not include these sites.
2. **Step 10 (forward-carry): `carry-missing: not carried to R10-ORCH-MACHINERY`.** The body's `## Forward-carry` says R10-ORCH-MACHINERY's item (3) premise changed: the page cannot share one model builder with `plan_table.py`. At `origin/handoff/audit-r10-roster` `8a6d22506a7bfe497888384533010e346bc85ffe`, that group's `brief` still reads "(3) The plan page as a tree instrument sharing one model builder with tools/audit/seat/plan_table.py". None of its `carry` entries names `plan_page`, `R10-PLAN-ARTIFACT`, `2558` or `gen.py` (`ev/orch_machinery_carry.txt`). The body names no roster SHA where the carry was written. So the finding exists only as a `Carry:` marker in this PR's body, which `finding-propagation.md` says is not propagation.

## Findings

- Survivor B: `plan_page.main`'s `generated.model` refusal is unpinned. It needs a self-test arm that runs `main` on a fresh plan with `generated.model` removed and expects rc 1 and no file written. Carry: R10-PLAN-ARTIFACT
- Survivor C: `plan_page.main`'s `replan.check_plan` refusal is unpinned. It needs an arm with a fresh but violating plan, expecting rc 1 and no file written. Carry: R10-PLAN-ARTIFACT
- Survivor D: the link caption's drawn count is unpinned, though the body names it as a fixed defect. It needs an arm on a fixture where drawn != skipped that asserts the caption figure. Carry: R10-PLAN-ARTIFACT
- Survivor E: `stale_reason`'s explicit `ref` argument has no arm where it differs from `generated.roster_ref`. Lower stakes than B to D, since `main` resolves `ref` itself before calling, but `--check` with a ref override is not covered. Carry: R10-PLAN-ARTIFACT
- Forward-carry not written: the premise change to R10-ORCH-MACHINERY item (3) has to go into that group's `brief` or `carry` on the roster, with its control (`plan_page.py --self-test` re-measured at that stage's merge base) stated as a precondition, before this PR merges. The same applies to retiring the out-of-tree `gen.py`/`tpl.html`. Carry: R10-ORCH-MACHINERY

## Evidence

- RESULT `plan_page self-test: 36 checks, 0 failed` at the head (`ev/plan_page_selftest.txt`). This matches the body.
- RESULT `replan.py --self-test: 0 failed`, including `mutation freshness: 'if have != want:' -> rc=1` (`ev/replan_selftest.txt`). This matches the body.
- RESULT fixer's driver `r10_plan_page_mutants.py`: `survived=0`, 14 rows killed (`ev/fixer_mutants.txt`). This reproduces the body, but the driver is the fixer's own and does not cover B to E.
- RESULT reviewer mutants: M0 null rc 0/0; A (`if not want:` -> `if False:`, a blob-less plan accepted) killed by replan's self-test; B, C, D and E survived (`ev/reviewer_mutants.txt`).
- Finder's harness: this group has no finder or committed finder harness. It is a roster `kind: fix, class: tooling` group with `findings: []` and `issues: []` (`ev/roster_groups.txt`). Every arm here is the fixer's or mine. Mine is `ev/reviewer_mutants.txt`, and I disclose it as my own instrument.
- `git merge-tree --write-tree origin/main 59c5b20ef0d7beef377fe2580bd87f9fdb783ff7` exited 0 with tree `86a75f8c99b8044ee7d83b5dbc115c2d2448981a`: clean, with no claim-file conflict.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden` are untouched in the three-dot diff from the merge base.
- Cheap checks at the head (`ev/cheap_checks.txt`):
  - `selftest_wiring: 39 self-testing, 39 wired, 0 unwired`. The body says 38; main added one instrument after the body's measurement base. Both counts have 0 unwired.
  - `tmp_paths: 0 refused`.
  - `ref_privacy ... 0 refused`.
  - `claims hygiene: origin/main ok`.
  - `closure.py select --diff origin/main`: `MODE: FULL`, with reason `tests/closure.py changes the gate itself`. This matches the body.
  - `tests/harness_headers.py` could not run in this container (`No module named 'voluptuous'`). I did not re-derive that figure.
- Figures I could not re-derive: the live-page figures (108 rows, stage counts, 11 of 14 open PRs). They used a hand-assembled GitHub snapshot that is not committed, and the roster has since grown to 128 groups at `8a6d2250`.
- CI on this head, from the check-runs API at about 21:09Z. Concluded: `pr-contract` (run 39675845704) green, `arch-score` green twice, `budget-raise-gate` green twice. Still queued or in progress: `pr-contract` (run 39675846088), `instrument-self-tests`, `policy-docs`, `delivery-status`, `env-matrix`, `wave-script`, `scope`, `hassfest`, `validate-hacs`, `briefs`, `mutation` and `closure-scope`. The verdict above rests on local measurement, not on those runs.
- `nightly-status` (job 119485352084) is red on scheduled run 39563978649 (`mutation-nightly`, `slow`), the run the body's `## Red checks` names and answers as main's. It is not a required context and does not block.
- Head check: the PR's head was `59c5b20ef0d7beef377fe2580bd87f9fdb783ff7` when I read it, and the body's `## Head` names it.
