Fix review: blocked 22ed5ed703125446b70f18eac07dc75b5592a53a root-cause-unanswered: pr-contract went red at this head on the body's unrouted `## Forward-carry`, and the body neither names nor answers it

bus-nonce: 7a86ac0b7292a0842998cf8fcba50633

## Head

Measured `22ed5ed703125446b70f18eac07dc75b5592a53a`, the head the body's `## Head` names.
During the review the head moved to `478cc27efd03d59d97899cff0d67f2e912ce7918`, a
coordinator-directed recarry merging `origin/main` (`76bb45628745`, #2465's merge
commit) into the branch. Per the dispatch I keep this verdict at 22ed5ed7 and
measure the delta and the floors at the new head below. The block holds at **both**
heads (pr-contract is red at 478cc27e too; see Red checks), so it is not a
head-moved block.

## Direction — the change is a withdrawal, not a raise (brief 1)

The diff removes `tests/stress_budgets.json`'s `coverage_floor_override`
(`floor` 18, `calls_floor` 6) and touches no other budget. That override could only
ever *lower* the floors: `coverage_floors` accepts it only when
`0 < floor < SCENARIO_WORK_MIN_COVERED` (`tests/stress.py` `lowers()`), and the
literal is 40. So the override was a one-sided easing (40/15 -> 18/6), and removing
it restores the stricter literal (40/15). A tightening needs no owner review; a
loosening would.

`python3 -I tools/policy/budget_raise_gate.py --base origin/main --head HEAD --pr 2485`:

- at 22ed5ed7: `RESULT budget_raises=0 count` / `PASS: no budget raise; no owner review is owed`
- at 478cc27e (vs origin/main 76bb4562): `RESULT budget_raises=0 count` / `PASS`

The gate's own self-test separates the two directions and passes 239/0:

    ok   stress: the override lowered is a raise
    ok   stress: the override withdrawn is routine (the literal is stricter)
    ok   stress: an override granted is a raise

So a re-added override is a raise the gate would refuse, and the committed head is
its withdrawal — routine. Not a raise wearing a withdrawal's clothes.

## Derivation, not a carried number (brief 2)

