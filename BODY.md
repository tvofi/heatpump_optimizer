`tests/card.mjs`'s link census (R10-DEEPLINK, #2283) is the guard that every
route out of the card goes through `haLink` and `navigateTo`. One declared
surface (`NAV_SURFACE`) is read by two arms: a static arm that refuses a
mention of any surface member in the card's code outside `navigateTo`, so it
covers code no press reaches; and a dynamic arm that presses every element the
shadow root wires to a click, records each instrumented surface member by
name, and reads `href`/`action`/`formaction` off the markup after every press.
A reach check compares the census's `ACTS` with every `act` branch the source
dispatches, in both directions, and requires each one pressed.

This head closes what the last review (verdict on `e59b1fb54`) blocked on.

- **A written programmatic form passed both arms.** `createElement("form")` +
  `setAttribute("action", ...)` + `.submit()` in the chart's undriven keydown
  handler read `rc=0 fails=0`. Four surface rows now name that form:
  `createElement("form")`; `setAttribute` / `setAttributeNS` /
  `createAttribute` at the `"action"` name position; `Reflect.set` /
  `Object.assign` / the computed-key assignment `["action"] =`; and `.submit`,
  `.requestSubmit`, `["submit"]` and `.submit.call(`. Each row is anchored to
  the call or member access, not the word: `form` is the card's own loop
  variable (`for (const form of forms)`) and `action` is the action entity's
  name in a dozen places, so a bare token would refuse the card.
- **The head was red on its own census.** The origin/main merge brought
  R10-UX-SETUP's setup-fold boolean `b.open`, which the `open` token matched.
  It is renamed `b.foldOpen`, not allowanced: an allowance keyed on `b.open`
  blinds the property-access spelling at that site and makes the next fold
  boolean on any other object a new exception (fixer.md step 14). The card is
  a hot file and outside this group's `files`; the rename is the only card
  change and is disclosed here for the orchestrator.
- **Ported from this group's first design.** The 2026-10-16 snapshot
  (`a3b1c00e2`, `d04c0c7e7`, never an ancestor of this branch) carried two
  pieces that still apply: the plants `T1c`/`T2c` (a press that throws or
  rejects only inside the census, which the card can detect by the census's
  one-parameter `open`), and the stub-selector residual.
- **The residual is now stated truthfully.** The census's Residual paragraph
  said a run-time-built name is caught on every row a press drives. It is not
  when the write goes through a selector the stub DOM (`tests/dom_stub.mjs`)
  cannot resolve, a tag.class pair such as `a.zz`: the press reaches the
  handler but the write runs on no element. The driver's `Y1` is that
  witness and reads green; `R7c`, the same write on a selector the stub
  resolves, reads red. Closing it needs the stub's selector engine, which is
  outside this group's files; the paragraph says so and the orchestrator has
  it as a report.

Closes #2317.

## Head

`c6ef1959a6927f40d1d9e0058ade122c838960a6` is the code head. Every figure below was measured at it unless the
figure names `778ae2565`, its parent. It is the round-7
head `e59b1fb54` plus the round-8 commits (`2c766810b` the rename, `b0422e2b3`
the four rows and their plants, `f1542b17d` the carry), a merge of origin/main
`6e5753a4aca8b240559e8e11e8a68c7de988cd73` (`176db5f00`, one roster conflict
resolved as main's R10-SCORES brief plus this group's carry), and `778ae2565`
(the ported plants and the residual paragraph; comment and driver only), and
`c6ef1959a` (the `F2` control repaired; driver only). The
merge base with origin/main is `6e5753a4aca8`. The card, `tests/card.mjs` and
the driver are byte-identical between `f1542b17d` and `176db5f00`:
`git diff --stat f1542b17d 176db5f00 -- custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js tests/card.mjs tools/audit/seat/r10_deeplink_mutants.py`
prints nothing.

## Mutation proof

Every plant is one mutation applied by
`tools/audit/seat/r10_deeplink_mutants.py`, which restores the file byte for
byte and refuses to start on a dirty tree. `V*` are the round-7 programmatic
form in the chart's keydown handler (`V1` is the review's plant verbatim);
`X*` delete one of this fix's own lines; `F*` are green controls; `T1c`/`T2c`
are the ported plants; `Y1` is the residual's witness.

