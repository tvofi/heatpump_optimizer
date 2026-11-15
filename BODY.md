R11-PRE-MACHINERY-LIMITER, part 1 of 3: card P2 (owner ruling 2026-11-13) and the group's carries 0-4. Carries 5-12 are parts 2 and 3, dispatched at this handoff.

**P2, the target.** `machinery_ratchet.py` gains THE TARGET (its docstring is the rule): `dev/governance/config/machinery_target_budgets.json` holds `anchor`, `every_merges` and `step`, and the target is `nonproduction_merges - step * floor(n / every_merges)`, n the first-parent merges after the anchor up to the base (PR mode) or head (push mode), never below 0, compared against target plus the existing band. **The schedule:** anchor `b3831ff64e` (this branch's merge base, where the cap was recorded), 48 down every 290 merges: 290 is half the frozen `window_merges` (the owner's seven days of merges), 48 is 10% of the recorded 478 rounded half up (the audit's "e.g. -10% per week", section 6 row a2). **The enumerator:** `python3 tools/audit/machinery_ratchet.py --measure --head origin/main` now prints `target` and `merges_past_anchor`; `--check` prints a `target` line. At a round start the orchestrator records the cap down to `--measure` and asks the owner for the round's anchor and step (`ratchet-budgets.md`); `budget_raise_gate.py` classifies a moved anchor, a longer `every_merges` or a smaller `step` as a raise.

Why a second budgets file and not three keys in `machinery_budgets.json`: `governance.yml` grades a pull request with the BASE's `machinery_ratchet.py`, whose `load_budgets` refuses a key it does not read, so the keys there would turn `policy-docs` red on this pull request (a BOOTSTRAP split, `fixer.md` step 5). The new file is invisible to the base copy, and it is a `*_budgets.json`, so the raise gate guards it; a constant in the program would not be guarded (the program is not code-owned).

Where it binds, a design choice: only a non-production, unexempted candidate in PR mode. A production candidate cannot raise the metric, and the existing code refuses any candidate when the window is over the cap, so a binding target under the old semantics would refuse production work. In push mode the target is a report line: a schedule overtaking the window would otherwise turn a required check on main red with nothing to repair. The two caps stay the ceiling in both modes. **For the owner's review:** a machinery repair of a red required check on main is refused by the target like any machinery merge once the window is past it; its routes are the band, an earned exemption, or an owner-approved change to the schedule. The alternative, a ground the offline ratchet would have to read, was not taken.

**P2, the rest.** `proposal-triage.md`: on severity only a red required check on main or a blocked production pull request skips the machinery bars (`medium`, `high`, `major`, `critical` no longer do); root-cause countermeasure, closeout and owner directive keep their routes, which are not severity. `ratchet-budgets.md`: one in, one out for required checks, the set `merge_train.py owed-reds` prints.

**Carry 0, Carry 1 and Carry 2, the instrument freeze** (`orchestrator.md`, replacing the "proposal waits" bullet; Carry 1's owner and outside items also in the scope bullet and the playbook's round start): local prototype under `$HPO_STATE_DIR/r<N>/proto/<id>/`, each use a sweep-log `WORKAROUND <id> onset=<UTC> cost=<min>` line; the permanent fix a numbered entry of the proposals file in `$HPO_STATE_DIR/r<N>/` citing the prototype and its measured effect; consolidated (duplicates merged, uses and cost summed) and triaged once at round end; ACCEPTs built at the next round's start before its finders, the rest refused with their numbers; a workaround never changes production code, loosens a gate or budget, or skips a review; the exceptions are a production defect, an owner order, a red required check on main, and an owner or outside item. The scope bullet now folds an undeferred owner or outside item into the ongoing round. The playbook's round start gains step 4 (where the prior round's proposals and prototypes are, and that its ACCEPTs are built before finders); step 5 (was 4) already states the deferral record (who, when, their words) and that silence is none.

**Carry 3:** `nonproduction_merges` re-recorded 521 -> 478 (more than its band of 5 below the cap); `churn_per_kilo_product_lines` stays (13785 against 14797, inside its band of 3636). **Carry 4:** `pr_cap.py` classes open pull requests by `machinery_ratchet.is_product` (one predicate), `dispatch-gate --machinery OWNER/REPO` refuses a machinery group once machinery and unread pull requests fill the slots production does not hold (`replan.py` `DEFAULT_CAPS` slots less `PRODUCTION_SLOTS`), and `orchestrator_tick.py`'s cap levels print `pr_cap.class_line` every pass (five lines there; the batch's L5 hold on that instrument covers proposals, and P742 routes this carry here).

Payment for the policy caps: `ratchet-budgets.md` lost three spent sentences (two historical measurements of the CLAUDE.md split and the "deferred, not disabled" motivation); `dev/audit/README.md` lost the organization-transfer item, ruled out by tvofi 2026-11-14 (`dev/programme/HANDOVER.md`, the designer's answers), cut to one line.

## Head

`3ad61a1f6e09044cd47db34952a3ab681db1b1e5`, unchanged by this repair round (the round edits the body only), adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/3627.md`. The authored code head is `81e2beea953734b9c48e3224924735eb9572635c`.

`b569a6120604b75f4ead324f86391449a150ffd9` merges origin/main `66865be375` into the authored code head `81e2beea953734b9c48e3224924735eb9572635c` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

Merge base at the head: 66865be375f4ee283ee556f53fcd76cc3dbf40e2; `origin/main` 98847b99d7bb3238686efd6869f805c89c6d1ff1 at 2026-11-15T20:43Z, and `git merge-tree --write-tree origin/main HEAD` reports no conflict. The figures below are from the authored code head 81e2beea953734b9c48e3224924735eb9572635c at merge base b3831ff64eca1936f0b618193ee86c3e337b51a9 (`origin/main` at 2026-11-15T13:30Z) unless marked as re-taken at 3ad61a1f6e.

## Mutation proof

Each mutant applied alone at the head, its self-test run, the file restored:
- `machinery_ratchet.py` `bad.append("target")` -> `pass`: `target: 2 merges past it falls to 0 and refuses the machinery candidate under its cap` and `target: a record candidate is not production and is refused too` FAIL (66 checks, 2 failed).
- `binds = cand is not None and cand["kind"] != "production"` -> `binds = cand is not None`: `target: a production candidate is never refused by it (a report line)` FAIL.
- `scheduled_target` returning the cap: the two refusals above and `target: --measure prints it beside the metrics` FAIL (3 failed).
- `pr_cap.py` `if len(taken) < free:` -> `if True:`: `a machinery group is refused once machinery and unread fill the free slots` FAIL.
- `by_class` classing every read diff machinery: 5 checks FAIL, the first `by class: a product path makes production, none machinery, an unread diff neither`.
- `load_target`'s `if not isinstance(doc, dict)` -> `if False`: `target: a file that is not an object is refused` FAIL; its `v < (1 if k == "every_merges" else 0)` -> `<=` or `< (2 ...)`: `target: every_merges 1 and step 0 are the bounds it reads (null control)` FAIL (both `prepr.sh` survivors at the previous head, killed here).
- `budget_raise_gate.py` `("step",) MIN` -> `MAX`: `target: a faster decline is routine` and `target: a slower decline is a raise` FAIL.

## Null control

- `target: no file, no target: the refused candidate passes (null control)`: the same machinery candidate at the same base passes once the target file is gone.
- `target: 1 merge past the anchor is still 2, so a machinery candidate at 2 passes`: the schedule, not the window, refuses.
- `null control: one free machinery slot passes`; `null control: below the machinery slots the line is not flagged`; `target: null control` (an unchanged target file is no raise).
- At the merge base `git grep -n -i "one in, one out" b3831ff -- dev/governance` prints nothing; at the head one line in `ratchet-budgets.md`.

## Figures

- `python3 tools/audit/machinery_ratchet.py --measure --head origin/main` at b3831ff64e: `nonproduction_merges` 478, `churn_per_kilo_product_lines` 13785, `window` 580, `production` 102; at the head `target` 478, `merges_past_anchor` 0.
- `python3 -I tools/audit/machinery_ratchet.py --check --base origin/main --head HEAD --pr 1`: `ok nonproduction_merges 478 <= 478 + band 5`, `ok target nonproduction_merges 478 <= 478 + band 5 (0 merge(s) past anchor b3831ff64eca, 48 down per 290)`.
- Self-tests at the head: `machinery_ratchet.py --self-test` 68 checks, 0 failed; `pr_cap.py --self-test` 29, 0 failed; `budget_raise_gate.py --self-test` 287, 0 failed; `orchestrator_tick.py --self-test` 322, 0 failed.
- The severity skip, enumerated: `git grep -n -E 'major\`, \`critical|\`medium\`, \`high\`' <rev> -- dev tools/audit/seat CLAUDE.md .claude` prints `proposal-triage.md:23` at b3831ff64e and nothing at the head; `git grep -n -i severity -- 'tools/**/*.py' | grep -i -E 'bar|skip|exempt'` prints nothing at either end, so no program implements the skip.
- `node tools/policy/policy_lint.mjs --budgets` at the head: every row within its cap; `node tools/policy/policy_lint.mjs` TOTAL 0 errors; `node tools/policy/rules_sync.mjs --check` ok.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Re-taken at 3ad61a1f6e: `python3 tools/audit/archscore/score.py --diff 66865be375f4ee283ee556f53fcd76cc3dbf40e2 HEAD` prints `Architecture score: dS +0.0000 NULL`. The score reads only `custom_components/heatpump_optimizer`, and `git diff --stat 66865be375f4 HEAD -- custom_components` prints nothing, so NULL is the reading the score's own scope fixes; a diff touching no scored file has no improving payment the score could register.

<!-- figure-block: scope-line mb=66865be375f4ee283ee556f53fcd76cc3dbf40e2 head=3ad61a1f6e09044cd47db34952a3ab681db1b1e5 -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

## Raise justification

The base's `budget_raise_gate.py` reads the new `machinery_target_budgets.json` as an added file with no schema, all frozen, so a raise; the head's schema still reads its `anchor` appearing as one. It tightens: the target only lowers what `nonproduction_merges` admits. The owner's approving review is owed regardless (card P2 is policy).
- Payments tried: three keys in `machinery_budgets.json` (refused: the base copy's `load_budgets` would turn `policy-docs` red, see above); constants in `machinery_ratchet.py` (refused: not guarded by the raise gate, so a seat could slow the schedule unreviewed); a cap re-recorded below the measurement by hand each week (refused: under the old semantics it refuses production candidates and turns main's push red).
- Architecture score: dS +0.0000 NULL

## Unpinned sites

`python3 -I tools/audit/seat/mutant_run.py --diff b3831ff64eca...HEAD --cmd "sh -c 'python3 -I tools/audit/machinery_ratchet.py --self-test && python3 -I tools/audit/seat/pr_cap.py --self-test'" --max-mutants 40 --report-only` (and `prepr.sh`'s diff-mutant step at this head): 6 survivors, every one in `machinery_ratchet.py`'s self-test fixture, none in a production line: the fixture's pull-request numbers (`r.merge(1|5|6, ...)` swapped, which only names a merge), `caps(m1=2)` -> `3` on the exempted candidate (an exempted candidate is skipped whatever the cap), and two `ok(...)` assertion lines deleted (the 770 and 777 sites, a check removed rather than behaviour changed). Disposition: fixture data and assertions, no production behaviour to pin.

## Red checks

The owed set is `python3 tools/audit/seat/merge_train.py owed-reds`, which prints all three names below.

- `budget-raise-gate / budget-raise-gate` (jobs 132933980724, 132947660830): the merge base's `budget_raise_gate.py` reads the added `machinery_target_budgets.json` as five pinned values it cannot sign as routine (`_comment`, `_recorded`, `anchor`, `every_merges`, `step`; `RESULT budget_raises=5 count`), and refuses with no decisive review at the head. Red by design until an approving review at the head (see `## Raise justification` and `## Approval`). No cheaper detector exists: the gate is the approval itself, and `prepr.sh`'s body check already predicts the raise before the pull request opens.
- `pr-contract / pr-contract` (job 132946649167, step "Check the body against the contract"): the previous body named the raise gate's red as `budget-raise-gate`, not its full check name `budget-raise-gate / budget-raise-gate`, so `policy_lint.mjs --pr-body` found the red unanswered. Repaired in this body. Cheaper detector: `tools/pr/prepr.sh`'s body check runs `policy_lint.mjs --pr-body` locally, but only over the reds that exist when it runs; this red appeared after the handoff, so no detector earlier than the CI run that read it existed for this body. None built.
- `gate`: follows the two above and has no failure of its own.

## Approval

This diff touches policy owned by @tvofi under `.github/CODEOWNERS` (`dev/governance/rules/ratchet-budgets.md` and its generated copies, `dev/governance/roles/proposal-triage.md`, `dev/governance/roles/orchestrator.md`, `dev/audit/README.md`) and adds a budgets file the raise gate reads as a raise, so it merges only on the owner's approving GitHub review at the head (decision 0009 step 6; decision 0013). Owner rulings it implements: card P2 and P11 (2026-11-13), carries 0-2's verbatim owner words, P742's ratification (2026-11-15). The schedule's numbers (anchor, 48 per 290 merges) and the main-red route above are the owner's to confirm in that review.

## Forward-carry

- `dev/programme/HANDOVER.md`'s owed item "Two sentences of `dev/audit/README.md` are stale": its organization-transfer half is discharged by this diff, the soak half stays. Carry: dismissed: the next record pull request re-derives that list from the tree.

## Friction

none
