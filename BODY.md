The nightly's full-scope mutation lanes drive `tests/harness_headers.py` and
`tests/stress.py` as baseline drivers. Both measure the MACHINE, so running them
exclusively was not enough to keep their own limits off the lane's null control.
Each refused a `mutation-ledger` night on the comment-only edit every driver in
play must let survive: `harness_headers.py` SIGXCPU'd at `rc=-24` (run
`37108891698`, 10-03) and `stress.py`'s own cost budget killing it at `8.0x`
against its own `7.9x` (run `37189092011`, 10-04). That is the two-of-six-nights
arm of the nightly red, `#1930 (a)`.

`--scope full` now drops both out of its net, so they drive no mutant, pay no
baseline, and cannot refuse the lane. `--scope changed` still drives both: that
scope is where a site the diff added earns its pin and where the unpinned count
is repaid, so the pull-request gate is untouched. The form is #1930 (a)'s own
("Remove stress and harness_headers from the nightly/ledger driver set"), which
is stronger than deferring them to run alone: exclusivity was already their
behaviour and did not close the arm, because 10-04's refusal was `stress.py`'s
budget judging its own null control, which no scheduling fixes.

Owner approval is recorded and is not re-asked: tvofi, 2026-10-09, comment
`6078664059` on issue #201 — verbatim **"approve the count-raise"** — answering
the ask in comment `6078320192`, scoped to exactly this deferral.

**Where the raise landed, and why no cap moved.** The count it names is not a
stored number in this tree: #1577 made it derived, `tools/merge/ledger_merge.py`
holds `RETIRED = {"unpinned_sites"}` and drops a side that deleted it, and
`tests/mutation_table.py`'s `ledger_form_problems` refuses a committed one
("the ratchet reads the count at its base"). `ratchet_refusal` compares this
tree's count with the base's, so a branch that DELETED the pair's `killed_by`
rows would be refused at its own gate and the nightly would refuse again on the
merge commit, whose `HEAD^1` still carries them. The rows therefore stay — each
is a true claim that a driver kills a site, and the changed scope still runs that
driver — and the drop's cost is stated rather than swallowed: the census names
the deferred drivers and how many dispositions name one, and each is printed as a
`SKIP` of the scope that no longer drives it. **No cap was padded**;
`max_survivor_fraction` and `last_measured` are unchanged, and the only edit to
`tests/mutation_budgets.json` is one appended prose clause in `reason`, the leaf
the raise gate's schema marks free.

## Head

`14b891508`

## Mutation proof

Two mutants of the fix's own lines, plus the unmutated control, at `8be0fa30e`
(the code head; `4f6f2f3ee` and `14b891508` add prose and a ledger row only).
Elided where the check name is long; the runs are in
`/Users/timmalmstrom/hpo-seats/nightly-defer/logs/`.

- **Unmutated:** the four arms hold, and the net walk prints `75 production
  file(s); drivers unioned over the tree 26 -> 24; files losing a driver OUTSIDE
  EXCLUSIVE=[]; files losing one at all=75`.
- **M1, the drop loop deleted from `main()`:** RED
  `the full scope drops the EXCLUSIVE pair out of its net, ... main() takes the
  drop from that rule`. The other three arms stay green, so the arms are
  separable rather than one blob.
- **M2, `SCOPE_DEFERRED` emptied (`= {}`):** all four RED
  (`the full scope drops ...`; `a healthy full-scope run still drives every
  other driver ...`; `the census names every disposition ...`; `and the clause
  names each deferred driver ...`), and the net walk now prints `26 -> 26` and
  `files losing one at all=0` — the vacuity arm fires, which is what stops a
  no-op drop from passing the subset clauses.

**How the arms were driven, stated plainly.** The GREEN arm is the closure run:
`python3 tests/entities.py` reported `ALL 2254 ENTITY CHECKS PASSED` at
`e797e30bc`, whose `tests/` code is this head's. The RED arms were taken by
driving the same four `R.check` expressions directly
(`python3 -I .../logs/arms.py`), because the full closure run was starved on this
shared box — it had made no progress for 13 minutes at load average 66, and two
earlier attempts were killed at `rc=143`. Each mutant was restored with
`git checkout -- tests/mutation_table.py` (0 diff lines after both).

## Null control

`tests/entities.py` walks every production file rather than one instance: for
every file, the net `--scope full` drives after the drop is the net it drove
before, minus the pair — no file loses a driver outside `EXCLUSIVE`, every file's
net stays a subset of its old one, and the union over the tree loses exactly the
pair. The arm that fires is the non-zero count of files that lost one at all
(`75`), so a drop that removed nothing is refused rather than passed.

The census line is the second null control: the unpinned count and the ratchet
base are the same number, as a diff touching no production line and no
ratchet-read ledger row must leave them.

Nothing else is deferred: `scope_deferred("changed") == ()`, pinned by the same
check, so the pull-request scope loses no driver and the pinning path that repays
the count is intact.