The full sweep at this head, all 109 plants, run in four detached worktrees at
the head with their own `plan_view.py` payload (`python3
tools/audit/seat/r10_deeplink_mutants.py <plant ...>`, the plant list split
four ways):

Measured at `778ae2565` (the driver's parent of this head; `c6ef1959a`
changes only `F2`'s plant text). 109 plants: 76 `rc=1` each with at least one
FAIL line, 33 `rc=0 fails=0`, and 0 crashes (`rc!=0` with no FAIL line). The
33 green are exactly the plants written to be green:

- every `X*` deletion run alone with no plant (`X3`-`X13`, `X10`-`X13`),
  which moves no check because the card then holds nothing for the deleted
  line to refuse;
- every `X*` pair (`X4K3t`, `X5W1`, `X6Z`, `X6Z2`, `X8W3`, `X9Z3`, `X10V2`,
  `X10V13`, `X11V3`, `X11V9`, `X11V12`, `X12V7`, `X12V8`, `X12V11`, `X13V4`,
  `X13V5`, `X13V6`, `X13V10`): with that one line deleted the plant beside it
  passes, so the line is what closes it;
- the controls `F1`, `F3`, `F4`, and the residual witness `Y1`.

The 76 red include every class plant: `V1`-`V13` (each `rc=1 fails=1` on `no
navigation token in the card's code outside navigateTo`), the issue's own
`K1`/`K1b`/`K1c`, `K2`/`K2b`, `K3t`, `K5`/`K5b`/`K5c`/`K5r`, the round-5
`Z`/`Z2`-`Z2d`/`Z3`/`Z3b`/`Z3d` and control `Z3c`, `T1c`/`T2c`, and `X1`,
`X2`, `X1K5b`, `X3K2b`, `X7K1b`.

**One control was wrong, and is fixed here.** `F2` read `rc=1 fails=1` at
`778ae2565`, on `the act set the census declares is the one the card's source
dispatches` (source-only `action`): it was written `act === "action"`, the
act-branch syntax the reach check reads, so it declared an act branch and was
red on reach rather than on the action-through-member row it controls. The
prior body's "F1-F4 each rc=0" was not true of `F2`. At this head `F2`
compares the handler's own `key` and, with the row it controls and that row's
plant, `python3 tools/audit/seat/r10_deeplink_mutants.py
F2_action_as_an_object_assign_value_control
X12V8_action_member_row_is_what_closes_V8
V8_object_assign_action_in_undriven_keydown` prints `F2` `rc=0 fails=0`,
`X12V8` `rc=0 fails=0` and `V8` `rc=1 fails=1`.

**The ported plants and the residual**, `python3
tools/audit/seat/r10_deeplink_mutants.py T1c_census_only_throw_on_press
T2c_census_only_async_reject_on_press
Y1_runtime_name_on_unresolved_selector_residual
R7c_setAttribute_runtime_name`: `T1c` and `T2c` each `rc=1 fails=2` (`no
navigation token in the card's code outside navigateTo`, `no press throws`);
`Y1` `rc=0 fails=0`; `R7c` `rc=1 fails=1` (`every link the census records from
a press is one haLink builds for this entry`). These four are from the sweep
at `778ae2565` above.

## Null control

`python3 tools/audit/seat/r10_deeplink_mutants.py --null` prints
`RESULT mutant=NULL_no_plant rc=0 fails=0` at this head. `node tests/card.mjs` prints `ALL CARD CHECKS
PASSED` with 1257 `ok` and 0 `FAIL` lines (`grep -c '^  ok  '`,
`grep -c '^  FAIL'`). The false-positive control for the four form rows is the
card's own source: the census is green at this head with
`for (const form of forms)`, `sensor: "action"` and `w.action !== "off"` in
the code the static arm scans, and `F1`-`F4` in the sweep are each the same
words placed as values, an object key and an identifier prefix.

## Figures

The card-reading scripts ran at `778ae2565`, whose card, census and
`tests/` are this head's (`c6ef1959a` touches only the driver), after `PYTHONPATH=tests/hastub python3
tests/plan_view.py`, except where another tree is named.

- `node tests/card.mjs`: `ALL CARD CHECKS PASSED`, 1257 `ok`, 0 `FAIL`.
- `node tests/card_drift.mjs 6e5753a4aca8b240559e8e11e8a68c7de988cd73`:
  `card_drift: identical in all 40 states`.
- `python3 tests/closure.py select --diff 6e5753a4aca8 --workdir <dir>`:
  `MODE: SCOPED -- 9 script(s) run, 24 scoped out` over 5 changed files (the
  card, `tests/card.mjs`, the driver, `dev/programme/rosters/wave-r10-groups.json`
  and `dev/programme/delivery/2345.md`). Every script it names was run here:
- `PYTHONPATH=tests/hastub python3 tests/arch_score_head.py`: `ALL 16
  ARCHITECTURE SCORE HEAD CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/deployment_shape.py`: `ALL
  DEPLOYMENT SHAPE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 169 checks PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2346 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4155 FEATURE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 109 HARNESS
  HEADER CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/plan_view.py`: `plan reason codes,
  price provenance and slot energy OK`.
- `python3 tests/structure.py` at this head: `STRUCTURE RATCHET PASSED`, with
  `max_method_loc 373 <= 373` and `seam_cut_total 752 <= 752`.
- `python3 tools/audit/archscore/score.py --diff 6e5753a4aca8`:
  `Architecture score: dS +0.0000 NULL` at this head.
- `python3 tools/pr/ci_predict.py --base 6e5753a4aca8` at this head: `CI
  PREDICT: no closures or fast red predicted against 6e5753a4aca8`.
- Claim files, `VERSION`, the manifest version and the `RELEASE_NOTES.md`
  heading are untouched: `git diff --stat 6e5753a4aca8...HEAD --
  tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION
  custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` prints
  nothing.

## Red checks

At the previous head `e59b1fb54`:

- `fast (3.14)`: `node tests/card.mjs` failed `no navigation token in the
  card's code outside navigateTo` on the `b.open` lines the origin/main merge
  brought in (job 117464541848). Closed here by the rename; `node
  tests/card.mjs` is green at this head (above). The cheaper detector exists
  and is `fixer.md` step 6's: re-run the scoped gate (`scope.run`, which names
  `tests/card.mjs`) after any merge of origin/main and before the push; its
  standing cost is one `card.mjs` run, about 30 s on CI's runner. The merge
  `e59b1fb54` was pushed without that re-run; this head ran it after its own
  merge (`176db5f00`).
