Policy change on two owner rulings (tvofi, 2026-11-08, chat to the orchestrator): the bar for a new process, tooling or instrument proposal and for the owner's exemption moves from over 10% to over 20% improvement (CI time, programme completion time, right-first-time, token usage); an already planned instrument or machinery group, or an existing non-production CI lane or seat, stays only on a measured improvement of at least 10% (was 5%, in no policy file; its only statement was `dev/programme/triage/s6-batch126.md`, a record left as written); a minor or low defect repair in instrument or machinery code takes the same bars. Approval: mandate 6715477401 (scope all) covers the owner's approving review.

Sites changed: `dev/governance/roles/proposal-triage.md` (exemption sentence, keep test, minor-defect rule), `dev/governance/rules/ratchet-budgets.md` plus its generated `.claude/rules/` and `.cursor/rules/` copies (`node tools/policy/rules_sync.mjs`), `tools/audit/machinery_ratchet.py` (docstring, `THRESHOLD`, self-test cases at exactly 20%), `tools/audit/seat/instruments/machinery_ratchet.py.md`. Left alone: unrelated percentages (docs solver/furnace figures, round 9 perf-gate noise, D0 price figures, rate-limit floors) and the older `dev/programme/triage/s6-batch*.md` records that recount the 10% bar as applied then.

## Repair of the blocked review (comment 6719859854)

Block 1, the severity scale. The minor-defect rule now names every value the roster's `severity` field carries, once. **For the owner to confirm:** `low` and `normal` take the bar (over 20% to add, at least 10% to keep); `medium`, `high`, `major` and `critical` skip it and keep their route, as do a required countermeasure, closeout and an owner directive; an unset `severity` is classified first. This is the minimal reading of the ruling's "minor or low" (bar) against "major or critical" (skip); `medium` and `high` are read as not minor. If the owner means `medium` to be minor, it is a one-word move between the two lists.

Block 2, the obligations the word-budget cut removed. Each is restored in `proposal-triage.md` at this head:

- an ACCEPT runs its rule on each instance, result beside it: "An ACCEPT runs its rule per instance, result beside it."
- git and local logs before the API: "Git and local logs before the API."
- the `Cost:` field's estimate: "`Cost:` (the estimate, each capped file's `--budgets` row)"
- the cost units: "critical-path wall-clock/seat time; tokens (model x effort x expected runs); API calls; standing CPU (Pi-class, CI runners); complexity (lines, new files, checks, hot files, review rounds); maintenance"
- `Instances:` "or log" and cite-don't-carry: "(each figure beside its command or log: cite, don't carry)"
- an exemption ACCEPT's PR records it: "says so; its PR records it."
- the Proposals-line source: "Sources: the orchestrator's sweep and Proposals line, seat results, verdict optimisation notes."
- medium effort, rulings checked against code: "One opus seat, medium effort; check rulings against code."
- the definition of proposal-sourced text: "it refuses text naming `triage P<n>` or `proposal P<n>` citing no ACCEPT ruling."
- also restored, though the review did not list it: ACCEPT's "new group, brief" destination. Not restored: DEFER's "or the owning group", which the previous head also lacked and the review did not list. DEFER still names "what would change it". Raised here for the reviewer.

Paid without a raise, by tightening the same file's prose: the provenance "tvofi 2026-10-22;" (kept as "decision 0015"), the exemption's four measures (cited to `ratchet-budgets.md` instead of repeated), the merged keep-test and minor-defect paragraphs, and shorter wording elsewhere. No `*budgets*.json` file is in the diff.

## Head

eda3592e3317f21d59398f67dd43ab085dd79996 (a fast-forward of c7f4535d and of the PR head acd78b4d). origin/main at 6188936a8bdc58b510ecb8794ad86350283c49a7, 2026-11-08T10:08:56Z: `git merge-tree --write-tree origin/main HEAD` exited 0 (no conflict), so main was not merged, per the owner ruling of 2026-11-07.

## Mutation proof

Mutant: `THRESHOLD = Fraction(1, 5)` set back to `Fraction(1, 10)` in `tools/audit/machinery_ratchet.py`; `python3 tools/audit/machinery_ratchet.py --self-test` printed `FAIL exemption: exactly 20% refuses: got 0, want 1` and `FAIL exemption: exactly 20% as floats refuses: got 0, want 1`, `54 checks, 2 failed`. Restored (`git checkout`): `54 checks, 0 failed`. Re-run at this head.

## Null control

For the self-test: at the base the self-test passes with exactly 10% refusing; at the head 21% passes (`ex-11`) and exactly 20% refuses, so the cases tell the two thresholds apart. For the severity mapping: a script that reads the `severity` values from `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster` (9fd3d6a2) and looks for each one as a code span in `proposal-triage.md` finds none missing at this head and finds `critical, high, low, major, medium, normal` all missing at acd78b4d. So the check reads the defect at the old head and its absence at this one.

## Figures

- Roster scale, `python3 -I` over `wave-r10-groups.json` at `handoff/audit-r10-roster` 9fd3d6a2 (the review read 9263aea2; the counts are unchanged): 388 groups; high 90, low 56, medium 202, critical 8, normal 7, major 1, unset 24; R10-FLY-TRIAGE-BAR is `medium`.
- `python3 tools/audit/machinery_ratchet.py --self-test`: `54 checks, 0 failed`.
- `node tools/policy/policy_lint.mjs --budgets`: `proposal-triage.md` 35 lines / 489 ~tokens against caps 36 / 489. The column is bytes/4 (`cmdBudgets` / `sizes()` in `policy_lint.mjs`), not words. The previous body called it "words": 487 at the previous head, 489 at the base.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `MUTANT_CMD="python3 tools/audit/machinery_ratchet.py --self-test" PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh`: `PRE-PR: eda3592e3317f21d59398f67dd43ab085dd79996 ... rc=0`, wall 1164 s for the whole run including the diff-mutant step; diff mutants: 7 survivors (answered below).

## Unpinned sites

All seven survivors sit on added lines inside `machinery_ratchet.py`'s own `self_test()`, the instrument's test assertions, not its production logic:

- `:614`, `:615`, `:616`, `:633` CALL_DEL (the `ok(...)` call deleted): deleting a self-test assertion cannot fail the same self-test. Disposition: value check. The THRESHOLD mutant above turns `:614` and `:615` red, so they bite; `:616` (21% passes) and `:633` (`improvement()` exact) are the positive and exact-value controls. The review's extra 1/4 mutant turned `:616` red.
- `:614`, `:615` CONST_SWAP (`entry(9 ...)` to `entry(10 ...)`): both cases expect a refusal, and an entry naming another PR is also refused, so the swap is equivalent for the refusing cases. Disposition: equivalent mutant.
- `:633` CONST_SWAP (the pr number in `improvement(entry(...))`): `improvement()` does not read `pr`. Disposition: equivalent mutant.

## Red checks

None concluded red at acd78b4d (the review's `merge_train.py classify`: `GREEN ... red: none`). Locally the closures step was skipped (`PREPR_SKIP_CLOSURES=1`, as the brief directs) and is left to CI's closures-autofix. Every other prepr step was ok or skip, and diff mutants WARN is report-only.

## Forward-carry

none

## Friction

none

## Approval

Owner rulings quoted in the opening paragraph (tvofi, 2026-11-08, two chat messages to the orchestrator); the owner's approving review at the head is covered by mandate 6715477401, scope all. The severity mapping in "Repair of the blocked review" is stated for the owner to confirm.
