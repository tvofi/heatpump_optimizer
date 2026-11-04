Fix review: merge 53ce1267c758ae81bd21af1a0d7eba80bc9223c8

bus-nonce: ffe5dc01038275e900e97420b6de8bdf

## Summary

Round 1 fix review of #3196 R10-TWO-ZONE-HHL at head 53ce1267c758ae81bd21af1a0d7eba80bc9223c8, merge base 8e90d81443317f76f22602a89651f7ca17c633f9 (= origin/main at review). Roles contract current (`git diff <base>...origin/main -- dev/governance/roles/` empty). The two production changes (`HousePlant.of_params` two-zone branch; `when=_single_zone` on the thermal-page heat-loss row) are each killed by the PR's own checks, every harness figure in the body re-derives at both ends, the class rule's readers are dispositioned, and it merges cleanly with origin/main.

## Findings

- The body's `## Head` says 53ce1267 "adds one commit, the bot's `ci: pin killed mutants`" to the authored 051b05d9; `git log 051b05d9..53ce1267` shows two: 45e9b4591 (tvofi, "record: the delivery row for #3196", `dev/programme/delivery/3196.md` only) and the bot pin. Neither touches code, so no figure is affected. Carry: dismissed: record-only commit, body wording only, no measured figure depends on it
- Finder's harness: the review packet reads "Finder's harness: none named"; the harness used (`dev/audit/harnesses/r10_two_zone_hhl_inert.py`) is committed and the body discloses it was ported in this diff to drive `arm` (the base copy raises TypeError, confirmed: ev/harness_base_owncopy.txt). Disclosed and committed, so step 9 is satisfied. Carry: dismissed: harness committed and its port disclosed in the body

## Evidence

- RESULT harness at head (ev/harness_head.txt): two_zone_max_dkw=0.000000, two_zone_max_dcost=0.000000, single_zone_max_dkw=4.921374, two_zone_sysid_steps=None,None,None, two_zone_heavy_sysid_steps=2.603,2.603,2.603, two_zone_plant=[(0.33, 2.26)], single_zone_sysid_steps=1.738,3.386,None.
- RESULT harness at merge base, head's harness file (ev/harness_base.txt): identical except two_zone_plant=[(0.1, 10.0), (0.4, 10.0), (1.0, 10.0)]. Every cell of the body's Figures table re-derived.
- Null controls re-run: single_zone_max_dkw 4.921374 and single_zone_sysid_steps 1.738,3.386,None at both ends (not flat-blind); features.py single-zone null check green at head.
- Mutation proof (worktrees at head, PYTHONPATH=tests/hastub), ev/mut_*.txt:
  - of_params fully reverted -> features.py `FAIL R10-TWO-ZONE-HHL a two-zone HousePlant is the zones' loss and mass...` (1 of 4779).
  - ua-only revert -> same FAIL; capacity-only revert -> same FAIL (both halves of the branch are pinned, my own mutants).
  - `, when=_single_zone` dropped -> config_flow_steps.py `FAIL a two-zone entry is not offered the whole-house heat loss...` (1 of 539). entities.py under this mutant also reported 1 of 2602 failing on `main() passes the committed table at its own recorded count (the null control)`, unrelated to the hide; it is green on the clean run.
  - `_single_zone` returning `True` (my mutant, sibling of the pinned RETURN_DEL) -> config_flow_steps.py same FAIL (1 of 539).
  - Clean head: features.py ALL 4779 PASSED, config_flow_steps.py ALL 539 PASSED, entities.py ALL 2602 PASSED.
- Class rule (step 6), re-run at head (ev/class_rule.txt, 29 lines): each attribute reader is in an enclosing function the body dispositions (_held_state, adoption_decision/refuse, arm, battery build, _house_loss_terms, _space_demand_kw, _house_heat_loss_anchor, _floor_demand_at_target, _house_ua_kw_per_c, slab_settlement_cap, house_heat_loss_base, _valve_draw_circuits, _simulate_step_single, _substeps_and_loss), all branched on two_zone except optimize's forecast ratio (inert by form; confirmed by two_zone_max_dkw=0 at head) and mixing_valve.flow_setpoint (parameter). No open seam. HousePlant consumers: only coordinator.py:10899 builds it; sysid reads ua/capacity in the sizer gate, the excursion guard and `_size_step_power`, matching the body.
- env_drift.py --all origin/main: NO UNCLAIMED DRIFT, NO STALE FIXTURE, 56 scenarios, rc=0 (ev/env_drift_full.log); claim files untouched.
- structure.py: STRUCTURE RATCHET PASSED (ev/structure.txt). archscore --diff origin/main: `Architecture score: dS +0.0000 NULL` (ev/archscore.txt). No budget file moved.
- VERSION, manifest.json and RELEASE_NOTES.md untouched in base...head.
- `git merge-tree --write-tree origin/main 53ce1267` exit 0, no conflicts; origin/main is still 8e90d814; PR head re-read before return is still 53ce1267c758ae81bd21af1a0d7eba80bc9223c8.
- Metric moves (step 14): the only instrument entry added is the mutation-ledger pin `_single_zone.RETURN_DEL.6de1e154`. It is earned, since my sibling mutant (`return True`) is killed by the same script. The entities.py round-trip skip is keyed on the registry's own `when`, so with the hide removed it skips nothing. config_flow_steps.py separately pins the hide and that a two-zone save keeps the stored value.
- CI: `merge_train.py classify 53ce1267... --pr 3196` exited 2 twice, `REFUSE ci: the check runs at 53ce1267c758 could not be read` (ev/classify.txt, ev/classify2.txt): unreadable by that tool from this seat. I read the head's check runs directly instead (GitHub check-runs API, 120 runs): all concluded. Latest `pr-contract / pr-contract` success (14:29:54Z, after every other run concluded), `gate` success (14:31:01Z), tests/mutation, closures, fast, coverage, typing, arch-score, budget-raise-gate success. The only red at the head is `tests / nightly-status`, which the body answers (push-only and red on main; this diff does not reach what it reads). Earlier `pr-contract` reds are answered in `## Red checks` (body faults; cheaper detector body_patch.sh --dry-run), as is the authored head's `tests / mutation` red (repaired by mutation-autofix, ci-autofix.md). Step 11 is answered.
- Forward-carry: body says none; the carries are consumed here, not produced, so step 10 has nothing to open.
- Figures not re-derived by me: the body's local scoped-gate line (`MODE: SCOPED -- 22 script(s) run, 11 scoped out.`) and the mutation-proof counts at 9c4b0f13. I cite CI's gate and closures runs at the head instead, per the rule against re-running the heavy gate.
- handoff-wip not pushed: the payload restricts this seat to its probe return ref.
