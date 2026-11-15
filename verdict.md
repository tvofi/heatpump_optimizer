Fix review: merge 7b687a4819e54718f84e4353ce92f665414cb70e

bus-nonce: 0366b2cc1251dbcc2625e7aaa999378f
pending-ci: gate

Round: 2 (delta over the reviewed head 2aff0cc4fe1ea58c40c1113b300592211ee75d3f). Scope: the delta (`tools/audit/seat/plan_phases.py`, `dev/audit/harnesses/r10_plan_page_mutants.py`), the prior verdict's findings and the live required checks. No `custom_components/` delta, so the scope does not widen.

## Findings

- The prior verdict asked the fix round to refuse or disposition four inputs that `violations` still accepts. The head does neither, and the body never names them. Each still passes `--check` and renders, measured at this head (ev/attack.txt, ev/semantic.txt). `started` later than `finished`: violations=0, and the done bar for a phase finished on 02 Jan is drawn as a 4 px sliver at 07 Jan (x=1011.4 against 120.0 in the null control). `forecast.start_from` later than `start_to`: violations=0. `round: true`: violations=0, and the heading prints "Round True phases", because `isinstance(True, int)` holds. `round` disagreeing with its `round<N>/` directory: not re-measured here, and it was accepted at the prior head with no delta touching it. None of these crashes the page; each draws a misleading one. Carry: R11-PRE-PLAN-RENDER

## Notes

- Note: stale-figures: the body's `## Figures` quotes `plan_page self-test: 133 checks, 0 failed` and "23 mutants killed". At this head the self-test prints `136 checks, 0 failed` (the three census checks), and the driver runs 27 `phases-*` mutants, all killed. Several per-mutant `fails=` counts in the body's mutation table predate the census, for example `phases-drawn` fails=6 in the body and 7 here, and `phases-keep-groups-page` 1 in the body and 3 here. Every verdict matches: killed, and M0 null.
- Note: figure-unverified: the class-repair RESULT lines in the body carry no `rc=`/`fails=` fields. I re-derived all five by name with the PR's driver (ev/mutants.txt).

## Evidence

- Prior block resolved. The four reproduction cases from the prior verdict each now earn a violation, and the section draws PHASES UNAVAILABLE without crashing: `entry=5` gives "entry not text (5)", `items[1].name=7` gives "no name (text)", `forecast.basis=3` gives "a forecast with no basis", and `note=1` gives "note not text (1)". Null control: the unmodified fixture gives violations=0 and draws (ev/attack.txt).
- Class closed under the body's enumeration rule. `_census` replaces every node of a fully populated file with each `_JUNK` value. Section keys read in `plan_phases.py` (`as_of basis detail entry exit finished forecast items name note phase phases round start_from start_to started status waiting_on`) are all in the census file; `title` and `plan` come from the module's own `PHASES` table, not the file. `plan_page.render` reaches the file only through `plan_phases.section` (`plan_page.py:710`). My own fuzz, beyond the census, replaced 2 or 3 nodes at once with 18 junk values, including None, NaN, 10**30, nested dicts and lists, and an invalid date: `RESULT fuzz=multi-node runs=18285 crashes=0` (ev/attack.txt).
- Mutation proof, re-run at this head with the PR's driver, M0 plus every `phases-*` mutant: `RESULT mutant=M0 rc=0 fails=0 verdict=null`, then the five new or re-anchored mutants: `phases-unknown-status rc=1 fails=3 killed`, `phases-status-unhashable rc=1 fails=1 killed`, `phases-text-typed rc=1 fails=1 killed`, `phases-items-list rc=1 fails=1 killed`, `phases-item-name-text rc=1 fails=1 killed`. All 27 mutants are killed, `RESULT survived=0` (ev/mutants.txt).
- Self-tests at this head: `plan_page self-test: 136 checks, 0 failed`. `plan_phases.py --check dev/programme/round11/phases.json` gives rc 0 (ev/selftests.txt).
- Merge with main: `git merge-tree --write-tree origin/main 7b687a4819e54718f84e4353ce92f665414cb70e` gives rc 0, with `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt).
- The body's `## Head` names 7b687a4819e54718f84e4353ce92f665414cb70e, and `refs/pull/3622/head` reads that SHA.
- Role contracts: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- The delta touches no VERSION, manifest, RELEASE_NOTES, golden, claim or budget file.
- Finder's harness: none named. This is an owner-directive feature, as in round 1.
- Red checks: no red at this head in `owed-reds`' set at render. The body's answers for `governance / instrument-self-tests` and `tests / fast (3.14)` at earlier heads stand.
- Carry destination: `R11-PRE-PLAN-RENDER` is `not-started` and `carry_receivable` on origin/main's `wave-r10-groups.json`. On `origin/handoff/audit-r10-roster` it is `absorbed`, and its work and carries continue in the same-named entry of `wave-r11-groups.json`, which is on no ref this clone can read. The body says Carry 6's remaining items stay on this group for its next part, so the finding routes there. `carry_audit.py check` gives rc 0 (`0 finding item(s)`).
- Semantic cases, measured: ev/semantic.txt. Census and fuzz: ev/attack.txt.
- CI: `merge_train.py classify 7b687a4819e54718f84e4353ce92f665414cb70e --pr 3622` read `WAIT 7b687a4819e54718f84e4353ce92f665414cb70e pending: gate red: none` on every run from 23:14 to 23:41 UTC (ev/classify.txt), so this verdict carries `pending-ci: gate`. The head is unchanged at the end of the review (`refs/pull/3622/head` = 7b687a4819e54718f84e4353ce92f665414cb70e).
