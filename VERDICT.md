Fix review: blocked 5c82409818aeecda5798676d8f8ea8bd9b232133 figure-false: the ruling says no test pins --max 40, but tests/entities.py:33938 requires the literal in mutation-ledger, so the carried one-token change turns entities.py red

bus-nonce: 5ce72605879a7c7ebdfb4fe1a1efecb3

Round 1. Measured head `5c82409818aeecda5798676d8f8ea8bd9b232133` (PR #2759 live head at review time), merge base `2636ce9e9`.

## Block

P85's Cost paragraph states: "`git grep -e '--max 40'` finds no test or entity that pins the figure (only the two workflow lines and a historical RCA sentence)". At this head that grep returns `tests/entities.py` too: line 33938 lists `('--scope full --drain "$out" --max 40', _ml_meas)` in `_ML_MISSING`, the required strings of the check "mutation-ledger measures without a write grant and mutation-ledger-push writes only rows". It also returns roster and fixplan lines (`dev/programme/rosters/wave-r9-groups.json` x2, `dev/audit/rounds/round9/fixplan/data.py`, `prestudy/ALT-ROSTER.json`), which are historical. I applied the carry exactly as written (mutation-ledger `--max 40` -> `70` in `.github/workflows/nightly.yml`) and that test's membership check went from present to absent (ev/pin_mutation.txt). So the fix is not "one token in nightly.yml": it is that token plus the pin in tests/entities.py. The carry text gives the fixer nothing about the pin, and the cost and risk rest on a premise this tree refutes. The repair is small: correct the Cost sentence, add the tests/entities.py pin to the carry text (move the pinned string to `--max 70` in the same PR), and re-lint the carry with brief_lint.mjs.

## Findings

- The ruling's cost premise is false at the head: `tests/entities.py:33938` pins mutation-ledger's `--max 40`, and the carry for R10-FLY-LEDGER-SAMPLE leaves it out. This is the block above, and it is settled by amending this PR's triage file. Carry: R10-FLY-LEDGER-SAMPLE | #2759 | O1 | dismissed: settled by the amendment this block requires before merge

## Evidence

- Figures re-derived at the head (ev/figures.txt): run 40054585693's job windows match the body (146 min, 144 min, 26 s). nightly.yml has `--budget-minutes 270`, a 330-minute timeout and the "records nothing" header, as quoted. 70 x 146/40 = 255.5 min, which matches "about 256". `rg` Verdict count is 1 ACCEPT. `roster_edit.ruling_verdict` returns P85 -> ACCEPT and P99 -> None, which reproduces the null control. batch15 is not at this base, as the ruling says.
- Not re-derived: the orchestrator's unpinned-site counts (4062 -> 4012, 6283 -> 6297), the 20 to 28 kills a day, about 3400 killable sites and `private: false`. The ruling marks these as not re-counted. I did not re-run the brief_lint scratch-roster null control.
- The pin evidence comes from my own instrument, ev/pin_check.py. It extracts `_workflow_job` from tests/entities.py and evaluates the same membership. I could not run the full tests/entities.py here because `homeassistant` is not installed in this container.
- Merge: `git merge-tree --write-tree origin/main 5c82409818aeecda5798676d8f8ea8bd9b232133` exits 0 (tree 6bf8d3e47). No claim files touched. VERSION, manifest and notes heading are untouched.
- Head: the body's Head section names `941827589`. The live head `5c8240981` adds only the PR's own delivery row (dev/programme/delivery/2759.md, one line for #2759), the same shape as #2752 merged.
- CI on the head: at read time all completed check runs were success or skipped. tests / closures, typing, fast (3.14), browser, governance / env-matrix and instrument-self-tests were still in_progress. No pr-contract run appeared in this head's check-run listing. None red, so step 11 owes nothing yet.
- Steps 1/2/3/6 (mutation proof, finder's harness, class): n/a. The diff is a ruling record with no production line.
