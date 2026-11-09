R10-HOTFIX-DELTA-REVIEW. Owner ruling (tvofi, 2026-11-09): "I though it was always only the delta that was reviewed in later review rounds? If not, make it so". Before this change, `fix-review.md` step 12 limited a later round to a main merge's resolution delta, and "any other move is re-reviewed", so every round after a blocked verdict re-reviewed the whole three-dot diff. Now a later round covers `git diff <reviewed-head> <head>`, a check that each finding of the previous verdict is resolved, and the live required checks. A full re-review needs a reason the verdict names: that the delta reaches code the earlier review relied on.

`review_packet.py render --reviewed-head <rh>` puts the delta and the VERDICT.md of the newest `verdict/<pr>` commit whose first line names `rh` (parsed by `proof_watch.parse_verdict`) in place of the three-dot diff. In three cases it keeps the three-dot diff and its `## Review scope: full (<why>)` line says which: a first round, an `rh` that is not an ancestor of the head, and an `rh` that no verdict names (`review_scope`). `bus.sh dispatch` already took `--reviewed-head` for the carry check, and now passes it to the renderer as well. A cloud reviewer renders its own packet from its prompt, so `cloud_dispatch.py --role reviewer` takes `--reviewed-head` too. It puts the flag into the reviewer's render command and into `bus.sh dispatch` (`--group` forwards it).

`standing-dispatch.md` states no review scope, so it is unchanged (brief item 1: "if it states the scope"). The dispatch seat already names `--reviewed-head <blocked head>` for round-2 reviews (`dev/programme/triage/s6-batch95.md`).

Alternatives: (a) only reword the policy and leave the packet alone. It lost because the reviewer starts from the packet, and a packet holding the full diff keeps steering it to a full review. (b) Render the delta whenever any earlier verdict exists, without checking ancestry. It lost because after a force-push `git diff rh head` is no later round's delta, so this change falls back to the full diff and says so.

## Head

b5136419898721dca18a1cd76f53aa93d25b369d

## Mutation proof

`python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py` (in this PR). For each mutant it edits one span in place, runs that file's own `--self-test` and restores the file; `mutant_guard` restores the file on a kill. The harness exits rc=0 with `MUTANTS: 7 run, 0 not as required`: M0 (the unmutated head, all three self-tests) is PASS and M1 to M6 are KILLED:

- M1 `scope_facts` always takes the three-dot diff: review_packet self-test rc=1, `FAIL scope_facts: a later round's diff is `git diff <rh> <head>` alone -- the round-one row is not in it`
- M2 `scope_parts` never renders the delta: rc=1, `FAIL scope: a later round renders `git diff <rh> <head>` and the previous verdict's findings, not the three-dot diff`
- M3 `review_scope` without the ancestor check: rc=1, `FAIL review_scope: delta only with a reviewed head that is an ancestor and a verdict naming it; else full, saying why` and `FAIL scope_facts null: a reviewed head that is not the head's ancestor reads the three-dot diff`
- M4 `previous_verdict` ignores the head the verdict names: rc=1, `FAIL previous_verdict: the newest verdict whose first line names <rh>; another head's, an older one and a malformed line are skipped; none naming it is None`
- M5 `bus.sh dispatch` drops `${rh:+--reviewed-head "$rh"}`: bus self-test rc=1, `FAIL a later round's dispatch hands the renderer its --reviewed-head, so the packet is the delta (fix-review.md 12; null: the harness dispatch below passes none)`
- M6 the cloud reviewer prompt drops `--reviewed-head`: cloud_dispatch self-test rc=1, `FAIL a later round's reviewer renders its packet with --reviewed-head and is told its scope is the delta (fix-review.md 12); null: a first round's render names no reviewed head`

## Null control