The instrument arm: at `--scope full`, naming the pair explicitly in `--scripts`
still drops both (`SKIP` lines below) while every other named driver still runs —
`drivers in play: tests/typing_ruler.py`, `baseline tests/typing_ruler.py: rc=0
failed=0`.

## Figures

- **The unpinned census and the drop, at `14b891508`** (this is the instrument
  line the brief names): `python3 tests/mutation_table.py --scope full --anchor
  "custom_components/heatpump_optimizer/boost.py:space_learning_frozen BOOLOP
  ad026ebf" --scripts
  tests/typing_ruler.py,tests/harness_headers.py,tests/stress.py`
  — `4617 unpinned site(s) of 5983 candidate sites, 4617 at the ratchet base
  HEAD^1; the ledger agrees with the deterministic inventory; this scope drives
  neither tests/harness_headers.py, tests/stress.py -- each measures the machine,
  so its own limits judged a comment-only null control on a shared runner and
  refused the lane: harness_headers.py SIGXCPU rc=-24 (run 37108891698),
  stress.py 8.0x against its own 7.9x budget (run 37189092011) -- and 4 recorded
  killed_by disposition(s) name one, so those pins stay in the ledger and this
  lane re-verifies none of them`
  — then `SKIP tests/harness_headers.py (...)`, `SKIP tests/stress.py (...)`,
  `1 mutant(s) over 1 file(s); drivers in play: tests/typing_ruler.py`.
- **The two drivers' cost at this lane's head**, each run alone, macOS arm64
  under Python 3.14.7 (2026-10-09T20:51Z–21:04Z):
  `python3 tests/harness_headers.py` -> `rc=0`, `349.2 s`;
  `python3 tests/gate_lock.py auto-lease --label nightly-defer-cost --
  python3 tests/stress.py` -> `rc=1`, `408.1 s`, whose red is the environment
  (`origin/main IS this commit`, 7 of 103 checks) rather than the code. Both are
  the pair's BASELINE cost, which the lane paid whether or not it drove them: the
  drop saves it, so the "+641 s per lane" the ask priced is a saving at this head,
  not a cost. Committed solo recordings at the same head, for CI's own ruler:
  `tests/harness_headers.py` 220.7 s, `tests/stress.py` 760.6 s.
- **The payment taken first.** `--anchor <anchor> --scripts <every remaining
  driver green unmutated>` over all five pinned sites, through the tree's own
  kill rule: `tests/manual_plan.py` kills the `boost.py` site, and that row now
  names it; the other four sites LIVES against every remaining driver. Log:
  `/Users/timmalmstrom/hpo-seats/nightly-defer/logs/replay_tier1.txt`.
- `python3 tests/entities.py` -> `ALL 2254 ENTITY CHECKS PASSED` (was 2243 before
  this diff; the four arms are new).
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`, no metric moved.
- `git diff --quiet <merge base> -- tests/mutation_budgets.json` -> the file
  differs by one appended `reason` clause and nothing else;
  `max_survivor_fraction` is `{"changed": 0.2, "full": 0.3}` at both ends.

## Red checks

- `closures` — `REFUSE failed while being recorded: tests/harness_headers.py
  (exit 1)`. **Environmental, and re-taken green at this head.** The step's own
  command re-run unchanged (`python3 tests/closure.py --exec-record
  tests/harness_headers.py <tmp>/rec.json`) reports
  `ALL 109 HARNESS HEADER CHECKS PASSED`, `rc=0`, 4 m 38 s
  (2026-10-10T11:51:21Z → 11:55:59Z). prepr's instance of the same recording ran
  on a shared box at load average 122 and its child sat at 0% CPU for the last 13
  minutes before exiting 1. Answer per `defect-root-cause.md`: there is no
  cheaper detector — the cheapest detector of a truncated recording IS the
  recording — and its standing cost is the script's own ~5 minutes, already paid
  by `fast` on every head. Nothing is weakened and no check is skipped; CI's
  `closures-autofix` re-records the same script on the pull request.
- `pr-body` — `PR-BODY: 2 error(s)`: `## Red checks` was empty and a `## Friction`
  bullet was wrapped, which the section's parser reads as unparseable. Both are
  answered by this edit.

## Forward-carry

`dev/audit/rca/R9-NIGHTLY-MUTATION-BOUND.md` §4(iv) routed this arm to the owner,
and this pull request answers it there: the section is kept as written and a
landed note corrects the two quantities a later seat would otherwise inherit (the
sign of the cost, and the belief that an unpinned count is storable). The four
pins no driver left in the net re-verifies are named there, so the next seat
reads owed work rather than an open decision.

The stale claim this fix repairs is the `EXCLUSIVE` comment in
`tests/mutation_table.py`, which said the full scope still drove the pair,
counted three rows naming them, and predicted an unpinned-count raise.

## Friction

- R9-RC-NIGHTLY-DEFER: stale: the brief and the approval ask for `tests/mutation_budgets.json` to reach a measured unpinned count, and the tree has stored none since #1577 (`tools/merge/ledger_merge.py` RETIRED; `ledger_form_problems` refuses a committed one), so the raise has no numeric object and the round spent establishing that is the friction.