Re-derived with the committed function, not the body's figure:

    RESULT coverage_floors(table, 20, 54) with override  = (18, 6), cites set
    RESULT coverage_floors(table, 20, 54) without override = (40, 15), cites None
    RESULT sweep_scenarios=54  calls_population=20
    RESULT own_share(40,20,54)=15   (matches the function's share rule)
    RESULT control: re-add override -> (18, 6)
    RESULT control: override floor 45 (> literal) is ignored -> (40, 15)

Same numbers at the #2465 tree (478cc27e): 54 scenarios, 20 families, (40, 15). The
54 scenario rows are untouched — the JSON goes 55 keys (54 + override) to 54 keys,
and `git diff` shows only the override key removed. Evidence:
`evidence/02_rederive_22ed5ed7.txt`, `evidence/03_rederive_478cc27e.txt`.

## Ledger edit (brief 3)

`dev/audit/config/bugclasses.json` row `R10-N-structure-blind` gains
`"landed": "ecdeb42c (#2441)"`. The field pre-existed (base value `null`), so no
field was invented. `ecdeb42c` is `Merge pull request #2441 from
tvofi/fix/r10-archscore-census`, an ancestor of `origin/main`.
`python3 tools/audit/fold_ledger.py check` -> `0 violation(s)`.
Evidence: `evidence/04_ledger.txt`.

## Claim files and suspension (brief 4)

Both claim files are byte-identical to the merge base
(`git diff --quiet <base> -- tests/golden/claimed_drift.txt
tests/golden/card_claimed_drift.txt` returns 0). The stamp's own rule
`tools/release/stamp.py::restore_suspended` finds **0** suspension notes at the
head and changes nothing; its positive control on `daca95c5d^` finds 19
` suspends ` lines and fires (12 restored, 7 stale, changed=True), so the rule is
not vacuous. Evidence: `evidence/05_claims_bytecompare.txt`,
`evidence/05_suspension.txt`.

## Red checks (brief 5)

Read from the head's own check-runs API (not `gh pr checks`).

- `nightly-status` red — **exempt**. It reads Actions run metadata only, not any
  file this diff touches; the failure is the scheduled `slow` lane at main's
  `0c298f6` (job 118512165515), and the job itself states it is not a required
  context. Orchestrator's to fix on main.
- `pr-contract` red — **this PR's, and unanswered**. `pr-contract` is a required
  context (ruleset 23698884). At 22ed5ed7 its push-time run (job 118637666157)
  failed in `carry_audit.py`:

      UNROUTED body item 522e1cd9 (## Forward-carry) [section]:
        "none. The stamp-time items R10-STAMP's roster entry carries from #2445 ..."

  I reproduced it against the live body:
  `python3 -I tools/audit/carry_audit.py check --body body.md` -> same 1 unrouted
  item (`evidence/08_carry_audit_repro.txt`). Cause: the section begins `none.`
  and then *records* items, which `carry_audit`'s `NONE_ITEM` rule deliberately
  refuses ("a `none` that goes on to record something is not one", #2341) — so it
  is a finding item with no `Carry:` marker. The body's `## Red checks` does not
  name or answer `pr-contract`. At 478cc27e it is red again
  (`evidence/07_checks_478cc27e.txt`).

The body's local stress reds (shoulder economics 4.67 vs 3.96 at both heads; RSS
24.5 vs 9.4 MiB after only) are the fixer's local runs, not CI checks; I did not
re-run the stress solver, and CI's `fast`/`coverage` lanes at 478cc27e settle the
actual coverage.

## #2465 caveat and the carry (brief 6, coordinator items 1-2)

#2465 is now merged (`76bb4562`). The delta
`git diff --name-only 22ed5ed7 478cc27e` is exactly #2465's file set and, crucially,
**does not touch `tests/stress_budgets.json` or `dev/audit/config/bugclasses.json`**
(nor `dev/programme/delivery/2485.md`) — none of this PR's own files
(`evidence/09_delta_22ed5ed7_478cc27e.txt`). On that basis a `merge` verdict would
carry to 478cc27e on the delta.

The floors question, measured on the #2465 tree: `coverage_floors(table, 20, 54)`
still returns `(40, 15)` and the counts still read 54 scenarios / 20 families
(`evidence/03_rederive_478cc27e.txt`). This is structural, not luck: the population
is `sweep_combinations()` (static `SEASONS`/`BUILDINGS`/literal specs in
`tests/stress.py`) and `calls_population(combos, table)` (family keys from
`case_key` over the same statics + the budget table). #2465 changes production code
and `tests/features.py`, none of which these read, and it does not touch
`tests/stress.py` or the table. So #2465 does not move the floors. What I cannot
settle locally is the *actual covered count* against the floor; CI's `stress`
lane at 478cc27e settles that.

The stamp should still re-run its own end-merge floor re-derivation after the
**final** recarry (it is cheap and the body's protocol promises it), but there is
no floor risk from #2465 itself.

## Usual (brief 7)

Diff is three files; `VERSION` (7.0.1), the manifest version and the
`RELEASE_NOTES.md` heading are untouched. The body's `## Head` names 22ed5ed7 (my
measured head); the live head is 478cc27e, so a re-post must re-point `## Head`.
`merge-tree --write-tree origin/main HEAD` -> rc 0, no conflict. `structure.py` ->
`STRUCTURE RATCHET PASSED`; `env_drift.py --claims-only origin/main` -> ok.

## The block, and its fix (body-only)

The budget direction, derivation, ledger, claim files and suspension all verify;
the sole blocker is the required `pr-contract` red, which the body does not answer.
The forward-carry's *substance* is fine — I confirmed the stamp-time items are
already in the roster (`dev/programme/rosters/wave-r10-groups.json:4056-4058`,
"Owed at the stamp"/"Owed after the stamp"), so this branch owes no new carry.

Fix:

1. In `## Forward-carry`, either make it a genuine `none.` (the items are already
   carried by the R10-STAMP roster) or route each with
   `Carry: R10-STAMP` — do not leave a `none.` followed by prose.
2. Add `pr-contract` to `## Red checks` with its answer: the cheaper detector is
   `carry_audit.py check --body` (seconds, standing cost ~0), which was not run
   before push.
3. Re-point `## Head` to the live head.
4. A body edit re-runs `pr-contract` at the same head; a round-2 verdict can then
   carry the delta/floors results above.

Carry: dismissed: body-only fix to this PR's own `## Forward-carry`, re-run pr-contract.

## RESULT

    RESULT budget_raises=0 at 22ed5ed7 (gate PASS) and at 478cc27e (gate PASS)
    RESULT override withdrawn: floors 18/6 -> literal 40/15 (a tightening, not a raise)
    RESULT coverage_floors base=(18, 6, cites) head=(40, 15, None); control re-add -> (18, 6)
    RESULT sweep_scenarios=54 calls_population=20 at both heads (incl. #2465 tree)
    RESULT ledger: field pre-existed (null); ecdeb42c (#2441) on main; fold_ledger 0 violations
    RESULT claim files byte-identical to merge base; suspension notes at head = 0 (control = 19)
    RESULT delta 22ed5ed7..478cc27e = #2465 only; misses stress_budgets.json and bugclasses.json
    RESULT pr-contract RED (required) at 22ed5ed7 and 478cc27e; carry_audit UNROUTED ## Forward-carry
    RESULT nightly-status RED but exempt (reads Actions metadata, not the diff; unrequired)
    RESULT structure.py PASS; env_drift --claims-only ok; merge-tree rc 0

Not verified: the local stress economics/RSS reds (no solver re-run on this box; CI's
stress lane at 478cc27e settles the covered count), and the actual covered count
against the 40/15 floors.
