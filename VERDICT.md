Fix review: merge a5146153e9b5bdbf0bf4bd6248a944bc8c45a47b

bus-nonce: 898903df73cbfb21abe6fe4c8c1e3a51

## Round

First fix review of #2766 (R10-MUTATION-ANCHOR, issue #2493, triage P-L #2632). Measured at head a5146153e9b5bdbf0bf4bd6248a944bc8c45a47b. The head had not moved when this verdict was written. Read from a detached worktree. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` was empty, so the contract copy is current.

## Findings

- P-L is only partly closed. `pin_entry`'s reason no longer carries the base ref, but it still embeds `rc=`/`failed=` of the baseline and kill runs. A bot's pin and a fixer's pin of one mutant measured on different bases can count failures differently (a later base adds or removes checks of the same driver), and then they are still two different files, an add/add conflict. The self-test pins identity only for equal run counts. The triage's fallback (a `ledgermerge` rule that takes the newer when anchor, killed_by and old are equal) would cover this. The PR delivers the fix route the roster states and removes the one field that differs on every such pair. Carry: R10-MUTATION-ANCHOR
- The 30 struck pins are now `survivor_triage` `gap` rows, so 30 sites lose a recorded kill until some driver re-pins them. Each row's reason says so, and the body routes it through the ledger's normal re-pin path. Carry: dismissed: these rows are the honest record of vacuous kills, not a regression, and a later `--pin-killed` or `--drain` kill re-pins them with no further work owed
- One `pr-contract / pr-contract` run at this head (run 40135929853, job 121005631303) concluded failure: `FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s`. The step is `tools/ci/codescan_wait.py`. The other `pr-contract` run at the same head (run 40135930031, started 22:27:05Z, after that red concluded at 22:24:51Z) passed, and `codeql / Analyze (python)` concluded success at 22:27:02Z. That is a CI wait timeout and nothing in this diff caused it. The body's `## Red checks: none` was written before CI ran. Carry: dismissed: a codeql wait timeout not caused by this diff, already superseded by a green pr-contract run at this head

## Evidence

- Merge: `git merge-tree --write-tree origin/main a5146153e` at origin/main 728018c34 (main moved past the PR base 0810d5b8f) exits rc=0, with `LEDGER-MERGE: resolved tests/closures.json` (inert_reads merged as a set). There is no conflict. `ev/merge_tree.txt`.
- The finder's harness at both ends: the climate rewrite `if None is not indoor:` of `climate.py:145`, then `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`.
  - RESULT base 50af6174f + rewrite: `1 of 2425 ENTITY CHECKS FAILED`. The only top-level red is `--anchor re-drives one site ... (R9-F10.13)` with `MUTATION TABLE REFUSED -- the ledger disagrees with the deterministic invent...`, so the finding reproduces.
  - RESULT head + rewrite: `ALL 2428 ENTITY CHECKS PASSED`.
  - RESULT head, no rewrite: `ALL 2428 ENTITY CHECKS PASSED` (6m51s).
  - `ev/entities_bc.txt`, `ev/entities_hc.txt`, `ev/entities_head.txt`.
- Mutation proof, re-taken through the full `tests/entities.py` at head (not a scratch block driver):
  - M1 as the body states it (all of `tests/mutation_table.py` back to 50af6174f) cannot run through the full script. The script crashes at module level on the P-L signature change (`TypeError: pin_results() missing 1 required positional argument: 'ref'`, entities.py:35785) before it reaches the anchor block. So the body's M1 figures come only from its scratch driver, which I did not re-run. I re-took M1 narrowly as `invalidated_rows` returning `[]`. RESULT: `2 of 2428 FAILED`, namely `a re-driven pin is not reproduced by a driver that only sees the row the mutant made stale ...` and `invalidated_rows names exactly the rows pinned to a rewritten line ...`.
  - M2: the `for p in rows: p.unlink()` pair in `drive()` deleted. That pair is one `p.unlink()` line plus its loop header; the body calls it "two `p.unlink()` lines". RESULT: `1 of 2428 FAILED`, `a re-driven pin is not reproduced ...`. Matches the body.
  - M3: `_mut_anchor`'s one-row stub reverted to the whole live ledger, on a tree carrying the climate rewrite. RESULT: `2 of 2428 FAILED`, `--anchor re-drives one site ...` and `a re-driven pin is not reproduced ...`. Matches the body.
  - M4: `pin_entry`'s reason given back `against {_rev(ROOT, 'HEAD')}`. RESULT: `1 of 2428 FAILED`, the P-L byte-identity check. Matches the body.
  - Mutant diffs are in `ev/mutant_*.diff` and results in `ev/entities_m*.txt`.