- `pr-contract`: refused the body because `fast (3.14)` was red and `## Red
  checks` did not name it (job 117470593100). This section is the answer; no
  cheaper detector beyond `tools/pr/prepr.sh`, which this body passed.
- `delivery-status`: not a required context; its log lists overdue record
  rows for other pull requests (#2335, #2323, #2311), none of them this diff's
  (job 117464452564). No finding for this branch.

## Forward-carry

`dev/programme/rosters/wave-r10-groups.json`: the four stage briefs that add
card rows or links -- R10-UX-SETUP, R10-ADVISOR, R10-SCORES and R10-UX-HEALTH
-- carry the census's refusals, including the two this round adds: an
identifier carrying the navigation primitive's name is red (`b.open` is
`b.foldOpen`), and a form built or submitted by name is red wherever it is
written. In R10-SCORES the carry sits after main's newer item (4) from
R10-RATIO-SITES, which the merge kept.

## Friction

- `finding-propagation.md: stale: R10-TICK (o), carried in this group's brief, says tools/audit/seat/train.sh line 182 resolves the checkout to the tools directory; train.sh now derives it with git rev-parse --show-toplevel and #2305 is merged, so nothing on this branch acts on it.`
- `fixer.md: cost: a crashed seat left this group's newest commits (f1542b17d) only in a /private/tmp worktree and a wip-sync snapshot, with a planted mutation uncommitted in the card; the next seat had to compare three heads by ancestry before it could start.`
