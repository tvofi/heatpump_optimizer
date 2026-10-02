Fix review: merge eff1a2a370d258c14a294914e2d8ffdc63b6bf16

PR #1820, R9-PROC-3, round 2. This review judges the delta e95150fa..eff1a2a3, which is a fast-forward of 2 commits touching prepr.sh and cloud-setup.sh. Body: handoff-body/r9-proc-3 @ 3794342b. Its `## Head` names eff1a2a3, and it answers round 1 at line 24.

## Round-1 findings, re-checked at the new head

1. **The refusal could be bypassed through a merge. Fixed.** `transport_in_ancestry` now runs `git log --full-history -c`. I re-ran my round-1 probe against the head's function (`probe_results.txt`):
   - A body written in a merge's own resolution is refused, rc=1 at both bases.
   - The null control passes: main carries a transport file, the branch merges it cleanly, and the fresh base gives rc=0.
   - The two new self-test rows encode these same two shapes.
   - Mutants (`mutants.txt`):
     - `-c` → `--no-merges` is killed: "a body written in a merge's own resolution is refused", 145/1.
     - `-c` → `-m` is killed: "merging a main that carries a transport file passes (null control)", 145/1.
   - The head's self-test prints 146 passed, 0 failed (`selftest_head.txt`).
2. **The setup script installed the wrong Python. Fixed.** PYVER is now read at run time from `tests/typing_budgets.json` `census.environment.python`, which is 3.14.7 at this head. The assert compares against that value, so no version is restated in the script. The fixer re-ran it end to end: rc 0, and real Home Assistant passed 61/61 on 3.14.7 (body lines 57-58). I did not re-run the install, per the review rules. `bash -n` passes. `/mnt/project-files/audit-r9/cloud-setup.md` is byte-identical to the script at this head.
3. **The ruff removal ran after the early exit. Fixed.** It now sits above the guard. I ran the head script with `HPO_REPO=/nonexistent` and a stub `ruff` first on PATH: it exited 0 with the no-checkout warning, and the stub was removed. Side effect: I did not set `HPO_KEEP_RUFF`, so this container's own `/root/.local/bin/ruff` was removed as well. That is harmless, because this container is ephemeral and ruff was only feeding the tree-rewriting hooks.
4. **The self-test trigger missed two imported modules. Fixed.** `counts.mjs` and `render_md.mjs` are now named in `selftest_inputs`, and a self-test row checks each one. The body says that deleting that line leaves an equivalent mutant (146/0), because `selftest_inputs` derives every script path named anywhere in `prepr.sh`. I accept that explanation: the trigger still works, and the row records the intent.

## Non-blocking

- `orchestrator.md:146` still says "seats LOCAL-ONLY". PROC-1 owns that, by the coordinator's note.
- The script now reads PYVER with the image's `python3` under `set -e`. If the key ever disappeared, the setup script would fail loudly rather than fall back. That is a fair trade for a value that must not drift.

CI was not re-run, per the review rules. The merge still owes green CI at the PR head and tvofi's code-owner approval (prepr.sh and fixer.md are code-owned and policy).