- Null control, my own sample: the first six `killed_by: tests/entities.py` pins with no second ledger row, ordered by sha1 of the anchor. The body's exact `nullpins` selection is not committed. Driven at head with `r10_anchor_vacuous.py --drive --jobs 2 --anchor ...x6`, each pin's row hidden (`hidden rows 1`), against two green baselines (`rc=0 failed=0`, 418 s and 415 s). RESULT: `DRIVEN 6 pin(s): 6 kill(s) survive the fix, 0 vacuous`. The harness's `checks` field also catches nested sub-run FAIL lines, which is cosmetic: the top-level kills were `failed=1` or `failed=2`. `ev/nullpins.txt`, `ev/nullpins_drive.txt`.
- Census, re-derived with my own script (`ev/second_pin_census_base.txt`) at the merge base 0810d5b8f:
  - 175 pins, 52 on a line carrying a second row, 5 on a line with a `survivor_triage` row, 49 on a line with a second `killed_by` row. All four match the body.
  - The harness census reads `175 ... 52` at the merge base and `145 ... 22` at head (`ev/census.txt`).
  - The finder's grep reads 175 at 50af6174f, 175 at 0810d5b8f and 145 at head.
  - The diff deletes 30 `killed_by` files and adds 30 `survivor_triage` files of the same names. The sample row I read keeps the anchor and `old`, has verdict `gap`, and quotes the old reason.
  - I did not re-run the 52-pin `--drive` measurement (22 survive, 30 vacuous) or the 9-pin re-drive. Those figures are the fixer's, stamped at 0be5e2de5 and 3deb7cb89.
- Class (step 6). The rule: every path in `tests/mutation_table.py` that writes a mutant into a worker tree and runs a driver. There is one, `main()`'s `drive()` (`path.write_text(mutated[...])`), and it serves the nightly, `--anchor`, `--pin-killed` and `--drain`. `run_baseline` writes nothing. `run_null` writes a comment-only line (`null_control` picks a line holding only a comment), which carries no site and so no row. `tools/audit/seat/verify_eight.py` writes mutants for `tests/features.py`, outside the ledger lanes. Every seam this rule returns is in the diff. The pool passed to `drive` is filtered to `id(m) in mutated`, so `hidden[id(mut)]` always exists.
- Claim files: `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are not in the three-dot diff. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched; CI's version-edit step agrees ("moves none of VERSION, the manifest version or a notes heading").
- Cheap checks at head: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`, and `tests/layout.py` printed `layout self-test: ok`.
- P-L sha readers: no reader of a pin reason's sha exists in `tests/mutation_table.py`, `tools/merge/ledger_merge.py`, `tools/pr/*.py` or the workflows (grep at head).
- Cost: `invalidated_rows` re-parses the file twice per mutant and does not cache the `before` set. I measured 0.58 s per call on `coordinator.py` (1155 sites). That is small next to a ~415 s `tests/entities.py` driver run. This is evidence only, not a defect.
- Harness provenance (step 9): `dev/audit/harnesses/r10_anchor_vacuous.py` is added by this PR, so it is the fixer's instrument. The brief names it the finder's. The finder's literal control, the climate rewrite through `tests/entities.py`, is what I ran at both ends above.
- CI at this head: all 53 check runs have concluded. All are success or skipped except the one `pr-contract` timeout under Findings. `tests / mutation`, `gate`, `tests / closures`, `tests / fast (3.14)`, `arch-score` and `budget-raise-gate` are all success. I did not open the mutation lane's log: the diff writes no production code line, so `changed_lines` draws no mutant from it.
- Forward-carry: the body states none. No finding in this PR changes a later stage's brief.
