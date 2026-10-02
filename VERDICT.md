Fix review: blocked e78ac3016b1cca0085709c984ebf848ebb2af8f4 root-cause-unanswered: mutation went red at 0135f1ac and 6cbc5661 (5 unpinned sites, repaired by the mutation-autofix carry e78ac301) and fast went red at 0135f1ac (main's always() red), unnamed in the body; body-only, no head change owed

bus-nonce: 1b9464d79aeded3883e0169b8789a8b6

Round 4. PR #1852 (R9-EG-B3a, Part of #1737). Measured head: `e78ac3016b1cca0085709c984ebf848ebb2af8f4`, the live head when I posted. It is the dispatched head `6cbc566164a4fbccac3df36ce0ea566474e1538a` plus the `mutation-autofix` commit `ci: pin killed mutants`, which I reviewed as a carry, as the dispatch asked. **The nonce was minted for 6cbc5661, so the orchestrator should expect `BUS undispatched` for e78ac301 and re-dispatch if the bus requires it.** The evidence directory names both heads.

**The code is ready.** Every gate check is green at e78ac301. What is owed is one paragraph in the body, plus `## Head` naming the current head. After that edit, the same head can take `merge`.

## The resolution delta and the carry

- **6cbc5661 = 0135f1ac + origin/main `aa7a81192`** (hotfix #1859). `git merge-tree --write-tree 0135f1ac5 aa7a81192` gives tree `12de0e13e4f1…`, identical to the head's tree, so the merge is fully automatic with no hand resolution. The PR's three-dot diff is unchanged (16 files).
- **e78ac301, carry (`ci: pin killed mutants`, github-actions[bot]).** It touches 5 `tests/mutation_ledger/killed_by/` files and nothing else (`evidence/carry_e78ac3016.diff`). It pins exactly the 5 sites the round-3 table named as added by this diff:
  - `binary_sensor.py` `_plan_outdoor_now` GUARD_OFF, killed by `entities.py`
  - `coordinator.py` `_build_data_dict` RETURN_DEL `return cast(Payload, data)`, killed by `env_drift.py`
  - `entity.py` `<module>` GUARD_OFF `if TYPE_CHECKING`, killed by `structure.py`
  - `entity.py` `_data` RETURN_DEL, killed by `entities.py`
  - `sensor.py` `_advice` RETURN_DEL, killed by `entities.py`

  Each pin was recorded `rc=0 failed=0 → rc=1 failed=1` against `aa7a81192`.

## CI at e78ac301 (`evidence/check_runs_e78ac301.tsv`, `workflow_runs_e78ac301.tsv`)

- **Everything that ran is green:** `fast (3.14)`, `mutation`, `typing`, `closures`, `coverage`, `coverage-ratchet`, `env-matrix`, `recheck-gate`, `nightly-ha (2025.2.0, stable)`, `budget-raise-gate`, `delivery-status`, `policy-docs`, `instrument-self-tests`, `wave-script`, `hassfest`, `validate-hacs` and CodeQL. These Tests results come from a `workflow_dispatch` run on this head.
- **The `pull_request` runs of `Tests` and `PR contract` at e78ac301 are `action_required`:** the bot's push is waiting for approval, so **`pr-contract` (the body check) has not run at this head.**

## What the body owes (the red-check trigger, `fix-review.md` step 11, "the head's runs are not the range's")

The body's `## Red checks` answers the four reds at 29b763d7, but nothing after them. These reds in the range are unnamed:

1. **`mutation` at 0135f1ac5 and at 6cbc5661 (`MUTATION TABLE REFUSED`, 5 unpinned sites added by this diff).** This is the killed-unpinned case that `ci-autofix.md` assigns to `mutation-autofix`. It was repaired by carry `e78ac301`, and naming it is the answer.
2. **`mutation-autofix` at 0135f1ac5 (`skip-measure-failed`).** It followed from item 3, which made the pin baseline inconclusive.
3. **`fast (3.14)` at 0135f1ac5.** One `entities.py` check, "no job-level `if` leads with `always()`", naming `tests.yml:mutation-ledger` and `-push`. It was main's red: main's own `8fa06663c` failed the same check, the PR touches no `.github/`, and hotfix #1859 (`aa7a81192`) fixed it.
4. `nightly-status` at 6cbc5661: "NIGHTLY ABSENT: mutation-ledger, mutation-ledger-push did not run in that scheduled run". This is **not this PR's** (step 11: the diff reaches no script, job, plan, HANDOVER or delivery row other than its own), and the check is unrequired. Naming it is optional. It reads skipped at e78ac301.

Also update `## Head` to name `e78ac3016b1cca0085709c984ebf848ebb2af8f4` as the PR head (the autofix carry on 6cbc5661). Then approve the held `pull_request` runs so `pr-contract` judges the body at this head. Neither step changes the head, so this verdict's measurements carry and I would return `merge` on the same SHA.

## Carried from earlier rounds (no production change since round 2)

- Contract: census 0 errors, my probe inverts as designed, golden type mismatches 0, EG-B3 at 173 = 173 (null control red against round-1 `payload.py`).
- Round-3 owed items all delivered: the qs_rules null control holds; `closures` is green with the hand-merged recordings; the architecture figures are right.
- B3b carries: the enumeration check's missed patterns, the `handover` store, the 23 `dict[str, object]` keys, and the overstated `untyped_payload_keys` figure.
- Fourth round: under the three-round rule, a re-cut body is owed from here. The edit above is that re-cut, and only the red-check and head sections change.
