Fix review: merge 0822a4e65e2288f4327a6662c291477a56b69c37

bus-nonce: 28ab03f8950913e86d5679973cbc22f0

Round: first (no `--reviewed-head`). I measured head 0822a4e65e2288f4327a6662c291477a56b69c37, which is the PR head at verdict time (`git ls-remote origin refs/pull/3558/head`).

## Evidence

- RESULT ci: `merge_train.py classify 0822a4e6... --pr 3558` prints `GREEN 0822a4e65e2288f4327a6662c291477a56b69c37 pending: none red: none` (ev/classify.log). There is no red check, so no `## Red checks` answer is owed.
- RESULT merge: `git merge-tree --write-tree origin/main 0822a4e6...` rc 0, one tree (ev/merge_tree.txt).
- RESULT roles-current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- RESULT re-measured, `bare_array.py --self-test` at the head: `bare_array self-test: ok` (ev/selftest_head.txt).
- RESULT re-measured, `bare_array.py --check` at the head: rc 0, no output, so the empty-line fix holds.
- RESULT re-measured, `bare_array.py --check --ref 154dbb4c` (the base): rc 1. It refuses exactly tick_loop.sh:466, 467 and 468, the three lines the body quotes. This is the fix's own mutant: those are the three `(` the diff adds.
- RESULT re-measured under bash 5, as the orchestrator asked: this container has GNU bash 5.2.21 and no bash 3.2. `bash tools/audit/seat/tick_loop.sh --self-test` at the head gives `tick_loop self-test: 42 checks, 0 failed`, rc 0 (ev/tick_selftest_bash5.log). The `fail closed (func)`, `(bashenv)` and `null control ... no function named exec` rows pass, so the re-parenthesised `case` runs correctly under bash 5. The body's figure under 3.2.57 is 41 checks. I cannot re-derive the 41 or explain the one-row difference.
- Taken from the body, not re-measured (no bash 3.2 here): `/bin/bash -n tick_loop.sh` fails at line 466 at the base and passes at the head. The body's 3.2 differential over the self-test fixtures and 28 snippets, and the run-time deaths of the quoted and backquoted shapes. The 3.2 timing figures. I judged the rule by reading and mutating it, below.
- RESULT re-measured, targeted mutants of the new rule, 14 hand-planted (ev/mutants.txt). 13 are killed:
  - the hit recording removed
  - a led pattern also refused
  - backquotes no longer resetting the substitution
  - `<(` and `>(` not opened
  - double quotes not tracked
  - here-documents not skipped
  - `then`/`do` dropped from command position
  - `;;&` not consumed whole
  - `scan()` dropping `case_sites`
  - comments not skipped
  - `esac` in pattern state ignored
  - the `${ }` close missing
  - `--check` printing an empty line again

  One survives: the backquote removed from `COMMAND`'s command-position set (see Findings).
- RESULT re-measured, a differential of that survivor: `case_sites` original against the mutant over all 109 tracked `*.sh` gives 0 differing files (ev/tree_scan.txt). The only input I found that tells them apart is `` x=$(echo `true`case a in a) :;; esac) ``, which no bash parses.
- RESULT re-measured, the body's balance figures: 109 tracked `*.sh`. 515 `case` words, under my own definition `\bcase\b` (the body names none); it matches the body. `case_sites` hits: none. `bash -n` under bash 5: 0 failures over all 109.
- RESULT re-measured, standing cost on this container: `--check` 0.06 s at the base and 0.34 s at the head. `--self-test` 0.03 s at the base and 0.22 s at the head. The order of magnitude matches the body's 0.7 s per run.
- RESULT CI wiring: `.github/workflows/governance.yml:711-712` runs `--self-test` and `--check` in the existing `bare-array-expansion` step, so the new rule rides that step.
- RESULT step 5: the diff does not touch `VERSION`, the manifest or `RELEASE_NOTES.md`. No golden or claim file moves, so step 4 has nothing to compare.
- RESULT step 14: no budget, closure or ledger moves. The packet's `figure_lint` prints `FIGURES: 3 resolved, 0 not verified, 0 refused`.
- RESULT step 6, class: the class is bash 3.2's paren-counting end of a substitution. The body names its enumeration: `case_sites` across every tracked `*.sh`, plus `bash -n`. I re-ran it and it returns no seam beyond the diff. The body states the uncovered shape, an unbalanced `)` in a here-document or `${...}` inside a substitution, and measures it absent. I can confirm absence only under bash 5's `bash -n`, which does not detect it.
- RESULT step 10: the body's `## Forward-carry` is `none`, and the packet's carry_audit reads 0 items.

## Findings

- Follow-up: the self-test row "case right after a backquote is a keyword" does not pin the fix the body says it pins. Removing `` ` `` from `COMMAND`'s character class survives the self-test, and no tracked script or parseable input I found tells the mutant apart. The fix is equivalent in effect, and the body's "a row pins it" is not borne out. Carry: dismissed: equivalent on every parseable input measured (0 of 109 tracked *.sh differ); it changes no refusal.
- Out of scope: `bare_array.py` scans only `tools/**/*.sh`, but 70 of the 109 tracked `*.sh` lie outside `tools/`, including `.claude/hooks/*.sh`, which run on the owner's host. The class can re-enter there unrefused. That scope predates this diff (triage P303), and `case_sites` over all 109 finds no site today. Carry: dismissed: pre-existing scope of the instrument, no site outside tools/ at this head
