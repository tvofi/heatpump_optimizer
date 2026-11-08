Policy change on two owner rulings (tvofi, 2026-11-08, chat to the orchestrator): the bar for a new process, tooling or instrument proposal and for the owner's exemption moves from over 10% to over 20% improvement (CI time, programme completion time, right-first-time, token usage); an already planned instrument or machinery group, or an existing non-production CI lane or seat, stays only on a measured improvement of at least 10% (was 5%, in no policy file; its only statement was `dev/programme/triage/s6-batch126.md`, a record left as written); a minor or low defect repair in instrument or machinery code takes the same bars. Owner correction of 2026-11-08: the issue bar applies only to instrument and machinery code. Approval: mandate 6715477401 (scope all) covers the owner's approving review.

Sites changed: `dev/governance/roles/proposal-triage.md` (exemption sentence, keep test, minor-defect rule), `dev/governance/rules/ratchet-budgets.md` plus its generated `.claude/rules/` and `.cursor/rules/` copies (`node tools/policy/rules_sync.mjs`), `tools/audit/machinery_ratchet.py` (docstring, `THRESHOLD`, self-test cases at exactly 20%), `tools/audit/seat/instruments/machinery_ratchet.py.md`. Left alone: unrelated percentages (docs solver/furnace figures, round 9 perf-gate noise, D0 price figures, rate-limit floors) and the older `dev/programme/triage/s6-batch*.md` records that recount the 10% bar as applied then.

## Repair of the blocked review (comment 6721196982)

Block, the rule conflict. The skip list at 2684306f named "a required countermeasure", and the opening defines a countermeasure policy requires as "(root cause, red-check carry, finding fix)", so a `low` or `normal` machinery repair that fixes a finding both met the bar and skipped it. At this head:

- the skip list reads "`medium`, `high`, `major`, `critical`, root-cause countermeasure, closeout, owner directive skip them": only a root-cause countermeasure skips, as the group brief keeps it;
- the opening reads "(root cause, red-check carry, finding fix; see below) keeps its route", pointing the finding-fix route at the Machinery paragraph, which is the one exception.

So a `low` or `normal` repair of instrument, machinery, CI-lane or seat code (outside `custom_components/`) meets both bars whether or not it fixes a finding; a product defect never takes the bar. The `low`/`normal` take, `medium`/`high`/`major`/`critical` skip mapping is unchanged from the orchestrator-approved one.

Findings, each restored:

- DEFER's "or the owning group" (base wording): "DEFER, what would change it or the owning group".
- "never assumed major" (group brief): "unset is classified first, never assumed major."
- "An even or marginal trade is REJECT" (base): "Even or marginal: REJECT".

Paid within the 489 ~token cap (bytes/4) without a raise, by prose trims that change no seat duty, each listed: "this cost/benefit gate before it is built" to "this gate before building" (the **Bar** paragraph defines the gate as cost against benefit); "the orchestrator's sweep" to "orchestrator sweep"; "outweighs its costs" to "outweighs cost"; "An ACCEPT on the exemption" to "An exemption ACCEPT"; "or an existing" to "or existing"; "A repair" to "Repair"; "a required countermeasure" to "root-cause countermeasure" (the repair itself); "closeout and an owner directive" to "closeout, owner directive"; "`Cost:` (the estimate," to "`Cost:` (estimate,"; "**A ruling** is a" to "**A ruling**: a"; "routes an ACCEPT" to "routes ACCEPTs"; "citing no ACCEPT ruling" to "citing no ACCEPT" (an ACCEPT is a ruling here). The paragraphs were re-wrapped at 79 columns. The nine obligations the round-2 review listed are all still present: per-instance rule run, git before the API, the `Cost:` estimate, "or log" and cite-don't-carry, the exemption PR records it, the cost units, the Proposals line, medium effort and rulings checked against code, and the proposal-sourced text definition. No `*budgets*.json` file is in the diff.

## Head

`42c0ebbb531244c8815968779d519f9680d0fef7`: the repair commit 54651332 (on 2684306f) merged with origin/main 8a4cf2618c53a6dca6b65df3eae5efc8832d1796, which had moved 117 commits since the last prepr run (merge at 2026-11-08T14:12:58Z, clean, no conflict). Every figure below is taken at this head. origin/main was re-read at 2026-11-08T14:42:53Z, still 8a4cf261, so it has not moved since this head's `tools/pr/prepr.sh` run and no second run was owed.

## Mutation proof

