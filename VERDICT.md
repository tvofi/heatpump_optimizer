Fix review: merge aaa846f0e2ea3a803b238135581c75cbb7f816be

bus-nonce: 4bc8331818574a2b3525d0cc0c56dbb6

## Round

Round 2 (round 1: `blocked 33660280381756f968ee197f374e9254eecfde19 countermeasure-silenced`). Measured at head `aaa846f0e2ea3a803b238135581c75cbb7f816be`, which was still the PR head when this verdict was written. Its tree equals the authored code head `40cf99db4` (`git diff --stat 40cf99db4 aaa846f0e` is empty), and `fix-review.md` is unchanged between the merge base and origin/main.

## Findings

- A surviving mutant in the acknowledgement-cover predicate. In `tools/audit/seat/owed_unactioned.py:193`, changing `(a[0] == "-" and not ids)` to `(a[0] == "-")` passes the self-test (29 of 29). The mutated tool would let an `OWED-ACK <t> <key> -` line cover a key whose lines carry a sha, so the cover would not be tied to a tip. The production line is correct at this head: attack A in `ev/attacks.txt` returns rc=1 and 0 acknowledged. Only the self-test pin is missing. Carry: dismissed: production behaviour verified correct at this head (ev/attacks.txt A); this is a missing pin, not a defect, and is a one-check addition for whoever next edits the tool
- Surviving mutants in the state-entry validation (`owed_unactioned.py:159-166`). All four pass the self-test 29 of 29: dropping the `keys` dict check, dropping `sweeps >= 1`, dropping the bool exclusion, and dropping the `utc(e["first"])` parse. The body says a state entry with a bad type is `UNREADABLE`, exit 2. That behaviour holds: attacks F, G, H and I in `ev/attacks.txt` each give rc=2. Only the missing-key case is pinned, by the round-1 `KeyError` mutant. Carry: dismissed: behaviour verified at this head (ev/attacks.txt F-I); missing pins, not a defect
- The `governance / instrument-self-tests` check on this head concluded `cancelled`. Its job hit its `timeout-minutes: 20` at 21:07:00Z, inside the step `Show the CI predictor (tools/pr/ci_predict.py) ...`, which this diff does not touch. The PR's own new step (38, `Show the owed-line reader ...`) concluded success in about 1 s. The job's total step time was 893 s on main `b6f6ceca4`, 1192 s on round 1 `336602803` (8 s under the cap, passed) and 1212 s here. The extra time is spread across untouched steps (`ev/step-deltas.tsv`: the pre-PR self-check +90 s, ci_predict +71 s). The job is running near its 20-minute cap, and this head needs one re-run of that job before it merges. Carry: dismissed: not this PR's (the timeout is in steps the diff does not reach, and the new step passed); the merge train re-runs the job once before merging, and the job's headroom against its cap belongs to whoever owns governance.yml's timeouts

## Evidence

- Self-test: `python3 -I tools/audit/seat/owed_unactioned.py --self-test` gives `29 checks, 0 failed` (`ev/selftest.txt`).
- The PR's mutation proof, re-run with `python3 -I dev/audit/rca/owed-unactioned/mutants.py .`: 15 mutants, 0 not killed. The per-mutant red counts match the body's table (`ev/mutants.tsv`). The "malformed state entry" mutant is killed by a `KeyError` crash, which is what the body says.
- My own targeted mutants (`ev/reviewer_mutants.tsv`): 14 planted. Eight were killed: an expired ack counted as live, a future ack accepted, the pid id dropped, whole-id equality dropped, the stale-board check, the ack line no longer anchored (the round-1 blocker), fires one sweep late, and the ref key not stripped. Five survived; they are reported under Findings O1 and O2. The naive-time mutant also survived, but it does not change behaviour on a UTC host, so it is not a finding.
- Attacks on the production tool (`ev/attacks.txt`):
  - echoed `ack:` line: refused;
  - 6-character id prefix: refused;
  - 7-character prefix: covers;
  - `ttl=nan`: refused;
  - expired acknowledgement: does not cover;
  - Markdown list-item ack: covers, as documented;
  - a long id whose first 12 characters match: covers, which is a 12-hex collision only.
