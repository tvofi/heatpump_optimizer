Fix review: blocked e2255027ecc58d2a3eb3e945045899bec4a52f59 class-open: brief_lint.mjs checkPathLine reads a pin whose quoted anchor is gone as moved when an incidental identifier in its clause sits once in the file, and --repin rewrites it to that line

bus-nonce: d637753107b17ee336c87834911c0537

Round 1 (first review of this PR; no --reviewed-head).

## Block

The body states the rule as "An anchor at several places, or gone, stays an error and is never rewritten", and the same PR adds that sentence to `dev/governance/rules/brief-citations.md` item 2. `checkPathLine` at this head does not hold it. It sorts every candidate by length (the quoted phrases, keywords and snake_case symbols `anchorCandidatesFor` pulls from the 220-character clause window) and returns on the first one found anywhere. So when the quoted phrase, the anchor the brief actually cites, is gone from the file, a shorter incidental symbol from the same clause that sits once in the file decides: the pin becomes a warning, and `--repin` moves it to that symbol's line. After the re-pin the brief lints with no error and no warning, while the phrase it quotes is cited at a line where it is not.

Reproduced at this head (`ev/repin_gone_anchor_probe.txt`). The roster brief is `See tools/pr/figure_block.py:5 "this cited phrase is gone from the file" which bounds timeout_s.`, and the quoted phrase has 0 occurrences in the file:
- head `node tools/policy/brief_lint.mjs <roster>`: `WARNING [P] path:line: tools/pr/figure_block.py:5: 'timeout_s' moved from tools/pr/figure_block.py:5 to line 138, its one place in the file`, `TOTAL: 0 error(s)`.
- base (63c6d1cff9) linter on the same file: `ERROR ... 'timeout_s' not found near tools/pr/figure_block.py:5; found at line 138 instead`, `TOTAL: 1 error(s)`. The change turns this error into a pass.
- head `--repin`: `1 pin(s) rewritten`, brief now `tools/pr/figure_block.py:138 "this cited phrase is gone from the file"`; re-lint: `TOTAL: 0 error(s)` with no finding at all.

`assertRepin`'s arm `an anchor that is gone is an error` covers only a context where no candidate is found anywhere. It never builds a gone quoted phrase next to a symbol found once, so the predicate's unguarded domain is exactly the case the rule names. What the re-cut needs: when the clause carries a quoted phrase, the phrase alone decides moved, ambiguous or gone, and a symbol must not stand in for a missing phrase. Add an `assertRepin` arm for this shape, plus its mutant in `r11_shared_files_p2_mutants.sh`. In the same code, class 2b's re-pin computes its range end as `Math.max(to, to + (end - start))` without the `Math.min(lines.length, ...)` clamp that class 2 uses (`movedTo.end`), so an anchored range can be re-pinned past the end of the file. Use `movedTo.end` in both.

## Evidence

- Mutation proof, re-run in a detached worktree at this head:
  - `bash dev/audit/harnesses/r11_shared_files_p2_mutants.sh`: `RESULT killed=16`, `RESULT survived_or_stale=0`, rc=0 (`ev/p2_mutants.txt`).
  - `python3 dev/audit/harnesses/claim_merge_mutants.py`: `RESULT killed=21`, `RESULT survived=0`, `RESULT stale=0`, rc=0 (`ev/claim_merge_mutants.txt`).
- Finder's instrument, `dev/audit/harnesses/claim_merge_census.py`, with the driver at origin/main (= merge base 63c6d1cff9) and at this head (`ev/census_base_driver.txt`, `ev/census_head_driver.txt`):
  - Base: `RESULT resolved=6 refused=6`. Head: `resolved=9 refused=3`.
  - Exactly `st:d7d4c511b`, `st:fb5658f13` and `st:f919d224` move from refused to resolved. `st:2d010b091` stays refused under both drivers, and the seven older rows are identical. This matches the body's Figures.
- Cheap checks at head (`ev/cheap_checks.txt`):
  - `figure_block self-test: 21 checks, 0 failed`.
  - brief_lint: `REPIN ok`, the W1-G14 fixture pin a WARNING at line 23115-23135. The body says 23114; the one line is from the main merge in 458beb455f.
  - `policy_lint`: `TOTAL: 0 error(s) across 58 policy file(s)`, `FIXTURE ok`. `RULES-SYNC ok`.
  - Agreement: `pair stored-figure-block: 2 readers, 39 items, 0 divergent`, `AGREEMENT ok`.
  - `STRUCTURE RATCHET PASSED`. `doc_claims ALL 441 checks PASSED`. `closure.py select`: `MODE: SCOPED -- 7 script(s) run, 26 scoped out`.
- `git merge-tree --write-tree origin/main e2255027ec`: rc=0, no conflict (`ev/mergetree.txt`). The PR base 63c6d1cff9 is current origin/main.
- `VERSION`, the manifest version and `RELEASE_NOTES.md`: untouched in the three-dot diff.
- `dev/governance/roles/` is unchanged on main since the merge base.
- `tests/env_drift.py` `_stamp_emptied_side`: read against the body's stated rule. It is keyed on which side moved the stamp, a removed stamp (`None`) keeps the refusal, and its five mutants S1-S5 are killed. No defect found.
- CI on this head: `merge_train.py classify e2255027ecc58d2a3eb3e945045899bec4a52f59 --pr 3837` printed WAIT (rc=3) from 20:21 to 20:29Z, then at 20:30:32Z rc=2: `REFUSE selftests: the head's governance / instrument-self-tests job 136973463090 concluded cancelled, which reads no step: re-run it`. The CI state is unreadable at this head (`ev/classify.log`). The block above stands on code and does not turn on it.
- The PR head re-read before return: `refs/heads/fix/r11-pre-shared-files-p2` = e2255027ecc58d2a3eb3e945045899bec4a52f59, unmoved.
- I wrote the probe roster, not the finder. It is a scratch JSON fed to the in-tree linter, and its full text is in the evidence file.
