Repair of the P676 hotfix. The first fix's new self-test padded the HOST wc's output, so on macOS (BSD wc already pads to width 8) its null control failed: `FAIL the padding wc stub pads its count ... (got               1, wanted        1)`, 539 passed, 1 failed. Both stubs now strip the host wc's output with `tr -d ' '` and emit one fixed form: the padding stub `printf '%8s\n'`, a second non-padding stub the bare count. The clean-tree comparison runs under each, so the check no longer depends on the host's wc. Only `tools/pr/prepr.sh` changes.

## Head

c8780ea33db1c31ff1d38144c70af3d1b3f25eda

## Mutation proof

Restoring the old comparison (dropping `| tr -d ' '` from the padding-wc arm) and running `bash tools/pr/prepr.sh --self-test` gave `FAIL and the in-place run leaves the work tree clean, under a wc that pads its count (got        0, wanted 0)` and `539 passed, 1 failed`; restored, the same command gives `540 passed, 0 failed`.

## Null control

Two arms assert the stubs behave as named: the padding stub yields `       1` and the non-padding stub yields `1` for `printf 'x\n' | wc -l`, whatever the host wc prints, so each later comparison is measured under a known wc. Unmodified tree: the arm passed on Linux only because Linux wc does not pad.

## Figures

- `bash tools/pr/prepr.sh --self-test`: 540 passed, 0 failed at the head above.
- `bash tools/pr/prepr.sh`: PRE-PR rc=0 at the head above.

## Red checks

none

## Forward-carry

This is the third macOS-only prepr self-test failure (the class barrier fires): the deferred raw-`wc` string-compare lint (P676(b)) and a host-independence rule for self-test stubs are owed; both land in dev/programme/rosters/wave-r10-groups.json, group R10-PREPR-DARWIN-SELFTEST-LANE, on the roster branch at 5b1b0f1586a2e95e84a7504e528b56bb8aa7020c. Carry: R10-PREPR-DARWIN-SELFTEST-LANE

## Friction

none
