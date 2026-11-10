Fix review: merge 18b19b658171d7918b373b789077f470b113957a

bus-nonce: 1ad18c46dfdc440acc3758dd7d90c90f

## Summary

Round 1 (no earlier probe/rev-3406-* ref). Measured head 18b19b658171d7918b373b789077f470b113957a, still the PR head when the verdict was written (ev/HEAD.txt). Merge base 5ab6030d70680830817791707e7c7be1a7b09e11. This is the merge base the review packet names. The body measured at 9b1bb58db7, and every figure I re-took at 5ab6030d agrees with the body's to within 0.01 MiB. The fix is a measurement fix in tests/stress.py: before the traced window, the probe and the empty probe both rebuild the interned-string table, so a solve's three interns can no longer cross a rebuild inside tracemalloc. The memory pass adds a fill perturbation with its own null control, and both checks run on every gate pass. No budget, claim file, VERSION, manifest or notes heading is touched.

## Evidence

- CI: `merge_train.py classify 18b19b658171d7918b373b789077f470b113957a --pr 3406` exited 0: `GREEN 18b19b658171d7918b373b789077f470b113957a pending: none red: none` (ev/classify.txt). `merge_train.py owed-reds` set: ev/owed-reds.txt. None of those checks is red, so no `## Red checks` answer is owed, and the body's "none" is correct.
- Merge: `git merge-tree --write-tree origin/main 18b19b658171d7918b373b789077f470b113957a` exited 0 (ev/merge-tree.txt). `LEDGER-MERGE: resolved tests/closures.json` is a set merge, not a conflict.
- Role currency: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Step 1, mutation proof, driven through the head's own `intern_fill_readings` and the two checks' predicates exactly as the memory pass applies them (ev/fillcheck_driver.py, my own driver), on typical_slab/winter, 2 runs each:
  - Head, unmutated: `clean=3.30 filled=3.30 bare=6.97 perturbation_lands=ok independence=ok` in 2 of 2 runs (ev/fillcheck-head.txt).
  - M1 is the PR's named mutant: the headroom call in `_memory_probe_main` is deleted (ev/mutant1.diff). Result: `filled=6.97/6.96 vs clean=3.30 independence=FAIL` in 2 of 2 runs (ev/fillcheck-mut1.txt). Killed.
  - M2 is my own mutant: the `--intern-fill-short` fill becomes a no-op (ev/mutant2.diff). Result: `bare=3.30 vs clean=3.30 perturbation_lands=FAIL` in 2 of 2 runs (ev/fillcheck-mut2.txt). Killed, so the null-control check is not vacuous.
- Step 2/9, harness: none was committed by a finder. The finding came from CI job 129554889319's log. The harness is the fixer's own, dev/audit/harnesses/r10_stress_intern_fill.py, which the PR lands and discloses as "the harness behind the figures". I ran it at both ends.
- Step 3, null control at both ends, edge mode on typical_slab/shoulder (ev/edge-*.txt):
  - Base: `short=1 traced_mib=5.72` and `short=50 traced_mib=2.06`.
  - Head: `short=1 traced_mib=2.06` and `short=50 traced_mib=2.05`.
  - Body: base 5.72/2.05, head 2.05/2.04. Agrees within 0.01.
- Step 6, other configurations, edge at 1 short (ev/edge2-*.txt):
  - heavy_old/shoulder: base 6.99, head 3.32.
  - winter_extreme/2z/dhw: base 6.99, head 3.33.
  - Both are fixed at the head and match the body's clean 3.33/3.34.
- Step 6, class: `git grep -n "tracemalloc.start" -- tests dev/audit` at the head returns 13 sites (ev/class-grep.txt). Each is the new harness, stress.py's two sites, replay.py, or a round harness the body dispositions.
  - The replay seam re-measured at the head: `RESULT replay fixture=synthetic-dhw-only.json memory_cycles=24 slots=[0] total=0` (ev/replay-head.txt), as the body states.
- Step 4/5: three-dot name list has 4 files: the harness, delivery/3406.md, tests/closures.json and tests/stress.py. No claim file is touched. The diff has no production code and no fixture, so env_drift has nothing to move. VERSION, the manifest and the RELEASE_NOTES heading are untouched.
- Step 7: the body's `## Head` names 18b19b658171d7918b373b789077f470b113957a, which is the head I measured.
- Step 14: the one moved instrument is tests/closures.json (+1 INERT read for the new harness). That entry is earned by the new tracked file, which tests/entities.py requires to be classified. No budget, ledger or score moved. The body's archscore `dS +0.0000 NULL` was not re-run, and the gate is green on it.
- Step 15: the added lines are test-only. The harness re-implements `_intern_until_rebuild` and the forked count rather than importing them. This is by design: it has to drive the merge-base tree, which lacks those functions.
- Figures I did not re-derive:
  - CI's 3.9/5.1/3.3 MiB readings and the 1.83 MiB CI table step (job-log citations).
  - The 43669-43674 per-process spread: the two-process `--intern-count` of a2a6cd9b4 is not at this head. My own forked counts on this image read 43598-43654 interns to the rebuild, a different fill level from the body's, which is consistent with an image-dependent fill.
  - The "3 slots per solve" count and "9 of 9 / 0 of 4" crossings.
  - The RSS-arm direct readings.
  - The scoped-gate wall times. I cite CI's green `tests / fast (3.14)` and `gate` rather than re-run them.

- Closing self-audit: `carry_audit.py check` gave `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`, rc 0. It ran against an abridged copy of the PR body that kept the Head, Red checks, Forward-carry and Friction sections, because this seat reads the body only through MCP. The packet's own carry_audit at this head, over the full body, read 0 finding items (ev/review-packet.md).

## Findings

- Follow-up: the body itself measures that, in the gate context, the memory pass's attributable-RSS arm reads 0.0 on every probe at both ends. CI's red pass shows the same: empty probe 117.2 MiB, attributable 0.0 on all six. So `rss_attrib_fail_threshold` cannot fire there, and an RSS regression smaller than the empty probe's lead passes the gate. This predates the PR and the PR does not settle it. Owed: make the empty probe's watermark comparable to a probe's in the gate context, with a planted RSS growth that reads red. Carry: R10-SUITE-HOST-DETERMINISM
- Follow-up: `give_interned_table_headroom()` in `_memory_baseline_main` is a value site that no gate check reads. The body names it as unpinned: deleting it moves direct attributable 6.8-7.4 to 10.3-10.7 MiB, and no check sees that. It becomes pinnable once the RSS arm above can fire, so it belongs with that item. Carry: R10-SUITE-HOST-DETERMINISM
- Residual: the body says `dev/audit/rounds/round4/D9/h7_memory_gate.py` "drive[s] stress's own --memory-probe, so the fix closes them too". Its INJECT_SRC opens its own `tracemalloc.start()` at line 143 with no headroom step, so its injection probe is not closed. It is frozen round evidence, its 2x injection can only read higher, and no gate depends on it. Carry: dismissed: frozen round evidence, no gate reads it

## Friction

none