- A first round still gets the full diff. In the pure self-test, `build` with no scope renders `## Review scope: full (first round` and `## Three-dot diff`, and no `## Delta diff` or `## Previous verdict`. On real commits in a throwaway repository, `scope_facts(7, None, ...)` reads the three-dot diff, and that diff holds round one's delivery row. The delta read over the same head does not.
- A reviewed head that is not an ancestor of the head falls back to the three-dot diff (`scope_facts null` check).
- In bus.sh, the existing harness dispatch check pins the exact renderer argv `render|--pr|7|--head|<h>|--out|...|--harness|...|`, with no `--reviewed-head`. In cloud_dispatch, a first-round prompt contains no `--reviewed-head`.
- I ran `previous_verdict` against the live `verdict/3359` ref. For `40c79702c72359f00a0a932eabf727a942b1f9eb` it returns that head's newest verdict, `Fix review: merge 40c79702...`, not the earlier blocked one. A head that no verdict names returns `None`, and so does an absent ref (`verdict/999999`).

## Figures

- `python3 -I tools/audit/seat/review_packet.py --self-test`: 72 checks at the base 2f6d699e504d6dc0bb6040d99c21c5b015a290e4 and 79 at the head, 0 failed at both.
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test`: 132 checks at the base and 135 at the head, 0 failed. The three new checks are the table-driven `--group forwards --reviewed-head` row plus two prompt checks.
- `bash tools/audit/seat/bus.sh --self-test`: 161 checks at the base and 162 at the head, 0 failed.
- `node tools/policy/policy_lint.mjs --budgets`: the `fix-review.md` row is at its token cap at the head, the same cap as at the base. The new step-12 text is paid for by rewording steps 6, 8, 9, 12 and 13 with no change in meaning. No cap is changed.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`. No rule source changed, so nothing was regenerated.
- `python3 tests/closure.py select --diff 2f6d699e504d6dc0bb6040d99c21c5b015a290e4`: `MODE: SCOPED`, and `scope.run` names `tests/doc_claims.py` and `tests/entities.py`. Both ran with `PYTHONPATH=tests/hastub`: doc_claims `ALL 297 checks PASSED`, entities `3 of 2707 ENTITY CHECKS FAILED`. All three are de.json checks (`de.json has exactly strings.json's keys` and the two `every flow field has a label/description ... in de.json` checks), and the key gap they report also exists at the base 2f6d699e. A key-set diff of `strings.json` against `translations/de.json` at the base prints `flow_heat_c`, `flow_min_lift_k` and `selector.space_setpoint_unit.options.return`. This diff touches nothing under `custom_components/`. The `run_always` steps also passed: `env_drift.py --claims-only` (`claims hygiene: ... ok`) and `closure.py selftest` (`ALL 118 closure shrink pins PASSED`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 2f6d699e504d6dc0bb6040d99c21c5b015a290e4 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 tools/pr/ci_predict.py --apply-inert`: added the new harness as an inert read of `tests/harness_headers.py` in `tests/closures.json`, then printed `CI PREDICT: no closures, fast, governance or instrument red predicted`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- Finder's harness: none. The finding is an owner ruling on process, not a measured defect, and its controls are the self-test arms above, which the fixer wrote.

## Unpinned sites

- `cloud_dispatch._bus_dispatch` passes `--reviewed-head` to `bus.sh dispatch`. No test drives this argv, because the reviewer path through `dispatch_group` would need a verdict ref at a reviewed head in the throwaway origin. The flag reaching `dispatch_group` is pinned by the table-driven `--group forwards --reviewed-head to dispatch_group` check. bus.sh's own handling of `--reviewed-head` is pinned by its P348 checks.

## Approval

This change to `dev/governance/roles/fix-review.md` step 12 carries out the owner's ruling (tvofi, 2026-11-09): "I though it was always only the delta that was reviewed in later review rounds? If not, make it so". The ruling is not the approval. Merging still needs the owner's approving review at this PR's head (code-owner rule, decision 0009 step 6). The rewording that pays for the new step-12 text, in steps 6, 8, 9, 12 and 13, is also in scope for that review.

## Red checks

none

## Forward-carry

- main at 2f6d699e504d6dc0bb6040d99c21c5b015a290e4 fails `tests/entities.py`'s three de.json checks: `strings.json` has `flow_heat_c` and `flow_min_lift_k` labels and descriptions, and `selector.space_setpoint_unit.options.return`, but `translations/de.json` does not. This is not this PR's red, but `entities.py` is in this diff's scope, so `gate` will inherit it here until main is repaired. Carry: #201

## Friction

none
