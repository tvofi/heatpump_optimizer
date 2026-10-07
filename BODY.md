Repairs main's red `closures` job. #2017 (b281a4c3) added `tools/audit/harnesses/eg_b7_seam_hubs.py`; `tests/harness_headers.py` reads every harness file, and `tests/closures.json` did not record that read. This adds the one line `tools/audit/harnesses/eg_b7_seam_hubs.py` to `inert_reads` of `tests/harness_headers.py`, in sorted position after `dual_path.py`. The twelve other `tools/audit/harnesses/*` files that script reads sit in the same list, so this follows the table's own precedent. No closure moves and no issue is closed.

_Requested by **tvofi**_

## Head

`042b66fa11575c4c520807cf540ff48eaa606101`

## Root cause

The reviewer of #2017 relied on CI's `closures` check for the closure table, and that check had not yet run on main: it runs on a push to main, and on a pull request only when the diff can move a closure. A new harness file read by `harness_headers.py` is a diff the pull-request scoping did not flag. The first run that measured it was the push to main, which failed. `closures-autofix` printed `skip-manual-repair-owed`, so no bot repair follows. Cheaper detector: `python3 tests/closure.py check --in-dir <recordings>`, the step the job runs, which needs a Linux recording and so cannot run on a seat's Mac.

## Mutation proof

Reverting the one line in `tests/closures.json` and running the check below prints `INERT READS UNDER-APPROXIMATED` and `tests/harness_headers.py: tools/audit/harnesses/eg_b7_seam_hubs.py`, rc=1.

## Null control

The same check on origin/main `17f30f9ced` fails with that line. A recording that lists an inert read already in the table (for example `tools/audit/harnesses/dual_path.py`) passes on both trees.

## Figures

Taken at `042b66fa11575c4c520807cf540ff48eaa606101`. The recording is a one-script stand-in, `{"script":"tests/harness_headers.py","files":[],"inert_reads":["tools/audit/harnesses/eg_b7_seam_hubs.py"]}`, not a Linux derivation. The full derivation was not run off Linux.

- `python3 tests/closure.py check --in-dir <dir holding that recording> --partial` at origin/main: rc=1, `INERT READS UNDER-APPROXIMATED`.
- The same command at this head: rc=0, `closure: committed closures cover every file this run touched`.

## Red checks

`closures`: the defect fixed here. Main run job 112789710707 at 38c03d94 failed on `tests/harness_headers.py: tools/audit/harnesses/eg_b7_seam_hubs.py`. Cheaper detector: none on a Mac, since the recording needs strace on Linux; the standing cost is the push-to-main run.

`delivery-status`: main's. This diff touches no delivery file and not `tests/delivery_status.py`.

`nightly-status`: main's. This diff does not change `tests/nightly_status.py`, `tests.yml`, `governance.yml`, the plan or `dev/programme/HANDOVER.md`.

## Forward-carry

none

## Friction

none
