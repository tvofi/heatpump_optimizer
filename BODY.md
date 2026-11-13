**A policy change, awaiting the owner's review.** It changes what the D5 and D6 finder seats must do from round 11 on, and the finder scopes that size them; I drafted it, and merging needs the owner's approving review (`CLAUDE.md`, "Where the policy is").

The owner's rulings of 2026-11-13, verbatim (1 = all user facing text in production; 2 = every single sentence in all documentation; 3 = all code comments):

1. "Do 1 in round 10, and 2 and 3 in round 11 sequenced as you recommend. Code comments in instruments and the documents that describe the instruments, developer and other non-static documentation also in scope for 3."
2. "The test suite comments are in scope. Also, since 1-2 is done before 3, they may not trust code comments, only the actual code behaviour"
3. "Go by your recommendation, but I would like the scope of d5 and d6 to always cover that full scope"

What changes:

- **`tools/audit/text_ledger.py`** (new instrument) enumerates every unit a seat must judge. For D6 that is each sentence of a document, each fenced block, each sentence of every JSON string leaf (strings.json and translations), and each user-visible literal in the Python and card JavaScript (two words or more, with markup, interpolation and CSS dropped). For D5 it is each comment block and each docstring in Python, JavaScript and shell. A file with no text is one `file` unit, and a unit's id is the sha1 of its text, so ledgers diff across rounds. `check` refuses an unrowed unit, an orphan row, a claim without an executed command and result, a verdict outside true/false/stale/unverifiable, and a non-true verdict without the truth. `--plant` writes one sentence into a copy of a file and must see that sentence refused as unrowed: the per-seat null control that an omission is visible.
- **`dev/audit/config/scopes.json`.** D5's universe grows from production Python and the card to production, `tools/**` and `tests/**` (`.py`, `.sh`, `.js`, `.mjs`), in nine seats. D6's universe gains RELEASE_NOTES.md, production Python and the card (user-visible strings), the instrument documents, READMEs under tools/, tests/README.md, dev/audit/README.md, role contracts, rules, dimension briefs, the living handover and the plan, in seven seats. D6's `static` map names the records it leaves out, each with its reason: round evidence and RCAs, the archive, delivery, register and triage rows, decision records, dated design records, the generated `.claude`/`.cursor` rules, and the linters' fixtures. A new `ledger` key per dimension caps each seat at `max_units` text units (4500, chosen so the largest single file, tests/features.py, fits with room), so a seat's cell can be finished.
- **`tools/audit/check_scopes.py`** enforces both, and its `--self-test` refuses each perturbation. A seat over the cap is refused by name. So is a path matching D6's `classify` globs (`**.md`, `**.mdc`, `**.html`) that is in neither the universe nor `static`, a path in both, and a static entry that names nothing or carries no reason. A new README or role file therefore cannot slip out of D6 unnoticed.
- **`dev/governance/dimensions/D6.md`, `D5.md`.** D6 rows every unit and runs one executed check per claim against the code that decides the behaviour, never a comment. D6 runs before D5's comment pass. A finding covers one file, and its harness output is `check`'s. D5 step 4 stops sampling: every comment and docstring in its cells is judged true or false of the code it sits on by an executed check of that code, and the concision judgement is kept. D6 carries the rulings verbatim and D5 cites them, so there is one copy.
- **`.claude/workflows/audit-find.js`.** Boxes B11-B13 hold the ten new light seats. `CADENCE` stays at 2 for D5 and D6, and **that is wrong for ruling 1**: at 2, D5 and D6 are off in round 11, while the ruling puts "2 and 3 in round 11". The base's `check-wave-script.mjs` named D5 as its cadence-off arm, so it refuses `D5: 1` (`ci_predict` BOOTSTRAP). Following fixer.md step 5, this pull request is p1. It carries the grader hunk, which now reads every dimension's activity off `CADENCE` and so passes at either value, plus the policy. p2 is the one-line `CADENCE` move, `D5: 1, D6: 1`, which can land once p1 is on main (Forward-carry).

**Why round 10 missed "The optimizer never writes a recommended space set-point."** I established this from the record rather than assuming it. The sentence is `space_setpoint_entity`'s description in strings.json and translations/en.json, added by 6f02b8a71e (#483). No round-8, -9 or -10 D6 output contains it (`git grep` below, rc 1). Round 9's claims table (`dev/audit/rounds/round9/D6/s1/claims_table.txt`) has four strings.json rows, C50, C53, C54 and C59, all about field keys and labels. Round 10's D6-s3 owned strings.json, and its `claims_checked=3741` (`dev/audit/rounds/round10/D6/s3/REPORT.md`) counted key parity between strings.json and en/sv, plus services.yaml against the registered schemas. That is a check that keys exist, not that their sentences are true. The method extracted only sentences that looked claim-bearing and kept no record of the ones it skipped, so the skip left no trace. Under the amended method the miss is impossible in two places. First, `text_ledger.py units --dim D6` lists that sentence as a unit, and `check` refuses any ledger without a row for it; the self-test pins that sentence as a unit. Second, the row is a claim about behaviour, so its check must run the code: D6.md step 2 says "A key-parity check is no truth check".

