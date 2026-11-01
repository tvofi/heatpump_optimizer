Fix review: merge 3602d1b64c88a947c7f5e815fff15b46a6c4c496

bus-nonce: 6a3d761828097b6c3e0d4717eb8947e2

## Round

The re-cut round after the block of 50694d12d. verdict/3049 holds 4 blocked verdicts (87abaed68, a7e6a3e5d, 16cb22f64, 50694d12d), so by that ref this is round 5, which is also the body's count. My brief says "after the fifth block"; I could not find a fifth blocked verdict, and I report the gap rather than resolve it. Measured head: 3602d1b64c88a947c7f5e815fff15b46a6c4c496, the PR head when the check runs were read. It merges code head 2f97d5701 and then origin/main e4c9e2016. The roles diff from the merge base to main is empty, so this contract is current.

## Findings

- The body's heading is `## Re-cut note`, not `## Re-cut`. `tools/audit/seat/bus.sh` three_rounds() greps `^## Re-cut[[:space:]]*$`, and that grep refuses this line (re-run here: NOMATCH). This dispatch went out with 4 blocked rounds, so it needed `--past-three` and the heading gated nothing this time. Even so, the re-cut form fixer.md asks for is not met to the letter. The fix is a body edit that leaves the head where it is: rename the heading to `## Re-cut` before the merge. Carry: R10-FLY-GH-CALL-LOG

## Evidence

- Last block, re-run with the finder's harness, exported from origin/verdict/3049 (finder-probe.sh, finder-probe2.sh, probe3.sh) under `env -u BASH_ENV`. Count rule: lines starting LEAK.
  - Shim from 50694d12d: probe 2, probe2 0, probe3 2.
  - Shim at this head: probe 2, probe2 0, probe3 0.
  - The two probe3 rows `python3 -X "importtime LEAKVAL" c.py` and `python3 -W "ignore LEAKVAL" c.py` now log `python3`.
  - The 2 left in probe are the disclosed residuals: `sh ./GH_TOKEN=abcLEAKVAL/script` and the `bashLEAKVAL` argv[0] symlink.
  - NOLINE counts are unchanged at both ends (1/1/4); those shapes never call gh.
  - These match every figure in the body's Figures bullet (ev/harness-both-ends.txt).
  Carry: dismissed: evidence, not a finding
- My own hunt, ev/probe4.sh, 24 shapes. It is my instrument, not the finder's.
  - Shapes: shebang-packed `-X`/`-W` values, `env -S python3 -W ...`, script paths containing a space, `-X'a LEAKVAL'` glued and spaced, a symlinked `python3.99` and an unlisted `pythonw`, `perl -mM`, `bash -m`, `python3 -E -s -c`, `sh -vs`, and gh-side `-H`/`--header=`/`-f`/`--body`/`?query` values.
  - Old shim: 3 LEAK. This head: 0 LEAK. The 3 old leaks act as the null control for this harness.
  - A script path containing a space is logged cut at the space (`python3 d`), as the header states. `-s` on python ends the field as a stdin-script letter, also as stated.
  - I found no shape that reaches the parent field beyond the disclosed argv[0]/script-path residual.
  Carry: dismissed: evidence, not a finding
- Docs: the shim header, instruments/shims_seat-gh.md and the body each state the rule the code runs. A value-taking letter (python -W/-X, shell -o/-O) ends the field unlogged. `c`/`e`/`s` log the option up to the letter. `--eval`/`--print`/`--command` log the name only. Any other option ends the field. `-m <module>` and the first non-option word are logged. I found none of the three claiming more than the code does.
- Self-test at this head: `gh_calls self-test: 84 checks, 0 failed`. I counted 84 ok/FAIL lines; one arm skips because the run is as root. This re-derives the body's figure.
- Failing first: the head's gh_calls.py with the 50694d12d shim gives `84 checks, 8 failed`, as the body says.
- My textual mutants, run through the self-test (ev/mutants-head.txt):
  - Old skip restored: KILLED, 8 failed.
  - Value letter read as a no-value letter: KILLED, 7.
  - Value letter logs the next word: KILLED, 8.
  - python vals emptied: KILLED, 1, by the textual mutant arm.
  - `$vals` line deleted: KILLED, 1.
  - Shell vals emptied: survives. That mutant is behaviour-equivalent: o/O are not in the shell flag set, so they fall to the end-unlogged arm either way.
  - All 17 of the self-test's own mutant arms read killed.
- Standing checks (ev/standing.txt):
  - seat_venv self-test: 21 checks, 0 failed.
  - `ALL 2497 ENTITY CHECKS PASSED`.
  - `STRUCTURE RATCHET PASSED`.
  - `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - VERSION, RELEASE_NOTES.md, the manifest and both claim files are untouched in the three-dot diff, and the claim files are byte-identical.
  - The delivery row dev/programme/delivery/3049.md is in the three-dot diff.
- Merge with origin/main 1d28de993: `git merge-tree --write-tree` rc 0. `LEDGER-MERGE: resolved tests/closures.json` appears; no MERGE-CLAIM line, because the claim files did not conflict.
- Re-cut form, apart from the heading finding above: the body carries every template heading (Head, Mutation proof, Null control, Figures, Red checks, Forward-carry, Friction). Its figures are re-taken in this pass, and the round history is cut down to the one block it answers.
- Check runs at this head, all 53 on one page, read live:
  - None concluded failure.
  - `governance / instrument-self-tests` and `codeql / Analyze (python)` are success.
  - `pr-contract` is success, started 16:26:56Z after every run concluded red on earlier heads.
  - `governance / instrument-self-tests`, red on an earlier head, is named and answered under the body's Red checks.
  - The body's CodeQL clause ("no check has run yet") was written before the push. At this head CodeQL is success; the clause names no red that is still owed.
- CI wait: `merge_train.py classify 3602d1b64c88a947c7f5e815fff15b46a6c4c496` -> rc 0 `GREEN 3602d1b64c88a947c7f5e815fff15b46a6c4c496 pending: none red: none` at 16:37:10Z (ev/ci-classify.txt).
- Forward-carry: the body says none. A shim and reader confined to the seat change no later stage, so none is owed.
