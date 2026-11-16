R11-PRE-NEW-DIMENSIONS, p2 of 2: two dimensions whose oracle is the plan (D16, actuator write) and the documented effect (D17, feature behaviour), each over a universe a command prints. Policy pull request (two dimension briefs, `CLAUDE.md`, `COMMON.md`, `D3.md`, `policy_budgets.json`); finder-critical: the round-11 finder start waits on it.

**Split.** p1 (#3646, `tools/audit/prepare_baseline.sh`'s `ISOLATED_DIMS` gaining D16) is on main as `47f0f18a7e`. This head is the earlier p2 head `4f73a0c5e8` merged into `origin/main` `030a4d377f9f26f5b8befe5721d86aea454f29e0` by merge, on refs of the topic `r11-pre-new-dimensions-p2`. Six files conflicted; each takes main's side with this group's own edits re-applied, listed in the merge commit's message.

**Evaluation.** Built from `c6ce415b7711d76cf6c08f926f30da91f7bda924`, the tip of `eval/r11`, whose `review` field reads `approve` of `02a48db212e0e49af62863575cba86bc339d4958`. At that tip every card closed here is `accepted` with tvofi's ruling and `gates_finders` true, and names one file: E11-U1 `dev/governance/dimensions/D17.md`; E11-U2, E11-U4, E11-U5, E11-U6, E11-U7, E11-U8, E11-U9 and E11-U10 `dev/governance/dimensions/D16.md`. This diff adds both files, so each card's `paths` is among the merge's changed files. No card names a path the design does not. The fold of `check_scopes.py --round` (a path ending in a slash read as a prefix) is not built: its condition, "unless the approved evaluation names file paths", is met. E11-U9 and E11-U10 are ruled ("Accept all four") and built with the rest. This head is not an ancestor of the review sha (decision 0018 section 6; `## Figures`).

**Wording.** Both briefs are drafted by this seat under mandate 6893738184 (scope all, in force to 2026-12-15T12:00Z), declared in `D16.md`'s opening, which `D17.md` cites; the owner's to change at review.

**Design.** Follows the note `a9377bcf47957e63060733e61a9cb551a8734b1c` (`Design review: approve` at `daa950c68c`), with the verdict's three notes built: the duty-mode refusal is set equality with a planted fourth mode as its red arm; the brief's pump has P >= 3f; E11-U6's cell books step k-1 `idle` so a step selected late moves it. R11-PRE-FINDER-CONTRACT's p2 is on main (#3647), so the two departures the earlier p2 head made for its absence are gone: this diff adds no cadence entry (main's driver has no cadence table) and changes no line of `dev/audit/config/finding.schema.json` (main's patterns already reach D17). One departure remains: the note cites `D3 step 6` for a void oracle and `D3.md` has five numbered steps; both briefs cite `tests/README.md`, which carries the rule.

**What each U card is driven by** (the step is the brief's numbered step; the input is the pull request the card's `unowned` names):

| card | brief, step | cell | input |
|---|---|---|---|
| E11-U1 | D17 step 3 | the away step's weekend and holiday comfort fields, an `option` line | 3013 |
| E11-U2 | D16 step 2 | `boost-partial` | 3562 |
| E11-U4 | D16 step 2 | `disinfection` | 3452 |
| E11-U9 | D16 step 2 | `min-cold-tank` | R10-SETPOINT-BOOST |
| E11-U6 | D16 step 3 | `partial`, the cycle held across the end of step k, step k-1 `idle` | 3478 |
| E11-U8 | D16 step 3 | `partial` entered from `idle` | 3530 |
| E11-U5 | D16 step 3 | `idle` entered by a re-solve minutes after `partial` switched the supply on | 3512 |
| E11-U7 | D16 step 4 | `partial`, the water set-point | 3405 |
| E11-U10 | D16 step 4 | `dhw-only`, the tank above its set-point less the hysteresis | 3531 |

**What is built.**

- `tools/audit/enumerate.py`. `d16-writes`: a write line is a call of, or a reference to, the service call, less a call whose literal domain is on `READ_ONLY_DOMAINS`; a domain that is no literal prints `domain=?` and is a cell. It no longer counts the forecast read and now counts the service call handed on uncalled inside `coordinator.py`. `--cells` is sites times `STATES`, one axis of plan states, and refuses unless `const.py`'s `PUMP_DUTY_MODES` equal the duty modes those states name. `d17-features` takes `--kind`; its prefixes are `KINDS`.
- `D16.md`, `D17.md`: the oracle, the territory against D1, D2, D6, D8, D12 and each other stated once, the steps above, D16's two owed perturbations with their null controls.
- `scopes.json`, `rotation.json`: three seats each. D17's universe holds the package, `services.yaml`, `strings.json` and the blueprints, its `kind` axis the enumerator's prefixes.
- `check_scopes.py`: an axis the enumerator also prints must name exactly its prefixes (`AXIS_SOURCES`), and five self-test arms. Its existing arm that dropped D4's and D6's blueprints globs now drops the glob from every universe that names one, since D17's holds the blueprints too.
- `audit-find.js`: DIMS, ISOLATED (D16 only, equal to `prepare_baseline.sh`'s list on main), the six seats heavy on B11 and B13, no box added. `finder_overlap.py`'s seat pattern reaches D17.
- `COMMON.md` lines naming the dimensions that read `docs/` (D17 added) and those with an isolated worktree (D16 added); `D3.md` no longer calls itself "the one finder" with a worktree, untrue of the driver's ISOLATED set.
- `tests/closures.json`: `tests/entities.py`'s closure gains the two briefs (recorded on Linux by the earlier p2 head; the claimnotes merge driver merged it as a set with main's).

Design choices a reviewer should not read as bugs: `READ_ONLY_DOMAINS` is keyed on the domain, not the service, so every call on `weather` is no write, and a write the integration ever makes on that domain would need the key widened to (domain, service). The states are an enumerator constant and not a `scopes.json` axis: every card's step needs all states at one site, so seats are cut by step. `check_scopes.py` loads the enumerator by path to read `KINDS`: one copy the check reads, never a third list.

Alternatives that lost: the oracle read from `desired` (one call, and it grades the arbiter against itself: E11-U2 and E11-U9 are defects inside it); one dimension for both (E11-U1 has no write-path defect and E11-U2 no feature that is off); a box per dimension (two containers for seats that already have a worktree or share the export read-only).

## Head

4632a10bff41d516b5a5cf1176f14b29c8481f51

## Mutation proof

Ten predicate mutants, each applied alone in a detached worktree at this head, the file's `--self-test` run, then restored. Each exits 1 naming:

- `enumerate.py`, `if dom not in READ_ONLY_DOMAINS` made always true (a read-only domain no longer skipped): `d16 a call on a read-only domain is no write (the count stays)`, `d16 a domain passed by keyword is read`
- `enumerate.py`, the site test also requiring the attribute to be called (only calls are sites): `d16 a reference handed on uncalled is a write with no literal domain`
- `enumerate.py`, a `domain=?` site dropped: that arm and `d16 a call whose domain is no literal is a cell, never dropped`
- `enumerate.py`, `modes != named` made `not modes`: `d16 --cells a duty mode added in production and rowed by no state is refused`
- `enumerate.py`, `modes != named` made `not named <= modes`: the same arm
- `enumerate.py`, `--kind` filtering nothing: `d17 --kind prints one prefix's lines`
- `enumerate.py`, the stray-prefix refusal never taken: `d17 a printed prefix KINDS does not name is refused`
- `enumerate.py`, the `domain=` keyword not read: `d16 a domain passed by keyword is read`
- `check_scopes.py`, `axis_errors`' comparison never taken: `SELF-TEST FAILED`, `D16 and D17 arms: 3/5 held`
- `check_scopes.py`, `axis_errors`' set equality made `set(vals) <= set(src())`: `SELF-TEST FAILED`, `D16 and D17 arms: 4/5 held`

Each line names the arm or arms read from that run's `SELF-TEST FAILED` line up to its first 230 characters; an arm past that was not transcribed.

Unpinned by construction: the contents of `STATES`, `READ_ONLY_DOMAINS` and `KINDS` are data; a state renamed or a domain added moves no arm. The briefs' state table is the second reader of `STATES`.

## Unpinned sites

All four are lines of `check_scopes.py`'s self-test, none a production predicate.

- `tools/audit/check_scopes.py:901 CONST_SWAP`: equivalent. The index picks which D17 seat the arm empties; any seat emptied leaves its cells unowned, which is what the arm asserts.
- `tools/audit/check_scopes.py:904 CONST_SWAP`: equivalent. The index picks which D17 seat also carries the planted kind; the refusal asserted is `axis_errors`' on the axis list, whichever seat carries it.
- `tools/audit/check_scopes.py:904 STMT_DEL`: equivalent for the arm. With no seat carrying the planted kind the axis list still names a kind the enumerator does not print, and the arm asserts that refusal by its text.
- `tools/audit/check_scopes.py:1050 STMT_DEL`: the mutant deletes one arm of the self-test (the blueprints globs dropped from every universe that names one); nothing counts the self-test's arms, so an arm removed is not seen by the arms that remain. The arm predates this diff, which changes its wording and which universes it strips; no killing check is added, since a count of arms pinned in the same file is deleted by the same edit.

## Null control

- The base enumerator (`origin/main:tools/audit/enumerate.py`) over this head's tree prints the forecast read (`_fetch_weather_forecast`) as a write and no line for the handed-on service call (`_disinfection_switch`); this head's prints the reverse (`## Figures`).
- `check_scopes.py --self-test`: the live file passes; a block of D16's first seat copied into its second is refused naming both seats; D17's last seat emptied is refused `unowned`; a kind planted in `scopes.json` alone, and a prefix planted in the enumerator alone, are each refused naming it.
- The schedule is graded by `tools/policy/check-wave-script.mjs`, which this diff does not change (`git diff origin/main 4632a10bff41d516b5a5cf1176f14b29c8481f51 -- tools/policy/check-wave-script.mjs` prints nothing), so the base copy and the head's are one file.
- The D16 oracle's own controls are the brief's: P1 and P2 are owed by the finder in its worktree, with the unedited tree green and the docstring edited alone moving no cell.
- No finder harness exists for the cards (each is an owner or outside report); the planted cells above are the fixture.

## Figures

Each at 4632a10bff41d516b5a5cf1176f14b29c8481f51 unless a sha is named; an arm is one comparison in a self-test.

- `python3 -I tools/audit/enumerate.py --self-test`: `SELF-TEST passed (160 arms)`; at 030a4d377f9f26f5b8befe5721d86aea454f29e0: `SELF-TEST passed (147 arms)`.
- `python3 -I tools/audit/enumerate.py d16-writes` piped to `wc -l`: 38, of which 8 `write` and 30 `hold` (the first word of each line, counted); 4 of the 8 print `domain=?`. Main's copy over the same tree prints one line naming `_fetch_weather_forecast` and none naming `_disinfection_switch`; this head's none and one.
- The same with `--cells`: 532, which is 38 times the 14 entries of `STATES`; main's copy over the same tree: 456.
- `python3 -I tools/audit/enumerate.py d17-features` piped to `wc -l`: 307; by `--kind`: option 130, config-field 102, options-step 26, config-step 15, service 15, entity 14, blueprint 5, summing to 307.
- `python3 -I tools/audit/enumerate.py --briefs`: exit 0, with `ok D16 d16-writes --cells` and `ok D17 d17-features` among its lines.
- `python3 -I tools/audit/check_scopes.py --repo . --ref HEAD`: exit 0; `ok D16 mode=cells seats=3 universe=94`, `ok D17 mode=cells seats=3 universe=101`, `unclassified=0`. `--self-test`: `SELF-TEST passed (every perturbed scope refused)`.
- `node tools/policy/check-wave-script.mjs`: 249 passed, 0 failed.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`; `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tools/audit/fold_ledger.py sync --dry-run`: the driver already carries the schema.
- `python3 -I tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `git merge-base --is-ancestor HEAD 02a48db212e0e49af62863575cba86bc339d4958`: exit 1 (not an ancestor).
- Gate scope, `python3 tests/closure.py select --diff 030a4d377f9f26f5b8befe5721d86aea454f29e0`: the mode line below; the one script it names is `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py`: exit 0, `ALL 2723 ENTITY CHECKS PASSED`.
- `tools/pr/prepr.sh` with `PREPR_SKIP_CLOSURES=1`, `MUTANT_IN_PLACE=1` and both self-tests as `MUTANT_CMD`: rc 0 at 4632a10bff41d516b5a5cf1176f14b29c8481f51; no step refused; `ci predict` names no closures, fast, governance or instrument red against 030a4d377f9f; `diff mutants` is its one `WARN`, 4 survivors among the diff's first 40 mutants, each under `## Unpinned sites`.

<!-- figure-block: scope-line mb=030a4d377f9f26f5b8befe5721d86aea454f29e0 head=4632a10bff41d516b5a5cf1176f14b29c8481f51 -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

## Raise justification

Rows of `node tools/policy/policy_lint.mjs --budgets` raised, each to the value it measures at this head (the literals are in the diff of `dev/governance/config/policy_budgets.json`): the `lines` and `~tokens` rows of `dev/governance/dimensions/D16.md` and `dev/governance/dimensions/D17.md`, new, and `corpus:`. No other row rises. Three rows are re-recorded down to their measurement: the `~tokens` rows of `CLAUDE.md`, of the row the lint keys `tools/audit/briefs/COMMON.md`, and of the row it keys `tools/audit/briefs/D3.md`. The other four aggregates are inside their band and untouched. `corpus:` at `origin/main` already measures above its recorded cap and inside the band; the value written is this head's measurement.

Payments tried: (1) taken: the prototype's "Escapes this dimension exists for" lists dropped from both briefs, the cards carry them; (2) taken: the prototype's fourth D17 step (null control and perturbation) dropped, `COMMON.md` owes both of every finding; (3) taken: the territory against each neighbour stated once, in D16's hunting section, with D17 citing D16 for the ruling and wording; (4) taken: `CLAUDE.md`'s two rows paid inside the file by shortening the D16 row until the file's `~tokens` row is below main's cap; `COMMON.md`'s two additions by cutting "that have already cost a day each", which names no trap and no cost a seat can check; `D3.md` by "the one finder"; (5) not taken: D16's state table moved into the enumerator's output, since prose moved to an uncapped file is the reclassification `ratchet-budgets.md` refuses, and the invariants are the oracle the brief exists to state; (6) not taken: one brief for both dimensions, the design's rejected alternative, which would cut the two headers and one hunting section and leave `unowned` unable to say which oracle failed; (7) not taken: cutting another brief's prose to make room, which is R11-PRE-BRIEFS-TEXT's diff on the same files.

Architecture score: dS +0.0000 NULL

## Approval

Pending; none is claimed here. A policy pull request: it merges on tvofi's approving review at the head, or, under mandate 6893738184, on the orchestrator's declared review after the fix review, which is also what approves the raise (decision 0013).

## Red checks

- budget-raise-gate: red by design until an approving review at the head: this diff raises rows of `dev/governance/config/policy_budgets.json` and `## Raise justification` is what the gate reads. Cheaper detector: none owed; `node tools/policy/policy_lint.mjs --budgets` prints each raised row before any push at no standing cost.

## Forward-carry

- `d16-writes --cells` now prints `<site> | <state>` over 14 states where it printed `<site> | duty=<mode> | <condition>`, and write lines end `domain=<literal or ?>`. No tracked file is keyed on the old strings: `git grep -l '| duty=' -- . ':!tools/audit/enumerate.py'` prints nothing at this head, so no stage has a ledger to re-key. Carry: dismissed: no consumer of the old format exists in the tree
- Carry 0 of this group (the actuator-write half of intake carry 175): built here, the cell ledger is `d16-writes --cells` with `--ledger`, the target the plan's computed value. Carry: dismissed: built here
- Carry 1 of this group (from r11-pre-briefs-census, item dcd38e1b): both briefs cite the two universes and `--briefs` runs them. Carry: dismissed: built here
- Carry 2 of this group (merge main into p2 after p1, re-run prepr, hand off): done at this head, on the refs of topic `r11-pre-new-dimensions-p2`; the step ref `handoff-wip/r11-pre-new-dimensions` of the earlier seat is left as it was. Carry: dismissed: done here
- Carry 3 of this group (which of the two p2s merges last): R11-PRE-FINDER-CONTRACT's merged first (#3647), and this head is built on it. Carry: dismissed: settled by #3647's merge

## Friction

- designer: stale: the note cites `D3 step 6`; `D3.md` has five numbered steps at this base. Carry: dismissed: both briefs cite `tests/README.md` instead