**Finding shape and COMMON.md: it fits as written, so this PR does not change COMMON.md.** A finding covers one file with false or stale rows. Each COMMON.md requirement maps onto it:
- Item 1, the executed number: `text_ledger.py check`'s counts over the seat's ledger, which is TSV under the round directory.
- Item 2, the instrumented symbol: the production symbol that the false row's own check drives.
- Item 3, the perturbation: the one-line production edit that makes that row's check return the sentence's claim. The count moves down by one when that row is re-run.
- Item 4, the metric: false or stale rows per file.

The planted unit is an extra null control on completeness. COMMON item 5 asks for one only for cost, gain or time, so it fits beside that item.

The truth-side control the dispatch proposed, a known-false sentence planted where the seat cannot see it, is **not built**. Planting it blind means editing the export before the fan-out, and every dimension's seats read that same export (`audit-find.js` `workdir`), so a planted sentence would corrupt other dimensions' measurements. Forward-carry asks the owner for a ruling.

Generated scope-line block: The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

## Head

ac1607ad7344f75d619dd5f0b2f2c66d12663a3f, cut from 90c6bc3b0756475e28d4ace8d8e31c4788474933. origin/main was e23124ff6e45bac1d48b4a775dad555a37965355 at 2026-11-13T18:30:38Z, and `git merge-tree --write-tree origin/main HEAD` prints one tree.

## Mutation proof

