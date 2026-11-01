Fix review: merge cae73963448dc1f660a70797a55372fdac19a243

bus-nonce: ad9fdc28710a4cd101f6fd8aaff776af

Round 1. Head measured: cae73963448dc1f660a70797a55372fdac19a243 (still the live head per /pulls/3072). Detached worktree at that SHA.

## Findings

None. Every check below held.

## Evidence

- Harness self-test at the head: `r10_row_head_carry self-test: 8 checks, 0 failed`. The null control reads +3330 on a pair where P ran to completion, so the harness can read a carry that pays.
- Live re-run with my own credentials (`--since 2026-10-28 --limit 40`, ev/harness.txt). The live window has moved on since the body was written, so it covers #3024..#3071, not #3008..#3043, and the exact body figures (13631 / 74900 / -61269) do not reproduce. I did not re-derive them. The conclusion reproduces on the newer 40 pairs: gain 25514 s, loss 73650 s, net -48136 s, median net -1905 s/pair, only 4 of 40 pairs positive. P's code run was cancelled in 39 of 40 (the body says 40/40, and one P was a failure here). Median gap between the two heads' first code runs is 16 s, max 47 s, against the body's 15 s and 37 s. The census also differs: row+other 4 (matches), other 1289, row-only 153 against 1119 and 131 in the body, because the window is larger. The positive pairs are P runs that ran long, which is what the null control predicts.
- The body's "8.6%" for arm (b) is 34376/398267 = 0.0863. The arithmetic is right. I could not re-derive its two inputs at the live window, so I checked only the division.
- Carry 3: the new tests.yml comment ("a run's work to its last `tests / *` job with runner queue removed (see tests/ci_ratchet.py run_minutes; U9a)") matches the run_minutes docstring ("critical path with every runner wait removed").
- Carry 4: `body_patch.sh --self-test` reads 91 checks, 0 failed. The three named mutants (titlereadback, titleshape, titlecontract) report ok, i.e. caught. I planted two of my own, and each was caught by the self-test:
  - Skipping the expected-head equality check: the self-test fails on 'naming the reason' and others.
  - Sending a body field alongside the title: the self-test fails on 'the live body is the body file's exact bytes' (got 'x') and others.
  The file was restored and `cmp` against the original is identical.
- Delivery rows: the diff changes only the title text of `dev/programme/delivery/2846.md` and `2844.md`. #2844 has 9 `roster_edit` commits in `21b4552^1..21b4552^2`, so "9 ops" is true. The owed-action commands name `569849cf18f65ef58a45e85036d4e0544d79f1bc` for 2846 and `9dc2d96330e520e08b2918dd01f58e7d4ffa8a7e` for 2844. `/pulls/<n>` reports exactly those heads, and the live titles still read the old text. This is an owed orchestrator action before merge (each first with `--dry-run`), not a defect. I did not re-run the P184-P191 / V104-V111 figures against the triage record; the row regeneration through `record_row.row_line` is covered by the body_patch round-trip self-test.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 with no conflicts.
- The three-dot diff of VERSION, RELEASE_NOTES.md, tests/golden (both claim files included) and the manifest is empty. `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED. The new harness has an entry in the tests/closures.json inert list. The packet shows 0 refusals, 0 advisories and `CARRY-AUDIT: 0 finding item(s)`.
- CI: `merge_train.py classify` exits 0, GREEN, nothing pending or red. The gate MODE is FULL because tests.yml changes the gate itself, as stated. I did not re-run the gate or the mutation lane, per the contract's rule to cite CI's heavy runs.
- Premises I did not check in code: that `tools/ci/gate.py` would read results from another head under a carry, and that GitHub cancels a whole run. The measurement supports the "not needed" ruling without them.