Mutant: `THRESHOLD = Fraction(1, 5)` set back to `Fraction(1, 10)` in `tools/audit/machinery_ratchet.py`; `python3 tools/audit/machinery_ratchet.py --self-test` printed `FAIL exemption: exactly 20% refuses: got 0, want 1` and `FAIL exemption: exactly 20% as floats refuses: got 0, want 1`, `54 checks, 2 failed`. Restored (`git checkout`): `54 checks, 0 failed`. Re-run at this head.

## Null control

For the rule conflict: `git show <ref>:dev/governance/roles/proposal-triage.md | tr '\n' ' ' | grep -oE "required countermeasure|root-cause countermeasure|finding fix[^)]*\)|never assumed major|Even or marginal|what would change it or the owning group"` prints, at 2684306f, `finding fix)` and `required countermeasure` only; at this head, `finding fix; see below)`, `Even or marginal`, `root-cause countermeasure`, `never assumed major` and `what would change it or the owning group`, and no `required countermeasure`. So the same command reads the conflict and the three omissions at the reviewed head and their repair at this one.

For the self-test: at the base the self-test passes with exactly 10% refusing; at the head 21% passes (`ex-11`) and exactly 20% refuses, so the cases tell the two thresholds apart. For the severity mapping: every `severity` value on the roster (below) is named once as a code span in `proposal-triage.md`; the round-3 review confirmed it at 1726b3bc.

## Figures

- Roster scale, `python3 -I` over `wave-r10-groups.json` at `handoff/audit-r10-roster` 9fd3d6a2 (the round-3 review re-read 1726b3bc, same counts): 388 groups; high 90, low 56, medium 202, critical 8, normal 7, major 1, unset 24; R10-FLY-TRIAGE-BAR is `medium`.
- `python3 tools/audit/machinery_ratchet.py --self-test`: `54 checks, 0 failed`.
- `node tools/policy/policy_lint.mjs --budgets`: `proposal-triage.md` 36 lines / 489 ~tokens against caps 36 / 489 (1956 bytes; the column is bytes/4).
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`; `scope.run` names `tests/entities.py`: `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `4 of 2666 ENTITY CHECKS FAILED` at this head and the same `4 of 2666 ENTITY CHECKS FAILED` at origin/main 8a4cf261 with this diff absent; the four names (the coverage-job cache reuse, the release ZIP build, the two Pages-workflow checks) match line for line between the two logs (`diff` of the `FAIL` lines: identical). They come from this container, which cannot run those workflow steps, not from this diff, which touches no file those checks read. CI's `fast` lane is the authority.
- `MUTANT_CMD="python3 tools/audit/machinery_ratchet.py --self-test" PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh`: `PRE-PR: 42c0ebbb531244c8815968779d519f9680d0fef7 ... rc=0`, run on the committed merge head; closures skipped, diff mutants WARN (7 survivors, the same seven answered under Unpinned sites), every other step ok or skip.

## Unpinned sites

All seven survivors sit on added lines inside `machinery_ratchet.py`'s own `self_test()`, the instrument's test assertions, not its production logic; this repair adds no code site:

- `:614`, `:615`, `:616`, `:633` CALL_DEL (the `ok(...)` call deleted): deleting a self-test assertion cannot fail the same self-test. Disposition: value check. The THRESHOLD mutant above turns `:614` and `:615` red, so they bite; `:616` (21% passes) and `:633` (`improvement()` exact) are the positive and exact-value controls. The review's extra mutants (1/4, 21/100) turned `:616` red.
- `:614`, `:615` CONST_SWAP (`entry(9 ...)` to `entry(10 ...)`): both cases expect a refusal, and an entry naming another PR is also refused, so the swap is equivalent for the refusing cases. Disposition: equivalent mutant.
- `:633` CONST_SWAP (the pr number in `improvement(entry(...))`): `improvement()` does not read `pr`. Disposition: equivalent mutant.

## Red checks

`gate` at 2684306f (the round-3 review's `merge_train.py classify`: `RED ... red: gate`): not a code result. Gate job 128721651467 ended `RATE-LIMITED reset_epoch=1794138942 ... exit code 3` on the shared GitHub API rate limit, and the test jobs it reads were cancelled with no result. Cause: the shared API rate limit, not this diff; no cheaper detector could have run it, so no root-cause countermeasure is owed. This push re-runs it. Locally the closures step was skipped (`PREPR_SKIP_CLOSURES=1`) and is left to CI's closures-autofix.

## Forward-carry

none

## Friction

none

## Approval

Owner rulings quoted in the opening paragraph (tvofi, 2026-11-08, two chat messages to the orchestrator) and the owner's correction of 2026-11-08; the owner's approving review at the head is covered by mandate 6715477401, scope all, under which the orchestrator approves this policy merge.
