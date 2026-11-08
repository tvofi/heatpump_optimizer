Fix review: merge 5c419e4cfc66af1e345e26a08edd68a4956dfded

bus-nonce: 1a83e6d48773b39d2653d8c19f268118

## Evidence

Round 1 of the fix review of PR 3346 (R10-WHY-NOW-WIDGET, part 2). Head measured: 5c419e4cfc66af1e345e26a08edd68a4956dfded, still the branch head at verdict time (git ls-remote). Merge base 996ded2a6dc52816bd4c7dd873c048d85fc6adad. Roles diff merge-base...origin/main is empty, so the contract is current.

- Three-dot diff: tests/card_browser.mjs (+21: exports `H.unreachable`, adds the own-box/unclipped probe at the start of `p9Grid`) and dev/programme/delivery/3346.md (the delivery row is in the diff). VERSION, the manifest and RELEASE_NOTES.md are untouched. No new tracked file other than the delivery row; no budget file touched; no claim file touched.
- RESULT head: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs` after plan_view.py: ALL BROWSER CHECKS PASSED, EXIT 0, `ok P9 instrument: a text run clipped by its own box reads as clipped, and an unclipped one as clear` (ev/browser-head.log).
- RESULT figure: a probe-only copy of the head prints `{"own":187.0625,"free":0}`, matching the body's 187.1 px / 0.0 px.
- RESULT mutant A (failing first; the pre-#3274 walk, `run.el` -> `parentOf(run.el)`, ev/mutant-A.diff): only the P9 instrument check fails, `own box 0.0 px, unclipped 0.0 px`, EXIT 1 (ev/browser-mutA.log). This matches the body's mutation proof.
- RESULT mutant B (null control; `unreachable` returns 999 for every run, ev/mutant-B.diff): the P9 instrument check fails with `own box 999.0 px, unclipped 999.0 px` and the P9 grid fails, EXIT 1 (ev/browser-mutB.log). So the free-run half of the check is live and a walk that marks everything clipped is caught.
- The finder's harness for carry 7c609975 is the P9 grid in tests/card_browser.mjs itself. This PR adds the pin the carry lacked. The class is one seam, the walk start in `unreachable()`; the body names no enumeration rule and the carry states one site.
- The body's carry 0 claim (the widget settled by #3274) is in the tree at the merge base: `why_now` in the payload, `whyNowHtml` in the card, the why-now cases in tests/card.mjs. That part was settled before this PR, so it is not re-measured here.
- `python3 tests/closure.py select --diff <mb>`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`; card_browser.mjs is on the grid surface and was run by hand above.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tools/audit/archscore/score.py --diff <mb> <head>`: `Architecture score: dS +0.0000 NULL`, rc 0.
- tests/entities.py run plainly (no BASH_ENV, no workaround) did not run clean: ModuleNotFoundError for homeassistant at tests/harness.py:25, rc 1. The module is missing from this environment, so this is not a failure of the PR. With `PYTHONPATH=tests/hastub` it ran clean: ALL 2668 ENTITY CHECKS PASSED, rc 0.
- `git merge-tree --write-tree origin/main <head>`: rc 0 against 996ded2a6d and again against the newer main 17e621f08c (tree 975539730f). No conflict.
- CI: `merge_train.py classify 5c419e4cfc66af1e345e26a08edd68a4956dfded --pr 3346` -> `GREEN 5c419e4cfc66af1e345e26a08edd68a4956dfded pending: none red: none`, rc 0 (ev/classify.log). The packet's check digest is all success or skipped, so the body's `## Red checks: none` holds.
- The body's `## Head` names 5c419e4cfc66af1e345e26a08edd68a4956dfded. Its forward-carry is none, and none is owed: the PR closes the carry rather than producing one.
- Diff mutants: no production line and no Python line changed, so mutant_run.py has nothing to mutate. The hand mutants above cover the JS lines.