- `text_ledger.py`: with `unrowed = sorted(ids - set(by_id))` changed to `unrowed = []`, `python3 -I tools/audit/text_ledger.py --self-test` prints `FAIL a dropped row is refused by its unit id` and `17 checks, 1 failed`. Restored, it prints `17 checks, 0 failed`.
- `check_scopes.py` cap: with `if n > d["ledger"]["max_units"]` replaced by `if False`, `python3 -I tools/audit/check_scopes.py --self-test --repo .` prints `SELF-TEST FAILED`, with the arm "a seat over ledger.max_units is refused by name" false.
- `check_scopes.py` line: with `errs = [f"classified in neither ...` emptied (`errs = [] and [...]`), the self-test prints `SELF-TEST FAILED`.
- Cadence control: with `activeIn` reduced to `!!CADENCE[dim]`, so the round number is ignored, `node tools/policy/check-wave-script.mjs` prints `FAIL ...and the cadence is otherwise read from the round number (off at 11: ; ...)` and `224 passed, 2 failed`. Restored, it prints `226 passed, 0 failed` both at the base cadence and with `D5: 1, D6: 1` (p2's tree).
- The self-test's own arm against a vacuous `--plant`: a ledger that already rows the planted unit must fail `--plant` (`--plant fails a ledger that already rows the planted unit`).

## Null control

- Base scopes, base tree: `python3 tools/audit/check_scopes.py --repo . --ref 90c6bc3b0756475e28d4ace8d8e31c4788474933 --scopes <(git show 90c6bc3b0756475e28d4ace8d8e31c4788474933:dev/audit/config/scopes.json)` prints `D5 ... universe=100`, three seats, and `D6 ... universe=86`, three seats, with no unit column, because the base has no `ledger` key.
- The self-test's complete ledger passes `check` with and without `--plant` (arm "null control: the complete ledger passes, and its plant is refused"). Its live D5 and D6 pass the cap and the line (arm "null control: the live D5 and D6 pass the cap and the line").

## Figures

- D5 and D6 seats, units per seat (rule: `text_ledger.py`'s units over each seat's files for the ledger step): `python3 tools/audit/check_scopes.py --repo . --ref HEAD` prints D5 `seats=9 universe=535`, with units per seat from 0 to 3808, and D6 `seats=7 universe=344`, with units from 2230 to 3988. Coverage `unclassified=0`.
- Round-10 sentence enumerated: `python3 tools/audit/text_ledger.py units --dim D6 custom_components/heatpump_optimizer/strings.json | grep -c "never writes a recommended space set-point"` prints 1, out of 2234 units in that file (`| wc -l`).
- Absent from every earlier D6 output: `git grep -c "never writes a recommended" 90c6bc3b0756475e28d4ace8d8e31c4788474933 -- dev/audit/rounds/round9/D6 dev/audit/rounds/round10/D6` exits 1. The control is that the same `git grep` over `custom_components/heatpump_optimizer/strings.json` finds it.
- Self-tests, in governance.yml's `self-tests-outside-seat` order: `python3 -I tools/audit/check_scopes.py --self-test --repo .` prints `SELF-TEST passed`, and `python3 -I tools/audit/text_ledger.py --self-test` prints `17 checks, 0 failed`. `node tools/policy/check-wave-script.mjs` prints `226 passed, 0 failed`, its cadence line reading `off at 11: D5, D6, D11, D13`. `python3 -I tools/audit/seat/selftest_wiring.py --check` reports every self-testing file as wired, and `python3 -I tools/ci/selftest_scope.py --self-test` reports 0 failed.
- `tools/ci/selftest_closures.json`'s `self-tests-outside-seat` entry was re-measured by `python3 -I tools/ci/selftest_scope.py record --step self-tests-outside-seat` (Linux, strace): a new `run_sha`, plus `tools/policy/legacy_control_files.json`. The record also rewrote `beatd`'s probes, which this branch does not touch, so I restored that entry from the base; main's re-measure owns it.
- Policy caps: `node tools/policy/policy_lint.mjs --budgets` shows D5.md and D6.md under their per-file line and token caps, and the corpus inside its band. No cap was raised. D6's growth was paid by cutting prose that is now spent or carried by a detector: "Read `COMMON.md` first" (the dispatch prompt says it), step 3's claims-table columns (now `text_ledger.py`'s header and refusals), the `## Numbers` list (now `check`'s RESULT lines), and the per-type recipes for performance and versions, which are folded into "one executed check per claim". D5's false sentence was corrected: "lacks ... `RELEASE_NOTES.md`" contradicted COMMON.md's "Keep `RELEASE_NOTES.md`".
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `node tools/policy/policy_lint.mjs` reports 0 errors, and `node tools/policy/brief_lint.mjs` was run as well.

## Red checks

none

## Approval

Pending: the owner's approving review at this head. This is a policy change (D5.md, D6.md, scopes.json and its instruments), and no approval is recorded here.

## Carries

- Carry 0 (owner instruction 2026-11-13, the round playbook): already carried at this head, with no new pointer needed. This group adds no policy file or role contract. It amends two dimension briefs and extends one instrument, and the playbook already names all three at the phase where they run. Dry read from the playbook alone: `dev/audit/README.md:30`, phase "2 dimensions and finders", names the instrument `tools/audit/check_scopes.py` over `dev/audit/config/scopes.json` (the `ledger` cap and the D6 classify line it now refuses) and the contract `dev/governance/dimensions/`. That contract leads to `dev/governance/dimensions/D5.md:24` and `dev/governance/dimensions/D6.md:18`, which name the enforcing instrument `tools/audit/text_ledger.py` (`units`, `check --plant`). `tools/audit/check_scopes.py:30` imports `text_ledger.py` for the cap. The same row names `.claude/workflows/audit-find.js`, which holds the B11-B13 boxes and `CADENCE`. The playbook group R10-ROUND-PLAYBOOK-FINAL has merged its p2 (#3550, merge 23963d39be, an ancestor of this head), so the playbook is in this tree. Its roster stage is still `carries-open` at roster `handoff/audit-r10-roster` fc39918db8, so the group has not finished. Its reconciliation pass re-derives every path the playbook names, and that pass covers this group's paths without a carry from here.
- Carry 1 (body item d21035c2, p2 of this split, `CADENCE` to `D5: 1, D6: 1`): not built here. The base's `check-wave-script.mjs` refuses `D5: 1` (`ci_predict` BOOTSTRAP, fixer.md step 5), so the move lands only once this pull request is on main. It is a split part of this group, landed as carry 1 on `handoff/audit-r10-roster` at fc39918db8. Carry: R10-D5-D6-FULL-SCOPE (items d21035c2)

## Forward-carry

- p2 of this split: set `CADENCE` to `D5: 1, D6: 1` in `.claude/workflows/audit-find.js` once this pull request is on main, so that D5 and D6 run in round 11 as ruling 1 orders. The grader in this pull request already passes at that value (Mutation proof). Carry: R10-D5-D6-FULL-SCOPE
- The truth-side planted-false-sentence control needs a per-seat copy of the export, or a verifier-side plant. Which of the two is the owner's call, because it changes the round's export contract. Carry: dismissed: a question for the owner's review of this pull request, not a finding with a measured seam
- `ledger.max_units` (4500) is set without a throughput measurement, so the round-11 reports' `unfinished` field is its first measurement. The cap lives in scopes.json, where the next round's dispatch reads it. Carry: dismissed: recorded in scopes.json's `ledger._rule`, which the next round reads

## Friction

none
