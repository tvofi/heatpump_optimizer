_Requested by **tvofi**_

Part of #201

Before: `bash tools/audit/seat/bus.sh --self-test` on the Mac (macOS, bash 3.2, LibreSSL) printed 45 checks, 1 failed: "watch without --once keeps waiting while nothing changes". That arm wrapped `watch` in `timeout 3` and expected exit 124. `timeout` is GNU coreutils and stock macOS has none, so the shell exits 127 and writes "command not found" to the captured output, failing both conditions. `watch` itself was fine; only the instrument was Linux-only.

After: the arm runs `watch --every 1` in the background, checks after three seconds that it is still running (`kill -0`), kills it, and expects it to have printed nothing. No production line of `bus.sh` changes.

How: one self-test arm in `tools/audit/seat/bus.sh`.

## Head

69646cefda47d1c9734d42b56d64cc124888268f

Merge base: main 8a0ca90a.

## Approval

Owed before merge: tvofi's approving review at this head, under the code-owner rule on `tools/audit/`.

## Mutation proof

Red first, the Mac's failure reproduced on Linux: with a `timeout` on `PATH` that exits 127 the way a missing command does, main's script prints 45 checks, 1 failed, the same arm. This head prints 45 checks, 0 failed under the same `PATH`.

The arm still detects what it is for: `watch`'s loop made to return after a quiet pass (`[ $once = 1 ] && return 0` replaced by `return 0`) fails it, 45 checks, 1 failed.

## Null control

This head with the system `timeout` present: 45 checks, 0 failed. The fixed arm uses no `timeout`, so its presence or absence does not move it.

## Figures

- `bash tools/audit/seat/bus.sh --self-test` at 69646cef: 45 checks, 0 failed.
- `bash tools/audit/prepr.sh <this body>`: no refusal, rc 0.

## Red checks

none

## Forward-carry

none. The class (a GNU-only tool in a self-test the Mac runs) is named here; this pull request does not sweep other scripts for it.

## Friction

none
