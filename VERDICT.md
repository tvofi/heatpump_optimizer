Fix review: merge d846957a3ca50757e973d03b0bcafcbf0a12808a

bus-nonce: 6a5706449e5c6ef2d43009e1a6e587ba
pending-ci: arch-score / arch-score,budget-raise-gate / budget-raise-gate,codeql / Analyze (actions),codeql / Analyze (javascript-typescript),codeql / Analyze (python),gate,governance / env-matrix,governance / policy-docs,governance / wave-script,hassfest / hassfest,pr-contract / pr-contract,tests / arch-instrument,tests / briefs,tests / browser,tests / closure-scope,tests / closures,tests / coverage,tests / coverage-ratchet,tests / fast (3.14),tests / mutation,tests / typing,validate / validate-hacs

Round 1 (full scope, first round). Measured head d846957a3ca50757e973d03b0bcafcbf0a12808a; it was the PR head at the last read.

## Evidence
- Diff (three-dot): one comment line in .claude/hooks/pre-bash.sh (verdict/3294 -> PR 3294's fix review) plus dev/programme/delivery/3585.md. No executable line moved, so no mutation proof or null control is owed; the body says n/a and that is correct. See ev/diff.txt.
- RESULT bash -n .claude/hooks/pre-bash.sh: ok. RESULT pre-bash.sh --self-test at the head: 46 passed, 0 failed (matches the body).
- RESULT git grep for bare verdict/<N> citations under .claude, tools and dev/governance at the head: remaining hits are tools/audit/carry_audit.py and tools/audit/seat/bus.sh test fixtures about verdict/1, verdict/12 and verdict/3417, none in pre-bash.sh. The body's claim about the closeout pattern holds for the edited line. I did not run closeout.py and cannot say whether those other paths are in its refusal scope; they are not this PR's.
- RESULT merge-tree: git merge-tree --write-tree origin/main head exits 0, no conflict (ev/merge-tree.stderr).
- RESULT VERSION, manifest version, RELEASE_NOTES.md, tests, claim files: untouched by the diff (diff stat is two files).
- Figures: body quotes none; the only count is 46 passed, which I re-derived. Red checks: none owed; the body's "none" stands as no run had concluded red. Forward-carry: none claimed, none owed for a comment-only change.
- CI: classify printed "WAIT d846957a3ca50757e973d03b0bcafcbf0a12808a pending: gate red: none" on every run over about 30 minutes; the head's workflow runs (cancel-superseded, prelude, refresh) were still queued at the last packet render and no required check had started, so no CI result is cited. Hence pending-ci above, for the relay to post once green.
- A stray 40-hex line (36e4fd30...) sits in the PR body under Head; it is not the head and does not affect the verdict.
- Code-owned path (.claude/hooks/): merge needs the owner's approving review, as the body says.
