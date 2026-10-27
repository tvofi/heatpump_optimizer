Triage batch 38 rules V126, the gate lease that appears to give one seat the whole push lane for half an hour. The verdict is **ACCEPT narrowed**: the bound that can be moved is on the waiter, not on the holder. The proposal's arm 1 -- bound the lease and renew it -- is REJECTED because it is already the mechanism (`LEASE_SECONDS = 1800`, and `renew()` refuses with rc 75 while another label's ticket waits) and because the 38-minute wait the proposal measured is `fcntl` on a *running* measurement, which no expiry can preempt; arm 2 (measuring scripts sharing the heavy-slot pool) is REJECTED because `tests/stress.py` and `tests/harness_headers.py` are leased precisely because their numbers are comparable only with nothing else running; arm 3 (longer leases) is REJECTED as proposed. What the ruling carries, to the group that owns `tests/gate_lock.py` and `tools/pr/prepr.sh`, is a wait deadline that falls back to the exit the rule already sanctions: a named unrun left to CI.

The measurement that closes the proposal's question: the tree's own recordings put `tests/stress.py` at 936.3 s, so the observed 38-minute block is two consecutive legitimate measurement runs, not a lease period being spent. No product behaviour changes in this batch: the diff is one markdown file under `dev/programme/triage/`.

P206's destination is `R10-PREPR-CAP`, the group that owns `tools/pr/prepr.sh` and `tests/gate_lock.py` in `dev/programme/rosters/wave-r10-groups.json`. That group's stage is `done`, so the carry audit refuses it as a body destination and the carry is routed in prose instead, as P196 was: the roster seat reopens `R10-PREPR-CAP` and appends this batch's carry text, which is the roster-queue line filed with the batch.

## Head

`d606ade6db7775606e3f31f8df45032a183c5e1a` merges the authored code head `8d91422e71e33e53ac71a76563133695834061d0` and then merges origin/main `34cd75bf1` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`388b0ab5ca97c1c761ca360daed5f4eabe0c12af` merges the authored code head `d8e3db265ff68f20cc2adb4edb1d5f86fd3dd579` and then merges origin/main `524c1896b` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`1a7484a36d0e797d73f4c1bca3a619d4bf6b6dfc` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2881.md`. The authored code head is `51dd6d00b7c2321fe4f3acb6e3c8b68c74d6d55c`.

`51dd6d00b7c2321fe4f3acb6e3c8b68c74d6d55c`; the file is the whole diff against `524c1896b6943b3da03d6cad61420ced31e14c9c`.

## Mutation proof

`tools/audit/seat/roster_edit.py`'s triage gate is this file's only in-tree consumer, and an ACCEPT is what lets the carried text cite it. On the committed file, with the seat library on `sys.path`:

```
P206 verdict: ACCEPT
refusal on committed file: None
```

Flipping the verdict line to `DEFER` in an out-of-tree copy prints `mutant verdict: DEFER` and `mutant refusal: dev/programme/triage/s6-batch38.md#P206 is not an ACCEPT ruling (DEFER)`: the gate reads this file's verdict, so a DEFER could not be laundered into a carry.

## Null control

An entry that does not exist (`P999`) prints `P999 verdict: None`, and a missing file prints `the triage ruling dev/programme/triage/s6-batch38.md is not on the roster branch or origin/main`.

## Figures

One line per figure, with the command that printed it.

- `tests/stress.py` 936.3 s and `tests/harness_headers.py` 241.1 s: `python3 -c "import json; print(json.load(open('tests/closures.json'))['recorded']['tests/stress.py'])"` and the same for `harness_headers.py`.
- the lease period and its refusal: `LEASE_SECONDS = 1800` (line 78), `RENEW_REFUSED_RC = 75` (line 120), `renew()` at line 568 in `tests/gate_lock.py`.
- the lease is taken per script and only for measuring ones: `tests/run.sh`'s `leased()` (lines 317-355) asks `needs-lease` about one script, and `needs_lease` (lines 918-954) answers `lease` only for `MACHINE_MEASURING`. Measured: a scope naming two ordinary scripts answers `slot`, one naming `tests/stress.py` answers `lease` (`python3 tests/gate_lock.py needs-lease <file>`).
- the waiter's wait has no deadline: `take()` (lines 511-566) is `while True: ... time.sleep(WAIT_POLL_SECS)`, and `grep -n 'timeout\|deadline\|max_wait' tests/gate_lock.py` finds only subprocess-cleanup waits.
- the observed wait: `update_pr.sh fix/r10-cop-partload` (pid 62391) as an fcntl waiter for 38 minutes while the owner file passed from `fix-2854-stress2` (released 11:59:49Z) to `r10-train-overlap-grade` (taken 11:59:52Z, `expires_at` 12:29:52Z); read at 12:13Z with `cat /tmp/hpo-gate.lock/owner`. The orchestrator's measurement, not re-derived here.
- the destination: `R10-PREPR-CAP` owns `tools/pr/prepr.sh` and `tests/gate_lock.py`, stage `done`, no carry; `tests/run.sh` is named in no group's `files` across 208 groups (`dev/programme/rosters/wave-r10-groups.json`).

## Red checks

none

## Forward-carry

none

## Friction

none


