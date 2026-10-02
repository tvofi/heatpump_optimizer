Fix review: merge c4311a4629a88260a16eb49db4ae8616db671b7e

bus-nonce: d709ae45416fa0e8debd08f8d64c6740

This is a delta review, round 4, of the main merge into #1847. The verdict is merge, with `policy-docs` red as ruled. tvofi ruled on 2026-10-02 that `policy-docs` is the accepted bootstrap red on #1847, merged past with `--admin`.

- Previous verified head: 1517fa2d (my round-3 merge verdict).
- Measured head: c4311a4629a88260a16eb49db4ae8616db671b7e. I re-read the live head before posting and it was unchanged.
- Main: 2e7422e5. #1850, the precursor, merged at bf37bd3a, and #1853 merged at 2e7422e5.

## The merge is git's automatic result

c4311a46 has parents 1517fa2d and 2e7422e5. Its tree is a75e6004. `git merge-tree --write-tree 1517fa2d 2e7422e5` exits 0 with no conflict and writes the same tree, a75e6004. No hand resolution is present.

## The remaining diff is the verified diff minus exactly the precursor

- Branch diff before: `aab94eea..1517fa2d`, 15 files. Branch diff now: `2e7422e5..c4311a46`, 13 files (`old_files.txt`, `new_files.txt`).
- The two files that left are exactly `.claude/workflows/check-wave-script.mjs` and `.claude/workflows/policy_lint.mjs`. Their blobs are the same at 1517fa2d, at the precursor 07b0704b, at main 2e7422e5 and at c4311a46: 510411b4 and 17e61d73 (`precursor_blobs.txt`). The branch's content in them was the precursor's, and it is now main's.
- For the other 13 files, the old and new patches are byte-identical with `index` lines excluded (`patch_compare.txt`, `cmp` rc 0).
- Main's other movement since aab94eea is outside the branch's files: optimizer.py, `structure_budgets.json`, two mutation-ledger pins and delivery rows. My checks at this head:
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - Census arm: ok.
  - Agreement lane: `divergent=0 ... refused=0`.
  - Lane self-test: 13 of 13.

## CI at this head (`checks_final.tsv`, commit check-runs API, background watch until every run completed)

`policy-docs` is the only red. Its only refusal is the bootstrap, the same as at 1517fa2d: base-pinned `field_coverage.mjs` gives `REFUSED registry: pinned agreement.mjs / agreement_py.py / tests/structure.py`, `refused=3` (`ci_policy_docs.txt`).

`wave-script` passed: `check-wave-script` 153 passed, 0 failed, so main's copy now carries the precursor's group 15. `agreement lane: the base does not carry it ... skipped`, as expected, since main still lacks `agreement.mjs`. `SELF-TEST 13 of 13` (`ci_wave_script.txt`).

`pr-contract` passed. `fast (3.14)` passed (it carries `tests/entities.py` and `tests/harness_headers.py`). Every other completed run passed or was skipped. The one cancelled `pr-contract` run and the one cancelled `budget-raise-gate` run were each superseded by a later run of the same name that succeeded.

Evidence: `evidence/`. `HEAD.txt` names the head.