- `live.sh` re-run with two empty ack files, matching the body's "0 OWED-ACK lines" (`ev/live_rerun.txt`): the output is byte-identical to the committed `live_out.txt` apart from the two ack-file name lines. That covers 12 keys, then 12 unactioned, then 0 under the null control, and 12 unactioned on the echo control with exit 1.
- Figures re-derived at this head (`ev/figures.txt`):
  - 26 owed-family lines, of which 8 are shown by `tail -8`;
  - `selftest_wiring`: 100 self-testing, 100 wired;
  - `sweep_render` self-test: 21 checks, 0 failed.
- Figures I could not re-derive, because their inputs are session files outside the tree (`orch-sweep.log`, `cloud-relay.log`, the session transcript, `~/.local/state/hpo`):
  - the night replay, 30 of 31 exit 1, mean 5.6;
  - the owed block at line 56 of 65;
  - 19 reads, 15 of which drop the owed block;
  - 33 `HELD-REVIEW` passes;
  - `disposed=2`;
  - 0.08 s per run.
  These are not verified by me. `figure_lint` resolves all 7 commands at this head.
- Merge: `git merge-tree --write-tree` exits 0 against origin/main `b6f6ceca4` and against the newer origin/main `b0b2d7697` (tree `7b855b54b`). There is no conflict and no claim-driver involvement (`ev/merge-tree.txt`).
- VERSION, the manifest version, `RELEASE_NOTES.md` and both claim files are untouched in the three-dot diff. pr-contract prints "no version edit".
- The new file is classified: `owed_unactioned.py` is added to the `tests/closures.json` INERT READS list. `tests/structure.py` prints STRUCTURE RATCHET PASSED. `rules_sync.mjs --check` is ok. Local `tests/entities.py` could not run under the container's Python 3.11 (an f-string syntax error that is the interpreter version, not the diff), so CI's `tests / fast (3.14)` success stands for it.
- The `sweep_template.md` step (5) edit uses only placeholders main already defines (`{{tick_log}}`, `{{orch_scratch}}`, `{{seat_ledger}}`).
- CI at this head, from the check-runs API (`ev/check-runs.tsv`): 37 success, 17 skipped, 1 neutral (the CodeQL summary), and 1 cancelled (`governance / instrument-self-tests`, Finding O3). No check concluded failure.
- pr-contract ran twice after the cancel concluded: at 21:26:12Z and 21:29:19Z, both success on this head (`ev/pr-contract.tsv`). Its log prints "red-history ... every failure conclusion across them: none", "PR-BODY: 0 error(s)", "FIGURES: 7 resolved" and "CARRY-AUDIT: 0 finding item(s)". Under `fix-review.md` step 11, that green run is the evidence that the body was checked after the last non-green conclusion. The body's `## Red checks: none` agrees with it.
- The `tests / mutation` lane is green. It draws no mutants from `tools/audit/seat/` in practice, so the targeted mutants above are the evidence.
- Step 6 (class): this is an RCA record, not a harness-scoped fix. The record's section 4 enumerates the class's reach. Each item outside the diff is dispositioned in the body as the orchestrator's (the `orch_sweep.sh` fold, the split ledger home) or as V179's. No seam is left open.
- Step 9: the finding has no finder's harness. The instruments are the fixer's own (`replay.py`, `live.sh`, `mutants.py`), and the body discloses them as in-tree evidence scripts.
- Step 10 (forward-carry): the body says none. The orchestrator-owed session changes are stated in the body and live outside the tree.
- Owner review: `.github/workflows/governance.yml` is code-owned, so `@tvofi`'s approving review is still required at merge.
